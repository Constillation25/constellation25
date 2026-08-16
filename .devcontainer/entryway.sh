#!/bin/bash
# C25 Dev Container Entryway - Atomic Agent & Skill Loader
# Invoked on container boot via devcontainer.json postStartCommand

C25_ROOT="$HOME/constellation25"
DC_ROOT="$C25_ROOT/.devcontainer"
LOG="$DC_ROOT/logs/entryway.log"

echo "═══════════════════════════════════════════" | tee -a "$LOG"
echo "[$(date '+%F %T')] C25 DevContainer Entryway initializing..." | tee -a "$LOG"

# Load all agent.sh hooks
for agent in "$DC_ROOT/agents/"*.sh; do
  [ -f "$agent" ] || continue
  name=$(basename "$agent" .sh)
  echo "[$(date '+%F %T')] Loading agent: $name" | tee -a "$LOG"
  bash "$agent" --entryway 2>>"$LOG" || echo "  ⚠ $name failed entryway hook" | tee -a "$LOG"
done

# Load all .skills manifests
for skill in "$DC_ROOT/skills/"*.skills; do
  [ -f "$skill" ] || continue
  name=$(basename "$skill")
  echo "[$(date '+%F %T')] Registering skill: $name" | tee -a "$LOG"
  # Skills are manifests - source them into env if they're bash-compatible
  if head -1 "$skill" | grep -q "^#!"; then
    bash "$skill" --register 2>>"$LOG" || echo "  ⚠ $skill failed registration" | tee -a "$LOG"
  fi
done

echo "[$(date '+%F %T')] ✅ Entryway complete. Fleet ready." | tee -a "$LOG"
echo "═══════════════════════════════════════════" | tee -a "$LOG"
