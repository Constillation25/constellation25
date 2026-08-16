#!/data/data/com.termux/files/usr/bin/python3
"""
Docker Container Runner
Runs containers with port mapping, environment variables
Simulates: docker run -p 4000:80 helloworld
Based on Flask app running in container diagram
"""
import json
import time
import socket
import threading
import logging
from pathlib import Path
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler

logging.basicConfig(level=logging.INFO, format='%(asctime)s [DOCKER] %(message)s')
logger = logging.getLogger(__name__)

class ContainerConfig:
    """Container configuration"""
    def __init__(self, image_name, tag="latest"):
        self.image_name = image_name
        self.tag = tag
        self.full_image = f"{image_name}:{tag}"
        self.port_mappings = []  # (host_port, container_port)
        self.environment = {}
        self.volumes = []
        self.network = "bridge"
        self.restart_policy = "no"
        self.name = None

    def add_port_mapping(self, host_port, container_port):
        self.port_mappings.append((host_port, container_port))
        return self

    def add_env(self, key, value):
        self.environment[key] = value
        return self

    def add_volume(self, host_path, container_path):
        self.volumes.append((host_path, container_path))
        return self

    def set_name(self, name):
        self.name = name
        return self

    def get_config(self):
        return {
            "image": self.full_image,
            "name": self.name,
            "ports": self.port_mappings,
            "environment": self.environment,
            "volumes": self.volumes,
            "network": self.network,
            "restart": self.restart_policy
        }

class FlaskAppHandler(BaseHTTPRequestHandler):
    """Simulated Flask app running inside container"""
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        response = {
            "message": "Hello from SovereignGTP Container!",
            "app": "helloworld",
            "environment": "production",
            "timestamp": datetime.now().isoformat()
        }
        self.wfile.write(json.dumps(response, indent=2).encode())

    def log_message(self, format, *args):
        logger.info(f"  [Container] {args[0]}")

class DockerContainer:
    """Represents a running Docker container"""
    def __init__(self, container_id, config):
        self.container_id = container_id
        self.config = config
        self.status = "created"
        self.started_at = None
        self.ports_bound = []
        self.server = None
        self.server_thread = None

    def start(self):
        """Start the container"""
        self.status = "running"
        self.started_at = datetime.now().isoformat()

        # Bind ports
        for host_port, container_port in self.config.port_mappings:
            self.ports_bound.append({
                "host_port": host_port,
                "container_port": container_port,
                "protocol": "tcp"
            })

        # Start simulated Flask app
        if self.config.port_mappings:
            host_port = self.config.port_mappings[0][0]
            self._start_flask_app(host_port)

        logger.info(f"Container started: {self.container_id[:12]}")
        logger.info(f"  Serving Flask app \"app\" (lazy loading)")
        logger.info(f"  Environment: production")
        logger.info(f"  WARNING: Do not use the development server in a production environment.")
        logger.info(f"  Use a production WSGI server instead.")
        logger.info(f"  Debug mode: off")

        return self.get_status()

    def _start_flask_app(self, port):
        """Start simulated Flask app on port"""
        try:
            self.server = HTTPServer(('0.0.0.0', port), FlaskAppHandler)
            self.server_thread = threading.Thread(target=self.server.serve_forever, daemon=True)
            self.server_thread.start()
            logger.info(f"  Running on http://0.0.0.0:{port}/ (Press CTRL+C to quit)")
        except Exception as e:
            logger.error(f"  Failed to start Flask app: {e}")

    def stop(self):
        """Stop the container"""
        if self.server:
            self.server.shutdown()
        self.status = "exited"
        logger.info(f"Container stopped: {self.container_id[:12]}")

    def get_status(self):
        return {
            "container_id": self.container_id,
            "image": self.config.full_image,
            "name": self.config.name,
            "status": self.status,
            "started_at": self.started_at,
            "ports": self.ports_bound,
            "environment": self.config.environment
        }

class DockerRunner:
    """Docker container runner"""
    def __init__(self):
        self.containers = {}
        self.images = {}

    def pull_image(self, image_name, tag="latest"):
        """Pull container image"""
        full_image = f"{image_name}:{tag}"
        self.images[full_image] = {
            "image": full_image,
            "pulled": datetime.now().isoformat(),
            "size_mb": 125
        }
        logger.info(f"Image pulled: {full_image}")
        return self.images[full_image]

    def run(self, image_name, tag="latest", port_mappings=None, environment=None, name=None):
        """Run a container (docker run)"""
        full_image = f"{image_name}:{tag}"

        # Auto-pull if not present
        if full_image not in self.images:
            self.pull_image(image_name, tag)

        # Create config
        config = ContainerConfig(image_name, tag)
        if port_mappings:
            for mapping in port_mappings:
                config.add_port_mapping(mapping[0], mapping[1])
        if environment:
            for key, value in environment.items():
                config.add_env(key, value)
        if name:
            config.set_name(name)

        # Create container
        container_id = f"container_{int(time.time())}_{hash(full_image) % 10000}"
        container = DockerContainer(container_id, config)

        self.containers[container_id] = container

        # Start container
        status = container.start()

        logger.info(f"docker run -p {port_mappings[0][0]}:{port_mappings[0][1]} {full_image}")
        return status

    def list_containers(self):
        """List running containers"""
        return [c.get_status() for c in self.containers.values()]

    def stop_container(self, container_id):
        """Stop a container"""
        if container_id in self.containers:
            self.containers[container_id].stop()
            return True
        return False

    def get_runner_status(self):
        return {
            "total_containers": len(self.containers),
            "running": len([c for c in self.containers.values() if c.status == "running"]),
            "images": len(self.images),
            "containers": [c.get_status() for c in self.containers.values()]
        }

if __name__ == "__main__":
    runner = DockerRunner()

    print("=== DOCKER CONTAINER RUNNER DEMO ===\n")

    # Pull image
    print("1. Pulling image:")
    runner.pull_image("helloworld", "latest")
    print(f"   Image: helloworld:latest\n")

    # Run container (like: docker run -p 4000:80 helloworld)
    print("2. Running container:")
    print("   $ docker run -p 4000:80 helloworld")
    status = runner.run(
        "helloworld",
        tag="latest",
        port_mappings=[(4000, 80)],
        environment={"FLASK_ENV": "production"},
        name="helloworld-container"
    )
    print(f"\n   Container ID: {status['container_id'][:12]}")
    print(f"   Status: {status['status']}")
    print(f"   Ports: {status['ports']}")
    print(f"   Started: {status['started_at']}\n")

    # List containers
    print("3. Listing containers:")
    containers = runner.list_containers()
    for c in containers:
        print(f"   {c['container_id'][:12]}  {c['image']:<20} {c['status']:<10} {c['ports']}")
    print()

    # Run another container with different port
    print("4. Running second container:")
    print("   $ docker run -p 4001:80 videocourts")
    runner.run(
        "videocourts",
        tag="v2.5.0",
        port_mappings=[(4001, 80)],
        environment={"DB_HOST": "localhost", "DB_PORT": "5432"},
        name="videocourts-container"
    )
    print()

    # Runner status
    print("5. Runner status:")
    runner_status = runner.get_runner_status()
    print(f"   Total containers: {runner_status['total_containers']}")
    print(f"   Running: {runner_status['running']}")
    print(f"   Images: {runner_status['images']}\n")

    # Stop container
    print("6. Stopping first container:")
    first_container = list(runner.containers.keys())[0]
    runner.stop_container(first_container)
    print(f"   Container {first_container[:12]} stopped")

    print("\n=== DOCKER RUNNER ARCHITECTURE ===")
    print("docker run -p HOST_PORT:CONTAINER_PORT IMAGE_NAME")
    print("Features: Port mapping, environment variables, container naming")
