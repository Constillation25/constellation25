#!/data/data/com.termux/files/usr/bin/bash

# CONSTELLATION25 — RUN
# Usage: ./run.sh              (one cycle)
#        ./run.sh --loop       (continuous)
#        ./run.sh --path       (pathfinder only)
#        ./run.sh --patch      (patcher only)
#        ./run.sh --sync       (sync only)
#        ./run.sh --train      (trainer only)
#        ./run.sh --report     (read last report)

BASE="$HOME/github-repos/Constillation25"
M='\033[0;35m'; G='\033[0;32m'; C='\033[0;36m'; Y='\033[1;33m'; B='\033[1m'; N='\033[0m'

cycle() {
  local CYC="${1:-1}"
  echo -e "\n${M}${B}  ★  CONSTELLATION25  —  CYCLE $CYC  ★${N}\n"
  bash "$BASE/_agents/pathfinder.sh"
  bash "$BASE/_agents/patcher.sh"
  bash "$BASE/_agents/synchronizer.sh"
  bash "$BASE/_agents/build_trainer.sh"
  echo -e "\n${G}${B}  ✓ CYCLE $CYC COMPLETE${N}"
  echo -e "  ${C}Report: $BASE/_reports/build_intelligence.md${N}\n"
}

case "${1:-}" in
  --loop)
    C=1
    while true; do
      cycle $C; C=$((C+1))
      echo -e "${Y}  Next cycle in 60s... Ctrl+C to stop${N}"; sleep 60
    done ;;
  --path)   bash "$BASE/_agents/pathfinder.sh" ;;
  --patch)  bash "$BASE/_agents/patcher.sh" ;;
  --sync)   bash "$BASE/_agents/synchronizer.sh" ;;
  --train)  bash "$BASE/_agents/build_trainer.sh" ;;
  --report) cat "$BASE/_reports/build_intelligence.md" 2>/dev/null || echo "Run a full cycle first" ;;
  *)        cycle 1 ;;
esac
