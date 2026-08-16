#!/data/data/com.termux/files/usr/bin/python3
"""
BugRepro Orchestrator
Integrates RAG Store + GUI Graph + LLM Routing to reproduce bugs.
Assigned to Artemis (QA) and Mars (Security) agents in the Constellation25 mesh.
"""
import sys
import json
import time
from pathlib import Path

# Add parent paths for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from rag_store.local_rag import LocalRAGStore
from gui_graph.extractor import GUIGraphExtractor

class BugReproOrchestrator:
    def __init__(self):
        self.rag = LocalRAGStore()
        self.gui = GUIGraphExtractor()
        self.reproduction_log = []

    def process_bug_report(self, ambiguous_report):
        """
        Main pipeline:
        1. Retrieve similar bugs from RAG
        2. Get GUI transition graph
        3. Route to LLM (Simulated here) to generate S2R
        4. Execute reproduction
        """
        print(f"\n[BUGREPRO] Processing ambiguous report: '{ambiguous_report[:50]}...'")
        
        # Step 1: RAG Retrieval
        print("[BUGREPRO] Step 1: Retrieving similar bugs from RAG...")
        similar_bugs = self.rag.retrieve_similar(ambiguous_report, top_k=2)
        print(f"  Found {len(similar_bugs)} similar historical bugs.")
        
        # Step 2: GUI Knowledge
        print("[BUGREPRO] Step 2: Extracting GUI transition graph...")
        gui_graph = self.gui.get_app_knowledge()
        print(f"  Graph has {len(gui_graph['nodes'])} UI states.")
        
        # Step 3: LLM Routing (Simulated Sovereign LLM)
        print("[BUGREPRO] Step 3: Routing to Sovereign LLM for S2R generation...")
        generated_steps = self._simulate_llm_routing(ambiguous_report, similar_bugs, gui_graph)
        print(f"  Generated {len(generated_steps)} reproduction steps.")
        
        # Step 4: Execution
        print("[BUGREPRO] Step 4: Executing reproduction steps...")
        success = self._execute_steps(generated_steps)
        
        result = {
            "report": ambiguous_report,
            "similar_bugs_found": len(similar_bugs),
            "steps_generated": generated_steps,
            "success": success,
            "timestamp": time.time()
        }
        self.reproduction_log.append(result)
        return result

    def _simulate_llm_routing(self, report, similar_bugs, gui_graph):
        """Simulates the LLM generating Steps to Reproduce"""
        # In production, this calls the local LLM or SovereignGTP API
        steps = [
            "1. Launch application",
            "2. Navigate to " + (gui_graph['nodes'][0]['elements'][0] if gui_graph['nodes'] else "main screen"),
            "3. Input ambiguous data based on report",
            "4. Observe crash/bug behavior"
        ]
        return steps

    def _execute_steps(self, steps):
        """Simulates executing the steps via ADB/Termux"""
        for step in steps:
            print(f"  [EXEC] {step}")
            time.sleep(0.2) # Simulate UI interaction delay
        return True # Simulated success

if __name__ == "__main__":
    orchestrator = BugReproOrchestrator()
    
    print("╔════════════════════════════════════════════════════════════╗")
    print("║   BUGREPRO ORCHESTRATOR - CONSTELLATION25 MESH            ║")
    print("╚════════════════════════════════════════════════════════════╝")
    
    # Test with an ambiguous bug report
    ambiguous_report = "the app just dies when i try to do the thing with the money button"
    
    result = orchestrator.process_bug_report(ambiguous_report)
    
    print("\n[RESULT] Reproduction Success:", result["success"])
    print("[RESULT] Steps taken:", result["steps_generated"])
