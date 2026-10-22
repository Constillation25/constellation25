#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════════
# VideoCourts™ — Termux Deploy Script v1.0.0
# Deploys public release to GitHub + Vercel from Termux/Android
# ═══════════════════════════════════════════════════════════════════
set -e

REPO_DIR="$HOME/Constellation25/repos/videocourts"
SD_BACKUP="/storage/F9CD-9D96/Constellation25/repos/videocourts-public-$(date +%Y%m%d_%H%M%S)"
GITHUB_REPO="FacePrintPay/videocourts"   # update if different
BUILD_ID="VC-PUBLIC-20260906"

echo "═══════════════════════════════════════════════"
echo "  VideoCourts™ Public Deploy — $BUILD_ID"
echo "═══════════════════════════════════════════════"

# ── Guard: token env vars must be unset for gh/vercel CLIs ──
unset GITHUB_TOKEN
unset VERCEL_TOKEN

# ── 1. Check prereqs ──
for cmd in git node npm; do
  command -v "$cmd" >/dev/null || { echo "❌ Missing: $cmd"; exit 1; }
done
echo "✅ Prereqs OK"

# ── 2. Verify storage ──
AVAIL=$(df -k "$HOME" | awk 'NR==2{print $4}')
if [ "$AVAIL" -lt 204800 ]; then
  echo "⚠️  Low internal storage (${AVAIL}k). Routing git tmp to SD card."
  export GIT_TMPDIR="/storage/F9CD-9D96/c25_tmp"
  mkdir -p "$GIT_TMPDIR"
fi

# ── 3. Copy source to canonical repo location ──
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
echo "📂 Syncing source → $REPO_DIR"
mkdir -p "$REPO_DIR"
rsync -a --no-links --exclude=".git" --exclude="node_modules" --exclude="dist" \
  "$SCRIPT_DIR/" "$REPO_DIR/"

# ── 4. SD card backup ──
echo "💾 Backing up to SD card → $SD_BACKUP"
mkdir -p "$SD_BACKUP"
rsync -a --no-links --exclude="node_modules" --exclude="dist" "$SCRIPT_DIR/" "$SD_BACKUP/"
echo "✅ SD backup done"

# ── 5. Install deps ──
cd "$REPO_DIR"
echo "📦 Installing npm dependencies…"
npm install --no-cache-dir 2>/dev/null || npm install

# ── 6. Build ──
echo "🔨 Building production bundle…"
npm run build
echo "✅ Build complete → dist/"

# ── 7. Git push ──
echo "🔀 Pushing to GitHub: $GITHUB_REPO"
if [ ! -d ".git" ]; then
  git init
  git remote add origin "https://github.com/$GITHUB_REPO.git"
fi

# Ensure HTTPS remote (no SSH in Termux)
git remote set-url origin "https://github.com/$GITHUB_REPO.git"

git add -A
git commit -m "VideoCourts Public Release $BUILD_ID — $(date '+%Y-%m-%d %H:%M')" || echo "(nothing new to commit)"
git push origin main || git push origin HEAD:main

# ── 8. Vercel deploy ──
echo "🚀 Deploying to Vercel…"
# Wipe stale project config to avoid broken redirect URLs
rm -rf .vercel/
npx vercel --prod --yes 2>&1

echo ""
echo "═══════════════════════════════════════════════"
echo "  ✅ DEPLOY COMPLETE — VideoCourts™ v1.0.0"
echo "  Build: $BUILD_ID"
echo "  Repo:  https://github.com/$GITHUB_REPO"
echo "═══════════════════════════════════════════════"
