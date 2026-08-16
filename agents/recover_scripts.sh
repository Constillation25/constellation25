#!/data/data/com.termux/files/usr/bin/bash
# CONSTELLATION25 - Automated Script Recovery (Hardened)

BASE="$HOME/constellation25"
HISTORY="$HOME/.bash_history"
REPORT="$BASE/logs/recovery_report.log"
TODO="$BASE/logs/agent_todo.log"
RECOVERED_DIR="$BASE/recovered_scripts"

mkdir -p "$RECOVERED_DIR"
> "$REPORT"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$REPORT"
}

echo "🛠️  CONSTELLATION25 Automated Script Recovery"
echo "=============================================="

recovered=0
failed=0

# Only look for clear script invocations
grep -E '(^|[[:space:]])([./]*[a-zA-Z0-9_/-]+\.(sh|py))($|[[:space:]])' "$HISTORY" 2>/dev/null | \
tail -n 300 | sort | uniq | while read -r line; do

    # Extract the most likely script path
    script=$(echo "$line" | grep -oE '[./a-zA-Z0-9_/-]+\.(sh|py)' | head -1)
    [ -z "$script" ] && continue

    # Skip wildcards and junk
    [[ "$script" == *"*"* ]] && continue
    [[ "$script" == *"--"* ]] && continue
    [[ "$script" == *"|"* ]] && continue

    # Resolve path
    full=""
    for try in "$script" "$HOME/$script" "$BASE/$script" "$BASE/agents/$script"; do
        if [ -f "$try" ]; then
            full="$try"
            break
        fi
    done

    # Case 1: Missing file
    if [ -z "$full" ]; then
        name=$(basename "$script" 2>/dev/null)
        [ -z "$name" ] && continue

        log "❌ Missing: $script"
        
        # Create a useful stub
        cat > "$RECOVERED_DIR/$name" << STUB
#!/data/data/com.termux/files/usr/bin/bash
# Recovered stub for $name
# Original reference: $line
echo "This is a recovered stub for $name"
echo "Please restore the real file or update the reference."
STUB
        chmod +x "$RECOVERED_DIR/$name"
        log "   ✅ Stub created → recovered_scripts/$name"
        recovered=$((recovered+1))
        continue
    fi

    # Case 2: Not executable
    if [ ! -x "$full" ]; then
        chmod +x "$full"
        log "⚠️  Fixed permissions: $full"
        recovered=$((recovered+1))
        continue
    fi

    # Case 3: Basic syntax check for shell scripts
    if [[ "$full" == *.sh ]]; then
        if ! bash -n "$full" 2>/dev/null; then
            # Fix common Windows line endings
            sed -i 's/\r$//' "$full"
            if bash -n "$full" 2>/dev/null; then
                log "✅ Fixed line endings: $full"
                recovered=$((recovered+1))
            else
                log "❌ Syntax error remains: $full"
                failed=$((failed+1))
            fi
        fi
    fi
done

echo ""
echo "=============================================="
echo "Recovery Summary"
echo "  Recovered / Fixed : $recovered"
echo "  Still failing     : $failed"
echo "  Report            : $REPORT"
echo "  Recovered stubs   : $RECOVERED_DIR/"
echo "=============================================="

echo "[$(date)] Recovery run – $recovered fixed, $failed still broken" >> "$TODO"
