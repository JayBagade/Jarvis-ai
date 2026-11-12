import os, sqlite3
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import requests

ROOT = Path(__file__).parent
DB = ROOT / "jarvis_memory.db"
app = FastAPI(title="JARVIS")

SYSTEM_PROMPT = """You are JARVIS, Jay's personal AI assistant.
Personality: chill, thoughtful, confident, intelligent buddy. Speak naturally, not like a corporate bot.
Be concise by default; explain deeply when asked. Joke lightly only when Jay jokes first.
Help Jay with learning, building projects, and MUKTAAI EXPORTS. Be honest about limitations.
Never claim to have performed actions you did not perform."""

def init_db():
    with sqlite3.connect(DB) as c:
        c.execute("""CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            role TEXT NOT NULL, content TEXT NOT NULL
        )""")
init_db()

class ChatIn(BaseModel):
    message: str

@app.get("/", response_class=HTMLResponse)
def home():
    return (ROOT / "index.html").read_text(encoding="utf-8")

@app.get("/api/history")
def history():
    with sqlite3.connect(DB) as c:
        rows = c.execute("SELECT role,content FROM messages ORDER BY id DESC LIMIT 30").fetchall()
    return {"messages":[{"role":r,"content":t} for r,t in reversed(rows)]}

@app.post("/api/chat")
def chat(data: ChatIn):
    message = data.message.strip()
    if not message:
        raise HTTPException(400, "Please type a message.")
    if len(message) > 8000:
        raise HTTPException(413, "Message is too long (max 8,000 characters).")
    key = os.getenv("GEMINI_API_KEY")
    if not key:
        raise HTTPException(503, "JARVIS setup incomplete: add GEMINI_API_KEY in the host's Secrets/Environment settings.")
    with sqlite3.connect(DB) as c:
        rows = c.execute("SELECT role,content FROM messages ORDER BY id DESC LIMIT 12").fetchall()
    history = [{"role":"model" if role=="assistant" else "user",
                "parts":[{"text":content}]} for role,content in reversed(rows)]
    payload={"system_instruction":{"parts":[{"text":SYSTEM_PROMPT}]},
             "contents":history+[{"role":"user","parts":[{"text":message}]}],
             "generationConfig":{"temperature":0.7,"maxOutputTokens":900}}
    url="https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"
    try:
        res=requests.post(url,params={"key":key},json=payload,timeout=45)
        if not res.ok:
            detail=res.json().get("error",{}).get("message",f"Gemini HTTP {res.status_code}")
            raise HTTPException(502, detail)
        answer="".join(p.get("text","") for p in res.json()["candidates"][0]["content"]["parts"]).strip()
    except requests.Timeout:
        raise HTTPException(504,"Gemini took too long. Try again.")
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(502,"Gemini response could not be read. Try again.")
    with sqlite3.connect(DB) as c:
        c.execute("INSERT INTO messages(role,content) VALUES(?,?)",("user",message))
        c.execute("INSERT INTO messages(role,content) VALUES(?,?)",("assistant",answer))
    return {"reply":answer}

@app.post("/api/clear")
def clear():
    with sqlite3.connect(DB) as c:
        c.execute("DELETE FROM messages")
    return {"ok":True}
