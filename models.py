import sqlite3
import os

DB_PATH = os.environ.get("DB_PATH", "/tmp/news.db")


def _conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with _conn() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS articles (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                title      TEXT    NOT NULL,
                description TEXT,
                link       TEXT    UNIQUE NOT NULL,
                pub_date   TEXT,
                source     TEXT,
                lang       TEXT,
                created_at TEXT    DEFAULT (datetime('now'))
            )
        """)
        conn.commit()


def save_articles(articles):
    saved = 0
    with _conn() as conn:
        for a in articles:
            cur = conn.execute(
                """INSERT OR IGNORE INTO articles
                   (title, description, link, pub_date, source, lang)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (a["title"], a["description"], a["link"],
                 a["pub_date"], a["source"], a["lang"]),
            )
            saved += cur.rowcount
        conn.commit()
    return saved


def get_articles(page=1, per_page=20, lang=None, source=None):
    query = "SELECT * FROM articles WHERE 1=1"
    params = []
    if lang:
        query += " AND lang = ?"
        params.append(lang)
    if source:
        query += " AND source = ?"
        params.append(source)
    query += " ORDER BY pub_date DESC LIMIT ? OFFSET ?"
    params += [per_page, (page - 1) * per_page]
    with _conn() as conn:
        return conn.execute(query, params).fetchall()


def count_articles(lang=None, source=None):
    query = "SELECT COUNT(*) FROM articles WHERE 1=1"
    params = []
    if lang:
        query += " AND lang = ?"
        params.append(lang)
    if source:
        query += " AND source = ?"
        params.append(source)
    with _conn() as conn:
        return conn.execute(query, params).fetchone()[0]


def get_sources():
    with _conn() as conn:
        rows = conn.execute("SELECT DISTINCT source FROM articles ORDER BY source").fetchall()
    return [r["source"] for r in rows]
