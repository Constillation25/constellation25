#!/data/data/com.termux/files/usr/bin/bash
# C25 PROTOCOL: TASK EXECUTION, LEDGER LOGGING, AND NOTIFICATION

TASK_ID="$1"
AGENT_NAME="$2"
COMMAND_PAYLOAD="$3"
LEDGER="$HOME/constellation25/logs/task256_ledger.csv"
SANDBOX="$HOME/constellation25/bashbox/sandbox/${TASK_ID}.sh"
NOTIFY_SCRIPT="$HOME/constellation25/core/c25_notify.py"

if [ -z "$TASK_ID" ] || [ -z "$AGENT_NAME" ] || [ -z "$COMMAND_PAYLOAD" ]; then
    echo "Usage: c25_task_executor.sh <task_id> <agent_name> '<command_payload>'"
    exit 1
fi

TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

# 1. Log to task256 Ledger (Pending State)
echo "${TASK_ID},${AGENT_NAME},\"${COMMAND_PAYLOAD//\"/\\\"}\",${TIMESTAMP},PENDING," >> "$LEDGER"

# 2. Write command to Bashbox Sandbox
echo "#!/data/data/com.termux/files/usr/bin/bash" > "$SANDBOX"
echo "$COMMAND_PAYLOAD" >> "$SANDBOX"
chmod +x "$SANDBOX"

# 3. Execute in Sandbox
echo "[EXEC] Running $TASK_ID for $AGENT_NAME in Bashbox..."
OUTPUT=$(bash "$SANDBOX" 2>&1)
EXIT_CODE=$?

# 4. Determine Status and Details
if [ $EXIT_CODE -eq 0 ]; then
    STATUS="SUCCESS"
    DETAILS="Execution successful. Output: ${OUTPUT:0:500}" # Truncate for email safety
else
    STATUS="FAILED"
    DETAILS="Execution failed with code $EXIT_CODE. Error: ${OUTPUT:0:500}"
fi

# 5. Update Ledger with Completion Details
# Escape commas and quotes in details for CSV integrity
SAFE_DETAILS="${DETAILS//\"/\\\"}"
SAFE_DETAILS="${SAFE_DETAILS//,/;}"
sed -i "s/${TASK_ID},${AGENT_NAME},.*PENDING,/${TASK_ID},${AGENT_NAME},\"${COMMAND_PAYLOAD//\"/\\\"}\",${TIMESTAMP},${STATUS},\"${SAFE_DETAILS}\"/" "$LEDGER"

# 6. Trigger Termux Toast & Email Notification
python3 "$NOTIFY_SCRIPT" "$TASK_ID" "$AGENT_NAME" "$DETAILS" "$STATUS"

# 7. Cleanup Sandbox (Optional: comment out to keep for forensic logging)
rm -f "$SANDBOX"

echo "[DONE] $TASK_ID processed. Ledger and notifications updated."
