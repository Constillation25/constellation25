#!/data/data/com.termux/files/usr/bin/bash
curl -X POST http://localhost:3000/api/webhook -H "Content-Type: application/json" -d '{"event":"c25_deploy","status":"initiated"}'
echo ""
echo "✅ Webhook test sent"
