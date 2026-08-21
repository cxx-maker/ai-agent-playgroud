"""SQLite 状态管理"""
import sqlite3
import os
from datetime import datetime


DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "session.db")


def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                id TEXT PRIMARY KEY,
                resume TEXT DEFAULT '',
                jd TEXT DEFAULT '',
                company TEXT DEFAULT '',
                job_title TEXT DEFAULT '',
                created_at TEXT NOT NULL
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)


def save_session_state(session_id, resume="", jd="", company="", job_title=""):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            INSERT OR REPLACE INTO sessions
            (id, resume, jd, company, job_title, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (session_id, resume, jd, company, job_title,
              datetime.now().isoformat()))


def load_session_state(session_id):
    with sqlite3.connect(DB_PATH) as conn:
        row = conn.execute(
            "SELECT resume, jd, company, job_title FROM sessions WHERE id = ?",
            (session_id,)
        ).fetchone()
    if row:
        return {"resume": row[0], "jd": row[1], "company": row[2], "job_title": row[3]}
    return {"resume": "", "jd": "", "company": "", "job_title": ""}


def save_message(session_id, role, content):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "INSERT INTO messages (session_id, role, content, created_at) VALUES (?, ?, ?, ?)",
            (session_id, role, content, datetime.now().isoformat())
        )


def load_session_messages(session_id, limit=20):
    with sqlite3.connect(DB_PATH) as conn:
        rows = conn.execute(
            "SELECT role, content FROM messages WHERE session_id = ? "
            "ORDER BY created_at DESC LIMIT ?",
            (session_id, limit)
        ).fetchall()
    return [{"role": r[0], "content": r[1]} for r in reversed(list(rows))]
