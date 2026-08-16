#!/data/data/com.termux/files/usr/bin/python3
"""
WordPress HA Cluster
Internet → Load Balancer → WP1 + WP2 → Shared MariaDB
High-availability WordPress with shared database backend
"""
import json
import time
import hashlib
import threading
import logging
from pathlib import Path
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

logging.basicConfig(level=logging.INFO, format='%(asctime)s [WP-HA] %(message)s')
logger = logging.getLogger(__name__)

class MariaDB:
    """Shared MariaDB instance (simulated)"""
    def __init__(self, db_path=None):
        self.db_path = db_path or str(Path.home() / "constellation25" / "data" / "mariadb")
        Path(self.db_path).mkdir(parents=True, exist_ok=True)
        self.tables = {"wp_posts": [], "wp_users": [], "wp_options": []}
        self.connections = 0
        self.queries_executed = 0
        logger.info("MariaDB initialized")

    def execute_query(self, table, operation, data=None):
        """Execute database operation"""
        self.queries_executed += 1

        if operation == "INSERT":
            record = {**data, "id": len(self.tables[table]) + 1, "created": datetime.now().isoformat()}
            self.tables[table].append(record)
            return {"status": "success", "id": record["id"]}

        elif operation == "SELECT":
            if data and "id" in data:
                results = [r for r in self.tables[table] if r.get("id") == data["id"]]
            else:
                results = self.tables[table]
            return {"status": "success", "results": results, "count": len(results)}

        elif operation == "UPDATE":
            if data and "id" in data:
                for i, record in enumerate(self.tables[table]):
                    if record.get("id") == data["id"]:
                        self.tables[table][i].update(data)
                        return {"status": "success", "updated": 1}
            return {"status": "not_found"}

        elif operation == "DELETE":
            if data and "id" in data:
                original_len = len(self.tables[table])
                self.tables[table] = [r for r in self.tables[table] if r.get("id") != data["id"]]
                return {"status": "success", "deleted": original_len - len(self.tables[table])}
            return {"status": "error"}

        return {"status": "unknown_operation"}

    def get_stats(self):
        return {
            "tables": {t: len(rows) for t, rows in self.tables.items()},
            "active_connections": self.connections,
            "queries_executed": self.queries_executed
        }

class WordPressInstance:
    """Individual WordPress instance"""
    def __init__(self, instance_id, db):
        self.instance_id = instance_id
        self.db = db
        self.requests_served = 0
        self.uptime = 0
        self.status = "running"
        self.cache = {}

    def handle_request(self, path, method="GET", data=None):
        """Handle HTTP request"""
        self.requests_served += 1
        self.uptime += 1

        # Check cache first
        cache_key = f"{method}:{path}"
        if cache_key in self.cache and method == "GET":
            return {"source": "cache", "instance": self.instance_id, "data": self.cache[cache_key]}

        # Route to appropriate handler
        if path == "/" or path == "/index.php":
            response = self._serve_homepage()
        elif path.startswith("/wp-admin"):
            response = self._serve_admin(data)
        elif path.startswith("/api/posts"):
            if method == "POST":
                response = self._create_post(data)
            else:
                response = self._list_posts()
        else:
            response = {"status": 404, "message": "Not found"}

        # Cache GET responses
        if method == "GET":
            self.cache[cache_key] = response

        response["instance"] = self.instance_id
        return response

    def _serve_homepage(self):
        posts = self.db.execute_query("wp_posts", "SELECT")
        return {
            "status": 200,
            "type": "homepage",
            "posts": posts.get("results", []),
            "instance": self.instance_id
        }

    def _serve_admin(self, data):
        return {
            "status": 200,
            "type": "admin_panel",
            "instance": self.instance_id,
            "message": "WordPress Admin"
        }

    def _create_post(self, data):
        if not data:
            return {"status": 400, "message": "No data provided"}

        result = self.db.execute_query("wp_posts", "INSERT", data)
        # Invalidate cache
        self.cache.clear()
        return {"status": 201, "post_id": result.get("id")}

    def _list_posts(self):
        posts = self.db.execute_query("wp_posts", "SELECT")
        return {"status": 200, "posts": posts.get("results", [])}

    def get_status(self):
        return {
            "instance_id": self.instance_id,
            "status": self.status,
            "requests_served": self.requests_served,
            "uptime": self.uptime,
            "cache_size": len(self.cache)
        }

class LoadBalancer:
    """Load balancer distributing traffic across WP instances"""
    def __init__(self, algorithm="round_robin"):
        self.algorithm = algorithm
        self.instances = []
        self.current_index = 0
        self.total_requests = 0
        self.health_checks = {}

    def add_instance(self, instance):
        self.instances.append(instance)
        self.health_checks[instance.instance_id] = "healthy"
        logger.info(f"Instance added to LB: {instance.instance_id}")

    def get_next_instance(self):
        """Get next healthy instance based on algorithm"""
        if not self.instances:
            return None

        if self.algorithm == "round_robin":
            instance = self.instances[self.current_index % len(self.instances)]
            self.current_index += 1
            return instance

        elif self.algorithm == "least_connections":
            return min(self.instances, key=lambda i: i.requests_served)

        return self.instances[0]

    def route_request(self, path, method="GET", data=None):
        """Route request to appropriate instance"""
        self.total_requests += 1

        instance = self.get_next_instance()
        if not instance:
            return {"status": 503, "message": "No instances available"}

        response = instance.handle_request(path, method, data)
        return response

    def health_check(self):
        """Check health of all instances"""
        for instance in self.instances:
            if instance.status == "running":
                self.health_checks[instance.instance_id] = "healthy"
            else:
                self.health_checks[instance.instance_id] = "unhealthy"

    def get_status(self):
        return {
            "algorithm": self.algorithm,
            "total_requests": self.total_requests,
            "instances": [i.get_status() for i in self.instances],
            "health": self.health_checks
        }

class WordPressHACluster:
    """Complete HA WordPress setup"""
    def __init__(self):
        self.db = MariaDB()
        self.lb = LoadBalancer("round_robin")

    def setup(self, num_instances=2):
        """Setup HA cluster with multiple WP instances"""
        for i in range(num_instances):
            instance = WordPressInstance(f"WP-{i+1}", self.db)
            self.lb.add_instance(instance)

        logger.info(f"HA Cluster setup: {num_instances} WP instances + MariaDB")

    def create_post(self, title, content, author):
        """Create a post (routed through LB)"""
        return self.lb.route_request(
            "/api/posts",
            method="POST",
            data={"title": title, "content": content, "author": author}
        )

    def get_homepage(self):
        """Get homepage (routed through LB)"""
        return self.lb.route_request("/")

    def get_cluster_status(self):
        return {
            "load_balancer": self.lb.get_status(),
            "database": self.db.get_stats()
        }

if __name__ == "__main__":
    cluster = WordPressHACluster()

    print("=== WORDPRESS HA CLUSTER DEMO ===\n")

    # Setup cluster
    print("1. Setting up HA cluster:")
    cluster.setup(num_instances=2)
    print(f"   Instances: WP-1, WP-2")
    print(f"   Database: MariaDB (shared)\n")

    # Create posts
    print("2. Creating posts:")
    result = cluster.create_post("Hello World", "Welcome to SovereignGTP", "CyGeL")
    print(f"   Post created: {result}")

    result = cluster.create_post("BioAuth Integration", "Biometric auth working", "CyGeL")
    print(f"   Post created: {result}\n")

    # Serve homepage (load balanced)
    print("3. Serving homepage (load balanced):")
    for i in range(4):
        response = cluster.get_homepage()
        print(f"   Request {i+1} → {response['instance']} ({response['type']})")

    print()

    # Cluster status
    print("4. Cluster status:")
    status = cluster.get_cluster_status()
    print(f"   Load Balancer: {status['load_balancer']['algorithm']}")
    print(f"   Total requests: {status['load_balancer']['total_requests']}")
    print(f"   Database queries: {status['database']['queries_executed']}")
    print(f"   Posts in DB: {status['database']['tables']['wp_posts']}")

    print("\n=== WORDPRESS HA ARCHITECTURE ===")
    print("Internet → Load Balancer → WP-1 + WP-2 → Shared MariaDB")
    print("Features: Round-robin LB, shared DB, per-instance caching")
