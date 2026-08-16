-- ARTie DEPLOYMENT LEDGER: Tracks every artifact pushed to production
CREATE TABLE IF NOT EXISTS artie_deployment_ledger (
    id TEXT PRIMARY KEY,
    artifact_name TEXT NOT NULL,
    target_directory TEXT NOT NULL,
    deployed_by_agent TEXT NOT NULL,
    sha256_hash TEXT NOT NULL,
    deployed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
