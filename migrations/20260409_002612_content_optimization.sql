BEGIN TRANSACTION;
ALTER TABLE affiliate_posts ADD COLUMN optimized_at TIMESTAMP;
ALTER TABLE affiliate_posts ADD COLUMN ftcompliance_verified BOOLEAN DEFAULT FALSE;
CREATE INDEX IF NOT EXISTS idx_aff_opt_status ON affiliate_posts(status, optimized_at);
COMMIT;
