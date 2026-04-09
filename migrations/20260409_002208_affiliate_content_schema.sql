BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS affiliate_posts (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  platform TEXT NOT NULL,
  post_content TEXT NOT NULL,
  utm_link TEXT,
  status TEXT DEFAULT 'draft',
  source_script TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_aff_platform_status ON affiliate_posts(platform, status);
COMMIT;
