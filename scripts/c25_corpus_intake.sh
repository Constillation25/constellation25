#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail
INBOX="$HOME/corpus_kit/inbox"
MANIFESTS="$HOME/corpus_kit/manifests"
IPC="$HOME/c25_ipc/pending"
TS=$(date +%Y%m%d-%H%M%S)
mkdir -p "$INBOX" "$MANIFESTS" "$IPC"

echo "[INTAKE] Scanning for AI exports..."
FOUND=0
for path in "$HOME/storage/shared/Download" "$HOME/downloads" "/sdcard/Download"; do
  [[ -d "$path" ]] && find "$path" -maxdepth 4 -type f \( -iname "*takeout*.zip" -o -iname "*openai*.zip" -o -iname "*claude*.zip" -o -iname "conversations.json" \) -print0 2>/dev/null | while IFS= read -r -d '' f; do
    cp -n "$f" "$INBOX/" && echo "[INTAKE] Secured: $(basename "$f")" && FOUND=1
  done
done

if [[ $(ls -A "$INBOX" 2>/dev/null) ]]; then
  (cd "$INBOX" && sha256sum * > "$MANIFESTS/intake_$TS.sha256")
  echo '{"agent":"Saturn","action":"SCAF_VAULT_SECURE","payload":{"dir":"'"$INBOX"'"}}' > "$IPC/task_saturn_$TS.json"
  echo '{"agent":"Neptune","action":"CORPUS_PARSE","payload":{"dir":"'"$INBOX"'"}}' > "$IPC/task_neptune_$TS.json"
  echo "[INTAKE] Payloads hashed and routed to IPC."
else
  echo "[INTAKE] WARNING: No raw AI exports found. Manual browser export required."
fi
