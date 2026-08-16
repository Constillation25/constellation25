#!/data/data/com.termux/files/usr/bin/python3
"""
Secret Manager
Manages credentials for CI/CD pipelines, web applications, and databases
Flow: CI/CD Pipeline → Secret Manager → Web Application → Database
"""
import json
import time
import hashlib
import logging
from pathlib import Path
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s [SECRET-MGR] %(message)s')
logger = logging.getLogger(__name__)

class SecretManager:
    """Secure credential storage and retrieval"""
    def __init__(self, secrets_dir=None):
        self.secrets_dir = secrets_dir or str(Path.home() / "constellation25" / "config" / "secrets")
        Path(self.secrets_dir).mkdir(parents=True, exist_ok=True)
        self.secrets_file = f"{self.secrets_dir}/secrets.json"
        self.secrets = self._load_secrets()
        self.access_log = []

    def _load_secrets(self):
        if Path(self.secrets_file).exists():
            with open(self.secrets_file, 'r') as f:
                return json.load(f)
        return {"secrets": {}, "created": datetime.now().isoformat()}

    def _save_secrets(self):
        with open(self.secrets_file, 'w') as f:
            json.dump(self.secrets, f, indent=2)

    def _hash_secret(self, secret_value):
        """Hash secret for storage (in production, use proper encryption)"""
        return hashlib.sha256(secret_value.encode()).hexdigest()

    def store_secret(self, name, value, metadata=None):
        """Store a secret credential"""
        secret_id = hashlib.sha256(f"{name}{time.time()}".encode()).hexdigest()[:16]

        secret_entry = {
            "id": secret_id,
            "name": name,
            "value_hash": self._hash_secret(value),
            "value_encrypted": value,  # In production, encrypt this
            "metadata": metadata or {},
            "created": datetime.now().isoformat(),
            "last_accessed": None,
            "access_count": 0,
            "rotation_count": 0
        }

        self.secrets["secrets"][name] = secret_entry
        self._save_secrets()

        logger.info(f"Secret stored: {name}")
        return secret_entry

    def get_secret(self, name, requester="unknown"):
        """
        Retrieve a secret (logs access for audit trail)
        requester: CI/CD Pipeline, Web Application, etc.
        """
        if name not in self.secrets["secrets"]:
            logger.warning(f"Secret not found: {name} (requested by {requester})")
            return None

        secret = self.secrets["secrets"][name]
        secret["last_accessed"] = datetime.now().isoformat()
        secret["access_count"] += 1
        self._save_secrets()

        # Log access
        self.access_log.append({
            "secret": name,
            "requester": requester,
            "timestamp": datetime.now().isoformat(),
            "action": "retrieve"
        })

        logger.info(f"Secret retrieved: {name} (by {requester})")
        return secret["value_encrypted"]

    def rotate_secret(self, name, new_value):
        """Rotate a secret (update with new value)"""
        if name not in self.secrets["secrets"]:
            return False

        old_hash = self.secrets["secrets"][name]["value_hash"]
        self.secrets["secrets"][name]["value_hash"] = self._hash_secret(new_value)
        self.secrets["secrets"][name]["value_encrypted"] = new_value
        self.secrets["secrets"][name]["rotation_count"] += 1
        self.secrets["secrets"][name]["last_rotated"] = datetime.now().isoformat()
        self._save_secrets()

        logger.info(f"Secret rotated: {name} (rotation #{self.secrets['secrets'][name]['rotation_count']})")

        # Log rotation
        self.access_log.append({
            "secret": name,
            "requester": "system",
            "timestamp": datetime.now().isoformat(),
            "action": "rotate",
            "old_hash": old_hash[:16]
        })

        return True

    def delete_secret(self, name):
        """Delete a secret"""
        if name in self.secrets["secrets"]:
            del self.secrets["secrets"][name]
            self._save_secrets()
            logger.info(f"Secret deleted: {name}")
            return True
        return False

    def list_secrets(self):
        """List all secrets (without values)"""
        return {
            name: {
                "id": s["id"],
                "created": s["created"],
                "last_accessed": s["last_accessed"],
                "access_count": s["access_count"],
                "rotation_count": s["rotation_count"]
            }
            for name, s in self.secrets["secrets"].items()
        }

    def get_access_log(self):
        """Get access audit log"""
        return self.access_log[-50:]  # Last 50 entries

class CICDPipeline:
    """Simulates CI/CD pipeline requesting credentials"""
    def __init__(self, secret_manager):
        self.sm = secret_manager
        self.deployed_apps = []

    def deploy_web_app(self, app_name, db_secret_name):
        """
        CI/CD Pipeline flow:
        1. Request database credentials from Secret Manager
        2. Deploy web application with credentials as env vars
        3. Web app connects to database
        """
        logger.info(f"CI/CD Pipeline: Deploying {app_name}")

        # Step 1: Get credentials from Secret Manager
        db_password = self.sm.get_secret(db_secret_name, requester="CI/CD Pipeline")
        if not db_password:
            logger.error(f"Failed to get secret: {db_secret_name}")
            return None

        # Step 2: Deploy with env vars
        deployment = {
            "app": app_name,
            "env_vars": {
                "DB_PASSWORD": "***REDACTED***",
                "DB_HOST": "localhost",
                "DB_PORT": 5432
            },
            "deployed": datetime.now().isoformat(),
            "status": "deployed"
        }

        self.deployed_apps.append(deployment)
        logger.info(f"Web application deployed: {app_name}")

        return deployment

class WebApplication:
    """Simulates web application using credentials"""
    def __init__(self, secret_manager):
        self.sm = secret_manager
        self.db_connections = []

    def connect_to_database(self, db_secret_name):
        """
        Web Application flow:
        1. Request credentials from Secret Manager
        2. Connect to database
        """
        logger.info(f"Web Application: Connecting to database")

        # Get credentials
        db_password = self.sm.get_secret(db_secret_name, requester="Web Application")
        if not db_password:
            logger.error("Failed to get database credentials")
            return False

        # Simulate connection
        connection = {
            "host": "localhost",
            "port": 5432,
            "user": "app_user",
            "password": "***REDACTED***",
            "connected": True,
            "timestamp": datetime.now().isoformat()
        }

        self.db_connections.append(connection)
        logger.info("Database connection established")
        return True

if __name__ == "__main__":
    sm = SecretManager()

    print("=== SECRET MANAGER CI/CD FLOW DEMO ===\n")

    # Store database credentials
    print("1. Storing database credentials:")
    sm.store_secret("prod_db_password", "SuperSecret123!", {"env": "production", "db": "postgresql"})
    sm.store_secret("api_key", "sk-1234567890", {"service": "external-api"})
    print(f"   Secrets stored: {len(sm.list_secrets())}\n")

    # CI/CD Pipeline deployment
    print("2. CI/CD Pipeline deploying web application:")
    pipeline = CICDPipeline(sm)
    deployment = pipeline.deploy_web_app("VideoCourts-Web", "prod_db_password")
    if deployment:
        print(f"   App: {deployment['app']}")
        print(f"   Status: {deployment['status']}")
        print(f"   Deployed: {deployment['deployed']}\n")

    # Web Application connecting to database
    print("3. Web Application connecting to database:")
    webapp = WebApplication(sm)
    connected = webapp.connect_to_database("prod_db_password")
    print(f"   Connected: {connected}")
    print(f"   Active connections: {len(webapp.db_connections)}\n")

    # Rotate secret
    print("4. Rotating database password:")
    sm.rotate_secret("prod_db_password", "NewSecret456!")
    rotated_secret = sm.secrets["secrets"]["prod_db_password"]
    print(f"   Rotation count: {rotated_secret['rotation_count']}")
    print(f"   Last rotated: {rotated_secret.get('last_rotated')}\n")

    # Access log
    print("5. Access audit log:")
    for entry in sm.get_access_log():
        print(f"   [{entry['action']}] {entry['secret']} by {entry['requester']} at {entry['timestamp']}")

    print("\n=== SECRET MANAGER FLOW ===")
    print("CI/CD Pipeline → Secret Manager → Web Application → Database")
    print("All credential access is logged and auditable")
