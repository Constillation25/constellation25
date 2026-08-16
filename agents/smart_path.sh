#!/data/data/com.termux/files/usr/bin/bash
# CONSTELLATION25 - Smart Path Resolver & Auto-Creator
# Usage: source this file or call: resolve_path "some/missing/file.sh"

BASE="$HOME/constellation25"
SEARCH_ROOTS=(
    "$HOME"
    "$HOME/constellation25"
    "$HOME/storage"
    "$HOME/downloads"
    "$HOME/github"
    "$HOME/FacePrintPay"
    "$HOME/faceprintpay"
    "$HOME/backups"
    "$HOME/.termux"
)

log() {
    echo "[$(date '+%H:%M:%S')] $1"
}

# Find the most likely matching file
find_likely() {
    local target="$1"
    local name=$(basename "$target")
    
    # Exact name search
    for root in "${SEARCH_ROOTS[@]}"; do
        [ -d "$root" ] || continue
        found=$(find "$root" -type f -name "$name" 2>/dev/null | head -3)
        if [ -n "$found" ]; then
            echo "$found"
            return 0
        fi
    done
    
    # Fuzzy search (partial name)
    for root in "${SEARCH_ROOTS[@]}"; do
        [ -d "$root" ] || continue
        found=$(find "$root" -type f -iname "*${name%.*}*" 2>/dev/null | head -3)
        if [ -n "$found" ]; then
            echo "$found"
            return 0
        fi
    done
    
    return 1
}

# Main resolver
resolve_path() {
    local path="$1"
    
    # Already exists
    if [ -e "$path" ]; then
        echo "$path"
        return 0
    fi
    
    log "Path not found: $path"
    
    # Try to find a likely match
    likely=$(find_likely "$path")
    if [ -n "$likely" ]; then
        log "→ Found likely match: $likely"
        echo "$likely"
        return 0
    fi
    
    # Auto-create
    if [[ "$path" == */ ]]; then
        # It's a directory
        mkdir -p "$path"
        log "→ Created directory: $path"
        echo "$path"
    else
        # It's a file – create parent dirs + empty file
        mkdir -p "$(dirname "$path")"
        touch "$path"
        log "→ Created empty file: $path"
        echo "$path"
    fi
}

# Batch resolver for history / scripts
auto_heal_paths() {
    log "Starting auto-heal scan..."
    
    # Common missing paths from your history
    missing_list=(
        "c25_master_control.sh"
        "scripts/start-agents.sh"
        "scripts/ollama-agent.sh"
        "scripts/qwen-agent.sh"
        "aggressive-cleanup.sh"
        "catalog-agents.sh"
        "sovereign-grok.sh"
    )
    
    for item in "${missing_list[@]}"; do
        resolve_path "$BASE/$item" > /dev/null
    done
    
    log "Auto-heal complete"
}

# If called directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    if [ -n "$1" ]; then
        resolve_path "$1"
    else
        auto_heal_paths
    fi
fi
