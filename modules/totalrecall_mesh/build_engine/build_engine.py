#!/data/data/com.termux/files/usr/bin/python3
"""
TotalRecall Build Engine
Uses the agent mesh to build, validate, and deploy environments
Pipeline: Source → Agent Mesh → Build Artifact → Deploy/Archive
"""
import json
import time
import hashlib
import logging
from pathlib import Path
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s [TR-BUILD] %(message)s')
logger = logging.getLogger(__name__)

class BuildEnvironment:
    """A build environment (like a VM or container)"""
    def __init__(self, env_id, env_type):
        self.env_id = env_id
        self.env_type = env_type  # development, staging, production, forensic
        self.status = "initialized"
        self.created = datetime.now().isoformat()
        self.components = []
        self.deployments = []
        self.forensic_snapshots = []

    def add_component(self, component):
        self.components.append(component)
        logger.info(f"Component added to {self.env_id}: {component.get('name')}")

    def deploy(self, artifact):
        deployment = {
            "deployment_id": f"DEP-{int(time.time())}",
            "artifact_id": artifact.get("artifact_id"),
            "deployed_at": datetime.now().isoformat(),
            "status": "deployed"
        }
        self.deployments.append(deployment)
        logger.info(f"Deployed to {self.env_id}: {deployment['deployment_id']}")
        return deployment

    def take_forensic_snapshot(self):
        snapshot = {
            "snapshot_id": f"SNAP-{int(time.time())}",
            "taken_at": datetime.now().isoformat(),
            "components": len(self.components),
            "deployments": len(self.deployments),
            "hash": hashlib.sha256(f"{self.env_id}{time.time()}".encode()).hexdigest()
        }
        self.forensic_snapshots.append(snapshot)
        logger.info(f"Forensic snapshot taken: {snapshot['snapshot_id']}")
        return snapshot

    def get_env_info(self):
        return {
            "env_id": self.env_id,
            "env_type": self.env_type,
            "status": self.status,
            "components": len(self.components),
            "deployments": len(self.deployments),
            "forensic_snapshots": len(self.forensic_snapshots)
        }

class BuildEngine:
    """TotalRecall Build Engine"""
    def __init__(self):
        self.environments = {}
        self.build_queue = []
        self.completed_builds = []
        self.build_dir = Path.home() / "constellation25" / "builds"
        self.build_dir.mkdir(parents=True, exist_ok=True)

    def create_environment(self, env_type="development"):
        """Create a new build environment"""
        env_id = f"env-{env_type}-{int(time.time())}"
        env = BuildEnvironment(env_id, env_type)
        self.environments[env_id] = env
        logger.info(f"Environment created: {env_id} ({env_type})")
        return env

    def queue_build(self, source, source_type, target_env=None):
        """Queue a build"""
        build_id = f"BUILD-{int(time.time())}"
        build = {
            "build_id": build_id,
            "source": source,
            "source_type": source_type,
            "target_env": target_env,
            "queued_at": datetime.now().isoformat(),
            "status": "queued"
        }
        self.build_queue.append(build)
        logger.info(f"Build queued: {build_id}")
        return build

    def execute_build(self, build, agent_mesh):
        """Execute a build through the agent mesh"""
        build["status"] = "running"
        build["started_at"] = datetime.now().isoformat()

        # Run through agent mesh
        result = agent_mesh.run_pipeline(build["source"], build["source_type"])

        build["status"] = "completed"
        build["completed_at"] = datetime.now().isoformat()
        build["result"] = result

        # If routed to deploy, deploy to target environment
        if result.get("final_destination") == "deploy" and build.get("target_env"):
            if build["target_env"] in self.environments:
                artifact = result["results"].get("compile", {}).get("artifact", {})
                self.environments[build["target_env"]].deploy(artifact)

        self.completed_builds.append(build)
        self.build_queue = [b for b in self.build_queue if b["build_id"] != build["build_id"]]

        logger.info(f"Build completed: {build['build_id']} → {result.get('final_destination')}")
        return build

    def process_queue(self, agent_mesh):
        """Process all queued builds"""
        results = []
        for build in list(self.build_queue):
            result = self.execute_build(build, agent_mesh)
            results.append(result)
        return results

    def take_all_snapshots(self):
        """Take forensic snapshots of all environments"""
        snapshots = []
        for env in self.environments.values():
            snapshot = env.take_forensic_snapshot()
            snapshots.append({"env_id": env.env_id, "snapshot": snapshot})
        return snapshots

    def get_engine_status(self):
        return {
            "environments": len(self.environments),
            "queued_builds": len(self.build_queue),
            "completed_builds": len(self.completed_builds),
            "environment_details": {eid: env.get_env_info() for eid, env in self.environments.items()}
        }

if __name__ == "__main__":
    from agent_mesh import AgentMesh

    engine = BuildEngine()
    mesh = AgentMesh()

    print("=== TOTALRECALL BUILD ENGINE DEMO ===\n")

    # Create environments
    print("1. Creating build environments:")
    dev_env = engine.create_environment("development")
    prod_env = engine.create_environment("production")
    forensic_env = engine.create_environment("forensic")
    print(f"   Environments: {len(engine.environments)}")
    for eid, env in engine.environments.items():
        print(f"     - {eid} ({env.env_type})")
    print()

    # Queue builds
    print("2. Queueing builds:")
    source1 = "def forensic_analyzer(): return analyze()"
    source2 = "class EvidenceVault: def store(self, data): pass"
    source3 = "# Low value comment only"

    build1 = engine.queue_build(source1, "forensic_code", "dev")
    build2 = engine.queue_build(source2, "forensic_code", "prod")
    build3 = engine.queue_build(source3, "forensic_code", "forensic")
    print(f"   Queued: {len(engine.build_queue)} builds")
    print()

    # Process queue
    print("3. Processing build queue through agent mesh:")
    results = engine.process_queue(mesh)
    for r in results:
        print(f"   {r['build_id']}: {r['status']} → {r['result'].get('final_destination')}")
    print()

    # Take forensic snapshots
    print("4. Taking forensic snapshots:")
    snapshots = engine.take_all_snapshots()
    for s in snapshots:
        print(f"   {s['env_id']}: {s['snapshot']['snapshot_id']}")
    print()

    # Engine status
    print("5. Build engine status:")
    status = engine.get_engine_status()
    print(f"   Environments: {status['environments']}")
    print(f"   Queued: {status['queued_builds']}")
    print(f"   Completed: {status['completed_builds']}")

    print("\n=== BUILD ENGINE ARCHITECTURE ===")
    print("Source → Queue → Agent Mesh → Build → Deploy/Archive")
    print("Environments: development, staging, production, forensic")
