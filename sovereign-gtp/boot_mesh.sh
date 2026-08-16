#!/data/data/com.termux/files/usr/bin/bash
set -e
C25_ROOT="${C25_ROOT:-${HOME}/constellation25}"
SGTP_ROOT="${C25_ROOT}/sovereign-gtp"
LOGS_DIR="${SGTP_ROOT}/logs"
PIDS_DIR="${SGTP_ROOT}/pids"

echo "🌍 SovereignGTP - Constellation25 Boot"
echo "======================================="

if [ ! -d "${SGTP_ROOT}/agents" ]; then
    echo "❌ Error: SovereignGTP not installed at ${SGTP_ROOT}"
    exit 1
fi

echo "✓ Environment ready"
mkdir -p "${LOGS_DIR}" "${PIDS_DIR}" "${SGTP_ROOT}/tasks/incoming" "${SGTP_ROOT}/tasks/processed" "${SGTP_ROOT}/outputs"

echo "✓ TotalRecall started"
python3 "${SGTP_ROOT}/totalrecall/logger.py" --daemon > "${LOGS_DIR}/totalrecall.log" 2>&1 &
echo $! > "${PIDS_DIR}/totalrecall.pid"

ACTIVE_AGENTS=("helio" "vault" "echo" "chronos" "mercury" "venus" "earth" "mars")
for agent in "${ACTIVE_AGENTS[@]}"; do
    if [ -f "${SGTP_ROOT}/agents/${agent}.py" ]; then
        python3 "${SGTP_ROOT}/agents/${agent}.py" > "${LOGS_DIR}/${agent}.log" 2>&1 &
        echo $! > "${PIDS_DIR}/${agent}.pid"
        echo "✓ ${agent} started (PID: $(cat ${PIDS_DIR}/${agent}.pid))"
    fi
done

echo ""
echo "🟢 Mesh ONLINE - $(ls ${PIDS_DIR}/*.pid 2>/dev/null | wc -l) processes running"
echo "📊 Monitor: ./monitor_tasks.sh"
echo "📤 Send: ./send_task.sh helio A_landing_page 'Your task'"
echo "🛑 Stop: ./stop_mesh.sh"
