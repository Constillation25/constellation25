#!/usr/bin/env python3
import socket
import os
import concurrent.futures
from datetime import datetime

LOG_FILE = os.path.expanduser("~/constellation25/logs/autonomous/subdomain_enum.log")
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

def log(msg):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[ENUM {ts}] {msg}")
    with open(LOG_FILE, "a") as f:
        f.write(f"[{ts}] {msg}\n")

def resolve_subdomain(subdomain, target):
    full_domain = f"{subdomain}.{target}"
    try:
        ip = socket.gethostbyname(full_domain)
        log(f"✅ FOUND: {full_domain} -> {ip}")
        return full_domain
    except socket.gaierror:
        return None

def main():
    import sys
    if len(sys.argv) < 2:
        print("Usage: python3 subdomain_enum.py <target-domain.com>")
        return
        
    target = sys.argv[1]
    log(f"Starting subdomain enumeration for {target}...")
    
    # High-value subdomains for web apps
    wordlist = [
        "www", "mail", "api", "dev", "staging", "admin", "portal", 
        "test", "vpn", "webmail", "ftp", "ssh", "git", "jenkins",
        "kibana", "grafana", "jira", "confluence", "status", "blog",
        "uat", "qa", "prod", "internal", "dashboard", "app"
    ]
    
    found_subdomains = []
    
    # Use threading to speed it up (pure stdlib)
    with concurrent.futures.ThreadPoolExecutor(max_workers=15) as executor:
        futures = {executor.submit(resolve_subdomain, sub, target): sub for sub in wordlist}
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            if result:
                found_subdomains.append(result)
                
    log(f"Enumeration complete. Found {len(found_subdomains)} live subdomains.")
    
    # Save to file for the Hunter to use
    output_file = os.path.expanduser(f"~/constellation25/bugcrowd_hunter/subdomains_{target}.txt")
    with open(output_file, "w") as f:
        for sub in found_subdomains:
            f.write(f"{sub}\n")
            
    log(f"Subdomains saved to: {output_file}")

if __name__ == "__main__":
    main()
