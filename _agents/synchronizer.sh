#!/data/data/com.termux/files/usr/bin/bash
BASE="$HOME/github-repos/Constillation25"
LOG="$BASE/_logs/sync.log"
CFG="$BASE/_config/endpoints.json"

echo "[SYNC] $(date)" | tee "$LOG"

SYNCED=0
for d in "$BASE"/*/; do
  REPO=$(basename "$d")
  [[ "$REPO" == _* || "$REPO" == .* ]] && continue
  cd "$d" || continue

  CHANGES=$(git status --porcelain 2>/dev/null | grep -v '\.bak$' | wc -l)
  if [ "$CHANGES" -gt 0 ]; then
    git add -A 2>/dev/null
    git commit -m "🌌 Constellation25: unified patch [$(date '+%Y-%m-%d %H:%M')]" >> "$LOG" 2>&1
    echo "  ✓ Committed: $REPO ($CHANGES changes)" | tee -a "$LOG"
    SYNCED=$((SYNCED+1))
  fi

  REMOTE=$(git remote -v 2>/dev/null | wc -l)
  [ "$REMOTE" -gt 0 ] && git pull --rebase --quiet 2>>"$LOG"
  cd "$BASE"
done

# Backend sync
SYNC_URL=$(python3 -c "
import json,os
try: print(json.load(open('$CFG')).get('sync_endpoint',''))
except: print('')
" 2>/dev/null)

if [ -n "$SYNC_URL" ]; then
  HEALTH_URL=$(python3 -c "
import json,os
try: print(json.load(open('$CFG')).get('health_check',''))
except: print('')
" 2>/dev/null)
  ONLINE=$(curl -s --connect-timeout 3 "$HEALTH_URL" 2>/dev/null)
  if [ -n "$ONLINE" ]; then
    PAYLOAD="{\"agent\":\"synchronizer\",\"repos_synced\":$SYNCED,\"timestamp\":\"$(date -u +%Y-%m-%dT%H:%M:%SZ)\"}"
    curl -s -X POST "$SYNC_URL" -H "Content-Type: application/json" -d "$PAYLOAD" >> "$LOG" 2>&1
    echo "  ✓ Platform sync sent to $SYNC_URL" | tee -a "$LOG"
  else
    echo "  ⚠ Backend offline — git-only sync" | tee -a "$LOG"
  fi
fi

echo "[SYNC] $SYNCED repos synced" | tee -a "$LOG"
echo "✓ SYNCHRONIZER complete"
