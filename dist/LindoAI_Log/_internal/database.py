import sqlite3

def init_db():
    conn = sqlite3.connect("log.db")
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            start_time TEXT NOT NULL,
            end_time TEXT NOT NULL,
            content TEXT NOT NULL,
            project TEXT
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS meta (
            date TEXT PRIMARY KEY,
            location TEXT,
            recorder TEXT,
            weather TEXT,
            temperature TEXT
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS phrases (
            phrase TEXT PRIMARY KEY,
            count INTEGER DEFAULT 1
        )
    """)

    conn.commit()
    conn.close()

def insert_log(date, start_time, end_time, content, project):
    conn = sqlite3.connect("log.db")
    c = conn.cursor()
    c.execute("INSERT INTO logs (date, start_time, end_time, content, project) VALUES (?, ?, ?, ?, ?)",
              (date, start_time, end_time, content, project))
    c.execute("INSERT INTO phrases (phrase, count) VALUES (?, 1) ON CONFLICT(phrase) DO UPDATE SET count = count + 1",
              (content,))
    conn.commit()
    conn.close()

def get_logs_by_date(date_str):
    conn = sqlite3.connect("log.db")
    c = conn.cursor()
    c.execute("SELECT id, start_time, end_time, content, project FROM logs WHERE date = ? ORDER BY start_time", (date_str,))
    rows = c.fetchall()
    conn.close()
    return rows


def save_meta(date, location, recorder, weather, temperature):
    conn = sqlite3.connect("log.db")
    c = conn.cursor()
    c.execute("REPLACE INTO meta (date, location, recorder, weather, temperature) VALUES (?, ?, ?, ?, ?)",
              (date, location, recorder, weather, temperature))
    conn.commit()
    conn.close()

def get_meta(date):
    conn = sqlite3.connect("log.db")
    c = conn.cursor()
    c.execute("SELECT location, recorder, weather, temperature FROM meta WHERE date = ?", (date,))
    row = c.fetchone()
    conn.close()
    return row or ("", "", "", "")

def get_top_phrases(limit=10):
    conn = sqlite3.connect("log.db")
    c = conn.cursor()
    c.execute("SELECT phrase FROM phrases ORDER BY count DESC LIMIT ?", (limit,))
    rows = c.fetchall()
    conn.close()
    return [row[0] for row in rows]