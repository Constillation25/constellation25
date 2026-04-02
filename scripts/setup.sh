#!/data/data/com.termux/files/usr/bin/bash
echo "🔧 C25 Setup: Validating environment..."
[ -f "package.json" ] || { echo "❌ package.json missing"; exit 1; }
npm install --production 2>/dev/null || npm install
echo "✅ Dependencies installed. Build ready."
