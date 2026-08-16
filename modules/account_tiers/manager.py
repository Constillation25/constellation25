#!/data/data/com.termux/files/usr/bin/python3
"""
Account Tier Manager
Manages account tiers: Discover, Test, Build
Each tier has different requirements (Email, Billing, KYC, Support)
Based on account tier table diagram
"""
import json
import time
import hashlib
import logging
from pathlib import Path
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s [ACCOUNT-TIERS] %(message)s')
logger = logging.getLogger(__name__)

class AccountTier:
    """Represents an account tier"""
    def __init__(self, tier_name, requirements):
        self.tier_name = tier_name
        self.requirements = requirements
        self.features = {
            "Discover": {
                "max_projects": 3,
                "max_storage_gb": 5,
                "max_bandwidth_gb": 10,
                "support_level": "Community",
                "sla": "None"
            },
            "Test": {
                "max_projects": 10,
                "max_storage_gb": 25,
                "max_bandwidth_gb": 100,
                "support_level": "Email",
                "sla": "Best effort"
            },
            "Build": {
                "max_projects": -1,  # Unlimited
                "max_storage_gb": 250,
                "max_bandwidth_gb": 1000,
                "support_level": "Priority",
                "sla": "99.9% uptime"
            }
        }.get(tier_name, {})

    def check_requirement(self, req_name):
        """Check if requirement is needed for this tier"""
        return self.requirements.get(req_name, False)

    def get_tier_info(self):
        return {
            "tier": self.tier_name,
            "requirements": self.requirements,
            "features": self.features
        }

class UserAccount:
    """User account with tier"""
    def __init__(self, user_id, email):
        self.user_id = user_id
        self.email = email
        self.tier = "Discover"  # Default tier
        self.created_at = datetime.now().isoformat()
        self.verified = {
            "email": False,
            "billing": False,
            "kyc": False
        }
        self.billing_info = None
        self.kyc_info = None
        self.projects = []
        self.storage_used_gb = 0
        self.bandwidth_used_gb = 0

    def upgrade_tier(self, new_tier):
        """Upgrade account tier"""
        valid_tiers = ["Discover", "Test", "Build"]
        if new_tier not in valid_tiers:
            return {"error": f"Invalid tier. Must be one of: {valid_tiers}"}

        # Check requirements
        tier_reqs = AccountTier(new_tier, {}).requirements
        missing = []

        if tier_reqs.get("email") and not self.verified["email"]:
            missing.append("Email verification")
        if tier_reqs.get("billing") and not self.verified["billing"]:
            missing.append("Billing information")
        if tier_reqs.get("kyc") and not self.verified["kyc"]:
            missing.append("KYC verification")

        if missing:
            return {"error": f"Missing requirements: {', '.join(missing)}"}

        old_tier = self.tier
        self.tier = new_tier
        logger.info(f"Account {self.user_id} upgraded from {old_tier} to {new_tier}")
        return {"status": "upgraded", "from": old_tier, "to": new_tier}

    def verify_email(self):
        """Verify email address"""
        self.verified["email"] = True
        logger.info(f"Email verified for {self.user_id}")
        return True

    def add_billing_info(self, billing_data):
        """Add billing information"""
        self.billing_info = billing_data
        self.verified["billing"] = True
        logger.info(f"Billing info added for {self.user_id}")
        return True

    def add_kyc_info(self, kyc_data):
        """Add KYC verification"""
        self.kyc_info = kyc_data
        self.verified["kyc"] = True
        logger.info(f"KYC verified for {self.user_id}")
        return True

    def get_account_status(self):
        tier = AccountTier(self.tier, {})
        return {
            "user_id": self.user_id,
            "email": self.email,
            "tier": self.tier,
            "verified": self.verified,
            "features": tier.get_tier_info()["features"],
            "usage": {
                "projects": len(self.projects),
                "storage_gb": self.storage_used_gb,
                "bandwidth_gb": self.bandwidth_used_gb
            }
        }

class AccountTierManager:
    """Manages account tiers and upgrades"""
    def __init__(self):
        self.accounts = {}
        self.tier_definitions = {
            "Discover": {
                "email": True,
                "billing": False,
                "kyc": False,
                "support_level": "Community"
            },
            "Test": {
                "email": True,
                "billing": True,
                "kyc": False,
                "support_level": "Email"
            },
            "Build": {
                "email": True,
                "billing": True,
                "kyc": True,
                "support_level": "Priority"
            }
        }

    def create_account(self, email):
        """Create new account"""
        user_id = hashlib.sha256(f"{email}{time.time()}".encode()).hexdigest()[:16]
        account = UserAccount(user_id, email)
        self.accounts[user_id] = account

        # Auto-verify email for Discover tier
        account.verify_email()

        logger.info(f"Account created: {user_id} ({email})")
        return account

    def get_account(self, user_id):
        """Get account by ID"""
        return self.accounts.get(user_id)

    def upgrade_account(self, user_id, new_tier):
        """Upgrade account tier"""
        if user_id not in self.accounts:
            return {"error": "Account not found"}

        account = self.accounts[user_id]
        return account.upgrade_tier(new_tier)

    def get_tier_requirements(self, tier):
        """Get requirements for a tier"""
        return self.tier_definitions.get(tier, {})

    def get_manager_status(self):
        return {
            "total_accounts": len(self.accounts),
            "tier_distribution": {
                tier: len([a for a in self.accounts.values() if a.tier == tier])
                for tier in ["Discover", "Test", "Build"]
            }
        }

if __name__ == "__main__":
    manager = AccountTierManager()

    print("=== ACCOUNT TIER MANAGER DEMO ===\n")

    # Show tier requirements table
    print("1. Account Tier Requirements:")
    print(f"{'':<20} {'Discover':<12} {'Test':<12} {'Build':<12}")
    print("-" * 50)
    print(f"{'E-mail address':<20} {'✓':<12} {'✓':<12} {'✓':<12}")
    print(f"{'Billing Info':<20} {'':<12} {'✓':<12} {'✓':<12}")
    print(f"{'Identity (KYC)':<20} {'':<12} {'':<12} {'✓':<12}")
    print(f"{'Support Level':<20} {'Community':<12} {'Email':<12} {'Priority':<12}")
    print()

    # Create account
    print("2. Creating account (Discover tier):")
    account = manager.create_account("cygel@kre8tive.space")
    print(f"   User ID: {account.user_id}")
    print(f"   Email: {account.email}")
    print(f"   Tier: {account.tier}")
    print(f"   Features: {account.get_account_status()['features']}\n")

    # Try to upgrade to Test (need billing)
    print("3. Attempting upgrade to Test tier:")
    result = manager.upgrade_account(account.user_id, "Test")
    print(f"   Result: {result.get('error', 'Success')}\n")

    # Add billing info
    print("4. Adding billing information:")
    account.add_billing_info({
        "name": "CyGeL White",
        "card_last4": "4242",
        "verified": True
    })
    print("   Billing info added\n")

    # Upgrade to Test
    print("5. Upgrading to Test tier:")
    result = manager.upgrade_account(account.user_id, "Test")
    print(f"   Status: {result.get('status')}")
    print(f"   From: {result.get('from')} → To: {result.get('to')}\n")

    # Try to upgrade to Build (need KYC)
    print("6. Attempting upgrade to Build tier:")
    result = manager.upgrade_account(account.user_id, "Build")
    print(f"   Result: {result.get('error', 'Success')}\n")

    # Add KYC
    print("7. Completing KYC verification:")
    account.add_kyc_info({
        "country": "US",
        "id_type": "passport",
        "verified": True,
        "verified_at": datetime.now().isoformat()
    })
    print("   KYC verified\n")

    # Upgrade to Build
    print("8. Upgrading to Build tier:")
    result = manager.upgrade_account(account.user_id, "Build")
    print(f"   Status: {result.get('status')}")
    print(f"   From: {result.get('from')} → To: {result.get('to')}\n")

    # Final account status
    print("9. Final account status:")
    status = account.get_account_status()
    print(f"   Tier: {status['tier']}")
    print(f"   Support: {status['features']['support_level']}")
    print(f"   Storage: {status['usage']['storage_gb']}GB / {status['features']['max_storage_gb']}GB")
    print(f"   Bandwidth: {status['usage']['bandwidth_gb']}GB / {status['features']['max_bandwidth_gb']}GB")
    print(f"   Projects: {status['usage']['projects']} / {status['features']['max_projects']}")

    print("\n=== ACCOUNT TIER ARCHITECTURE ===")
    print("Discover → Test → Build")
    print("Requirements: Email → +Billing → +KYC")
