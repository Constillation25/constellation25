#!/data/data/com.termux/files/usr/bin/bash
C25_ROOT="${C25_ROOT:-${HOME}/constellation25}"
SGTP_ROOT="${C25_ROOT}/sovereign-gtp"
clear
echo "🌍 SovereignGTP Task Monitor"
echo "============================"
while true; do
    INCOMING=$(ls "${SGTP_ROOT}/tasks/incoming"/*.json 2>/dev/null | wc -l)
    PROCESSED=$(ls "${SGTP_ROOT}/tasks/processed"/*.json 2>/dev/null | wc -l)
    OUTPUTS=$(ls "${SGTP_ROOT}/outputs"/*.* 2>/dev/null | wc -l)
    AGENTS=0
    for pid_file in "${SGTP_ROOT}/pids"/*.pid; do
        [ -f "$pid_file" ] || continue
        pid=$(cat "$pid_file")
        if kill -0 "$pid" 2>/dev/null; then
            AGENTS=$((AGENTS + 1))
        fi
    done
    echo "📥 Incoming:  ${INCOMING}"
    echo "✅ Processed: ${PROCESSED}"
    echo "📄 Outputs:   ${OUTPUTS}"
    echo "🤖 Agents:    ${AGENTS}/25"
    echo ""
    echo "🕐 Recent Activity (last 5):"
    tail -5 "${SGTP_ROOT}/logs/totalrecall.log" 2>/dev/null | while read line; do
        echo "   $line"
    done
    echo ""
    echo "Press Ctrl+C to exit"
    echo "────────────────────────────────"
    sleep 5
    clear
    echo "🌍 SovereignGTP Task Monitor"
    echo "============================"
done
