import sqlite3
from datetime import datetime, timezone

DB_PATH = "voidradio.db"


def get_connection():
    return sqlite3.connect(DB_PATH)


def init_db():
    conn = get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS stories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            reddit_id TEXT UNIQUE NOT NULL,
            subreddit TEXT NOT NULL,
            title TEXT NOT NULL,
            author TEXT,
            content TEXT NOT NULL,
            score INTEGER DEFAULT 0,
            flair TEXT,
            url TEXT,
            created_utc REAL,
            fetched_at TEXT NOT NULL
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS transmissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            story_id INTEGER NOT NULL UNIQUE,
            transmission TEXT NOT NULL,
            model TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY (story_id) REFERENCES stories(id)
        )
    """)
    conn.commit()
    conn.close()


def story_exists(reddit_id):
    conn = get_connection()
    row = conn.execute(
        "SELECT 1 FROM stories WHERE reddit_id = ?", (reddit_id,)
    ).fetchone()
    conn.close()
    return row is not None


def insert_story(story):
    conn = get_connection()
    conn.execute(
        """
        INSERT OR IGNORE INTO stories
            (reddit_id, subreddit, title, author, content, score, flair, url, created_utc, fetched_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            story["reddit_id"],
            story["subreddit"],
            story["title"],
            story["author"],
            story["content"],
            story["score"],
            story["flair"],
            story["url"],
            story["created_utc"],
            datetime.now(timezone.utc).isoformat(),
        ),
    )
    conn.commit()
    conn.close()


def get_last_fetch_time():
    conn = get_connection()
    row = conn.execute("SELECT MAX(fetched_at) FROM stories").fetchone()
    conn.close()
    if row and row[0]:
        return datetime.fromisoformat(row[0])
    return None


def get_stories(limit=None, subreddit=None):
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    query = "SELECT * FROM stories"
    params = []
    if subreddit:
        query += " WHERE subreddit = ?"
        params.append(subreddit)
    query += " ORDER BY created_utc DESC"
    if limit:
        query += " LIMIT ?"
        params.append(limit)
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_unformatted_stories():
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    rows = conn.execute("""
        SELECT s.* FROM stories s
        LEFT JOIN transmissions t ON s.id = t.story_id
        WHERE t.id IS NULL
        ORDER BY s.created_utc DESC
    """).fetchall()
    conn.close()
    return [dict(row) for row in rows]


def insert_transmission(story_id, transmission, model):
    conn = get_connection()
    conn.execute(
        """
        INSERT OR IGNORE INTO transmissions (story_id, transmission, model, created_at)
        VALUES (?, ?, ?, ?)
        """,
        (story_id, transmission, model, datetime.now(timezone.utc).isoformat()),
    )
    conn.commit()
    conn.close()


def get_transmissions(limit=None):
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    query = "SELECT t.*, s.title FROM transmissions t JOIN stories s ON s.id = t.story_id ORDER BY t.created_at DESC"
    params = []
    if limit:
        query += " LIMIT ?"
        params.append(limit)
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return [dict(row) for row in rows]
