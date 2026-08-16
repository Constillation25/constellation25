#!/data/data/com.termux/files/usr/bin/env bash
set -euo pipefail
QA="$HOME/constellation25/quick_actions"
mkdir -p "$QA"
TSV="$QA/.index.tsv"; : > "$TSV"

mapfile -t FILES < <({
  find "$HOME" -maxdepth 5 -type f \( -name '*.sh' -o -name '*boot*' -o -name '*agent*' \) \
    ! -path '*/storage/*' ! -path '*/node_modules/*' ! -path '*/.git/*' 2>/dev/null
  find "$HOME/constellation25" "$HOME/c25_ipc" -maxdepth 6 -type f \( -name '*.sh' -o -name '*boot*' -o -name '*agent*' \) \
    ! -path '*/node_modules/*' 2>/dev/null
} | sort -u)

mapfile -t DIRS < <(find "$HOME" -maxdepth 5 -type d \( -name '*agent*' -o -name '*boot*' \) \
  ! -path '*/storage/*' ! -path '*/node_modules/*' 2>/dev/null | sort -u)

desc_of() {
  local f="$1" d=""
  d=$(grep -m1 -E '^#[[:space:]]*(DESC|Description|Purpose):' "$f" 2>/dev/null | sed -E 's/^#[[:space:]]*(DESC|Description|Purpose)://I' || true)
  [ -z "$d" ] && d=$(awk 'NR==1 && /^#!/{next} /^#/{sub(/^#+[ \t]*/,""); if (length($0)>8) {print; exit}}' "$f" 2>/dev/null || true)
  [ -z "$d" ] && d=$(basename "$f" | sed -E 's/\.(sh|py|json)$//; s/[_-]+/ /g')
  d=${d//$'\t'/ }
  printf '%s' "$d" | head -c 160
}
type_of() {
  case "$(basename "$1")" in
    *boot*) echo boot;;
    *agent*) echo agent;;
    *.sh) echo sh;;
    *) echo file;;
  esac
}

i=0
for f in "${FILES[@]}"; do
  i=$((i+1))
  printf '%03d\t%s\t%s\t%s\n' "$i" "$f" "$(type_of "$f")" "$(desc_of "$f")" >> "$TSV"
done

python3 - "$TSV" "$QA/index.json" "$QA/index.md" "${DIRS[*]:-}" <<'PY'
import json, sys
from pathlib import Path
tsv, idx, md, dirs = sys.argv[1], Path(sys.argv[2]), Path(sys.argv[3]), (sys.argv[4] or "").split()
rows = [l.rstrip("\n").split("\t", 3) for l in open(tsv) if l.strip()]
data = [{"id":r[0],"path":r[1],"type":r[2],"desc":r[3],"run":f"#run {r[0]}"} for r in rows]
idx.write_text(json.dumps(data, indent=1))
md.write_text("# C25 Quick Actions\n\n" +
  "\n".join(f"- [#{r[0]}] `{r[1]}` — {r[3]} (`#run {r[0]}`)" for r in rows) +
  "\n\n## Agent/Boot Directories\n" + "\n".join(f"- `{d}`" for d in dirs) + "\n")
print("=== C25 QUICK ACTIONS ===")
for r in rows:
    print(f"[#{r[0]}] {r[1].split('/')[-1]} — {r[3]} — #run {r[0]}")
print("\n=== AGENT/BOOT DIRS ===")
for d in dirs: print(f"[dir] {d}")
PY
