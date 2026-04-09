#!/bin/bash
# Local fallback processor for offline C25 agent simulation
set -euo pipefail
BASE="$HOME/constellation25"
QUEUE="$BASE/tasks/pending"

for task_file in "$QUEUE"/*.json; do
  [[ -f "$task_file" ]] || continue
  echo "🤖 Processing: $(basename "$task_file")"
  # Simulate agent execution timestamps
  echo "$(date -Iseconds) | AGENT_SIM | $(basename "$task_file") | status:queued" >> "$BASE/logs/local_agent_sim.log"
done
echo "✅ Local queue processed. Review: $BASE/logs/local_agent_sim.log"
