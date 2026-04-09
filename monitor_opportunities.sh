#!/usr/bin/env bash
set -o pipefail; export LC_ALL=C
QUEUE="$HOME/.c25_agent_queue"
LOG="$HOME/constellation25/opportunity_monitor.log"
: > "$LOG"

log() { echo "[$(date +%H:%M:%S)] [Monitor] $*" | tee -a "$LOG"; }
log "START" "Scanning for new funding/opportunity signals..."

# Check Reddit r/forhire for new AI/agent gigs
curl -sf "https://www.reddit.com/r/forhire/search.json?q=ai+OR+automation+OR+agent+OR+funding&sort=new&restrict_sr=1&limit=5" \
  -H "User-Agent: Mozilla/5.0 (C25-Monitor/1.0)" 2>/dev/null | \
python3 -c "
import sys,json,re
data=json.load(sys.stdin).get('data',{}).get('children',[])
for c in 
  p=c.get('data',{}); t=p.get('title',''); st=p.get('selftext','')
  if any(k in (t+st).lower() for k in ['budget','pay','\$','funding','investment','contract','hire']):
    print(f'NEW:{t}|https://reddit.com{p.get(\"permalink\",\"\")}')
" 2>/dev/null | while IFS='|' read -r title url; do
  [[ -z "$title" ]] && continue
  id=$(echo "$url$title" | md5sum | cut -c1-10)
  # Only queue if not already present
  if ! grep -q "$id" "$QUEUE"/*.json 2>/dev/null; then
    cat > "$QUEUE/opp_${id}.json" << EOF
{"type":"opportunity","title":"$title","url":"$url","status":"new","source":"reddit","priority":"high"}
EOF
    log "NEW OPP: $title"
  fi
done

# Check Wellfound for new AI startup funding rounds
curl -sf "https://wellfound.com/api/jobs?query=ai+agent+funding&location=Remote" 2>/dev/null | \
python3 -c "
import sys,json
jobs=json.load(sys.stdin).get('jobs',[])[:3]
for j in jobs:
  t=j.get('name',''); u=j.get('url',''); f=j.get('funding_stage','')
  if t and f: print(f'FUNDING:{t}|{u}|{f}')
" 2>/dev/null | while IFS='|' read -r title url stage; do
  [[ -z "$title" ]] && continue
  id=$(echo "$url$title" | md5sum | cut -c1-10)
  if ! grep -q "$id" "$QUEUE"/*.json 2>/dev/null; then
    cat > "$QUEUE/funding_${id}.json" << EOF
{"type":"funding_round","title":"$title","url":"$url","stage":"$stage","status":"new","source":"wellfound"}
EOF
    log "FUNDING SIGNAL: $title ($stage)"
  fi
done

log "COMPLETE" "Monitoring cycle finished. Check $QUEUE for new opportunities."
