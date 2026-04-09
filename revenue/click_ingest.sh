#!/bin/bash
set -euo pipefail
BASE="$HOME/constellation25"
TRACKING="$BASE/revenue/utm_telemetry"

# Parse incoming UTM payload (expects: source, medium, campaign, timestamp)
PAYLOAD_FILE="$1"
if [[ ! -f "$PAYLOAD_FILE" ]]; then
  echo "⚠️ No payload provided. Usage: ./click_ingest.sh <json_payload>"
  exit 1
fi

SOURCE=$(jq -r '.utm_source // "unknown"' "$PAYLOAD_FILE")
TIMESTAMP=$(jq -r '.timestamp // (now | strftime("%Y-%m-%dT%H:%M:%SZ"))' "$PAYLOAD_FILE")
CAMPAIGN=$(jq -r '.utm_campaign // "unknown"' "$PAYLOAD_FILE")

# Append to campaign tracker
LATEST=$(ls -t "$TRACKING"/campaign_*.json 2>/dev/null | head -1)
if [[ -f "$LATEST" ]]; then
  jq --arg src "$SOURCE" --arg ts "$TIMESTAMP" \
     '.clicks += [{"source": $src, "timestamp": $ts, "status": "tracked"}]' \
     "$LATEST" > "$LATEST.tmp" && mv "$LATEST.tmp" "$LATEST"
  echo "✅ Click recorded: $SOURCE | $TIMESTAMP"
fi
