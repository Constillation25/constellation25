#!/bin/bash
# Neo Morphious - Adaptive Runtime Mutator
# Monitors agent health, mutates failing agents, hot-swaps modules atomically.
AGENT_DIR="$HOME/constellation25/agents/neo_morphious"
IPC="$HOME/c25_ipc/pending"
LOG="$HOME/constellation25/logs/neo_morphious.log"

echo "[$(date '+%F %T')] Neo Morphious online. Scanning for drift..." >> "$LOG"

# Watch for mutation requests in IPC
for task in "$IPC"/mutation_*.json; do
  [ -f "$task" ] || continue
  echo "[$(date '+%F %T')] Mutation request: $(basename "$task")" >> "$LOG"
  mkdir -p "$IPC/processing"
  mv "$task" "$IPC/processing/"
done
