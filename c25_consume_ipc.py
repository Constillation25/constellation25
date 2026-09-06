import json, sqlite3, shutil
from pathlib import Path
Q = Path.home()/"c25_ipc/pending"
D = Path.home()/"c25_ipc/done"; D.mkdir(parents=True, exist_ok=True)
DB = Path.home()/"constellation25/db/c25.db"
con = sqlite3.connect(DB)
n = 0
for pf in sorted(Q.glob("aquarius_ingest_*.json")):
    data = json.load(open(pf))
    entries = data.get("payload", {}).get("files", [])
    con.executemany("INSERT INTO aquarius_entries (task_id, data) VALUES (?,?)", [(data.get("task_id"), json.dumps(e)) for e in entries])
    con.commit(); shutil.move(str(pf), str(D/pf.name)); n += len(entries)
con.close()
if n: print(f"[+] consumed {n} entries")
