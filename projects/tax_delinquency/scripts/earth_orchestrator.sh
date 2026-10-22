#!/data/data/com.termux/files/usr/bin/bash
C25_BASE="$HOME/constellation25/projects/tax_delinquency"
LOG="$C25_BASE/logs/orchestrator.log"
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Earth Agent: Starting sweep..." >> "$LOG"
python3 "$C25_BASE/scripts/mercury_scraper.py" >> "$LOG" 2>&1
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Earth Agent: Sweep complete." >> "$LOG"
