#!/data/data/com.termux/files/usr/bin/python3
"""
TotalRecall Mesh Orchestrator - 25 AGENT BUILD MODE
Reads TotalRecall blueprint and dispatches to 25 Planetary Agents to build the ecosystem.
"""
import sys
import os
import json
import time
import logging
from pathlib import Path
from datetime import datetime

# FIX: Add parent directories to path so imports work
MESH_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(MESH_DIR))

logging.basicConfig(level=logging.INFO, format='%(asctime)s [TR-ORCH] %(message)s')
logger = logging.getLogger(__name__)

# Import the 25 Agents
from agents.planetary_agents import get_25_agents

class TotalRecallOrchestrator:
    def __init__(self):
        self.agents = get_25_agents()
        self.orchestrator_id = f"orch-{int(time.time())}"
        self.started_at = datetime.now().isoformat()
        self.base_build_dir = Path.home() / "constellation25" / "production_build"
        self.base_build_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"TotalRecall Orchestrator initialized with {len(self.agents)} agents")

    def read_totalrecall_blueprint(self):
        """Read the existing TotalRecall files as the blueprint"""
        blueprint = []
        tr_dir = Path.home() / "constellation25" / "modules" / "totalrecall_mesh"
        
        if tr_dir.exists():
            for file in tr_dir.rglob('*.py'):
                with open(file, 'r', errors='ignore') as f:
                    content = f.read()
                    blueprint.append({"file": str(file), "content": content})
        
        logger.info(f"Read {len(blueprint)} blueprint files from TotalRecall")
        return blueprint

    def execute_build(self):
        """Dispatch 25 agents to build the ecosystem from the blueprint"""
        blueprint = self.read_totalrecall_blueprint()
        
        print("\n" + "="*60)
        print("  STARTING 25-AGENT BUILD SEQUENCE")
        print("="*60 + "\n")
        
        total_files = 0
        total_errors = 0
        
        for agent in self.agents:
            print(f"[{agent.name}] Building {agent.domain}...")
            result = agent.build(self.base_build_dir, blueprint)
            total_files += result["files_built"]
            total_errors += result["errors"]
            
        print("\n" + "="*60)
        print(f"  BUILD COMPLETE")
        print(f"  Files Built: {total_files}")
        print(f"  Errors: {total_errors}")
        print("="*60 + "\n")
        
        return {"files_built": total_files, "errors": total_errors}

if __name__ == "__main__":
    orchestrator = TotalRecallOrchestrator()
    orchestrator.execute_build()
