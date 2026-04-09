BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS content_optimization_log (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  batch_timestamp TEXT NOT NULL,
  platform TEXT NOT NULL,
  file_path TEXT NOT NULL,
  optimization_status TEXT DEFAULT 'queued',
  utm_campaign TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
COMMIT;
