#!/data/data/com.termux/files/usr/bin/bash
# C25 Ollama Daemon Start Script

echo "[🤖] Initializing Ollama Daemon..."
pkill -f ollama 2>/dev/null
sleep 1

# Start with nohup to prevent Android from killing it
nohup ollama serve > ~/constellation25/agents/logs/ollama.log 2>&1 &

# Readiness loop (waits up to 20 seconds for server to boot)
for i in {1..10}; do
    if ollama list > /dev/null 2>&1; then
        echo "[✅] Ollama server is online and ready."
        exit 0
    fi
    echo "[⏳] Waiting for Ollama... ($i/10)"
    sleep 2
done

echo "[] Ollama failed to start. Check logs:"
cat ~/constellation25/agents/logs/ollama.log
exit 1
