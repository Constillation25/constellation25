#!/data/data/com.termux/files/usr/bin/python3
"""
Edge Services Pipeline
User → Customizable Edge Services Endpoint (SSL/TLS) → Edge Services Cache → ORIGIN (Object Storage or Load Balancer)
Based on Edge Services Pipeline diagram
"""
import json
import time
import hashlib
import logging
from pathlib import Path
from datetime import datetime

logging.basicConfig(level.INFO, format='%(asctime)s [EDGE-SERVICES] %(message)s')
logger = logging.getLogger(__name__)

class EdgeCache:
    """Edge cache for content delivery"""
    def __init__(self, cache_size_mb=1000, ttl_seconds=3600):
        self.cache_size_mb = cache_size_mb
        self.ttl_seconds = ttl_seconds
        self.items = {}
        self.hits = 0
        self.misses = 0

    def get(self, key):
        """Get item from cache"""
        if key in self.items:
            item = self.items[key]
            if time.time() < item["expires"]:
                self.hits += 1
                logger.info(f"Cache HIT: {key}")
                return item["content"]
            else:
                # Expired
                del self.items[key]

        self.misses += 1
        logger.info(f"Cache MISS: {key}")
        return None

    def set(self, key, content, ttl=None):
        """Set item in cache"""
        self.items[key] = {
            "content": content,
            "created": time.time(),
            "expires": time.time() + (ttl or self.ttl_seconds),
            "size": len(content) if isinstance(content, bytes) else len(content.encode())
        }
        logger.info(f"Cache SET: {key} (TTL: {ttl or self.ttl_seconds}s)")

    def purge(self, key=None):
        """Purge cache"""
        if key:
            if key in self.items:
                del self.items[key]
                logger.info(f"Cache purged: {key}")
        else:
            self.items.clear()
            logger.info("Cache fully purged")

    def get_stats(self):
        total = self.hits + self.misses
        hit_rate = (self.hits / total * 100) if total > 0 else 0
        return {
            "items": len(self.items),
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": f"{hit_rate:.1f}%",
            "size_mb": round(sum(i["size"] for i in self.items.values()) / (1024 * 1024), 2)
        }

class OriginServer:
    """Origin server (Object Storage or Load Balancer)"""
    def __init__(self, origin_type, origin_url):
        self.origin_type = origin_type  # "object_storage" or "load_balancer"
        self.origin_url = origin_url
        self.requests = 0

    def fetch(self, path):
        """Fetch content from origin"""
        self.requests += 1
        logger.info(f"Origin fetch: {self.origin_type}://{self.origin_url}{path}")

        # Simulate content
        if self.origin_type == "object_storage":
            return f"Object from storage: {path}"
        else:
            return f"Response from load balancer: {path}"

class EdgeEndpoint:
    """Customizable edge services endpoint with SSL/TLS"""
    def __init__(self, endpoint_id, domain, ssl_cert=None):
        self.endpoint_id = endpoint_id
        self.domain = domain
        self.ssl_cert = ssl_cert
        self.ssl_enabled = ssl_cert is not None
        self.custom_rules = []
        self.requests = 0

    def configure_ssl(self, cert_path, key_path):
        """Configure SSL/TLS certificate"""
        self.ssl_cert = {
            "cert_path": cert_path,
            "key_path": key_path,
            "installed": datetime.now().isoformat()
        }
        self.ssl_enabled = True
        logger.info(f"SSL configured for {self.domain}")

    def add_rule(self, rule_type, pattern, action):
        """Add custom edge rule"""
        rule = {
            "type": rule_type,
            "pattern": pattern,
            "action": action,
            "created": datetime.now().isoformat()
        }
        self.custom_rules.append(rule)
        logger.info(f"Edge rule added: {rule_type} {pattern} → {action}")

    def handle_request(self, path):
        """Handle incoming request"""
        self.requests += 1
        return {
            "endpoint": self.domain,
            "path": path,
            "ssl": self.ssl_enabled,
            "timestamp": datetime.now().isoformat()
        }

    def get_config(self):
        return {
            "endpoint_id": self.endpoint_id,
            "domain": self.domain,
            "ssl_enabled": self.ssl_enabled,
            "custom_rules": len(self.custom_rules),
            "requests": self.requests
        }

class EdgeServicesPipeline:
    """Complete edge services pipeline"""
    def __init__(self):
        self.cache = EdgeCache()
        self.endpoints = {}
        self.origins = {}

    def create_endpoint(self, domain, origin_type, origin_url, ssl_cert=None):
        """Create edge endpoint"""
        endpoint = EdgeEndpoint(f"ep-{int(time.time())}", domain, ssl_cert)
        self.endpoints[domain] = endpoint

        origin = OriginServer(origin_type, origin_url)
        self.origins[domain] = origin

        logger.info(f"Endpoint created: {domain} → {origin_type}://{origin_url}")
        return endpoint

    def serve_request(self, domain, path):
        """Serve request through edge pipeline"""
        if domain not in self.endpoints:
            return {"error": f"Endpoint {domain} not found"}

        endpoint = self.endpoints[domain]
        origin = self.origins[domain]

        # Handle request at edge
        endpoint.handle_request(path)

        # Check cache first
        cache_key = f"{domain}{path}"
        cached = self.cache.get(cache_key)

        if cached:
            return {
                "source": "cache",
                "content": cached,
                "endpoint": domain,
                "ssl": endpoint.ssl_enabled
            }

        # Fetch from origin
        content = origin.fetch(path)

        # Cache it
        self.cache.set(cache_key, content)

        return {
            "source": "origin",
            "content": content,
            "endpoint": domain,
            "ssl": endpoint.ssl_enabled,
            "origin_type": origin.origin_type
        }

    def purge_cache(self, domain, path=None):
        """Purge cache for domain"""
        if path:
            cache_key = f"{domain}{path}"
            self.cache.purge(cache_key)
        else:
            # Purge all for domain
            keys_to_purge = [k for k in self.cache.items.keys() if k.startswith(domain)]
            for key in keys_to_purge:
                self.cache.purge(key)
        logger.info(f"Cache purged for {domain}")

    def get_pipeline_status(self):
        return {
            "endpoints": len(self.endpoints),
            "cache": self.cache.get_stats(),
            "endpoint_details": {d: e.get_config() for d, e in self.endpoints.items()}
        }

if __name__ == "__main__":
    pipeline = EdgeServicesPipeline()

    print("=== EDGE SERVICES PIPELINE DEMO ===\n")

    # Create endpoint
    print("1. Creating edge endpoint:")
    endpoint = pipeline.create_endpoint(
        domain="cdn.kre8tive.space",
        origin_type="object_storage",
        origin_url="s3.fr-par.scw.cloud/videocourts-assets",
        ssl_cert="letsencrypt"
    )
    print(f"   Domain: {endpoint.domain}")
    print(f"   SSL: {endpoint.ssl_enabled}")
    print(f"   Origin: Object Storage\n")

    # Add custom rules
    print("2. Adding custom edge rules:")
    endpoint.add_rule("redirect", "/old-path", "/new-path")
    endpoint.add_rule("cache", "/assets/*", "cache_ttl=86400")
    endpoint.add_rule("security", "/admin/*", "require_auth=true")
    print(f"   Rules added: {len(endpoint.custom_rules)}\n")

    # Serve requests
    print("3. Serving requests:")
    for i in range(3):
        result = pipeline.serve_request("cdn.kre8tive.space", f"/video/{i}.mp4")
        print(f"   Request {i+1}: {result['source']} ({result['endpoint']})")
    print()

    # Cache stats
    print("4. Cache statistics:")
    cache_stats = pipeline.cache.get_stats()
    print(f"   Items: {cache_stats['items']}")
    print(f"   Hits: {cache_stats['hits']}")
    print(f"   Misses: {cache_stats['misses']}")
    print(f"   Hit rate: {cache_stats['hit_rate']}")
    print(f"   Size: {cache_stats['size_mb']} MB\n")

    # Purge cache
    print("5. Purging cache:")
    pipeline.purge_cache("cdn.kre8tive.space")
    print("   Cache purged\n")

    # Pipeline status
    print("6. Pipeline status:")
    status = pipeline.get_pipeline_status()
    print(f"   Endpoints: {status['endpoints']}")
    print(f"   Cache hit rate: {status['cache']['hit_rate']}")

    print("\n=== EDGE SERVICES ARCHITECTURE ===")
    print("User → Customizable Edge Services Endpoint (SSL/TLS) → Edge Services Cache → ORIGIN")
    print("Origin: Object Storage Bucket OR Load Balancer")
