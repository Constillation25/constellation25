CREATE TABLE c25_ipc_queue (
    task_id TEXT PRIMARY KEY,
    agent_id TEXT NOT NULL,
    action TEXT NOT NULL,
    payload TEXT,
    status TEXT DEFAULT 'pending'
);
