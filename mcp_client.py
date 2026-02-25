#!/usr/bin/env python3
"""
MCP Client for Constellation-25
Python client library for interacting with MCP server.
"""
import requests, json

class MCPClient:
    """Client for MCP protocol communication."""
    
    def __init__(self, host="localhost", port=8080):
        self.base_url = f"http://{host}:{port}/mcp"
    
    def orchestrate(self, task, agents=None, strategy="parallel"):
        """
        Orchestrate agents on a task.
        
        Args:
            task: Task description
            agents: List of agent names/IDs to use (None = all)
            strategy: 'parallel', 'sequential', or 'adaptive'
        """
        response = requests.post(f"{self.base_url}/orchestrate", json={
            "task": task,
            "agents": agents or [],
            "strategy": strategy
        })
        return response.json()
    
    def share_knowledge(self, from_agent, to_agents, knowledge, knowledge_type="artifact"):
        """
        Share knowledge between agents.
        
        Args:
            from_agent: Source agent name
            to_agents: List of target agent names
            knowledge: Knowledge/data to share
            knowledge_type: 'artifact', 'insight', or 'tool'
        """
        response = requests.post(f"{self.base_url}/knowledge-share", json={
            "from_agent": from_agent,
            "to_agents": to_agents,
            "knowledge": knowledge,
            "type": knowledge_type
        })
        return response.json()
    
    def call_tool(self, agent, tool_name, parameters):
        """
        Execute a tool on behalf of an agent.
        
        Args:
            agent: Agent name
            tool_name: 'llm', 'memoria_search', 'bash_execute', etc.
            parameters: Tool-specific parameters
        """
        response = requests.post(f"{self.base_url}/tool-call", json={
            "agent": agent,
            "tool": tool_name,
            "parameters": parameters
        })
        return response.json()
    
    def get_agent_status(self):
        """Get status of all agents."""
        response = requests.post(f"{self.base_url}/agent-status", json={})
        return response.json()

# CLI interface
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: mcp_client.py <command> [args...]")
        print("Commands:")
        print("  orchestrate <task> [strategy]")
        print("  status")
        print("  tool-call <agent> <tool> <params_json>")
        sys.exit(1)
    
    client = MCPClient()
    command = sys.argv[1]
    
    if command == "orchestrate":
        task = sys.argv[2] if len(sys.argv) > 2 else "test task"
        strategy = sys.argv[3] if len(sys.argv) > 3 else "parallel"
        result = client.orchestrate(task, strategy=strategy)
        print(json.dumps(result, indent=2))
    
    elif command == "status":
        result = client.get_agent_status()
        print(json.dumps(result, indent=2))
    
    elif command == "tool-call":
        agent = sys.argv[2] if len(sys.argv) > 2 else "Earth"
        tool = sys.argv[3] if len(sys.argv) > 3 else "memoria_search"
        params = json.loads(sys.argv[4]) if len(sys.argv) > 4 else {}
        result = client.call_tool(agent, tool, params)
        print(json.dumps(result, indent=2))
    
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)
