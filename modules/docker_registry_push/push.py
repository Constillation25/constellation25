#!/data/data/com.termux/files/usr/bin/python3
"""
Docker Registry Push
docker login → docker pull → docker tag → docker push
Based on Push instructions diagram for Scaleway Container Registry
"""
import json
import time
import hashlib
import logging
import subprocess
from pathlib import Path
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s [DOCKER-PUSH] %(message)s')
logger = logging.getLogger(__name__)

class DockerRegistry:
    """Docker registry (like Scaleway Container Registry)"""
    def __init__(self, registry_url):
        self.registry_url = registry_url
        self.namespaces = {}
        self.images = {}

    def create_namespace(self, namespace_name):
        """Create a registry namespace"""
        self.namespaces[namespace_name] = {
            "name": namespace_name,
            "created": datetime.now().isoformat(),
            "images": []
        }
        logger.info(f"Namespace created: {namespace_name}")
        return namespace_name

    def push_image(self, namespace, image_name, tag, image_data=None):
        """Push an image to registry"""
        full_image = f"{self.registry_url}/{namespace}/{image_name}:{tag}"

        if not image_data:
            image_data = f"fake_image_content_{int(time.time())}"

        image_id = hashlib.sha256(image_data.encode()).hexdigest()[:16]

        self.images[full_image] = {
            "image": full_image,
            "image_id": image_id,
            "namespace": namespace,
            "name": image_name,
            "tag": tag,
            "size_mb": round(len(image_data) / (1024 * 1024), 2),
            "pushed_at": datetime.now().isoformat(),
            "digest": f"sha256:{hashlib.sha256(image_data.encode()).hexdigest()}"
        }

        if namespace in self.namespaces:
            self.namespaces[namespace]["images"].append(full_image)

        logger.info(f"Image pushed: {full_image}")
        return self.images[full_image]

    def pull_image(self, full_image):
        """Pull an image from registry"""
        if full_image not in self.images:
            return {"error": f"Image {full_image} not found"}

        logger.info(f"Image pulled: {full_image}")
        return self.images[full_image]

    def list_images(self, namespace=None):
        """List images in registry"""
        if namespace:
            return [img for img_name, img in self.images.items() if img["namespace"] == namespace]
        return list(self.images.values())

class DockerClient:
    """Docker client for login, pull, tag, push operations"""
    def __init__(self):
        self.logged_in = False
        self.current_registry = None
        self.local_images = {}
        self.secret_token = None

    def login(self, registry_url, username="nologin", password=None):
        """docker login"""
        if not password:
            return {"error": "Password/secret token required"}

        self.logged_in = True
        self.current_registry = registry_url
        self.secret_token = password

        logger.info(f"Logged in to {registry_url}")
        return {
            "status": "logged_in",
            "registry": registry_url,
            "username": username
        }

    def pull(self, image_name, tag="latest"):
        """docker pull"""
        full_image = f"{image_name}:{tag}"
        self.local_images[full_image] = {
            "image": full_image,
            "pulled_at": datetime.now().isoformat(),
            "size_mb": 75.5  # Simulated
        }
        logger.info(f"Pulled: {full_image}")
        return self.local_images[full_image]

    def tag(self, source_image, target_image):
        """docker tag"""
        if source_image not in self.local_images:
            return {"error": f"Image {source_image} not found locally"}

        self.local_images[target_image] = {
            "image": target_image,
            "source": source_image,
            "tagged_at": datetime.now().isoformat()
        }
        logger.info(f"Tagged: {source_image} → {target_image}")
        return self.local_images[target_image]

    def push(self, image_name):
        """docker push"""
        if image_name not in self.local_images:
            return {"error": f"Image {image_name} not found locally"}

        if not self.logged_in:
            return {"error": "Not logged in. Run docker login first"}

        logger.info(f"Pushed: {image_name}")
        return {
            "status": "pushed",
            "image": image_name,
            "pushed_at": datetime.now().isoformat()
        }

    def get_client_status(self):
        return {
            "logged_in": self.logged_in,
            "registry": self.current_registry,
            "local_images": len(self.local_images)
        }

class DockerPushWorkflow:
    """Complete docker push workflow"""
    def __init__(self, registry_url):
        self.registry = DockerRegistry(registry_url)
        self.client = DockerClient()
        self.workflow_steps = []

    def execute_workflow(self, namespace, image_name, tag, secret_token):
        """Execute complete push workflow"""
        steps = []

        # Step 1: docker login
        steps.append({"step": 1, "command": f"docker login {self.registry.registry_url}/{namespace} -u nologin -p [SECRET_TOKEN]"})
        login_result = self.client.login(f"{self.registry.registry_url}/{namespace}", password=secret_token)
        steps[-1]["result"] = login_result

        # Step 2: docker pull
        steps.append({"step": 2, "command": f"docker pull {image_name}:{tag}"})
        pull_result = self.client.pull(image_name, tag)
        steps[-1]["result"] = pull_result

        # Step 3: docker tag
        target_image = f"{self.registry.registry_url}/{namespace}/{image_name}:{tag}"
        steps.append({"step": 3, "command": f"docker tag {image_name}:{tag} {target_image}"})
        tag_result = self.client.tag(f"{image_name}:{tag}", target_image)
        steps[-1]["result"] = tag_result

        # Step 4: docker push
        steps.append({"step": 4, "command": f"docker push {target_image}"})
        push_result = self.client.push(target_image)
        steps[-1]["result"] = push_result

        # Actually push to registry
        if "error" not in push_result:
            self.registry.push_image(namespace, image_name, tag)

        self.workflow_steps = steps
        return steps

    def get_workflow_status(self):
        return {
            "registry": self.registry.registry_url,
            "total_images": len(self.registry.images),
            "workflow_steps": len(self.workflow_steps)
        }

if __name__ == "__main__":
    workflow = DockerPushWorkflow("rg.fr-par.scw.cloud")

    print("=== DOCKER REGISTRY PUSH DEMO ===\n")

    # Create namespace
    print("1. Creating registry namespace:")
    workflow.registry.create_namespace("mynamespace")
    print(f"   Namespace: mynamespace")
    print(f"   Registry: {workflow.registry.registry_url}\n")

    # Execute push workflow
    print("2. Executing push workflow:")
    print("   Sign in to your registry:")
    print("   $ docker login rg.fr-par.scw.cloud/mynamespace -u nologin -p [YOUR_SECRET_TOKEN]")
    print()
    print("   Push your first image in your terminal:")
    print("   $ docker pull ubuntu:latest")
    print("   $ docker tag ubuntu:latest rg.fr-par.scw.cloud/mynamespace/ubuntu:latest")
    print("   $ docker push rg.fr-par.scw.cloud/mynamespace/ubuntu:latest")
    print()

    steps = workflow.execute_workflow(
        namespace="mynamespace",
        image_name="ubuntu",
        tag="latest",
        secret_token="$SCW_SECRET_TOKEN"
    )

    print("3. Workflow execution:")
    for step in steps:
        print(f"   Step {step['step']}: {step['command']}")
        result = step['result']
        if 'error' in result:
            print(f"     ❌ Error: {result['error']}")
        else:
            print(f"     ✅ Success")
    print()

    # List images
    print("4. Registry images:")
    images = workflow.registry.list_images()
    for img in images:
        print(f"   {img['image']}")
        print(f"     ID: {img['image_id']}")
        print(f"     Size: {img['size_mb']} MB")
        print(f"     Pushed: {img['pushed_at']}")

    print("\n=== DOCKER PUSH WORKFLOW ===")
    print("docker login → docker pull → docker tag → docker push")
    print("Registry: rg.fr-par.scw.cloud/mynamespace")
