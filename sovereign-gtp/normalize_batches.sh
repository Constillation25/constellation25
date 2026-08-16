#!/data/data/com.termux/files/usr/bin/bash
set -e
C25_ROOT="${C25_ROOT:-${HOME}/constellation25}"
BATCHES_DIR="${C25_ROOT}/sovereign-gtp/batches"
echo "📋 Normalizing batch files to 100 tasks each..."
for batch_file in "${BATCHES_DIR}"/*.txt; do
    [ -f "$batch_file" ] || continue
    filename=$(basename "$batch_file")
    current_count=$(wc -l < "$batch_file")
    if [ "$current_count" -lt 100 ]; then
        needed=$((100 - current_count))
        echo "  📝 ${filename}: ${current_count} → 100 tasks (+${needed})"
        for i in $(seq 1 $needed); do
            echo "Auto-generated task ${current_count + i} for ${filename%.txt}" >> "$batch_file"
        done
    elif [ "$current_count" -gt 100 ]; then
        echo "  ⚠️  ${filename}: ${current_count} tasks (truncating to 100)"
        head -100 "$batch_file" > "${batch_file}.tmp" && mv "${batch_file}.tmp" "$batch_file"
    else
        echo "  ✓ ${filename}: already 100 tasks"
    fi
done
echo "✅ Normalization complete"
echo "   Total batches: $(ls ${BATCHES_DIR}/*.txt | wc -l)"
echo "   Total tasks: $(cat ${BATCHES_DIR}/*.txt | wc -l)"
