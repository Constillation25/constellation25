#!/data/data/com.termux/files/usr/bin/env python3
import os
import json
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler

ALLOWED_BASES = [
    os.path.expanduser("~/constellation25"),
    os.path.expanduser("~/c25_master_build"),
    os.path.expanduser("~/c25_ipc")
]
CODE_EXTENSIONS = {'.py', '.js', '.jsx', '.ts', '.tsx', '.sh', '.json', '.md', '.yaml', '.yml', '.html', '.css'}
MAX_FILE_SIZE = 500 * 1024

class C25Handler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass # We use custom logging below

    def do_GET(self):
        print(f"🔍 INCOMING REQUEST: {self.path}")
        
        # 1. Serve Main Dashboard
        if self.path == '/' or self.path == '/index.html':
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(self.get_html().encode('utf-8'))
            return

        # 2. Serve Directory Tree API
        if self.path.startswith('/api/tree'):
            query = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            target_dir = query.get('path', [os.path.expanduser("~/constellation25")])[0]
            
            if not self.is_safe(target_dir) or not os.path.isdir(target_dir):
                self.send_error(403, "Forbidden")
                return

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(self.build_tree(target_dir)).encode('utf-8'))
            return

        # 3. Serve File Content API
        if self.path.startswith('/api/read'):
            query = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            file_path = query.get('path', [''])[0]
            
            if not self.is_safe(file_path) or not os.path.isfile(file_path):
                self.send_error(403, "Forbidden")
                return

            try:
                size = os.path.getsize(file_path)
                if size > MAX_FILE_SIZE:
                    content = f"⚠️ FILE TOO LARGE ({size/1024:.1f}KB). Limit is 500KB."
                else:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                
                self.send_response(200)
                self.send_header('Content-type', 'text/plain; charset=utf-8')
                self.end_headers()
                self.wfile.write(content.encode('utf-8'))
            except Exception as e:
                self.send_error(500, str(e))
            return

        # 4. Catch-all 404
        self.send_error(404, f"Not Found: {self.path}")

    def is_safe(self, path):
        abs_path = os.path.abspath(path)
        return any(abs_path.startswith(os.path.abspath(base)) for base in ALLOWED_BASES)

    def build_tree(self, directory):
        tree = {"name": os.path.basename(directory) or directory, "path": directory, "type": "dir", "children": []}
        try:
            for item in sorted(os.listdir(directory)):
                if item.startswith('.'): continue
                item_path = os.path.join(directory, item)
                if os.path.isdir(item_path):
                    tree["children"].append(self.build_tree(item_path))
                else:
                    ext = os.path.splitext(item)[1].lower()
                    if ext in CODE_EXTENSIONS:
                        tree["children"].append({"name": item, "path": item_path, "type": "file", "ext": ext})
        except PermissionError:
            pass
        return tree

    def get_html(self):
        return """<!DOCTYPE html>
<html><head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>C25 Code Explorer</title>
<style>
body{margin:0;font-family:monospace;background:#0d1117;color:#c9d1d9;display:flex;height:100vh}
#side{width:40%;background:#161b22;border-right:1px solid #30363d;overflow-y:auto;padding:10px}
#main{width:60%;display:flex;flex-direction:column;overflow:hidden}
#head{padding:10px;border-bottom:1px solid #30363d;background:#161b22;font-weight:bold}
#view{flex:1;overflow:auto;padding:15px}
pre{background:#0d1117;padding:10px;border:1px solid #30363d;overflow-x:auto;white-space:pre-wrap;font-size:12px}
.dir{cursor:pointer;padding:4px;color:#58a6ff;font-weight:bold}
.file{cursor:pointer;padding:4px 0 4px 15px;color:#c9d1d9}
.file:hover{color:#58a6ff;text-decoration:underline}
</style></head><body>
<div id="side"><h3 style="margin-top:0">🌌 C25 Explorer</h3><div id="tree">Loading...</div></div>
<div id="main"><div id="head">Select a file</div><div id="view"><pre id="content">Ready.</pre></div></div>
<script>
async function loadTree(path) {
    const res = await fetch('/api/tree?path=' + encodeURIComponent(path));
    const data = await res.json();
    render(data, document.getElementById('tree'), 0);
}
function render(node, container, level) {
    container.innerHTML = '';
    if (node.type === 'dir') {
        const div = document.createElement('div');
        div.className = 'dir';
        div.style.paddingLeft = (level * 15) + 'px';
        div.textContent = '📁 ' + node.name;
        div.onclick = async () => {
            const childDiv = document.createElement('div');
            childDiv.style.marginLeft = '15px';
            childDiv.innerHTML = 'Loading...';
            div.parentNode.insertBefore(childDiv, div.nextSibling);
            const res = await fetch('/api/tree?path=' + encodeURIComponent(node.path));
            const children = (await res.json()).children || [];
            childDiv.innerHTML = '';
            children.forEach(c => render(c, childDiv, 0));
        };
        container.appendChild(div);
    } else {
        const div = document.createElement('div');
        div.className = 'file';
        div.style.paddingLeft = (level * 15 + 15) + 'px';
        div.textContent = '📄 ' + node.name;
        div.onclick = async () => {
            document.getElementById('head').textContent = node.name;
            document.getElementById('content').textContent = 'Loading...';
            const res = await fetch('/api/read?path=' + encodeURIComponent(node.path));
            document.getElementById('content').textContent = await res.text();
        };
        container.appendChild(div);
    }
}
loadTree('/data/data/com.termux/files/home/constellation25');
</script></body></html>"""

if __name__ == '__main__':
    PORT = 8080
    print("="*50)
    print("🌌 C25 CODEBASE EXPLORER STARTED")
    print(f"🚀 Open browser to: http://localhost:{PORT}")
    print("🔍 Watch this terminal for incoming requests.")
    print("Press Ctrl+C to stop.")
    print("="*50)
    HTTPServer(('0.0.0.0', PORT), C25Handler).serve_forever()
