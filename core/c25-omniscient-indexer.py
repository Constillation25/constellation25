#!/data/data/com.termux/files/usr/bin/env python3
"""
C25 OMNISCIENT INDEXER (TOTAL RECALL FORENSIC ENGINE)
Ingests ALL raw data from Termux, SD Card, Obsidian, GitHub, Vercel, Replit.
Builds a unified, interconnected knowledge graph. NO FILTERS.
"""

import os
import sys
import json
import sqlite3
import re
from pathlib import Path
from datetime import datetime
import hashlib

HOME_DIR = Path.home()
SD_CARD = Path("/storage/emulated/0")
DB_PATH = HOME_DIR / "c25_store" / "omniscient_index.db"
MANIFEST_PATH = HOME_DIR / "c25_store" / "omniscient_manifest.json"

# Target ALL meaningful extensions
TARGET_EXTENSIONS = {
    '.html', '.sh', '.py', '.json', '.mht', '.md', '.txt', 
    '.js', '.css', '.yaml', '.yml', '.ts', '.tsx', '.jsx',
    '.env', '.gitignore', '.toml', '.xml', '.sql', '.log'
}

# Directories we explicitly WANT to scan deeply
TARGET_DIRS = [
    HOME_DIR,
    SD_CARD / "github",
    SD_CARD / "c25",
    SD_CARD / "c25_sovereign_product",
    SD_CARD / "ObsidianVault",
    SD_CARD / "termux_backup_1775713397", # Your specific backup
]

# Only skip absolute garbage that will crash the scanner
HARD_EXCLUDES = {'.git', 'node_modules', '.cache', 'c25_store', 'Android/data'}

class OmniscientIndexer:
    def __init__(self):
        self.db = sqlite3.connect(str(DB_PATH))
        self.db.execute("PRAGMA journal_mode=WAL;") # High-performance writes
        self.db.execute("PRAGMA synchronous=NORMAL;")
        self.setup_database()
        self.file_map = {} # path -> id
        
    def setup_database(self):
        self.db.execute("""
            CREATE TABLE IF NOT EXISTS artifacts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                path TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                extension TEXT,
                size_bytes INTEGER,
                content_hash TEXT,
                preview TEXT,
                location_type TEXT, -- 'termux', 'sdcard', 'obsidian', 'github'
                indexed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        self.db.execute("""
            CREATE TABLE IF NOT EXISTS connections (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_id INTEGER,
                target_keyword TEXT,
                connection_type TEXT, -- 'mentions', 'imports', 'references'
                FOREIGN KEY (source_id) REFERENCES artifacts(id)
            )
        """)
        self.db.execute("CREATE INDEX IF NOT EXISTS idx_ext ON artifacts(extension)")
        self.db.execute("CREATE INDEX IF NOT EXISTS idx_loc ON artifacts(location_type)")
        self.db.commit()

    def get_location_type(self, path: Path) -> str:
        path_str = str(path).lower()
        if "obsidian" in path_str: return "obsidian_vault"
        if "github" in path_str: return "github_repo"
        if "vercel" in path_str: return "vercel_deploy"
        if "replit" in path_str: return "replit_artifact"
        if "backup" in path_str: return "historical_backup"
        if str(path).startswith(str(HOME_DIR)): return "termux_home"
        return "sd_card"

    def scan_and_ingest(self):
        print("🌌 INITIATING TOTAL RECALL SCAN...")
        total_found = 0
        total_ingested = 0
        
        for base_dir in TARGET_DIRS:
            if not base_dir.exists():
                continue
                
            print(f"  ⟳ Scanning: {base_dir}")
            for root, dirs, files in os.walk(base_dir, followlinks=False):
                # Prune hard excludes to prevent infinite loops/bloat
                dirs[:] = [d for d in dirs if d not in HARD_EXCLUDES]
                
                for file in files:
                    file_path = Path(root) / file
                    ext = file_path.suffix.lower()
                    
                    if ext not in TARGET_EXTENSIONS:
                        continue
                        
                    total_found += 1
                    
                    try:
                        # Read first 1KB for fast hashing and preview
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content_snippet = f.read(1024)
                            
                        content_hash = hashlib.md5(content_snippet.encode()).hexdigest()
                        
                        # Check if already indexed
                        cursor = self.db.execute(
                            "SELECT id FROM artifacts WHERE path = ? AND content_hash = ?", 
                            (str(file_path), content_hash)
                        )
                        if cursor.fetchone():
                            continue # Already indexed, unchanged
                            
                        # Insert into DB
                        self.db.execute("""
                            INSERT INTO artifacts (path, name, extension, size_bytes, content_hash, preview, location_type)
                            VALUES (?, ?, ?, ?, ?, ?, ?)
                        """, (
                            str(file_path),
                            file_path.name,
                            ext,
                            file_path.stat().st_size,
                            content_hash,
                            content_snippet.replace('\n', ' ').strip()[:200],
                            self.get_location_type(file_path)
                        ))
                        
                        file_id = self.db.lastrowid
                        self.file_map[str(file_path)] = file_id
                        total_ingested += 1
                        
                        # Extract connections (keywords, imports, mentions)
                        self.extract_connections(file_id, file_path.name, content_snippet)
                        
                    except Exception as e:
                        pass # Skip unreadable files silently, keep scanning
                    
                    if total_found % 1000 == 0:
                        print(f"    ...processed {total_found} files, ingested {total_ingested} new artifacts.")
                        
        self.db.commit()
        print(f"\n✅ SCAN COMPLETE: Found {total_found} target files. Ingested {total_ingested} new artifacts.")

    def extract_connections(self, file_id: int, filename: str, content: str):
        """Find what this file mentions or connects to"""
        connections = set()
        
        # 1. Extract C25 / Project keywords
        keywords = re.findall(r'\b(constellation25|videocourts|aikre8tive|pathos|faceprintpay|versed|lunar27|manus|replit|vercel)\b', content, re.IGNORECASE)
        connections.update([(kw.lower(), 'mentions_project') for kw in keywords])
        
        # 2. Extract imports/sources
        if filename.endswith('.py'):
            connections.update((m, 'imports') for m in re.findall(r'(?:from|import)\s+([\w\.]+)', content))
        elif filename.endswith('.sh'):
            connections.update((m, 'sources') for m in re.findall(r'(?:source|\.)\s+["\']?([^"\';\s]+)', content))
            
        for target, conn_type in connections:
            if target and len(target) > 2:
                self.db.execute("""
                    INSERT INTO connections (source_id, target_keyword, connection_type)
                    VALUES (?, ?, ?)
                """, (file_id, target, conn_type))

    def generate_manifest(self):
        print("📋 Generating Interconnected Manifest...")
        manifest = {"generated": datetime.now().isoformat(), "stats": {}, "hubs": []}
        
        # Stats by location
        cursor = self.db.execute("""
            SELECT location_type, COUNT(*), SUM(size_bytes) 
            FROM artifacts GROUP BY location_type ORDER BY COUNT(*) DESC
        """)
        for loc, count, size in cursor:
            manifest["stats"][loc] = {"count": count, "size_mb": round((size or 0) / 1024 / 1024, 2)}
            
        # Find the "Hubs" (most referenced keywords/files)
        cursor = self.db.execute("""
            SELECT target_keyword, connection_type, COUNT(*) as refs 
            FROM connections 
            GROUP BY target_keyword 
            ORDER BY refs DESC 
            LIMIT 15
        """)
        manifest["hubs"] = [{"keyword": row[0], "type": row[1], "references": row[2]} for row in cursor]
        
        with open(MANIFEST_PATH, 'w') as f:
            json.dump(manifest, f, indent=2)
        return manifest

    def run(self):
        print("=" * 60)
        print("🌌 C25 OMNISCIENT INDEXER (TOTAL RECALL)")
        print("Compiling ALL raw data into a unified knowledge graph.")
        print("=" * 60)
        
        self.scan_and_ingest()
        manifest = self.generate_manifest()
        
        print("\n" + "=" * 60)
        print("✅ TOTAL RECALL COMPLETE")
        print("=" * 60)
        print(f"📊 Database: {DB_PATH}")
        print(f"📋 Manifest: {MANIFEST_PATH}")
        print("\n📈 Ecosystem Breakdown:")
        for loc, stats in manifest["stats"].items():
            print(f"  📍 {loc}: {stats['count']} files ({stats['size_mb']} MB)")
            
        print("\n🔗 Top Interconnected Hubs (The Core of Your System):")
        for hub in manifest["hubs"]:
            print(f"  ↳ '{hub['keyword']}' ({hub['type']}) - referenced {hub['references']} times")

if __name__ == "__main__":
    # Optional: Uncomment next line to force a fresh, complete rebuild of the index
    # if DB_PATH.exists(): DB_PATH.unlink()
    
    indexer = OmniscientIndexer()
    indexer.run()
