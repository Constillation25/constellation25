#!/data/data/com.termux/files/usr/bin/bash

# ╔════════════════════════════════════════════════════════════╗
# ║     CONSTELLATION25 - MASTER CONTROL                       ║
# ║     17 Planetary Agents | TotalRecall | ReadDo | BioAuth   ║
# ╚════════════════════════════════════════════════════════════╝

BASE="$HOME/constellation25"
LOG="$BASE/logs/master.log"
mkdir -p "$BASE/logs"

log() { echo "[$(date '+%H:%M:%S')] $1" | tee -a "$LOG"; }

show_menu() {
echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║           CONSTELLATION 25 - MASTER CONTROL               ║"
echo "╠════════════════════════════════════════════════════════════╣"
echo "║  1  Start All Agents                                       ║"
echo "║  2  Stop All Agents                                        ║"
echo "║  3  Agent Status                                           ║"
echo "║  4  Run TotalRecall                                        ║"
echo "║  5  Push to GitHub                                         ║"
echo "║  6  View Logs                                              ║"
echo "║  7  Task Box (ReadDo)                                      ║"
echo "║  8  Storage Status                                         ║"
echo "║  9  Mass Deploy                                            ║"
echo "║  0  Exit                                                   ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
read -p "Select [0-9]: " choice

case "$choice" in
    1) bash "$BASE/start_all_agents.sh" ;;
    2) bash "$BASE/stop_all_agents.sh" ;;
    3) bash "$BASE/status_agents.sh" ;;
    4) bash ~/total_recall_fast.sh ;;
    5) bash "$BASE/push_to_github.sh" ;;
    6) tail -50 "$LOG" ;;
    7) bash "$BASE/task_box.sh" ;;
    8)
        echo ""
        echo "=== STORAGE STATUS ==="
        df -h /data/data/com.termux/files /storage/emulated/0
        echo ""
        echo "=== LARGEST DIRS ==="
        du -sh ~/* 2>/dev/null | sort -hr | head -10
        ;;
    9) bash ~/push_all_to_github.sh ;;
    0) echo "Exiting..." ; exit 0 ;;
    *) echo "Invalid option" ;;
esac

show_menu
}

show_menu
