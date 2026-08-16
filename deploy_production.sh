#!/data/data/com.termux/files/usr/bin/bash
# ============================================================
# CONSTELLATION25 MASTER PRODUCTION DEPLOYMENT
# Runs all phases in sequence
# ============================================================

echo "════════════════════════════════════════════════════════════╗"
echo "║   CONSTELLATION25 PRODUCTION DEPLOYMENT                   ║"
echo "║   TotalRecall Builder Agent Mesh                          ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Phase 1: Start Redis
echo "[1/5] Starting Redis..."
redis-server --daemonize yes 2>/dev/null || echo "[!] Redis not installed, using fallback queue"
echo ""

# Phase 2: Run file walker
echo "[2/5] Running file walker agent..."
python3 ~/constellation25/modules/totalrecall_mesh/agents/file_walker.py
echo ""

# Phase 3: Git sync
echo "[3/5] Syncing git repos..."
bash ~/constellation25/scripts/git_sync.sh
echo ""

# Phase 4: Stream deploy
echo "[4/5] Streaming deployment..."
python3 ~/constellation25/modules/totalrecall_mesh/orchestrator/streaming_deploy.py
echo ""

# Phase 5: Run TotalRecall orchestrator
echo "[5/5] Starting TotalRecall orchestrator..."
python3 ~/constellation25/modules/totalrecall_mesh/orchestrator/orchestrator.py
echo ""

echo "╔════════════════════════════════════════════════════════════╗"
echo "║   DEPLOYMENT COMPLETE                                     ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "Next steps:"
echo "  1. Check logs: ~/constellation25/logs/"
echo "  2. View mesh status: python3 ~/constellation25/modules/totalrecall_mesh/orchestrator/orchestrator.py"
echo "  3. Monitor queue: redis-cli LLEN totalrecall:tasks"
