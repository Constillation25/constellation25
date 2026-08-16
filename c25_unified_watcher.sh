#!/bin/bash
# C25 Unified Watcher: Monitors IPC queue and triggers worker atomically
DB_PATH="$HOME/constellation25/.state/c25_sovereign_ledger.db"
LOG_FILE="$HOME/constellation25/.logs/watcher.log"

echo "[$(date)] Watcher initialized." >> "$LOG_FILE"

while true; do
    # Check for pending tasks
    PENDING=$(sqlite3 "$DB_PATH" "SELECT COUNT(*) FROM c25_ipc_queue WHERE status='pending';")
    
    if [ "$PENDING" -gt 0 ]; then
        echo "[$(date)] Detected $PENDING pending tasks. Triggering worker..." >> "$LOG_FILE"
        bash "$HOME/constellation25/c25_agent_worker.sh" >> "$LOG_FILE" 2>&1
    fi
    
    # Sleep for 5 seconds before next check (low CPU footprint)
    sleep 5
done
