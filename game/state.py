import sqlite3
import json
import os
from datetime import datetime

DB_PATH = "data/game.db"

def init():
    os.makedirs("data", exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # I went with three tables. Anything more is showing off.
    c.execute("""
        CREATE TABLE IF NOT EXISTS clues (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            raw_class TEXT,
            game_weapon TEXT,
            suspect_count INTEGER,
            confidence REAL
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS deductions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            suspect_probs TEXT,
            weapon_probs TEXT,
            room_probs TEXT
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            started_at TEXT,
            culprit TEXT,
            weapon TEXT,
            room TEXT,
            solved INTEGER DEFAULT 0,
            correct INTEGER DEFAULT 0
        )
    """)

    conn.commit()
    conn.close()

def start_session(mystery):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "INSERT INTO sessions (started_at, culprit, weapon, room) VALUES (?, ?, ?, ?)",
        (datetime.now().isoformat(), mystery["culprit"], mystery["weapon"], mystery["room"])
    )
    sid = c.lastrowid
    conn.commit()
    conn.close()
    return sid

def log_clue(raw_class, game_weapon, suspect_count, confidence):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "INSERT INTO clues (timestamp, raw_class, game_weapon, suspect_count, confidence) VALUES (?, ?, ?, ?, ?)",
        (datetime.now().isoformat(), raw_class, game_weapon, suspect_count, confidence)
    )
    conn.commit()
    conn.close()

def log_deduction(suspect_probs, weapon_probs, room_probs):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "INSERT INTO deductions (timestamp, suspect_probs, weapon_probs, room_probs) VALUES (?, ?, ?, ?)",
        (datetime.now().isoformat(), json.dumps(suspect_probs), json.dumps(weapon_probs), json.dumps(room_probs))
    )
    conn.commit()
    conn.close()

def get_clues():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT timestamp, raw_class, game_weapon, suspect_count, confidence FROM clues ORDER BY id DESC LIMIT 50")
    rows = c.fetchall()
    conn.close()
    return rows

def close_session(sid, correct):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE sessions SET solved=1, correct=? WHERE id=?", (int(correct), sid))
    conn.commit()
    conn.close()
