#!/usr/bin/env bash
set -euo pipefail
BASE="$HOME/constellation25/research/lut-inference"
PKG="$BASE/package"
mkdir -p "$PKG"
MANIFEST="$PKG/manifest.json"
TARBALL="$PKG/c25-lut-research-v1.tar.gz"
CHECKSUM="$PKG/SHA256SUMS"

echo '{"build_time":"'$(date -u +%FT%TZ)'","files":[]}' > "$MANIFEST"
cd "$BASE"

FILES=$(find . -type f -not -path './package/*' -not -path './.git/*' | sort)
echo "[" > "$MANIFEST.tmp"
FIRST=true
for f in $FILES; do
  HASH=$(sha256sum "$f" | awk '{print $1}')
  SIZE=$(stat -c%s "$f" 2>/dev/null || stat -f%z "$f" 2>/dev/null || echo 0)
  if [ "$FIRST" = true ]; then FIRST=false; else echo "," >> "$MANIFEST.tmp"; fi
  echo "  {\"path\":\"$f\",\"sha256\":\"$HASH\",\"size\":$SIZE}" >> "$MANIFEST.tmp"
done
echo "]" >> "$MANIFEST.tmp"

python3 -c "
import json
m = json.load(open('$PKG/manifest.json'))
m['files'] = json.load(open('$MANIFEST.tmp'))
m['total_files'] = len(m['files'])
m['total_bytes'] = sum(f['size'] for f in m['files'])
json.dump(m, open('$MANIFEST','w'), indent=2)
print(f'Manifest: {m[\"total_files\"]} files, {m[\"total_bytes\"]} bytes')
"
rm -f "$MANIFEST.tmp"

tar czf "$TARBALL" --exclude='./package' .
sha256sum "$TARBALL" > "$CHECKSUM"
TAR_SIZE=$(stat -c%s "$TARBALL" 2>/dev/null || stat -f%z "$TARBALL" 2>/dev/null || echo "?")
echo "[+] Tarball built: $TARBALL ($TAR_SIZE bytes)"
echo "[+] Checksum: $(cat $CHECKSUM)"
echo "[+] Manifest: $MANIFEST"
ls -lh "$PKG/"
