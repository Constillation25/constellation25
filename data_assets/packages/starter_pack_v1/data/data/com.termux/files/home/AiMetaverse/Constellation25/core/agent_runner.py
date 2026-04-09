import sqlite3
import datetime
import sys

class C25Agent:
    def __init__(self, db_path):
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()

    def get_active_agents(self):
        self.cursor.execute("SELECT * FROM agents WHERE status='active'")
        return self.cursor.fetchall()

    def log_action(self, agent_id, action):
        print(f"[{datetime.datetime.now()}] Agent {agent_id}: {action}")

    def close(self):
        self.conn.close()

if __name__ == "__main__":
    try:
        agent = C25Agent('../db/c25_core.db')
        print("=== C25 Agent Core Online ===")
        active = agent.get_active_agents()
        for agent_info in active:
            agent.log_action(agent_info[0], f"System Check - {agent_info[1]}")
        agent.close()
    except Exception as e:
        print(f"Error: {e}")
