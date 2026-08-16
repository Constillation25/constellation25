#!/data/data/com.termux/files/usr/bin/bash
# ============================================================
# CONSTELLATION25 GIT SYNC SCRIPT
# Syncs all repos without downloading - streams code
# ============================================================

echo "[*] CONSTELLATION25 GIT SYNC STARTING..."
echo "[*] Mode: Stream (no full clone)"
echo ""

# Configuration
BASE_DIR="$HOME/constellation25"
REPOS_DIR="$BASE_DIR/repos"
LOG_FILE="$BASE_DIR/logs/git_sync_$(date +%Y%m%d_%H%M%S).log"

mkdir -p "$REPOS_DIR" "$BASE_DIR/logs"

# List of repos to sync (add your 299 repos here)
REPOS=(
    "FacePrintPay/constellation25"
    "FacePrintPay/videocourts"
    "FacePrintPay/mybuyo"
    "FacePrintPay/commz"
    "FacePrintPay/pathos"
    # Add remaining 294 repos...
)

# Function to sync a repo (stream mode)
sync_repo() {
    local repo=$1
    local repo_name=$(basename "$repo")
    local repo_path="$REPOS_DIR/$repo_name"
    
    echo "[SYNC] $repo"
    
    if [ -d "$repo_path/.git" ]; then
        # Repo exists, pull latest
        cd "$repo_path"
        git pull --rebase --autostash 2>&1 | tee -a "$LOG_FILE"
        echo "[✓] Pulled: $repo_name"
    else
        # Clone with depth 1 (shallow clone = stream)
        git clone --depth 1 "https://github.com/$repo.git" "$repo_path" 2>&1 | tee -a "$LOG_FILE"
        echo "[✓] Cloned: $repo_name"
    fi
}

# Sync all repos
echo "[*] Syncing ${#REPOS[@]} repos..."
echo ""

for repo in "${REPOS[@]}"; do
    sync_repo "$repo"
    echo ""
done

echo "[*] GIT SYNC COMPLETE"
echo "[*] Log: $LOG_FILE"
