import os
import uuid
from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
from database import init_db, save_chat_message, get_chat_history
from rag_engine import extract_text_from_pdf, chunk_text, embed_and_store_chunks, query_rag

app = FastAPI(title="AI Document Assistant")

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.on_event("startup")
def startup_event():
    init_db()

class QueryRequest(BaseModel):
    query: str
    session_id: str = None

@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")
    
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as f:
        f.write(await file.read())
        
    try:
        extracted = extract_text_from_pdf(file_path)
        chunks = chunk_text(extracted, file.filename)
        embed_and_store_chunks(chunks)
        return {
            "message": "File uploaded and indexed successfully",
            "filename": file.filename,
            "chunks_created": len(chunks)
        }
    except Exception as e:
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/query")
async def query_document(request: QueryRequest):
    session_id = request.session_id or str(uuid.uuid4())
    
    try:
        result = query_rag(request.query)
        save_chat_message(
            session_id=session_id,
            query=request.query,
            response=result["answer"],
            sources=result["sources"]
        )
        return {
            "session_id": session_id,
            "query": request.query,
            "answer": result["answer"],
            "sources": result["sources"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/history/{session_id}")
async def get_history(session_id: str):
    history = get_chat_history(session_id)
    return {
        "session_id": session_id,
        "history": history
    }

@app.get("/documents")
async def list_documents():
    files = [f for f in os.listdir(UPLOAD_DIR) if f.lower().endswith(".pdf")]
    return {
        "documents": files
    }
