import hashlib
from cryptography.fernet import Fernet

class ZeroKnowledgeProxy:
    def __init__(self, customer_key: bytes):
        self.cipher = Fernet(customer_key)

    def encrypt_prompt(self, prompt: str) -> bytes:
        return self.cipher.encrypt(prompt.encode())

    def decrypt_completion(self, encrypted_data: bytes) -> str:
        return self.cipher.decrypt(encrypted_data).decode()

    def log_forensic_hash(self, data: str) -> str:
        # ZERO RETENTION: Only the SHA-256 hash touches the disk
        return hashlib.sha256(data.encode()).hexdigest()
