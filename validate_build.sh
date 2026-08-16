#!/bin/bash
echo "=== SOVEREIGNGTP BUILD VALIDATION ==="
echo ""

# Check core components
components=(
  "c25_orchestrator.py:Orchestrator"
  "modules/bioauth/bioauth.py:BioAuth"
  "tools/c25-bio-push/main.sh:BioAuth Push"
  "modules/totalrecall/engine.py:TotalRecall"
  "modules/videocourts/analyze.py:VideoCourts"
  "modules/mybuyo/engine.py:MyBuyo"
  "modules/commz/mesh.py:Commz"
  "modules/pathos/engine.py:PaTHos"
)

echo "Core Components:"
for comp in "${components[@]}"; do
  IFS=':' read -r path name <<< "$comp"
  if [ -f "$HOME/constellation25/$path" ]; then
    echo "  ✅ $name"
  else
    echo "  ❌ $name (MISSING)"
  fi
done

echo ""
echo "Agent Systems:"
agents=("earth" "mercury" "venus" "mars" "jupiter" "saturn" "uranus" "neptune" "pluto")
for agent in "${agents[@]}"; do
  if [ -d "$HOME/constellation25/agents/$agent" ]; then
    echo "  ✅ $agent"
  else
    echo "  ❌ $agent (MISSING)"
  fi
done

echo ""
echo "Live Services:"
services=("orchestrator" "stalker" "dashboard")
for svc in "${services[@]}"; do
  if pgrep -f "$svc" > /dev/null; then
    echo "  ✅ $svc (RUNNING)"
  else
    echo "  ❌ $svc (STOPPED)"
  fi
done
