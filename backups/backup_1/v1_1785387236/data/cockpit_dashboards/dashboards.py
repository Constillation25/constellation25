#!/data/data/com.termux/files/usr/bin/python3
"""
Cockpit Dashboards
Grafana-style managed dashboards with explore functionality
General / Cockpit Dashboards Home → Managed Dashboards → Explore
Based on Cockpit Dashboards diagram
"""
import json
import time
import random
import logging
from pathlib import Path
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO, format='%(asctime)s [COCKPIT] %(message)s')
logger = logging.getLogger(__name__)

class DashboardPanel:
    """A single panel/widget in a dashboard"""
    def __init__(self, panel_id, title, panel_type):
        self.panel_id = panel_id
        self.title = title
        self.panel_type = panel_type  # graph, stat, table, gauge
        self.data_source = None
        self.query = ""
        self.refresh_interval = 30  # seconds
        self.created = datetime.now().isoformat()

    def configure(self, data_source, query):
        """Configure panel data source and query"""
        self.data_source = data_source
        self.query = query
        logger.info(f"Panel configured: {self.title} ({data_source})")

    def get_data(self):
        """Simulate getting panel data"""
        if self.panel_type == "graph":
            # Generate time series data
            data = []
            now = datetime.now()
            for i in range(60):
                timestamp = (now - timedelta(minutes=i)).isoformat()
                value = random.uniform(0, 100)
                data.append({"timestamp": timestamp, "value": round(value, 2)})
            return data
        elif self.panel_type == "stat":
            return {"value": round(random.uniform(0, 100), 2), "unit": "%"}
        elif self.panel_type == "table":
            return {
                "columns": ["Time", "Service", "Status", "Latency"],
                "rows": [
                    [datetime.now().isoformat(), "Service-A", "healthy", f"{random.uniform(10, 100):.0f}ms"],
                    [datetime.now().isoformat(), "Service-B", "healthy", f"{random.uniform(10, 100):.0f}ms"],
                    [datetime.now().isoformat(), "Service-C", "warning", f"{random.uniform(100, 500):.0f}ms"]
                ]
            }
        return {}

    def get_panel_info(self):
        return {
            "panel_id": self.panel_id,
            "title": self.title,
            "type": self.panel_type,
            "data_source": self.data_source,
            "refresh_interval": self.refresh_interval
        }

class Dashboard:
    """A complete dashboard with multiple panels"""
    def __init__(self, dashboard_id, title):
        self.dashboard_id = dashboard_id
        self.title = title
        self.panels = {}
        self.created = datetime.now().isoformat()
        self.last_refreshed = None
        self.is_starred = False
        self.tags = []

    def add_panel(self, panel):
        """Add a panel to dashboard"""
        self.panels[panel.panel_id] = panel
        logger.info(f"Panel added to {self.title}: {panel.title}")

    def refresh(self):
        """Refresh all panels"""
        self.last_refreshed = datetime.now().isoformat()
        logger.info(f"Dashboard refreshed: {self.title}")

    def toggle_star(self):
        """Toggle starred status"""
        self.is_starred = not self.is_starred
        logger.info(f"Dashboard {'starred' if self.is_starred else 'unstarred'}: {self.title}")

    def get_dashboard_info(self):
        return {
            "dashboard_id": self.dashboard_id,
            "title": self.title,
            "panels": len(self.panels),
            "panel_list": [p.get_panel_info() for p in self.panels.values()],
            "created": self.created,
            "last_refreshed": self.last_refreshed,
            "is_starred": self.is_starred,
            "tags": self.tags
        }

class CockpitDashboards:
    """Cockpit Dashboards manager"""
    def __init__(self):
        self.dashboards = {}
        self.managed_dashboards = []
        self.explore_queries = []

    def create_dashboard(self, title):
        """Create a new dashboard"""
        dashboard_id = f"dash_{int(time.time())}"
        dashboard = Dashboard(dashboard_id, title)
        self.dashboards[dashboard_id] = dashboard
        self.managed_dashboards.append(dashboard_id)
        logger.info(f"Dashboard created: {title}")
        return dashboard

    def add_panel_to_dashboard(self, dashboard_id, panel):
        """Add panel to dashboard"""
        if dashboard_id not in self.dashboards:
            return {"error": "Dashboard not found"}

        self.dashboards[dashboard_id].add_panel(panel)
        return panel.get_panel_info()

    def explore(self, query, data_source="prometheus"):
        """Explore data with custom query"""
        result = {
            "query": query,
            "data_source": data_source,
            "executed_at": datetime.now().isoformat(),
            "results": []
        }

        # Simulate query execution
        for i in range(10):
            result["results"].append({
                "timestamp": (datetime.now() - timedelta(seconds=i*10)).isoformat(),
                "value": round(random.uniform(0, 100), 2)
            })

        self.explore_queries.append(result)
        logger.info(f"Explore query executed: {query}")
        return result

    def get_dashboards_home(self):
        """Get Cockpit Dashboards Home"""
        return {
            "title": "Cockpit Dashboards Home",
            "path": "General / Cockpit Dashboards Home",
            "managed_dashboards": len(self.managed_dashboards),
            "dashboards": [self.dashboards[did].get_dashboard_info() for did in self.managed_dashboards]
        }

if __name__ == "__main__":
    cockpit = CockpitDashboards()

    print("=== COCKPIT DASHBOARDS DEMO ===\n")

    # Create dashboards
    print("1. Creating dashboards:")
    dash1 = cockpit.create_dashboard("System Overview")
    dash2 = cockpit.create_dashboard("Application Metrics")
    print(f"   Dashboards created: {len(cockpit.managed_dashboards)}\n")

    # Add panels
    print("2. Adding panels to System Overview:")
    panel1 = DashboardPanel("p1", "CPU Usage", "graph")
    panel1.configure("prometheus", "rate(cpu_usage_total[5m])")
    cockpit.add_panel_to_dashboard(dash1.dashboard_id, panel1)

    panel2 = DashboardPanel("p2", "Memory Usage", "gauge")
    panel2.configure("prometheus", "memory_usage_bytes / memory_total_bytes")
    cockpit.add_panel_to_dashboard(dash1.dashboard_id, panel2)

    panel3 = DashboardPanel("p3", "Service Status", "table")
    panel3.configure("prometheus", "service_health_status")
    cockpit.add_panel_to_dashboard(dash1.dashboard_id, panel3)

    print(f"   Panels added: {len(dash1.panels)}")
    for p in dash1.panels.values():
        print(f"     - {p.title} ({p.panel_type})")
    print()

    # Refresh dashboard
    print("3. Refreshing dashboard:")
    dash1.refresh()
    print(f"   Last refreshed: {dash1.last_refreshed}\n")

    # Star dashboard
    print("4. Starring dashboard:")
    dash1.toggle_star()
    print(f"   Starred: {dash1.is_starred}\n")

    # Explore data
    print("5. Exploring data:")
    result = cockpit.explore("rate(http_requests_total[5m])", "prometheus")
    print(f"   Query: {result['query']}")
    print(f"   Data source: {result['data_source']}")
    print(f"   Results: {len(result['results'])} data points\n")

    # Dashboards home
    print("6. Cockpit Dashboards Home:")
    home = cockpit.get_dashboards_home()
    print(f"   Path: {home['path']}")
    print(f"   Managed dashboards: {home['managed_dashboards']}")
    for dash_info in home['dashboards']:
        star = "★" if dash_info['is_starred'] else "☆"
        print(f"     {star} {dash_info['title']} ({dash_info['panels']} panels)")

    print("\n=== COCKPIT DASHBOARDS ARCHITECTURE ===")
    print("General / Cockpit Dashboards Home → Managed Dashboards → Explore")
    print("Features: Panels (graph, stat, table, gauge), Refresh, Star, Explore")
