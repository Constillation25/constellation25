#!/usr/bin/env python3
import os, json, urllib.request, urllib.error, ssl
from datetime import datetime

LOG_FILE = os.path.expanduser("~/constellation25/logs/autonomous/bugcrowd_hunter.log")
REPORT_DIR = os.path.expanduser("~/constellation25/bugcrowd_hunter/reports")
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
os.makedirs(REPORT_DIR, exist_ok=True)

def log(msg):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[HUNTER {ts}] {msg}")
    with open(LOG_FILE, "a") as f:
        f.write(f"[{ts}] {msg}\n")

# Ignore SSL errors for recon (some targets have bad certs)
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

def check_endpoint(target, path):
    url = f"https://{target}{path}" if not target.startswith("http") else f"{target}{path}"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Bugcrowd-Hunter/1.0)'})
    try:
        with urllib.request.urlopen(req, timeout=5, context=ctx) as response:
            if response.status == 200:
                return True, url, response.read(500).decode('utf-8', errors='ignore')
    except urllib.error.HTTPError as e:
        if e.code == 403:
            return False, url, "403 Forbidden (Exists but protected)"
        return False, url, f"HTTP {e.code}"
    except Exception as e:
        return False, url, str(e)
    return False, url, "Unreachable"

def generate_bugcrowd_report(target, findings):
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_name = f"report_{target.replace('.', '_')}_{ts}.md"
    report_path = os.path.join(REPORT_DIR, report_name)
    
    with open(report_path, "w") as f:
        f.write(f"# Information Disclosure / Sensitive File Exposure on {target}\n\n")
        f.write(f"**Target:** {target}\n")
        f.write(f"**Date:** {datetime.now().strftime('%Y-%m-%d')}\n")
        f.write(f"**Severity:** Medium / High (Depending on data exposed)\n\n")
        
        f.write("## Description\n")
        f.write(f"During passive reconnaissance of `{target}`, the automated sovereign scanner identified exposed sensitive files and directories that should not be publicly accessible. This can lead to leakage of API keys, database credentials, or internal infrastructure details.\n\n")
        
        f.write("## Findings & Steps to Reproduce\n")
        for finding in findings:
            f.write(f"### {finding['path']}\n")
            f.write(f"- **URL:** `{finding['url']}`\n")
            f.write(f"- **Status:** {finding['status']}\n")
            if finding['status'] == 'EXPOSED':
                f.write(f"- **Evidence:** \n```text\n{finding['snippet'][:200]}...\n```\n")
            f.write("\n")
            
        f.write("## Impact\n")
        f.write("An attacker can use these exposed files to gather sensitive information about the application's backend, potentially leading to full system compromise, credential stuffing, or unauthorized access to third-party APIs.\n\n")
        
        f.write("## Remediation\n")
        f.write("1. Restrict access to sensitive files via web server configuration (e.g., Nginx/Apache `.htaccess` or `nginx.conf`).\n")
        f.write("2. Ensure `.env`, `.git`, and backup files are not deployed to the public web root.\n")
        f.write("3. Implement a strict Content Security Policy (CSP) and proper directory indexing controls.\n")
        
    log(f"Report generated: {report_path}")
    return report_path

def hunt(target):
    log(f"Starting hunt on {target}...")
    
    # High-value paths to check for misconfigurations
    paths_to_check = [
        "/.env", "/.git/HEAD", "/.git/config", "/robots.txt", 
        "/sitemap.xml", "/.well-known/security.txt", "/wp-config.php.bak",
        "/package.json", "/composer.json", "/.aws/credentials"
    ]
    
    findings = []
    for path in paths_to_check:
        exposed, url, snippet = check_endpoint(target, path)
        if exposed:
            log(f"🚨 EXPOSED: {url}")
            findings.append({"path": path, "url": url, "status": "EXPOSED", "snippet": snippet})
        else:
            log(f"[-] Safe/Missing: {url} ({snippet})")
            
    if findings:
        log(f"Found {len(findings)} exposures! Generating Bugcrowd report...")
        report = generate_bugcrowd_report(target, findings)
        return report
    else:
        log(f"No critical exposures found on {target}. Target is hardened.")
        return None

def main():
    log("=== Bugcrowd AI Hunter Online ===")
    # DEFAULT TARGET: Change this to your authorized Bugcrowd/HackerOne target!
    target = "example.com" 
    
    # You can also pass a target via command line: python3 hunter.py target.com
    import sys
    if len(sys.argv) > 1:
        target = sys.argv[1]
        
    report = hunt(target)
    if report:
        print(f"\n✅ HUNT COMPLETE. Submit this report to Bugcrowd:")
        print(f"📄 {report}")
    else:
        print("\n❌ No vulnerabilities found on this target. Try another.")

if __name__ == "__main__":
    main()
