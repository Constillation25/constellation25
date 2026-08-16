#!/data/data/com.termux/files/usr/bin/bash
set -e
if [ $# -lt 2 ]; then
    echo "Usage: $0 <agent> <category> [batch_size] [delay_seconds]"
    exit 1
fi
AGENT="$1"
CATEGORY="$2"
BATCH_SIZE="${3:-25}"
DELAY="${4:-0.1}"
C25_ROOT="${C25_ROOT:-${HOME}/constellation25}"
BATCH_FILE="${C25_ROOT}/sovereign-gtp/batches/${CATEGORY}.txt"
TASKS_DIR="${C25_ROOT}/sovereign-gtp/tasks/incoming"

if [ ! -f "${BATCH_FILE}" ]; then
    echo "❌ Batch file not found: ${BATCH_FILE}"
    exit 1
fi

echo "📦 Sending ${CATEGORY} tasks to ${AGENT}..."
COUNT=0
while IFS= read -r payload; do
    [ -z "$payload" ] && continue
    TIMESTAMP=$(date -Iseconds)
    TASK_ID="${AGENT}_${CATEGORY}_$(date +%s)_${RANDOM}"
    cat > "${TASKS_DIR}/${TASK_ID}.json" << TASKJSON
{
  "task_id": "${TASK_ID}",
  "agent": "${AGENT}",
  "type": "${CATEGORY}",
  "payload": "${payload}",
  "timestamp": "${TIMESTAMP}",
  "sender": "batch",
  "priority": "normal"
}
TASKJSON
    COUNT=$((COUNT + 1))
    if [ $((COUNT % BATCH_SIZE)) -eq 0 ]; then
        echo "  ✓ Sent ${COUNT} tasks..."
        sleep "$DELAY"
    fi
done < "${BATCH_FILE}"
echo "🎯 Complete: ${COUNT} tasks queued for ${AGENT}"
