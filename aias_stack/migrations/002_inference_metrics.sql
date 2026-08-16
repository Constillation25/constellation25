CREATE TABLE IF NOT EXISTS inference_metrics (
    id TEXT PRIMARY KEY,
    model_id TEXT NOT NULL,
    provider TEXT NOT NULL,
    tokens_in INTEGER,
    tokens_out INTEGER,
    latency_ms INTEGER,
    throughput_tps REAL,              -- Target: 60% faster than direct OpenAI
    encrypted BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
