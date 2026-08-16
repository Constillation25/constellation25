#!/bin/bash
set -e
DB_PATH="$HOME/constellation25/.state/c25_sovereign_ledger.db"
LOG_FILE="$HOME/constellation25/.logs/task_redeploy.log"

echo "[*] Initiating C25 Master Task Redeployment..." | tee -a "$LOG_FILE"

# Define all canonical task scripts
SCRIPTS=(
  "agents/execute_task.py"
  "agents/run_all_tasks.sh"
  "agents/yesquid_task_worker.sh"
  "task_box.sh"
  "sovereign-gtp/send_task.sh"
  "sovereign-gtp/monitor_tasks.sh"
)

for script in "${SCRIPTS[@]}"; do
  if [ -f "$script" ]; then
    echo "[*] Processing: $script" | tee -a "$LOG_FILE"
    
    # Register task in ledger
    TASK_ID="redeploy_$(basename "$script" | sed 's/\..*//')_$(date +%s)"
    sqlite3 "$DB_PATH" "INSERT OR IGNORE INTO c25_ipc_queue (task_id, agent_id, action, status) VALUES ('$TASK_ID', 'Earth', 'execute_script', 'pending');"
    
    # Execute script
    if [[ "$script" == *.py ]]; then
      python3 "$script" >> "$LOG_FILE" 2>&1 && echo "[+] $script executed successfully" | tee -a "$LOG_FILE"
    else
      bash "$script" >> "$LOG_FILE" 2>&1 && echo "[+] $script executed successfully" | tee -a "$LOG_FILE"
    fi
    
    # Mark completed
    sqlite3 "$DB_PATH" "UPDATE c25_ipc_queue SET status='completed' WHERE task_id='$TASK_ID';"
  else
    echo "[-] Skipping missing: $script" | tee -a "$LOG_FILE"
  fi
done

echo "[+] Master Task Redeployment Complete." | tee -a "$LOG_FILE"
