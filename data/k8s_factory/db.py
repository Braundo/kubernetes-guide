import sqlite3, os
from datetime import datetime, timezone

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "k8s_factory.db")

def get_db():
    db = sqlite3.connect(DB_PATH)
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA journal_mode=WAL")
    db.execute("""CREATE TABLE IF NOT EXISTS items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        url TEXT UNIQUE NOT NULL, title TEXT NOT NULL,
        summary TEXT DEFAULT '', published TEXT DEFAULT '',
        source_name TEXT DEFAULT '', category_hint TEXT DEFAULT '',
        content_hash TEXT DEFAULT '', stars INTEGER DEFAULT 0,
        crawled_at TEXT NOT NULL, processed INTEGER DEFAULT 0,
        generated_file TEXT DEFAULT '')""")
    db.execute("""CREATE TABLE IF NOT EXISTS run_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        started_at TEXT NOT NULL, finished_at TEXT DEFAULT '',
        items_crawled INTEGER DEFAULT 0, items_generated INTEGER DEFAULT 0,
        status TEXT DEFAULT 'running', error TEXT DEFAULT '')""")
    db.commit()
    return db

def insert_item(db, item):
    try:
        db.execute("""INSERT INTO items (url,title,summary,published,source_name,
            category_hint,content_hash,stars,crawled_at)
            VALUES (?,?,?,?,?,?,?,?,?)""",
            (item["url"], item["title"], item.get("summary",""),
             item.get("published",""), item.get("source_name",""),
             item.get("category_hint",""), item.get("content_hash",""),
             item.get("stars",0), datetime.now(timezone.utc).isoformat()))
        db.commit()
    except sqlite3.IntegrityError: pass

def item_exists_by_url(db, url):
    return db.execute("SELECT 1 FROM items WHERE url=?", (url,)).fetchone() is not None

def get_unprocessed_items(db):
    return [dict(r) for r in db.execute(
        "SELECT * FROM items WHERE processed=0 ORDER BY crawled_at DESC").fetchall()]

def mark_processed(db, item_id, filename):
    db.execute("UPDATE items SET processed=1, generated_file=? WHERE id=?",
               (filename, item_id))
    db.commit()

def get_recent_articles(db, days=7):
    cutoff = datetime.now(timezone.utc).isoformat()[:10]
    return [dict(r) for r in db.execute(
        "SELECT * FROM items WHERE processed=1 AND crawled_at > date(?, '-' || ? || ' days') ORDER BY crawled_at DESC",
        (cutoff, str(days))).fetchall()]

def log_run_start(db):
    c = db.execute("INSERT INTO run_log (started_at) VALUES (?)",
                   (datetime.now(timezone.utc).isoformat(),))
    db.commit()
    return c.lastrowid

def log_run_end(db, run_id, crawled, generated, status, error=""):
    db.execute("""UPDATE run_log SET finished_at=?, items_crawled=?,
        items_generated=?, status=?, error=? WHERE id=?""",
        (datetime.now(timezone.utc).isoformat(), crawled, generated,
         status, error, run_id))
    db.commit()
