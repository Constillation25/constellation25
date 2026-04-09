#!/usr/bin/env bash
set -euo pipefail; export LC_ALL=C
BASE="${HOME}/constellation25"
AGENT_DIR="${BASE}/agents/executors"
QUEUE_DIR="${HOME}/.c25_agent_queue"
LOG="${BASE}/dispatch.log"
: > "${LOG}"
log() { echo "[$(date +%H:%M:%S)] [Dispatch] $*" | tee -a "${LOG}"; }

process_queue() {
  local count=0
  for task_file in "${QUEUE_DIR}"/*.json; do
    [[ -f "${task_file}" ]] || continue
    agent=$(grep -o '"agent":"[^"]*"' "${task_file}" 2>/dev/null | cut -d'"' -f4 || echo "unknown")
    task=$(grep -o '"task":"[^"]*"' "${task_file}" 2>/dev/null | cut -d'"' -f4 || echo "unknown")
    priority=$(grep -o '"priority":"[^"]*"' "${task_file}" 2>/dev/null | cut -d'"' -f4 || echo "standard")
    
    executor="${AGENT_DIR}/${agent,,}_executor.sh"
    if [[ -x "${executor}" ]]; then
      log "EXEC" "[${priority}] ${agent} → ${task}"
      "${executor}" "${task}" 2>&1 | tee -a "${LOG}" || log "WARN: ${agent} executor failed"
      sed -i 's/"status":"pending"/"status":"completed"/' "${task_file}" 2>/dev/null || true
      count=$((count + 1))
    else
      log "SKIP" "No executor for ${agent} (standby)"
    fi
  done
  log "COMPLETE" "Processed ${count} tasks"
}

case "${1:-run}" in
  run) process_queue ;;
  list)
    echo "=== PENDING TASKS ==="
    for f in "${QUEUE_DIR}"/*.json; do
      [[ -f "${f}" ]] || continue
      echo "- $(basename "${f}"): $(grep -o '"agent":"[^"]*"' "${f}" | cut -d'"' -f4) → $(grep -o '"task":"[^"]*"' "${f}" | cut -d'"' -f4)"
    done
    ;;
  status)
    echo "=== AGENT STATUS ==="
    for agent in earth neptune jupiter ceres mars venus saturn mercury uranus pluto; do
      exec="${AGENT_DIR}/${agent}_executor.sh"
      if [[ -x "${exec}" ]]; then echo "✅ ${agent}: ready"; else echo "⏳ ${agent}: standby"; fi
    done
    ;;
  *) log "Usage: $0 {run|list|status}" ;;
esac
