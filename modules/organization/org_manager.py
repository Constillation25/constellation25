#!/data/data/com.termux/files/usr/bin/python3
"""
Organization Manager
Organization → Projects → Resources
With Organization Management (Billing, Support) and IAM (Users, Policies, API Keys, Groups, Apps)
"""
import json
import time
import uuid
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s [ORG-MANAGER] %(message)s')
logger = logging.getLogger(__name__)

class Resource:
    """Individual resource within a project"""
    def __init__(self, name, resource_type, project_id):
        self.id = str(uuid.uuid4())[:8]
        self.name = name
        self.type = resource_type
        self.project_id = project_id
        self.created = time.time()
        self.metadata = {}

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "project_id": self.project_id,
            "created": self.created,
            "metadata": self.metadata
        }

class Project:
    """Project containing resources"""
    def __init__(self, name, is_default=False):
        self.id = str(uuid.uuid4())[:8]
        self.name = name
        self.is_default = is_default
        self.created = time.time()
        self.resources = {}

    def add_resource(self, name, resource_type):
        resource = Resource(name, resource_type, self.id)
        self.resources[resource.id] = resource
        logger.info(f"Resource added to {self.name}: {name} ({resource_type})")
        return resource

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "is_default": self.is_default,
            "created": self.created,
            "resources": {rid: r.to_dict() for rid, r in self.resources.items()}
        }

class IAMUser:
    """IAM User with policies and API keys"""
    def __init__(self, username, email):
        self.id = str(uuid.uuid4())[:8]
        self.username = username
        self.email = email
        self.created = time.time()
        self.policies = []
        self.api_keys = []
        self.groups = []
        self.apps = []
        self.active = True

    def add_policy(self, policy_name):
        self.policies.append(policy_name)
        logger.info(f"Policy {policy_name} added to user {self.username}")

    def generate_api_key(self, key_name):
        api_key = {
            "id": str(uuid.uuid4())[:8],
            "name": key_name,
            "key": f"sk_{uuid.uuid4().hex[:32]}",
            "created": time.time(),
            "active": True
        }
        self.api_keys.append(api_key)
        logger.info(f"API Key generated for {self.username}: {key_name}")
        return api_key

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "created": self.created,
            "policies": self.policies,
            "api_keys": [k["name"] for k in self.api_keys],
            "groups": self.groups,
            "apps": self.apps,
            "active": self.active
        }

class Organization:
    """Top-level organization containing projects, IAM, billing, support"""
    def __init__(self, org_name, config_dir=None):
        self.name = org_name
        self.id = str(uuid.uuid4())[:8]
        self.created = time.time()
        self.config_dir = config_dir or str(Path.home() / "constellation25" / "config" / "orgs")
        Path(self.config_dir).mkdir(parents=True, exist_ok=True)

        # Resources (Projects)
        self.projects = {}

        # Organization Management
        self.support_plans = []
        self.abuse_tickets = []
        self.support_tickets = []
        self.billing = {"balance": 0.0, "invoices": []}

        # IAM
        self.users = {}
        self.policies = {}
        self.groups = {}
        self.apps = {}

        self._load_or_create_default()

    def _load_or_create_default(self):
        """Load existing org or create default structure"""
        org_file = f"{self.config_dir}/{self.name}.json"
        if Path(org_file).exists():
            with open(org_file, 'r') as f:
                data = json.load(f)
                # Restore from saved state
                for proj_data in data.get("projects", []):
                    proj = Project(proj_data["name"], proj_data["is_default"])
                    proj.id = proj_data["id"]
                    self.projects[proj.id] = proj
        else:
            # Create default project
            default_proj = Project("Default Project", is_default=True)
            self.projects[default_proj.id] = default_proj
            self._save()
            logger.info(f"Organization created: {self.name}")

    def _save(self):
        org_file = f"{self.config_dir}/{self.name}.json"
        data = {
            "name": self.name,
            "id": self.id,
            "created": self.created,
            "projects": [p.to_dict() for p in self.projects.values()],
            "users": [u.to_dict() for u in self.users.values()],
            "billing": self.billing
        }
        with open(org_file, 'w') as f:
            json.dump(data, f, indent=2)

    def create_project(self, name):
        project = Project(name)
        self.projects[project.id] = project
        self._save()
        logger.info(f"Project created: {name}")
        return project

    def add_user(self, username, email):
        user = IAMUser(username, email)
        self.users[user.id] = user
        self._save()
        logger.info(f"User created: {username}")
        return user

    def add_support_ticket(self, subject, description, priority="medium"):
        ticket = {
            "id": str(uuid.uuid4())[:8],
            "subject": subject,
            "description": description,
            "priority": priority,
            "status": "open",
            "created": time.time()
        }
        self.support_tickets.append(ticket)
        self._save()
        logger.info(f"Support ticket created: {subject}")
        return ticket

    def add_billing_invoice(self, amount, description):
        invoice = {
            "id": str(uuid.uuid4())[:8],
            "amount": amount,
            "description": description,
            "status": "pending",
            "created": time.time()
        }
        self.billing["invoices"].append(invoice)
        self._save()
        return invoice

    def get_summary(self):
        return {
            "organization": self.name,
            "projects": len(self.projects),
            "users": len(self.users),
            "support_tickets": len(self.support_tickets),
            "billing_balance": self.billing["balance"],
            "default_project": next((p.name for p in self.projects.values() if p.is_default), None)
        }

if __name__ == "__main__":
    org = Organization("Kre8tiveKonceptz")

    print("=== ORGANIZATION MANAGEMENT DEMO ===\n")

    # Create projects
    print("1. Creating Projects:")
    proj2 = org.create_project("Project 2")
    proj3 = org.create_project("Project 3")
    print(f"   Default Project: {list(org.projects.values())[0].name}")
    print(f"   Project 2: {proj2.name}")
    print(f"   Project 3: {proj3.name}\n")

    # Add resources to projects
    print("2. Adding Resources:")
    default_proj = list(org.projects.values())[0]
    default_proj.add_resource("VideoCourts Engine", "compute")
    default_proj.add_resource("MyBuyo Database", "database")
    proj2.add_resource("Agent Swarm", "compute")
    print(f"   Default Project: {len(default_proj.resources)} resources")
    print(f"   Project 2: {len(proj2.resources)} resources\n")

    # Create IAM users
    print("3. Creating IAM Users:")
    user1 = org.add_user("CyGeL", "cygel@kre8tive.space")
    user1.add_policy("admin")
    user1.generate_api_key("production-key")
    user2 = org.add_user("Agent_Mars", "mars@c25.local")
    user2.add_policy("deploy")
    print(f"   Users: {len(org.users)}")
    print(f"   CyGeL policies: {user1.policies}")
    print(f"   CyGeL API keys: {len(user1.api_keys)}\n")

    # Support tickets
    print("4. Support Tickets:")
    org.add_support_ticket("BioAuth integration issue", "Fingerprint scanner timeout", "high")
    org.add_support_ticket("Feature request", "Add Ed25519 SSH key support", "low")
    print(f"   Open tickets: {len(org.support_tickets)}\n")

    # Billing
    print("5. Billing:")
    org.add_billing_invoice(999.00, "Professional License - Annual")
    org.add_billing_invoice(2500.00, "VeRseD_Ai Biometric Gate")
    print(f"   Invoices: {len(org.billing['invoices'])}")
    print(f"   Total: ${sum(inv['amount'] for inv in org.billing['invoices']):,.2f}\n")

    # Summary
    print("6. Organization Summary:")
    print(json.dumps(org.get_summary(), indent=2))
