#!/usr/bin/env python3
import requests, json, sys, time, re
from bs4 import BeautifulSoup

SOURCES = [
    {
        "name": "reddit_forhire",
        "url": "https://www.reddit.com/r/forhire/new.json?limit=25",
        "type": "reddit_json",
        "headers": {"User-Agent": "C25-Bot/1.0"}
    },
    {
        "name": "reddit_freelance_forhire",
        "url": "https://www.reddit.com/r/freelance_forhire/new.json?limit=25",
        "type": "reddit_json",
        "headers": {"User-Agent": "C25-Bot/1.0"}
    },
    {
        "name": "fiverr_services",
        "url": "https://www.fiverr.com/rss/level_two/programming-tech/ai-services",
        "type": "rss",
        "headers": {}
    },
    {
        "name": "gumroad_discover",
        "url": "https://gumroad.com/api/v2/discover?query=ai+automation+consulting",
        "type": "gumroad_json",
        "headers": {"User-Agent": "C25-Bot/1.0"}
    }
]

def clean(t): return re.sub(r'\s+', ' ', t or '').strip()

def fetch_reddit(url, headers):
    r = requests.get(url, headers=headers, timeout=15)
    r.raise_for_status()
    data = r.json()
    results = []
    for child in data.get("data", {}).get("children", []):
        post = child.get("data", {})
        title = post.get("title", "")
        selftext = post.get("selftext", "")
        if title and ("hire" in title.lower() or "contract" in title.lower() or "looking for" in title.lower()):
            results.append({
                "source": "reddit",
                "title": clean(title),
                "desc": clean(selftext[:200]),
                "url": f"https://reddit.com{post.get('permalink','')}",
                "budget": ""
            })
    return results

def fetch_rss(url):
    import xml.etree.ElementTree as ET
    r = requests.get(url, timeout=15)
    r.raise_for_status()
    root = ET.fromstring(r.text)
    results = []
    for item in root.findall('.//item'):
        t = item.findtext('title', '').strip()
        d = clean(item.findtext('description'))
        l = item.findtext('link', '')
        if t and any(k in t.lower() for k in ["ai","automation","script","bot","agent"]):
            results.append({"source":"fiverr","title":t,"desc":d[:150],"url":l,"budget":""})
    return results

def fetch_gumroad(url, headers):
    r = requests.get(url, headers=headers, timeout=15)
    r.raise_for_status()
    data = r.json()
    results = []
    for prod in data.get("products", [])[:10]:
        title = prod.get("name","")
        desc = prod.get("description","")
        url_p = prod.get("short_url","")
        if any(k in (title+desc).lower() for k in ["consulting","automation","ai","script","bot"]):
            results.append({"source":"gumroad","title":clean(title),"desc":clean(desc[:150]),"url":url_p,"budget":prod.get("price")})
    return results

def main():
    all_contracts = []
    for src in SOURCES:
        try:
            if src["type"] == "reddit_json":
                all_contracts.extend(fetch_reddit(src["url"], src["headers"]))
            elif src["type"] == "rss":
                all_contracts.extend(fetch_rss(src["url"]))
            elif src["type"] == "gumroad_json":
                all_contracts.extend(fetch_gumroad(src["url"], src["headers"]))
            time.sleep(1.2)
        except Exception as e:
            print(f"[WARN] {src['name']} failed: {e}", file=sys.stderr)
    print(json.dumps(all_contracts, indent=2))

if __name__ == "__main__": main()
