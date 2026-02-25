#!/usr/bin/env python3
"""
Data Integration — Connect Constellation-25 to external data sources.
Supports: REST APIs, databases, file systems, web scraping.
FRAMEWORK PILLAR: Scalable Market (external data access)
"""
import os, sys, json, subprocess

class DataIntegrator:
    """
    Unified interface for external data sources.
    FRAMEWORK PILLAR: Adaptive Execution (data source failover)
    """
    
    def __init__(self):
        self.sources = self._detect_available_sources()
    
    def _detect_available_sources(self):
        """Detect which data sources are available."""
        sources = ["filesystem", "http"]
        
        # Check for database clients
        if self._check_command("sqlite3"):
            sources.append("sqlite")
        if self._check_command("psql"):
            sources.append("postgres")
        if self._check_command("mongosh"):
            sources.append("mongodb")
        
        return sources
    
    def _check_command(self, cmd):
        """Check if a command is available."""
        try:
            subprocess.run([cmd, "--version"], capture_output=True, timeout=2)
            return True
        except Exception:
            return False
    
    def fetch(self, source_type, **params):
        """
        Fetch data from external source with automatic retry.
        FRAMEWORK PILLAR: Adaptive Execution
        """
        max_retries = 2
        for attempt in range(max_retries):
            try:
                if source_type == "http":
                    return self._fetch_http(**params)
                elif source_type == "sqlite":
                    return self._fetch_sqlite(**params)
                elif source_type == "postgres":
                    return self._fetch_postgres(**params)
                elif source_type == "mongodb":
                    return self._fetch_mongodb(**params)
                elif source_type == "filesystem":
                    return self._fetch_filesystem(**params)
                else:
                    return {"success": False, "error": f"Unknown source: {source_type}"}
            except Exception as e:
                if attempt == max_retries - 1:
                    return {"success": False, "error": str(e)}
        
        return {"success": False, "error": "Max retries exceeded"}
    
    def _fetch_http(self, url, method="GET", headers=None, data=None):
        """Fetch data from HTTP/REST API."""
        cmd = ["curl", "-s", "-X", method]
        
        if headers:
            for key, value in headers.items():
                cmd.extend(["-H", f"{key}: {value}"])
        
        if data:
            cmd.extend(["-d", json.dumps(data)])
        
        cmd.append(url)
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            try:
                return {
                    "success": True,
                    "data": json.loads(result.stdout),
                    "source": "http"
                }
            except json.JSONDecodeError:
                return {
                    "success": True,
                    "data": result.stdout,
                    "source": "http"
                }
        else:
            return {"success": False, "error": result.stderr}
    
    def _fetch_sqlite(self, db_path, query):
        """Fetch data from SQLite database."""
        result = subprocess.run(
            ["sqlite3", "-json", db_path, query],
            capture_output=True, text=True, timeout=10
        )
        
        if result.returncode == 0:
            try:
                return {
                    "success": True,
                    "data": json.loads(result.stdout),
                    "source": "sqlite"
                }
            except json.JSONDecodeError:
                return {
                    "success": True,
                    "data": result.stdout,
                    "source": "sqlite"
                }
        else:
            return {"success": False, "error": result.stderr}
    
    def _fetch_postgres(self, host, database, query, user=None, password=None):
        """Fetch data from PostgreSQL database."""
        conn_str = f"postgresql://{user}@{host}/{database}" if user else f"postgresql:///{database}"
        
        result = subprocess.run(
            ["psql", conn_str, "-t", "-A", "-c", query],
            capture_output=True, text=True, timeout=10
        )
        
        if result.returncode == 0:
            return {
                "success": True,
                "data": result.stdout.strip().split('\n'),
                "source": "postgres"
            }
        else:
            return {"success": False, "error": result.stderr}
    
    def _fetch_mongodb(self, host, database, collection, query):
        """Fetch data from MongoDB."""
        mongo_cmd = f'db.{collection}.find({query}).toArray()'
        
        result = subprocess.run(
            ["mongosh", f"{host}/{database}", "--quiet", "--eval", mongo_cmd],
            capture_output=True, text=True, timeout=10
        )
        
        if result.returncode == 0:
            try:
                return {
                    "success": True,
                    "data": json.loads(result.stdout),
                    "source": "mongodb"
                }
            except json.JSONDecodeError:
                return {
                    "success": True,
                    "data": result.stdout,
                    "source": "mongodb"
                }
        else:
            return {"success": False, "error": result.stderr}
    
    def _fetch_filesystem(self, path, operation="read"):
        """Read/write filesystem data."""
        try:
            if operation == "read":
                with open(path, 'r') as f:
                    content = f.read()
                
                # Try to parse as JSON
                try:
                    data = json.loads(content)
                except json.JSONDecodeError:
                    data = content
                
                return {
                    "success": True,
                    "data": data,
                    "source": "filesystem"
                }
            elif operation == "list":
                import os
                files = os.listdir(path)
                return {
                    "success": True,
                    "data": files,
                    "source": "filesystem"
                }
            else:
                return {"success": False, "error": f"Unknown operation: {operation}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

# Data transformation utilities
class DataTransformer:
    """Transform data between formats for agent consumption."""
    
    @staticmethod
    def to_markdown(data, title="Data"):
        """Convert data to markdown format."""
        if isinstance(data, list) and len(data) > 0 and isinstance(data[0], dict):
            # Table format
            headers = list(data[0].keys())
            lines = [f"# {title}", "", "| " + " | ".join(headers) + " |"]
            lines.append("| " + " | ".join(["---"] * len(headers)) + " |")
            for row in data:
                lines.append("| " + " | ".join(str(row.get(h, "")) for h in headers) + " |")
            return "\n".join(lines)
        else:
            return f"# {title}\n\n```json\n{json.dumps(data, indent=2)}\n```"
    
    @staticmethod
    def to_csv(data):
        """Convert data to CSV format."""
        if not isinstance(data, list) or len(data) == 0:
            return ""
        
        headers = list(data[0].keys())
        lines = [",".join(headers)]
        for row in data:
            lines.append(",".join(str(row.get(h, "")) for h in headers))
        return "\n".join(lines)

# CLI interface
if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: data_integration.py <source_type> <params_json>")
        print("Example: data_integration.py http '{\"url\": \"https://api.example.com/data\"}'")
        print("Example: data_integration.py sqlite '{\"db_path\": \"~/data.db\", \"query\": \"SELECT * FROM users\"}'")
        sys.exit(1)
    
    source_type = sys.argv[1]
    params = json.loads(sys.argv[2])
    
    integrator = DataIntegrator()
    print(f"Available sources: {integrator.sources}", file=sys.stderr)
    
    result = integrator.fetch(source_type, **params)
    print(json.dumps(result, indent=2))
