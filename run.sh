#!/usr/bin/env bash
# CONSTELLATION-25 - PATHOS ORCHESTRATED AGENT RUNNER

PATHOS="http://localhost:5000"

ping_pathos() {
  curl -s "$PATHOS" >/dev/null 2>&1 && return 0
  echo "⚠️  PaTHos not running. Starting..."
  cd "$HOME/sovereign-gtp/src/PaThosAi/virtual-platform/backend"
  node server.js &
  sleep 2
}

while true; do
  clear
  ping_pathos

  echo "╔════════════════════════════════════════════════════════════╗"
  echo "║        CONSTELLATION 25 - PATHOS ORCHESTRATED              ║"
  printf "║        Time: %-47s║\n" "$(date '+%Y-%m-%d %H:%M:%S')"
  echo "║        PaTHos: ✅ localhost:5000                           ║"
  echo "╠════════════════════════════════════════════════════════════╣"
  echo "║  1  Earth      - Foundational code structure               ║"
  echo "║  2  Moon       - Syntax error resolution                   ║"
  echo "║  3  Sun        - Performance optimization                  ║"
  echo "║  4  Mercury    - Unit test generation                      ║"
  echo "║  5  Venus      - Regression testing                        ║"
  echo "║  6  Mars       - Security vulnerability                    ║"
  echo "║  7  Jupiter    - Code documentation & analysis             ║"
  echo "║  8  Saturn     - Refactoring & modernization               ║"
  echo "║  9  Uranus     - NLP documentation generation              ║"
  echo "║  10 Neptune    - Code deduplication                        ║"
  echo "║  11 Cygnus     - AI algorithm/model code                   ║"
  echo "║  12 Orion      - UI/UX optimization                        ║"
  echo "║  13 Andromeda  - External API/service integration          ║"
  echo "║  14 Pleiades   - Virtual env management                    ║"
  echo "║  15 Sirius     - Deployment & scaling                      ║"
  echo "║  16 Canis Major- Technical debt resolution                 ║"
  echo "║  17 Hydra      - CI/CD pipeline execution                  ║"
  echo "╚════════════════════════════════════════════════════════════╝"
  printf "🌌 Agent [1-17] or 'bash' for terminal: "
  read -r CHOICE

  [[ "$CHOICE" == "bash" ]] && bash && continue
  [[ "$CHOICE" == "q" || "$CHOICE" == "quit" ]] && echo "Exiting." && exit 0

  case "$CHOICE" in
    1)  AGENT="Earth"      MODULE="earth"     TASK="foundational code structure" ;;
    2)  AGENT="Moon"       MODULE="miranda"   TASK="syntax error resolution" ;;
    3)  AGENT="Sun"        MODULE="triton"    TASK="performance optimization" ;;
    4)  AGENT="Mercury"    MODULE="mercury"   TASK="unit test generation" ;;
    5)  AGENT="Venus"      MODULE="venus"     TASK="regression testing" ;;
    6)  AGENT="Mars"       MODULE="mars"      TASK="security vulnerability scan" ;;
    7)  AGENT="Jupiter"    MODULE="jupiter"   TASK="code documentation and analysis" ;;
    8)  AGENT="Saturn"     MODULE="saturn"    TASK="refactoring and modernization" ;;
    9)  AGENT="Uranus"     MODULE="uranus"    TASK="NLP documentation generation" ;;
    10) AGENT="Neptune"    MODULE="neptune"   TASK="code deduplication" ;;
    11) AGENT="Cygnus"     MODULE="ceres"     TASK="AI algorithm and model code" ;;
    12) AGENT="Orion"      MODULE="eris"      TASK="UI/UX optimization" ;;
    13) AGENT="Andromeda"  MODULE="gonggong"  TASK="external API and service integration" ;;
    14) AGENT="Pleiades"   MODULE="pluto"     TASK="virtual environment management" ;;
    15) AGENT="Sirius"     MODULE="sedna"     TASK="deployment and scaling" ;;
    16) AGENT="Canis"      MODULE="quaoar"    TASK="technical debt resolution" ;;
    17) AGENT="Hydra"      MODULE="haumea"    TASK="CI/CD pipeline execution" ;;
    *)  echo "Invalid choice."; sleep 1; continue ;;
  esac

  echo ""
  echo "🌌 [$AGENT] Active via PaTHos/$MODULE — $TASK"
  echo "──────────────────────────────────────────"
  printf "Enter target file or describe task: "
  read -r INPUT

  echo ""
  echo "📡 Routing to PaTHos..."

  # Route through PaTHos first
  PATHOS_RESULT=$(curl -s -X POST "$PATHOS/pathos/execute" \
    -H "Content-Type: application/json" \
    -d "{\"module\":\"$MODULE\",\"input\":\"$INPUT\",\"task\":\"$TASK\"}" 2>/dev/null)

  if [[ -n "$PATHOS_RESULT" ]] && echo "$PATHOS_RESULT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('result',''))" 2>/dev/null; then
    echo ""
  else
    # Fallback to bash_agent
    echo "[PaTHos unavailable — template fallback]"
    python "$HOME/constellation-25/bash_agent.py" "$AGENT: $TASK - $INPUT"
  fi

  echo ""
  echo "──────────────────────────────────────────"
  printf "Press Enter to return to menu..."
  read -r
done
