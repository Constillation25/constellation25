#!/data/data/com.termux/files/usr/bin/bash
set -uo pipefail
C25="$HOME/constellation25"; MAN="$C25/manifests"; REPOS="$C25/repos"
mkdir -p "$C25/logs" "$MAN" "$REPOS"
log(){ echo "[FIN] $*" | tee -a "$C25/logs/finish.log"; }
git config --global push.autoSetupRemote true
git config --global user.name 2>/dev/null || git config --global user.name "CyGeL White"
git config --global user.email 2>/dev/null || git config --global user.email "owner@kre8tiveholdings.com"
log "A: repo list recovery (history + .git dirs + token API)"
: > /tmp/repos.all
cat "$MAN/git_repos.txt" 2>/dev/null >> /tmp/repos.all
grep -hoE 'github\.com[:/][^/ ]+\.git' ~/.bash_history ~/.zsh_history 2>/dev/null | sed -E 's|.*[:/][^/]+/||; s|\.git$||' >> /tmp/repos.all
grep -hA1 'git clone' ~/.bash_history 2>/dev/null | grep -oE 'github\.com[^ ]+' | sed -E 's|.*[:/][^/]+/||; s|\.git$||' >> /tmp/repos.all
find "$HOME" -maxdepth 6 -type d -name ".git" 2>/dev/null | sed 's|/.git$||' | while IFS= read -r d; do basename "$d"; done >> /tmp/repos.all
TOK=$(grep -hoE 'ghp_[A-Za-z0-9]{36,}|github_pat_[A-Za-z0-9_]{22,}' ~/.config/gh/hosts.yml ~/.git-credentials ~/.netrc 2>/dev/null | head -1)
ORG=$(sed -E 's|.*[:/]([^/]+)/[^/]+$|\1|' "$MAN/org_url.txt" 2>/dev/null | head -1); [ -n "$ORG" ] || ORG="Kre8tiveHoldings"
if [ -n "$TOK" ]; then log "token found - private API"; for p in 1 2 3 4; do curl -s -H "Authorization: token $TOK" "https://api.github.com/orgs/$ORG/repos?per_page=100&page=$p" | grep -oE '"name": *"[^"]+"' | cut -d'"' -f4 >> /tmp/repos.all; done; else log "no token - recovery only"; fi
grep -vE '^[./]' /tmp/repos.all | grep -v '^$' | sort -u > "$MAN/git_repos.txt"
log "repos listed: $(wc -l < "$MAN/git_repos.txt")"
log "B: clone x8"
export REPOS BASE="https://github.com/$ORG" LOGF="$C25/logs/clone_fail.log"; touch "$LOGF"
clone(){ [ -d "$REPOS/$1/.git" ] || git clone --depth 1 -q "$BASE/$1" "$REPOS/$1" 2>>"$LOGF" || true; }
export -f clone
xargs -P 8 -n 1 -I{} bash -c 'clone "{}"' < "$MAN/git_repos.txt"
log "repos local: $(ls "$REPOS" | wc -l)"
log "C: universe build"
bash "$C25/scripts/c25-universe.sh" || log "UNIVERSE FAIL"
log "D: vaults"
while IFS= read -r v; do [ -d "$v" ] && cp "$C25/master_ui/universe.html" "$v/Constellation25-Universe.html" 2>/dev/null; done < "$MAN/obsidian_vaults.txt"
log "E: distribute + push"
while IFS= read -r r; do T="$REPOS/$r"; [ -d "$T/.git" ] || continue
  mkdir -p "$T/docs"; cp "$C25/master_ui/universe.html" "$T/index.html"; cp "$C25/master_ui/universe.html" "$T/docs/index.html"
  (cd "$T" && { git checkout -q main || git checkout -q master; } 2>/dev/null
   git add -A; git commit -qm "c25: spatial universe UI" && git push -q -u origin HEAD) || echo "SYNC_FAIL $r" >> "$C25/logs/sync_fail.log"
done < "$MAN/git_repos.txt"
log "DONE repos:$(ls "$REPOS" | wc -l) fails:$(wc -l < "$C25/logs/sync_fail.log")"
