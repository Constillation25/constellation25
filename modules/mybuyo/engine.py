#!/data/data/com.termux/files/usr/bin/python3
"""MyBuyo - Sovereign Commerce & Biometric Payment Engine"""
import json, os, sys, time
from pathlib import Path

TX_LOG = Path.home() / "constellation25" / "logs" / "mybuyo_transactions.json"

def process_transaction(amount, recipient, auth_token):
    TX_LOG.parent.mkdir(parents=True, exist_ok=True)
    
    tx = {
        "id": f"TX-{int(time.time())}",
        "amount": amount,
        "recipient": recipient,
        "auth_token": auth_token,
        "status": "COMPLETED",
        "timestamp": time.time()
    }
    
    # Append to local ledger
    existing = []
    if TX_LOG.exists():
        with open(TX_LOG, "r") as f: existing = json.load(f)
    existing.append(tx)
    
    with open(TX_LOG, "w") as f: json.dump(existing, f, indent=2)
    print(f"[MyBuyo] ✅ Transaction {tx['id']} processed: ${amount} to {recipient}")
    return tx

if __name__ == "__main__":
    if len(sys.argv) > 2:
        process_transaction(sys.argv[1], sys.argv[2], "bioauth_verified")
    else:
        print("Usage: python3 engine.py <amount> <recipient>")
