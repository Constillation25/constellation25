#!/data/data/com.termux/files/usr/bin/python3
"""
SovereignGTP Master Module Registry
Maps ALL build artifacts to their responsible agents and execution paths.
Every artifact in the ecosystem is a callable module.
"""

import json
import os
import subprocess
import sys
from pathlib import Path
from datetime import datetime

BASE = Path.home() / "constellation25"
IPC_PENDING = Path.home() / "c25_ipc" / "pending"
IPC_COMPLETED = Path.home() / "c25_ipc" / "completed"
BIOAUTH = BASE / "modules" / "bioauth" / "bioauth.py"

# ============================================================
# MASTER MODULE REGISTRY
# Every artifact mapped to its agent, path, and auth requirement
# ============================================================

MODULES = {
    # --- CORE ORCHESTRATION (Earth Agent) ---
    "orchestrator": {
        "agent": "earth",
        "path": str(BASE / "c25_orchestrator.py"),
        "description": "25-agent orchestration daemon",
        "requires_bioauth": False,
        "category": "core"
    },
    "stalker_watchdog": {
        "agent": "earth",
        "path": str(BASE / "stalker_global.sh"),
        "description": "System watchdog and auto-restart",
        "requires_bioauth": False,
        "category": "core"
    },
    "task_box": {
        "agent": "earth",
        "path": str(BASE / "task_box.sh"),
        "description": "Interactive task routing interface",
        "requires_bioauth": False,
        "category": "core"
    },
    "start_all_agents": {
        "agent": "earth",
        "path": str(BASE / "start_all_agents.sh"),
        "description": "Launch all 25 planetary agents",
        "requires_bioauth": True,
        "category": "core"
    },
    "stop_all_agents": {
        "agent": "earth",
        "path": str(BASE / "stop_all_agents.sh"),
        "description": "Graceful shutdown of all agents",
        "requires_bioauth": True,
        "category": "core"
    },

    # --- DEPLOYMENT (Mars Agent) ---
    "deploy_unified": {
        "agent": "mars",
        "path": str(BASE / "tools/1bash_deploy_all.sh"),
        "description": "Ultimate 1BASH deploy all artifacts",
        "requires_bioauth": True,
        "category": "deployment"
    },
    "deploy_vercel": {
        "agent": "mars",
        "path": str(BASE / "tools/vercel_deploy.sh"),
        "description": "Vercel production deployment",
        "requires_bioauth": True,
        "category": "deployment"
    },
    "deploy_cloudflare": {
        "agent": "mars",
        "path": str(BASE / "tools/cloudflare_deploy.sh"),
        "description": "Cloudflare Workers deployment",
        "requires_bioauth": True,
        "category": "deployment"
    },
    "bio_push_github": {
        "agent": "mars",
        "path": str(BASE / "tools/c25-bio-push/main.sh"),
        "description": "Biometric-authorized GitHub push",
        "requires_bioauth": True,
        "category": "deployment"
    },
    "nuclear_repo_recreate": {
        "agent": "mars",
        "path": str(BASE / "tools/nuclear_repo_recreate.sh"),
        "description": "Emergency repository rebuild",
        "requires_bioauth": True,
        "category": "deployment"
    },

    # --- SECURITY (Vesta Agent) ---
    "bioauth_gate": {
        "agent": "vesta",
        "path": str(BIOAUTH),
        "description": "Biometric authentication gate",
        "requires_bioauth": False,
        "category": "security"
    },
    "faceprintpay_auth": {
        "agent": "vesta",
        "path": str(BASE / "modules/faceprintpay/auth.py"),
        "description": "FacePrintPay biometric verification",
        "requires_bioauth": False,
        "category": "security"
    },
    "sovereign_vault": {
        "agent": "vesta",
        "path": str(BASE / "tools/sovereignvault_manager.sh"),
        "description": "SovereignVault encryption and storage",
        "requires_bioauth": True,
        "category": "security"
    },
    "precommit_security": {
        "agent": "vesta",
        "path": str(BASE / "tools/precommit_security_check.sh"),
        "description": "Pre-commit credential leak scanner",
        "requires_bioauth": False,
        "category": "security"
    },
    "secret_file_scanner": {
        "agent": "vesta",
        "path": str(BASE / "tools/find_remove_secrets.sh"),
        "description": "Find and remove exposed secrets",
        "requires_bioauth": False,
        "category": "security"
    },

    # --- FORENSICS (Neptune Agent) ---
    "totalrecall_engine": {
        "agent": "neptune",
        "path": str(BASE / "modules/totalrecall/engine.py"),
        "description": "TotalRecall forensic analysis engine",
        "requires_bioauth": True,
        "category": "forensics"
    },
    "videocourts_analysis": {
        "agent": "neptune",
        "path": str(BASE / "modules/videocourts/analyze.py"),
        "description": "VideoCourts forensic video analysis",
        "requires_bioauth": True,
        "category": "forensics"
    },
    "blockchain_evidence": {
        "agent": "neptune",
        "path": str(BASE / "tools/blockchain_evidence_pipeline.sh"),
        "description": "Blockchain evidence pipeline",
        "requires_bioauth": True,
        "category": "forensics"
    },
    "forensic_file_analysis": {
        "agent": "neptune",
        "path": str(BASE / "tools/forensic_file_analysis.py"),
        "description": "File forensic analysis and hashing",
        "requires_bioauth": False,
        "category": "forensics"
    },
    "data_wipe_detector": {
        "agent": "neptune",
        "path": str(BASE / "tools/data_wipe_detector.sh"),
        "description": "Detect unauthorized data deletion",
        "requires_bioauth": True,
        "category": "forensics"
    },

    # --- COMMERCE (Jupiter Agent) ---
    "mybuyo_engine": {
        "agent": "jupiter",
        "path": str(BASE / "modules/mybuyo/engine.py"),
        "description": "MyBuyo commerce and payment engine",
        "requires_bioauth": True,
        "category": "commerce"
    },
    "yesquidpro_exchange": {
        "agent": "jupiter",
        "path": str(BASE / "modules/yesquidpro/exchange.py"),
        "description": "YesQuidPro barter and trade platform",
        "requires_bioauth": False,
        "category": "commerce"
    },
    "stripe_webhook": {
        "agent": "jupiter",
        "path": str(BASE / "modules/stripe/webhook_handler.py"),
        "description": "Stripe payment webhook processor",
        "requires_bioauth": True,
        "category": "commerce"
    },

    # --- COMMUNICATIONS (Moon Agent) ---
    "commz_mesh": {
        "agent": "moon",
        "path": str(BASE / "modules/commz/mesh.py"),
        "description": "Commz encrypted mesh messaging",
        "requires_bioauth": False,
        "category": "communications"
    },

    # --- CREATIVE (Venus Agent) ---
    "artifactly_deploy": {
        "agent": "venus",
        "path": str(BASE / "modules/artifactly/deploy.py"),
        "description": "Artifactly artifact deployment engine",
        "requires_bioauth": False,
        "category": "creative"
    },
    "ai_creative_studio": {
        "agent": "venus",
        "path": str(BASE / "modules/creative/studio.py"),
        "description": "AI Creative Studio multi-modal generation",
        "requires_bioauth": False,
        "category": "creative"
    },

    # --- DATA & BACKUP (Saturn Agent) ---
    "r2_backup": {
        "agent": "saturn",
        "path": str(BASE / "tools/cloudflare_r2_backup.sh"),
        "description": "Cloudflare R2 backup system",
        "requires_bioauth": True,
        "category": "backup"
    },
    "obsidian_sync": {
        "agent": "saturn",
        "path": str(BASE / "tools/obsidian_sync.sh"),
        "description": "Obsidian vault synchronization",
        "requires_bioauth": False,
        "category": "backup"
    },
    "storage_cleanup": {
        "agent": "saturn",
        "path": str(BASE / "tools/storage_cleanup.sh"),
        "description": "Storage analysis and cleanup",
        "requires_bioauth": False,
        "category": "backup"
    },
    "file_inventory": {
        "agent": "saturn",
        "path": str(BASE / "tools/forensic_inventory.sh"),
        "description": "316K file inventory and audit",
        "requires_bioauth": False,
        "category": "backup"
    },

    # --- NLP & CODE (Mercury Agent) ---
    "nlp2code": {
        "agent": "mercury",
        "path": str(BASE / "modules/nlp2code/orchestrator.py"),
        "description": "NLP2CODE natural language to code engine",
        "requires_bioauth": False,
        "category": "nlp"
    },
    "pathos_engine": {
        "agent": "mercury",
        "path": str(BASE / "modules/pathos/engine.py"),
        "description": "PaTHos NLP programming language engine",
        "requires_bioauth": False,
        "category": "nlp"
    },

    # --- HEALTH & MONITORING (Hygiea Agent) ---
    "health_monitor": {
        "agent": "hygiea",
        "path": str(BASE / "tools/health_monitor.sh"),
        "description": "System health monitoring daemon",
        "requires_bioauth": False,
        "category": "monitoring"
    },
    "agent_status": {
        "agent": "hygiea",
        "path": str(BASE / "status_agents.sh"),
        "description": "Agent status and diagnostics",
        "requires_bioauth": False,
        "category": "monitoring"
    },
    "system_diagnostic": {
        "agent": "hygiea",
        "path": str(BASE / "tools/system_diagnostic.sh"),
        "description": "Full system diagnostic and recovery",
        "requires_bioauth": False,
        "category": "monitoring"
    }
}

def list_modules(category=None):
    """List all registered modules, optionally filtered by category."""
    results = {}
    for name, mod in MODULES.items():
        if category is None or mod["category"] == category:
            results[name] = mod
    return results

def get_module(name):
    """Get a specific module by name."""
    return MODULES.get(name)

def execute_module(name, args=None, skip_bioauth=False):
    """
    Execute a registered module.
    Checks BioAuth if required before execution.
    """
    mod = get_module(name)
    if not mod:
        return {"success": False, "error": f"Module '{name}' not found"}

    # BioAuth gate
    if mod["requires_bioauth"] and not skip_bioauth:
        print(f"[BioAuth] Module '{name}' requires biometric authorization...")
        bio_result = subprocess.run(
            [sys.executable, str(BIOAUTH), "verify", f"Execute module: {name}"],
            capture_output=True, text=True
        )
        try:
            auth_data = json.loads(bio_result.stdout)
            if not auth_data.get("verified"):
                return {"success": False, "error": "BioAuth denied"}
        except:
            if "AUTH_RESULT_SUCCESS" not in bio_result.stdout:
                return {"success": False, "error": "BioAuth verification failed"}

    # Execute
    cmd = ["bash", mod["path"]] if mod["path"].endswith(".sh") else [sys.executable, mod["path"]]
    if args:
        cmd.extend(args)

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        return {
            "success": result.returncode == 0,
            "output": result.stdout,
            "error": result.stderr if result.returncode != 0 else None,
            "module": name,
            "agent": mod["agent"]
        }
    except subprocess.TimeoutExpired:
        return {"success": False, "error": "Module execution timed out", "module": name}
    except Exception as e:
        return {"success": False, "error": str(e), "module": name}

def queue_task(module_name, agent=None, args=None):
    """Queue a module execution task for the orchestrator."""
    mod = get_module(module_name)
    if not mod:
        return False

    import time
    task = {
        "agent": agent or mod["agent"],
        "action": f"execute_module:{module_name}",
        "module": module_name,
        "command": mod["path"],
        "args": args or [],
        "requires_bioauth": mod["requires_bioauth"],
        "priority": "high" if mod["requires_bioauth"] else "normal",
        "created": datetime.now().isoformat(),
        "status": "pending"
    }

    IPC_PENDING.mkdir(parents=True, exist_ok=True)
    task_file = IPC_PENDING / f"{mod['agent']}_{module_name}_{int(time.time())}.json"
    with open(task_file, "w") as f:
        json.dump(task, f, indent=2)

    return str(task_file)

# CLI
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("SovereignGTP Module Registry")
        print(f"Total modules: {len(MODULES)}")
        print(f"Categories: {', '.join(set(m['category'] for m in MODULES.values()))}")
        print("\nUsage:")
        print("  python3 module_registry.py list [category]")
        print("  python3 module_registry.py run <module_name>")
        print("  python3 module_registry.py queue <module_name>")
        sys.exit(0)

    action = sys.argv[1]

    if action == "list":
        cat = sys.argv[2] if len(sys.argv) > 2 else None
        mods = list_modules(cat)
        for name, mod in mods.items():
            bio = "🔒" if mod["requires_bioauth"] else "  "
            print(f"  {bio} [{mod['agent']:8s}] {name:30s} - {mod['description']}")

    elif action == "run" and len(sys.argv) > 2:
        result = execute_module(sys.argv[2], sys.argv[3:])
        print(json.dumps(result, indent=2))

    elif action == "queue" and len(sys.argv) > 2:
        task_file = queue_task(sys.argv[2])
        if task_file:
            print(f"✅ Task queued: {task_file}")
        else:
            print(f"❌ Module not found: {sys.argv[2]}")
