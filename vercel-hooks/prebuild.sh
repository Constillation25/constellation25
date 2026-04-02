#!/data/data/com.termux/files/usr/bin/bash
echo "⚙️  Vercel Pre-Build Hook: Preparing environment..."
npm ci --production 2>/dev/null || true
echo "✅ Pre-build complete"
