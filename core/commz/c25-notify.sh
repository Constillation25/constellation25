#!/bin/bash
source "$HOME/constellation25/core/commz/.env"

AGENT_NAME="$1"
TASK_STATUS="$2"
TASK_ACTION="$3"

MSG="🪐 [C25 ALERT]
Agent: $AGENT_NAME
Action: $TASK_ACTION
Status: $TASK_STATUS
Time: $(date '+%Y-%m-%d %H:%M:%S')"

# Primary: Telegram
if [ "$BOT_TOKEN" != "YOUR_BOT_TOKEN_HERE" ]; then
  curl -s -X POST "https://api.telegram.org/bot${BOT_TOKEN}/sendMessage" \
    -d "chat_id=${CHAT_ID}" \
    -d "text=${MSG}" \
    -d "parse_mode=HTML" > /dev/null 2>&1
  echo "[$(date)] SENT via Telegram: $AGENT_NAME" >> "$HOME/constellation25/logs/commz_audit.log"
else
  # Fallback: Termux SMS
  termux-sms-send -n "$PHONE_NUMBER" "$MSG" 2>/dev/null
  echo "[$(date)] SENT via SMS: $AGENT_NAME" >> "$HOME/constellation25/logs/commz_audit.log"
fi
