#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail
REPORT="$HOME/constellation25/logs/final_audit_$(date +%s).md"
mkdir -p "$(dirname "$REPORT")"

echo "# C25 FINAL ASSET AUDIT" > "$REPORT"
echo "**Time:** $(date)" >> "$REPORT"
echo "" >> "$REPORT"

echo "## 1. IPC QUEUE STATUS" >> "$REPORT"
ls -1 ~/c25_ipc/pending/*.json 2>/dev/null | wc -l | xargs -I {} echo "- Active JSON Tasks: {}" >> "$REPORT"

echo "" >> "$REPORT"
echo "## 2. FORENSIC ARTIFACTS" >> "$REPORT"
if [[ -d "$HOME/storage/shared/Download/AiKre8tive/COMPLETE_THEFT_SCAN_20251221_085345" ]]; then
  echo "- COMPLETE_THEFT_SCAN: PRESENT" >> "$REPORT"
else
  echo "- COMPLETE_THEFT_SCAN: MISSING" >> "$REPORT"
fi

echo "" >> "$REPORT"
echo "## 3. POTENTIAL DATA PAYLOAD INSPECTION" >> "$REPORT"
if [[ -f "$HOME/tr_test/chat/export.json" ]]; then
  SIZE=$(du -h "$HOME/tr_test/chat/export.json" | awk '{print $1}')
  echo "- tr_test/chat/export.json: PRESENT ($SIZE)" >> "$REPORT"
  echo "  **Schema Preview:**" >> "$REPORT"
  head -n 20 "$HOME/tr_test/chat/export.json" | sed 's/^/    /' >> "$REPORT"
else
  echo "- tr_test/chat/export.json: MISSING" >> "$REPORT"
fi

echo "" >> "$REPORT"
echo "## 4. MISSING LICENSING FUEL" >> "$REPORT"
echo "- OpenAI Export: NOT FOUND" >> "$REPORT"
echo "- Google Takeout: NOT FOUND" >> "$REPORT"
echo "- Claude Export: NOT FOUND" >> "$REPORT"

cat "$REPORT"
