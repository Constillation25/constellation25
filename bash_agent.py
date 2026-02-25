#!/usr/bin/env python3
"""
BashAgent (#25) — Generates deployable bash scripts from task descriptions.
Now with optional LLM integration for intelligent code generation.
FRAMEWORK PILLAR: Dynamic Assessment (intelligent code generation)
"""
import sys, os, json

# Try to use LLM for intelligent generation if available
USE_LLM = os.getenv("CONSTELLATION_USE_LLM", "false").lower() == "true"

def generate_with_llm(task):
    """Use LLM to generate bash script intelligently."""
    try:
        sys.path.insert(0, os.path.dirname(__file__))
        from llm_wrapper import LLMWrapper
        
        wrapper = LLMWrapper()
        prompt = f"""Generate a bash script to accomplish this task: {task}

Requirements:
- Include proper error handling (set -e)
- Add comments explaining each section
- Make it production-ready
- Output ONLY the bash script, no explanations

Task: {task}"""
        
        result = wrapper.call(prompt, max_tokens=2048, temperature=0.3)
        
        if result["success"]:
            # Extract just the script from response
            script = result["response"]
            # Remove markdown code fences if present
            script = script.replace("```bash", "").replace("```", "").strip()
            
            # Log the LLM call to Memoria
            try:
                from memoria import Memoria
                mem = Memoria()
                mem.log_llm_call(
                    agent="BashAgent",
                    model=result["model"],
                    provider=result["provider"],
                    prompt=prompt[:500],
                    response=script[:1000],
                    tokens=result.get("tokens", 0),
                    latency_ms=result.get("latency_ms", 0),
                    success=True
                )
            except Exception:
                pass
            
            return script
        else:
            # Fall back to template if LLM fails
            return generate_template(task)
    except Exception as e:
        print(f"[WARN] LLM generation failed: {e}", file=sys.stderr)
        return generate_template(task)

def generate_template(task):
    """Template-based script generation (fallback)."""
    t = task.lower()
    lines = [
        "#!/bin/bash",
        f"# BashAgent — Constellation-25",
        f"# Task: {task}",
        "set -e",
        "",
    ]
    if "videocourts" in t or "faceprintpay" in t:
        project = "videocourts" if "videocourts" in t else "faceprintpay"
        lines += [
            f'echo "[BashAgent] Building {project}..."',
            f"mkdir -p ~/{project}/{{src,public,api}}",
            f'echo "{project} scaffold created."',
        ]
    elif "install" in t or "setup" in t:
        lines += [
            'echo "[BashAgent] Running setup..."',
            "pkg install -y termux-api jq python nodejs 2>/dev/null || true",
            'echo "Setup complete."',
        ]
    elif "git" in t or "push" in t or "deploy" in t:
        lines += [
            'echo "[BashAgent] Git operations..."',
            "git add .",
            'git commit -m "Constellation-25 auto-commit $(date +%Y-%m-%d)" || true',
            "git push origin main || echo 'Push failed - check remote'",
        ]
    elif "test" in t:
        lines += [
            'echo "[BashAgent] Running tests..."',
            "cd ~/constellation-25",
            'echo "test" | python3 earth_agent.py | python3 -c "import sys,json; print(\'Tasks:\', len(json.load(sys.stdin)[\'tasks\']))"',
            'echo "Tests complete."',
        ]
    elif "backup" in t or "archive" in t:
        lines += [
            'echo "[BashAgent] Creating backup..."',
            'BACKUP="$HOME/backup_$(date +%Y%m%d_%H%M%S).tar.gz"',
            'tar -czf "$BACKUP" ~/constellation-25 ~/github-repos 2>/dev/null || true',
            'ls -lh "$BACKUP"',
            'echo "Backup complete."',
        ]
    else:
        lines += [
            f'echo "[BashAgent] Executing: {task}"',
            "# Add your commands below",
            'echo "Task completed."',
        ]
    
    lines.append("")
    return "\n".join(lines)

if __name__ == "__main__":
    task = " ".join(sys.argv[1:]).strip() or "generic execution"
    
    if USE_LLM:
        script = generate_with_llm(task)
    else:
        script = generate_template(task)
    
    print(script)
