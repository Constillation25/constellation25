#!/data/data/com.termux/files/usr/bin/python3
"""
Serverless Compute Router
Decision tree that routes workloads to the right compute product:
- Serverless Containers (web services, microservices that can't be split)
- Serverless Functions (short tasks, small functions, auto-scaling)
- Serverless Jobs (long-running tasks >15 minutes)
"""
import json
import time
import subprocess
import threading
import logging
from pathlib import Path
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s [SERVERLESS] %(message)s')
logger = logging.getLogger(__name__)

class ServerlessFunction:
    """Short-lived function execution (<15 min, auto-scaling)"""
    def __init__(self, runtime="python3"):
        self.runtime = runtime
        self.functions_dir = Path.home() / "constellation25" / "serverless" / "functions"
        self.functions_dir.mkdir(parents=True, exist_ok=True)
        self.executions = []

    def deploy(self, name, code, handler="handler"):
        """Deploy a serverless function"""
        func_dir = self.functions_dir / name
        func_dir.mkdir(exist_ok=True)

        func_file = func_dir / f"{name}.{self._get_extension()}"
        with open(func_file, 'w') as f:
            f.write(code)

        config = {
            "name": name,
            "runtime": self.runtime,
            "handler": handler,
            "deployed": datetime.now().isoformat(),
            "type": "function"
        }

        with open(func_dir / "config.json", 'w') as f:
            json.dump(config, f, indent=2)

        logger.info(f"Function deployed: {name} ({self.runtime})")
        return config

    def invoke(self, name, payload=None):
        """Invoke a serverless function"""
        func_dir = self.functions_dir / name
        config_file = func_dir / "config.json"

        if not config_file.exists():
            return {"error": f"Function {name} not found"}

        with open(config_file, 'r') as f:
            config = json.load(f)

        start_time = time.time()
        # Simulate execution
        result = {"status": "success", "name": name, "payload": payload}
        duration = time.time() - start_time

        execution = {
            "id": f"exec_{int(time.time())}",
            "function": name,
            "started": datetime.now().isoformat(),
            "duration_ms": round(duration * 1000, 2),
            "status": "success",
            "cold_start": True
        }

        self.executions.append(execution)
        logger.info(f"Function invoked: {name} ({execution['duration_ms']}ms)")
        return result

    def _get_extension(self):
        extensions = {"python3": "py", "nodejs": "js", "go": "go"}
        return extensions.get(self.runtime, "py")

class ServerlessContainer:
    """Container-based web service (microservices that can't be split)"""
    def __init__(self):
        self.containers_dir = Path.home() / "constellation25" / "serverless" / "containers"
        self.containers_dir.mkdir(parents=True, exist_ok=True)
        self.running = {}

    def deploy(self, name, dockerfile_content, port=8080):
        """Deploy a serverless container"""
        container_dir = self.containers_dir / name
        container_dir.mkdir(exist_ok=True)

        with open(container_dir / "Dockerfile", 'w') as f:
            f.write(dockerfile_content)

        config = {
            "name": name,
            "port": port,
            "deployed": datetime.now().isoformat(),
            "type": "container",
            "status": "deployed"
        }

        with open(container_dir / "config.json", 'w') as f:
            json.dump(config, f, indent=2)

        self.running[name] = config
        logger.info(f"Container deployed: {name} on port {port}")
        return config

    def start(self, name):
        """Start a container"""
        if name not in self.running:
            return {"error": f"Container {name} not deployed"}

        self.running[name]["status"] = "running"
        self.running[name]["started"] = datetime.now().isoformat()
        logger.info(f"Container started: {name}")
        return self.running[name]

    def stop(self, name):
        """Stop a container"""
        if name in self.running:
            self.running[name]["status"] = "stopped"
            logger.info(f"Container stopped: {name}")
            return True
        return False

class ServerlessJob:
    """Long-running job execution (>15 minutes)"""
    def __init__(self):
        self.jobs_dir = Path.home() / "constellation25" / "serverless" / "jobs"
        self.jobs_dir.mkdir(parents=True, exist_ok=True)
        self.jobs = {}

    def submit(self, name, command, max_duration_minutes=60):
        """Submit a long-running job"""
        job_id = f"job_{int(time.time())}"

        job = {
            "id": job_id,
            "name": name,
            "command": command,
            "max_duration_minutes": max_duration_minutes,
            "submitted": datetime.now().isoformat(),
            "status": "queued",
            "type": "job"
        }

        self.jobs[job_id] = job

        # Save job definition
        job_file = self.jobs_dir / f"{job_id}.json"
        with open(job_file, 'w') as f:
            json.dump(job, f, indent=2)

        logger.info(f"Job submitted: {name} (max {max_duration_minutes} min)")
        return job

    def execute(self, job_id):
        """Execute a job"""
        if job_id not in self.jobs:
            return {"error": f"Job {job_id} not found"}

        job = self.jobs[job_id]
        job["status"] = "running"
        job["started"] = datetime.now().isoformat()

        logger.info(f"Job executing: {job['name']}")

        # Simulate long-running execution
        job["status"] = "completed"
        job["completed"] = datetime.now().isoformat()
        job["duration_minutes"] = 0.1  # Simulated

        return job

    def list_jobs(self):
        return list(self.jobs.values())

class ServerlessRouter:
    """
    Decision tree router - routes workloads to the right compute product
    Based on the decision tree diagram
    """
    def __init__(self):
        self.functions = ServerlessFunction()
        self.containers = ServerlessContainer()
        self.jobs = ServerlessJob()

    def route(self, app_type, **kwargs):
        """
        Route application to correct compute product
        app_type: "web" or "task"
        """
        if app_type == "web":
            return self._route_web(**kwargs)
        elif app_type == "task":
            return self._route_task(**kwargs)
        else:
            return {"error": "app_type must be 'web' or 'task'"}

    def _route_web(self, is_microservice=False, can_split=False, **kwargs):
        """Route web service"""
        if not is_microservice:
            # Not microservices → Serverless Containers
            return {
                "product": "Serverless Containers",
                "reason": "Web service not based on microservices",
                "action": "deploy_container"
            }

        if is_microservice and can_split:
            # Microservices that can be split → Serverless Functions
            return {
                "product": "Serverless Functions",
                "reason": "Microservices can be split into small functions",
                "action": "deploy_function"
            }

        # Microservices that can't be split → Serverless Containers
        return {
            "product": "Serverless Containers",
            "reason": "Microservices cannot be split into small functions",
            "action": "deploy_container"
        }

    def _route_task(self, duration_minutes=10, needs_auto_scale=False, fits_runtime=True, **kwargs):
        """Route task"""
        if duration_minutes > 15:
            # Long task → Serverless Jobs
            return {
                "product": "Serverless Jobs",
                "reason": f"Task lasts {duration_minutes} minutes (>15 min)",
                "action": "submit_job"
            }

        if duration_minutes <= 15 and needs_auto_scale:
            if fits_runtime:
                # Short task, auto-scale, fits runtime → Serverless Functions
                return {
                    "product": "Serverless Functions",
                    "reason": "Short task with auto-scaling, fits runtime",
                    "action": "deploy_function"
                }
            else:
                # Doesn't fit runtime → Serverless Containers
                return {
                    "product": "Serverless Containers",
                    "reason": "Task doesn't fit serverless function runtimes",
                    "action": "deploy_container"
                }

        if duration_minutes <= 15 and not needs_auto_scale:
            # Short task, no auto-scale → Serverless Jobs
            return {
                "product": "Serverless Jobs",
                "reason": "Short task without auto-scaling requirement",
                "action": "submit_job"
            }

        return {"error": "Could not route task"}

    def get_status(self):
        return {
            "functions_deployed": len(list((self.functions.functions_dir).iterdir())) if self.functions.functions_dir.exists() else 0,
            "containers_running": len([c for c in self.containers.running.values() if c.get("status") == "running"]),
            "jobs_queued": len([j for j in self.jobs.jobs.values() if j["status"] == "queued"]),
            "total_executions": len(self.functions.executions)
        }

if __name__ == "__main__":
    router = ServerlessRouter()

    print("=== SERVERLESS COMPUTE ROUTER DEMO ===\n")

    # Test decision tree
    print("1. Routing decisions:")

    # Web service, not microservices → Containers
    result = router.route("web", is_microservice=False)
    print(f"   Web (no microservices) → {result['product']}")

    # Web service, microservices, can split → Functions
    result = router.route("web", is_microservice=True, can_split=True)
    print(f"   Web (microservices, splittable) → {result['product']}")

    # Web service, microservices, can't split → Containers
    result = router.route("web", is_microservice=True, can_split=False)
    print(f"   Web (microservices, not splittable) → {result['product']}")

    # Task >15 min → Jobs
    result = router.route("task", duration_minutes=30)
    print(f"   Task (30 min) → {result['product']}")

    # Task <15 min, auto-scale, fits runtime → Functions
    result = router.route("task", duration_minutes=5, needs_auto_scale=True, fits_runtime=True)
    print(f"   Task (5 min, auto-scale) → {result['product']}")

    # Task <15 min, no auto-scale → Jobs
    result = router.route("task", duration_minutes=10, needs_auto_scale=False)
    print(f"   Task (10 min, no auto-scale) → {result['product']}\n")

    # Deploy actual resources
    print("2. Deploying resources:")

    # Deploy a function
    func_code = """
def handler(event, context):
    return {"statusCode": 200, "body": "Hello from SovereignGTP!"}
"""
    router.functions.deploy("hello-function", func_code)
    router.functions.invoke("hello-function", {"name": "CyGeL"})

    # Deploy a container
    dockerfile = """FROM python:3.9-slim
WORKDIR /app
COPY . .
CMD ["python", "app.py"]
"""
    router.containers.deploy("videocourts-api", dockerfile, port=8080)
    router.containers.start("videocourts-api")

    # Submit a job
    router.jobs.submit("forensic-analysis", "python3 /app/analyze.py --full-scan", max_duration_minutes=45)

    # Status
    print("\n3. System status:")
    print(json.dumps(router.get_status(), indent=2))

    print("\n=== DECISION TREE SUMMARY ===")
    print("Web + No microservices → Serverless Containers")
    print("Web + Microservices + Splittable → Serverless Functions")
    print("Web + Microservices + Not splittable → Serverless Containers")
    print("Task >15 min → Serverless Jobs")
    print("Task <15 min + Auto-scale + Fits runtime → Serverless Functions")
    print("Task <15 min + No auto-scale → Serverless Jobs")
