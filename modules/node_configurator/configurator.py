#!/data/data/com.termux/files/usr/bin/python3
"""
Node Configurator
Configure node pool options: Autoscale, Autoheal, Placement Groups
Based on "Configure Nodes Options" UI diagram
"""
import json
import time
import logging
from pathlib import Path
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s [NODE-CONFIG] %(message)s')
logger = logging.getLogger(__name__)

class NodePool:
    """Node pool with configuration options"""
    def __init__(self, pool_id, pool_name):
        self.pool_id = pool_id
        self.pool_name = pool_name
        self.created = datetime.now().isoformat()

        # Configuration options
        self.autoscale = {
            "enabled": False,
            "min_nodes": 1,
            "max_nodes": 500,
            "current_nodes": 1,
            "target_nodes": 1
        }

        self.autoheal = {
            "enabled": True,
            "check_interval_seconds": 60,
            "unhealthy_threshold": 3,
            "last_check": None,
            "nodes_replaced": 0
        }

        self.placement_group = {
            "linked": False,
            "group_id": None,
            "max_instances": 20,
            "warning": "Placement groups are limited to 20 instances. By activating this feature on your pool, you won't be able to scale it beyond 20 nodes."
        }

        self.nodes = []
        self._initialize_nodes()

    def _initialize_nodes(self):
        """Initialize nodes based on current count"""
        for i in range(self.autoscale["current_nodes"]):
            node = {
                "node_id": f"{self.pool_id}-node-{i+1}",
                "status": "ready",
                "created": datetime.now().isoformat(),
                "health_status": "healthy",
                "consecutive_unhealthy": 0
            }
            self.nodes.append(node)

    def configure_autoscale(self, enabled, min_nodes=1, max_nodes=500):
        """Configure autoscaling"""
        self.autoscale["enabled"] = enabled
        self.autoscale["min_nodes"] = min_nodes
        self.autoscale["max_nodes"] = max_nodes

        if enabled:
            logger.info(f"Autoscale enabled: {min_nodes}-{max_nodes} nodes")
        else:
            logger.info(f"Autoscale disabled: fixed at {self.autoscale['current_nodes']} nodes")

        return self.autoscale

    def configure_autoheal(self, enabled, check_interval=60, unhealthy_threshold=3):
        """Configure autoheal"""
        self.autoheal["enabled"] = enabled
        self.autoheal["check_interval_seconds"] = check_interval
        self.autoheal["unhealthy_threshold"] = unhealthy_threshold

        if enabled:
            logger.info(f"Autoheal enabled: check every {check_interval}s, threshold {unhealthy_threshold}")
        else:
            logger.info("Autoheal disabled")

        return self.autoheal

    def link_placement_group(self, group_id):
        """Link to existing placement group"""
        if self.autoscale["max_nodes"] > 20:
            logger.warning("Warning: Linking placement group will limit scaling to 20 nodes")
            self.autoscale["max_nodes"] = 20

        self.placement_group["linked"] = True
        self.placement_group["group_id"] = group_id

        logger.info(f"Placement group linked: {group_id} (max 20 nodes)")
        return self.placement_group

    def simulate_node_failure(self, node_id):
        """Simulate node becoming unhealthy"""
        for node in self.nodes:
            if node["node_id"] == node_id:
                node["health_status"] = "unhealthy"
                node["consecutive_unhealthy"] += 1
                logger.warning(f"Node {node_id} is unhealthy (count: {node['consecutive_unhealthy']})")
                return node
        return None

    def run_autoheal_check(self):
        """Run autoheal check and replace unhealthy nodes"""
        if not self.autoheal["enabled"]:
            return {"status": "disabled"}

        self.autoheal["last_check"] = datetime.now().isoformat()
        replaced_nodes = []

        for node in self.nodes[:]:  # Copy list to avoid modification during iteration
            if node["health_status"] == "unhealthy":
                if node["consecutive_unhealthy"] >= self.autoheal["unhealthy_threshold"]:
                    # Replace node
                    logger.info(f"Autoheal: Replacing unhealthy node {node['node_id']}")
                    self.nodes.remove(node)
                    replaced_nodes.append(node["node_id"])
                    self.autoheal["nodes_replaced"] += 1

                    # Add new healthy node
                    new_node = {
                        "node_id": f"{self.pool_id}-node-{int(time.time())}",
                        "status": "ready",
                        "created": datetime.now().isoformat(),
                        "health_status": "healthy",
                        "consecutive_unhealthy": 0
                    }
                    self.nodes.append(new_node)

        return {
            "status": "completed",
            "replaced_nodes": replaced_nodes,
            "total_replaced": self.autoheal["nodes_replaced"]
        }

    def scale_nodes(self, target_count):
        """Scale node count (manual or autoscale)"""
        if self.placement_group["linked"] and target_count > 20:
            return {"error": "Cannot scale beyond 20 nodes with placement group"}

        if self.autoscale["enabled"]:
            if target_count < self.autoscale["min_nodes"] or target_count > self.autoscale["max_nodes"]:
                return {"error": f"Target must be between {self.autoscale['min_nodes']} and {self.autoscale['max_nodes']}"}

        current = len(self.nodes)
        if target_count > current:
            # Scale up
            for i in range(target_count - current):
                new_node = {
                    "node_id": f"{self.pool_id}-node-{int(time.time())}-{i}",
                    "status": "ready",
                    "created": datetime.now().isoformat(),
                    "health_status": "healthy",
                    "consecutive_unhealthy": 0
                }
                self.nodes.append(new_node)
            logger.info(f"Scaled up: {current} → {target_count} nodes")
        elif target_count < current:
            # Scale down
            self.nodes = self.nodes[:target_count]
            logger.info(f"Scaled down: {current} → {target_count} nodes")

        self.autoscale["current_nodes"] = len(self.nodes)
        return {"status": "scaled", "current_nodes": len(self.nodes)}

    def get_pool_status(self):
        return {
            "pool_id": self.pool_id,
            "pool_name": self.pool_name,
            "autoscale": self.autoscale,
            "autoheal": self.autoheal,
            "placement_group": self.placement_group,
            "nodes": len(self.nodes),
            "node_details": self.nodes
        }

class NodeConfigurator:
    """Main configurator for node pools"""
    def __init__(self):
        self.pools = {}

    def create_pool(self, pool_name, initial_nodes=1):
        """Create a new node pool"""
        pool_id = f"pool-{len(self.pools) + 1}"
        pool = NodePool(pool_id, pool_name)
        pool.autoscale["current_nodes"] = initial_nodes
        pool._initialize_nodes()
        self.pools[pool_id] = pool

        logger.info(f"Pool created: {pool_name} ({initial_nodes} nodes)")
        return pool

    def configure_pool(self, pool_id, autoscale=None, autoheal=None, placement_group=None):
        """Configure pool options"""
        if pool_id not in self.pools:
            return {"error": f"Pool {pool_id} not found"}

        pool = self.pools[pool_id]
        results = {}

        if autoscale:
            results["autoscale"] = pool.configure_autoscale(**autoscale)

        if autoheal:
            results["autoheal"] = pool.configure_autoheal(**autoheal)

        if placement_group:
            results["placement_group"] = pool.link_placement_group(placement_group["group_id"])

        return results

    def get_all_pools_status(self):
        return {
            "total_pools": len(self.pools),
            "pools": {pid: pool.get_pool_status() for pid, pool in self.pools.items()}
        }

if __name__ == "__main__":
    configurator = NodeConfigurator()

    print("=== NODE CONFIGURATOR DEMO ===\n")

    # Create pool
    print("1. Creating node pool:")
    pool = configurator.create_pool("default-pool", initial_nodes=1)
    print(f"   Pool: {pool.pool_name}")
    print(f"   Initial nodes: {len(pool.nodes)}\n")

    # Configure autoscale
    print("2. Configuring autoscale:")
    result = configurator.configure_pool(
        pool.pool_id,
        autoscale={"enabled": False, "min_nodes": 1, "max_nodes": 500}
    )
    print(f"   Autoscale: {result['autoscale']['enabled']}")
    print(f"   Range: {result['autoscale']['min_nodes']}-{result['autoscale']['max_nodes']}\n")

    # Configure autoheal
    print("3. Configuring autoheal:")
    result = configurator.configure_pool(
        pool.pool_id,
        autoheal={"enabled": True, "check_interval": 60, "unhealthy_threshold": 3}
    )
    print(f"   Autoheal: {result['autoheal']['enabled']}")
    print(f"   Check interval: {result['autoheal']['check_interval_seconds']}s")
    print(f"   Unhealthy threshold: {result['autoheal']['unhealthy_threshold']}\n")

    # Simulate node failure and autoheal
    print("4. Simulating node failure:")
    node_id = pool.nodes[0]["node_id"]
    for i in range(3):
        pool.simulate_node_failure(node_id)
    print(f"   Node {node_id} unhealthy count: {pool.nodes[0]['consecutive_unhealthy']}")

    print("\n5. Running autoheal check:")
    heal_result = pool.run_autoheal_check()
    print(f"   Status: {heal_result['status']}")
    print(f"   Replaced nodes: {heal_result['replaced_nodes']}")
    print(f"   Total replaced: {heal_result['total_replaced']}")
    print(f"   Current nodes: {len(pool.nodes)}\n")

    # Scale nodes
    print("6. Scaling nodes:")
    scale_result = pool.scale_nodes(3)
    print(f"   {scale_result['status']}: {scale_result['current_nodes']} nodes\n")

    # Link placement group
    print("7. Linking placement group:")
    result = configurator.configure_pool(
        pool.pool_id,
        placement_group={"group_id": "pg-12345"}
    )
    print(f"   Linked: {result['placement_group']['linked']}")
    print(f"   Group ID: {result['placement_group']['group_id']}")
    print(f"   Max nodes: {result['placement_group']['max_instances']}")
    print(f"   Warning: {result['placement_group']['warning']}\n")

    # Try to scale beyond 20
    print("8. Attempting to scale beyond 20 nodes (should fail):")
    scale_result = pool.scale_nodes(25)
    print(f"   Result: {scale_result.get('error', 'success')}\n")

    # Final status
    print("9. Final pool status:")
    status = configurator.get_all_pools_status()
    pool_status = status["pools"][pool.pool_id]
    print(f"   Pool: {pool_status['pool_name']}")
    print(f"   Autoscale: {pool_status['autoscale']['enabled']}")
    print(f"   Autoheal: {pool_status['autoheal']['enabled']}")
    print(f"   Placement group: {pool_status['placement_group']['linked']}")
    print(f"   Current nodes: {pool_status['nodes']}")

    print("\n=== NODE CONFIGURATOR OPTIONS ===")
    print("✓ Autoscale: Automatically scale nodes up/down (impacts pricing)")
    print("✓ Autoheal: Periodic health checks, replace unhealthy nodes")
    print("✓ Placement groups: Link to existing group (max 20 nodes)")
