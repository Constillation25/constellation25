#!/usr/bin/env python3
"""
Memoria — SQLite conversation and artifact log for Constellation-25.
Now includes LLM wrapper support and function call tracking.
"""
import sqlite3, sys, json, os, time

DB_PATH = os.path.expanduser("~/constellation-25/memoria.db")

class Memoria:
    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH)
        # Main memories table
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS memories (
                id        INTEGER PRIMARY KEY AUTOINCREMENT,
                source    TEXT,
                agent     TEXT    DEFAULT 'Earth',
                content   TEXT,
                artifacts TEXT    DEFAULT '',
                status    TEXT    DEFAULT 'pending',
                ts        DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        # LLM calls tracking table
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS llm_calls (
                id           INTEGER PRIMARY KEY AUTOINCREMENT,
                agent        TEXT,
                model        TEXT,
                provider     TEXT,
                prompt       TEXT,
                response     TEXT,
                tokens_used  INTEGER DEFAULT 0,
                latency_ms   INTEGER DEFAULT 0,
                success      INTEGER DEFAULT 1,
                ts           DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        # Function calls tracking table
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS function_calls (
                id           INTEGER PRIMARY KEY AUTOINCREMENT,
                agent        TEXT,
                function_name TEXT,
                parameters   TEXT,
                result       TEXT,
                success      INTEGER DEFAULT 1,
                ts           DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        self.conn.commit()

    def log(self, source, content, agent="Earth", status="pending", artifacts=""):
        """
        FRAMEWORK PILLAR: Structural Transparency
        Logs all agent actions with verifiable status for audit trail.
        """
        self.conn.execute(
            "INSERT INTO memories (source, agent, content, status, artifacts) VALUES (?,?,?,?,?)",
            (source, content, agent, status, artifacts)
        )
        self.conn.commit()
    
    def log_llm_call(self, agent, model, provider, prompt, response, tokens=0, latency_ms=0, success=True):
        """
        Track LLM API calls for cost monitoring and optimization.
        FRAMEWORK PILLAR: Scalable Market (cost tracking)
        """
        self.conn.execute(
            "INSERT INTO llm_calls (agent, model, provider, prompt, response, tokens_used, latency_ms, success) VALUES (?,?,?,?,?,?,?,?)",
            (agent, model, provider, prompt[:500], response[:1000], tokens, latency_ms, int(success))
        )
        self.conn.commit()
    
    def log_function_call(self, agent, function_name, parameters, result, success=True):
        """
        Track function/tool calls for agent actions.
        FRAMEWORK PILLAR: Structural Transparency
        """
        self.conn.execute(
            "INSERT INTO function_calls (agent, function_name, parameters, result, success) VALUES (?,?,?,?,?)",
            (agent, function_name, json.dumps(parameters), str(result)[:500], int(success))
        )
        self.conn.commit()

    def search(self, query):
        return self.conn.execute(
            "SELECT source, agent, ts, content, status, artifacts FROM memories WHERE content LIKE ?",
            (f"%{query}%",)
        ).fetchall()

    def recent(self, n=10):
        return self.conn.execute(
            "SELECT source, agent, ts, content, status FROM memories ORDER BY ts DESC LIMIT ?",
            (n,)
        ).fetchall()
    
    def get_stats(self):
        """
        FRAMEWORK PILLAR: Scalable Market (Trust & Reputation)
        Returns agent success rates for reputation scoring.
        """
        stats = self.conn.execute("""
            SELECT agent,
                   COUNT(*) as total,
                   SUM(CASE WHEN status='success' THEN 1 ELSE 0 END) as successes,
                   SUM(CASE WHEN status='failure' THEN 1 ELSE 0 END) as failures
            FROM memories
            WHERE agent != 'System'
            GROUP BY agent
        """).fetchall()
        return stats
    
    def get_llm_stats(self):
        """Get LLM usage statistics for cost analysis."""
        stats = self.conn.execute("""
            SELECT provider, model,
                   COUNT(*) as calls,
                   SUM(tokens_used) as total_tokens,
                   AVG(latency_ms) as avg_latency,
                   SUM(CASE WHEN success=1 THEN 1 ELSE 0 END) as successes
            FROM llm_calls
            GROUP BY provider, model
        """).fetchall()
        return stats

if __name__ == "__main__":
    mem = Memoria()
    cmd = sys.argv[1] if len(sys.argv) > 1 else "help"
    if cmd == "log":
        source    = sys.argv[2] if len(sys.argv) > 2 else "unknown"
        content   = sys.argv[3] if len(sys.argv) > 3 else ""
        agent     = sys.argv[4] if len(sys.argv) > 4 else "Earth"
        status    = sys.argv[5] if len(sys.argv) > 5 else "pending"
        artifacts = sys.argv[6] if len(sys.argv) > 6 else ""
        mem.log(source, content, agent, status, artifacts)
        print("Logged.")
    elif cmd == "search":
        query = " ".join(sys.argv[2:])
        print(json.dumps(mem.search(query), default=str))
    elif cmd == "recent":
        n = int(sys.argv[2]) if len(sys.argv) > 2 else 10
        print(json.dumps(mem.recent(n), default=str))
    elif cmd == "stats":
        print(json.dumps(mem.get_stats(), default=str))
    elif cmd == "llm-stats":
        print(json.dumps(mem.get_llm_stats(), default=str))
    else:
        print("Usage: memoria.py log SOURCE CONTENT [AGENT] [STATUS] [ARTIFACTS]")
        print("       memoria.py search QUERY")
        print("       memoria.py recent [N]")
        print("       memoria.py stats       # Agent success rates")
        print("       memoria.py llm-stats   # LLM usage statistics")
