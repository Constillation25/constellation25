#!/bin/bash
echo "[C25 Dispatcher] Watching IPC queue..."
while true; do
  for f in ~/c25_ipc/pending/*.json; do
    [ -e "$f" ] || continue
    echo "[C25] Processing $(basename $f)"
    mv "$f" "${f%.json}.completed"
  done
  sleep 5
done
