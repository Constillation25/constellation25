#!/usr/bin/env python3
"""Constellation25 Base Agent Template"""
import json, os, sys, hashlib, time, uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

class BaseAgent:
    def __init__(self, name: str, tasks_dir: str, outputs_dir: str, logs_dir: str):
        self.name = name
        self.tasks_dir = Path(tasks_dir) / "incoming"
        self.processed_dir = Path(tasks_dir) / "processed"
        self.outputs_dir = Path(outputs_dir)
        self.logs_dir = Path(logs_dir)
        self.heartbeat_interval = 30
        self.last_heartbeat = time.time()
        for d in [self.tasks_dir, self.processed_dir, self.outputs_dir, self.logs_dir]:
            d.mkdir(parents=True, exist_ok=True)
    
    def log(self, message: str, level: str = "INFO"):
        timestamp = datetime.now().isoformat()
        log_entry = f"{timestamp} | {self.name.upper()} | {level} | {message}"
        print(log_entry)
        with open(self.logs_dir / f"{self.name}.log", "a") as f:
            f.write(log_entry + "\n")
    
    def poll_tasks(self) -> List[Path]:
        tasks = []
        for task_file in self.tasks_dir.glob(f"{self.name}_*.json"):
            try:
                with open(task_file) as f:
                    task = json.load(f)
                if task.get("agent") == self.name or task.get("type", "").startswith(self.name):
                    tasks.append(task_file)
            except Exception as e:
                self.log(f"Error reading {task_file}: {e}", "ERROR")
        return tasks
    
    def process_task(self, task_file: Path) -> Optional[Path]:
        try:
            with open(task_file) as f:
                task = json.load(f)
            task_type = task.get("type", "unknown")
            payload = task.get("payload", "")
            task_id = task.get("task_id", str(uuid.uuid4()))
            self.log(f"Processing: {task_type} - {payload[:50]}...")
            artifact_content = self.generate_artifact(task_type, payload)
            output_file = self.outputs_dir / f"{self.name}_{task_id}_{task_type.replace('/', '_')}.txt"
            with open(output_file, "w") as f:
                f.write(artifact_content)
            self.log(f"✓ Output: {output_file.name}")
            processed_file = self.processed_dir / task_file.name
            task_file.rename(processed_file)
            self.totalrecall_log(task_id, task_type, payload, output_file)
            return output_file
        except Exception as e:
            self.log(f"✗ Error processing {task_file}: {e}", "ERROR")
            return None
    
    def generate_artifact(self, task_type: str, payload: str) -> str:
        return f"""=== SovereignGTP Task Artifact ===
Agent:   {self.name}
Type:    {task_type}
Payload: {payload}
Created: {datetime.now().isoformat()}
--- Extra ---
Stub output. Override generate_artifact() in subclass.
"""
    
    def totalrecall_log(self, task_id: str, task_type: str, payload: str, output_file: Path):
        try:
            sha256 = hashlib.sha256(open(output_file, 'rb').read()).hexdigest()
            entry = {
                "timestamp": datetime.now().isoformat(),
                "agent": self.name,
                "task_id": task_id,
                "task_type": task_type,
                "payload_hash": hashlib.sha256(payload.encode()).hexdigest(),
                "output_file": str(output_file),
                "output_sha256": sha256,
                "chain_of_custody": "verified"
            }
            with open(self.logs_dir / "totalrecall.log", "a") as f:
                f.write(json.dumps(entry) + "\n")
            with open(self.logs_dir / "totalrecall_mesh.manifest", "a") as f:
                f.write(f"{entry['timestamp']} | {self.name.upper()} | {task_type} -> {output_file.name}\n")
        except Exception as e:
            self.log(f"TotalRecall logging error: {e}", "WARN")
    
    def send_heartbeat(self):
        now = time.time()
        if now - self.last_heartbeat >= self.heartbeat_interval:
            self.log("♥ Heartbeat", "DEBUG")
            self.last_heartbeat = now
            with open(Path(self.logs_dir) / f"{self.name}.heartbeat", "w") as f:
                json.dump({"agent": self.name, "timestamp": datetime.now().isoformat(), "pid": os.getpid()}, f)
    
    def run(self):
        self.log(f"🚀 {self.name} agent starting (PID: {os.getpid()})")
        try:
            while True:
                tasks = self.poll_tasks()
                if tasks:
                    self.log(f"📥 Found {len(tasks)} pending tasks")
                    for task_file in tasks:
                        self.process_task(task_file)
                else:
                    self.log("⏳ No pending tasks, waiting...", "DEBUG")
                self.send_heartbeat()
                time.sleep(5)
        except KeyboardInterrupt:
            self.log("🛑 Received shutdown signal")
        except Exception as e:
            self.log(f"💥 Agent crashed: {e}", "ERROR")
            raise

if __name__ == "__main__":
    agent_name = sys.argv[1] if len(sys.argv) > 1 else "generic"
    agent = BaseAgent(
        name=agent_name,
        tasks_dir=f"{os.getenv('C25_ROOT', os.path.expanduser('~') + '/constellation25')}/sovereign-gtp/tasks",
        outputs_dir=f"{os.getenv('C25_ROOT', os.path.expanduser('~') + '/constellation25')}/sovereign-gtp/outputs",
        logs_dir=f"{os.getenv('C25_ROOT', os.path.expanduser('~') + '/constellation25')}/sovereign-gtp/logs"
    )
    agent.run()
