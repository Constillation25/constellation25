#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail
C25="$HOME/constellation25"; MAN="$C25/manifests"; mkdir -p "$MAN"
git config --global push.autoSetupRemote true
git config --global pull.rebase true
{ find "$HOME" -xdev -type f \( -name "*.html" -o -name "*.htm" \) 2>/dev/null
  [ -d "$HOME/storage/shared" ] && find "$HOME/storage/shared" -type f \( -name "*.html" -o -name "*.htm" \) 2>/dev/null
} > "$MAN/html_inventory.txt" || true
echo "[SATURN] total html: $(wc -l < "$MAN/html_inventory.txt")"
sed 's|/[^/]*$||' "$MAN/html_inventory.txt" | sort | uniq -c | sort -rn | head -20 > "$MAN/html_hotspots.txt"
find "$HOME" -maxdepth 6 -type d -name ".git" 2>/dev/null | sed 's|/.git$||' > "$MAN/git_dirs.txt"
git -C "$HOME/backups" remote get-url origin > "$MAN/org_url.txt" 2>/dev/null || true
if command -v gh >/dev/null 2>&1 && gh auth status >/dev/null 2>&1; then
  gh repo list --limit 400 --json name -q '.[].name' > "$MAN/git_repos.txt" 2>/dev/null || true
fi
[ -s "$MAN/git_repos.txt" ] || while IFS= read -r d; do basename "$d"; done < "$MAN/git_dirs.txt" > "$MAN/git_repos.txt"
sort -u "$MAN/git_repos.txt" -o "$MAN/git_repos.txt"
echo "[EARTH] repos known: $(wc -l < "$MAN/git_repos.txt")"
{ [ -f "$HOME/.local/share/com.vercel.cli/auth.json" ] || [ -n "${VERCEL_TOKEN:-}" ]; } && echo VERCEL_AUTH_OK || echo VERCEL_AUTH_MISSING | tee "$MAN/vercel_auth.txt"
