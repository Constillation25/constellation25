#!/usr/bin/env python3
"""Constellation25 MCP Server | Routes agent tasks to Ollama + Bash executors"""
import http.server, json, subprocess, os, sys, time, threading
from pathlib import Path

QUEUE_DIR = Path(os.environ.get("C25_QUEUE_DIR", Path.home() / ".c25_agent_queue"))
AGENT_DIR = Path(os.environ.get("C25_AGENT_DIR", Path.home() / "constellation25" / "agents" / "executors"))
OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434/api/generate")
LOG_FILE = Path(os.environ.get("C25_LOG", "/dev/stderr"))

def log(msg):
    ts = time.strftime("%H:%M:%S")
    print(f"[{ts}] [MCP] {msg}", file=open(LOG_FILE, "a") if str(LOG_FILE)!="/dev/stderr" else sys.stderr)

def call_ollama(prompt, model="qwen2.5:0.5b"):
    """Lightweight Ollama call for LLM-heavy agent tasks"""
    try:
        import requests
        r = requests.post(OLLAMA_URL, json={"model": model, "prompt": prompt, "stream": False}, timeout=30)
        return r.json().get("response", "Ollama response empty")
    except Exception as e:
        return f"[OllamaFallback] {e}"

def run_bash_agent(agent_name, task, **params):
    """Execute bash executor"""
    exec_path = AGENT_DIR / f"{agent_name.lower()}_executor.sh"
    if not exec_path.is_file():
        return {"status": "error", "msg": f"Executor missing: {exec_path.name}"}
    try:
        res = subprocess.run(["bash", str(exec_path), task, *params.values()], capture_output=True, text=True, timeout=15)
        return {"status": "success", "stdout": res.stdout.strip(), "stderr": res.stderr.strip()}
    except Exception as e:
        return {"status": "error", "msg": str(e)}

def process_queue():
    """Scan queue, route to Ollama or Bash, update status"""
    processed = 0
    for f in QUEUE_DIR.glob("*.json"):
        try:
            data = json.loads(f.read_text())
            if data.get("status") in ("completed", "processing"): continue
            data["status"] = "processing"
            f.write_text(json.dumps(data))
            
            agent = data.get("agent", "").lower().replace("agent_", "")
            task = data.get("task", "unknown")
            
            if agent in ["mars", "ceres", "jupiter"] and "draft" in task or "score" in task:
                # Route LLM tasks to Ollama
                prompt = f"As {agent.upper()}, execute task: {task}. Context: {data.get('title', data.get('name', 'general'))}. Return concise result."
                result = call_ollama(prompt)
            else:
                # Route to Bash executor
                result = run_bash_agent(agent, task, **{k:v for k,v in data.items() if k not in ["agent","task","status"]})
            
            data["status"] = "completed"
            data["result"] = str(result)[:500]
            f.write_text(json.dumps(data))
            processed += 1
        except Exception as e:
            log(f"Queue error {f.name}: {e}")
    return processed

class MCPHandler(http.server.SimpleHTTPRequestHandler):
    def do_POST(self):
        if self.path == "/process":
            count = process_queue()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"processed": count}).encode())
        else:
            self.send_response(404)
            self.end_headers()
    def do_GET(self):
        if self.path == "/status":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"queue_size": len(list(QUEUE_DIR.glob("*.json")))}).encode())
        else:
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"Constellation25 MCP Server Ready")

if __name__ == "__main__":
    port = int(os.environ.get("C25_MCP_PORT", 8765))
    log(f"Starting MCP Server on :{port} | Queue: {QUEUE_DIR}")
    server = http.server.HTTPServer(("0.0.0.0", port), MCPHandler)
    server.serve_forever()
