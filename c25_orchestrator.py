#!/data/data/com.termux/files/usr/bin/python3
import asyncio
import json
import time
from datetime import datetime
from pathlib import Path
from enum import Enum
import random

class CircuitState(Enum):
    CLOSED = "CLOSED"
    OPEN = "OPEN"
    HALF_OPEN = "HALF_OPEN"

class CircuitBreaker:
    def __init__(self, name, failure_threshold=5, recovery_timeout=30):
        self.name = name
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failures = 0
        self.last_failure = None
        self.state = CircuitState.CLOSED

    def to_dict(self):
        return {
            "name": self.name,
            "state": self.state.value,
            "failures": self.failures,
            "last_failure": self.last_failure.isoformat() if self.last_failure else None
        }

    @classmethod
    def from_dict(cls, data):
        cb = cls(data["name"])
        cb.state = CircuitState(data["state"])
        cb.failures = data.get("failures", 0)
        if data.get("last_failure"):
            cb.last_failure = datetime.fromisoformat(data["last_failure"])
        return cb

class C25Orchestrator:
    def __init__(self):
        self.base = Path.home() / "constellation25"
        self.config_dir = self.base / "config"
        self.ipc_pending = Path.home() / "c25_ipc" / "pending"
        self.ipc_completed = Path.home() / "c25_ipc" / "completed"
        self.log_file = self.base / "logs" / "agent_task.log"
        self.state_file = self.config_dir / "circuit_state.json"

        for p in [self.base, self.config_dir, self.ipc_pending, self.ipc_completed, self.log_file.parent]:
            p.mkdir(parents=True, exist_ok=True)

        self.circuit_breakers = self.load_or_create_state()
        self.task_queue = asyncio.Queue()
        self.max_concurrency = 5

    def load_or_create_state(self):
        if self.state_file.exists():
            try:
                with open(self.state_file) as f:
                    data = json.load(f)
                return {name: CircuitBreaker.from_dict(cb) for name, cb in data.items()}
            except:
                pass
        agents = ["mercury", "venus", "jupiter", "uranus", "neptune", "saturn", "mars", "pluto"]
        breakers = {agent: CircuitBreaker(agent) for agent in agents}
        self.save_state(breakers)
        return breakers

    def save_state(self, breakers=None):
        if breakers is None:
            breakers = self.circuit_breakers
        data = {name: cb.to_dict() for name, cb in breakers.items()}
        with open(self.state_file, "w") as f:
            json.dump(data, f, indent=2)

    def log(self, message):
        entry = f"[{datetime.now()}] {message}\n"
        print(entry.strip())
        with open(self.log_file, "a") as f:
            f.write(entry)

    async def worker(self, worker_id):
        while True:
            task_file = await self.task_queue.get()
            try:
                await self.execute_agent(task_file)
            finally:
                self.task_queue.task_done()

    async def execute_agent(self, task_file: Path):
        try:
            with open(task_file) as f:
                task = json.load(f)
            agent = task.get("agent", "unknown").lower()
            self.log(f"🔄 Worker executing {agent}")
            # Real agent execution
            import subprocess
            result = subprocess.run(
                ["python3", str(self.base / "agents" / "execute_task.py"), str(task_file)],
                capture_output=True, text=True
            )
            self.log(result.stdout.strip() if result.stdout else f"✅ {agent} completed")
            task_file.rename(self.ipc_completed / task_file.name)
        except Exception as e:
            self.log(f"❌ Agent error: {e}")

    async def run_forever(self):
        self.log("🌍 EARTH ORCHESTRATOR DAEMON STARTED (persistent mode)")
        
        # Start worker pool
        workers = [asyncio.create_task(self.worker(i)) for i in range(self.max_concurrency)]

        while True:
            # Look for new pending tasks
            pending = list(self.ipc_pending.glob("*.json"))
            for task_file in pending:
                await self.task_queue.put(task_file)

            await self.task_queue.join()
            self.save_state()
            await asyncio.sleep(15)  # Check for new tasks every 15 seconds

if __name__ == "__main__":
    orch = C25Orchestrator()
    try:
        asyncio.run(orch.run_forever())
    except KeyboardInterrupt:
        print("\nOrchestrator stopped by user")
