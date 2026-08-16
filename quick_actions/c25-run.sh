#!/data/data/com.termux/files/usr/bin/env bash
set -euo pipefail
ID="${1#\#}"
QA="$HOME/constellation25/quick_actions"
[ -f "$QA/index.json" ] || { echo "index missing — run: qa"; exit 1; }
TARGET=$(python3 - "$QA/index.json" "$ID" <<'PY'
import json, sys
data = json.load(open(sys.argv[1]))
print({d["id"]: d["path"] for d in data}.get(sys.argv[2].zfill(3), ""))
PY
)
[ -n "$TARGET" ] || { echo "no such action: $ID"; exit 1; }
echo "[$(date -u +%H:%M:%SZ)] executing #$ID -> $TARGET" | tee -a "$QA/run.log"
bash "$TARGET"
