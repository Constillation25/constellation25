#!/data/data/com.termux/files/usr/bin/bash
# CONSTELLATION25 - Interactive Task Box (with descriptions)

BASE="$HOME/constellation25"
PENDING="$HOME/c25_ipc/pending"
mkdir -p "$PENDING"

clear
echo "🌌 CONSTELLATION25 // 25 PLANETARY AGENTS"
echo "=============================================================="
echo ""
echo " 1. Earth      - Master Orchestrator (routing, control)"
echo " 2. Mercury    - NLP & Speed (LangChain, plagiarism)"
echo " 3. Venus      - Creation (AI art, virtual worlds)"
echo " 4. Mars       - Compute (supercomputing, HMD)"
echo " 5. Jupiter    - Commerce (payments, recommendations)"
echo " 6. Saturn     - Events (meetings, concerts)"
echo " 7. Uranus     - Specialized ML (bird prediction)"
echo " 8. Neptune    - Deep Ops (BentoML, W&B)"
echo " 9. Pluto      - Memory & Edge (ChromaDB, Pinecone)"
echo "10. Ceres      - Data Pipeline (ETL, cleaning)"
echo "11. Vesta      - Security (auth, encryption)"
echo "12. Pallas     - Analytics (metrics, reporting)"
echo "13. Hygiea     - Health Monitoring (heartbeats)"
echo "14. Juno       - Coordination (multi-agent)"
echo "15. Europa     - Knowledge (RAG, documents)"
echo "16. Ganymede   - Communication (messaging)"
echo "17. Callisto   - Storage (files, backups)"
echo "18. Titan      - Simulation (forecasting)"
echo "19. Enceladus  - Experimentation (A/B testing)"
echo "20. Triton     - Edge Devices (IoT, wearables)"
echo "21. Charon     - Archival (Sovereign Archive)"
echo "22. Miranda    - UI / Experience (dashboards)"
echo "23. Ariel      - Automation (workflows)"
echo "24. Umbriel    - Resilience (circuit breakers)"
echo "25. Oberon     - Governance (policy, audit)"
echo ""
echo "=============================================================="
echo ""

read -p "Enter agent number (1-25) or name: " choice
read -p "Enter task description: " task

declare -A agents=(
  [1]="earth" [2]="mercury" [3]="venus" [4]="mars" [5]="jupiter"
  [6]="saturn" [7]="uranus" [8]="neptune" [9]="pluto" [10]="ceres"
  [11]="vesta" [12]="pallas" [13]="hygiea" [14]="juno" [15]="europa"
  [16]="ganymede" [17]="callisto" [18]="titan" [19]="enceladus" [20]="triton"
  [21]="charon" [22]="miranda" [23]="ariel" [24]="umbriel" [25]="oberon"
)

if [[ $choice =~ ^[0-9]+$ ]] && [ "$choice" -ge 1 ] && [ "$choice" -le 25 ]; then
  agent=${agents[$choice]}
else
  agent=$(echo "$choice" | tr '[:upper:]' '[:lower:]')
fi

timestamp=$(date +%s)
task_file="$PENDING/${agent}_${timestamp}.json"

cat > "$task_file" << JSON
{
  "agent": "$agent",
  "task": "$task",
  "priority": "normal",
  "created": "$(date -Iseconds)",
  "status": "pending"
}
JSON

echo ""
echo "✅ Task successfully sent to → $agent"
echo "   Saved as: $task_file"
echo ""
echo "The Orchestrator will pick it up automatically."
