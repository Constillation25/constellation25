#!/data/data/com.termux/files/usr/bin/bash
echo "🛑 Stopping all Constellation25 agents..."

pkill -f "stalker_global.sh" 2>/dev/null && echo "  Stalker stopped"
pkill -f "c25_orchestrator.py" 2>/dev/null && echo "  Orchestrator stopped"
pkill -f "streamlit" 2>/dev/null && echo "  Streamlit stopped"

rm -f ~/constellation25/stalker_global.pid 2>/dev/null
echo "✅ All agents stopped"
