CREATE TABLE IF NOT EXISTS c25_ledger (
    id TEXT PRIMARY KEY,
    timestamp INTEGER NOT NULL,
    event_type TEXT NOT NULL,
    payload TEXT,
    signature TEXT
);
CREATE TABLE IF NOT EXISTS sovereign_licenses (
    license_key TEXT PRIMARY KEY,
    tier TEXT CHECK(tier IN ('Indie', 'Enterprise', 'Lifetime_NFT')),
    owner_id TEXT,
    created_at INTEGER DEFAULT (strftime('%s', 'now'))
);
