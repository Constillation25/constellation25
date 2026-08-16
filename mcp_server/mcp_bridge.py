import http.server
import socketserver
import json
import time

PORT = 8080

class MCPHandler(http.server.SimpleHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        print(f"[MCP] Received Task: {post_data.decode('utf-8')}")
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'{"status": "processed"}')
    
    def log_message(self, format, *args):
        pass # Silence logs for performance

with socketserver.TCPServer(("", PORT), MCPHandler) as httpd:
    print(f"[MCP BRIDGE] Online on port {PORT}")
    httpd.serve_forever()
