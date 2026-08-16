#!/data/data/com.termux/files/usr/bin/python3
"""
GUI Transition Graph Extractor
Explores the app GUI and extracts state transitions.
Uses Termux API / ADB for local UI inspection.
"""
import json
import subprocess
import time
from pathlib import Path

GRAPH_PATH = Path.home() / "constellation25" / "modules" / "bugrepro" / "gui_graph" / "transition_graph.json"

class GUIGraphExtractor:
    def __init__(self):
        self.graph = {"nodes": [], "edges": [], "explored_states": set()}
        GRAPH_PATH.parent.mkdir(parents=True, exist_ok=True)

    def get_current_ui_state(self):
        """Get current UI state via ADB uiautomator dump"""
        try:
            # Dump UI hierarchy
            subprocess.run(["adb", "shell", "uiautomator", "dump", "/sdcard/ui.xml"], check=True, capture_output=True)
            subprocess.run(["adb", "pull", "/sdcard/ui.xml", "/tmp/ui.xml"], check=True, capture_output=True)
            
            # Parse basic elements (simplified for Termux)
            with open("/tmp/ui.xml", "r") as f:
                content = f.read()
            
            # Extract clickable elements (simplified regex for demo)
            import re
            elements = re.findall(r'text="([^"]*)".*?clickable="true"', content)
            return {"elements": list(set(elements)), "raw_hash": hash(content)}
        except Exception as e:
            print(f"[GUI] ADB not available, using mock state: {e}")
            return {"elements": ["Login", "Settings", "Profile"], "raw_hash": hash("mock")}

    def explore_and_build_graph(self, max_steps=5):
        """Explore the app and build the transition graph"""
        print("[GUI] Starting GUI exploration...")
        
        current_state = self.get_current_ui_state()
        state_id = f"state_{len(self.graph['nodes'])}"
        
        self.graph["nodes"].append({
            "id": state_id,
            "elements": current_state["elements"]
        })

        for step in range(max_steps):
            print(f"[GUI] Exploring step {step + 1}/{max_steps}...")
            
            # Simulate interaction (in real env, this taps the element via ADB)
            next_state = self.get_current_ui_state()
            next_state_id = f"state_{len(self.graph['nodes'])}"
            
            # Add transition
            self.graph["edges"].append({
                "from": state_id,
                "to": next_state_id,
                "action": f"tap_{current_state['elements'][0] if current_state['elements'] else 'unknown'}"
            })
            
            self.graph["nodes"].append({
                "id": next_state_id,
                "elements": next_state["elements"]
            })
            
            state_id = next_state_id
            current_state = next_state
            time.sleep(0.5) # Simulate app transition time

        self._save_graph()
        print(f"[GUI] Graph built: {len(self.graph['nodes'])} nodes, {len(self.graph['edges'])} edges")

    def _save_graph(self):
        with open(GRAPH_PATH, "w") as f:
            json.dump(self.graph, f, indent=2)

    def get_app_knowledge(self):
        """Return the graph for the LLM to use"""
        if GRAPH_PATH.exists():
            with open(GRAPH_PATH, "r") as f:
                return json.load(f)
        return self.graph

if __name__ == "__main__":
    extractor = GUIGraphExtractor()
    print("=== GUI TRANSITION GRAPH EXTRACTOR ===")
    extractor.explore_and_build_graph(max_steps=3)
    
    print("\nGraph Summary:")
    print(json.dumps(extractor.get_app_knowledge(), indent=2)[:500] + "...")
