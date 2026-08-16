#!/data/data/com.termux/files/usr/bin/bash
# CONSTELLATION25 - History Scanner Agent
# Scans bash history for failed commands and offers recovery

HISTORY_FILE="$HOME/.bash_history"
REPORT="$HOME/constellation25/logs/failed_commands_report.log"
TODO="$HOME/constellation25/logs/agent_todo.log"

mkdir -p "$(dirname $REPORT)"

echo "🔍 CONSTELLATION25 History Scanner"
echo "=================================="
echo "Scanning bash history for failed commands..."
echo ""

# Clear previous report
> "$REPORT"

# Common failure patterns
failed_count=0

# Read history (last 500 commands for performance)
tail -n 500 "$HISTORY_FILE" 2>/dev/null | while IFS= read -r cmd; do
    # Skip empty lines and comments
    [[ -z "$cmd" || "$cmd" == \#* ]] && continue

    # Detect likely failed patterns
    if echo "$cmd" | grep -qE "(error|failed|No such file|permission denied|command not found|not found|returned non-zero)"; then
        failed_count=$((failed_count+1))
        echo "❌ Possible failed command:" | tee -a "$REPORT"
        echo "   $cmd" | tee -a "$REPORT"
        echo "" | tee -a "$REPORT"
    fi

    # Detect scripts that were called but may have failed
    if echo "$cmd" | grep -qE "\.sh|python3 .*\.py|bash "; then
        # Check if the target file still exists
        target=$(echo "$cmd" | awk '{print $NF}')
        if [[ -n "$target" && ! -f "$target" && ! -f "$HOME/$target" && ! -f "$HOME/constellation25/$target" ]]; then
            echo "⚠️  Script referenced but file missing:" | tee -a "$REPORT"
            echo "   Command: $cmd" | tee -a "$REPORT"
            echo "   Reason : File not found → $target" | tee -a "$REPORT"
            echo "" | tee -a "$REPORT"
        fi
    fi
done

echo "=================================="
echo "Scan complete. Report saved to:"
echo "$REPORT"
echo ""

# Show summary
if [ -s "$REPORT" ]; then
    echo "📋 Failed / Suspicious commands found:"
    cat "$REPORT"
    echo ""
    echo "Do you want me to:"
    echo "  1) Add all to ToDo list"
    echo "  2) Attempt automatic fix & re-run"
    echo "  3) Just show report (do nothing)"
    read -p "Choose [1/2/3]: " choice

    case $choice in
        1)
            echo "[$(date)] History scan – failed commands added to ToDo" >> "$TODO"
            cat "$REPORT" >> "$TODO"
            echo "✅ Added to ToDo list"
            ;;
        2)
            echo "🔧 Attempting recovery..."
            # Simple recovery example – re-run last failed script if it exists
            last_script=$(grep -oE '[^ ]+\.sh' "$REPORT" | tail -1)
            if [ -n "$last_script" ] && [ -f "$last_script" ]; then
                echo "Re-running: $last_script"
                bash "$last_script"
            else
                echo "No recoverable script found automatically."
                echo "Please review the report and re-run manually."
            fi
            ;;
        3)
            echo "Report only – no action taken."
            ;;
    esac
else
    echo "✅ No obvious failed commands detected in recent history."
fi
