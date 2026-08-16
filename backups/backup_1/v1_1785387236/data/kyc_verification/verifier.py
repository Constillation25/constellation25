#!/data/data/com.termux/files/usr/bin/python3
"""
KYC Verification System
Identity verification with country selection and ID type (Passport, Driver's license, Identity card)
Based on KYC verification UI diagram
"""
import json
import time
import hashlib
import logging
from pathlib import Path
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s [KYC] %(message)s')
logger = logging.getLogger(__name__)

class IDDocument:
    """Represents an ID document"""
    def __init__(self, doc_type, country, doc_number):
        self.doc_type = doc_type  # passport, drivers_license, identity_card
        self.country = country
        self.doc_number = doc_number
        self.verified = False
        self.verified_at = None
        self.front_image = None
        self.back_image = None
        self.selfie_image = None

    def upload_front(self, image_path):
        """Upload front of ID"""
        self.front_image = image_path
        logger.info(f"ID front uploaded: {image_path}")

    def upload_back(self, image_path):
        """Upload back of ID (if applicable)"""
        self.back_image = image_path
        logger.info(f"ID back uploaded: {image_path}")

    def upload_selfie(self, image_path):
        """Upload selfie for liveness check"""
        self.selfie_image = image_path
        logger.info(f"Selfie uploaded: {image_path}")

    def verify(self):
        """Verify the ID document"""
        # Simulate verification process
        self.verified = True
        self.verified_at = datetime.now().isoformat()
        logger.info(f"ID verified: {self.doc_type} from {self.country}")
        return True

    def get_info(self):
        return {
            "type": self.doc_type,
            "country": self.country,
            "number": self.doc_number[-4:] if self.doc_number else "****",  # Hide full number
            "verified": self.verified,
            "verified_at": self.verified_at
        }

class KYCVerifier:
    """KYC verification system"""
    def __init__(self):
        self.supported_countries = {
            "US": "United States",
            "GB": "United Kingdom",
            "IT": "Italy",
            "FR": "France",
            "DE": "Germany",
            "ES": "Spain",
            "CA": "Canada",
            "AU": "Australia"
        }

        self.id_types = {
            "passport": "Passport",
            "drivers_license": "Driver's license",
            "identity_card": "Identity card"
        }

        self.verifications = {}

    def get_countries(self):
        """Get list of supported countries"""
        return self.supported_countries

    def get_id_types(self):
        """Get list of supported ID types"""
        return self.id_types

    def create_verification(self, user_id, country, id_type, id_number):
        """Create a new KYC verification"""
        if country not in self.supported_countries:
            return {"error": f"Country {country} not supported"}

        if id_type not in self.id_types:
            return {"error": f"ID type {id_type} not supported"}

        doc = IDDocument(id_type, country, id_number)
        verification = {
            "user_id": user_id,
            "document": doc,
            "status": "pending",
            "created_at": datetime.now().isoformat(),
            "steps": {
                "upload_front": False,
                "upload_back": False,
                "upload_selfie": False,
                "verification": False
            }
        }

        self.verifications[user_id] = verification
        logger.info(f"KYC verification created for {user_id}")
        return verification

    def upload_documents(self, user_id, front_path, back_path=None, selfie_path=None):
        """Upload ID documents"""
        if user_id not in self.verifications:
            return {"error": "Verification not found"}

        verification = self.verifications[user_id]
        doc = verification["document"]

        # Upload front (required)
        doc.upload_front(front_path)
        verification["steps"]["upload_front"] = True

        # Upload back (optional for passport, required for others)
        if back_path:
            doc.upload_back(back_path)
            verification["steps"]["upload_back"] = True

        # Upload selfie (required)
        if selfie_path:
            doc.upload_selfie(selfie_path)
            verification["steps"]["upload_selfie"] = True

        logger.info(f"Documents uploaded for {user_id}")
        return verification

    def verify_identity(self, user_id):
        """Verify identity"""
        if user_id not in self.verifications:
            return {"error": "Verification not found"}

        verification = self.verifications[user_id]
        doc = verification["document"]

        # Check all steps completed
        if not all(verification["steps"].values()):
            missing = [step for step, done in verification["steps"].items() if not done]
            return {"error": f"Incomplete steps: {', '.join(missing)}"}

        # Perform verification
        doc.verify()
        verification["status"] = "verified"
        verification["steps"]["verification"] = True
        verification["verified_at"] = datetime.now().isoformat()

        logger.info(f"Identity verified for {user_id}")
        return verification

    def get_verification_status(self, user_id):
        """Get verification status"""
        if user_id not in self.verifications:
            return {"error": "Verification not found"}

        verification = self.verifications[user_id]
        return {
            "user_id": user_id,
            "status": verification["status"],
            "document": verification["document"].get_info(),
            "steps": verification["steps"],
            "created_at": verification["created_at"],
            "verified_at": verification.get("verified_at")
        }

if __name__ == "__main__":
    verifier = KYCVerifier()

    print("=== KYC VERIFICATION SYSTEM DEMO ===\n")

    # Show supported countries and ID types
    print("1. Supported countries and ID types:")
    print("   Countries:")
    for code, name in list(verifier.get_countries().items())[:5]:
        print(f"     - {name} ({code})")
    print("   ID Types:")
    for id_type, name in verifier.get_id_types().items():
        print(f"     - {name}")
    print()

    # Create verification (like Italy in screenshot)
    print("2. Creating KYC verification:")
    print("   Country: Italy (IT)")
    print("   ID Type: Passport")
    verification = verifier.create_verification(
        user_id="user_12345",
        country="IT",
        id_type="passport",
        id_number="AB1234567"
    )
    print(f"   Status: {verification['status']}\n")

    # Upload documents
    print("3. Uploading documents:")
    # Create dummy files
    Path("/tmp/kyc").mkdir(exist_ok=True)
    front = "/tmp/kyc/passport_front.jpg"
    back = "/tmp/kyc/passport_back.jpg"
    selfie = "/tmp/kyc/selfie.jpg"

    for f in [front, back, selfie]:
        Path(f).touch()

    result = verifier.upload_documents("user_12345", front, back, selfie)
    print(f"   Front uploaded: {result['steps']['upload_front']}")
    print(f"   Back uploaded: {result['steps']['upload_back']}")
    print(f"   Selfie uploaded: {result['steps']['upload_selfie']}\n")

    # Verify identity
    print("4. Verifying identity:")
    result = verifier.verify_identity("user_12345")
    print(f"   Status: {result['status']}")
    print(f"   Verified at: {result.get('verified_at')}\n")

    # Get final status
    print("5. Verification status:")
    status = verifier.get_verification_status("user_12345")
    print(f"   User: {status['user_id']}")
    print(f"   Document: {status['document']['type']} ({status['document']['country']})")
    print(f"   Number: ****{status['document']['number']}")
    print(f"   Verified: {status['document']['verified']}")
    print(f"   Steps completed: {all(status['steps'].values())}")

    print("\n=== KYC VERIFICATION ARCHITECTURE ===")
    print("Select Country → Select ID Type → Upload Documents → Verification")
    print("ID Types: Passport, Driver's License, Identity Card")
