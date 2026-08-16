#!/data/data/com.termux/files/usr/bin/bash
# ============================================================
# CONSTELLATION25 - Stalker Global Agent (Watchdog)
# Version: 28.1
# ============================================================

BASE_DIR="$HOME/constellation25"
LOG_DIR="$BASE_DIR/logs"
LOG_FILE="$LOG_DIR/stalker_global.log"
PID_FILE="$BASE_DIR/stalker_global.pid"
ORCHESTRATOR="$BASE_DIR/c25_orchestrator.py"
CHECK_INTERVAL=30

mkdir -p "$LOG_DIR"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

cleanup() {
    log "🛑 Stalker Global Agent shutting down..."
    rm -f "$PID_FILE"
    exit 0
}

trap cleanup SIGINT SIGTERM

# Save own PID
echo $$ > "$PID_FILE"

log "🌌 Stalker Global Agent started (PID: $$)"
log "Monitoring directory: $BASE_DIR"

# Function to check if orchestrator is running
is_orchestrator_running() {
    pgrep -f "c25_orchestrator.py" > /dev/null
    return $?
}

# Function to start orchestrator
start_orchestrator() {
    log "⚡ Starting c25_orchestrator.py..."
    cd "$BASE_DIR"
    nohup python3 "$ORCHESTRATOR" >> "$LOG_DIR/orchestrator_bg.log" 2>&1 &
    sleep 2
    if is_orchestrator_running; then
        log "✅ Orchestrator started successfully"
    else
        log "❌ Failed to start orchestrator"
    fi
}

# Main monitoring loop
while true; do
    if is_orchestrator_running; then
        log "💚 Orchestrator is online"
    else
        log "⚠️ Orchestrator is DOWN — restarting..."
        start_orchestrator
    fi

    # Optional: Check circuit breaker state
    if [ -f "$BASE_DIR/config/circuit_state.json" ]; then
        log "📊 Circuit state file present"
    fi

    sleep $CHECK_INTERVAL
done
