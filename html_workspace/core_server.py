import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# Mount core repos dynamically based on the manifest
manifest = os.path.expanduser("~/constellation25/html_workspace/core_production_html.txt")
mounted_dirs = set()

with open(manifest, 'r') as f:
    for line in f:
        file_path = line.strip()
        # Mount the root of the specific project repo, not the individual file
        parts = file_path.split('/repos/')
        if len(parts) > 1:
            repo_root = parts[0] + '/repos/' + parts[1].split('/')[0]
            if repo_root not in mounted_dirs and os.path.exists(repo_root):
                mount_name = parts[1].split('/')[0]
                app.mount(f"/{mount_name}", StaticFiles(directory=repo_root, html=True), name=mount_name)
                mounted_dirs.add(repo_root)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8080)
