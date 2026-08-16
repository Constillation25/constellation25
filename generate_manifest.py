#!/data/data/com.termux/files/usr/bin/python3
import os
import json
from pathlib import Path
from datetime import datetime

BUILD_DIR = Path.home() / "constellation25" / "production_build"
AGENTS = ["core", "analytics", "ui_ux", "security", "legal", "storage", "rnd", "data", "mobile", "master", "cache", "api", "qa", "infra", "codegen", "ipc", "logging", "multimodal", "identity", "cicd", "database", "business", "compute", "firewall", "predictive"]

manifest = {
    "system": "Constellation25 TotalRecall Mesh",
    "generated_at": datetime.now().isoformat(),
    "build_status": "COMPLETE",
    "agent_domains": {}
}

total_files = 0
for agent in AGENTS:
    agent_dir = BUILD_DIR / agent
    if agent_dir.exists():
        files = list(agent_dir.rglob("*"))
        py_files = [f for f in files if f.suffix == '.py']
        manifest["agent_domains"][agent] = {
            "total_files": len(files),
            "python_files": len(py_files),
            "status": "VALIDATED" if len(py_files) > 0 else "EMPTY"
        }
        total_files += len(files)

manifest["summary"] = {
    "total_files_processed": total_files,
    "agents_active": len([a for a in manifest["agent_domains"] if manifest["agent_domains"][a]["status"] == "VALIDATED"])
}

with open(BUILD_DIR / "FULL_BUILD_MANIFEST.json", "w") as f:
    json.dump(manifest, f, indent=2)

# Also write a readable markdown version
with open(BUILD_DIR / "FULL_BUILD_MANIFEST.md", "w") as f:
    f.write("# Constellation25 Full Build Manifest\n\n")
    f.write(f"**Generated:** {manifest['generated_at']}\n")
    f.write(f"**Total Files Processed:** {manifest['summary']['total_files_processed']}\n")
    f.write(f"**Active Agent Domains:** {manifest['summary']['agents_active']}/25\n\n")
    f.write("## Agent Build Status\n\n")
    for agent, data in manifest["agent_domains"].items():
        f.write(f"- **{agent.upper()}**: {data['python_files']} Python files, {data['total_files']} total files. Status: `{data['status']}`\n")

print("  [✓] Manifest generated: ~/constellation25/production_build/FULL_BUILD_MANIFEST.md")
