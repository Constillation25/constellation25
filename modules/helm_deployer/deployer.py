#!/data/data/com.termux/files/usr/bin/python3
"""
Helm Chart Deployer
Helm chart (templates) + values.yaml (configurations) → Helm → Create/Update resources → Kubernetes Cluster
Based on Helm deployment flow diagram
"""
import json
import time
import yaml
import logging
from pathlib import Path
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s [HELM] %(message)s')
logger = logging.getLogger(__name__)

class HelmChart:
    """Helm chart containing templates"""
    def __init__(self, chart_name, version="1.0.0"):
        self.chart_name = chart_name
        self.version = version
        self.templates = {}
        self.created = datetime.now().isoformat()
        self.description = ""

    def add_template(self, template_name, template_content):
        """Add a Kubernetes resource template"""
        self.templates[template_name] = template_content
        logger.info(f"Template added: {template_name}")

    def get_chart_info(self):
        return {
            "name": self.chart_name,
            "version": self.version,
            "templates": len(self.templates),
            "template_list": list(self.templates.keys()),
            "created": self.created
        }

class ValuesYaml:
    """values.yaml configuration file"""
    def __init__(self):
        self.values = {}

    def set(self, key, value):
        """Set a configuration value"""
        self.values[key] = value
        logger.info(f"Value set: {key} = {value}")

    def get(self, key, default=None):
        """Get a configuration value"""
        return self.values.get(key, default)

    def get_all(self):
        return self.values

    def to_yaml(self):
        return yaml.dump(self.values, default_flow_style=False)

class HelmRelease:
    """A Helm release (deployed instance of a chart)"""
    def __init__(self, release_name, chart, values):
        self.release_name = release_name
        self.chart = chart
        self.values = values
        self.status = "pending"
        self.revision = 1
        self.created = datetime.now().isoformat()
        self.updated = None
        self.resources = []
        self.namespace = "default"

    def install(self, namespace="default"):
        """Install the release (helm install)"""
        self.namespace = namespace
        self.status = "deployed"
        self.created = datetime.now().isoformat()

        # Render templates with values
        self.resources = self._render_templates()

        logger.info(f"Release installed: {self.release_name} (revision {self.revision})")
        return self.get_release_info()

    def upgrade(self, new_values=None):
        """Upgrade the release (helm upgrade)"""
        if new_values:
            self.values.values.update(new_values)

        self.revision += 1
        self.updated = datetime.now().isoformat()
        self.resources = self._render_templates()

        logger.info(f"Release upgraded: {self.release_name} (revision {self.revision})")
        return self.get_release_info()

    def _render_templates(self):
        """Render templates with values (simplified)"""
        resources = []
        for template_name, template_content in self.chart.templates.items():
            # Simple template rendering (replace {{ .Values.xxx }})
            rendered = template_content
            for key, value in self.values.get_all().items():
                placeholder = "{{ .Values." + key + " }}"
                rendered = rendered.replace(placeholder, str(value))

            resources.append({
                "name": template_name,
                "content": rendered,
                "namespace": self.namespace
            })

        return resources

    def get_release_info(self):
        return {
            "release_name": self.release_name,
            "chart": f"{self.chart.chart_name}-{self.chart.version}",
            "namespace": self.namespace,
            "status": self.status,
            "revision": self.revision,
            "resources": len(self.resources),
            "created": self.created,
            "updated": self.updated
        }

class HelmDeployer:
    """Main Helm deployer"""
    def __init__(self):
        self.charts = {}
        self.releases = {}

    def create_chart(self, chart_name, version="1.0.0"):
        """Create a new Helm chart"""
        chart = HelmChart(chart_name, version)
        self.charts[chart_name] = chart
        logger.info(f"Chart created: {chart_name}")
        return chart

    def create_values(self, values_dict=None):
        """Create values.yaml"""
        values = ValuesYaml()
        if values_dict:
            for key, value in values_dict.items():
                values.set(key, value)
        return values

    def install_release(self, release_name, chart_name, values, namespace="default"):
        """Install a Helm release"""
        if chart_name not in self.charts:
            return {"error": f"Chart {chart_name} not found"}

        chart = self.charts[chart_name]
        release = HelmRelease(release_name, chart, values)
        result = release.install(namespace)

        self.releases[release_name] = release
        return result

    def upgrade_release(self, release_name, new_values=None):
        """Upgrade a Helm release"""
        if release_name not in self.releases:
            return {"error": f"Release {release_name} not found"}

        release = self.releases[release_name]
        return release.upgrade(new_values)

    def list_releases(self):
        """List all releases"""
        return [r.get_release_info() for r in self.releases.values()]

    def get_deployer_status(self):
        return {
            "charts": len(self.charts),
            "releases": len(self.releases),
            "chart_details": {name: chart.get_chart_info() for name, chart in self.charts.items()},
            "release_details": [r.get_release_info() for r in self.releases.values()]
        }

if __name__ == "__main__":
    deployer = HelmDeployer()

    print("=== HELM CHART DEPLOYER DEMO ===\n")

    # Create Helm chart (templates)
    print("1. Creating Helm chart (templates):")
    chart = deployer.create_chart("sovereigngtp", "2.5.0")

    # Add Kubernetes resource templates
    deployment_template = """apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ .Values.app_name }}
  namespace: {{ .Values.namespace }}
spec:
  replicas: {{ .Values.replica_count }}
  selector:
    matchLabels:
      app: {{ .Values.app_name }}
  template:
    metadata:
      labels:
        app: {{ .Values.app_name }}
    spec:
      containers:
      - name: {{ .Values.app_name }}
        image: {{ .Values.image }}
        ports:
        - containerPort: {{ .Values.container_port }}"""

    service_template = """apiVersion: v1
kind: Service
metadata:
  name: {{ .Values.app_name }}-svc
  namespace: {{ .Values.namespace }}
spec:
  selector:
    app: {{ .Values.app_name }}
  ports:
  - port: {{ .Values.service_port }}
    targetPort: {{ .Values.container_port }}"""

    chart.add_template("deployment.yaml", deployment_template)
    chart.add_template("service.yaml", service_template)
    print(f"   Chart: {chart.chart_name} v{chart.version}")
    print(f"   Templates: {len(chart.templates)}\n")

    # Create values.yaml (configurations)
    print("2. Creating values.yaml (configurations):")
    values = deployer.create_values({
        "app_name": "videocourts",
        "namespace": "production",
        "replica_count": 3,
        "image": "rg.fr-par.scw.cloud/videocourts:latest",
        "container_port": 8080,
        "service_port": 80
    })
    print("   values.yaml:")
    print(values.to_yaml())

    # Install release (helm install)
    print("3. Installing Helm release:")
    print("   $ helm install videocourts-release sovereigngtp -f values.yaml")
    result = deployer.install_release("videocourts-release", "sovereigngtp", values, namespace="production")
    print(f"\n   Release: {result['release_name']}")
    print(f"   Chart: {result['chart']}")
    print(f"   Namespace: {result['namespace']}")
    print(f"   Status: {result['status']}")
    print(f"   Revision: {result['revision']}")
    print(f"   Resources created: {result['resources']}\n")

    # Upgrade release (helm upgrade)
    print("4. Upgrading Helm release:")
    print("   $ helm upgrade videocourts-release sovereigngtp -f values.yaml --set replica_count=5")
    upgrade_result = deployer.upgrade_release("videocourts-release", {"replica_count": 5})
    print(f"\n   Release: {upgrade_result['release_name']}")
    print(f"   Status: {upgrade_result['status']}")
    print(f"   Revision: {upgrade_result['revision']} (upgraded from 1)")
    print(f"   Resources updated: {upgrade_result['resources']}\n")

    # List releases
    print("5. Listing releases:")
    releases = deployer.list_releases()
    for r in releases:
        print(f"   {r['release_name']:<25} {r['chart']:<20} {r['status']:<10} revision {r['revision']}")
    print()

    # Deployer status
    print("6. Deployer status:")
    status = deployer.get_deployer_status()
    print(f"   Charts: {status['charts']}")
    print(f"   Releases: {status['releases']}")

    print("\n=== HELM DEPLOYER ARCHITECTURE ===")
    print("Helm chart (templates) + values.yaml (configurations) → Helm → Create/Update resources → Kubernetes Cluster")
    print("Commands: helm install, helm upgrade, helm list")
