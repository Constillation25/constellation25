#!/data/data/com.termux/files/usr/bin/bash
set -uo pipefail
C25="$HOME/constellation25"; MAN="$C25/manifests"; REPOS="$C25/repos"
mkdir -p "$C25/logs" "$MAN"; log(){ echo "[FIX2] $*" | tee -a "$C25/logs/fix2.log"; }
sed -i 's/set -euo pipefail/set -uo pipefail/' "$C25/scripts/c25-universe.sh"
log "1: repo list rebuild (manifests, not /tmp)"
RA="$MAN/repos.all"; : > "$RA"
cat "$MAN/git_repos.txt" 2>/dev/null >> "$RA"
grep -hoE 'github\.com[:/][^/ "]+' ~/.bash_history ~/.ash_history ~/.zsh_history 2>/dev/null | sed -E 's|.*[:/][^/]+/||; s|\.git$||' >> "$RA"
find "$HOME" -maxdepth 6 -type d -name ".git" 2>/dev/null | sed 's|/.git$||' | while IFS= read -r d; do basename "$d"; done >> "$RA"
grep -vE '^[./]' "$RA" | grep -v '^$' | sort -u > "$MAN/git_repos.txt"
log "repos: $(wc -l < "$MAN/git_repos.txt")"
log "2: hubs = repos + backups projects"
{ cat "$MAN/git_repos.txt"
  find "$HOME/backups" -maxdepth 1 -mindepth 1 -type d 2>/dev/null | while IFS= read -r d; do basename "$d"; done
  ls "$REPOS" 2>/dev/null; } | grep -v '^$' | sort -u > "$MAN/hubs.txt"
sed -i 's|"$MAN/git_repos.txt"|"$MAN/hubs.txt"|' "$C25/scripts/c25-universe.sh"
log "hubs: $(wc -l < "$MAN/hubs.txt")"
log "3: universe build"
bash "$C25/scripts/c25-universe.sh" || log "UNIVERSE FAIL AGAIN"
cp -f "$C25/master_ui/universe.html" "$C25/master_ui/index.html" 2>/dev/null
log "4: vaults + distribute"
while IFS= read -r v; do [ -d "$v" ] && cp "$C25/master_ui/universe.html" "$v/Constellation25-Universe.html" 2>/dev/null; done < "$MAN/obsidian_vaults.txt"
while IFS= read -r r; do T="$REPOS/$r"; [ -d "$T/.git" ] || continue
  mkdir -p "$T/docs"; cp "$C25/master_ui/universe.html" "$T/index.html"; cp "$C25/master_ui/universe.html" "$T/docs/index.html"
  (cd "$T" && { git checkout -q main || git checkout -q master; } 2>/dev/null
   git add -A; git commit -qm "c25: spatial universe UI" && git push -q -u origin HEAD) || echo "SYNC_FAIL $r" >> "$C25/logs/sync_fail.log"
done < "$MAN/git_repos.txt"
log "FIX2 DONE - universe: $(wc -c < "$C25/master_ui/universe.html" 2>/dev/null || echo 0) bytes"
