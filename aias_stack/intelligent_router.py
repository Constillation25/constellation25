#!/usr/bin/env python3
"""
Earth's Intelligent Task Router
Adapted from decision-tree logic (like the OS flowchart)
Routes tasks to optimal agent based on:
- Complexity
- Security requirements  
- Resource needs
- User expertise
"""

class IntelligentRouter:
    def __init__(self):
        self.agents = {
            "Venus": {"security": 10, "complexity": 7, "specialty": "encryption"},
            "Mercury": {"security": 6, "complexity": 8, "specialty": "api"},
            "Earth": {"security": 8, "complexity": 10, "specialty": "orchestration"},
            "Mars": {"security": 7, "complexity": 6, "specialty": "cli"},
            "Jupiter": {"security": 7, "complexity": 9, "specialty": "infrastructure"},
            "Saturn": {"security": 6, "complexity": 7, "specialty": "benchmarking"},
        }
    
    def route_task(self, task):
        """
        Decision tree routing:
        1. Is it security-critical? → Venus
        2. Is it API-related? → Mercury  
        3. Is it orchestration? → Earth
        4. Is it CLI/terminal? → Mars
        5. Is it infrastructure? → Jupiter
        6. Default → Earth
        """
        task_type = task.get('type', 'general')
        security_level = task.get('security_level', 'medium')
        complexity = task.get('complexity', 5)
        
        # Decision tree
        if security_level == 'critical' or task_type == 'encryption':
            return "Venus"
        elif task_type == 'api' or task_type == 'endpoint':
            return "Mercury"
        elif task_type == 'orchestration' or complexity >= 9:
            return "Earth"
        elif task_type == 'cli' or task_type == 'terminal':
            return "Mars"
        elif task_type == 'infrastructure' or task_type == 'scaling':
            return "Jupiter"
        elif task_type == 'benchmark' or task_type == 'testing':
            return "Saturn"
        else:
            return "Earth"  # Default orchestrator
    
    def get_agent_queue(self, agent):
        """Get current queue for agent"""
        return f"~/c25_ipc/pending/{agent.lower()}_*.json"

router = IntelligentRouter()
