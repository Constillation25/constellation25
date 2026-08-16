import sys
from pathlib import Path

def view_file(filepath):
    path = Path(filepath).expanduser().resolve()
    if not path.exists():
        print("[!] File not found:", path)
        return
    
    sep = "=" * 60
    print("\n" + sep)
    print(" FILE:", path.name)
    print(" PATH:", path)
    print(" SIZE:", path.stat().st_size, "bytes")
    print(sep + "\n")
    
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            print(f.read())
    except Exception as e:
        print("[!] Error reading:", e)
    
    print("\n" + sep + "\n")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: c25_open <filepath>")
    else:
        view_file(sys.argv[1])