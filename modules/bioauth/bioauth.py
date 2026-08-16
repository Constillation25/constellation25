#!/data/data/com.termux/files/usr/bin/python3
"""BioAuth - Biometric Authorization Gate"""
import subprocess, json, hashlib, time, os, sys
from datetime import datetime

TOKEN_STORE = os.path.expanduser("~/.c25_bioauth_token.json")
LOG_FILE = os.path.expanduser("~/c25_logs/bioauth.log")

def log(msg):
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a") as f:
        f.write(f"[{timestamp}] {msg}\n")
    print(msg)

def verify_biometric(reason="Authorize action"):
    log(f"[BioAuth] Requesting biometric: {reason}")
    try:
        result = subprocess.run(["termux-fingerprint", "-d", reason], capture_output=True, text=True, timeout=45)
        output = result.stdout.strip()
        try:
            data = json.loads(output)
            if data.get("auth_result") == "AUTH_RESULT_SUCCESS":
                log("[BioAuth] ✓ Biometric verification SUCCESS")
                return True
            else:
                log(f"[BioAuth] ✗ Biometric verification FAILED: {output}")
                return False
        except json.JSONDecodeError:
            if "success" in output.lower() or "AUTH_RESULT_SUCCESS" in output:
                log("[BioAuth] ✓ Biometric verification SUCCESS (fallback)")
                return True
            log(f"[BioAuth] ✗ Biometric verification FAILED: {output}")
            return False
    except subprocess.TimeoutExpired:
        log("[BioAuth] ✗ Biometric prompt timed out")
        return False
    except FileNotFoundError:
        log("[BioAuth] ✗ 'termux-fingerprint' not found. Run: pkg install termux-api")
        return False

def generate_token(action):
    timestamp = int(time.time())
    expires = timestamp + 300
    payload = {"action": action, "issued": timestamp, "expires": expires}
    raw = f"{action}:{timestamp}:{expires}:c25_master_secret"
    signature = hashlib.sha256(raw.encode()).hexdigest()[:16]
    token = {"payload": payload, "signature": signature, "token_string": f"BIOAUTH:{signature}:{expires}"}
    os.makedirs(os.path.dirname(TOKEN_STORE), exist_ok=True)
    with open(TOKEN_STORE, "w") as f:
        json.dump(token, f, indent=2)
    log(f"[BioAuth] Token generated for: {action} (expires in 300s)")
    return token

def validate_token():
    if not os.path.exists(TOKEN_STORE):
        return False
    with open(TOKEN_STORE) as f:
        token = json.load(f)
    if time.time() > token["payload"]["expires"]:
        log("[BioAuth] Token expired")
        os.remove(TOKEN_STORE)
        return False
    return True

def authorize(action):
    if validate_token():
        log(f"[BioAuth] Using existing valid token for: {action}")
        with open(TOKEN_STORE) as f:
            return json.load(f)
    if not verify_biometric(f"Authorize: {action}"):
        log(f"[BioAuth] Authorization DENIED for: {action}")
        return None
    return generate_token(action)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 bioauth.py <verify|authorize> [action]")
        sys.exit(1)
    action = sys.argv[1]
    target = sys.argv[2] if len(sys.argv) > 2 else "global"
    if action == "verify":
        result = verify_biometric("Test Verification")
        print(json.dumps({"verified": result}))
    else:
        token = authorize(f"{action}:{target}")
        print(json.dumps({"authorized": token is not None, "action": f"{action}:{target}"}))
