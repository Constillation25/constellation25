#!/usr/bin/env python3
"""
Earth Agent (#1) — Entry point for Constellation-25.
Reads raw conversation from stdin, prunes it, creates tasks for all 25 agents.
Usage:  echo "Claude: some text" | python3 earth_agent.py
Output: JSON with keys: source, pruned, tasks, artifacts
"""
import sys, json, re, subprocess, os

AGENTS_FILE = os.path.expanduser("~/constellation-25/agents.json")
MEMORIA     = os.path.expanduser("~/constellation-25/memoria.py")

def load_agents():
    with open(AGENTS_FILE) as f:
        return json.load(f)["agents"]

def parse_convo(raw):
    # Match optional emoji + "Source: content" tag
    match = re.match(r'[^\w\s]?(\w+):\s*(.*)', raw.strip(), re.DOTALL | re.IGNORECASE)
    source  = match.group(1) if match else "Input"
    content = match.group(2) if match else raw.strip()
    # Prune: strip timestamps like [12s], collapse whitespace
    pruned = re.sub(r'\[\d+s\]', '', content)
    pruned = re.sub(r'\s+', ' ', pruned).strip()
    return source, pruned

def build_tasks(agents, source, pruned):
    """
    FRAMEWORK PILLAR: Dynamic Assessment
    Task decomposition with granular agent state and capacity inference.
    """
    snippet = pruned[:60]
    complexity = assess_complexity(pruned)  # High/Medium/Low
    tasks = []
    
    for agent in agents:
        i, name, role = agent["id"], agent["name"], agent["role"]
        pillars = agent.get("pillars", [])
        
        if i == 1:
            desc = f"[Earth] Parsed source='{source}', complexity={complexity}, routed to 25 agents."
        elif i == 25:
            desc = f"[BashAgent] Generate deployable bash script for: {pruned}"
        else:
            desc = f"[{name}] {role} — processing: '{snippet}...'"
        
        # Dynamic priority based on complexity and agent pillars
        priority = "high" if complexity == "high" and "Adaptive Execution" in pillars else "normal"
        
        tasks.append({
            "agent_id": i,
            "agent_name": name,
            "task": desc,
            "pillars": pillars,
            "priority": priority,
            "status": "pending"  # For Structural Transparency
        })
    return tasks

def assess_complexity(text):
    """Assess task complexity for Dynamic Assessment pillar."""
    words = len(text.split())
    if words > 200 or "deploy" in text.lower() or "build" in text.lower():
        return "high"
    elif words > 50:
        return "medium"
    return "low"

def memoria_search(pruned):
    try:
        r = subprocess.run(["python3", MEMORIA, "search", pruned[:40]],
                           capture_output=True, text=True, timeout=5)
        return json.loads(r.stdout) if r.stdout.strip() else []
    except Exception:
        return []

def memoria_log(source, pruned):
    try:
        subprocess.run(["python3", MEMORIA, "log", source, pruned, "Earth"],
                       capture_output=True, timeout=5)
    except Exception:
        pass

if __name__ == "__main__":
    raw = sys.stdin.read()
    if not raw.strip():
        print(json.dumps({"error": "No input on stdin."}))
        sys.exit(1)
    agents         = load_agents()
    source, pruned = parse_convo(raw)
    artifacts      = memoria_search(pruned)
    tasks          = build_tasks(agents, source, pruned)
    memoria_log(source, pruned)
    print(json.dumps(
        {"source": source, "pruned": pruned, "tasks": tasks, "artifacts": artifacts},
        ensure_ascii=False
    ))
