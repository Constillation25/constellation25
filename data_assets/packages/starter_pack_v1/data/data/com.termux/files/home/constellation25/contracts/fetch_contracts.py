#!/usr/bin/env python3
import requests, bs4, json, sys, time, re, xml.etree.ElementTree as ET
from urllib.parse import urljoin

SOURCES = [
    {"name": "remoteok_ai",    "url": "https://remoteok.com/api?tag=ai", "type": "json"},
    {"name": "weworkremotely", "url": "https://weworkremotely.com/categories/remote-programming-jobs.rss", "type": "rss"},
    {"name": "hackerone",      "url": "https://hackerone.com/opportunities", "type": "scrape_permitted"}
]

def clean_html(text): return re.sub(r'<[^>]+>', '', text or '').strip()

def fetch():
    contracts = []
    for src in SOURCES:
        try:
            r = requests.get(src["url"], headers={"User-Agent": "C25-ContractBot/1.0"}, timeout=15)
            r.raise_for_status()
            if src["type"] == "json":
                data = r.json()
                for j in (data if isinstance(data, list) else []):
                    contracts.append({"source": src["name"], "title": j.get("title",""), "desc": str(j.get("description","")), "url": j.get("url",""), "budget": ""})
            elif src["type"] == "rss":
                root = ET.fromstring(r.text)
                for item in root.findall('.//item'):
                    t = item.findtext('title', '').strip()
                    d = clean_html(item.findtext('description'))
                    l = item.findtext('link', '')
                    if t: contracts.append({"source": src["name"], "title": t, "desc": d, "url": l, "budget": ""})
            elif src["type"] == "scrape_permitted":
                soup = bs4.BeautifulSoup(r.text, "html.parser")
                for a in soup.select("a.opportunity-title, a.job-link, a[href*='/contract/']"):
                    contracts.append({"source": src["name"], "title": a.text.strip() or "Untitled", "desc": "", "url": urljoin(src["url"], a.get("href","")), "budget": ""})
            time.sleep(1.5)
        except Exception as e:
            print(f"[WARN] {src['name']} failed: {e}", file=sys.stderr)
    print(json.dumps(contracts, indent=2))

if __name__ == "__main__": fetch()
