-- Migration: 001_init_finds_schema
-- Agent: Ceres 🪨 (Database Architecture)
CREATE TABLE IF NOT EXISTS magnet_finds (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    latitude REAL NOT NULL,
    longitude REAL NOT NULL,
    zone TEXT NOT NULL CHECK(zone IN ('springs', 'vacant_lot_right', 'hill_house', 'lake_edge', 'pathways')),
    depth_inches INTEGER,
    object_description TEXT,
    estimated_era TEXT,
    recovered BOOLEAN DEFAULT 0
);

CREATE INDEX IF NOT EXISTS idx_finds_zone ON magnet_finds(zone);
