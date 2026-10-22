#!/bin/bash
IPC_COMPLETED="$HOME/c25_ipc/completed"
IPC_ARCHIVE="$HOME/c25_ipc/archive"
LOG_DIR="$HOME/constellation25/logs"
NOTIFY="$HOME/constellation25/core/commz/c25-notify.sh"
HEARTBEAT_LOG="$LOG_DIR/watcher_health.log"
LAST_HEARTBEAT=0

mkdir -p "$IPC_ARCHIVE" "$LOG_DIR"

echo "[$(date)] C25 Watcher started (PID $$)" >> "$HEARTBEAT_LOG"

while true; do
  # Heartbeat every 300 seconds (5 min)
  NOW=$(date +%s)
  if (( NOW - LAST_HEARTBEAT >= 300 )); then
    echo "[$(date)] HEARTBEAT OK (PID $$)" >> "$HEARTBEAT_LOG"
    LAST_HEARTBEAT=$NOW
  fi

  # Poll completed directory
  for FILE in "$IPC_COMPLETED"/*.json; do
    [ -f "$FILE" ] || continue

    AGENT=$(jq -r '.agent // "Unknown"' "$FILE" 2>/dev/null)
    RESULT=$(jq -r '.result // .status // "Completed"' "$FILE" 2>/dev/null)
    ACTION=$(jq -r '.action // "task"' "$FILE" 2>/dev/null)

    # Fire notification
    bash "$NOTIFY" "$AGENT" "$RESULT" "$ACTION"

    # Archive to prevent duplicate fires
    mv "$FILE" "$IPC_ARCHIVE/$(basename "$FILE").$(date +%s)"
  done

  sleep 3
done
