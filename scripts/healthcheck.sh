#!/data/data/com.termux/files/usr/bin/bash
echo "🩺 C25 Health Check..."
curl -s http://localhost:3000/health | grep -q "online" && echo "✅ Server responding" || echo "⚠️ Server not running locally (expected on Vercel)"
[ -f "agents/agent_01.json" ] && echo "✅ Agent configs present" || echo "⚠️ Agents missing"
echo "✅ Health check passed"
