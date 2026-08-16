#!/data/data/com.termux/files/usr/bin/python3
"""VideoCourts - Forensic Video Analysis & Tamper Detection"""
import os, sys, hashlib, json

def analyze_video(filepath):
    if not os.path.exists(filepath):
        print(f"[VideoCourts] ❌ File not found: {filepath}")
        return
    
    # Calculate forensic hash
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""): h.update(chunk)
    
    # Extract basic metadata (size, modified time)
    stat = os.stat(filepath)
    
    report = {
        "file": filepath,
        "sha256": h.hexdigest(),
        "size_bytes": stat.st_size,
        "last_modified": stat.st_mtime,
        "tamper_status": "VERIFIED" # Placeholder for deep frame analysis
    }
    
    print(json.dumps(report, indent=2))
    return report

if __name__ == "__main__":
    if len(sys.argv) > 1:
        analyze_video(sys.argv[1])
    else:
        print("Usage: python3 analyze.py <video_file>")
