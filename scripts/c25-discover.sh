#!/data/data/com.termux/files/usr/bin/bash
# c25-discover.sh | Earth + Saturn | inventory
set -euo pipefail
C25="$HOME/constellation25"; MAN="$C25/manifests"; mkdir -p "$MAN"
ls -la ~/backups | tee "$MAN/backups_inventory.txt"
find ~/backups -type f -name "*.html" > "$MAN/html_inventory.txt"
echo "[SATURN] html files: $(wc -l < "$MAN/html_inventory.txt")"
find ~/backups -type f | sed 's/.*\.//' | sort | uniq -c | sort -rn > "$MAN/ext_profile.txt"
ls "$C25/repos" 2>/dev/null > "$MAN/git_repos.txt" || true
if command -v vercel >/dev/null 2>&1; then
  timeout 20 vercel project ls 2>/dev/null | awk 'NR>1{print $1}' > "$MAN/vercel_projects.txt" || true
else echo "VERCEL_CLI_MISSING" > "$MAN/vercel_projects.txt"; fi
echo "[EARTH] discovery complete"
