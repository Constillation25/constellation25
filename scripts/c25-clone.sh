#!/data/data/com.termux/files/usr/bin/bash
# Atlas | shallow parallel clone x8
set -euo pipefail
C25="$HOME/constellation25"; MAN="$C25/manifests"; REPOS="$C25/repos"
mkdir -p "$REPOS" "$C25/logs"; touch "$C25/logs/clone_fail.log"
ORG_URL=$(cat "$MAN/org_url.txt" 2>/dev/null || true); BASE="${ORG_URL%/*}"
[ -n "$BASE" ] || BASE="https://github.com/Kre8tiveHoldings"
export REPOS BASE LOGF="$C25/logs/clone_fail.log"
clone() { [ -d "$REPOS/$1/.git" ] || git clone --depth 1 -q "$BASE/$1" "$REPOS/$1" 2>>"$LOGF" || true; }
export -f clone
xargs -P 8 -n 1 -I{} bash -c 'clone "{}"' < "$MAN/git_repos.txt"
echo "[ATLAS] repos local: $(ls "$REPOS" | wc -l); fails: $(wc -l < "$LOGF")"
