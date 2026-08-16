#!/data/data/com.termux/files/usr/bin/bash
echo "[MERCURY] Scanning codebase for dependencies..."
find ~/constellation25 -name "package.json" -exec grep -l "dependencies" {} \; 2>/dev/null | wc -l | xargs -I{} echo "  Found {} Node.js packages"
find ~/constellation25 -name "requirements.txt" 2>/dev/null | wc -l | xargs -I{} echo "  Found {} Python requirements files"
echo "[MERCURY] Dependency mapping complete."
