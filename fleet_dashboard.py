#!/usr/bin/env python3
import os, json, glob
from datetime import datetime

LEDGER_DIR = os.path.expanduser("~/constellation25/ledger/")
MICRO_SAAS_DIR = os.path.expanduser("~/constellation25/micro_saas/")

def print_header(title):
    print(f"\n{'='*50}")
    print(f"  {title}")
    print(f"{'='*50}")

def count_items(file_pattern):
    files = glob.glob(os.path.join(LEDGER_DIR, file_pattern))
    return len(files)

def read_json(file_path):
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            return json.load(f)
    return []

def main():
    print("\n🌌 CONSTELLATION25 SOVEREIGN FLEET DASHBOARD 🌌")
    print(f"⏱️  Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 1. Agentik Licenses
    print_header("💰 AGENTIK LICENSES ($25 Cash App)")
    licenses = read_json(os.path.join(LEDGER_DIR, "agentik_licenses.json"))
    print(f"Total Issued: {len(licenses)}")
    if licenses:
        latest = licenses[-1]
        print(f"Latest: {latest.get('license_id')} -> {latest.get('buyer_handle')} (Status: {latest.get('status')})")
        
    # 2. Bugcrowd Bounties
    print_header("🎯 BUGCROWD BOUNTY QUEUE")
    bounties = read_json(os.path.join(LEDGER_DIR, "bugcrowd_submissions.json"))
    print(f"Total Queued: {len(bounties)}")
    if bounties:
        latest = bounties[-1]
        print(f"Latest: {latest.get('submission_id')} -> {latest.get('target')} ({latest.get('vuln_type')})")
        
    # 3. Market Arbitrage
    print_header("📈 TREND ARBITRAGE INTELLIGENCE")
    arbitrage = read_json(os.path.join(LEDGER_DIR, "market_arbitrage.json"))
    if arbitrage:
        latest = arbitrage[-1]
        print(f"Industry Scanned: {latest.get('industry')}")
        print(f"Top Niche Identified: {latest.get('niches', [{}])[0].get('niche')}")
    else:
        print("Awaiting first market scan...")
        
    # 4. Monetization Funnels
    print_header("✍️ COPYWRITER ASSETS (FUNNELS)")
    funnels = count_items("funnel_*.json")
    print(f"Total Funnels Generated: {funnels}")
    
    # 5. Micro-SaaS Factory
    print_header("🏭 MICRO-SAAS FACTORY DEPLOYMENTS")
    saas_tools = glob.glob(os.path.join(MICRO_SAAS_DIR, "*.html"))
    print(f"Total Live HTML Tools: {len(saas_tools)}")
    if saas_tools:
        for tool in saas_tools[-3:]: # Show last 3
            print(f"  - {os.path.basename(tool)}")
            
    print(f"\n{'='*50}")
    print("  FLEET STATUS: AUTONOMOUS & OPERATIONAL")
    print(f"{'='*50}\n")

if __name__ == "__main__":
    main()
