#!/data/data/com.termux/files/usr/bin/python3
"""
Server Management Dashboard
Online.net-style server management with Server list, IP Failover, Network configuration, DDoS alerts
Based on Online.net dashboard diagram
"""
import json
import time
import random
import logging
from pathlib import Path
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO, format='%(asctime)s [SERVER-MGMT] %(message)s')
logger = logging.getLogger(__name__)

class Server:
    """Represents a server instance"""
    def __init__(self, server_id, name, server_type):
        self.server_id = server_id
        self.name = name
        self.server_type = server_type
        self.status = "online"
        self.public_ip = f"51.159.{random.randint(1, 255)}.{random.randint(1, 255)}"
        self.private_ip = f"10.10.{random.randint(1, 255)}.{random.randint(1, 255)}"
        self.created = datetime.now().isoformat()
        self.uptime_hours = random.randint(100, 1000)
        self.cpu_usage = random.uniform(10, 80)
        self.memory_usage = random.uniform(30, 70)
        self.disk_usage = random.uniform(20, 60)
        self.bandwidth_used_gb = random.uniform(100, 1000)
        self.failover_ips = []
        self.ddos_alerts = []
        self.network_config = {
            "mtu": 1500,
            "dns_servers": ["8.8.8.8", "8.8.4.4"],
            "firewall_rules": []
        }

    def add_failover_ip(self, ip_address):
        """Add IP failover"""
        failover = {
            "ip": ip_address,
            "status": "active",
            "added_at": datetime.now().isoformat()
        }
        self.failover_ips.append(failover)
        logger.info(f"Failover IP added: {ip_address}")
        return failover

    def add_ddos_alert(self, alert_type, severity):
        """Add DDoS alert"""
        alert = {
            "type": alert_type,
            "severity": severity,
            "detected_at": datetime.now().isoformat(),
            "status": "active",
            "mitigation": "auto"
        }
        self.ddos_alerts.append(alert)
        logger.warning(f"DDoS alert: {alert_type} ({severity})")
        return alert

    def configure_network(self, mtu=None, dns_servers=None):
        """Configure network settings"""
        if mtu:
            self.network_config["mtu"] = mtu
        if dns_servers:
            self.network_config["dns_servers"] = dns_servers
        logger.info(f"Network configured for {self.name}")

    def add_firewall_rule(self, rule):
        """Add firewall rule"""
        self.network_config["firewall_rules"].append(rule)
        logger.info(f"Firewall rule added: {rule}")

    def get_server_info(self):
        return {
            "server_id": self.server_id,
            "name": self.name,
            "type": self.server_type,
            "status": self.status,
            "public_ip": self.public_ip,
            "private_ip": self.private_ip,
            "uptime_hours": self.uptime_hours,
            "cpu_usage": f"{self.cpu_usage:.1f}%",
            "memory_usage": f"{self.memory_usage:.1f}%",
            "disk_usage": f"{self.disk_usage:.1f}%",
            "bandwidth_gb": round(self.bandwidth_used_gb, 2),
            "failover_ips": len(self.failover_ips),
            "ddos_alerts": len(self.ddos_alerts)
        }

class ServerManagementDashboard:
    """Server management dashboard"""
    def __init__(self):
        self.servers = {}
        self.created = datetime.now().isoformat()

    def add_server(self, name, server_type):
        """Add a server"""
        server_id = f"srv_{int(time.time())}_{random.randint(1000, 9999)}"
        server = Server(server_id, name, server_type)
        self.servers[server_id] = server
        logger.info(f"Server added: {name}")
        return server

    def get_server_list(self):
        """Get server list"""
        return [s.get_server_info() for s in self.servers.values()]

    def get_ip_failover(self, server_id):
        """Get IP failover configuration"""
        if server_id not in self.servers:
            return {"error": "Server not found"}

        server = self.servers[server_id]
        return {
            "server": server.name,
            "public_ip": server.public_ip,
            "failover_ips": server.failover_ips
        }

    def get_network_config(self, server_id):
        """Get network configuration"""
        if server_id not in self.servers:
            return {"error": "Server not found"}

        server = self.servers[server_id]
        return {
            "server": server.name,
            "network": server.network_config
        }

    def get_ddos_alerts(self, server_id):
        """Get DDoS alerts"""
        if server_id not in self.servers:
            return {"error": "Server not found"}

        server = self.servers[server_id]
        return {
            "server": server.name,
            "alerts": server.ddos_alerts,
            "total_alerts": len(server.ddos_alerts)
        }

    def get_dashboard_status(self):
        return {
            "total_servers": len(self.servers),
            "online_servers": len([s for s in self.servers.values() if s.status == "online"]),
            "servers": self.get_server_list()
        }

if __name__ == "__main__":
    dashboard = ServerManagementDashboard()

    print("=== SERVER MANAGEMENT DASHBOARD DEMO ===\n")

    # Add servers
    print("1. Server list:")
    server1 = dashboard.add_server("Production Web", "GP1-S")
    server2 = dashboard.add_server("Database Server", "GP1-M")
    server3 = dashboard.add_server("Backup Server", "DEV1-L")

    servers = dashboard.get_server_list()
    for s in servers:
        print(f"   {s['name']}:")
        print(f"     Type: {s['type']}")
        print(f"     IP: {s['public_ip']}")
        print(f"     Status: {s['status']}")
        print(f"     CPU: {s['cpu_usage']}, Memory: {s['memory_usage']}")
    print()

    # IP Failover
    print("2. IP Failover:")
    server1.add_failover_ip("51.159.100.1")
    server1.add_failover_ip("51.159.100.2")
    failover = dashboard.get_ip_failover(server1.server_id)
    print(f"   Server: {failover['server']}")
    print(f"   Public IP: {failover['public_ip']}")
    print(f"   Failover IPs: {len(failover['failover_ips'])}")
    for ip in failover['failover_ips']:
        print(f"     - {ip['ip']} ({ip['status']})")
    print()

    # Network configuration
    print("3. Network configuration:")
    server1.configure_network(mtu=9000, dns_servers=["1.1.1.1", "8.8.8.8"])
    server1.add_firewall_rule({"port": 80, "protocol": "TCP", "action": "ALLOW"})
    server1.add_firewall_rule({"port": 443, "protocol": "TCP", "action": "ALLOW"})
    server1.add_firewall_rule({"port": 22, "protocol": "TCP", "action": "ALLOW", "source": "10.0.0.0/8"})

    network = dashboard.get_network_config(server1.server_id)
    print(f"   Server: {network['server']}")
    print(f"   MTU: {network['network']['mtu']}")
    print(f"   DNS: {', '.join(network['network']['dns_servers'])}")
    print(f"   Firewall rules: {len(network['network']['firewall_rules'])}")
    for rule in network['network']['firewall_rules']:
        print(f"     - {rule['port']}/{rule['protocol']} {rule['action']}")
    print()

    # DDoS alerts
    print("4. DDoS alerts:")
    server1.add_ddos_alert("SYN Flood", "high")
    server2.add_ddos_alert("UDP Amplification", "medium")

    for server in [server1, server2]:
        alerts = dashboard.get_ddos_alerts(server.server_id)
        print(f"   {alerts['server']}: {alerts['total_alerts']} alerts")
        for alert in alerts['alerts']:
            print(f"     - {alert['type']} ({alert['severity']}) at {alert['detected_at']}")
    print()

    # Dashboard status
    print("5. Dashboard status:")
    status = dashboard.get_dashboard_status()
    print(f"   Total servers: {status['total_servers']}")
    print(f"   Online: {status['online_servers']}")

    print("\n=== SERVER MANAGEMENT ARCHITECTURE ===")
    print("Server → Server list | IP Failover | Network configuration | DDoS alerts")
    print("Features: Multi-server management, failover IPs, firewall rules, DDoS protection")
