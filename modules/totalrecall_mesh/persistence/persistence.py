#!/data/data/com.termux/files/usr/bin/python3
"""
Production Persistence Manager
SQLite database for builds, artifacts, snapshots, evidence
"""
import json
import sqlite3
import logging
from pathlib import Path
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s [PERSIST] %(message)s')
logger = logging.getLogger(__name__)

class ProductionPersistence:
    """SQLite-based persistence layer"""
    def __init__(self, db_path=None):
        self.db_path = db_path or str(Path.home() / "constellation25" / "production" / "totalrecall.db")
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self._init_schema()

    def _init_schema(self):
        """Initialize database schema"""
        cursor = self.conn.cursor()
        
        # Builds table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS builds (
                build_id TEXT PRIMARY KEY,
                source_type TEXT,
                target_env TEXT,
                status TEXT,
                queued_at TEXT,
                started_at TEXT,
                completed_at TEXT,
                result TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Artifacts table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS artifacts (
                artifact_id TEXT PRIMARY KEY,
                build_id TEXT,
                source TEXT,
                source_type TEXT,
                hash TEXT,
                size_bytes INTEGER,
                compiled_at TEXT,
                FOREIGN KEY (build_id) REFERENCES builds(build_id)
            )
        """)
        
        # Snapshots table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS snapshots (
                snapshot_id TEXT PRIMARY KEY,
                env_id TEXT,
                taken_at TEXT,
                components INTEGER,
                deployments INTEGER,
                hash TEXT,
                FOREIGN KEY (env_id) REFERENCES environments(env_id)
            )
        """)
        
        # Environments table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS environments (
                env_id TEXT PRIMARY KEY,
                env_type TEXT,
                status TEXT,
                created_at TEXT,
                components INTEGER DEFAULT 0,
                deployments INTEGER DEFAULT 0
            )
        """)
        
        # Evidence table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS evidence (
                evidence_id TEXT PRIMARY KEY,
                source TEXT,
                content TEXT,
                evidence_type TEXT,
                hash TEXT,
                verified INTEGER DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        self.conn.commit()
        logger.info("Database schema initialized")

    def save_build(self, build):
        """Save build to database"""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO builds 
            (build_id, source_type, target_env, status, queued_at, started_at, completed_at, result)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            build.get('build_id'),
            build.get('source_type'),
            build.get('target_env'),
            build.get('status'),
            build.get('queued_at'),
            build.get('started_at'),
            build.get('completed_at'),
            json.dumps(build.get('result', {}))
        ))
        self.conn.commit()
        logger.info(f"Build saved: {build.get('build_id')}")

    def save_artifact(self, artifact, build_id):
        """Save artifact to database"""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO artifacts 
            (artifact_id, build_id, source, source_type, hash, size_bytes, compiled_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            artifact.get('artifact_id'),
            build_id,
            artifact.get('source', '')[:500],
            artifact.get('source_type'),
            artifact.get('hash'),
            artifact.get('size_bytes'),
            artifact.get('compiled_at')
        ))
        self.conn.commit()

    def save_snapshot(self, snapshot, env_id):
        """Save snapshot to database"""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO snapshots 
            (snapshot_id, env_id, taken_at, components, deployments, hash)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            snapshot.get('snapshot_id'),
            env_id,
            snapshot.get('taken_at'),
            snapshot.get('components'),
            snapshot.get('deployments'),
            snapshot.get('hash')
        ))
        self.conn.commit()

    def save_environment(self, env):
        """Save environment to database"""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO environments 
            (env_id, env_type, status, created_at, components, deployments)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            env.get('env_id'),
            env.get('env_type'),
            env.get('status'),
            env.get('created_at'),
            env.get('components', 0),
            env.get('deployments', 0)
        ))
        self.conn.commit()

    def save_evidence(self, evidence):
        """Save evidence to database"""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO evidence 
            (evidence_id, source, content, evidence_type, hash, verified)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            evidence.get('evidence_id'),
            evidence.get('source'),
            evidence.get('content', '')[:1000],
            evidence.get('evidence_type'),
            evidence.get('hash'),
            1 if evidence.get('verified') else 0
        ))
        self.conn.commit()

    def get_build(self, build_id):
        """Get build by ID"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM builds WHERE build_id = ?", (build_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

    def get_all_builds(self, limit=100):
        """Get all builds"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM builds ORDER BY created_at DESC LIMIT ?", (limit,))
        return [dict(row) for row in cursor.fetchall()]

    def get_stats(self):
        """Get database statistics"""
        cursor = self.conn.cursor()
        stats = {}
        for table in ['builds', 'artifacts', 'snapshots', 'environments', 'evidence']:
            cursor.execute(f"SELECT COUNT(*) as count FROM {table}")
            stats[table] = cursor.fetchone()['count']
        return stats

if __name__ == "__main__":
    persist = ProductionPersistence()
    print("=== PRODUCTION PERSISTENCE MANAGER ===\n")
    print(f"Database: {persist.db_path}")
    print(f"Stats: {persist.get_stats()}")
