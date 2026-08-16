#!/data/data/com.termux/files/usr/bin/python3
"""
Constellation25 AI File Assistant
Reads a file, explains it, and suggests next steps.
Uses local Ollama if available, otherwise provides heuristic analysis.
"""
import sys
import os
import urllib.request
import json
from pathlib import Path

def read_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {e}"

def query_local_llm(prompt, model="llama3"):
    """Try to query local Ollama. Falls back gracefully if not running."""
    url = "http://localhost:11434/api/generate"
    data = {"model": model, "prompt": prompt, "stream": False}
    try:
        req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'), headers={'Content-Type': 'application/json'})
        with urllib.request.urlopen(req, timeout=30) as response:
            return json.loads(response.read())['response']
    except:
        return None

def analyze_file(filepath):
    print(f"\n{'='*60}")
    print(f" 📄 FILE: {filepath}")
    print(f"{'='*60}\n")
    
    content = read_file(filepath)
    if not content or len(content) < 10:
        print("⚠️ File is empty or unreadable.")
        return

    # Show first 500 chars for context
    print("👀 PREVIEW:")
    print(content[:500].replace('\n', ' ') + "...\n")

    # AI Prompt
    prompt = f"""You are the Constellation25 DevOps GuruCTO. 
    Analyze this file: {os.path.basename(filepath)}
    
    File content snippet:
    {content[:1500]}
    
    Provide a concise response with exactly these 3 sections:
    1. 🧠 EXPLANATION: What does this file do in 1-2 sentences?
    2. ⚠️ ISSUES: Any obvious bugs, missing imports, or security risks?
    3. 🚀 NEXT STEPS: 2 specific, actionable suggestions on what to build or fix next.
    """

    print("🤖 AI ANALYSIS:")
    ai_response = query_local_llm(prompt)
    
    if ai_response:
        print(ai_response)
    else:
        print("  [!] Local Ollama not detected. Running heuristic analysis...")
        print("  🧠 EXPLANATION: This is a local source file in the Constellation25 mesh.")
        if filepath.endswith('.py'):
            print("  ⚠️ ISSUES: Ensure all imports are relative to the totalrecall_mesh root.")
            print("  🚀 NEXT STEPS: 1. Run `python3 -m py_compile {filepath}` to validate syntax. 2. Add this file to the 25-agent build manifest.")
        elif filepath.endswith('.sh'):
            print("  ⚠️ ISSUES: Ensure it has `#!/data/data/com.termux/files/usr/bin/bash` at the top.")
            print("  🚀 NEXT STEPS: 1. Run `chmod +x {filepath}`. 2. Test execution in an isolated subshell.")
        print()

    print(f"{'='*60}\n")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 c25_assist.py <filepath>")
        print("Example: python3 c25_assist.py ~/constellation25/modules/totalrecall_mesh/orchestrator/orchestrator.py")
    else:
        analyze_file(sys.argv[1])
