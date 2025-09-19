import sqlite3

conn = sqlite3.connect('dummy.db')
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS points (
    user_id INTEGER,
    shift_title TEXT,
    user_points INTEGER,
    rated_at TIMESTAMP,
    UNIQUE(user_id, shift_title)
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT,
    is_auth INTEGER DEFAULT 0
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS favorites (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    shift_title TEXT,
    order_index INTEGER,
    UNIQUE(user_id, shift_title)
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS shifts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT UNIQUE
)
""")

conn.commit()
conn.close()