#!/data/data/com.termux/files/usr/bin/bash

echo "╔════════════════════════════════════════════╗"
echo "║  SOVEREIGN FINAL CLEAN REBUILD              ║"
echo "╚════════════════════════════════════════════╝"

cd ~/constellation25

# Clean logs older than 7 days
find logs/ -name "*.log" -mtime +7 -delete 2>/dev/null
echo "✓ Old logs cleaned"

# Rebuild recovered stubs into proper scripts
for stub in recovered_scripts/*.sh; do
    [ -f "$stub" ] && chmod +x "$stub"
done
echo "✓ Stubs made executable"

# Re-run agent status
bash status_agents.sh

echo ""
echo "✅ Clean rebuild complete"
