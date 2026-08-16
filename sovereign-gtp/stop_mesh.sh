#!/data/data/com.termux/files/usr/bin/bash
set -e
C25_ROOT="${C25_ROOT:-${HOME}/constellation25}"
PIDS_DIR="${C25_ROOT}/sovereign-gtp/pids"
echo "🛑 Stopping SovereignGTP mesh..."
for pid_file in "${PIDS_DIR}"/*.pid; do
    [ -f "$pid_file" ] || continue
    agent=$(basename "$pid_file" .pid)
    pid=$(cat "$pid_file")
    if kill -0 "$pid" 2>/dev/null; then
        echo "  ✓ Stopping ${agent} (PID: ${pid})"
        kill "$pid" 2>/dev/null || true
        rm -f "$pid_file"
    fi
done
rm -f "${PIDS_DIR}"/*.pid 2>/dev/null || true
echo ""
echo "🟡 Mesh OFFLINE"
echo "   Logs preserved in: ${C25_ROOT}/sovereign-gtp/logs/"
echo "   Outputs preserved in: ${C25_ROOT}/sovereign-gtp/outputs/"
