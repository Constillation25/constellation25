#!/usr/bin/env python3
import os, csv, time, random, requests
from bs4 import BeautifulSoup
from datetime import datetime

TARGETS_FILE = os.path.expanduser("~/constellation25/projects/tax_delinquency/targets/active_counties.txt")
MASTER_CSV = os.path.expanduser("~/constellation25/projects/tax_delinquency/data/master_delinquent_taxes.csv")
LOG_FILE = os.path.expanduser("~/constellation25/projects/tax_delinquency/logs/mercury_scan.log")

def log(msg):
    with open(LOG_FILE, "a") as f: 
        f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}\n")

def scrape(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/115.0.0.0"}
        r = requests.get(url, headers=headers, timeout=10)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, 'lxml')
        rows = soup.find_all('tr')
        return f"Success: Found {len(rows)} table rows."
    except Exception as e:
        return f"Error: {str(e)}"

if not os.path.exists(MASTER_CSV):
    with open(MASTER_CSV, "w") as f:
        f.write("Timestamp,State,County,Parcel_ID,Property_Address,Owner_Name,Delinquent_Amount,Listing_URL,Source_Type\n")

with open(TARGETS_FILE, "r") as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith("#"):
            parts = line.split("|")
            if len(parts) == 4:
                state, county, url, stype = parts
                log(f"Scanning {county}, {state}...")
                result = scrape(url)
                log(f"Result: {result}")
                time.sleep(random.uniform(2.0, 4.0))
log("Scan complete.")
