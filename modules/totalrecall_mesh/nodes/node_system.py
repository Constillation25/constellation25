#!/data/data/com.termux/files/usr/bin/python3
"""
TotalRecall Node System
Distributed mesh of nodes that host the agent workers
Each node: registers, heartbeats, reports capacity, executes tasks
"""
import json
import time
import uuid
import hashlib
import logging
import os
from pathlib import Path
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s [TR-NODE] %(message)s')
logger = logging.getLogger(__name__)

class TotalRecallNode:
    """A single node in the TotalRecall mesh"""
    def __init__(self, node_id=None, node_type="worker"):
        self.node_id = node_id or f"node-{uuid.uuid4().hex[:8]}"
        self.node_type = node_type  # worker, compiler, router, orchestrator
        self.hostname = os.uname().nodename
        self.status = "idle"  # idle, busy, offline, degraded
        self.registered_at = datetime.now().isoformat()
        self.last_heartbeat = datetime.now().isoformat()
        self.tasks_completed = 0
        self.tasks_failed = 0
        self.current_task = None

        # Capacity
        self.cpu_cores = os.cpu_count() or 4
        self.memory_mb = self._get_memory_mb()
        self.disk_free_gb = self._get_disk_free_gb()
        self.agent_slots = min(4, self.cpu_cores)
        self.active_agents = 0

        # Capabilities
        self.capabilities = self._detect_capabilities()

        # IPC paths
        self.ipc_dir = Path.home() / "c25_ipc"
        self.node_dir = self.ipc_dir / "nodes" / self.node_id
        self.node_dir.mkdir(parents=True, exist_ok=True)

    def _get_memory_mb(self):
        try:
            with open('/proc/meminfo', 'r') as f:
                for line in f:
                    if line.startswith('MemTotal:'):
                        return int(line.split()[1]) // 1024
        except:
            return 2048
        return 2048

    def _get_disk_free_gb(self):
        try:
            stat = os.statvfs(str(Path.home()))
            return (stat.f_bavail * stat.f_frsize) / (1024**3)
        except:
            return 10.0

    def _detect_capabilities(self):
        caps = ["python3", "bash", "git"]
        # Check for optional tools
        for tool in ["docker", "node", "gcc", "ffmpeg", "tesseract"]:
            try:
                import shutil
                if shutil.which(tool):
                    caps.append(tool)
            except:
                pass
        return caps

    def heartbeat(self):
        """Send heartbeat and update status"""
        self.last_heartbeat = datetime.now().isoformat()
        self.status = "idle" if not self.current_task else "busy"

        # Write heartbeat file for mesh discovery
        heartbeat_file = self.node_dir / "heartbeat.json"
        with open(heartbeat_file, 'w') as f:
            json.dump({
                "node_id": self.node_id,
                "status": self.status,
                "last_heartbeat": self.last_heartbeat,
                "tasks_completed": self.tasks_completed,
                "active_agents": self.active_agents,
                "capabilities": self.capabilities
            }, f, indent=2)

    def claim_task(self, task):
        """Claim a task for execution"""
        self.current_task = task
        self.status = "busy"
        self.active_agents += 1
        logger.info(f"Node {self.node_id} claimed task: {task.get('task_id')}")
        return True

    def complete_task(self, success=True):
        """Mark task as complete"""
        if success:
            self.tasks_completed += 1
        else:
            self.tasks_failed += 1
        self.current_task = None
        self.active_agents = max(0, self.active_agents - 1)
        self.status = "idle"

    def get_node_info(self):
        return {
            "node_id": self.node_id,
            "node_type": self.node_type,
            "hostname": self.hostname,
            "status": self.status,
            "cpu_cores": self.cpu_cores,
            "memory_mb": self.memory_mb,
            "disk_free_gb": round(self.disk_free_gb, 2),
            "agent_slots": self.agent_slots,
            "active_agents": self.active_agents,
            "capabilities": self.capabilities,
            "tasks_completed": self.tasks_completed,
            "tasks_failed": self.tasks_failed,
            "last_heartbeat": self.last_heartbeat
        }

class NodeMesh:
    """Manages the mesh of TotalRecall nodes"""
    def __init__(self, mesh_name="totalrecall-mesh"):
        self.mesh_name = mesh_name
        self.nodes = {}
        self.mesh_dir = Path.home() / "c25_ipc" / "mesh"
        self.mesh_dir.mkdir(parents=True, exist_ok=True)

    def register_node(self, node):
        """Register a node in the mesh"""
        self.nodes[node.node_id] = node
        self._save_mesh_state()
        logger.info(f"Node registered: {node.node_id} ({node.node_type})")
        return node.get_node_info()

    def deregister_node(self, node_id):
        """Remove a node from the mesh"""
        if node_id in self.nodes:
            del self.nodes[node_id]
            self._save_mesh_state()
            logger.info(f"Node deregistered: {node_id}")

    def discover_nodes(self):
        """Discover nodes via heartbeat files"""
        nodes_dir = Path.home() / "c25_ipc" / "nodes"
        if not nodes_dir.exists():
            return []

        discovered = []
        for node_dir in nodes_dir.iterdir():
            heartbeat = node_dir / "heartbeat.json"
            if heartbeat.exists():
                try:
                    with open(heartbeat, 'r') as f:
                        data = json.load(f)
                    # Check if heartbeat is fresh (< 60 seconds)
                    last_hb = datetime.fromisoformat(data["last_heartbeat"])
                    age = (datetime.now() - last_hb).total_seconds()
                    if age < 60:
                        discovered.append(data)
                except:
                    pass
        return discovered

    def find_best_node(self, task_requirements=None):
        """Find the best node for a task"""
        available = [n for n in self.nodes.values() if n.status == "idle"]
        if not available:
            return None

        # Score nodes
        scored = []
        for node in available:
            score = 0
            score += node.cpu_cores * 10
            score += (node.memory_mb // 512) * 5
            score += node.tasks_completed
            if task_requirements:
                for cap in task_requirements.get("capabilities", []):
                    if cap in node.capabilities:
                        score += 20
            scored.append((score, node))

        scored.sort(key=lambda x: x[0], reverse=True)
        return scored[0][1] if scored else None

    def broadcast_heartbeat(self):
        """All nodes send heartbeat"""
        for node in self.nodes.values():
            node.heartbeat()

    def get_mesh_status(self):
        total_tasks = sum(n.tasks_completed for n in self.nodes.values())
        total_failed = sum(n.tasks_failed for n in self.nodes.values())
        active = len([n for n in self.nodes.values() if n.status == "busy"])
        idle = len([n for n in self.nodes.values() if n.status == "idle"])

        return {
            "mesh_name": self.mesh_name,
            "total_nodes": len(self.nodes),
            "active_nodes": active,
            "idle_nodes": idle,
            "total_tasks_completed": total_tasks,
            "total_tasks_failed": total_failed,
            "success_rate": f"{(total_tasks / max(total_tasks + total_failed, 1) * 100):.1f}%",
            "nodes": [n.get_node_info() for n in self.nodes.values()]
        }

    def _save_mesh_state(self):
        state_file = self.mesh_dir / "mesh_state.json"
        state = {
            "mesh_name": self.mesh_name,
            "nodes": {nid: n.get_node_info() for nid, n in self.nodes.items()},
            "updated": datetime.now().isoformat()
        }
        with open(state_file, 'w') as f:
            json.dump(state, f, indent=2)

if __name__ == "__main__":
    mesh = NodeMesh("totalrecall-builder-mesh")

    print("=== TOTALRECALL NODE SYSTEM DEMO ===\n")

    # Register nodes
    print("1. Registering mesh nodes:")
    node1 = TotalRecallNode(node_type="compiler")
    node2 = TotalRecallNode(node_type="worker")
    node3 = TotalRecallNode(node_type="router")
    node4 = TotalRecallNode(node_type="orchestrator")

    for node in [node1, node2, node3, node4]:
        info = mesh.register_node(node)
        print(f"   {info['node_id']}: {info['node_type']} ({info['cpu_cores']} cores, {info['memory_mb']}MB)")
    print()

    # Send heartbeats
    print("2. Broadcasting heartbeats:")
    mesh.broadcast_heartbeat()
    print(f"   Nodes online: {len(mesh.nodes)}\n")

    # Find best node for task
    print("3. Finding best node for compile task:")
    best = mesh.find_best_node({"capabilities": ["python3", "git"]})
    if best:
        print(f"   Selected: {best.node_id} ({best.node_type})")
        print(f"   Score: {best.cpu_cores} cores, {best.memory_mb}MB RAM")
    print()

    # Claim and complete task
    print("4. Executing task on node:")
    task = {"task_id": "compile-001", "type": "compile", "source": "forensic_evidence"}
    best.claim_task(task)
    print(f"   Node {best.node_id} status: {best.status}")
    time.sleep(0.1)
    best.complete_task(success=True)
    print(f"   Task completed. Node status: {best.status}")
    print(f"   Tasks completed: {best.tasks_completed}\n")

    # Mesh status
    print("5. Mesh status:")
    status = mesh.get_mesh_status()
    print(f"   Mesh: {status['mesh_name']}")
    print(f"   Total nodes: {status['total_nodes']}")
    print(f"   Active: {status['active_nodes']}, Idle: {status['idle_nodes']}")
    print(f"   Tasks completed: {status['total_tasks_completed']}")
    print(f"   Success rate: {status['success_rate']}")

    print("\n=== NODE SYSTEM ARCHITECTURE ===")
    print("Mesh nodes: compiler, worker, router, orchestrator")
    print("Discovery: heartbeat files in ~/c25_ipc/nodes/")
    print("Routing: score-based best node selection")
