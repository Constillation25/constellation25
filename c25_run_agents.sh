#!/usr/bin/env bash
set -euo pipefail; export LC_ALL=C
BASE="${HOME}/constellation25"
QUEUE="${HOME}/.c25_agent_queue"
MCP_PID_FILE="${BASE}/.mcp_pid"
PORT=8765

start_mcp() {
  if pgrep -f "mcp_ollama_bridge.py" &>/dev/null; then
    echo "[MCP] Already running"
  else
    python3 "${BASE}/mcp_ollama/mcp_ollama_bridge.py" &>/dev/null &
    echo $! > "${MCP_PID_FILE}"
    sleep 1
    echo "[MCP] Started on :${PORT}"
  fi
}

stop_mcp() {
  [[ -f "${MCP_PID_FILE}" ]] && kill "$(cat "${MCP_PID_FILE}")" 2>/dev/null || true
  pkill -f "mcp_ollama_bridge.py" 2>/dev/null || true
  echo "[MCP] Stopped"
}

status_mcp() {
  curl -s "http://localhost:${PORT}/status" 2>/dev/null || echo "[MCP] Offline"
}

run_tasks() {
  start_mcp
  echo "[Dispatch] Triggering queue processing..."
  curl -s -X POST "http://localhost:${PORT}/process" 2>/dev/null
  echo ""
  echo "[Dispatch] Queue processed. Checking results..."
  completed=$(grep -c '"status":"completed"' "${QUEUE}"/*.json 2>/dev/null || echo 0)
  pending=$(grep -c '"status":"pending"' "${QUEUE}"/*.json 2>/dev/null || echo 0)
  echo "✅ Completed: ${completed} | ⏳ Pending: ${pending}"
}

case "${1:-run}" in
  start) start_mcp ;;
  stop) stop_mcp ;;
  status) status_mcp ;;
  run) run_tasks ;;
  *) echo "Usage: $0 {start|stop|status|run}" ;;
esac
