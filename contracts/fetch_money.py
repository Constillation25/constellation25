#!/usr/bin/env python3
import requests, json, sys, time, re, xml.etree.ElementTree as ET
SOURCES = [
    {"name":"reddit_forhire","url":"https://www.reddit.com/r/forhire/new.json?limit=25","type":"reddit"},
    {"name":"reddit_freelance","url":"https://www.reddit.com/r/freelance_forhire/new.json?limit=25","type":"reddit"},
    {"name":"fiverr_ai","url":"https://www.fiverr.com/rss/level_two/programming-tech/ai-services","type":"rss"},
    {"name":"gumroad","url":"https://gumroad.com/api/v2/discover?query=ai+automation+consulting","type":"gumroad"}
]
def clean(t): return re.sub(r'\s+',' ',t or '').strip()
def fetch():
    results=[]
    for s in SOURCES:
        try:
            r=requests.get(s["url"],headers={"User-Agent":"C25-MoneyBot/1.0"},timeout=15);r.raise_for_status()
            if s["type"]=="reddit":
                for c in r.json().get("data",{}).get("children",[]):
                    p=c.get("data",{});t=p.get("title","");st=p.get("selftext","")
                    if t and any(k in t.lower() for k in ["hire","contract","looking for","need","seeking"]):
                        results.append({"source":"reddit","title":clean(t),"desc":clean(st[:150]),"url":f"https://reddit.com{p.get('permalink','')}","budget":""})
            elif s["type"]=="rss":
                root=ET.fromstring(r.text)
                for i in root.findall('.//item'):
                    t=i.findtext('title','').strip();d=clean(i.findtext('description'));l=i.findtext('link','')
                    if t and any(k in t.lower() for k in ["ai","automation","script","bot","agent"]):
                        results.append({"source":"fiverr","title":t,"desc":d[:150],"url":l,"budget":""})
            elif s["type"]=="gumroad":
                for prod in r.json().get("products",[])[:10]:
                    t=prod.get("name","");d=prod.get("description","");u=prod.get("short_url","")
                    if any(k in (t+d).lower() for k in ["consulting","automation","ai","script"]):
                        results.append({"source":"gumroad","title":clean(t),"desc":clean(d[:150]),"url":u,"budget":prod.get("price")})
            time.sleep(1.2)
        except Exception as e: print(f"[WARN] {s['name']}: {e}",file=sys.stderr)
    print(json.dumps(results,indent=2))
if __name__=="__main__": fetch()
