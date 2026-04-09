#!/usr/bin/env bash
set -o pipefail; export LC_ALL=C
QUEUE="$HOME/.c25_agent_queue"
LOG="$HOME/constellation25/logs/stalker.log"
: > "$LOG"
log() { echo "[$(date +%H:%M:%S)] [Stalker] $*" | tee -a "$LOG"; }

log "START" "Scanning global platforms for AI/automation contracts..."

# Helper: Queue a qualified gig
queue_gig() {
  local title="$1" url="$2" source="$3" budget="${4:-2500}"
  [[ -z "$title" || -z "$url" ]] && return
  id=$(echo "${url}${title}" | md5sum | cut -c1-10)
  # Skip if already queued
  grep -q "$id" "$QUEUE"/*.json 2>/dev/null && return
  cat > "$QUEUE/stalker_${source}_${id}.json" << EOF
{"agent":"Agent_Mars","task":"draft","title":"$title","url":"$url","source":"$source","budget":"$budget","status":"pending","priority":"high","found_at":"$(date -u +%Y-%m-%dT%H:%M:%SZ)"}
EOF
  log "✅ QUEUED: [$source] ${title:0:50}... (\$$budget)"
}

# Platform 1: Reddit r/forhire (JSON API)
scan_reddit() {
  curl -sf "https://www.reddit.com/r/forhire/search.json?q=ai+OR+automation+OR+agent+OR+orchestrat+OR+langchain+OR+crewai&sort=new&restrict_sr=1&limit=15" \
    -H "User-Agent: Mozilla/5.0 (C25-Stalker/1.0)" --max-time 15 2>/dev/null | \
  python3 -c "
import sys,json,re
try:
  data=json.load(sys.stdin).get('data',{}).get('children',[])
  for c in 
    p=c.get('data',{}); t=p.get('title',''); st=p.get('selftext','')
    # Filter for paid gigs with budget indicators
    if any(k in (t+st).lower() for k in ['budget','pay','\$','hourly','fixed','contract','project','hire']) and any(k in (t+st).lower() for k in ['ai','automation','agent','orchestrat','langchain','crewai','autogen']):
      budget='2500'
      if re.search(r'\$\s*([2-9][0-9]{3,}|[0-9]{4,})', st): budget=re.search(r'\$\s*([0-9,]+)', st).group(1).replace(',','')
      print(f'{t}|https://reddit.com{p.get(\"permalink\",\"\")}|reddit|{budget}')
except Exception as e: print(f'ERROR: {e}', file=sys.stderr)
" 2>/dev/null | while IFS='|' read -r title url source budget; do
    queue_gig "$title" "$url" "$source" "$budget"
  done
}

# Platform 2: Upwork AI Category RSS
scan_upwork() {
  curl -sf "https://www.upwork.com/nx/api/job-feed/v1/search?client=upwork&format=rss&q=autonomous%20agent%20OR%20ai%20automation%20OR%20langchain%20OR%20crewai&category=531770282584862720" \
    -H "User-Agent: Mozilla/5.0" --max-time 15 2>/dev/null | \
  python3 -c "
import sys,xml.etree.ElementTree as ET,re
try:
  root=ET.fromstring(sys.stdin.read())
  for item in root.findall('.//item'):
    t=item.findtext('title',''); d=item.findtext('description',''); l=item.findtext('link','')
    if any(k in (t+d).lower() for k in ['ai','agent','automation','orchestrat','langchain','crewai']):
      budget='3500'
      if re.search(r'\$\s*([0-9,]+)', d): budget=re.search(r'\$\s*([0-9,]+)', d).group(1).replace(',','')
      print(f'{t}|{l}|upwork|{budget}')
except Exception as e: print(f'ERROR: {e}', file=sys.stderr)
" 2>/dev/null | while IFS='|' read -r title url source budget; do
    queue_gig "$title" "$url" "$source" "$budget"
  done
}

# Platform 3: Wellfound/AngelList (Startup Jobs)
scan_wellfound() {
  curl -sf "https://wellfound.com/api/jobs?query=ai+agent+automation&location=Remote" \
    -H "User-Agent: Mozilla/5.0" --max-time 15 2>/dev/null | \
  python3 -c "
import sys,json,re
try:
  jobs=json.load(sys.stdin).get('jobs',[])[:10]
  for j in jobs:
    t=j.get('name',''); d=j.get('short_description',''); u=j.get('url','')
    comp=j.get('compensation',{})
    budget=str(comp.get('min','5000'))
    if any(k in (t+d).lower() for k in ['agent','automation','ai','orchestrat']):
      print(f'{t}|{u}|wellfound|{budget}')
except Exception as e: print(f'ERROR: {e}', file=sys.stderr)
" 2>/dev/null | while IFS='|' read -r title url source budget; do
    queue_gig "$title" "$url" "$source" "$budget"
  done
}

# Platform 4: HackerNews "Who is hiring?" (monthly thread parser)
scan_hn() {
  # Fetch latest "Who is hiring?" thread ID (simplified)
  curl -sf "https://hn.algolia.com/api/v1/search?query=who%20is%20hiring&tags=story&numericFilters=points%3E50" \
    --max-time 10 2>/dev/null | \
  python3 -c "
import sys,json,re
try:
  data=json.load(sys.stdin).get('hits',[])
  for h in data[:3]:
    t=h.get('title',''); u=h.get('url','') or f\"https://news.ycombinator.com/item?id={h.get('objectID','')}\"
    if 'hiring' in t.lower() and any(k in t.lower() for k in ['ai','automation','agent']):
      print(f'{t}|{u}|hackernews|4000')
except: pass
" 2>/dev/null | while IFS='|' read -r title url source budget; do
    queue_gig "$title" "$url" "$source" "$budget"
  done
}

# Platform 5: RemoteOK AI Tag (JSON API)
scan_remoteok() {
  curl -sf "https://remoteok.com/api?tag=ai&limit=10" \
    -H "User-Agent: Mozilla/5.0" --max-time 10 2>/dev/null | \
  python3 -c "
import sys,json
try:
  jobs=json.load(sys.stdin)
  for j in jobs:
    t=j.get('position',''); c=j.get('company',''); u=j.get('url','')
    budget=j.get('min_salary',2500)
    if any(k in (t+c).lower() for k in ['agent','automation','ai','orchestrat']):
      print(f'{t} at {c}|{u}|remoteok|{budget}')
except: pass
" 2>/dev/null | while IFS='|' read -r title url source budget; do
    queue_gig "$title" "$url" "$source" "$budget"
  done
}

# Run all scans (with rate-limit delays)
scan_reddit; sleep 2
scan_upwork; sleep 2
scan_wellfound; sleep 2
scan_hn; sleep 2
scan_remoteok

# Summary
new_count=$(ls -1 "$QUEUE"/stalker_*.json 2>/dev/null | wc -l | tr -d ' ')
log "COMPLETE" "Scan finished. $new_count new opportunities queued."

# Auto-trigger agent processing if new gigs found
if [[ "$new_count" -gt 0 ]]; then
  log "TRIGGER" "Processing new queue with Agent_Mars..."
  "$HOME/constellation25/c25_run_agents.sh" run 2>/dev/null || true
fi
