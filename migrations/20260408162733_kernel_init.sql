-- CONSTELLATION25 KERNEL INITIALIZATION MIGRATION
BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS c25_kernel_registry (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    version TEXT NOT NULL UNIQUE,
    archive_hash TEXT NOT NULL,
    deployed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    status TEXT DEFAULT 'pending_validation'
);
CREATE TABLE IF NOT EXISTS c25_agent_tasks (
    task_id TEXT PRIMARY KEY,
    agent_name TEXT NOT NULL,
    action TEXT NOT NULL,
    priority TEXT CHECK(priority IN ('critical','high','standard','low')),
    completed INTEGER DEFAULT 0
);
COMMIT;
