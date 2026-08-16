import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse

class H(BaseHTTPRequestHandler):
    def do_GET(self):
        path = urlparse(self.path).path
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        if path == '/health':
            resp = {"status": "healthy", "repo": "constellation25", "mode": "TERMUX_NATIVE"}
        elif path == '/repos':
            resp = {"repos": ["constellation25", "faceprintpay", "versed_ai"]}
        else:
            resp = {"error": "Not found"}
        self.wfile.write(json.dumps(resp).encode())
        
    def do_POST(self):
        path = urlparse(self.path).path
        if path == '/nlp2code':
            length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(length).decode('utf-8')
            try:
                req = json.loads(body)
                intent = req.get("intent", "").lower()
                targets = ["constellation25"]
                if "jupiter" in intent: targets.append("jupiter_agent")
                if "faceprintpay" in intent: targets.append("faceprintpay")
                if "versed" in intent: targets.append("versed_ai")
                
                resp = {
                    "intent": req.get("intent"),
                    "action": "routed",
                    "targets": targets,
                    "status": "success"
                }
            except:
                resp = {"error": "Invalid JSON"}
        else:
            resp = {"error": "Not found"}
            
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(resp).encode())

    def log_message(self, *args): pass

HTTPServer(('0.0.0.0', 8000), H).serve_forever()
