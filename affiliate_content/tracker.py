#!/usr/bin/env python3
import json, os, time
from pathlib import Path

TRACK_FILE = Path.home() / "constellation25/affiliate_content/performance.json"

def log_click(link, source):
    data = {}
    if TRACK_FILE.exists():
        try: data = json.loads(TRACK_FILE.read_text())
        except: data = {}
    data.setdefault(link, {"clicks": 0, "source": source, "last_click": 0})
    data[link]["clicks"] += 1
    data[link]["last_click"] = int(time.time())
    TRACK_FILE.parent.mkdir(parents=True, exist_ok=True)
    TRACK_FILE.write_text(json.dumps(data, indent=2))
    return data[link]["clicks"]

if __name__ == "__main__":
    if TRACK_FILE.exists():
        data = json.loads(TRACK_FILE.read_text())
        total = sum(v["clicks"] for v in data.values())
        print(f"Total tracked clicks: {total}")
    else:
        print("No clicks tracked yet.")
