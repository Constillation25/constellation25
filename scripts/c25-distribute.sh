#!/data/data/com.termux/files/usr/bin/bash
# c25-distribute.sh | Venus + Vesta | master UI -> all repos (GH Pages + Vercel root)
set -euo pipefail
C25="$HOME/constellation25"; REPOS="$C25/repos"; UI="$C25/master_ui/index.html"
while IFS= read -r r; do
  [ -z "$r" ] && continue; T="$REPOS/$r"; [ -d "$T" ] || continue
  mkdir -p "$T/docs"
  cp "$UI" "$T/index.html"; cp "$UI" "$T/docs/index.html"
  (cd "$T" && git add -A && git commit -qm "c25: master ecosystem UI" && git push -q) || echo "GIT_SYNC_FAIL $r" >> "$C25/logs/sync_fail.log"
done < "$C25/manifests/git_repos.txt"
echo "[VESTA] git sync done; Vercel deploys -> Apollo/Vesta"
