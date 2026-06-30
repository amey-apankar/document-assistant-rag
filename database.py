import sqlite3
from datetime import datetime
import json

DB_PATH = "chat_history.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            query TEXT NOT NULL,
            response TEXT NOT NULL,
            sources TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def save_chat_message(session_id: str, query: str, response: str, sources: list):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    created_at = datetime.utcnow().isoformat()
    sources_str = json.dumps(sources)
    cursor.execute(
        "INSERT INTO chat_history (session_id, query, response, sources, created_at) VALUES (?, ?, ?, ?, ?)",
        (session_id, query, response, sources_str, created_at)
    )
    conn.commit()
    conn.close()

def get_chat_history(session_id: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT query, response, sources, created_at FROM chat_history WHERE session_id = ? ORDER BY id ASC",
        (session_id,)
    )
    rows = cursor.fetchall()
    conn.close()
    
    history = []
    for row in rows:
        history.append({
            "query": row[0],
            "response": row[1],
            "sources": json.loads(row[2]),
            "created_at": row[3]
        })
    return history
