#!/data/data/com.termux/files/usr/bin/python3
"""
Site Configuration Manager
Manages site configurations with save/load, bookmarks, and transfer settings
Based on FileZilla Site Manager configuration
"""
import json
import time
import yaml
import logging
from pathlib import Path
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s [SITE-CONFIG] %(message)s')
logger = logging.getLogger(__name__)

class SiteConfiguration:
    """Complete site configuration"""
    def __init__(self, site_name):
        self.site_name = site_name
        self.general = {
            "protocol": "FTP",
            "host": "",
            "port": 21,
            "encryption": "Require explicit FTP over TLS",
            "logon_type": "Normal",
            "user": "",
            "password": "",
            "background_color": "None",
            "comments": ""
        }
        self.advanced = {
            "default_remote_dir": "",
            "synchronize_local_dirs": False,
            "enable_recursive": True,
            "limit_speed": False,
            "speed_limit": 0
        }
        self.transfer_settings = {
            "transfer_mode": "Auto",
            "ascii_files": "Auto",
            "continue_interrupted": True,
            "overwrite_mode": "Overwrite if newer",
            "delete_extra_files": False
        }
        self.bookmarks = []
        self.created = datetime.now().isoformat()
        self.last_modified = None

    def update_general(self, **kwargs):
        """Update general settings"""
        for key, value in kwargs.items():
            if key in self.general:
                self.general[key] = value
        self.last_modified = datetime.now().isoformat()

    def update_advanced(self, **kwargs):
        """Update advanced settings"""
        for key, value in kwargs.items():
            if key in self.advanced:
                self.advanced[key] = value
        self.last_modified = datetime.now().isoformat()

    def update_transfer(self, **kwargs):
        """Update transfer settings"""
        for key, value in kwargs.items():
            if key in self.transfer_settings:
                self.transfer_settings[key] = value
        self.last_modified = datetime.now().isoformat()

    def add_bookmark(self, name, path):
        """Add bookmark"""
        bookmark = {
            "name": name,
            "path": path,
            "created": datetime.now().isoformat()
        }
        self.bookmarks.append(bookmark)
        return bookmark

    def export_to_yaml(self):
        """Export configuration to YAML"""
        return yaml.dump({
            "site_name": self.site_name,
            "general": self.general,
            "advanced": self.advanced,
            "transfer_settings": self.transfer_settings,
            "bookmarks": self.bookmarks
        }, default_flow_style=False)

    def get_config(self):
        return {
            "site_name": self.site_name,
            "general": self.general,
            "advanced": self.advanced,
            "transfer_settings": self.transfer_settings,
            "bookmarks": self.bookmarks,
            "created": self.created,
            "last_modified": self.last_modified
        }

class SiteConfigManager:
    """Manages site configurations"""
    def __init__(self, config_dir=None):
        self.config_dir = Path(config_dir) if config_dir else Path.home() / "constellation25" / "config" / "sites"
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.configurations = {}

    def create_config(self, site_name):
        """Create new site configuration"""
        config = SiteConfiguration(site_name)
        self.configurations[site_name] = config
        self._save_config(site_name)
        logger.info(f"Configuration created: {site_name}")
        return config

    def load_config(self, site_name):
        """Load configuration from file"""
        config_file = self.config_dir / f"{site_name}.yaml"
        if not config_file.exists():
            return {"error": f"Configuration {site_name} not found"}

        with open(config_file, 'r') as f:
            data = yaml.safe_load(f)

        config = SiteConfiguration(site_name)
        config.general.update(data.get("general", {}))
        config.advanced.update(data.get("advanced", {}))
        config.transfer_settings.update(data.get("transfer_settings", {}))
        config.bookmarks = data.get("bookmarks", [])

        self.configurations[site_name] = config
        logger.info(f"Configuration loaded: {site_name}")
        return config

    def save_config(self, site_name):
        """Save configuration to file"""
        if site_name not in self.configurations:
            return False

        self._save_config(site_name)
        logger.info(f"Configuration saved: {site_name}")
        return True

    def _save_config(self, site_name):
        """Internal save method"""
        config = self.configurations[site_name]
        config_file = self.config_dir / f"{site_name}.yaml"

        with open(config_file, 'w') as f:
            f.write(config.export_to_yaml())

    def list_configs(self):
        """List all configurations"""
        return list(self.configurations.keys())

    def duplicate_config(self, source_name, new_name):
        """Duplicate a configuration"""
        if source_name not in self.configurations:
            return {"error": f"Configuration {source_name} not found"}

        source = self.configurations[source_name]
        new_config = SiteConfiguration(new_name)

        # Copy settings
        new_config.general.update(source.general)
        new_config.advanced.update(source.advanced)
        new_config.transfer_settings.update(source.transfer_settings)
        new_config.bookmarks = source.bookmarks.copy()

        self.configurations[new_name] = new_config
        self._save_config(new_name)

        logger.info(f"Configuration duplicated: {source_name} → {new_name}")
        return new_config

    def get_manager_status(self):
        return {
            "total_configs": len(self.configurations),
            "config_dir": str(self.config_dir),
            "configs": list(self.configurations.keys())
        }

if __name__ == "__main__":
    manager = SiteConfigManager()

    print("=== SITE CONFIGURATION MANAGER DEMO ===\n")

    # Create configuration
    print("1. Creating site configuration:")
    config = manager.create_config("Production FTP")
    print(f"   Site: {config.site_name}\n")

    # Configure general settings
    print("2. Configuring General settings:")
    config.update_general(
        protocol="FTP - File Transfer Protocol",
        host="ftp.online.net",
        port=21,
        encryption="Require explicit FTP over TLS",
        logon_type="Normal",
        user="webmaster@example.com",
        password="secret123",
        background_color="None",
        comments="Production server"
    )
    print(f"   Protocol: {config.general['protocol']}")
    print(f"   Host: {config.general['host']}:{config.general['port']}")
    print(f"   User: {config.general['user']}")
    print(f"   Comments: {config.general['comments']}\n")

    # Configure advanced settings
    print("3. Configuring Advanced settings:")
    config.update_advanced(
        default_remote_dir="/var/www/html",
        synchronize_local_dirs=True,
        enable_recursive=True,
        limit_speed=False
    )
    print(f"   Default remote dir: {config.advanced['default_remote_dir']}")
    print(f"   Sync local dirs: {config.advanced['synchronize_local_dirs']}\n")

    # Configure transfer settings
    print("4. Configuring Transfer settings:")
    config.update_transfer(
        transfer_mode="Auto",
        ascii_files="Auto",
        continue_interrupted=True,
        overwrite_mode="Overwrite if newer"
    )
    print(f"   Transfer mode: {config.transfer_settings['transfer_mode']}")
    print(f"   Continue interrupted: {config.transfer_settings['continue_interrupted']}\n")

    # Add bookmarks
    print("5. Adding bookmarks:")
    config.add_bookmark("Web Root", "/var/www/html")
    config.add_bookmark("Uploads", "/var/www/uploads")
    config.add_bookmark("Logs", "/var/log/apache2")
    print(f"   Bookmarks: {len(config.bookmarks)}")
    for bm in config.bookmarks:
        print(f"     - {bm['name']}: {bm['path']}")
    print()

    # Export to YAML
    print("6. Exporting configuration:")
    yaml_config = config.export_to_yaml()
    print("   Configuration exported to YAML")
    print(f"   Lines: {len(yaml_config.split(chr(10)))}\n")

    # Duplicate configuration
    print("7. Duplicating configuration:")
    new_config = manager.duplicate_config("Production FTP", "Staging FTP")
    print(f"   Duplicated: Production FTP → Staging FTP")
    print(f"   New config user: {new_config.general['user']}\n")

    # List configurations
    print("8. All configurations:")
    configs = manager.list_configs()
    for c in configs:
        print(f"   - {c}")

    print("\n=== SITE CONFIGURATION ARCHITECTURE ===")
    print("General | Advanced | Transfer Settings | Bookmarks")
    print("Save/Load/Duplicate configurations")
