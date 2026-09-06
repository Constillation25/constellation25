#!/data/data/com.termux/files/usr/bin/env bash
set -euo pipefail
echo "=== C25 BOOT ==="
pgrep ollama >/dev/null || (nohup ollama serve >/dev/null 2>&1 & echo "[+] Ollama started")
sleep 2
pm2 delete c25_orchestrator 2>/dev/null || true
pm2 start python --name c25_orchestrator --interpreter-args "-m c25.boot"
pm2 save 2>/dev/null || true
echo "=== HEALTH ==="
curl -s -o /dev/null -w "ollama:%{http_code}\n" http://localhost:11434/api/tags || echo "ollama: down"
pm2 ls | tail -3
sqlite3 ~/constellation25/db/c25.db "CREATE TABLE IF NOT EXISTS aquarius_entries (id INTEGER PRIMARY KEY AUTOINCREMENT, task_id TEXT, data TEXT, ingested_at DATETIME DEFAULT CURRENT_TIMESTAMP);" 2>/dev/null || true
echo "=== BOOT COMPLETE ==="
