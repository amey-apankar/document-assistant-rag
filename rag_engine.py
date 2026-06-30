import os
from pypdf import PdfReader
import chromadb
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

chroma_client = chromadb.PersistentClient(path="chroma_db")
collection = chroma_client.get_or_create_collection(name="documents")

def extract_text_from_pdf(pdf_path: str):
    reader = PdfReader(pdf_path)
    extracted_data = []
    for i, page in enumerate(reader.pages):
        text = page.extract_text()
        if text and text.strip():
            extracted_data.append({
                "page_num": i + 1,
                "text": text.strip()
            })
    return extracted_data

def chunk_text(extracted_data: list, doc_name: str, chunk_size: int = 800, overlap: int = 100):
    chunks = []
    for page in extracted_data:
        text = page["text"]
        page_num = page["page_num"]
        
        start = 0
        while start < len(text):
            end = start + chunk_size
            chunk_content = text[start:end]
            
            chunks.append({
                "content": chunk_content,
                "metadata": {
                    "source": doc_name,
                    "page": page_num
                }
            })
            start += (chunk_size - overlap)
    return chunks

def embed_and_store_chunks(chunks: list):
    if not chunks:
        return
    
    texts = [c["content"] for c in chunks]
    metadatas = [c["metadata"] for c in chunks]
    
    # UPDATED: Using the new embedding model
    response = genai.embed_content(
        model="models/gemini-embedding-001",
        content=texts,
        task_type="retrieval_document"
    )
    embeddings = response["embedding"]
    
    ids = [f"{m['source']}_p{m['page']}_{i}" for i, m in enumerate(metadatas)]
    
    collection.add(
        embeddings=embeddings,
        documents=texts,
        metadatas=metadatas,
        ids=ids
    )

def query_rag(user_query: str, n_results: int = 3):
    query_resp = genai.embed_content(
        model="models/gemini-embedding-001",
        content=user_query,
        task_type="retrieval_query"
    )
    query_embedding = query_resp["embedding"]
    
    db_results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results
    )
    
    retrieved_texts = db_results["documents"][0]
    retrieved_metadatas = db_results["metadatas"][0]
    
    context_list = []
    sources = []
    for text, meta in zip(retrieved_texts, retrieved_metadatas):
        context_list.append(f"Source: {meta['source']} (Page {meta['page']})\nContent: {text}")
        source_info = f"{meta['source']} (Page {meta['page']})"
        if source_info not in sources:
            sources.append(source_info)
            
    context = "\n\n".join(context_list)
    
    prompt = f"""You are a helpful document assistant. Answer the user question accurately using only the context provided below. If the context does not contain the answer, say that you do not know. Always cite the sources (document name and page number) you used from the context.

Context:
{context}

Question:
{user_query}

Answer:"""

    model = genai.GenerativeModel("gemini-1.5-flash")
    generation = model.generate_content(prompt)
    answer = generation.text
    
    return {
        "answer": answer,
        "sources": sources
    }
