#!/data/data/com.termux/files/usr/bin/python3
"""TotalRecall - Forensic Evidence Vault & Immutable Ledger"""
import hashlib, json, os, sys, time
from pathlib import Path

VAULT_DIR = Path.home() / "constellation25" / "vault" / "totalrecall"
LEDGER = VAULT_DIR / "ledger.json"

def init_vault():
    VAULT_DIR.mkdir(parents=True, exist_ok=True)
    if not LEDGER.exists():
        with open(LEDGER, "w") as f: json.dump([], f)

def hash_file(filepath):
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""): h.update(chunk)
    return h.hexdigest()

def seal_evidence(filepath):
    init_vault()
    file_hash = hash_file(filepath)
    entry = {
        "file": str(filepath),
        "sha256": file_hash,
        "timestamp": time.time(),
        "status": "SEALED"
    }
    with open(LEDGER, "r+") as f:
        ledger = json.load(f)
        ledger.append(entry)
        f.seek(0)
        json.dump(ledger, f, indent=2)
    print(f"[TotalRecall] ✅ Evidence sealed: {file_hash[:16]}...")
    return entry

if __name__ == "__main__":
    if len(sys.argv) > 1:
        seal_evidence(sys.argv[1])
    else:
        print("Usage: python3 engine.py <file_to_seal>")
