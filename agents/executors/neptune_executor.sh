#!/usr/bin/env bash
set -euo pipefail; export LC_ALL=C
AG=$(basename "$0" _executor.sh | tr '[:lower:]' '[:upper:]' | sed 's/^/Agent_/')
log() { echo "[$(date +%H:%M:%S)] [${AG}] $*" >&2; }
case "${1:-}" in
  scan)     find "${2:-$HOME}" -maxdepth 8 -type f \( -name "*.sh" -o -name "*.py" -o -name "*.json" \) 2>/dev/null | head -n "${3:-100}" ;;
  archive)  tar -czf "${2:-archive.tar.gz}" -C "${3:-$HOME}" "$(basename "${4:-.}")" 2>/dev/null ;;
  validate) [[ "$2" =~ ^https?:// ]] && curl -sfI "$2" &>/dev/null && echo "valid" || echo "invalid" ;;
  dispatch) echo "[Dispatch] Processing queue_depth=$2" ;;
  stream)   echo "{\"metric\":\"${2:-unknown}\",\"value\":${3:-0},\"ts\":$(date +%s)}" >> "${HOME}/constellation25/telemetry/metrics.jsonl" 2>/dev/null ;;
  draft)    echo "PROPOSAL_DRAFT:$2|$3" ;;
  invoice)  echo "INVOICE:$2|$4|$5" >> "${HOME}/constellation25/billing/invoices.csv" 2>/dev/null ;;
  rotate)   ssh-keygen -t ed25519 -f "${2:-$HOME/.ssh/id_ed25519}.new" -N "" -C "c25-$(date +%s)" 2>/dev/null || echo "[KeyGen] Skipped (termux)" ;;
  backup)   mkdir -p "${3:-$HOME/.c25_backup}" && cp "${2:-$HOME/.c25_agent_queue}"/*.json "${3:-$HOME/.c25_backup}/" 2>/dev/null ;;
  *)        log "Unknown task: $1" ;;
esac
