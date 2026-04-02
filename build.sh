#!/data/data/com.termux/files/usr/bin/bash
echo "🔨 C25 Master Build Sequence..."
# Install Node deps
[ -f "package.json" ] && npm install --production 2>/dev/null || true
# Install Python deps
[ -f "requirements.txt" ] && pip install -r requirements.txt 2>/dev/null || true
# Run specific project builds if they exist
if [ -f "webpack.config.js" ] || [ -f "vite.config.js" ]; then
   npm run build 2>/dev/null || true
fi
echo "✅ C25 Master Build Complete"
