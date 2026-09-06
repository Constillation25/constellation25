#!/usr/bin/env python3
"""AQUARIUS TO C25 ORCHESTRA BRIDGE"""
import json, urllib.request, os
from datetime import datetime
from pathlib import Path

AQUARIUS_API = "http://localhost:8082/api/files"
IPC_DIR = Path.home() / "c25_ipc" / "pending"
IPC_DIR.mkdir(parents=True, exist_ok=True)

print("[*] Fetching live index from Aquarius...")
try:
    with urllib.request.urlopen(AQUARIUS_API, timeout=10) as resp:
        data = json.loads(resp.read().decode())
    print(f"[✓] Fetched {len(data)} entries.")
except Exception as e:
    print(f"[!] Failed to reach Aquarius: {e}")
    exit(1)

# Format as C25 IPC Task
task_payload = {
    "task_id": f"aquarius_ingest_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
    "task": "ingest_aquarius_index",
    "source": "aquarius_agent",
    "assigned_to": ["Earth", "Sun"],
    "priority": "high",
    "timestamp": datetime.now().isoformat(),
    "payload": {
        "total_entries": len(data),
        "files": data
    }
}

# Drop into IPC Queue
output_file = IPC_DIR / f"{task_payload['task_id']}.json"
with open(output_file, 'w') as f:
    json.dump(task_payload, f, indent=2)

print(f"[✓] Payload injected into C25 IPC Queue: {output_file}")
print("[*] Notifying Orchestrator...")
