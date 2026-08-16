-- ZERO DATA RETENTION: We only store cryptographic hashes, never raw prompts/completions.
CREATE TABLE IF NOT EXISTS sovereign_audit_ledger (
    id TEXT PRIMARY KEY,
    task_hash TEXT NOT NULL,          -- SHA-256 hash of the original prompt
    agents_involved TEXT,             -- JSON array of agent IDs dispatched
    chairman_winner TEXT,             -- Winning agent ID
    confidence_score REAL,            -- Chairman LLM evaluation score
    output_hash TEXT NOT NULL,        -- SHA-256 hash of the winning code/PR
    pr_url TEXT,                      -- Auto-generated PR link
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
