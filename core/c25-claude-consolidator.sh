#!/data/data/com.termux/files/usr/bin/bash
# ═══════════════════════════════════════════════════
# C25 CLAUDE CODE CONSOLIDATION ORCHESTRATOR (ULTRA-FAST)
# Uses ls/du instead of find for instant results
# ═══════════════════════════════════════════════════

set -e
C='\033[0;36m'; G='\033[0;32m'; Y='\033[1;33m'; R='\033[0;31m'; N='\033[0m'
HOME_DIR="/data/data/com.termux/files/home"
SD_CARD="/storage/emulated/0"
AUDIT_FILE="$HOME_DIR/c25_store/audit_context_$(date +%Y%m%d_%H%M%S).txt"
CLAUDE_OUTPUT="$HOME_DIR/c25_store/claude_consolidation_plan.md"

echo -e "${C}═══ C25 CLAUDE CODE CONSOLIDATION INITIATED ═══${N}"
echo -e "${Y}Timestamp: $(date '+%Y-%m-%d %H:%M:%S')${N}"

# ── 1. CAPTURE CURRENT STATE (ULTRA-FAST) ──
echo -e "\n${Y}── [1/4] Capturing Current Ecosystem State (Ultra-Fast) ──${N}"
mkdir -p "$HOME_DIR/c25_store"

{
    echo "# C25 ECOSYSTEM AUDIT CONTEXT"
    echo "# Generated: $(date '+%Y-%m-%d %H:%M:%S')"
    echo ""
    echo "## ACTIVE PROJECTS (Termux Home)"
    for dir in "$HOME_DIR/constellation25" "$HOME_DIR/VideoCourts-Project" \
               "$HOME_DIR/AiKre8tive-Stargate" "$HOME_DIR/PaThosAi" \
               "$HOME_DIR/FacePrintPay" "$HOME_DIR/Lunar27" "$HOME_DIR/VeRseD_Ai"; do
        if [ -d "$dir" ]; then
            echo ""
            echo "[$dir]"
            du -sh "$dir" 2>/dev/null || echo "Size: unknown"
            echo "Top-level contents:"
            ls -la "$dir" 2>/dev/null | head -n 15
        fi
    done

    echo ""
    echo "## MONOREPO STRUCTURE (SD Card)"
    if [ -d "$SD_CARD/c25/repos/constellation25-mono" ]; then
        echo ""
        echo "[$SD_CARD/c25/repos/constellation25-mono]"
        du -sh "$SD_CARD/c25/repos/constellation25-mono" 2>/dev/null || echo "Size: unknown"
        echo "Top-level directories:"
        ls -d "$SD_CARD/c25/repos/constellation25-mono"/*/ 2>/dev/null | head -n 20
        echo ""
        echo "Sample files (first 50):"
        ls "$SD_CARD/c25/repos/constellation25-mono"/*/*.html 2>/dev/null | head -n 50
    fi

    echo ""
    echo "## SCATTERED BUILDS (SD Card - Needs Consolidation)"
    for dir in "$SD_CARD/github" "$SD_CARD/c25_sovereign_product" "$SD_CARD/c25"; do
        if [ -d "$dir" ]; then
            echo ""
            echo "[$dir]"
            du -sh "$dir" 2>/dev/null || echo "Size: unknown"
            echo "Top-level contents:"
            ls -la "$dir" 2>/dev/null | head -n 20
        fi
    done

    echo ""
    echo "## ARCHIVE STATUS (Large Directories - Do Not Scan Contents)"
    echo "NOTE: These are massive archives. Only report size and existence."
    for backup_dir in "$SD_CARD"/termux_backup_*; do
        if [ -d "$backup_dir" ]; then
            echo ""
            echo "[$backup_dir]"
            du -sh "$backup_dir" 2>/dev/null || echo "Size: unknown"
            echo "Top-level directories:"
            ls -d "$backup_dir"/*/ 2>/dev/null | head -n 10
        fi
    done

    if [ -d "$SD_CARD/bard-totalrecall" ]; then
        echo ""
        echo "[$SD_CARD/bard-totalrecall]"
        du -sh "$SD_CARD/bard-totalrecall" 2>/dev/null || echo "Size: unknown"
        echo "Top-level contents:"
        ls -la "$SD_CARD/bard-totalrecall" 2>/dev/null | head -n 10
    fi

} > "$AUDIT_FILE"

TOTAL_LINES=$(wc -l < "$AUDIT_FILE")
echo -e "${G}✅ Audit context captured: $TOTAL_LINES lines → $AUDIT_FILE${N}"
echo -e "${Y}   (Ultra-fast: ls/du only, no recursive find)${N}"

# ── 2. CONSTRUCT CLAUDE CODE PROMPT ──
echo -e "\n${Y}── [2/4] Constructing Claude Code Consolidation Prompt ──${N}"

CLAUDE_PROMPT="You are the C25 Consolidation Agent for the Sovereign AI ecosystem.

CONTEXT:
I have a massive, fragmented ecosystem of files across Termux and SD card storage. The audit is in: $AUDIT_FILE

YOUR MISSION:
1. ANALYZE all files and directories in the audit
2. IDENTIFY the core active projects (VideoCourts, AiKre8tive-Stargate, PaThosAi, FacePrintPay, constellation25-mono, Lunar27, VeRseD_Ai)
3. IDENTIFY scattered backups, duplicates, and redundant builds (termux_backup_*, github/*, c25_sovereign_product/*)
4. CREATE a unified platform structure that:
   - Routes all frontend assets through a single entry point
   - Parses and deduplicates identical files
   - Prunes obsolete backups (move to cold storage, don't delete)
   - Organizes everything into a clean monorepo structure
5. GENERATE a detailed consolidation plan with:
   - Directory structure recommendations
   - File routing rules (where each asset should live)
   - Pruning strategy (what to archive vs keep active)
   - Symlink strategy (how to maintain backward compatibility)
6. SUGGEST next steps for automation (CI/CD, deployment scripts, agent integration)

CONSTRAINTS:
- DO NOT delete any files. Only move/archive duplicates.
- Maintain backward compatibility via symlinks where needed.
- Follow the C25 Zero-Scatter doctrine: all builds must be centralized.
- Prioritize the active projects listed above.
- Handle bard-totalrecall logs as historical archives (consolidate, don't delete).

OUTPUT FORMAT:
Provide a markdown report with:
- Executive summary
- Proposed directory structure
- File routing table (source → destination)
- Pruning recommendations
- Automation suggestions

Read the audit file and begin your analysis."

echo -e "${G}✅ Prompt constructed ($(echo "$CLAUDE_PROMPT" | wc -c) bytes)${N}"

# ── 3. INVOKE CLAUDE CODE ──
echo -e "\n${Y}── [3/4] Invoking Claude Code for Consolidation Analysis ──${N}"
echo -e "${C}This may take several minutes. Claude Code will analyze the entire ecosystem...${N}"

# Check if claude CLI is available
if ! command -v claude &> /dev/null; then
    echo -e "${R}❌ ERROR: Claude Code CLI not found in PATH${N}"
    echo -e "${Y}Install with: npm install -g @anthropic-ai/claude-code${N}"
    exit 1
fi

# Invoke Claude Code with the prompt, capturing output
echo "$CLAUDE_PROMPT" | timeout 300 claude --output-format text > "$CLAUDE_OUTPUT" 2>&1 || {
    echo -e "${R}⚠️  Claude Code encountered an error or timed out. Check: $CLAUDE_OUTPUT${N}"
    echo -e "${Y}Attempting interactive mode...${N}"
    echo "$CLAUDE_PROMPT" | timeout 300 claude > "$CLAUDE_OUTPUT" 2>&1
}

echo -e "${G}✅ Claude Code analysis complete → $CLAUDE_OUTPUT${N}"

# ── 4. DISPLAY CLAUDE CODE SUGGESTIONS ──
echo -e "\n${Y}── [4/4] Claude Code Consolidation Plan ──${N}"
echo -e "${C}═══════════════════════════════════════════════${N}"
cat "$CLAUDE_OUTPUT"
echo -e "${C}═══════════════════════════════════════════════${N}"

echo -e "\n${G}✅ CONSOLIDATION ORCHESTRATION COMPLETE${N}"
echo -e "${Y}📄 Full plan saved: $CLAUDE_OUTPUT${N}"
echo -e "${Y}📄 Audit context: $AUDIT_FILE${N}"
echo -e "\n${C}NEXT STEPS:${N}"
echo -e "  1. Review Claude Code's suggestions above"
echo -e "  2. Run: nano $CLAUDE_OUTPUT (to edit/refine the plan)"
echo -e "  3. Execute consolidation: bash ~/constellation25/core/c25-execute-consolidation.sh"

