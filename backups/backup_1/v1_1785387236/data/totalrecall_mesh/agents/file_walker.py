#!/data/data/com.termux/files/usr/bin/python3
"""
File Walker Agent
Walks all directories, reads files, creates missing directories, validates code
"""
import os
import json
import logging
from pathlib import Path
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s [WALKER] %(message)s')
logger = logging.getLogger(__name__)

class FileWalkerAgent:
    """Walks filesystem and validates/fixes structure"""
    def __init__(self, base_dir=None):
        self.base_dir = Path(base_dir) if base_dir else Path.home() / "constellation25"
        self.files_processed = 0
        self.directories_created = 0
        self.errors_found = 0
        self.errors_fixed = 0
        self.file_types = {
            '.py': 0, '.md': 0, '.html': 0, '.css': 0, '.js': 0,
            '.java': 0, '.json': 0, '.yaml': 0, '.yml': 0, '.sh': 0
        }

    def walk_directory(self, directory=None):
        """Walk directory tree"""
        directory = Path(directory) if directory else self.base_dir
        
        if not directory.exists():
            logger.warning(f"Directory does not exist: {directory}")
            return []

        files = []
        for root, dirs, filenames in os.walk(directory):
            # Skip hidden directories
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            
            for filename in filenames:
                file_path = Path(root) / filename
                files.append(file_path)
                self.files_processed += 1
                
                # Count file types
                ext = file_path.suffix.lower()
                if ext in self.file_types:
                    self.file_types[ext] += 1

        logger.info(f"Walked {directory}: {len(files)} files")
        return files

    def validate_file(self, file_path):
        """Validate a file"""
        errors = []
        
        # Check if file is readable
        if not file_path.exists():
            errors.append({"type": "missing", "file": str(file_path)})
            self.errors_found += 1
            return errors

        # Check file size
        if file_path.stat().st_size == 0:
            errors.append({"type": "empty", "file": str(file_path)})
            self.errors_found += 1

        # Check Python files for syntax
        if file_path.suffix == '.py':
            try:
                with open(file_path, 'r') as f:
                    compile(f.read(), file_path, 'exec')
            except SyntaxError as e:
                errors.append({"type": "syntax_error", "file": str(file_path), "error": str(e)})
                self.errors_found += 1

        return errors

    def create_missing_directories(self, required_dirs):
        """Create missing directories"""
        for dir_path in required_dirs:
            path = Path(dir_path)
            if not path.exists():
                path.mkdir(parents=True, exist_ok=True)
                self.directories_created += 1
                logger.info(f"Created directory: {dir_path}")

    def fix_errors(self, errors):
        """Fix common errors"""
        for error in errors:
            if error['type'] == 'empty':
                # Create minimal content
                with open(error['file'], 'w') as f:
                    f.write("# Empty file\n")
                self.errors_fixed += 1
                logger.info(f"Fixed empty file: {error['file']}")

    def get_walker_stats(self):
        return {
            "files_processed": self.files_processed,
            "directories_created": self.directories_created,
            "errors_found": self.errors_found,
            "errors_fixed": self.errors_fixed,
            "file_types": self.file_types
        }

if __name__ == "__main__":
    walker = FileWalkerAgent()
    print("=== FILE WALKER AGENT DEMO ===\n")
    
    # Walk constellation25 directory
    files = walker.walk_directory()
    print(f"Files processed: {walker.files_processed}")
    print(f"File types: {walker.file_types}")
    print()
    
    # Create missing directories
    required_dirs = [
        Path.home() / "constellation25" / "production",
        Path.home() / "constellation25" / "logs",
        Path.home() / "constellation25" / "secrets"
    ]
    walker.create_missing_directories(required_dirs)
    print(f"Directories created: {walker.directories_created}")
    print()
    
    # Stats
    print(f"Walker stats: {walker.get_walker_stats()}")
