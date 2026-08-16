import asyncio, os, json
import aiohttp
from bs4 import BeautifulSoup
from urllib.parse import urljoin

MANIFEST = os.path.expanduser("~/constellation25/html_workspace/core_production_html.txt")
HOME = os.path.expanduser("~")
BASE = "http://127.0.0.1:8080/"
REPORT = os.path.expanduser("~/constellation25/html_workspace/e2e_native_report.json")

async def validate(session, path):
    rel = path.replace(HOME, "").lstrip("/")
    url = urljoin(BASE, rel)
    errors = []
    try:
        async with session.get(url, timeout=10) as resp:
            if resp.status != 200:
                return {"file": path, "url": url, "status": resp.status, "errors": [f"HTTP {resp.status}"], "passed": False}
            html = await resp.text()

        soup = BeautifulSoup(html, 'html.parser')

        # Verify all external JS resolves
        for s in soup.find_all('script', src=True):
            asset_url = urljoin(url, s['src'])
            try:
                async with session.head(asset_url, timeout=5) as r:
                    if r.status != 200: errors.append(f"BROKEN JS: {s['src']} ({r.status})")
            except: errors.append(f"TIMEOUT JS: {s['src']}")

        # Verify all CSS resolves
        for l in soup.find_all('link', rel='stylesheet'):
            href = l.get('href')
            if href:
                asset_url = urljoin(url, href)
                try:
                    async with session.head(asset_url, timeout=5) as r:
                        if r.status != 200: errors.append(f"BROKEN CSS: {href} ({r.status})")
                except: errors.append(f"TIMEOUT CSS: {href}")

        # Verify images
        for img in soup.find_all('img', src=True):
            asset_url = urljoin(url, img['src'])
            try:
                async with session.head(asset_url, timeout=5) as r:
                    if r.status != 200: errors.append(f"BROKEN IMG: {img['src']} ({r.status})")
            except: pass

        return {"file": path, "url": url, "status": resp.status, "errors": errors, "passed": len(errors) == 0}
    except Exception as e:
        return {"file": path, "url": url, "status": "EXCEPTION", "errors": [str(e)], "passed": False}

async def main():
    with open(MANIFEST) as f:
        paths = [l.strip() for l in f if l.strip()]

    results = []
    connector = aiohttp.TCPConnector(limit=20)
    async with aiohttp.ClientSession(connector=connector) as session:
        sem = asyncio.Semaphore(20)
        async def bound(p):
            async with sem: return await validate(session, p)
        results = await asyncio.gather(*[bound(p) for p in paths])

    with open(REPORT, 'w') as f: json.dump(results, f, indent=2)
    passed = sum(1 for r in results if r["passed"])
    print(f"✅ Native E2E Complete: {passed}/{len(results)} passed.")
    print(f"📄 Report: {REPORT}")

if __name__ == "__main__":
    asyncio.run(main())
