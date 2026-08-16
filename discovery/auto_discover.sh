#!/data/data/com.termux/files/usr/bin/bash
set -e

C25_HOME=~/constellation25
DB_PATH=$C25_HOME/c25_unified_registry.db
SCAN_LOG=$C25_HOME/discovery/logs/scan_$(date +%Y%m%d_%H%M%S).log

echo "Starting auto-discovery at $(date)" | tee -a $SCAN_LOG

ORGS=("Constillation25" "FacePrintPay" "AiMetaverse" "TheKre8tive" "Kre8tive-Konceptz" "Kre8tive-Space")

scan_repo() {
    local org=$1
    local repo=$2
    local repo_path="$HOME/$org/$repo"
    
    [ ! -d "$repo_path" ] && return
    
    echo "  Scanning $org/$repo..." | tee -a $SCAN_LOG
    
    # Detect APIs
    if grep -rq "from flask import\|from fastapi import\|@app.route" "$repo_path" 2>/dev/null; then
        sqlite3 $DB_PATH "INSERT OR IGNORE INTO repo_capabilities (org, repo_name, capability_type, capability_name) VALUES ('$org', '$repo', 'API', 'flask-fastapi-app');"
    fi
    
    # Detect Agents
    if grep -rq "class.*Agent\|agent_name" "$repo_path" 2>/dev/null; then
        sqlite3 $DB_PATH "INSERT OR IGNORE INTO repo_capabilities (org, repo_name, capability_type, capability_name) VALUES ('$org', '$repo', 'AGENT', 'autonomous-agent');"
    fi
    
    # Detect Services
    if [ -f "$repo_path/Dockerfile" ] || [ -f "$repo_path/docker-compose.yml" ]; then
        sqlite3 $DB_PATH "INSERT OR IGNORE INTO repo_capabilities (org, repo_name, capability_type, capability_name) VALUES ('$org', '$repo', 'SERVICE', 'docker-service');"
    fi
    
    # Detect CLI Tools
    if find "$repo_path" -name "*.sh" -type f 2>/dev/null | head -1 | grep -q .; then
        sqlite3 $DB_PATH "INSERT OR IGNORE INTO repo_capabilities (org, repo_name, capability_type, capability_name) VALUES ('$org', '$repo', 'CLI', 'bash-tool');"
    fi
}

for org in "${ORGS[@]}"; do
    [ -d "$HOME/$org" ] || continue
    for repo in "$HOME/$org"/*; do
        [ -d "$repo" ] && scan_repo "$org" "$(basename "$repo")"
    done
done

echo "✅ Discovery complete. Total: $(sqlite3 $DB_PATH 'SELECT COUNT(*) FROM repo_capabilities;')" | tee -a $SCAN_LOG
