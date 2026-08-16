#!/usr/bin/env bash
# C25 Task Drain Worker - Yesquid Plan Executor
set -euo pipefail

C25_ROOT="${HOME}/constellation25"
WORKER="${C25_ROOT}/agents/yesquid_task_worker.sh"
PLAN_ID="${1:-52f7b763}"
MAX_DRAIN_LIMIT=5000 # Safety valve against infinite loops
BATCH_COUNT=0

# Pre-flight: Verify worker exists and is executable
if [[ ! -x "$WORKER" ]]; then
  echo "❌ FATAL: Worker not found or not executable at ${WORKER}"
  echo "💡 Fix: chmod +x ${WORKER}"
  exit 1
fi

echo "🚀 [C25-Earth] Starting task drain for Plan: ${PLAN_ID}"

while [[ $BATCH_COUNT -lt $MAX_DRAIN_LIMIT ]]; do
  # If worker exits non-zero (queue empty or error), break loop
  if ! "$WORKER" "$PLAN_ID"; then
    break
  fi
  ((BATCH_COUNT++))
done

if [[ $BATCH_COUNT -ge $MAX_DRAIN_LIMIT ]]; then
  echo "⚠️ WARNING: Hit max drain limit (${MAX_DRAIN_LIMIT}). Check worker logs."
else
  echo "✅ [C25-Earth] Finished draining ${BATCH_COUNT} batches for plan ${PLAN_ID}"
fi
