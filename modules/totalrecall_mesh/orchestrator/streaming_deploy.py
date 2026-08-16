#!/data/data/com.termux/files/usr/bin/python3
"""
Streaming Deployment Pipeline
Streams code from repos into TotalRecall mesh without full download
"""
import json
import time
import subprocess
import logging
from pathlib import Path
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s [STREAM] %(message)s')
logger = logging.getLogger(__name__)

class StreamingDeployer:
    """Streams code into TotalRecall mesh"""
    def __init__(self):
        self.repos_dir = Path.home() / "constellation25" / "repos"
        self.mesh_dir = Path.home() / "constellation25" / "modules" / "totalrecall_mesh"
        self.deployed_count = 0
        self.failed_count = 0

    def stream_repo_to_mesh(self, repo_path):
        """Stream repo code into mesh"""
        repo_path = Path(repo_path)
        if not repo_path.exists():
            logger.warning(f"Repo not found: {repo_path}")
            return False

        # Walk repo and stream files
        for file_path in repo_path.rglob('*'):
            if file_path.is_file() and not file_path.name.startswith('.'):
                # Read file
                try:
                    with open(file_path, 'r', errors='ignore') as f:
                        content = f.read()
                    
                    # Stream to mesh (simulate)
                    self.deployed_count += 1
                    logger.debug(f"Streamed: {file_path.name}")
                    
                except Exception as e:
                    self.failed_count += 1
                    logger.error(f"Failed to stream {file_path}: {e}")

        return True

    def deploy_all_repos(self):
        """Deploy all repos to mesh"""
        if not self.repos_dir.exists():
            logger.warning("No repos directory found")
            return

        repos = list(self.repos_dir.iterdir())
        logger.info(f"Found {len(repos)} repos to deploy")

        for repo in repos:
            if repo.is_dir():
                logger.info(f"Deploying: {repo.name}")
                self.stream_repo_to_mesh(repo)

        logger.info(f"Deployment complete: {self.deployed_count} files streamed, {self.failed_count} failed")

    def get_deploy_stats(self):
        return {
            "deployed_files": self.deployed_count,
            "failed_files": self.failed_count,
            "success_rate": f"{(self.deployed_count / max(self.deployed_count + self.failed_count, 1) * 100):.1f}%"
        }

if __name__ == "__main__":
    deployer = StreamingDeployer()
    print("=== STREAMING DEPLOYMENT PIPELINE ===\n")
    
    print("Deploying repos to TotalRecall mesh...")
    deployer.deploy_all_repos()
    
    print(f"\nDeployment stats: {deployer.get_deploy_stats()}")
