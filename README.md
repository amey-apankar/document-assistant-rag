# AI Document Assistant

This is an AI-powered Document Assistant backend. It lets you upload PDF documents and ask questions about them. The system extracts text from the files, cuts it into small sections, generates vector embeddings, and stores them in ChromaDB. When you ask a question, it searches the database for relevant sections and uses Google Gemini to answer with source citations. It also saves your conversation history in a SQLite database.

## Prerequisites

You need Python 3.10 or higher installed on your computer.

## Installation

First, clone this repository and go to the project directory.

Run the following command to install the required packages:

```bash
pip install -r requirements.txt
```

## Configuration

Copy the example environment file and name it .env:

```bash
copy .env.example .env
```

Open the newly created .env file and replace the placeholder value with your actual Google Gemini API key:

```env
GEMINI_API_KEY=your_actual_api_key_here
```

## Running the Application

You can start the FastAPI server by running this command in your terminal:

```bash
uvicorn main:app --reload
```

The server will start on http://127.0.0.1:8000. You can access the interactive API documentation at http://127.0.0.1:8000/docs.

## API Endpoints

Here are the main endpoints you can use:

* Upload a PDF: POST /upload (Send a PDF file as form-data)
* Ask a Question: POST /query (Send a JSON payload with your query and an optional session_id)
* View Chat History: GET /history/{session_id} (Retrieve history for a specific session)
* List Documents: GET /documents (Get a list of all uploaded PDFs)
