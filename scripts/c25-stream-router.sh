#!/data/data/com.termux/files/usr/bin/bash
# c25-stream-router.sh | Forge | route backups -> repos by code type
set -euo pipefail
C25="$HOME/constellation25"; REPOS="$C25/repos"; STAGE="$C25/unrouted"; mkdir -p "$STAGE"
rf() { case "$1" in
  html|css|jsx|tsx|vue) echo ui;; js|ts|mjs|cjs) echo lib;; sh|bash|py) echo tools;;
  yml|yaml) echo .github;; md|txt) echo docs;; sql) echo migrations;;
  test|spec) echo test;; node|wasm|ffi) echo bindings;; json) echo templates;; *) echo "";; esac; }
find ~/backups -type f | while IFS= read -r f; do
  ext="${f##*.}"; base="$(basename "$f")"
  case "$base" in *.test.*|*.spec.*) ext="test";; esac
  mod=$(echo "$f" | sed "s|$HOME/backups/||;s|/.*||")
  [ -d "$REPOS/$mod" ] || mod=""
  d=$(rf "$ext")
  if [ -n "$d" ] && [ -n "$mod" ]; then mkdir -p "$REPOS/$mod/$d"; cp -n "$f" "$REPOS/$mod/$d/"
  else mkdir -p "$STAGE/$ext"; cp -n "$f" "$STAGE/$STAGE/$ext/" 2>/dev/null || cp -n "$f" "$STAGE/$ext/"; fi
done
echo "[FORGE] routing done; unrouted: $(find "$STAGE" -type f | wc -l)"
