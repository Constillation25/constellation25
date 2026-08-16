#!/data/data/com.termux/files/usr/bin/python3
"""
Object Storage Browser
File/folder management with breadcrumb navigation
Simulates S3-like object storage interface
"""
import os
import json
import time
import shutil
import logging
from pathlib import Path
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s [STORAGE] %(message)s')
logger = logging.getLogger(__name__)

class ObjectStorage:
    """Object storage with folder hierarchy"""
    def __init__(self, storage_dir=None):
        self.storage_dir = storage_dir or str(Path.home() / "constellation25" / "storage")
        Path(self.storage_dir).mkdir(parents=True, exist_ok=True)
        self.metadata_file = f"{self.storage_dir}/.metadata.json"
        self.metadata = self._load_metadata()

    def _load_metadata(self):
        if Path(self.metadata_file).exists():
            with open(self.metadata_file, 'r') as f:
                return json.load(f)
        return {"objects": {}, "created": datetime.now().isoformat()}

    def _save_metadata(self):
        with open(self.metadata_file, 'w') as f:
            json.dump(self.metadata, f, indent=2)

    def create_folder(self, folder_name, parent_path="/"):
        """Create a new folder"""
        folder_path = Path(self.storage_dir) / folder_name.lstrip("/")
        folder_path.mkdir(parents=True, exist_ok=True)

        obj_id = f"folder_{int(time.time())}"
        self.metadata["objects"][obj_id] = {
            "id": obj_id,
            "name": folder_name,
            "type": "folder",
            "path": str(folder_path),
            "parent": parent_path,
            "created": datetime.now().isoformat(),
            "size": 0,
            "item_count": 0
        }
        self._save_metadata()

        logger.info(f"Folder created: {folder_name}")
        return self.metadata["objects"][obj_id]

    def upload_file(self, file_name, content, folder_path="/"):
        """Upload a file to storage"""
        target_dir = Path(self.storage_dir) / folder_path.lstrip("/")
        target_dir.mkdir(parents=True, exist_ok=True)

        file_path = target_dir / file_name
        with open(file_path, 'w') as f:
            f.write(content)

        obj_id = f"file_{int(time.time())}"
        self.metadata["objects"][obj_id] = {
            "id": obj_id,
            "name": file_name,
            "type": "file",
            "path": str(file_path),
            "parent": folder_path,
            "created": datetime.now().isoformat(),
            "size": len(content),
            "content_hash": hash(content)
        }
        self._save_metadata()

        logger.info(f"File uploaded: {file_name} ({len(content)} bytes)")
        return self.metadata["objects"][obj_id]

    def list_folder(self, folder_path="/"):
        """List contents of a folder"""
        target_dir = Path(self.storage_dir) / folder_path.lstrip("/")
        if not target_dir.exists():
            return []

        items = []
        for item in target_dir.iterdir():
            if item.name.startswith('.'):
                continue

            stat = item.stat()
            items.append({
                "name": item.name,
                "type": "folder" if item.is_dir() else "file",
                "size": stat.st_size if item.is_file() else 0,
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "path": str(item.relative_to(self.storage_dir))
            })

        return sorted(items, key=lambda x: (x["type"] == "file", x["name"]))

    def get_breadcrumb(self, folder_path="/"):
        """Get breadcrumb navigation path"""
        parts = folder_path.strip("/").split("/")
        breadcrumb = [{"name": "root", "path": "/"}]

        current_path = ""
        for part in parts:
            if part:
                current_path += f"/{part}"
                breadcrumb.append({
                    "name": part,
                    "path": current_path
                })

        return breadcrumb

    def delete_object(self, object_name, folder_path="/"):
        """Delete a file or folder"""
        target = Path(self.storage_dir) / folder_path.lstrip("/") / object_name

        if not target.exists():
            return False

        if target.is_dir():
            shutil.rmtree(target)
        else:
            target.unlink()

        # Remove from metadata
        self.metadata["objects"] = {
            k: v for k, v in self.metadata["objects"].items()
            if not v.get("path", "").endswith(object_name)
        }
        self._save_metadata()

        logger.info(f"Deleted: {object_name}")
        return True

    def get_storage_stats(self):
        """Get storage statistics"""
        total_size = 0
        file_count = 0
        folder_count = 0

        for obj in self.metadata["objects"].values():
            if obj["type"] == "file":
                total_size += obj.get("size", 0)
                file_count += 1
            elif obj["type"] == "folder":
                folder_count += 1

        return {
            "total_size_bytes": total_size,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "file_count": file_count,
            "folder_count": folder_count,
            "total_objects": len(self.metadata["objects"])
        }

class StorageBrowser:
    """Interactive storage browser with breadcrumb navigation"""
    def __init__(self, storage):
        self.storage = storage
        self.current_path = "/"

    def navigate(self, path):
        """Navigate to a folder"""
        self.current_path = path
        items = self.storage.list_folder(path)
        breadcrumb = self.storage.get_breadcrumb(path)

        return {
            "path": path,
            "breadcrumb": breadcrumb,
            "items": items
        }

    def display(self):
        """Display current folder contents"""
        result = self.navigate(self.current_path)

        print(f"\n{'='*60}")
        print(f"  OBJECT STORAGE BROWSER")
        print(f"{'='*60}\n")

        # Breadcrumb
        breadcrumb_str = " / ".join([b["name"] for b in result["breadcrumb"]])
        print(f"📁 {breadcrumb_str}\n")

        # Items
        if not result["items"]:
            print("  (empty folder)")
        else:
            for item in result["items"]:
                icon = "📁" if item["type"] == "folder" else ""
                size = f"{item['size']} bytes" if item["type"] == "file" else ""
                print(f"  {icon} {item['name']:<30} {size}")

        print(f"\n{'='*60}")

if __name__ == "__main__":
    storage = ObjectStorage()
    browser = StorageBrowser(storage)

    print("=== OBJECT STORAGE BROWSER DEMO ===\n")

    # Create folder structure
    print("1. Creating folder structure:")
    storage.create_folder("my-folder")
    storage.create_folder("my-folder/subfolder-1")
    storage.create_folder("my-folder/subfolder-2")
    storage.create_folder("projects")
    print(f"   Folders created\n")

    # Upload files
    print("2. Uploading files:")
    storage.upload_file("readme.md", "# My Project\nThis is a test file.", "/my-folder")
    storage.upload_file("config.json", '{"key": "value"}', "/my-folder/subfolder-1")
    storage.upload_file("data.csv", "id,name,value\n1,test,100", "/my-folder/subfolder-2")
    print(f"   Files uploaded\n")

    # Browse root
    print("3. Browsing root (/):")
    browser.current_path = "/"
    browser.display()

    # Browse my-folder
    print("\n4. Browsing /my-folder:")
    browser.current_path = "/my-folder"
    browser.display()

    # Browse subfolder
    print("\n5. Browsing /my-folder/subfolder-1:")
    browser.current_path = "/my-folder/subfolder-1"
    browser.display()

    # Storage stats
    print("\n6. Storage Statistics:")
    stats = storage.get_storage_stats()
    print(json.dumps(stats, indent=2))

    print("\n=== BREADCRUMB NAVIGATION ===")
    print("Root → my-folder → subfolder-1 → config.json")
