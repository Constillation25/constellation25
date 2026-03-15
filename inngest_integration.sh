#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail
LOG="$HOME/.constellation25/swarm.log"
mkdir -p "$(dirname "$LOG")"
log() { echo "[$(date "+%H:%M:%S")] $1" | tee -a "$LOG"; }
log "🌌 Constellation 25: Inngest Integration Started"
export INNGEST_EVENT_KEY="${INNGEST_EVENT_KEY:-dev_event_1772576417"}"
export INNGEST_SIGNING_KEY="${INNGEST_SIGNING_KEY:-dev_sign_6d91c30483b8653b22e0e3168468296b"}"
log "✅ Keys configured"
export INNGEST_DEV=1
export INNGEST_BASE_URL="http://localhost:8288"
log "🔗 Environment ready for self-hosted Inngest"
echo "✅ Integration complete. Next: cd ~/constellation25/inngest-project && ./start.sh"
