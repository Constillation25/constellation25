#!/data/data/com.termux/files/usr/bin/bash
# c25-master-ui.sh | Venus | master ecosystem index.html
set -euo pipefail
C25="$HOME/constellation25"; MAN="$C25/manifests"; HTML="$C25/master_ui/index.html"
cat > "$HTML" <<'HEAD'
<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Constellation25 | Vertically Integrated Ecosystem</title>
<style>
:root{--bg:#0a0e14;--card:#111826;--acc:#4da3ff;--txt:#e6edf3}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--txt);font-family:system-ui,sans-serif}
header{padding:3rem 1.5rem;text-align:center;background:linear-gradient(135deg,#0d1b2a,#1b263b)}
header h1{margin:0;font-size:2.2rem}header p{color:var(--acc)}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:1rem;padding:1.5rem;max-width:1200px;margin:auto}
.card{background:var(--card);border:1px solid #1f2a3a;border-radius:12px;padding:1rem}
.card h3{margin:0 0 .5rem;font-size:1rem;color:var(--acc)}
.badge{display:inline-block;font-size:.65rem;padding:2px 8px;border-radius:99px;background:#1f2a3a;margin-right:4px}
.card details{font-size:.75rem;color:#9fb0c3}
footer{text-align:center;padding:2rem;color:#5b6b7d}
</style></head><body>
<header><h1>CONSTELLATION25</h1><p>Vertically Integrated Ecosystem — 299 Repos • 2000+ Builds • Git + Vercel Unified</p></header>
<main class="grid">
HEAD
{ cat "$MAN/git_repos.txt" 2>/dev/null; sed 's/^/VERCEL:/' "$MAN/vercel_projects.txt" 2>/dev/null; } | sort -u | while IFS= read -r m; do
  [ -z "$m" ] && continue
  case "$m" in VERCEL:*) name="${m#VERCEL:}"; badges='<span class="badge">VERCEL</span>';; *) name="$m"; badges='<span class="badge">GIT</span>';; esac
  cnt=$(grep -c "/$name/" "$MAN/html_inventory.txt" 2>/dev/null || true)
  cat >> "$HTML" <<CARD
<div class="card"><h3>$name</h3>$badges<span class="badge">${cnt:-0} html</span>
<details><summary>builds</summary>$(grep "/$name/" "$MAN/html_inventory.txt" 2>/dev/null | head -50 | sed 's|.*|<div>&</div>|')</details>
</div>
CARD
done
cat >> "$HTML" <<'FOOT'
</main><footer>Kre8tive Holdings • SovereignGTP • #FullThrottle</footer></body></html>
FOOT
echo "[VENUS] master UI: $HTML ($(wc -c < "$HTML") bytes)"
