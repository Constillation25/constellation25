import os, threading, time
from http.server import BaseHTTPRequestHandler, HTTPServer

PORT = int(os.getenv("PORT", "8000"))
LABEL = "constellation25-orchestrator"

class H(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(('{"status":"operational","service":"' + LABEL + '"}').encode())
    def log_message(self, *a): pass

threading.Thread(target=lambda: HTTPServer(("0.0.0.0", PORT), H).serve_forever(), daemon=True).start()
print(f"[{LABEL}] health server on :{PORT}")

import subprocess, sys
while True:
    subprocess.run([sys.executable, os.path.expanduser("~/constellation25/c25_consume_ipc.py")], check=False)
    time.sleep(15)

while True:
    time.sleep(30)
