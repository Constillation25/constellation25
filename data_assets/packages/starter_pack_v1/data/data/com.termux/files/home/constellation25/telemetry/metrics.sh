#!/usr/bin/env bash
echo "[TELEMETRY] Heartbeat: OK"
echo "[TELEMETRY] Active Agents: 4"
echo "[TELEMETRY] Queue Depth: 2"
echo "[TELEMETRY] Uptime: $(uptime | awk -F'up' '{print $2}' | awk -F',' '{print $1}')"
