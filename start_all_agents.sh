#!/data/data/com.termux/files/usr/bin/bash
# CONSTELLATION25 - Launch All Agents + Listener in Background

BASE_DIR="$HOME/constellation25"
LOG_DIR="$BASE_DIR/logs"
mkdir -p "$LOG_DIR" "$BASE_DIR/incoming"

cd "$BASE_DIR"

echo "🌌 CONSTELLATION25 // LAUNCHING ALL AGENTS + LISTENER"
echo "===================================================="

# Stop previous instances
pkill -f "stalker_global.sh" 2>/dev/null
pkill -f "c25_orchestrator.py" 2>/dev/null
pkill -f "agents/listener.sh" 2>/dev/null
sleep 1

# 1. Stalker Global (Watchdog)
nohup ./stalker_global.sh >> "$LOG_DIR/stalker_global.log" 2>&1 &
echo "✅ Stalker Global started (PID $!)"

# 2. Earth Orchestrator
nohup python3 c25_orchestrator.py >> "$LOG_DIR/orchestrator_bg.log" 2>&1 &
echo "✅ Orchestrator started (PID $!)"

# 3. Agent Listener (watches for incoming tasks)
nohup ./agents/listener.sh >> "$LOG_DIR/listener.log" 2>&1 &
echo "✅ Agent Listener started (PID $!)"

sleep 2
echo ""
echo "All systems running in background."
echo "Drop files into: $BASE_DIR/incoming/"
echo ""
echo "Useful commands:"
echo "  ./status_agents.sh"
echo "  tail -f logs/listener.log"
echo "  ./stop_all_agents.sh"
