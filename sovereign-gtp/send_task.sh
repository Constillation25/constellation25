#!/data/data/com.termux/files/usr/bin/bash
set -e
if [ $# -lt 3 ]; then
    echo "Usage: $0 <agent> <task_type> <payload>"
    echo "Example: $0 helio A_landing_page 'Generate hero section'"
    exit 1
fi
AGENT="$1"
TASK_TYPE="$2"
PAYLOAD="$3"
TIMESTAMP=$(date -Iseconds)
TASK_ID="${AGENT}_$(date +%s)_${RANDOM}"
C25_ROOT="${C25_ROOT:-${HOME}/constellation25}"
TASKS_DIR="${C25_ROOT}/sovereign-gtp/tasks/incoming"

cat > "${TASKS_DIR}/${TASK_ID}.json" << TASKJSON
{
  "task_id": "${TASK_ID}",
  "agent": "${AGENT}",
  "type": "${TASK_TYPE}",
  "payload": "${PAYLOAD}",
  "timestamp": "${TIMESTAMP}",
  "sender": "cli",
  "priority": "normal"
}
TASKJSON

echo "📤 Task sent to ${AGENT}: ${TASK_TYPE}"
echo "   ID: ${TASK_ID}"
echo "   Queue: ${TASKS_DIR}/${TASK_ID}.json"
