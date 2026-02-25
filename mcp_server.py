#!/usr/bin/env python3
"""
MCP Server for Constellation-25
Implements Model Context Protocol for agent coordination.
Matches capabilities of: Manus, OpenClaw, Anthropic MCP
"""
import json, sys, os, time
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

sys.path.insert(0, os.path.dirname(__file__))
from memoria import Memoria
from llm_wrapper import LLMWrapper

class MCPHandler(BaseHTTPRequestHandler):
    """
    MCP Protocol Handler
    Implements agent orchestration, knowledge sharing, and tool coordination.
    """
    
    def do_POST(self):
        """Handle MCP protocol requests."""
        parsed = urlparse(self.path)
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length).decode('utf-8')
        
        try:
            request = json.loads(body) if body else {}
        except json.JSONDecodeError:
            self.send_error_response("Invalid JSON")
            return
        
        # MCP endpoints
        if parsed.path == '/mcp/orchestrate':
            self.handle_orchestrate(request)
        elif parsed.path == '/mcp/knowledge-share':
            self.handle_knowledge_share(request)
        elif parsed.path == '/mcp/tool-call':
            self.handle_tool_call(request)
        elif parsed.path == '/mcp/agent-status':
            self.handle_agent_status(request)
        else:
            self.send_error_response("Unknown endpoint")
    
    def handle_orchestrate(self, request):
        """
        MCP Orchestration endpoint
        Coordinates multiple agents on a complex task.
        """
        task = request.get('task', '')
        agents = request.get('agents', [])  # Specific agents to use
        strategy = request.get('strategy', 'parallel')  # parallel/sequential/adaptive
        
        if not task:
            self.send_error_response("Task required")
            return
        
        # Use Earth agent to decompose task
        import subprocess
        result = subprocess.run(
            ['python3', 'earth_agent.py'],
            input=task.encode(),
            capture_output=True,
            timeout=30
        )
        
        if result.returncode != 0:
            self.send_error_response(result.stderr.decode())
            return
        
        earth_output = json.loads(result.stdout.decode())
        
        # Filter to requested agents if specified
        if agents:
            earth_output['tasks'] = [
                t for t in earth_output['tasks']
                if t['agent_name'] in agents or t['agent_id'] in agents
            ]
        
        # Apply orchestration strategy
        if strategy == 'sequential':
            # Tasks executed in order
            for task in earth_output['tasks']:
                task['dependencies'] = [earth_output['tasks'][i-1]['agent_id']] if i > 0 else []
        elif strategy == 'adaptive':
            # High-priority tasks first
            earth_output['tasks'].sort(key=lambda t: 0 if t.get('priority') == 'high' else 1)
        
        # Log to Memoria
        mem = Memoria()
        mem.log("MCP", f"Orchestrated {len(earth_output['tasks'])} agents for: {task[:100]}", 
                "MCP", "success")
        
        self.send_json_response({
            "success": True,
            "strategy": strategy,
            "task_count": len(earth_output['tasks']),
            "tasks": earth_output['tasks']
        })
    
    def handle_knowledge_share(self, request):
        """
        MCP Knowledge Sharing endpoint
        Allows agents to share knowledge/artifacts with each other.
        """
        from_agent = request.get('from_agent', 'Unknown')
        to_agents = request.get('to_agents', [])  # List of target agents
        knowledge = request.get('knowledge', {})
        knowledge_type = request.get('type', 'artifact')  # artifact/insight/tool
        
        mem = Memoria()
        
        # Store knowledge in Memoria for target agents
        for target in to_agents:
            mem.log(
                source=from_agent,
                content=json.dumps(knowledge),
                agent=target,
                status="shared",
                artifacts=knowledge_type
            )
        
        self.send_json_response({
            "success": True,
            "from": from_agent,
            "to": to_agents,
            "type": knowledge_type
        })
    
    def handle_tool_call(self, request):
        """
        MCP Tool Call endpoint
        Executes tools/functions on behalf of agents.
        """
        agent = request.get('agent', 'Unknown')
        tool_name = request.get('tool', '')
        parameters = request.get('parameters', {})
        
        mem = Memoria()
        
        # Execute tool based on name
        result = None
        success = False
        
        if tool_name == 'llm':
            # LLM call
            wrapper = LLMWrapper()
            llm_result = wrapper.call(
                parameters.get('prompt', ''),
                provider=parameters.get('provider'),
                model=parameters.get('model')
            )
            result = llm_result
            success = llm_result.get('success', False)
            
            # Log LLM call
            if success:
                mem.log_llm_call(
                    agent=agent,
                    model=llm_result.get('model', 'unknown'),
                    provider=llm_result.get('provider', 'unknown'),
                    prompt=parameters.get('prompt', ''),
                    response=llm_result.get('response', ''),
                    tokens=llm_result.get('tokens', 0),
                    latency_ms=llm_result.get('latency_ms', 0)
                )
        
        elif tool_name == 'memoria_search':
            # Search Memoria
            query = parameters.get('query', '')
            results = mem.search(query)
            result = {"results": results}
            success = True
        
        elif tool_name == 'bash_execute':
            # Execute bash script
            import subprocess
            script = parameters.get('script', '')
            exec_result = subprocess.run(
                ['bash', '-c', script],
                capture_output=True,
                timeout=60
            )
            result = {
                "stdout": exec_result.stdout.decode(),
                "stderr": exec_result.stderr.decode(),
                "returncode": exec_result.returncode
            }
            success = exec_result.returncode == 0
        
        else:
            result = {"error": f"Unknown tool: {tool_name}"}
            success = False
        
        # Log function call
        mem.log_function_call(agent, tool_name, parameters, result, success)
        
        self.send_json_response({
            "success": success,
            "tool": tool_name,
            "result": result
        })
    
    def handle_agent_status(self, request):
        """
        MCP Agent Status endpoint
        Returns current status of all agents.
        """
        mem = Memoria()
        stats = mem.get_stats()
        llm_stats = mem.get_llm_stats()
        
        # Load agent definitions
        with open('agents.json') as f:
            agents_data = json.load(f)
        
        agent_status = []
        for agent in agents_data['agents']:
            # Find stats for this agent
            agent_stats = next((s for s in stats if s[0] == agent['name']), None)
            
            if agent_stats:
                _, total, successes, failures = agent_stats
                success_rate = (successes / total * 100) if total > 0 else 0
            else:
                total, successes, failures = 0, 0, 0
                success_rate = 0
            
            agent_status.append({
                "id": agent['id'],
                "name": agent['name'],
                "role": agent['role'],
                "pillars": agent.get('pillars', []),
                "total_tasks": total,
                "success_rate": round(success_rate, 1),
                "status": "active" if total > 0 else "idle"
            })
        
        self.send_json_response({
            "success": True,
            "agent_count": len(agent_status),
            "agents": agent_status,
            "llm_stats": llm_stats
        })
    
    def send_json_response(self, data):
        """Send JSON response."""
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
    
    def send_error_response(self, error):
        """Send error response."""
        self.send_response(400)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({"success": False, "error": error}).encode())
    
    def log_message(self, format, *args):
        """Custom log format."""
        print(f"[MCP] {format % args}")

if __name__ == "__main__":
    PORT = int(os.getenv("MCP_PORT", 8080))
    
    print("╔══════════════════════════════════════════════════════════════╗")
    print("║   CONSTELLATION-25 MCP SERVER                                ║")
    print(f"║   http://localhost:{PORT}                                    ║")
    print("╠══════════════════════════════════════════════════════════════╣")
    print("║   Endpoints:                                                 ║")
    print("║   POST /mcp/orchestrate     - Agent coordination             ║")
    print("║   POST /mcp/knowledge-share - Inter-agent knowledge          ║")
    print("║   POST /mcp/tool-call       - Tool execution                 ║")
    print("║   POST /mcp/agent-status    - Agent status                   ║")
    print("╚══════════════════════════════════════════════════════════════╝")
    print("")
    
    server = HTTPServer(('0.0.0.0', PORT), MCPHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[MCP Server stopped]")
        server.shutdown()
