#!/data/data/com.termux/files/usr/bin/python3
"""Commz - Encrypted Mesh Messaging Protocol"""
import hashlib, base64, json, os, sys, time
from pathlib import Path

MESH_DIR = Path.home() / "constellation25" / "mesh" / "commz"

def encrypt_message(sender, receiver, content):
    MESH_DIR.mkdir(parents=True, exist_ok=True)
    
    # Simple XOR + Base64 encryption for local mesh (upgrade to AES in prod)
    key = hashlib.sha256(f"{sender}{receiver}".encode()).digest()
    content_bytes = content.encode('utf-8')
    encrypted = bytes([c ^ key[i % len(key)] for i, c in enumerate(content_bytes)])
    payload = base64.b64encode(encrypted).decode('utf-8')
    
    msg = {
        "id": f"MSG-{int(time.time())}",
        "from": sender,
        "to": receiver,
        "payload": payload,
        "timestamp": time.time()
    }
    
    outfile = MESH_DIR / f"{msg['id']}.json"
    with open(outfile, "w") as f: json.dump(msg, f)
    print(f"[Commz] ✅ Message encrypted and queued for {receiver}")
    return msg

if __name__ == "__main__":
    if len(sys.argv) > 2:
        encrypt_message("local_node", sys.argv[1], sys.argv[2])
    else:
        print("Usage: python3 mesh.py <receiver_id> <message>")
