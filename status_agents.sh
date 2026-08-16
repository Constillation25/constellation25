#!/data/data/com.termux/files/usr/bin/bash
echo "🌌 CONSTELLATION25 AGENT STATUS"
echo "================================"

echo -n "Stalker Global:     "
if pgrep -f "stalker_global.sh" > /dev/null; then
    echo "🟢 RUNNING (PID $(pgrep -f stalker_global.sh))"
else
    echo "🔴 STOPPED"
fi

echo -n "Orchestrator:       "
if pgrep -f "c25_orchestrator.py" > /dev/null; then
    echo "🟢 RUNNING (PID $(pgrep -f c25_orchestrator.py))"
else
    echo "🔴 STOPPED"
fi

echo -n "Wake Lock:          "
if dumpsys power 2>/dev/null | grep -q "termux"; then
    echo "🟢 HELD"
else
    echo "⚪ Check notification"
fi

echo ""
echo "Recent Stalker log:"
tail -n 8 ~/constellation25/logs/stalker_global.log 2>/dev/null || echo "(no log)"

echo ""
echo "Recent Orchestrator log:"
tail -n 6 ~/constellation25/logs/orchestrator_bg.log 2>/dev/null || echo "(no log)"
