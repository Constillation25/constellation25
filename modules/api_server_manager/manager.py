#!/data/data/com.termux/files/usr/bin/python3
"""
API Server Manager
Manages server instances via REST API
POST {{baseUrl}}/instance/v1/zones/fr-par-1/servers
Based on API endpoint diagram
"""
import json
import time
import uuid
import logging
from pathlib import Path
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

logging.basicConfig(level=logging.INFO, format='%(asctime)s [API-SERVER] %(message)s')
logger = logging.getLogger(__name__)

class ServerInstance:
    """Represents a server instance"""
    def __init__(self, server_id, name, zone, image, server_type):
        self.server_id = server_id
        self.name = name
        self.zone = zone  # e.g., fr-par-1
        self.image = image
        self.server_type = server_type
        self.state = "starting"
        self.created_at = datetime.now().isoformat()
        self.modified_at = None
        self.public_ip = None
        self.private_ip = f"10.10.{uuid.uuid4().int % 256}.{uuid.uuid4().int % 256}"
        self.tags = []
        self.volumes = {}

    def start(self):
        """Start the server"""
        self.state = "running"
        self.modified_at = datetime.now().isoformat()
        self.public_ip = f"51.159.{uuid.uuid4().int % 256}.{uuid.uuid4().int % 256}"
        logger.info(f"Server started: {self.name} ({self.public_ip})")

    def stop(self):
        """Stop the server"""
        self.state = "stopped"
        self.modified_at = datetime.now().isoformat()
        logger.info(f"Server stopped: {self.name}")

    def reboot(self):
        """Reboot the server"""
        self.state = "rebooting"
        time.sleep(0.1)  # Simulate reboot
        self.state = "running"
        self.modified_at = datetime.now().isoformat()
        logger.info(f"Server rebooted: {self.name}")

    def get_info(self):
        return {
            "id": self.server_id,
            "name": self.name,
            "zone": self.zone,
            "image": self.image,
            "server_type": self.server_type,
            "state": self.state,
            "public_ip": self.public_ip,
            "private_ip": self.private_ip,
            "created_at": self.created_at,
            "modified_at": self.modified_at,
            "tags": self.tags,
            "volumes": self.volumes
        }

class APIServerManager:
    """API server manager (like Scaleway Instance API)"""
    def __init__(self, base_url="https://api.scaleway.com"):
        self.base_url = base_url
        self.servers = {}
        self.zones = ["fr-par-1", "fr-par-2", "fr-par-3", "nl-ams-1", "pl-waw-1"]
        self.images = ["Ubuntu 22.04", "Debian 11", "CentOS 8", "Alpine 3.16"]
        self.server_types = ["DEV1-S", "DEV1-M", "DEV1-L", "GP1-S", "GP1-M"]

    def create_server(self, name, zone, image, server_type, tags=None):
        """Create a new server instance"""
        if zone not in self.zones:
            return {"error": f"Invalid zone: {zone}. Available: {self.zones}"}

        server_id = str(uuid.uuid4())
        server = ServerInstance(server_id, name, zone, image, server_type)

        if tags:
            server.tags = tags

        # Add default volume
        server.volumes["0"] = {
            "id": str(uuid.uuid4()),
            "name": f"{name}-volume",
            "size": 20 * 1024 * 1024 * 1024,  # 20GB
            "volume_type": "l_ssd"
        }

        self.servers[server_id] = server
        server.start()

        logger.info(f"Server created: {name} in {zone}")
        return server.get_info()

    def list_servers(self, zone=None):
        """List all servers, optionally filtered by zone"""
        servers = list(self.servers.values())
        if zone:
            servers = [s for s in servers if s.zone == zone]
        return [s.get_info() for s in servers]

    def get_server(self, server_id):
        """Get server by ID"""
        if server_id not in self.servers:
            return {"error": f"Server {server_id} not found"}
        return self.servers[server_id].get_info()

    def delete_server(self, server_id):
        """Delete a server"""
        if server_id not in self.servers:
            return {"error": f"Server {server_id} not found"}

        server = self.servers[server_id]
        server.stop()
        del self.servers[server_id]
        logger.info(f"Server deleted: {server.name}")
        return {"status": "deleted", "server_id": server_id}

    def server_action(self, server_id, action):
        """Perform action on server (start, stop, reboot)"""
        if server_id not in self.servers:
            return {"error": f"Server {server_id} not found"}

        server = self.servers[server_id]

        if action == "start":
            server.start()
        elif action == "stop":
            server.stop()
        elif action == "reboot":
            server.reboot()
        else:
            return {"error": f"Unknown action: {action}"}

        return {"status": action, "server_id": server_id, "state": server.state}

    def get_api_status(self):
        return {
            "base_url": self.base_url,
            "total_servers": len(self.servers),
            "running_servers": len([s for s in self.servers.values() if s.state == "running"]),
            "zones": self.zones,
            "available_images": self.images,
            "available_types": self.server_types
        }

class APIServer:
    """HTTP API server for managing instances"""
    def __init__(self, manager, port=8080):
        self.manager = manager
        self.port = port
        self.server = None

    class RequestHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            parsed = urlparse(self.path)
            path = parsed.path

            if path == "/instance/v1/zones":
                # List zones
                zones = self.server.manager.zones
                self.send_json({"zones": zones})

            elif path.startswith("/instance/v1/zones/"):
                # Parse zone and resource
                parts = path.split("/")
                if len(parts) >= 6 and parts[5] == "servers":
                    zone = parts[4]
                    servers = self.server.manager.list_servers(zone)
                    self.send_json({"servers": servers})
                else:
                    self.send_error(404, "Not found")
            else:
                self.send_error(404, "Not found")

        def do_POST(self):
            parsed = urlparse(self.path)
            path = parsed.path

            # POST /instance/v1/zones/fr-par-1/servers
            if path.startswith("/instance/v1/zones/") and path.endswith("/servers"):
                parts = path.split("/")
                zone = parts[4]

                # Read request body
                content_length = int(self.headers.get('Content-Length', 0))
                body = self.rfile.read(content_length).decode('utf-8')
                data = json.loads(body) if body else {}

                # Create server
                result = self.server.manager.create_server(
                    name=data.get("name", f"server-{int(time.time())}"),
                    zone=zone,
                    image=data.get("image", "Ubuntu 22.04"),
                    server_type=data.get("server_type", "DEV1-S"),
                    tags=data.get("tags", [])
                )

                self.send_json(result, status=201)
            else:
                self.send_error(404, "Not found")

        def do_DELETE(self):
            parsed = urlparse(self.path)
            path = parsed.path

            # DELETE /instance/v1/zones/fr-par-1/servers/{server_id}
            if "/servers/" in path:
                server_id = path.split("/servers/")[-1]
                result = self.server.manager.delete_server(server_id)
                self.send_json(result)
            else:
                self.send_error(404, "Not found")

        def send_json(self, data, status=200):
            self.send_response(status)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(data, indent=2).encode())

        def log_message(self, format, *args):
            logger.info(f"API: {args[0]}")

    def start(self):
        """Start API server"""
        self.server = HTTPServer(('0.0.0.0', self.port), self.RequestHandler)
        self.server.manager = self.manager
        logger.info(f"API server started on port {self.port}")
        self.server.serve_forever()

if __name__ == "__main__":
    manager = APIServerManager("https://api.scaleway.com")

    print("=== API SERVER MANAGER DEMO ===\n")

    # Create servers
    print("1. Creating servers via API:")
    print("   POST /instance/v1/zones/fr-par-1/servers")

    server1 = manager.create_server(
        name="videocourts-prod",
        zone="fr-par-1",
        image="Ubuntu 22.04",
        server_type="GP1-S",
        tags=["production", "videocourts"]
    )
    print(f"\n   Server 1: {server1['name']}")
    print(f"   ID: {server1['id'][:8]}...")
    print(f"   Zone: {server1['zone']}")
    print(f"   IP: {server1['public_ip']}")
    print(f"   State: {server1['state']}")

    server2 = manager.create_server(
        name="mybuyo-api",
        zone="fr-par-2",
        image="Debian 11",
        server_type="DEV1-M",
        tags=["api", "mybuyo"]
    )
    print(f"\n   Server 2: {server2['name']}")
    print(f"   Zone: {server2['zone']}")
    print(f"   IP: {server2['public_ip']}")

    # List servers
    print("\n2. Listing servers:")
    print("   GET /instance/v1/zones/fr-par-1/servers")
    servers = manager.list_servers()
    for s in servers:
        print(f"   - {s['name']} ({s['zone']}): {s['public_ip']} [{s['state']}]")

    # Server action
    print("\n3. Server action:")
    print("   POST /instance/v1/zones/fr-par-1/servers/{id}/action")
    result = manager.server_action(server1['id'], "reboot")
    print(f"   Action: {result['status']}")
    print(f"   State: {result['state']}")

    # API status
    print("\n4. API status:")
    status = manager.get_api_status()
    print(f"   Base URL: {status['base_url']}")
    print(f"   Total servers: {status['total_servers']}")
    print(f"   Running: {status['running_servers']}")
    print(f"   Available zones: {', '.join(status['zones'][:3])}...")

    print("\n=== API SERVER MANAGER ARCHITECTURE ===")
    print("POST {{baseUrl}}/instance/v1/zones/fr-par-1/servers")
    print("Create, list, manage server instances via REST API")
