#!/usr/bin/env bash

# ╔══════════════════════════════════════════════════════════════╗
# ║   CONSTELLATION25 INSTALLER v1.0.0                           ║
# ║   17-Agent Sovereign AI Platform                             ║
# ║   By Cygel White | Kre8tive Konceptz                        ║
# ╚══════════════════════════════════════════════════════════════╝

set -e

C25_VERSION="1.0.0"
INSTALL_DIR="${C25_HOME:-$HOME/constellation25}"
GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo ""
echo -e "${CYAN}╔══════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║   CONSTELLATION25 v${C25_VERSION} INSTALLER                      ║${NC}"
echo -e "${CYAN}║   17-Agent Sovereign AI Platform                         ║${NC}"
echo -e "${CYAN}║   By Cygel White | Kre8tive Konceptz                     ║${NC}"
echo -e "${CYAN}╚══════════════════════════════════════════════════════════╝${NC}"
echo ""

# ── Detect platform ──
if [ -d "/data/data/com.termux" ]; then
    PLATFORM="termux"
elif [ "$(uname)" = "Darwin" ]; then
    PLATFORM="macos"
elif [ -f "/etc/debian_version" ]; then
    PLATFORM="debian"
else
    PLATFORM="linux"
fi
echo -e "${GREEN}✓ Platform: $PLATFORM${NC}"

# ── Install system dependencies ──
echo ""
echo "Installing dependencies..."
case "$PLATFORM" in
    termux)
        pkg install -y nodejs git python curl jq 2>/dev/null || true
        ;;
    macos)
        command -v brew >/dev/null 2>&1 || \
            /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
        brew install node git python3 curl jq 2>/dev/null || true
        ;;
    debian)
        sudo apt-get update -qq 2>/dev/null
        sudo apt-get install -y nodejs git python3 curl jq 2>/dev/null || true
        ;;
    *)
        echo -e "${YELLOW}⚠ Please install: nodejs git python3 curl jq${NC}"
        ;;
esac
echo -e "${GREEN}✓ Dependencies ready${NC}"

# ── Clone or update ──
echo ""
if [ -d "$INSTALL_DIR/.git" ]; then
    echo "Updating existing installation..."
    cd "$INSTALL_DIR"
    git pull origin main 2>/dev/null || echo "Using local version"
else
    echo "Cloning Constellation25..."
    # Try both org spellings
    git clone https://github.com/Constillation25/constellation25.git \
        "$INSTALL_DIR" 2>/dev/null || \
    git clone https://github.com/Constellation25/constellation25.git \
        "$INSTALL_DIR" 2>/dev/null || \
    git clone https://github.com/FacePrintPay/constellation25.git \
        "$INSTALL_DIR" 2>/dev/null || {
        echo -e "${YELLOW}Clone failed — using local install${NC}"
        mkdir -p "$INSTALL_DIR"
    }
fi

cd "$INSTALL_DIR"
find . -name "*.sh" -exec chmod +x {} \; 2>/dev/null
find . -name "*.py" -exec chmod +x {} \; 2>/dev/null
echo -e "${GREEN}✓ Installed at: $INSTALL_DIR${NC}"

# ── Setup shell ──
echo ""
SHELL_RC="$HOME/.bashrc"
[ -f "$HOME/.zshrc" ] && SHELL_RC="$HOME/.zshrc"

# Remove old c25 entries
grep -v "C25_HOME\|constellation25\|c25_master\|alias c25" \
    "$SHELL_RC" > "${SHELL_RC}.c25tmp" 2>/dev/null && \
    mv "${SHELL_RC}.c25tmp" "$SHELL_RC" || true

cat >> "$SHELL_RC" << SHELLEOF

# ── Constellation25 ──
export C25_HOME="$INSTALL_DIR"
export PATH="\$C25_HOME:\$C25_HOME/scripts:\$PATH"
alias c25='bash \$C25_HOME/c25_master_control.sh'
alias c25start='bash \$C25_HOME/start_all_agents.sh'
alias c25stop='bash \$C25_HOME/stop_all_agents.sh'
alias c25status='bash \$C25_HOME/status_agents.sh'
alias c25recall='bash \$C25_HOME/../total_recall_fast.sh 2>/dev/null || echo "Install TotalRecall first"'
alias c25push='bash \$C25_HOME/push_to_github.sh'
alias c25tasks='bash \$C25_HOME/task_box.sh'
alias c25help='cat \$C25_HOME/docs/QUICKSTART.md'
alias c25log='tail -f \$C25_HOME/logs/orchestrator_bg.log'
SHELLEOF

echo -e "${GREEN}✓ Shell aliases added to $SHELL_RC${NC}"

# ── Termux boot ──
if [ "$PLATFORM" = "termux" ]; then
    mkdir -p "$HOME/.termux/boot"
    cat > "$HOME/.termux/boot/01-c25-boot.sh" << BOOTEOF
#!/data/data/com.termux/files/usr/bin/bash
LOCK="$HOME/.c25_boot.lock"
[ -f "\$LOCK" ] && exit 0
touch "\$LOCK"
sleep 3
cd "$INSTALL_DIR" && bash start_all_agents.sh >> logs/boot.log 2>&1
trap "rm -f \$LOCK" EXIT
BOOTEOF
    chmod +x "$HOME/.termux/boot/01-c25-boot.sh"
    echo -e "${GREEN}✓ Termux boot integration added${NC}"
fi

# ── Done ──
echo ""
echo -e "${CYAN}╔══════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║   ✅ CONSTELLATION25 INSTALLED!                           ║${NC}"
echo -e "${CYAN}╠══════════════════════════════════════════════════════════╣${NC}"
echo -e "${CYAN}║   Next: source ~/.bashrc && c25                           ║${NC}"
echo -e "${CYAN}╚══════════════════════════════════════════════════════════╝${NC}"
echo ""
echo "  source ~/.bashrc"
echo "  c25"
echo ""
