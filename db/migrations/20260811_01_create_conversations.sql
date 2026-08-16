-- Migration: 20260811_01_create_conversations | Agent: Ceres | Owner: CyGeL White
CREATE TABLE IF NOT EXISTS conversations (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  source_file TEXT NOT NULL,
  source_sha256 TEXT NOT NULL UNIQUE,
  title TEXT,
  body_md TEXT NOT NULL,
  body_json TEXT,
  extracted_at TEXT NOT NULL DEFAULT (datetime('now')),
  ingested_by TEXT NOT NULL DEFAULT 'c25-neptune'
);
CREATE INDEX IF NOT EXISTS idx_conversations_sha ON conversations(source_sha256);

CREATE TABLE IF NOT EXISTS dedupe_ledger (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  canonical_path TEXT NOT NULL,
  canonical_sha256 TEXT NOT NULL,
  purged_path TEXT NOT NULL,
  purged_at TEXT NOT NULL DEFAULT (datetime('now'))
);
