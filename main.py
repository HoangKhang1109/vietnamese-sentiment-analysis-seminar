# main.py
from fastapi import FastAPI
from pydantic import BaseModel
from model import analyzer
from fastapi.middleware.cors import CORSMiddleware
import sqlite3
from datetime import datetime

app = FastAPI(title="Phân loại cảm xúc trong câu Tiếng Việt")

#Streamlit gọi API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Tạo database
def init_db():
    conn = sqlite3.connect('history.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS sentiments
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  text TEXT,
                  sentiment TEXT,
                  confidence REAL,
                  timestamp TEXT)''')
    conn.commit()
    conn.close()

init_db()

class TextInput(BaseModel):
    text: str

@app.post("/predict")
def predict_sentiment(input: TextInput):
    result = analyzer.predict(input.text)
    
    # Lưu vào DB
    conn = sqlite3.connect('history.db')
    c = conn.cursor()
    c.execute("INSERT INTO sentiments (text, sentiment, confidence, timestamp) VALUES (?, ?, ?, ?)",
              (result['text'], result['sentiment'], result['confidence'], datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()
    conn.close()
    return result

@app.get("/history")
def get_history():
    conn = sqlite3.connect('history.db')
    c = conn.cursor()
    c.execute("SELECT text, sentiment, confidence, timestamp FROM sentiments ORDER BY id DESC LIMIT 50")
    rows = c.fetchall()
    conn.close()
    return [{"text": r[0], "sentiment": r[1], "confidence": r[2], "time": r[3]} for r in rows]

@app.delete("/history")
def clear_history():
    conn = sqlite3.connect('history.db')
    c = conn.cursor()
    c.execute("DELETE FROM sentiments")           # Xóa hết dữ liệu
    c.execute("DELETE FROM sqlite_sequence WHERE name='sentiments'")  
    conn.commit()
    conn.close()
    return {"status": "cleared", "message": "Đã xóa toàn bộ lịch sử phân tích"}