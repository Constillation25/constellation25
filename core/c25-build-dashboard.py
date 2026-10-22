#!/data/data/com.termux/files/usr/bin/env python3
"""
C25 OMNISCIENT DASHBOARD GENERATOR
Reads the Total Recall SQLite DB and builds an interactive, interconnected HTML platform.
"""

import sqlite3
import json
import os
from pathlib import Path
from datetime import datetime

HOME_DIR = Path.home()
DB_PATH = HOME_DIR / "c25_store" / "omniscient_index.db"
OUTPUT_DIR = HOME_DIR / "c25_store" / "omniscient_dashboard"
DASHBOARD_HTML = OUTPUT_DIR / "index.html"

def main():
    if not DB_PATH.exists():
        print("❌ Database not found. Run c25-omniscient-indexer.py first.")
        return

    print("🌌 Building C25 Omniscient Dashboard...")
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    
    # 1. Get Ecosystem Stats
    stats_query = """
        SELECT location_type, COUNT(*) as count, ROUND(SUM(size_bytes) / 1024.0 / 1024.0, 2) as size_mb
        FROM artifacts GROUP BY location_type ORDER BY count DESC
    """
    stats = {row['location_type']: {'count': row['count'], 'size_mb': row['size_mb']} 
             for row in conn.execute(stats_query).fetchall()}
    
    total_files = sum(s['count'] for s in stats.values())
    total_size = sum(s['size_mb'] for s in stats.values())
    
    # 2. Get File Extensions Breakdown
    ext_query = """
        SELECT extension, COUNT(*) as count 
        FROM artifacts GROUP BY extension ORDER BY count DESC LIMIT 10
    """
    extensions = {row['extension'] or 'no_ext': row['count'] 
                  for row in conn.execute(ext_query).fetchall()}
    
    # 3. Get Top Interconnected Hubs (Keywords referenced most)
    hubs_query = """
        SELECT target_keyword, connection_type, COUNT(*) as refs
        FROM connections
        WHERE target_keyword IS NOT NULL AND target_keyword != ''
        GROUP BY target_keyword
        ORDER BY refs DESC
        LIMIT 15
    """
    hubs = [dict(row) for row in conn.execute(hubs_query).fetchall()]
    
    # 4. Get Sample of Files for the initial view (limit to 500 for performance)
    files_query = """
        SELECT id, name, path, extension, size_bytes, preview, location_type
        FROM artifacts
        ORDER BY size_bytes DESC
        LIMIT 500
    """
    files = [dict(row) for row in conn.execute(files_query).fetchall()]
    
    # 5. Get Connections for those files
    file_ids = [f['id'] for f in files]
    placeholders = ','.join('?' * len(file_ids))
    conn_query = f"""
        SELECT source_id, target_keyword, connection_type
        FROM connections
        WHERE source_id IN ({placeholders})
    """
    connections_list = [dict(row) for row in conn.execute(conn_query, file_ids).fetchall()]
    
    # Group connections by file_id
    file_connections = {}
    for c in connections_list:
        if c['source_id'] not in file_connections:
            file_connections[c['source_id']] = []
        file_connections[c['source_id']].append(c)
        
    for f in files:
        f['connections'] = file_connections.get(f['id'], [])

    conn.close()
    
    # Build the Dashboard HTML
    print("🎨 Rendering interactive HTML dashboard...")
    
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>C25 Omniscient Dashboard</title>
    <style>
        :root {{
            --bg-primary: #0a0e27;
            --bg-secondary: #1a1f3a;
            --accent: #00d4ff;
            --accent-glow: rgba(0, 212, 255, 0.3);
            --text-primary: #e0e6ed;
            --text-secondary: #8b95a5;
            --border: rgba(255, 255, 255, 0.1);
        }}
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: var(--bg-primary);
            color: var(--text-primary);
            min-height: 100vh;
            padding: 2rem;
        }}
        .container {{ max-width: 1600px; margin: 0 auto; }}
        
        header {{
            text-align: center;
            margin-bottom: 3rem;
            padding: 2rem;
            background: rgba(255,255,255,0.03);
            border-radius: 16px;
            border: 1px solid var(--border);
        }}
        h1 {{
            font-size: 2.5rem;
            background: linear-gradient(90deg, #00d4ff, #7b2ff7);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0.5rem;
        }}
        .subtitle {{ color: var(--text-secondary); font-size: 1.1rem; }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
            margin-bottom: 2rem;
        }}
        .stat-card {{
            background: var(--bg-secondary);
            padding: 1.5rem;
            border-radius: 12px;
            border: 1px solid var(--border);
            text-align: center;
        }}
        .stat-value {{ font-size: 2rem; font-weight: bold; color: var(--accent); }}
        .stat-label {{ color: var(--text-secondary); font-size: 0.9rem; margin-top: 0.5rem; }}
        
        .hubs-section {{
            background: var(--bg-secondary);
            padding: 1.5rem;
            border-radius: 12px;
            border: 1px solid var(--border);
            margin-bottom: 2rem;
        }}
        .hubs-title {{ font-size: 1.2rem; color: var(--accent); margin-bottom: 1rem; }}
        .hub-tags {{ display: flex; flex-wrap: wrap; gap: 0.5rem; }}
        .hub-tag {{
            background: rgba(123, 47, 247, 0.2);
            color: #c4b5fd;
            padding: 0.4rem 0.8rem;
            border-radius: 20px;
            font-size: 0.85rem;
            border: 1px solid rgba(123, 47, 247, 0.4);
        }}
        
        .search-container {{ margin-bottom: 2rem; }}
        .search-input {{
            width: 100%;
            padding: 1rem 1.5rem;
            background: var(--bg-secondary);
            border: 1px solid var(--border);
            border-radius: 12px;
            color: var(--text-primary);
            font-size: 1rem;
            transition: all 0.3s;
        }}
        .search-input:focus {{
            outline: none;
            border-color: var(--accent);
            box-shadow: 0 0 0 3px var(--accent-glow);
        }}
        
        .files-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
            gap: 1rem;
        }}
        .file-card {{
            background: var(--bg-secondary);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 1.2rem;
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }}
        .file-card:hover {{
            transform: translateY(-4px);
            border-color: var(--accent);
            box-shadow: 0 8px 24px var(--accent-glow);
        }}
        .file-card::before {{
            content: '';
            position: absolute;
            top: 0; left: 0; right: 0;
            height: 3px;
            background: linear-gradient(90deg, var(--accent), #7b2ff7);
        }}
        .file-header {{ display: flex; justify-content: space-between; align-items: start; margin-bottom: 0.8rem; }}
        .file-name {{ font-weight: 600; color: var(--accent); font-size: 1rem; word-break: break-all; }}
        .file-ext {{
            background: rgba(0, 212, 255, 0.1);
            color: var(--accent);
            padding: 0.2rem 0.6rem;
            border-radius: 4px;
            font-size: 0.75rem;
            font-weight: 600;
            white-space: nowrap;
        }}
        .file-path {{
            font-family: 'Courier New', monospace;
            font-size: 0.75rem;
            color: var(--text-secondary);
            margin-bottom: 0.8rem;
            word-break: break-all;
            display: -webkit-box;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
            overflow: hidden;
        }}
        .file-preview {{
            background: rgba(0,0,0,0.3);
            padding: 0.8rem;
            border-radius: 8px;
            font-family: 'Courier New', monospace;
            font-size: 0.75rem;
            color: var(--text-secondary);
            margin-bottom: 0.8rem;
            white-space: pre-wrap;
            word-break: break-word;
            max-height: 100px;
            overflow-y: auto;
        }}
        .file-connections {{
            display: flex;
            flex-wrap: wrap;
            gap: 0.4rem;
            margin-top: 0.8rem;
            padding-top: 0.8rem;
            border-top: 1px solid var(--border);
        }}
        .conn-tag {{
            font-size: 0.7rem;
            padding: 0.2rem 0.5rem;
            background: rgba(255,255,255,0.05);
            border-radius: 4px;
            color: var(--text-secondary);
        }}
        .conn-tag strong {{ color: var(--accent); }}
        
        .file-actions {{
            display: flex;
            gap: 0.5rem;
            margin-top: 1rem;
        }}
        .btn {{
            flex: 1;
            padding: 0.6rem;
            background: rgba(0, 212, 255, 0.1);
            border: 1px solid rgba(0, 212, 255, 0.3);
            border-radius: 8px;
            color: var(--accent);
            text-decoration: none;
            text-align: center;
            font-size: 0.85rem;
            font-weight: 500;
            transition: all 0.2s;
        }}
        .btn:hover {{ background: rgba(0, 212, 255, 0.2); }}
        .btn-primary {{ background: linear-gradient(90deg, var(--accent), #7b2ff7); border: none; color: white; }}
        .btn-primary:hover {{ opacity: 0.9; }}
        
        footer {{
            text-align: center;
            margin-top: 3rem;
            padding: 2rem;
            color: var(--text-secondary);
            font-size: 0.9rem;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🌌 C25 Omniscient Dashboard</h1>
            <p class="subtitle">Total Recall Forensic Engine • Unified Knowledge Graph</p>
        </header>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-value">{total_files:,}</div>
                <div class="stat-label">Total Artifacts</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{total_size:.1f} MB</div>
                <div class="stat-label">Total Indexed Size</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{len(stats)}</div>
                <div class="stat-label">Source Locations</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{len(hubs)}</div>
                <div class="stat-label">Active Hubs</div>
            </div>
        </div>
        
        <div class="hubs-section">
            <div class="hubs-title">🔗 Top Interconnected Hubs (Most Referenced)</div>
            <div class="hub-tags">
                {''.join(f'<span class="hub-tag">{h["target_keyword"]} <small>({h["refs"]} refs)</small></span>' for h in hubs) or '<span style="color: var(--text-secondary);">No connections mapped yet. Run indexer with fresh DB.</span>'}
            </div>
        </div>
        
        <div class="search-container">
            <input type="text" class="search-input" id="searchInput" placeholder="🔍 Search files by name, path, extension, or content preview...">
        </div>
        
        <div class="files-grid" id="filesGrid">
            <!-- Files injected via JS -->
        </div>
        
        <footer>
            <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p>C25 Sovereign AI Ecosystem • Zero-Scatter Doctrine • Local-First Architecture</p>
        </footer>
    </div>
    
    <script>
        const filesData = {json.dumps(files)};
        
        function renderFiles(files) {{
            const grid = document.getElementById('filesGrid');
            if (files.length === 0) {{
                grid.innerHTML = '<p style="grid-column: 1/-1; text-align: center; color: var(--text-secondary); padding: 2rem;">No files match your search.</p>';
                return;
            }}
            
            grid.innerHTML = files.map(file => {{
                const connHtml = file.connections.length > 0 
                    ? `<div class="file-connections">` + 
                      file.connections.slice(0, 5).map(c => 
                        `<span class="conn-tag"><strong>${{c.connection_type}}:</strong> ${{c.target_keyword}}</span>`
                      ).join('') + 
                      `</div>` 
                    : '';
                
                return `
                    <div class="file-card">
                        <div class="file-header">
                            <div class="file-name">${{file.name}}</div>
                            <div class="file-ext">${{file.extension || 'file'}}</div>
                        </div>
                        <div class="file-path">${{file.path}}</div>
                        <div class="file-preview">${{file.preview || 'No preview available'}}</div>
                        ${{connHtml}}
                        <div class="file-actions">
                            <a href="file://${{file.path}}" class="btn btn-primary" target="_blank">Open File</a>
                            <button class="btn" onclick="copyPath('${{file.path}}')">Copy Path</button>
                        </div>
                    </div>
                `;
            }}).join('');
        }}
        
        function copyPath(path) {{
            navigator.clipboard.writeText(path).then(() => {{
                alert('Path copied to clipboard!');
            }});
        }}
        
        document.getElementById('searchInput').addEventListener('input', (e) => {{
            const query = e.target.value.toLowerCase();
            const filtered = filesData.filter(f => 
                f.name.toLowerCase().includes(query) ||
                f.path.toLowerCase().includes(query) ||
                (f.extension && f.extension.toLowerCase().includes(query)) ||
                (f.preview && f.preview.toLowerCase().includes(query))
            );
            renderFiles(filtered);
        }});
        
        // Initial render
        renderFiles(filesData);
    </script>
</body>
</html>
"""
    
    with open(DASHBOARD_HTML, 'w', encoding='utf-8') as f:
        f.write(html_content)
        
    print(f"✅ Dashboard successfully built!")
    print(f"📊 Location: {DASHBOARD_HTML}")
    print(f"\n🚀 Open it in your browser:")
    print(f"   termux-open {DASHBOARD_HTML}")

if __name__ == "__main__":
    main()
