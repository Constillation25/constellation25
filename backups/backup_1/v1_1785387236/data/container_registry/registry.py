#!/data/data/com.termux/files/usr/bin/python3
"""
Container Registry Manager
Manages container images in registry namespaces (like Scaleway Container Registry)
Registry namespace → Container → Tag selection for deployment
Based on "Select the container to deploy from Container Registry" diagram
"""
import json
import time
import hashlib
import logging
from pathlib import Path
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s [REGISTRY] %(message)s')
logger = logging.getLogger(__name__)

class ContainerImage:
    """Represents a container image with tags"""
    def __init__(self, name, namespace):
        self.name = name
        self.namespace = namespace
        self.tags = {}
        self.created = datetime.now().isoformat()
        self.is_public = False
        self.pull_count = 0
        self.size_bytes = 0

    def add_tag(self, tag_name, image_digest=None):
        """Add a tag to this container image"""
        if not image_digest:
            image_digest = f"sha256:{hashlib.sha256(f'{self.name}:{tag_name}:{time.time()}'.encode()).hexdigest()}"

        self.tags[tag_name] = {
            "tag": tag_name,
            "digest": image_digest,
            "created": datetime.now().isoformat(),
            "size_bytes": self.size_bytes,
            "pull_count": 0
        }
        logger.info(f"Tag added: {self.name}:{tag_name}")
        return self.tags[tag_name]

    def get_tag(self, tag_name):
        """Get specific tag info"""
        return self.tags.get(tag_name)

    def list_tags(self):
        """List all tags"""
        return list(self.tags.keys())

    def pull(self, tag_name="latest"):
        """Simulate pulling image"""
        if tag_name not in self.tags:
            return {"error": f"Tag {tag_name} not found"}

        self.tags[tag_name]["pull_count"] += 1
        self.pull_count += 1
        logger.info(f"Pulled: {self.name}:{tag_name}")
        return self.tags[tag_name]

    def set_public(self, is_public):
        """Set container visibility"""
        self.is_public = is_public
        logger.info(f"{self.name} is now {'public' if is_public else 'private'}")

    def get_info(self):
        return {
            "name": self.name,
            "namespace": self.namespace,
            "tags": list(self.tags.keys()),
            "is_public": self.is_public,
            "pull_count": self.pull_count,
            "created": self.created
        }

class RegistryNamespace:
    """Registry namespace containing multiple containers"""
    def __init__(self, namespace_id, endpoint):
        self.namespace_id = namespace_id
        self.endpoint = endpoint  # e.g., rg.fr-par.scw.cloud/odoo-tutorial-namespace
        self.containers = {}
        self.created = datetime.now().isoformat()

    def create_container(self, name, is_public=False):
        """Create a new container in this namespace"""
        container = ContainerImage(name, self.namespace_id)
        container.set_public(is_public)
        self.containers[name] = container
        logger.info(f"Container created: {name} in {self.namespace_id}")
        return container

    def get_container(self, name):
        """Get container by name"""
        return self.containers.get(name)

    def list_containers(self):
        """List all containers in namespace"""
        return [c.get_info() for c in self.containers.values()]

    def get_namespace_info(self):
        return {
            "namespace_id": self.namespace_id,
            "endpoint": self.endpoint,
            "containers": len(self.containers),
            "container_list": self.list_containers()
        }

class ContainerRegistry:
    """Main container registry managing multiple namespaces"""
    def __init__(self, registry_endpoint="rg.fr-par.scw.cloud"):
        self.registry_endpoint = registry_endpoint
        self.namespaces = {}

    def create_namespace(self, namespace_name):
        """Create a new registry namespace"""
        namespace_id = namespace_name
        endpoint = f"{self.registry_endpoint}/{namespace_name}"
        namespace = RegistryNamespace(namespace_id, endpoint)
        self.namespaces[namespace_id] = namespace
        logger.info(f"Namespace created: {namespace_id}")
        return namespace

    def get_namespace(self, namespace_id):
        """Get namespace by ID"""
        return self.namespaces.get(namespace_id)

    def select_container_for_deployment(self, namespace_id, container_name, tag="latest"):
        """
        Select container for deployment (like the UI diagram)
        Returns deployment-ready container info
        """
        namespace = self.get_namespace(namespace_id)
        if not namespace:
            return {"error": f"Namespace {namespace_id} not found"}

        container = namespace.get_container(container_name)
        if not container:
            return {"error": f"Container {container_name} not found in {namespace_id}"}

        if not container.is_public:
            return {"error": "Container needs to be public in order to be selected and deployed"}

        tag_info = container.get_tag(tag)
        if not tag_info:
            return {"error": f"Tag {tag} not found"}

        return {
            "status": "ready_for_deployment",
            "registry_namespace": namespace.endpoint,
            "container": container_name,
            "tag": tag,
            "digest": tag_info["digest"],
            "full_image": f"{namespace.endpoint}/{container_name}:{tag}",
            "is_public": container.is_public
        }

    def get_registry_status(self):
        return {
            "endpoint": self.registry_endpoint,
            "namespaces": len(self.namespaces),
            "namespace_details": {nid: ns.get_namespace_info() for nid, ns in self.namespaces.items()}
        }

if __name__ == "__main__":
    registry = ContainerRegistry("rg.fr-par.scw.cloud")

    print("=== CONTAINER REGISTRY MANAGER DEMO ===\n")

    # Create namespace
    print("1. Creating registry namespace:")
    namespace = registry.create_namespace("odoo-tutorial-namespace")
    print(f"   Namespace: {namespace.namespace_id}")
    print(f"   Endpoint: {namespace.endpoint}\n")

    # Create containers
    print("2. Creating containers:")
    odoo = namespace.create_container("odoo", is_public=True)
    odoo.add_tag("latest")
    odoo.add_tag("16.0")
    odoo.add_tag("15.0")

    videocourts = namespace.create_container("videocourts", is_public=True)
    videocourts.add_tag("latest")
    videocourts.add_tag("v2.5.0")

    mybuyo = namespace.create_container("mybuyo", is_public=False)  # Private
    mybuyo.add_tag("latest")

    print(f"   Containers: {len(namespace.containers)}")
    for c in namespace.list_containers():
        public_icon = "" if c["is_public"] else "🔒"
        print(f"     {public_icon} {c['name']} (tags: {', '.join(c['tags'])})")
    print()

    # Select container for deployment (like UI)
    print("3. Selecting container for deployment:")
    print("   Registry namespace: rg.fr-par.scw.cloud/odoo-tutorial-namespace")

    result = registry.select_container_for_deployment("odoo-tutorial-namespace", "odoo", "latest")
    print(f"\n   Container: {result.get('container', 'error')}")
    print(f"   Tag: {result.get('tag', 'error')}")
    print(f"   Full image: {result.get('full_image', 'error')}")
    print(f"   Status: {result.get('status', 'error')}\n")

    # Try to deploy private container (should fail)
    print("4. Attempting to deploy private container (should fail):")
    result = registry.select_container_for_deployment("odoo-tutorial-namespace", "mybuyo", "latest")
    print(f"   Result: {result.get('error')}\n")

    # Pull image
    print("5. Pulling image:")
    pull_result = odoo.pull("latest")
    print(f"   Pulled: odoo:latest")
    print(f"   Digest: {pull_result['digest'][:20]}...")
    print(f"   Pull count: {odoo.pull_count}\n")

    # Registry status
    print("6. Registry status:")
    status = registry.get_registry_status()
    print(f"   Endpoint: {status['endpoint']}")
    print(f"   Namespaces: {status['namespaces']}")

    print("\n=== CONTAINER REGISTRY ARCHITECTURE ===")
    print("Registry namespace → Container → Tag selection → Deployment")
    print("Note: Container must be public to be deployed")
