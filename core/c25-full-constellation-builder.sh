#!/data/data/com.termux/files/usr/bin/bash
# ═══════════════════════════════════════════════════
# C25 FULL CONSTELLATION BUILDER (OPTIMIZED)
# Batch processing - 33K+ files in under 5 minutes
# ═══════════════════════════════════════════════════

set -e
C='\033[0;36m'; G='\033[0;32m'; Y='\033[1;33m'; R='\033[0;31m'; N='\033[0m'
HOME_DIR="/data/data/com.termux/files/home"
SD_CARD="/storage/emulated/0"
OUTPUT="$HOME_DIR/c25_store/full_constellation"
DASHBOARD="$OUTPUT/index.html"
MANIFEST="$OUTPUT/manifest.json"
TEMP_DIR=$(mktemp -d)

echo -e "${C}═══ C25 FULL CONSTELLATION BUILDER (OPTIMIZED) ═══${N}"
echo -e "${Y}Processing ALL files with batch categorization...${N}"

mkdir -p "$OUTPUT"

# ── 1. FIND ALL FILES ──
echo -e "\n${Y}── [1/3] Scanning ALL Storage ──${N}"

TEMP_SCAN="$TEMP_DIR/all_files.txt"

{
    timeout 30 find "$HOME_DIR" -maxdepth 5 -type f \( \
        -name "*.html" -o -name "*.sh" -o -name "*.py" -o -name "*.json" \
        -o -name "*.mht" -o -name "*.md" -o -name "*.txt" -o -name "*.js" \
        -o -name "*.css" -o -name "*.yaml" -o -name "*.yml" \
    \) ! -path "*/node_modules/*" ! -path "*/.git/*" ! -path "*/dist/*" \
       ! -path "*/.cache/*" ! -path "*/c25_store/*" 2>/dev/null || true
    
    timeout 30 find "$SD_CARD" -maxdepth 5 -type f \( \
        -name "*.html" -o -name "*.sh" -o -name "*.py" -o -name "*.json" \
        -o -name "*.mht" -o -name "*.md" -o -name "*.txt" -o -name "*.js" \
        -o -name "*.css" -o -name "*.yaml" -o -name "*.yml" \
    \) ! -path "*/node_modules/*" ! -path "*/.git/*" ! -path "*/dist/*" \
       ! -path "*/.cache/*" ! -path "*/Android/data/*" 2>/dev/null || true
    
} | sort -u > "$TEMP_SCAN"

TOTAL_FILES=$(wc -l < "$TEMP_SCAN")
echo -e "${G}✅ Found $TOTAL_FILES files${N}"

# ── 2. BATCH CATEGORIZE (INSTANT) ──
echo -e "\n${Y}── [2/3] Batch Categorizing (Fast Mode) ──${N}"

# Split files into category temp files using grep (instant)
echo "Categorizing with grep..."
grep -E '\.html$' "$TEMP_SCAN" > "$TEMP_DIR/html.txt" 2>/dev/null || true
grep -E '\.py$' "$TEMP_SCAN" > "$TEMP_DIR/python.txt" 2>/dev/null || true
grep -E '\.sh$' "$TEMP_SCAN" > "$TEMP_DIR/bash.txt" 2>/dev/null || true
grep -E '\.json$' "$TEMP_SCAN" > "$TEMP_DIR/json.txt" 2>/dev/null || true
grep -E '\.mht$' "$TEMP_SCAN" > "$TEMP_DIR/mht.txt" 2>/dev/null || true
grep -E '\.md$' "$TEMP_SCAN" > "$TEMP_DIR/markdown.txt" 2>/dev/null || true
grep -E '\.js$' "$TEMP_SCAN" > "$TEMP_DIR/javascript.txt" 2>/dev/null || true
grep -E '\.css$' "$TEMP_SCAN" > "$TEMP_DIR/css.txt" 2>/dev/null || true
grep -E '\.(yaml|yml)$' "$TEMP_SCAN" > "$TEMP_DIR/yaml.txt" 2>/dev/null || true
grep -E '\.txt$' "$TEMP_SCAN" > "$TEMP_DIR/text.txt" 2>/dev/null || true

# Count each category
HTML_COUNT=$(wc -l < "$TEMP_DIR/html.txt" 2>/dev/null || echo 0)
PYTHON_COUNT=$(wc -l < "$TEMP_DIR/python.txt" 2>/dev/null || echo 0)
BASH_COUNT=$(wc -l < "$TEMP_DIR/bash.txt" 2>/dev/null || echo 0)
JSON_COUNT=$(wc -l < "$TEMP_DIR/json.txt" 2>/dev/null || echo 0)
MHT_COUNT=$(wc -l < "$TEMP_DIR/mht.txt" 2>/dev/null || echo 0)
MD_COUNT=$(wc -l < "$TEMP_DIR/markdown.txt" 2>/dev/null || echo 0)
JS_COUNT=$(wc -l < "$TEMP_DIR/javascript.txt" 2>/dev/null || echo 0)
CSS_COUNT=$(wc -l < "$TEMP_DIR/css.txt" 2>/dev/null || echo 0)
YAML_COUNT=$(wc -l < "$TEMP_DIR/yaml.txt" 2>/dev/null || echo 0)
TXT_COUNT=$(wc -l < "$TEMP_DIR/text.txt" 2>/dev/null || echo 0)

echo -e "${G}✅ Categorized in seconds${N}"
echo -e "  🌐 HTML: $HTML_COUNT"
echo -e "  🐍 Python: $PYTHON_COUNT"
echo -e "  ⚡ Bash: $BASH_COUNT"
echo -e "  📋 JSON: $JSON_COUNT"
echo -e "  📧 MHT: $MHT_COUNT"
echo -e "  📝 Markdown: $MD_COUNT"
echo -e "  🟨 JavaScript: $JS_COUNT"
echo -e "  🎨 CSS: $CSS_COUNT"
echo -e "  ⚙️ YAML: $YAML_COUNT"
echo -e "  📄 Text: $TXT_COUNT"

# ── 3. BUILD JSON MANIFEST (ONE PYTHON CALL) ──
echo -e "\n${Y}── [3/3] Building JSON Manifest (Single Python Call) ──${N}"

python3 << PYEOF
import json
import os
from datetime import datetime

manifest = {
    "generated": datetime.now().isoformat(),
    "total_files": $TOTAL_FILES,
    "categories": {}
}

categories = {
    "html": "$TEMP_DIR/html.txt",
    "python": "$TEMP_DIR/python.txt",
    "bash": "$TEMP_DIR/bash.txt",
    "json": "$TEMP_DIR/json.txt",
    "mht": "$TEMP_DIR/mht.txt",
    "markdown": "$TEMP_DIR/markdown.txt",
    "javascript": "$TEMP_DIR/javascript.txt",
    "css": "$TEMP_DIR/css.txt",
    "yaml": "$TEMP_DIR/yaml.txt",
    "text": "$TEMP_DIR/text.txt"
}

for cat, filepath in categories.items():
    files = []
    if os.path.exists(filepath):
        with open(filepath, 'r') as f:
            for line in f:
                path = line.strip()
                if path:
                    files.append({
                        "name": os.path.basename(path),
                        "path": path,
                        "ext": cat
                    })
    manifest["categories"][cat] = files

with open("$MANIFEST", 'w') as f:
    json.dump(manifest, f, indent=2)

print(f"✅ Manifest built: {sum(len(v) for v in manifest['categories'].values())} files")
PYEOF

# ── 4. BUILD DASHBOARD ──
echo -e "\n${Y}── Building Dashboard ──${N}"

# Read manifest and inject into HTML
MANIFEST_JSON=$(cat "$MANIFEST")

cat > "$DASHBOARD" << DASHEOF
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>C25 Full Constellation - $TOTAL_FILES Files</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #0a0e27 0%, #1a1f3a 100%);
            color: #e0e6ed;
            min-height: 100vh;
            padding: 1rem;
        }
        .container { max-width: 1800px; margin: 0 auto; }
        header {
            text-align: center;
            margin-bottom: 2rem;
            padding: 2rem;
            background: rgba(255,255,255,0.05);
            border-radius: 16px;
        }
        h1 {
            font-size: 2.5rem;
            background: linear-gradient(90deg, #00d4ff, #7b2ff7);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0.5rem;
        }
        .subtitle { color: #8b95a5; font-size: 1.1rem; }
        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
            gap: 0.8rem;
            margin-bottom: 2rem;
        }
        .stat-card {
            background: rgba(255,255,255,0.05);
            padding: 1rem;
            border-radius: 12px;
            text-align: center;
            border: 1px solid rgba(255,255,255,0.1);
        }
        .stat-value {
            font-size: 1.8rem;
            font-weight: bold;
            color: #00d4ff;
        }
        .stat-label { color: #8b95a5; font-size: 0.8rem; }
        .search-bar {
            margin-bottom: 1.5rem;
            text-align: center;
        }
        .search-input {
            width: 100%;
            max-width: 600px;
            padding: 0.8rem 1.2rem;
            background: rgba(255,255,255,0.05);
            border: 1px solid rgba(255,255,255,0.2);
            border-radius: 8px;
            color: #e0e6ed;
            font-size: 1rem;
        }
        .search-input:focus {
            outline: none;
            border-color: #00d4ff;
        }
        .category-tabs {
            display: flex;
            gap: 0.5rem;
            margin-bottom: 2rem;
            flex-wrap: wrap;
            justify-content: center;
        }
        .tab {
            padding: 0.5rem 1rem;
            background: rgba(255,255,255,0.05);
            border: 1px solid rgba(255,255,255,0.2);
            border-radius: 8px;
            color: #e0e6ed;
            cursor: pointer;
            transition: all 0.2s;
            font-size: 0.85rem;
        }
        .tab:hover, .tab.active {
            background: rgba(0,212,255,0.2);
            border-color: #00d4ff;
        }
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
            gap: 1rem;
        }
        .module {
            aspect-ratio: 1;
            background: rgba(255,255,255,0.05);
            border-radius: 12px;
            border: 1px solid rgba(255,255,255,0.1);
            padding: 1rem;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }
        .module:hover {
            transform: translateY(-4px);
            border-color: #00d4ff;
            box-shadow: 0 8px 24px rgba(0,212,255,0.2);
        }
        .module::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 3px;
            background: linear-gradient(90deg, #00d4ff, #7b2ff7);
        }
        .module-icon { font-size: 2rem; margin-bottom: 0.5rem; }
        .module-title {
            font-size: 0.9rem;
            font-weight: 600;
            color: #00d4ff;
            margin-bottom: 0.5rem;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }
        .module-path {
            font-family: 'Courier New', monospace;
            font-size: 0.65rem;
            color: #8b95a5;
            word-break: break-all;
            flex: 1;
            overflow: hidden;
            display: -webkit-box;
            -webkit-line-clamp: 3;
            -webkit-box-orient: vertical;
            margin-bottom: 0.5rem;
        }
        .module-actions { display: flex; gap: 0.3rem; }
        .module-btn {
            flex: 1;
            padding: 0.4rem;
            background: rgba(0,212,255,0.1);
            border: 1px solid rgba(0,212,255,0.3);
            border-radius: 6px;
            color: #00d4ff;
            text-decoration: none;
            text-align: center;
            font-size: 0.75rem;
            transition: all 0.2s;
        }
        .module-btn:hover { background: rgba(0,212,255,0.2); }
        .type-badge {
            position: absolute;
            top: 0.5rem;
            right: 0.5rem;
            padding: 0.2rem 0.5rem;
            background: rgba(123,47,247,0.2);
            border-radius: 4px;
            font-size: 0.7rem;
            color: #7b2ff7;
            font-weight: 600;
        }
        .pagination {
            display: flex;
            justify-content: center;
            gap: 0.5rem;
            margin-top: 2rem;
            flex-wrap: wrap;
        }
        .page-btn {
            padding: 0.5rem 1rem;
            background: rgba(255,255,255,0.05);
            border: 1px solid rgba(255,255,255,0.2);
            border-radius: 6px;
            color: #e0e6ed;
            cursor: pointer;
        }
        .page-btn:hover, .page-btn.active {
            background: rgba(0,212,255,0.2);
            border-color: #00d4ff;
        }
        footer {
            text-align: center;
            margin-top: 2rem;
            padding: 1rem;
            color: #8b95a5;
            font-size: 0.85rem;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🌌 C25 Full Constellation</h1>
            <p class="subtitle">$TOTAL_FILES Files | ALL Builds | ONE Platform</p>
        </header>
        
        <div class="stats" id="stats"></div>
        
        <div class="search-bar">
            <input type="text" class="search-input" id="search" placeholder="🔍 Search files by name or path...">
        </div>
        
        <div class="category-tabs" id="tabs"></div>
        
        <div class="grid" id="grid"></div>
        
        <div class="pagination" id="pagination"></div>
        
        <footer>
            <p>Generated: $(date) | C25 Sovereign AI Ecosystem</p>
        </footer>
    </div>
    
    <script>
        const manifest = $MANIFEST_JSON;
        
        const icons = {
            html: '🌐', python: '🐍', bash: '⚡', json: '📋',
            mht: '📧', markdown: '📝', javascript: '🟨', css: '🎨',
            yaml: '⚙️', text: '📄'
        };
        
        const categoryNames = {
            html: 'HTML', python: 'Python', bash: 'Bash', json: 'JSON',
            mht: 'MHT', markdown: 'Markdown', javascript: 'JavaScript',
            css: 'CSS', yaml: 'YAML', text: 'Text'
        };
        
        let currentCategory = 'all';
        let currentPage = 1;
        const ITEMS_PER_PAGE = 100;
        let allFiles = [];
        
        // Flatten all files
        Object.entries(manifest.categories).forEach(([cat, files]) => {
            files.forEach(f => {
                f.category = cat;
                allFiles.push(f);
            });
        });
        
        // Stats
        document.getElementById('stats').innerHTML = Object.entries(manifest.categories).map(([cat, files]) => \`
            <div class="stat-card">
                <div class="stat-value">\${files.length}</div>
                <div class="stat-label">\${icons[cat] || '📦'} \${categoryNames[cat] || cat}</div>
            </div>
        \`).join('');
        
        // Tabs
        document.getElementById('tabs').innerHTML = \`
            <div class="tab active" data-category="all">ALL (\${manifest.total_files})</div>
            \${Object.entries(manifest.categories).map(([cat, files]) => \`
                <div class="tab" data-category="\${cat}">
                    \${icons[cat]} \${categoryNames[cat]} (\${files.length})
                </div>
            \`).join('')}
        \`;
        
        // Render
        function render() {
            let filtered = currentCategory === 'all' 
                ? allFiles 
                : allFiles.filter(f => f.category === currentCategory);
            
            const searchTerm = document.getElementById('search').value.toLowerCase();
            if (searchTerm) {
                filtered = filtered.filter(f => 
                    f.name.toLowerCase().includes(searchTerm) ||
                    f.path.toLowerCase().includes(searchTerm)
                );
            }
            
            const totalPages = Math.ceil(filtered.length / ITEMS_PER_PAGE);
            const start = (currentPage - 1) * ITEMS_PER_PAGE;
            const pageFiles = filtered.slice(start, start + ITEMS_PER_PAGE);
            
            document.getElementById('grid').innerHTML = pageFiles.map(file => \`
                <div class="module">
                    <div class="type-badge">.\${file.ext.toUpperCase()}</div>
                    <div class="module-icon">\${icons[file.category] || '📦'}</div>
                    <div class="module-title">\${file.name}</div>
                    <div class="module-path">\${file.path}</div>
                    <div class="module-actions">
                        <a href="file://\${file.path}" class="module-btn" target="_blank">Open</a>
                        <a href="file://\${file.path}" class="module-btn" target="_blank">View</a>
                    </div>
                </div>
            \`).join('') || '<p style="text-align:center;color:#8b95a5;grid-column:1/-1;">No files found</p>';
            
            // Pagination
            if (totalPages > 1) {
                let paginationHtml = '';
                if (currentPage > 1) paginationHtml += \`<div class="page-btn" onclick="goToPage(\${currentPage-1})">← Prev</div>\`;
                for (let i = 1; i <= Math.min(totalPages, 10); i++) {
                    paginationHtml += \`<div class="page-btn \${i === currentPage ? 'active' : ''}" onclick="goToPage(\${i})">\${i}</div>\`;
                }
                if (currentPage < totalPages) paginationHtml += \`<div class="page-btn" onclick="goToPage(\${currentPage+1})">Next →</div>\`;
                document.getElementById('pagination').innerHTML = paginationHtml;
            } else {
                document.getElementById('pagination').innerHTML = '';
            }
        }
        
        function goToPage(page) {
            currentPage = page;
            render();
            window.scrollTo(0, 0);
        }
        
        // Event listeners
        document.querySelectorAll('.tab').forEach(tab => {
            tab.addEventListener('click', () => {
                document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
                tab.classList.add('active');
                currentCategory = tab.dataset.category;
                currentPage = 1;
                render();
            });
        });
        
        document.getElementById('search').addEventListener('input', () => {
            currentPage = 1;
            render();
        });
        
        render();
    </script>
</body>
</html>
DASHEOF

# Cleanup
rm -rf "$TEMP_DIR"

echo -e "\n${C}═══════════════════════════════════════════════${N}"
echo -e "${G}✅ C25 FULL CONSTELLATION COMPLETE${N}"
echo -e "${C}═══════════════════════════════════════════════${N}"
echo -e "${Y}📊 Dashboard: $DASHBOARD${N}"
echo -e "${Y}📋 Manifest: $MANIFEST${N}"
echo -e "${Y}📁 Total Files: $TOTAL_FILES${N}"
echo -e "\n${C}Open:${N}"
echo -e "  termux-open $DASHBOARD"

