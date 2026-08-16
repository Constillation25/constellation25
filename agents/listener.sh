#!/data/data/com.termux/files/usr/bin/bash
# CONSTELLATION25 - Agent Listener & ToDo System
# Watches for incoming scripts/tasks and responds interactively

BASE="$HOME/constellation25"
WATCH_DIR="$BASE/incoming"
TODO_FILE="$BASE/logs/agent_todo.log"
LOG="$BASE/logs/listener.log"
PENDING="$HOME/c25_ipc/pending"

mkdir -p "$WATCH_DIR" "$PENDING" "$(dirname $TODO_FILE)" "$(dirname $LOG)"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG"
}

add_todo() {
    echo "[$(date '+%H:%M')] $1" >> "$TODO_FILE"
}

echo "🌌 CONSTELLATION25 Agent Listener started"
echo "Watching folder: $WATCH_DIR"
echo "Drop any .sh or .txt task file there and agents will respond."
echo ""

# Initial ToDo assumptions
add_todo "Monitor incoming scripts"
add_todo "Keep orchestrator alive"
add_todo "Respond to user tasks"

while true; do
    # Watch for new files
    for file in "$WATCH_DIR"/*; do
        [ -f "$file" ] || continue
        
        filename=$(basename "$file")
        log "📥 New file detected: $filename"

        # Move to processing
        mv "$file" "$PENDING/$filename"
        
        # Analyze and respond
        echo ""
        echo "=============================================="
        echo "🔔 Agent Alert: New task received → $filename"
        echo "=============================================="
        
        # Simple content preview
        if [[ "$filename" == *.sh ]]; then
            echo "Type: Bash script"
            head -n 5 "$PENDING/$filename"
        else
            echo "Type: Text task"
            cat "$PENDING/$filename"
        fi
        
        echo ""
        echo "Agent response options:"
        echo "  1) Execute it now"
        echo "  2) Add to ToDo list"
        echo "  3) Assign to specific agent"
        echo "  4) Ignore"
        echo ""
        read -p "Do you want me to process this? [1/2/3/4]: " choice
        
        case $choice in
            1)
                log "▶ Executing $filename"
                bash "$PENDING/$filename"
                add_todo "Executed: $filename"
                ;;
            2)
                add_todo "Pending review: $filename"
                echo "✅ Added to ToDo list"
                ;;
            3)
                read -p "Which agent (mercury/venus/jupiter/etc): " agent
                # Create JSON task for orchestrator
                cat > "$PENDING/${agent}_$(date +%s).json" << JSON
{
  "agent": "$agent",
  "task": "Process incoming file: $filename",
  "file": "$PENDING/$filename",
  "status": "pending"
}
JSON
                echo "✅ Assigned to $agent"
                add_todo "Assigned $filename to $agent"
                ;;
            4)
                echo "Ignored."
                ;;
            *)
                echo "Invalid choice – ignoring"
                ;;
        esac
        echo ""
    done
    
    sleep 4
done
