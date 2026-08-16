#!/data/data/com.termux/files/usr/bin/python3
"""Human-in-the-Loop Authorizer"""
import subprocess, json, sys, os

def log(msg):
    print(f"[HumanAuth] {msg}")

def request_permission(prompt_message):
    log(f"Asking: {prompt_message}")
    result = subprocess.run(["termux-dialog", "confirm", "-t", "Agent Request", "-i", prompt_message], capture_output=True, text=True)
    try:
        data = json.loads(result.stdout)
        return data.get("text") == "yes"
    except:
        return False

def verify_biometric(action_name):
    log(f"Requesting biometric for: {action_name}")
    subprocess.run(["termux-toast", f"🔒 Scan finger to authorize: {action_name}"])
    result = subprocess.run(["termux-fingerprint", "-d", f"Authorize: {action_name}"], capture_output=True, text=True, timeout=45)
    try:
        data = json.loads(result.stdout)
        return data.get("auth_result") == "AUTH_RESULT_SUCCESS"
    except:
        return "AUTH_RESULT_SUCCESS" in result.stdout

def main():
    if len(sys.argv) < 3:
        print("Usage: python3 human_auth.py '<question>' '<command_to_run>'")
        sys.exit(1)
    
    question = sys.argv[1]
    command = sys.argv[2]
    
    if not request_permission(question):
        log("❌ User denied permission. Agent task aborted.")
        subprocess.run(["termux-toast", "❌ Permission denied by user."])
        sys.exit(1)
    
    if not verify_biometric(question):
        log("❌ Biometric verification failed. Agent task aborted.")
        subprocess.run(["termux-toast", "❌ Fingerprint scan failed."])
        sys.exit(1)
    
    log("✅ Human authorized. Executing command...")
    subprocess.run(["termux-toast", "✅ Authorized. Executing..."])
    process = subprocess.run(command, shell=True, capture_output=False, text=True)
    
    if process.returncode == 0:
        log("✅ Task completed successfully.")
        subprocess.run(["termux-toast", "🚀 Task completed successfully!"])
    else:
        log(f"⚠️ Task finished with errors (code {process.returncode}).")
        subprocess.run(["termux-toast", "⚠️ Task finished with errors."])

if __name__ == "__main__":
    main()
