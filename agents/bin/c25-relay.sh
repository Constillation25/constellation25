#!/data/data/com.termux/files/usr/bin/bash
# C25 Relay Orchestrator v2.0

# 1. Start and verify Ollama
~/constellation25/agents/bin/c25-ollama-start.sh
if [ $? -ne 0 ]; then exit 1; fi

# 2. Define the Track Team
AGENTS=("Earth" "Venus" "Mars" "Jupiter" "Saturn")

declare -A TASKS
TASKS["Earth"]="You are Earth. DevOps & Routing. Task: Verify Termux directories and IPC routing for Vade Mecum recon."
TASKS["Venus"]="You are Venus. UI/UX & Frontend. Task: Design a text-based UI layout for the Vade Mecum treasure map."
TASKS["Mars"]="You are Mars. Security. Task: Identify physical security risks for exploring the 1929 Tise Hall gym."
TASKS["Jupiter"]="You are Jupiter. Legal. Task: Summarize NC state park metal detecting laws for Hanging Rock."
TASKS["Saturn"]="You are Saturn. Storage. Task: Create a SQLite schema to log physical finds at Vade Mecum."

# 3. Execute the Relay
echo "[🚀] C25 RELAY RACE STARTED: $(date)"
for agent in "${AGENTS[@]}"; do
    OUTPUT_FILE=~/constellation25/agents/responses/${agent}.txt
    echo "[🏃] $agent taking the baton..."
    
    ollama run mistral "${TASKS[$agent]}" > "$OUTPUT_FILE" 2>&1
    
    if [ -s "$OUTPUT_FILE" ]; then
        echo "[✅] $agent crossed the finish line."
    else
        echo "[❌] $agent failed. Check ~/constellation25/agents/logs/ollama.log"
    fi
done
echo "[🏆] RELAY COMPLETE: $(date)"
