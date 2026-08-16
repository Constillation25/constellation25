import json
import hashlib

class ChairmanLLM:
    def __init__(self):
        # Weighted evaluation metrics
        self.weights = {"correctness": 0.4, "performance": 0.3, "risk": 0.2, "complexity": 0.1}

    def evaluate_candidates(self, task_hash, candidates):
        """
        candidates: [{'agent_id': str, 'code': str, 'tests_passed': int}, ...]
        """
        scored = []
        for c in candidates:
            # Simulate LLM scoring logic (Replace with local Ollama/Qwen call in prod)
            correctness = c['tests_passed'] / 100.0
            performance = 1.0 / (len(c['code']) / 1000.0) # Penalize bloat
            score = (correctness * self.weights['correctness']) + \
                    (performance * self.weights['performance']) + \
                    (0.8 * self.weights['risk']) + (0.9 * self.weights['complexity'])
            
            scored.append({"agent_id": c['agent_id'], "score": score})
        
        winner = max(scored, key=lambda x: x['score'])
        return {
            "task_hash": task_hash,
            "winner": winner['agent_id'],
            "confidence": round(winner['score'], 2),
            "status": "PR_READY"
        }
