#!/data/data/com.termux/files/usr/bin/env bash
set -euo pipefail
DB="$HOME/constellation25/db/c25.db"
QA="$HOME/constellation25/quick_actions"
MODE="${1:-}"

case "$MODE" in
--all)
python3 - "$DB" "$QA" <<'PY'
import os, sys, sqlite3
from pathlib import Path
from collections import Counter, defaultdict
db, qa = sys.argv[1], Path(sys.argv[2])
EXT={"sh":"code","py":"code","js":"code","ts":"code","html":"code","css":"code","sql":"data",
"md":"docs","doc":"docs","docx":"docs","pdf":"docs","txt":"docs","mht":"docs",
"jpg":"media","jpeg":"media","png":"media","gif":"media","mp4":"media","webm":"media","mp3":"media","webarchive":"media",
"csv":"data","parquet":"data","db":"data","sqlite":"data","jsonl":"data",
"zip":"archives","tar":"archives","gz":"archives","7z":"archives","rar":"archives",
"json":"config","toml":"config","yaml":"config","yml":"config","conf":"config"}
PURPOSE=[("vault","secure storage vault"),("gdrive","Google Drive mirror"),("mail","email data"),
("agent","planetary agent workspace"),("ipc","inter-agent task queue"),("db","databases"),
("cache","throwaway cache — purge candidate"),("backup","backups"),("download","downloads"),
("camera","camera media"),("whatsapp","WhatsApp media"),("court","legal/VideoCourts assets"),
("faceprint","FacePrintPay assets"),("constellation","C25 core infra"),("report","reports")]
cat_of=lambda e: EXT.get(e,"other")
def purpose_of(p):
    pl=p.lower()
    for kw,pu in PURPOSE:
        if kw in pl: return pu
    return "general storage"
def human(b):
    for u in ["B","KB","MB","GB","TB"]:
        if b<1024: return f"{b:.1f}{u}"
        b/=1024
    return f"{b:.1f}PB"

roots=[Path.home()/"constellation25", Path.home()/"c25_ipc", Path.home()/"storage/shared"]
con=sqlite3.connect(db); con.execute("DELETE FROM file_inventory")
rows=[]; n=0
for root in roots:
    for dp,_,fns in os.walk(root):
        for fn in fns:
            try: st=os.stat(os.path.join(dp,fn))
            except OSError: continue
            e=fn.rsplit(".",1)[-1].lower() if "." in fn else ""
            rows.append((os.path.join(dp,fn),st.st_size,int(st.st_mtime),e,cat_of(e)))
            n+=1
            if n%50000==0: print(f"[progress] {n} files indexed")
con.executemany("INSERT OR REPLACE INTO file_inventory(path,size,mtime,ext,category) VALUES(?,?,?,?,?)",rows)
con.commit()
tot=sum(r[1] for r in rows)
cats=Counter(r[4] for r in rows); csize=defaultdict(int)
for r in rows: csize[r[4]]+=r[1]
dsize=defaultdict(int); dcnt=defaultdict(int)
for r in rows:
    parts=Path(r[0]).parts
    for d in range(3,min(len(parts),7)):
        k="/".join(parts[:d]); dsize[k]+=r[1]; dcnt[k]+=1
L=[f"# C25 Storage Digest\n\nTotal: {n} files, {human(tot)}\n\n## Categories\n"]
for c,cnt in cats.most_common(): L.append(f"- {c}: {cnt} files, {human(csize[c])}")
L.append("\n## Top 20 dirs by size\n")
for k,v in sorted(dsize.items(), key=lambda x:-x[1])[:20]:
    L.append(f"- `{k}` — {human(v)}, {dcnt[k]} files — likely: {purpose_of(k)}")
(qa/"digest.md").write_text("\n".join(L)+"\n")
print("\n".join(L))
print(f"\n[explain] indexed {n} files -> file_inventory + digest.md")
con.close()
PY
;;
find)
KW="${2:-}"
sqlite3 "$DB" "SELECT category, printf('%.1f MB', size/1048576.0), path FROM file_inventory WHERE path LIKE '%${KW}%' LIMIT 50;"
;;
*)
python3 - "$MODE" <<'PY'
import os, sys
from pathlib import Path
from collections import Counter
p=Path(sys.argv[1]).expanduser()
EXT={"sh":"shell script","py":"python script","md":"markdown doc","docx":"Word doc","mht":"web-archive conversation","json":"JSON data/config","jpg":"image","png":"image","mp4":"video","zip":"archive","db":"sqlite database","pdf":"PDF doc","html":"web page","css":"stylesheet","sql":"SQL script","webarchive":"saved web page"}
PURPOSE=[("vault","secure storage"),("gdrive","Google Drive mirror"),("mail","email"),("agent","agent workspace"),("ipc","task queue"),("cache","cache — purge candidate"),("backup","backup"),("court","legal assets"),("faceprint","FacePrintPay assets"),("constellation","C25 core infra")]
def human(b):
    for u in ["B","KB","MB","GB","TB"]:
        if b<1024: return f"{b:.1f}{u}"
        b/=1024
    return f"{b:.1f}PB"
def purpose_of(s):
    sl=s.lower()
    for kw,pu in PURPOSE:
        if kw in sl: return pu
    return "general storage"
if p.is_file():
    st=p.stat(); e=p.suffix[1:].lower()
    print(f"{p} is a {EXT.get(e, e or 'unknown')} file ({human(st.st_size)}). Likely purpose: {purpose_of(str(p))}.")
elif p.is_dir():
    cnt=0; size=0; exts=Counter()
    for dp,_,fns in os.walk(p):
        for fn in fns:
            try: st=os.stat(os.path.join(dp,fn))
            except OSError: continue
            cnt+=1; size+=st.st_size
            exts[fn.rsplit('.',1)[-1].lower() if '.' in fn else '(none)']+=1
            if cnt>=20000: break
        if cnt>=20000: break
    top=", ".join(f"{e}({c})" for e,c in exts.most_common(5))
    note="" if cnt<20000 else " (sampled 20k)"
    print(f"{p} is a directory with {cnt}{note} files totaling {human(size)}. Dominant types: {top}. Likely purpose: {purpose_of(str(p))}.")
else:
    print(f"{p} does not exist.")
PY
;;
esac
