#!/data/data/com.termux/files/usr/bin/bash
# ═══════════════════════════════════════════════════
# C25 CONSOLIDATION EXECUTION SCRIPT
# Performs moves, symlinks, and archives based on Claude Code plan
# ZERO DELETION - Archive only
# ═══════════════════════════════════════════════════

set -e
C='\033[0;36m'; G='\033[0;32m'; Y='\033[1;33m'; R='\033[0;31m'; N='\033[0m'
HOME_DIR="/data/data/com.termux/files/home"
SD_CARD="/storage/emulated/0"
MONOREPO="$SD_CARD/c25/repos/constellation25-mono"
COLD_STORAGE="$HOME_DIR/c25_store/cold_archive_$(date +%Y%m%d_%H%M%S)"
LOG_FILE="$HOME_DIR/c25_store/consolidation_log_$(date +%Y%m%d_%H%M%S).txt"

echo -e "${C}═══ C25 CONSOLIDATION EXECUTION INITIATED ═══${N}"
echo -e "${Y}Timestamp: $(date '+%Y-%m-%d %H:%M:%S')${N}"
echo -e "${Y}Log file: $LOG_FILE${N}"

# Initialize log
{
    echo "# C25 CONSOLIDATION EXECUTION LOG"
    echo "# Started: $(date '+%Y-%m-%d %H:%M:%S')"
    echo ""
} > "$LOG_FILE"

# ── 1. CREATE COLD STORAGE FOR ARCHIVES ──
echo -e "\n${Y}── [1/6] Creating Cold Storage ──${N}"
mkdir -p "$COLD_STORAGE"
echo "[$(date)] Created cold storage: $COLD_STORAGE" >> "$LOG_FILE"
echo -e "${G}✅ Cold storage ready: $COLD_STORAGE${N}"

# ── 2. CONSOLIDATE SCATTERED GITHUB BUILDS ──
echo -e "\n${Y}── [2/6] Consolidating Scattered GitHub Builds ──${N}"

# Map of scattered builds → monorepo destinations
declare -A BUILD_MAP=(
    ["$SD_CARD/github/VideoCourts-Project"]="$MONOREPO/packages/VideoCourts"
    ["$SD_CARD/github/AiKre8tive-Stargate"]="$MONOREPO/packages/AiKre8tive-Stargate"
    ["$SD_CARD/github/PaThosAi"]="$MONOREPO/packages/PaThosAi"
    ["$SD_CARD/github/FacePrintPay"]="$MONOREPO/packages/FacePrintPay"
    ["$SD_CARD/github/VeRseD_Ai"]="$MONOREPO/packages/VeRseD_Ai"
    ["$SD_CARD/github/mars-agent"]="$MONOREPO/packages/agents/mars-agent"
    ["$SD_CARD/github/luna-agent"]="$MONOREPO/packages/agents/luna-agent"
    ["$SD_CARD/github/io-agent"]="$MONOREPO/packages/agents/io-agent"
    ["$SD_CARD/github/europa-agent"]="$MONOREPO/packages/agents/europa-agent"
    ["$SD_CARD/github/pluto-agent"]="$MONOREPO/packages/agents/pluto-agent"
    ["$SD_CARD/github/recon-agent"]="$MONOREPO/packages/agents/recon-agent"
    ["$SD_CARD/github/makemake-agent"]="$MONOREPO/packages/agents/makemake-agent"
    ["$SD_CARD/github/ganymede-agent"]="$MONOREPO/packages/agents/ganymede-agent"
    ["$SD_CARD/github/haumea-agent"]="$MONOREPO/packages/agents/haumea-agent"
)

for source in "${!BUILD_MAP[@]}"; do
    dest="${BUILD_MAP[$source]}"
    if [ -d "$source" ]; then
        echo -e "${Y}⟳ Moving: $(basename "$source") → $(basename "$dest")${N}"
        mkdir -p "$(dirname "$dest")"
        mv "$source" "$dest" 2>/dev/null && {
            echo "[$(date)] MOVED: $source → $dest" >> "$LOG_FILE"
            # Create symlink for backward compatibility
            ln -s "$dest" "$source" 2>/dev/null && {
                echo "[$(date)] SYMLINK: $source → $dest" >> "$LOG_FILE"
                echo -e "${G}  ✅ Moved + symlinked${N}"
            } || {
                echo -e "${Y}  ⚠️  Moved (symlink failed - permission issue)${N}"
            }
        } || {
            echo -e "${R}  ❌ Move failed (directory in use or permission denied)${N}"
            echo "[$(date)] FAILED: $source → $dest" >> "$LOG_FILE"
        }
    fi
done

# ── 3. CONSOLIDATE TERMUX BACKUPS ──
echo -e "\n${Y}── [3/6] Archiving Termux Backups ──${N}"

for backup_dir in "$SD_CARD"/termux_backup_*; do
    if [ -d "$backup_dir" ]; then
        backup_name=$(basename "$backup_dir")
        echo -e "${Y}⟳ Archiving: $backup_name${N}"
        mv "$backup_dir" "$COLD_STORAGE/$backup_name" 2>/dev/null && {
            echo "[$(date)] ARCHIVED: $backup_dir → $COLD_STORAGE/$backup_name" >> "$LOG_FILE"
            echo -e "${G}  ✅ Archived to cold storage${N}"
        } || {
            echo -e "${R}  ❌ Archive failed${N}"
            echo "[$(date)] FAILED ARCHIVE: $backup_dir" >> "$LOG_FILE"
        }
    fi
done

# ── 4. CONSOLIDATE BARD-TOTALRECALL LOGS ──
echo -e "\n${Y}── [4/6] Archiving Bard TotalRecall Logs ──${N}"

if [ -d "$SD_CARD/bard-totalrecall" ]; then
    echo -e "${Y}⟳ Archiving: bard-totalrecall (historical AI logs)${N}"
    mv "$SD_CARD/bard-totalrecall" "$COLD_STORAGE/bard-totalrecall" 2>/dev/null && {
        echo "[$(date)] ARCHIVED: $SD_CARD/bard-totalrecall → $COLD_STORAGE/bard-totalrecall" >> "$LOG_FILE"
        echo -e "${G}  ✅ Archived to cold storage${N}"
    } || {
        echo -e "${R}  ❌ Archive failed${N}"
        echo "[$(date)] FAILED ARCHIVE: $SD_CARD/bard-totalrecall" >> "$LOG_FILE"
    }
fi

# ── 5. CONSOLIDATE C25_SOVEREIGN_PRODUCT ──
echo -e "\n${Y}── [5/6] Consolidating c25_sovereign_product ──${N}"

if [ -d "$SD_CARD/c25_sovereign_product" ]; then
    echo -e "${Y}⟳ Moving: c25_sovereign_product → monorepo/packages/sovereign-product${N}"
    mkdir -p "$MONOREPO/packages"
    mv "$SD_CARD/c25_sovereign_product" "$MONOREPO/packages/sovereign-product" 2>/dev/null && {
        echo "[$(date)] MOVED: $SD_CARD/c25_sovereign_product → $MONOREPO/packages/sovereign-product" >> "$LOG_FILE"
        ln -s "$MONOREPO/packages/sovereign-product" "$SD_CARD/c25_sovereign_product" 2>/dev/null && {
            echo "[$(date)] SYMLINK: $SD_CARD/c25_sovereign_product → $MONOREPO/packages/sovereign-product" >> "$LOG_FILE"
            echo -e "${G}  ✅ Moved + symlinked${N}"
        } || {
            echo -e "${Y}  ⚠️  Moved (symlink failed)${N}"
        }
    } || {
        echo -e "${R}  ❌ Move failed${N}"
        echo "[$(date)] FAILED: $SD_CARD/c25_sovereign_product" >> "$LOG_FILE"
    }
fi

# ── 6. VERIFY MONOREPO STRUCTURE ──
echo -e "\n${Y}── [6/6] Verifying Monorepo Structure ──${N}"

echo -e "${C}Monorepo packages:${N}"
ls -d "$MONOREPO/packages"/*/ 2>/dev/null | while read -r pkg; do
    pkg_name=$(basename "$pkg")
    pkg_size=$(du -sh "$pkg" 2>/dev/null | cut -f1)
    echo -e "  ${G}✓${N} $pkg_name ($pkg_size)"
done

echo -e "\n${C}Cold storage archives:${N}"
ls -d "$COLD_STORAGE"/*/ 2>/dev/null | while read -r archive; do
    archive_name=$(basename "$archive")
    archive_size=$(du -sh "$archive" 2>/dev/null | cut -f1)
    echo -e "  ${Y}⟳${N} $archive_name ($archive_size)"
done

# ── FINAL SUMMARY ──
echo -e "\n${C}═══════════════════════════════════════════════${N}"
echo -e "${G}✅ CONSOLIDATION EXECUTION COMPLETE${N}"
echo -e "${C}═══════════════════════════════════════════════${N}"
echo -e "${Y}📄 Full log: $LOG_FILE${N}"
echo -e "${Y}📦 Cold storage: $COLD_STORAGE${N}"
echo -e "${Y}🏗️  Monorepo: $MONOREPO${N}"

echo "[$(date)] CONSOLIDATION COMPLETE" >> "$LOG_FILE"

echo -e "\n${C}NEXT STEPS:${N}"
echo -e "  1. Review log: nano $LOG_FILE"
echo -e "  2. Verify monorepo: ls $MONOREPO/packages"
echo -e "  3. Test symlinks: ls -la $SD_CARD/github"
echo -e "  4. Deploy unified platform: bash $MONOREPO/deploy/unified-platform.sh"

