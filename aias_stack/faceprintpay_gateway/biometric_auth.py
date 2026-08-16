#!/usr/bin/env python3
"""
FacePrintPay Sovereign Identity Layer
Biometric authentication for C25 API Gateway
"""
import hashlib
import json
from datetime import datetime, timedelta

class FacePrintPayAuth:
    def __init__(self):
        self.biometric_hash = None
        self.session_tokens = {}
    
    def enroll_biometric(self, biometric_data: str) -> str:
        """Enroll user's biometric signature (SHA-256 hash)"""
        self.biometric_hash = hashlib.sha256(biometric_data.encode()).hexdigest()
        return {"status": "enrolled", "hash": self.biometric_hash[:16] + "..."}
    
    def verify_biometric(self, biometric_data: str) -> bool:
        """Verify biometric against enrolled hash"""
        verify_hash = hashlib.sha256(biometric_data.encode()).hexdigest()
        return verify_hash == self.biometric_hash
    
    def generate_api_key(self, user_id: str, biometric_data: str) -> dict:
        """Generate sovereign API key with biometric verification"""
        if not self.verify_biometric(biometric_data):
            return {"error": "Biometric verification failed"}
        
        # Generate unique API key
        timestamp = datetime.now().isoformat()
        key_material = f"{user_id}:{timestamp}:{self.biometric_hash}"
        api_key = hashlib.sha256(key_material.encode()).hexdigest()
        
        # Store session (24hr expiry)
        expiry = datetime.now() + timedelta(hours=24)
        self.session_tokens[api_key] = {
            "user_id": user_id,
            "created": timestamp,
            "expires": expiry.isoformat(),
            "biometric_verified": True
        }
        
        return {
            "api_key": api_key,
            "expires": expiry.isoformat(),
            "sovereign_identity": "FacePrintPay Verified"
        }
    
    def validate_api_key(self, api_key: str) -> bool:
        """Validate API key and check expiry"""
        if api_key not in self.session_tokens:
            return False
        
        expiry = datetime.fromisoformat(self.session_tokens[api_key]["expires"])
        return datetime.now() < expiry

# Initialize
auth = FacePrintPayAuth()
