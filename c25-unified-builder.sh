#!/data/data/com.termux/files/usr/bin/bash
# C25 Unified Auto-Updater
WATCH_DIR=~/c25_ipc/pending
while true; do
    for task in $WATCH_DIR/*.json; do
        if [ -f "$task" ]; then
            echo "Processing: $(basename $task)"
            # Agent routing logic here
            mv "$task" ~/c25_ipc/completed/ 2>/dev/null
        fi
    done
    sleep 2
done
