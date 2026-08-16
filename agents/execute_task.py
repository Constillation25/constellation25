#!/data/data/com.termux/files/usr/bin/python3
"""Agent Task Executor with BioAuth Gate"""
import sys, json, subprocess, os
from pathlib import Path

IPC_COMPLETED = Path.home() / "c25_ipc" / "completed"
IPC_COMPLETED.mkdir(parents=True, exist_ok=True)

def log(msg):
    print(f"[EXECUTOR] {msg}")

def request_human_auth(prompt_message):
    log(f"🔒 REQUESTING HUMAN AUTH: {prompt_message}")
    dialog_result = subprocess.run(["termux-dialog", "confirm", "-t", "Agent Authorization", "-i", prompt_message], capture_output=True, text=True)
    try:
        data = json.loads(dialog_result.stdout)
        if data.get("text") != "yes":
            log("❌ User denied permission.")
            subprocess.run(["termux-toast", "❌ Permission denied by user."])
            return False
    except:
        log("❌ Dialog failed or canceled.")
        return False

    log("👉 Prompting for fingerprint...")
    subprocess.run(["termux-toast", "🔒 Scan finger to authorize agent action..."])
    bio_result = subprocess.run(["termux-fingerprint", "-d", "Authorize Agent Action"], capture_output=True, text=True, timeout=45)
    
    try:
        data = json.loads(bio_result.stdout)
        if data.get("auth_result") == "AUTH_RESULT_SUCCESS":
            log("✅ Biometric verification SUCCESS")
            subprocess.run(["termux-toast", "✅ Authorized. Executing task..."])
            return True
        else:
            log("❌ Biometric verification FAILED")
            subprocess.run(["termux-toast", "❌ Fingerprint scan failed."])
            return False
    except:
        if "AUTH_RESULT_SUCCESS" in bio_result.stdout:
            log("✅ Biometric verification SUCCESS (fallback)")
            return True
        log("❌ Biometric verification FAILED (fallback)")
        return False

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 execute_task.py <task_file.json>")
        sys.exit(1)
    
    task_file = sys.argv[1]
    try:
        with open(task_file) as f:
            task = json.load(f)
    except Exception as e:
        log(f"❌ Failed to read task file: {e}")
        sys.exit(1)
    
    agent = task.get("agent", "unknown")
    action = task.get("action", task.get("task", "unknown_action"))
    command = task.get("command", "")
    requires_bio = task.get("requires_bioauth", False)
    tracking_id = task.get("_tracking_id", "")
    
    log(f"Processing task for [{agent.upper()}]: {action}")
    
    if requires_bio:
        prompt = f"Agent '{agent}' requests to: {action}. Allow execution?"
        if not request_human_auth(prompt):
            log("❌ Task ABORTED due to failed BioAuth.")
            task['_result'] = 'BioAuth failed - user denied or scan failed'
            task['_status'] = 'failed'
            completed_file = IPC_COMPLETED / f"{tracking_id}.json"
            with open(completed_file, 'w') as f:
                json.dump(task, f, indent=2)
            sys.exit(1)
    
    if command:
        log(f"⚙️ Executing: {command}")
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            output = result.stdout.strip() if result.stdout else "Command executed"
            if result.returncode == 0:
                log(f"✅ Task completed successfully.")
                task['_result'] = f"✅ Success: {output}"
                task['_status'] = 'completed'
            else:
                log(f"⚠️ Task finished with errors (code {result.returncode}).")
                task['_result'] = f"⚠️ Error (code {result.returncode}): {result.stderr.strip()}"
                task['_status'] = 'error'
        except Exception as e:
            log(f"❌ Execution failed: {e}")
            task['_result'] = f"❌ Execution failed: {str(e)}"
            task['_status'] = 'failed'
    else:
        log("ℹ️ No command specified in task. Marking as complete.")
        task['_result'] = "ℹ️ No command specified"
        task['_status'] = 'completed'
    
    completed_file = IPC_COMPLETED / f"{tracking_id}.json"
    with open(completed_file, 'w') as f:
        json.dump(task, f, indent=2)
    log(f"✅ Task status written to: {completed_file}")

if __name__ == "__main__":
    main()
