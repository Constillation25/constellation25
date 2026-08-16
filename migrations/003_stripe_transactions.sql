-- Migration: Stripe Transaction & Webhook Ledger
CREATE TABLE IF NOT EXISTS c25_stripe_txns (
    txn_id TEXT PRIMARY KEY,
    intent_id TEXT,
    amount INTEGER,
    currency TEXT,
    status TEXT,
    agent_origin TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_intent ON c25_stripe_txns(intent_id);
