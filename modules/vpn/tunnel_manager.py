#!/data/data/com.termux/files/usr/bin/python3
"""
VPN Tunnel Manager
Site-to-site VPN between VPN Gateway and Customer Gateway
Supports IPv4 & IPv6 traffic through encrypted tunnels
"""
import json
import time
import subprocess
import logging
from pathlib import Path
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s [VPN-TUNNEL] %(message)s')
logger = logging.getLogger(__name__)

class VPNTunnel:
    """Represents a single VPN tunnel"""
    def __init__(self, tunnel_id, local_gateway, remote_gateway, shared_secret):
        self.tunnel_id = tunnel_id
        self.local_gateway = local_gateway
        self.remote_gateway = remote_gateway
        self.shared_secret = shared_secret
        self.status = "down"
        self.created = datetime.now().isoformat()
        self.traffic_stats = {"ipv4_packets": 0, "ipv6_packets": 0, "bytes_transferred": 0}
        self.uptime_seconds = 0
        self.last_established = None

    def establish(self):
        """Establish the VPN tunnel"""
        self.status = "establishing"
        logger.info(f"Tunnel {self.tunnel_id}: Establishing connection...")

        # Simulate tunnel establishment
        time.sleep(0.1)  # Simulated handshake

        self.status = "up"
        self.last_established = datetime.now().isoformat()
        logger.info(f"Tunnel {self.tunnel_id}: UP ({self.local_gateway} ↔ {self.remote_gateway})")
        return True

    def teardown(self):
        """Tear down the VPN tunnel"""
        self.status = "down"
        logger.info(f"Tunnel {self.tunnel_id}: DOWN")
        return True

    def send_traffic(self, packet_type="ipv4", size_bytes=1024):
        """Simulate sending traffic through tunnel"""
        if self.status != "up":
            return {"error": "Tunnel is down"}

        if packet_type == "ipv4":
            self.traffic_stats["ipv4_packets"] += 1
        elif packet_type == "ipv6":
            self.traffic_stats["ipv6_packets"] += 1

        self.traffic_stats["bytes_transferred"] += size_bytes
        self.uptime_seconds += 1

        return {
            "tunnel": self.tunnel_id,
            "packet_type": packet_type,
            "size_bytes": size_bytes,
            "status": "delivered"
        }

    def get_status(self):
        return {
            "tunnel_id": self.tunnel_id,
            "status": self.status,
            "local_gateway": self.local_gateway,
            "remote_gateway": self.remote_gateway,
            "created": self.created,
            "last_established": self.last_established,
            "uptime_seconds": self.uptime_seconds,
            "traffic": self.traffic_stats
        }

class VPNGateway:
    """VPN Gateway managing multiple tunnels"""
    def __init__(self, gateway_id, public_ipv4, config_dir=None):
        self.gateway_id = gateway_id
        self.public_ipv4 = public_ipv4
        self.config_dir = config_dir or str(Path.home() / "constellation25" / "config" / "vpn")
        Path(self.config_dir).mkdir(parents=True, exist_ok=True)
        self.tunnels = {}
        self._load_config()

    def _load_config(self):
        config_file = f"{self.config_dir}/{self.gateway_id}.json"
        if Path(config_file).exists():
            with open(config_file, 'r') as f:
                data = json.load(f)
                for tunnel_data in data.get("tunnels", []):
                    tunnel = VPNTunnel(
                        tunnel_data["tunnel_id"],
                        tunnel_data["local_gateway"],
                        tunnel_data["remote_gateway"],
                        tunnel_data["shared_secret"]
                    )
                    tunnel.status = tunnel_data.get("status", "down")
                    self.tunnels[tunnel.tunnel_id] = tunnel

    def _save_config(self):
        config_file = f"{self.config_dir}/{self.gateway_id}.json"
        data = {
            "gateway_id": self.gateway_id,
            "public_ipv4": self.public_ipv4,
            "tunnels": [t.get_status() for t in self.tunnels.values()]
        }
        with open(config_file, 'w') as f:
            json.dump(data, f, indent=2)

    def create_tunnel(self, remote_gateway, shared_secret):
        """Create a new VPN tunnel to customer gateway"""
        tunnel_id = f"tunnel_{len(self.tunnels) + 1}"
        tunnel = VPNTunnel(tunnel_id, self.public_ipv4, remote_gateway, shared_secret)
        self.tunnels[tunnel_id] = tunnel
        self._save_config()

        logger.info(f"Tunnel created: {tunnel_id} ({self.public_ipv4} → {remote_gateway})")
        return tunnel

    def establish_all(self):
        """Establish all configured tunnels"""
        for tunnel in self.tunnels.values():
            tunnel.establish()
        self._save_config()

    def teardown_all(self):
        """Tear down all tunnels"""
        for tunnel in self.tunnels.values():
            tunnel.teardown()
        self._save_config()

    def send_traffic(self, tunnel_id, packet_type="ipv4", size_bytes=1024):
        """Send traffic through specific tunnel"""
        if tunnel_id not in self.tunnels:
            return {"error": f"Tunnel {tunnel_id} not found"}

        return self.tunnels[tunnel_id].send_traffic(packet_type, size_bytes)

    def get_status(self):
        return {
            "gateway_id": self.gateway_id,
            "public_ipv4": self.public_ipv4,
            "tunnels": {tid: t.get_status() for tid, t in self.tunnels.items()},
            "total_tunnels": len(self.tunnels),
            "active_tunnels": len([t for t in self.tunnels.values() if t.status == "up"])
        }

class CustomerGateway:
    """Customer-side VPN gateway"""
    def __init__(self, gateway_id, public_ipv4):
        self.gateway_id = gateway_id
        self.public_ipv4 = public_ipv4
        self.connected_tunnels = []

    def connect_to_vpn_gateway(self, vpn_gateway, shared_secret):
        """Establish connection to VPN gateway"""
        tunnel = vpn_gateway.create_tunnel(self.public_ipv4, shared_secret)
        self.connected_tunnels.append(tunnel.tunnel_id)
        return tunnel

if __name__ == "__main__":
    print("=== VPN TUNNEL MANAGER DEMO ===\n")

    # Create VPN Gateway (sovereign infrastructure)
    vpn_gw = VPNGateway("vpn-gw-01", "203.0.113.10")

    # Create Customer Gateway (client site)
    customer_gw = CustomerGateway("customer-gw-01", "198.51.100.20")

    print("1. Creating VPN tunnels:")
    tunnel1 = customer_gw.connect_to_vpn_gateway(vpn_gw, "super-secret-key-123")
    print(f"   Tunnel 1: {vpn_gw.public_ipv4} ↔ {customer_gw.public_ipv4}")
    print(f"   Status: {tunnel1.status}\n")

    print("2. Establishing tunnels:")
    vpn_gw.establish_all()
    print(f"   Active tunnels: {vpn_gw.get_status()['active_tunnels']}\n")

    print("3. Sending traffic:")
    result = vpn_gw.send_traffic("tunnel_1", "ipv4", 2048)
    print(f"   IPv4 packet: {result}")

    result = vpn_gw.send_traffic("tunnel_1", "ipv6", 4096)
    print(f"   IPv6 packet: {result}\n")

    print("4. Tunnel status:")
    print(json.dumps(vpn_gw.get_status(), indent=2))

    print("\n5. Tearing down:")
    vpn_gw.teardown_all()
    print(f"   Active tunnels: {vpn_gw.get_status()['active_tunnels']}")

    print("\n=== VPN ARCHITECTURE ===")
    print("VPN Gateway (Public IPv4) ←→ Tunnel 1 (IPv4 & IPv6 traffic) ←→ Customer Gateway (Public IPv4)")
