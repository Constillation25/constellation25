#!/usr/bin/env bash
LOG="$HOME/constellation25/research/lut-inference/runtime/full_runtime.log"
echo "" >> "$LOG"
echo "=== HEALTH SNAPSHOT $(date -u +%FT%TZ) ===" >> "$LOG"
for p in 8000 8001 8002 8003 8004 8005 8006 8007 8008 8009 9000; do
  STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:$p/health 2>/dev/null || echo "000")
  echo "Port $p: $STATUS" >> "$LOG"
done
echo "--- PM2 Process List ---" >> "$LOG"
pm2 list 2>/dev/null >> "$LOG" || echo "PM2 not available" >> "$LOG"
echo "--- Disk ---" >> "$LOG"
df -h /data 2>/dev/null >> "$LOG"
echo "=== END HEALTH SNAPSHOT ===" >> "$LOG"
echo "[+] Health snapshot appended to runtime log"
