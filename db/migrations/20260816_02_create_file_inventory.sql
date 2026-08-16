-- Migration: 20260816_02_create_file_inventory | Agent: Ceres | Owner: CyGeL White
CREATE TABLE IF NOT EXISTS file_inventory (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  path TEXT NOT NULL UNIQUE,
  size INTEGER NOT NULL,
  mtime INTEGER NOT NULL,
  ext TEXT,
  category TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_inv_cat ON file_inventory(category);
CREATE INDEX IF NOT EXISTS idx_inv_path ON file_inventory(path);
