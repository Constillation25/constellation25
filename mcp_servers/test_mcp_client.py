#!/usr/bin/env python3
import subprocess
import json
import sys

MCP_SERVER = "/data/data/com.termux/files/home/constellation25/mcp_servers/c25_revenue_mcp.py"

def send_mcp_request(request):
    """Send JSON-RPC request to MCP server via stdio"""
    proc = subprocess.Popen(
        ["python3", MCP_SERVER],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # Send request
    proc.stdin.write(json.dumps(request) + "\n")
    proc.stdin.flush()
    
    # Read response
    response = proc.stdout.readline()
    proc.stdin.close()
    proc.wait()
    
    return json.loads(response)

# Test 1: Initialize handshake
print("🤝 Test 1: MCP Initialize Handshake")
init_req = {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}}
resp = send_mcp_request(init_req)
print(f"Response: {json.dumps(resp, indent=2)}\n")

# Test 2: List available tools
print("🛠️  Test 2: List Sovereign Tools")
list_req = {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}}
resp = send_mcp_request(list_req)
print(f"Available tools: {len(resp['result']['tools'])}")
for tool in resp['result']['tools']:
    print(f"  - {tool['name']}: {tool['description']}")
print()

# Test 3: Generate an Agentik License
print("💰 Test 3: Generate Agentik License for @duckman_dev")
license_req = {
    "jsonrpc": "2.0",
    "id": 3,
    "method": "tools/call",
    "params": {
        "name": "generate_agentik_license",
        "arguments": {
            "buyer_handle": "@duckman_dev",
            "payment_method": "cashapp"
        }
    }
}
resp = send_mcp_request(license_req)
print(f"License Generation Result:")
print(json.dumps(json.loads(resp['result']['content'][0]['text']), indent=2))
print()

# Test 4: Queue a Bugcrowd Bounty
print("🎯 Test 4: Queue Bugcrowd Bounty Submission")
bounty_req = {
    "jsonrpc": "2.0",
    "id": 4,
    "method": "tools/call",
    "params": {
        "name": "submit_bugcrowd_bounty",
        "arguments": {
            "target_domain": "acme-corp.com",
            "vulnerability_type": "Exposed .env file with AWS credentials",
            "evidence_path": "/data/data/com.termux/files/home/constellation25/bugcrowd_hunter/reports/report_acme-corp_com_20260703.md"
        }
    }
}
resp = send_mcp_request(bounty_req)
print(f"Bounty Queue Result:")
print(json.dumps(json.loads(resp['result']['content'][0]['text']), indent=2))

