#!/data/data/com.termux/files/usr/bin/python3
"""
C25 CAPABILITY GATEWAY
Exposes fetch, read, do, and todo actions for the 25 Planetary Agents.
"""
import os
import sys
import json
import urllib.request
import subprocess
from pathlib import Path
from datetime import datetime

TODO_FILE = Path.home() / "c25_ipc" / "pending" / "master_todo.json"

def ensure_todo_file():
    TODO_FILE.parent.mkdir(parents=True, exist_ok=True)
    if not TODO_FILE.exists():
        with open(TODO_FILE, 'w') as f:
            json.dump([], f)

# ==============================================================================
# 1. FETCH CAPABILITY
# ==============================================================================
def fetch_data(target):
    """Fetch content from a URL or search query."""
    print(f"[GATEWAY] Fetching: {target}")
    if target.startswith('http'):
        try:
            req = urllib.request.Request(target, headers={'User-Agent': 'C25-Agent/1.0'})
            with urllib.request.urlopen(req, timeout=10) as response:
                return {"status": "success", "data": response.read()[:2000].decode('utf-8', errors='ignore')}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    else:
        return {"status": "info", "message": "Web search not yet configured. Use direct URLs."}

# ==============================================================================
# 2. READ CAPABILITY
# ==============================================================================
def read_file(filepath):
    """Read a file from Termux, Internal Storage, or Obsidian."""
    print(f"[GATEWAY] Reading: {filepath}")
    path = Path(filepath).expanduser()
    
    # Security check: prevent reading outside allowed zones
    allowed_roots = [Path.home(), Path.home() / "storage" / "shared"]
    if not any(str(path).startswith(str(root)) for root in allowed_roots):
        return {"status": "error", "message": "Access denied: Path outside allowed directories."}
    
    if not path.exists():
        return {"status": "error", "message": f"File not found: {filepath}"}
    
    try:
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        return {"status": "success", "data": content[:4000]} # Return first 4000 chars
    except Exception as e:
        return {"status": "error", "message": str(e)}

# ==============================================================================
# 3. DO CAPABILITY (Execute)
# ==============================================================================
def execute_task(script_path, args=""):
    """Safely execute a verified shell or python script."""
    print(f"[GATEWAY] Executing: {script_path} {args}")
    path = Path(script_path).expanduser()
    
    if not path.exists() or not path.is_file():
        return {"status": "error", "message": "Script not found."}
    
    try:
        # Determine command
        if str(path).endswith('.sh'):
            cmd = ['bash', str(path)] + args.split()
        elif str(path).endswith('.py'):
            cmd = ['python3', str(path)] + args.split()
        else:
            return {"status": "error", "message": "Unsupported script type."}
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60, cwd=str(path.parent))
        
        if result.returncode == 0:
            return {"status": "success", "stdout": result.stdout.strip(), "stderr": result.stderr.strip()}
        else:
            return {"status": "error", "exit_code": result.returncode, "stderr": result.stderr.strip()}
    except subprocess.TimeoutExpired:
        return {"status": "error", "message": "Execution timed out (60s limit)."}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# ==============================================================================
# 4. TODO CAPABILITY
# ==============================================================================
def manage_todo(action, task_details=""):
    """Add, list, or complete tasks in the master C25 queue."""
    ensure_todo_file()
    print(f"[GATEWAY] Todo Action: {action} | Details: {task_details}")
    
    with open(TODO_FILE, 'r') as f:
        try:
            todos = json.load(f)
        except:
            todos = []
    
    if action == "add":
        new_task = {
            "id": datetime.now().strftime("%Y%m%d%H%M%S"),
            "task": task_details,
            "status": "pending",
            "created": datetime.now().isoformat()
        }
        todos.append(new_task)
        with open(TODO_FILE, 'w') as f:
            json.dump(todos, f, indent=2)
        return {"status": "success", "message": f"Task added: {new_task['id']}"}
    
    elif action == "list":
        pending = [t for t in todos if t['status'] == 'pending']
        return {"status": "success", "data": pending}
    
    elif action == "complete":
        for t in todos:
            if t['id'] == task_details:
                t['status'] = 'completed'
                t['completed'] = datetime.now().isoformat()
                break
        with open(TODO_FILE, 'w') as f:
            json.dump(todos, f, indent=2)
        return {"status": "success", "message": f"Task {task_details} marked complete."}
    
    else:
        return {"status": "error", "message": "Invalid action. Use 'add', 'list', or 'complete'."}

# ==============================================================================
# INTERACTIVE CLI LOOP
# ==============================================================================
def main():
    print("╔════════════════════════════════════════════════════════════╗")
    print("║   C25 CAPABILITY GATEWAY ONLINE                          ║")
    print("║   Commands: fetch, read, do, todo, exit                  ║")
    print("╚════════════════════════════════════════════════════════════╝")
    
    while True:
        try:
            user_input = input("\n[C25-GATEWAY] > ").strip()
            if not user_input or user_input.lower() == 'exit':
                print("[GATEWAY] Shutting down.")
                break
            
            parts = user_input.split(maxsplit=1)
            command = parts[0].lower()
            args = parts[1] if len(parts) > 1 else ""
            
            if command == "fetch":
                result = fetch_data(args)
            elif command == "read":
                result = read_file(args)
            elif command == "do":
                script_args = args.split(maxsplit=1)
                result = execute_task(script_args[0], script_args[1] if len(script_args) > 1 else "")
            elif command == "todo":
                todo_parts = args.split(maxsplit=1)
                action = todo_parts[0] if todo_parts else "list"
                details = todo_parts[1] if len(todo_parts) > 1 else ""
                result = manage_todo(action, details)
            else:
                result = {"status": "error", "message": f"Unknown command: {command}"}
            
            print(json.dumps(result, indent=2))
            
        except KeyboardInterrupt:
            print("\n[GATEWAY] Interrupted. Shutting down.")
            break
        except Exception as e:
            print(json.dumps({"status": "error", "message": str(e)}))

if __name__ == "__main__":
    main()
