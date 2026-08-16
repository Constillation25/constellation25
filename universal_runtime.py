#!/data/data/com.termux/files/usr/bin/python3
"""
UNIVERSAL RUNTIME ORCHESTRATOR v2
Fast scan with progress tracking and aggressive filtering
"""
import os
import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime
from collections import defaultdict
import signal

class TimeoutError(Exception):
    pass

def timeout_handler(signum, frame):
    raise TimeoutError("Scan timeout")

class UniversalRuntime:
    def __init__(self):
        self.scan_paths = [
            Path.home() / "constellation25",
        ]
        
        # Aggressively skip these directories (they're massive or irrelevant)
        self.skip_dirs = {
            '.git', 'node_modules', '__pycache__', '.obsidian',
            'production_build', 'repos', 'logs', 'agent_builds',
            'TotalRecall-Builder', '.cache', '.npm', '.local'
        }
        
        self.discovered_scripts = []
        self.execution_order = []
        self.context = {}
        self.scan_count = 0
        self.max_scripts = 500  # Limit to prevent overload
        
        self.log_file = Path.home() / "constellation25" / "logs" / f"runtime_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        Path(self.log_file).parent.mkdir(parents=True, exist_ok=True)
    
    def log(self, msg):
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_line = f"[{timestamp}] {msg}"
        print(log_line, flush=True)
        with open(self.log_file, 'a') as f:
            f.write(log_line + "\n")
    
    def scan_all_locations(self):
        """Fast scan with progress tracking"""
        self.log("[SCAN] Initiating fast filesystem scan...")
        self.log(f"[SCAN] Skipping directories: {', '.join(self.skip_dirs)}")
        
        for base_path in self.scan_paths:
            if not base_path.exists():
                self.log(f"[!] Path not found: {base_path}")
                continue
            
            self.log(f"[>] Scanning: {base_path}")
            
            try:
                for root, dirs, files in os.walk(base_path):
                    # Aggressively filter directories
                    dirs[:] = [d for d in dirs if d not in self.skip_dirs]
                    
                    # Progress indicator
                    self.scan_count += 1
                    if self.scan_count % 100 == 0:
                        print(f"\r[SCAN] Processed {self.scan_count} directories, found {len(self.discovered_scripts)} scripts...", end='', flush=True)
                    
                    # Check file limit
                    if len(self.discovered_scripts) >= self.max_scripts:
                        self.log(f"\n[!] Reached max script limit ({self.max_scripts}). Stopping scan.")
                        break
                    
                    for file in files:
                        file_path = Path(root) / file
                        
                        if self._is_executable_script(file_path):
                            self.discovered_scripts.append({
                                'path': str(file_path),
                                'name': file,
                                'type': self._get_script_type(file),
                                'size': file_path.stat().st_size,
                                'depth': len(file_path.relative_to(base_path).parts)
                            })
                
                print()  # New line after progress indicator
                
            except Exception as e:
                self.log(f"[!] Scan error: {e}")
                continue
        
        self.log(f"[✓] Scan complete: {len(self.discovered_scripts)} scripts discovered")
        return self.discovered_scripts
    
    def _is_executable_script(self, path):
        """Fast check if file is executable"""
        if not path.is_file():
            return False
        
        # Quick extension check first
        ext = path.suffix.lower()
        if ext in ['.sh', '.bash', '.py', '.js']:
            return True
        
        # Check executable permission
        if os.access(path, os.X_OK):
            return True
        
        return False
    
    def _get_script_type(self, filename):
        """Determine script type"""
        ext = Path(filename).suffix.lower()
        name = filename.lower()
        
        if 'boot' in name or 'wake' in name or 'start' in name:
            return 'boot'
        elif 'deploy' in name or 'install' in name:
            return 'deploy'
        elif 'agent' in name:
            return 'agent'
        elif ext in ['.sh', '.bash']:
            return 'bash'
        elif ext == '.py':
            return 'python'
        elif ext == '.js':
            return 'node'
        else:
            return 'utility'
    
    def map_dependencies(self):
        """Map execution order"""
        self.log("[MAP] Building execution dependency graph...")
        
        priority_map = {
            'boot': 0,
            'deploy': 1,
            'agent': 2,
            'bash': 3,
            'python': 4,
            'node': 5,
            'utility': 6
        }
        
        # Sort by priority, then by depth (shallower first), then alphabetically
        sorted_scripts = sorted(
            self.discovered_scripts,
            key=lambda x: (
                priority_map.get(x['type'], 99),
                x['depth'],
                x['path']
            )
        )
        
        self.execution_order = sorted_scripts
        self.log(f"[✓] Mapped {len(self.execution_order)} scripts to execution order")
        
        # Show execution plan
        self.log("[MAP] Execution plan:")
        for idx, script in enumerate(self.execution_order[:20], 1):
            self.log(f"  {idx}. [{script['type']}] {script['name']}")
        
        if len(self.execution_order) > 20:
            self.log(f"  ... and {len(self.execution_order) - 20} more")
        
        return self.execution_order
    
    def execute_all(self, dry_run=False):
        """Execute all scripts"""
        self.log("[EXEC] Starting execution sequence...")
        
        success_count = 0
        fail_count = 0
        
        for idx, script in enumerate(self.execution_order, 1):
            script_path = script['path']
            
            self.log(f"[{idx}/{len(self.execution_order)}] {script['name']} ({script['type']})")
            
            if dry_run:
                self.log(f"  [DRY RUN] {script_path}")
                success_count += 1
                continue
            
            try:
                if script['type'] == 'bash':
                    cmd = ['bash', script_path]
                elif script['type'] == 'python':
                    cmd = ['python3', script_path]
                elif script['type'] == 'node':
                    cmd = ['node', script_path]
                else:
                    cmd = [script_path]
                
                result = subprocess.run(
                    cmd,
                    timeout=60,  # 1 minute timeout
                    capture_output=True,
                    text=True,
                    cwd=str(Path(script_path).parent)
                )
                
                if result.returncode == 0:
                    self.log(f"  [✓] Success")
                    success_count += 1
                else:
                    self.log(f"  [!] Failed (exit: {result.returncode})")
                    fail_count += 1
            
            except subprocess.TimeoutExpired:
                self.log(f"  [!] TIMEOUT")
                fail_count += 1
            except Exception as e:
                self.log(f"  [!] ERROR: {str(e)[:100]}")
                fail_count += 1
        
        self.log(f"[✓] Execution complete: {success_count} success, {fail_count} failed")
        return success_count, fail_count

def main():
    runtime = UniversalRuntime()
    
    print("╔════════════════════════════════════════════════════════════╗")
    print("║   UNIVERSAL RUNTIME ORCHESTRATOR v2                      ║")
    print("║   Fast scan + dependency mapping                         ║")
    print("╚════════════════════════════════════════════════════════════╝")
    print()
    
    # Phase 1: Fast scan
    scripts = runtime.scan_all_locations()
    
    if not scripts:
        print("[!] No scripts found.")
        sys.exit(1)
    
    # Phase 2: Map dependencies
    runtime.map_dependencies()
    
    # Phase 3: Execute or dry run
    if '--dry-run' in sys.argv:
        print("\n[DRY RUN MODE]\n")
        runtime.execute_all(dry_run=True)
    else:
        print("\n[EXECUTION MODE]\n")
        runtime.execute_all(dry_run=False)
    
    print()
    print("╔════════════════════════════════════════════════════════════╗")
    print("║   RUNTIME COMPLETE                                       ║")
    print(f"║   Log: {runtime.log_file}")
    print("╚════════════════════════════════════════════════════════════╝")

if __name__ == "__main__":
    main()
