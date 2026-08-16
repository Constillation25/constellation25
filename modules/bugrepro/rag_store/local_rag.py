#!/data/data/com.termux/files/usr/bin/python3
"""
BugRepro Local RAG Store
Stores historical bug reports and S2R (Steps to Reproduce) entities.
Uses SQLite Full-Text Search for sovereign, local retrieval.
"""
import sqlite3
import json
import time
from pathlib import Path

DB_PATH = Path.home() / "constellation25" / "modules" / "bugrepro" / "rag_store" / "bug_rag.db"

class LocalRAGStore:
    def __init__(self):
        DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(DB_PATH))
        self.conn.execute("PRAGMA journal_mode=WAL")
        self._init_schema()

    def _init_schema(self):
        self.conn.execute("""
            CREATE VIRTUAL TABLE IF NOT EXISTS bug_reports USING fts5(
                title, description, s2r_entities, steps_to_reproduce,
                content='bug_reports', content_rowid='rowid'
            )
        """)
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS bug_metadata (
                rowid INTEGER PRIMARY KEY,
                app_name TEXT,
                severity TEXT,
                timestamp REAL
            )
        """)
        self.conn.commit()

    def ingest_bug(self, title, description, s2r_entities, steps, app_name="Unknown", severity="Medium"):
        """Ingest a bug report into the RAG store"""
        cursor = self.conn.execute("""
            INSERT INTO bug_reports(title, description, s2r_entities, steps_to_reproduce)
            VALUES (?, ?, ?, ?)
        """, (title, description, json.dumps(s2r_entities), json.dumps(steps)))
        
        rowid = cursor.lastrowid
        self.conn.execute("""
            INSERT INTO bug_metadata(rowid, app_name, severity, timestamp)
            VALUES (?, ?, ?, ?)
        """, (rowid, app_name, severity, time.time()))
        self.conn.commit()
        print(f"[RAG] Ingested bug: {title} (ID: {rowid})")
        return rowid

    def retrieve_similar(self, query_text, top_k=3):
        """Retrieve similar bug reports using FTS5"""
        cursor = self.conn.execute("""
            SELECT rowid, title, description, s2r_entities, steps_to_reproduce, rank
            FROM bug_reports
            WHERE bug_reports MATCH ?
            ORDER BY rank
            LIMIT ?
        """, (query_text, top_k))
        
        results = []
        for row in cursor.fetchall():
            results.append({
                "id": row[0],
                "title": row[1],
                "description": row[2],
                "s2r_entities": json.loads(row[3]) if row[3] else [],
                "steps": json.loads(row[4]) if row[4] else [],
                "rank": row[5]
            })
        return results

if __name__ == "__main__":
    store = LocalRAGStore()
    print("=== BUGREPRO LOCAL RAG STORE ===")
    
    # Seed with example data
    store.ingest_bug(
        "App crashes on login",
        "When clicking login with empty password, app force closes.",
        ["LoginButton", "PasswordInput"],
        ["1. Open app", "2. Leave password empty", "3. Click Login"],
        "MyBuyo", "High"
    )
    
    # Test retrieval
    results = store.retrieve_similar("crash login empty password")
    print(f"\nRetrieved {len(results)} similar bugs:")
    for r in results:
        print(f"  - {r['title']} (Rank: {r['rank']:.2f})")
