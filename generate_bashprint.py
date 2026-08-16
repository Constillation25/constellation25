#!/data/data/com.termux/files/usr/bin/python3
"""
Termux Bashprint Generator
Dumps bash history into structured JSON/MD for Agent analysis and auto-correction.
"""
import os
import json
import re
from pathlib import Path
from datetime import datetime

HISTORY_FILE = Path.home() / ".bash_history"
OUTPUT_JSON = Path.home() / "constellation25" / "logs" / "bashprint.json"
OUTPUT_MD = Path.home() / "constellation25" / "logs" / "bashprint.md"

def analyze_command(cmd):
    """Categorize and assess command complexity/intent"""
    cmd = cmd.strip()
    if not cmd or cmd.startswith('#'):
        return None
    
    category = "general"
    complexity = "low"
    notes = []
    
    # Intent categorization
    if cmd.startswith(('git ', 'gh ')): category = "version_control"
    elif cmd.startswith(('python3 ', 'python ')): category = "execution_build"
    elif cmd.startswith(('pkg ', 'apt ', 'termux-setup-storage')): category = "package_management"
    elif cmd.startswith(('mkdir ', 'rm ', 'cp ', 'mv ', 'find ', 'cat ')): category = "file_operations"
    elif cmd.startswith('cd '): category = "navigation"
    elif cmd.startswith('bash ') or cmd.endswith('.sh'): category = "script_execution"
    
    # Complexity / Failure Risk Detection
    if '&&' in cmd or '||' in cmd: 
        complexity = "high"
        notes.append("Chained command (high failure risk if prior step fails)")
    if '|' in cmd: 
        complexity = "medium"
        notes.append("Uses piping")
    if '<<' in cmd or 'EOF' in cmd: 
        complexity = "high"
        notes.append("Heredoc block (prone to terminal paste truncation)")
    if 'rm -rf' in cmd: 
        complexity = "high"
        notes.append("Destructive operation")
    if 'out of diskspace' in cmd.lower() or 'error' in cmd.lower():
        notes.append("Historical failure indicator")

    return {
        "command": cmd,
        "category": category,
        "complexity": complexity,
        "notes": notes,
        "agent_action": f"Agent should verify syntax and dependencies for this {category} command."
    }

def main():
    if not HISTORY_FILE.exists():
        print(f"[!] History file not found at {HISTORY_FILE}")
        return

    with open(HISTORY_FILE, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()

    # Deduplicate and reverse to get chronological order (oldest to newest)
    seen = set()
    unique_commands = []
    for line in reversed(lines):
        cmd = line.strip()
        if cmd and cmd not in seen:
            seen.add(cmd)
            unique_commands.append(cmd)
    
    unique_commands.reverse() # Back to chronological

    parsed_history = []
    stats = {"total": 0, "high_complexity": 0, "categories": {}}

    print(f"[*] Analyzing {len(unique_commands)} unique commands...")
    
    for cmd in unique_commands:
        analysis = analyze_command(cmd)
        if analysis:
            parsed_history.append(analysis)
            stats["total"] += 1
            stats["categories"][analysis["category"]] = stats["categories"].get(analysis["category"], 0) + 1
            if analysis["complexity"] == "high":
                stats["high_complexity"] += 1

    # Write JSON
    payload = {
        "generated_at": datetime.now().isoformat(),
        "system": "Termux Constellation25",
        "stats": stats,
        "history": parsed_history
    }
    
    with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
        json.dump(payload, f, indent=2)

    # Write Markdown (Agent-readable summary)
    with open(OUTPUT_MD, 'w', encoding='utf-8') as f:
        f.write("# Constellation25 Termux Bashprint\n\n")
        f.write(f"**Generated:** {payload['generated_at']}\n")
        f.write(f"**Total Unique Commands:** {stats['total']}\n")
        f.write(f"**High Complexity / Risk Commands:** {stats['high_complexity']}\n\n")
        
        f.write("## Category Breakdown\n")
        for cat, count in stats["categories"].items():
            f.write(f"- **{cat.replace('_', ' ').title()}**: {count}\n")
        
        f.write("\n## High-Risk / Complex Commands (Agent Review Required)\n")
        high_risk = [h for h in parsed_history if h["complexity"] == "high"]
        for h in high_risk[-20:]: # Last 20 high risk
            f.write(f"- `{h['command']}`\n")
            for note in h['notes']:
                f.write(f"  - ⚠️ *{note}*\n")
        
        f.write("\n---\n*Agents can parse this file to auto-correct failed bash syntax, suggest missing `pkg install` dependencies, and align with the user's historical build intent.*\n")

    print(f"[✓] Bashprint generated successfully.")
    print(f"  JSON: {OUTPUT_JSON}")
    print(f"  MD:   {OUTPUT_MD}")

if __name__ == "__main__":
    main()
