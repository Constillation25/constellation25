#!/usr/bin/env bash
set -o pipefail; export LC_ALL=C
echo "=== C25 GLOBAL REVENUE DASHBOARD ==="
echo "Date: $(date +%Y-%m-%d) | Time: $(date +%H:%M)"
echo ""
echo "💰 Freelance Pipeline:"
accrued=$(python3 -c "
import json
from pathlib import Path
t=0.0
for f in Path.home().glob('.c25_agent_queue/*.json'):
  try:
    d=json.loads(f.read_text())
    r=d.get('revenue_accrued',0)
    if isinstance(r,(int,float)): t+=r
  except: pass
print(f'{t:.2f}')
" 2>/dev/null || echo "0.00")
printf "  Accrued: \$%.2f\n" "$accrued"
gap=$(python3 -c "print(f'{1000-float(\"$accrued\"):.2f}')" 2>/dev/null || echo "1000.00")
echo ""
echo "🌍 Global Stalker:"
stalker_count=$(ls -1 ~/.c25_agent_queue/stalker_*.json 2>/dev/null | wc -l | tr -d ' ')
echo "  New opportunities: $stalker_count"
echo ""
echo "🔗 Affiliate Clicks:"
python3 ~/constellation25/affiliate_content/tracker.py 2>/dev/null || echo "  Tracking active"
echo ""
echo "📦 Content Ready:"
yt=$(ls -1 ~/constellation25/youtube_content/scripts/*.md 2>/dev/null | wc -l | tr -d ' ')
aff=$(ls -1 ~/constellation25/affiliate_content/posts/*.md 2>/dev/null | wc -l | tr -d ' ')
echo "  YouTube scripts: $yt"
echo "  Affiliate posts: $aff"
echo ""
printf "🎯 Target: \$1,000/day | Gap: \$%.2f\n" "$gap"
