#!/data/data/com.termux/files/usr/bin/python3
"""
Production Encryption Manager
Encrypts evidence vault and sensitive artifacts
"""
import json
import hashlib
import logging
from pathlib import Path
from datetime import datetime
from cryptography.fernet import Fernet

logging.basicConfig(level=logging.INFO, format='%(asctime)s [ENCRYPT] %(message)s')
logger = logging.getLogger(__name__)

class ProductionEncryption:
    """Encryption manager for sensitive data"""
    def __init__(self, key_file=None):
        self.key_file = key_file or str(Path.home() / "constellation25" / "secrets" / "encryption.key")
        Path(self.key_file).parent.mkdir(parents=True, exist_ok=True)
        self.key = self._load_or_generate_key()
        self.fernet = Fernet(self.key)

    def _load_or_generate_key(self):
        """Load existing key or generate new one"""
        if Path(self.key_file).exists():
            with open(self.key_file, 'rb') as f:
                return f.read()
        else:
            key = Fernet.generate_key()
            with open(self.key_file, 'wb') as f:
                f.write(key)
            logger.info(f"Encryption key generated: {self.key_file}")
            return key

    def encrypt(self, data):
        """Encrypt data"""
        if isinstance(data, str):
            data = data.encode()
        encrypted = self.fernet.encrypt(data)
        return encrypted

    def decrypt(self, encrypted_data):
        """Decrypt data"""
        decrypted = self.fernet.decrypt(encrypted_data)
        return decrypted.decode()

    def encrypt_file(self, file_path):
        """Encrypt a file"""
        with open(file_path, 'rb') as f:
            data = f.read()
        encrypted = self.encrypt(data)
        encrypted_path = f"{file_path}.enc"
        with open(encrypted_path, 'wb') as f:
            f.write(encrypted)
        logger.info(f"File encrypted: {file_path} → {encrypted_path}")
        return encrypted_path

    def decrypt_file(self, encrypted_path):
        """Decrypt a file"""
        with open(encrypted_path, 'rb') as f:
            encrypted = f.read()
        decrypted = self.decrypt(encrypted)
        original_path = encrypted_path.replace('.enc', '')
        with open(original_path, 'w') as f:
            f.write(decrypted)
        logger.info(f"File decrypted: {encrypted_path} → {original_path}")
        return original_path

    def hash_data(self, data):
        """Create SHA-256 hash of data"""
        if isinstance(data, str):
            data = data.encode()
        return hashlib.sha256(data).hexdigest()

if __name__ == "__main__":
    encryption = ProductionEncryption()
    print("=== PRODUCTION ENCRYPTION MANAGER ===\n")
    
    # Test encryption
    test_data = "sensitive forensic evidence"
    encrypted = encryption.encrypt(test_data)
    print(f"Original: {test_data}")
    print(f"Encrypted: {encrypted[:50]}...")
    
    decrypted = encryption.decrypt(encrypted)
    print(f"Decrypted: {decrypted}")
    
    # Hash test
    hash_val = encryption.hash_data(test_data)
    print(f"Hash: {hash_val}")
