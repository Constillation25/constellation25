import os, json
from http.server import BaseHTTPRequestHandler, HTTPServer

C25_ROOT = os.path.expanduser("~/constellation25")
SKIP_DIRS = {'node_modules', '.git', 'c25_ipc', 'logs', '__pycache__', '.server'}
VALID_EXTS = {'.sh', '.bash', '.py', '.js', '.ts', '.json', '.yml', '.yaml', '.md', '.html', '.css', '.txt', 'dockerfile', '.gitignore'}

def scan_files(root):
    files = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for f in filenames:
            ext = os.path.splitext(f)[1].lower()
            name_lower = f.lower()
            if ext in VALID_EXTS or name_lower.startswith('readme') or name_lower == 'dockerfile':
                rel = os.path.relpath(os.path.join(dirpath, f), root)
                files.append({"name": f, "path": rel, "ext": ext.lstrip('.') or ('readme' if name_lower.startswith('readme') else 'dockerfile')})
    return sorted(files, key=lambda x: x['path'])

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/api/files':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(scan_files(C25_ROOT)).encode())
        elif self.path.endswith('.html') or self.path == '/':
            path = self.path if self.path != '/' else '/c25_explorer.html'
            filepath = os.path.join(C25_ROOT, path.lstrip('/'))
            if os.path.isfile(filepath):
                self.send_response(200)
                self.send_header('Content-Type', 'text/html')
                self.end_headers()
                with open(filepath, 'rb') as f: self.wfile.write(f.read())
            else:
                self.send_response(404); self.end_headers()
        else:
            self.send_response(404); self.end_headers()
    def log_message(self, format, *args): pass  # Silence logs

if __name__ == '__main__':
    print(f" C25 File Index Server running on :8081")
    HTTPServer(('127.0.0.1', 8081), Handler).serve_forever()
