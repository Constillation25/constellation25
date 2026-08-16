#!/data/data/com.termux/files/usr/bin/python3
"""
Production Queue Manager
Redis-based task queue replacing file-based IPC
"""
import json
import time
import redis
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s [QUEUE] %(message)s')
logger = logging.getLogger(__name__)

class ProductionQueue:
    """Redis-based production queue"""
    def __init__(self, redis_host='localhost', redis_port=6379, db=0):
        try:
            self.redis = redis.Redis(host=redis_host, port=redis_port, db=db, decode_responses=True)
            self.redis.ping()
            logger.info("Redis connected")
        except:
            logger.warning("Redis not available, using fallback queue")
            self.redis = None
            self.fallback_queue = []

    def enqueue(self, task):
        """Add task to queue"""
        task_json = json.dumps(task)
        if self.redis:
            self.redis.lpush('totalrecall:tasks', task_json)
            logger.info(f"Task enqueued: {task.get('task_id')}")
        else:
            self.fallback_queue.append(task)

    def dequeue(self, timeout=5):
        """Get next task from queue"""
        if self.redis:
            result = self.redis.brpop('totalrecall:tasks', timeout=timeout)
            if result:
                return json.loads(result[1])
        else:
            if self.fallback_queue:
                return self.fallback_queue.pop(0)
        return None

    def queue_size(self):
        """Get queue size"""
        if self.redis:
            return self.redis.llen('totalrecall:tasks')
        return len(self.fallback_queue)

    def get_queue_stats(self):
        return {
            "queue_size": self.queue_size(),
            "backend": "redis" if self.redis else "fallback"
        }

if __name__ == "__main__":
    queue = ProductionQueue()
    print("=== PRODUCTION QUEUE MANAGER ===\n")
    print(f"Queue stats: {queue.get_queue_stats()}")
    
    # Test enqueue/dequeue
    task = {"task_id": "test-001", "type": "compile", "source": "test_code()"}
    queue.enqueue(task)
    print(f"Enqueued: {task['task_id']}")
    
    dequeued = queue.dequeue(timeout=1)
    if dequeued:
        print(f"Dequeued: {dequeued['task_id']}")
