#!/data/data/com.termux/files/usr/bin/bash
# ═══════════════════════════════════════════════════
# C25 SOVEREIGN AI ECOSYSTEM — BOOTSTRAP & PROVISION
# Idempotent, atomic, zero-scatter installation kit
# ═══════════════════════════════════════════════════

set -e # Fail fast on any error

C='\033[0;36m'; G='\033[0;32m'; Y='\033[1;33m'; R='\033[0;31m'; N='\033[0m'
HOME_DIR="/data/data/com.termux/files/home"
PREFIX="/data/data/com.termux/files/usr"

echo -e "${C}═══ C25 BOOTSTRAP INITIATED ═══${N}"
echo -e "${Y}Target: Termux Environment (${PREFIX})${N}"

# ── 1. SYSTEM PACKAGE PROVISIONING ──
echo -e "\n${Y}── [1/5] Provisioning System Packages ──${N}"
pkg update -y && pkg upgrade -y
pkg install -y python nodejs git curl jq rsync nano inotify-tools openssh termux-api

# ── 2. DIRECTORY SCAFFOLDING (Zero-Scatter) ──
echo -e "\n${Y}── [2/5] Scaffolding C25 Directory Tree ──${N}"
mkdir -p "$HOME_DIR/constellation25"/{core,commz,bashbox/sandbox,logs,projects}
mkdir -p "$HOME_DIR/c25_ipc"/{pending,completed,archive}
mkdir -p "$HOME_DIR/c25_store"

# ── 3. PYTHON & NODE DEPENDENCIES ──
echo -e "\n${Y}── [3/5] Resolving Language Dependencies ──${N}"
# Python (Force local user install to avoid root/permission issues in Termux)
pip3 install --upgrade pip --break-system-packages 2>/dev/null || true
pip3 install --user requests urllib3 --break-system-packages 2>/dev/null || true

# Node.js (Global install in Termux prefix, no cache to save space)
if [ -f "$HOME_DIR/constellation25/package.json" ]; then
    cd "$HOME_DIR/constellation25"
    npm install --no-cache-dir --omit=dev
fi

# ── 4. SHELL INTEGRATION & ALIASES ──
echo -e "\n${Y}── [4/5] Injecting Shell Integration ──${N}"
C25_ALIASES="# ── C25 SOVEREIGN AI ALIASES ──
alias c25-start='python3 ~/constellation25/core/c25_code_explorer.py'
alias c25-watch='bash ~/constellation25/core/commz/c25-watcher.sh &'
alias c25-notify='bash ~/constellation25/core/commz/c25-notify.sh'
alias c25-purge='bash ~/constellation25/core/c25-snapshot-purge.sh'
export PATH=\"\$HOME/constellation25/core:\$PATH\"
"

# Append to .bashrc only if not already present
if ! grep -q "C25 SOVEREIGN AI ALIASES" "$HOME_DIR/.bashrc" 2>/dev/null; then
    echo "$C25_ALIASES" >> "$HOME_DIR/.bashrc"
    echo -e "${G}✅ Shell aliases injected into ~/.bashrc${N}"
else
    echo -e "${G}✅ Shell aliases already present (skipped)${N}"
fi

# ── 5. PERMISSIONS & FINALIZATION ──
echo -e "\n${Y}── [5/5] Setting Executable Permissions ──${N}"
find "$HOME_DIR/constellation25" -name "*.sh" -exec chmod +x {} \;
find "$HOME_DIR/constellation25" -name "*.py" -exec chmod +x {} \;

echo -e "\n${C}═══ C25 BOOTSTRAP COMPLETE ═══${N}"
echo -e "${G}✅ Ecosystem is provisioned and ready.${N}"
echo -e "${Y}⚠️ ACTION REQUIRED: Run 'source ~/.bashrc' or restart Termux to activate aliases.${N}"
