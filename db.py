import sqlite3
from contextlib import contextmanager
from pathlib import Path

DB_PATH = Path("bot.sqlite3")

def init_db() -> None:
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute("""
        CREATE TABLE IF NOT EXISTS chat_settings (
            chat_id INTEGER PRIMARY KEY,
            welcome_enabled INTEGER DEFAULT 1,
            welcome_text TEXT DEFAULT 'خوش آمدی {name} 🌿',
            rules_text TEXT DEFAULT 'قوانین گروه را رعایت کنید.',
            links_blocked INTEGER DEFAULT 1,
            join_verify INTEGER DEFAULT 1
        )
        """)
        c.execute("""
        CREATE TABLE IF NOT EXISTS warnings (
            chat_id INTEGER,
            user_id INTEGER,
            count INTEGER DEFAULT 0,
            PRIMARY KEY (chat_id, user_id)
        )
        """)
        c.execute("""
        CREATE TABLE IF NOT EXISTS notes (
            chat_id INTEGER,
            key TEXT,
            value TEXT,
            PRIMARY KEY (chat_id, key)
        )
        """)
        conn.commit()

@contextmanager
def get_conn():
    conn = sqlite3.connect(DB_PATH)
    try:
        yield conn
    finally:
        conn.close()

def ensure_chat(chat_id: int) -> None:
    with get_conn() as conn:
        c = conn.cursor()
        c.execute("INSERT OR IGNORE INTO chat_settings (chat_id) VALUES (?)", (chat_id,))
        conn.commit()

def get_settings(chat_id: int) -> dict:
    ensure_chat(chat_id)
    with get_conn() as conn:
        c = conn.cursor()
        row = c.execute("""
            SELECT welcome_enabled, welcome_text, rules_text, links_blocked, join_verify
            FROM chat_settings WHERE chat_id=?
        """, (chat_id,)).fetchone()
    return {
        "welcome_enabled": bool(row[0]),
        "welcome_text": row[1],
        "rules_text": row[2],
        "links_blocked": bool(row[3]),
        "join_verify": bool(row[4]),
    }

def set_setting(chat_id: int, field: str, value) -> None:
    ensure_chat(chat_id)
    allowed = {"welcome_enabled", "welcome_text", "rules_text", "links_blocked", "join_verify"}
    if field not in allowed:
        raise ValueError("Invalid setting field")
    with get_conn() as conn:
        c = conn.cursor()
        c.execute(f"UPDATE chat_settings SET {field}=? WHERE chat_id=?", (value, chat_id))
        conn.commit()

def get_warns(chat_id: int, user_id: int) -> int:
    with get_conn() as conn:
        c = conn.cursor()
        row = c.execute("SELECT count FROM warnings WHERE chat_id=? AND user_id=?", (chat_id, user_id)).fetchone()
    return int(row[0]) if row else 0

def add_warn(chat_id: int, user_id: int, inc: int = 1) -> int:
    with get_conn() as conn:
        c = conn.cursor()
        c.execute("INSERT OR IGNORE INTO warnings (chat_id, user_id, count) VALUES (?, ?, 0)", (chat_id, user_id))
        c.execute("UPDATE warnings SET count = count + ? WHERE chat_id=? AND user_id=?", (inc, chat_id, user_id))
        conn.commit()
        row = c.execute("SELECT count FROM warnings WHERE chat_id=? AND user_id=?", (chat_id, user_id)).fetchone()
    return int(row[0])

def reset_warns(chat_id: int, user_id: int) -> None:
    with get_conn() as conn:
        c = conn.cursor()
        c.execute("DELETE FROM warnings WHERE chat_id=? AND user_id=?", (chat_id, user_id))
        conn.commit()

def set_note(chat_id: int, key: str, value: str) -> None:
    with get_conn() as conn:
        c = conn.cursor()
        c.execute("INSERT OR REPLACE INTO notes (chat_id, key, value) VALUES (?, ?, ?)", (chat_id, key, value))
        conn.commit()

def get_note(chat_id: int, key: str) -> str | None:
    with get_conn() as conn:
        c = conn.cursor()
        row = c.execute("SELECT value FROM notes WHERE chat_id=? AND key=?", (chat_id, key)).fetchone()
    return row[0] if row else None

def del_note(chat_id: int, key: str) -> None:
    with get_conn() as conn:
        c = conn.cursor()
        c.execute("DELETE FROM notes WHERE chat_id=? AND key=?", (chat_id, key))
        conn.commit()
