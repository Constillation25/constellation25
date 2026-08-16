#!/data/data/com.termux/files/usr/bin/python3
"""
SSH Key Manager
Generate, store, and manage SSH key pairs (RSA, Ed25519, ECDSA)
Replaces PuTTY Key Generator with native Python implementation
"""
import os
import json
import time
import hashlib
import logging
from pathlib import Path
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s [SSH-KEYS] %(message)s')
logger = logging.getLogger(__name__)

class SSHKeyManager:
    """Manages SSH key generation and storage"""
    def __init__(self, keys_dir=None):
        self.keys_dir = keys_dir or str(Path.home() / "constellation25" / "config" / "ssh_keys")
        Path(self.keys_dir).mkdir(parents=True, exist_ok=True)
        self.index_file = f"{self.keys_dir}/index.json"
        self.keys = self._load_index()

    def _load_index(self):
        if Path(self.index_file).exists():
            with open(self.index_file, 'r') as f:
                return json.load(f)
        return {"keys": [], "created": datetime.now().isoformat()}

    def _save_index(self):
        with open(self.index_file, 'w') as f:
            json.dump(self.keys, f, indent=2)

    def generate_key(self, key_type="ed25519", bits=4096, comment="", passphrase=None):
        """
        Generate SSH key pair
        key_type: rsa, ed25519, ecdsa
        bits: key size (RSA only, default 4096)
        """
        import subprocess

        key_name = f"id_{key_type}_{int(time.time())}"
        private_key_path = f"{self.keys_dir}/{key_name}"
        public_key_path = f"{private_key_path}.pub"

        logger.info(f"Generating {key_type.upper()} key ({bits} bits)...")

        # Use ssh-keygen for actual key generation
        cmd = ["ssh-keygen", "-t", key_type]
        if key_type == "rsa":
            cmd.extend(["-b", str(bits)])
        cmd.extend(["-f", private_key_path, "-N", passphrase or "", "-C", comment or "c25-sovereign"])

        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                # Read public key
                with open(public_key_path, 'r') as f:
                    public_key = f.read().strip()

                # Calculate fingerprint
                fingerprint = self._calculate_fingerprint(public_key_path)

                key_entry = {
                    "name": key_name,
                    "type": key_type,
                    "bits": bits if key_type == "rsa" else (256 if key_type == "ed25519" else 256),
                    "comment": comment,
                    "fingerprint": fingerprint,
                    "public_key_path": public_key_path,
                    "private_key_path": private_key_path,
                    "created": datetime.now().isoformat(),
                    "has_passphrase": bool(passphrase)
                }

                self.keys["keys"].append(key_entry)
                self._save_index()

                logger.info(f"Key generated: {key_name}")
                logger.info(f"Fingerprint: {fingerprint}")
                return key_entry
            else:
                logger.error(f"Key generation failed: {result.stderr}")
                return None

        except Exception as e:
            logger.error(f"Error generating key: {e}")
            return None

    def _calculate_fingerprint(self, public_key_path):
        """Calculate SHA256 fingerprint of public key"""
        import subprocess
        try:
            result = subprocess.run(
                ["ssh-keygen", "-lf", public_key_path],
                capture_output=True, text=True
            )
            if result.returncode == 0:
                # Extract fingerprint from output like: "4096 SHA256:xxx comment (RSA)"
                parts = result.stdout.strip().split()
                return parts[1] if len(parts) > 1 else "unknown"
        except:
            pass
        return "unknown"

    def list_keys(self):
        """List all managed keys"""
        return self.keys["keys"]

    def get_key(self, key_name):
        """Get specific key by name"""
        for key in self.keys["keys"]:
            if key["name"] == key_name:
                return key
        return None

    def delete_key(self, key_name):
        """Delete a key pair"""
        key = self.get_key(key_name)
        if not key:
            return False

        # Delete files
        try:
            os.remove(key["private_key_path"])
            os.remove(key["public_key_path"])
        except:
            pass

        # Remove from index
        self.keys["keys"] = [k for k in self.keys["keys"] if k["name"] != key_name]
        self._save_index()

        logger.info(f"Key deleted: {key_name}")
        return True

    def export_public_key(self, key_name):
        """Export public key for adding to servers"""
        key = self.get_key(key_name)
        if not key:
            return None

        try:
            with open(key["public_key_path"], 'r') as f:
                return f.read().strip()
        except:
            return None

    def add_to_authorized_keys(self, key_name, target_file=None):
        """Add public key to authorized_keys file"""
        public_key = self.export_public_key(key_name)
        if not public_key:
            return False

        target = target_file or str(Path.home() / ".ssh" / "authorized_keys")
        Path(target).parent.mkdir(parents=True, exist_ok=True)

        try:
            with open(target, 'a') as f:
                f.write(f"\n# C25 Key: {key_name}\n{public_key}\n")
            logger.info(f"Key added to {target}")
            return True
        except Exception as e:
            logger.error(f"Failed to add key: {e}")
            return False

if __name__ == "__main__":
    import sys

    manager = SSHKeyManager()

    if len(sys.argv) > 1:
        cmd = sys.argv[1]

        if cmd == "generate":
            key_type = sys.argv[2] if len(sys.argv) > 2 else "ed25519"
            bits = int(sys.argv[3]) if len(sys.argv) > 3 else 4096
            comment = sys.argv[4] if len(sys.argv) > 4 else "c25-sovereign"
            result = manager.generate_key(key_type, bits, comment)
            if result:
                print(json.dumps(result, indent=2))

        elif cmd == "list":
            keys = manager.list_keys()
            print(json.dumps(keys, indent=2))

        elif cmd == "delete" and len(sys.argv) > 2:
            manager.delete_key(sys.argv[2])
            print(f"Key deleted: {sys.argv[2]}")

        elif cmd == "export" and len(sys.argv) > 2:
            pub_key = manager.export_public_key(sys.argv[2])
            if pub_key:
                print(pub_key)

        else:
            print("Usage:")
            print("  python3 key_manager.py generate [type] [bits] [comment]")
            print("  python3 key_manager.py list")
            print("  python3 key_manager.py delete <key_name>")
            print("  python3 key_manager.py export <key_name>")
    else:
        print("=== SSH KEY MANAGER DEMO ===\n")

        # Generate Ed25519 key (modern, secure)
        print("1. Generating Ed25519 key:")
        key1 = manager.generate_key("ed25519", comment="c25-primary")
        if key1:
            print(f"   Name: {key1['name']}")
            print(f"   Type: {key1['type']}")
            print(f"   Fingerprint: {key1['fingerprint']}\n")

        # Generate RSA 4096 key
        print("2. Generating RSA 4096-bit key:")
        key2 = manager.generate_key("rsa", 4096, comment="c25-legacy")
        if key2:
            print(f"   Name: {key2['name']}")
            print(f"   Type: {key2['type']}")
            print(f"   Bits: {key2['bits']}")
            print(f"   Fingerprint: {key2['fingerprint']}\n")

        # List all keys
        print("3. All managed keys:")
        for key in manager.list_keys():
            print(f"   - {key['name']} ({key['type']}, {key['fingerprint']})")

        print("\n=== SSH KEY TYPES ===")
        print("Ed25519: Modern, fast, secure (recommended)")
        print("RSA 4096: Legacy compatibility, widely supported")
        print("ECDSA: NIST standard, good balance")
