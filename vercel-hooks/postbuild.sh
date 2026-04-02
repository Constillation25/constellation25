#!/data/data/com.termux/files/usr/bin/bash
echo "✅ Vercel Post-Build Hook: Verifying output..."
[ -f "index.js" ] && echo "✅ Entry point verified" || exit 1
echo "✅ Post-build complete"
