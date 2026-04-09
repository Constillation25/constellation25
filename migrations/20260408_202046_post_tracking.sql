-- Migration: Affiliate Post Performance Tracking
BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS post_metrics (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  platform TEXT NOT NULL,
  post_file TEXT UNIQUE,
  utm_link TEXT,
  clicks INTEGER DEFAULT 0,
  conversions REAL DEFAULT 0.0,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_post_platform ON post_metrics(platform);
COMMIT;
