#!/data/data/com.termux/files/usr/bin/bash
set -e

DB_PATH=~/constellation25/c25_unified_registry.db
DASHBOARD_DIR=~/constellation25/dashboard
mkdir -p $DASHBOARD_DIR

cat << 'HTMLEOF' > $DASHBOARD_DIR/index.html
<!DOCTYPE html>
<html>
<head>
    <title>Constellation25 Unified Platform</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #0a0a0a; color: #00ff00; }
        h1 { color: #00ffff; }
        .stats { display: flex; gap: 20px; margin: 20px 0; }
        .stat-box { background: #1a1a1a; padding: 15px; border-radius: 8px; border: 1px solid #00ff00; }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; }
        th, td { padding: 10px; text-align: left; border-bottom: 1px solid #333; }
        th { background: #1a1a1a; color: #00ffff; }
    </style>
</head>
<body>
    <h1>🌌 Constellation25 Unified Platform</h1>
    <p>Auto-discovered capabilities across 224+ repositories</p>
    <div class="stats">
HTMLEOF

sqlite3 $DB_PATH "SELECT capability_type, COUNT(*) FROM repo_capabilities GROUP BY capability_type;" | \
awk -F'|' '{print "        <div class=\"stat-box\"><h2>" $2 "</h2><p>" $1 "</p></div>"}' >> $DASHBOARD_DIR/index.html

echo '    </div><h2>Capabilities</h2><table><tr><th>Org</th><th>Repo</th><th>Type</th><th>Capability</th></tr>' >> $DASHBOARD_DIR/index.html

sqlite3 -separator '|' $DB_PATH "SELECT org, repo_name, capability_type, capability_name FROM repo_capabilities;" | \
awk -F'|' '{print "        <tr><td>" $1 "</td><td>" $2 "</td><td>" $3 "</td><td>" $4 "</td></tr>"}' >> $DASHBOARD_DIR/index.html

echo '    </table></body></html>' >> $DASHBOARD_DIR/index.html
echo "✅ Dashboard: $DASHBOARD_DIR/index.html"
