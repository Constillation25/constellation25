#!/data/data/com.termux/files/usr/bin/python3
"""PaTHos - NLP Routing & Agent Orchestration Engine"""
import json, sys

AGENT_MAP = {
    "deploy": "mars",
    "security": "vesta",
    "forensic": "neptune",
    "commerce": "jupiter",
    "mesh": "moon",
    "creative": "venus",
    "data": "saturn",
    "nlp": "mercury",
    "health": "hygiea",
    "orchestrate": "earth"
}

def route_command(nlp_input):
    input_lower = nlp_input.lower()
    for keyword, agent in AGENT_MAP.items():
        if keyword in input_lower:
            return {"intent": keyword, "agent": agent, "status": "ROUTED"}
    return {"intent": "unknown", "agent": "earth", "status": "FALLBACK"}

if __name__ == "__main__":
    if len(sys.argv) > 1:
        result = route_command(" ".join(sys.argv[1:]))
        print(json.dumps(result, indent=2))
    else:
        print("Usage: python3 engine.py <natural_language_command>")
