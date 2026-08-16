#!/data/data/com.termux/files/usr/bin/bash
set -uo pipefail
C25="$HOME/constellation25"; MAN="$C25/manifests"; OUT="$C25/master_ui"
mkdir -p "$OUT"; NT=$(mktemp); ET=$(mktemp)
AGENTS="earth mercury venus mars jupiter saturn uranus neptune pluto sun moon apollo artemis atlas forge nexus echo prism juno vesta ceres pallas titan aegis oracle"
declare -A RIDX B2I
getmod() { local p="$1" b; while [ -n "$p" ] && [ "$p" != "/" ]; do b="${p##*/}"; [ -n "${RIDX[$b]:-}" ] && { echo "$b"; return; }; p="${p%/*}"; done; }
emit(){ printf '[%s,"%s","%s","%s",%s],\n' "$1" "$2" "$3" "$4" "$5" >> "$NT"; }
edge(){ printf '[%s,%s,%s],\n' "$1" "$2" "$3" >> "$ET"; }
i=0; emit 0 core "PATHOS CORE" "constellation25/pathos" -1
for a in $AGENTS; do i=$((i+1)); emit $i agent "$a" "c25/agents/$a" 0; edge 0 $i 2; done
j=1; for a in $AGENTS; do edge $j $((j%25+1)) 2; j=$((j+1)); done
while IFS= read -r r; do [ -n "$r" ] || continue; i=$((i+1)); RIDX[$r]=$i; emit $i repo "$r" "repos/$r" 0; edge 0 $i 2; done < "$MAN/hubs.txt"
while IFS= read -r f; do [ -n "$f" ] || continue
  b="${f##*/}"; b="${b//\"/}"; m=$(getmod "$(dirname "$f")"); p=0; [ -n "$m" ] && p=${RIDX[$m]}
  i=$((i+1)); B2I[$b]=$i; emit $i file "$b" "$f" $p; edge $i $p 0
done < "$MAN/html_all.txt"
n=0
while IFS= read -r f; do [ -n "$f" ] || continue; n=$((n+1)); [ $n -gt 4000 ] && break
  s=${B2I["${f##*/}"]:-}; [ -n "$s" ] || continue
  grep -oE '(href|src)="[^"]+"' "$f" 2>/dev/null | sed -E 's/.*"([^"/]+)"$/\1/' | while IFS= read -r ref; do
    t=${B2I[$ref]:-}; [ -n "$t" ] && [ "$t" != "$s" ] && edge $s $t 1
  done
done < "$MAN/html_all.txt"
sort -u "$ET" -o "$ET"
cat > "$OUT/universe.html" <<'HTML'
<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>CONSTELLATION25 × PATHOS — Spatial Ops Universe</title>
<style>body{margin:0;overflow:hidden;background:#04070c;font-family:ui-monospace,monospace;color:#cfe3ff}
#cv{display:block}#hud{position:fixed;top:10px;left:12px;font-size:12px;text-shadow:0 0 8px #4da3ff}
#hud b{color:#4da3ff}#q{position:fixed;top:10px;right:12px;background:#0a1220;border:1px solid #1f3a5f;color:#cfe3ff;padding:6px 10px;border-radius:6px}
#p{position:fixed;right:12px;top:48px;max-width:320px;max-height:45vh;overflow:auto;background:#0a1220ee;border:1px solid #1f3a5f;border-radius:8px;padding:10px;font-size:11px;display:none}
#con{position:fixed;left:0;right:0;bottom:0;background:#050a12f2;border-top:1px solid #1f3a5f;font-size:11px}
#log{height:110px;overflow:auto;padding:6px 10px;white-space:pre-wrap;color:#7dffb2}
#cin{width:100%;background:#0a1220;border:0;border-top:1px solid #1f3a5f;color:#7dffb2;padding:8px 10px;font-family:inherit;outline:none}</style>
</head><body><canvas id="cv"></canvas>
<div id="hud"><b>CONSTELLATION25 × PATHOS</b> // SPATIAL OPS UNIVERSE<br><span id="st"></span></div>
<input id="q" placeholder="search module / file…"><div id="p"></div>
<div id="con"><div id="log"></div><input id="cin" placeholder="> help"></div>
<script>
const N=[
HTML
cat "$NT" >> "$OUT/universe.html"; echo "];const E=[" >> "$OUT/universe.html"; cat "$ET" >> "$OUT/universe.html"
cat >> "$OUT/universe.html" <<'HTML2'
];
const CV=document.getElementById('cv'),X=CV.getContext('2d');let W,H;
function rs(){const d=devicePixelRatio||1;W=CV.width=innerWidth*d;H=CV.height=innerHeight*d}rs();onresize=rs;
let px=0,py=0,sc=.8,sel=-1;const POS=[],DEG=[],RP={};let ri=0;
const RC=N.filter(n=>n[1]=="repo").length||1;
N.forEach((n,i)=>{if(n[1]=="repo"){const a=ri++/RC*6.283;RP[i]={x:Math.cos(a)*340,y:Math.sin(a)*340}}});
N.forEach((n,i)=>{if(n[1]=="core")POS[i]={x:0,y:0};
 else if(n[1]=="agent"){const a=(i-1)/25*6.283;POS[i]={x:Math.cos(a)*150,y:Math.sin(a)*150}}
 else if(n[1]=="repo")POS[i]=RP[i];
 else{const c=RP[n[4]]||{x:0,y:0};const h=(i*2654435761%360)*.01745,d=35+(i*97)%120;POS[i]={x:c.x+Math.cos(h)*d,y:c.y+Math.sin(h)*d}}});
E.forEach(e=>{DEG[e[0]]=(DEG[e[0]]||0)+1;DEG[e[1]]=(DEG[e[1]]||0)+1});
const STARS=[...Array(500)].map(()=>({x:Math.random(),y:Math.random(),z:Math.random()}));
document.getElementById('st').textContent=N.length+" nodes • "+E.length+" edges • "+RC+" repos • "+N.filter(n=>n[1]=="file").length+" html files";
function draw(){X.setTransform(1,0,0,1,0,0);X.fillStyle="#04070c";X.fillRect(0,0,W,H);
 X.fillStyle="#9fc9ff";STARS.forEach(s=>{X.globalAlpha=.2+s.z*.6;X.fillRect(s.x*W,s.y*H,s.z*2,s.z*2)});X.globalAlpha=1;
 X.setTransform(sc,0,0,sc,W/2+px,H/2+py);
 E.forEach(e=>{if(e[2]==0&&sc<.6)return;X.strokeStyle=e[2]==1?"rgba(0,255,200,.5)":e[2]==2?"rgba(255,190,80,.35)":"rgba(77,163,255,.12)";
  X.beginPath();X.moveTo(POS[e[0]].x,POS[e[0]].y);X.lineTo(POS[e[1]].x,POS[e[1]].y);X.stroke()});
 N.forEach((n,i)=>{const p=POS[i];if(n[1]=="file"){X.fillStyle=i==sel?"#fff":"#6ea8e8";X.fillRect(p.x-1,p.y-1,2.2,2.2)}
  else{const r=n[1]=="core"?26:n[1]=="agent"?7:4+Math.min(8,(DEG[i]||2)/8);
   X.fillStyle=n[1]=="core"?"#ffd76a":n[1]=="agent"?"#ff9a4d":"#4da3ff";X.shadowColor=X.fillStyle;X.shadowBlur=i==sel?25:10;
   X.beginPath();X.arc(p.x,p.y,r,0,7);X.fill();X.shadowBlur=0;
   if(sc>1.4||n[1]=="file"&&sc>3){X.fillStyle="#cfe3ff";X.font=(n[1]=="core"?14:9)+"px monospace";X.fillText(n[2],p.x+r+3,p.y+3)}}});
 requestAnimationFrame(draw)}draw();
let dn=0,mx,my;CV.addEventListener('pointerdown',e=>{dn=1;mx=e.clientX;my=e.clientY});
CV.addEventListener('pointermove',e=>{if(dn){px+=(e.clientX-mx)*devicePixelRatio;py+=(e.clientY-my)*devicePixelRatio;mx=e.clientX;my=e.clientY}});
CV.addEventListener('pointerup',e=>{dn=0;const d=devicePixelRatio;
 const wx=(e.clientX*d-W/2-px)/sc,wy=(e.clientY*d-H/2-py)/sc;let bi=-1,bd=1e9;
 POS.forEach((p,i)=>{const q=(p.x-wx)**2+(p.y-wy)**2;if(q<bd){bd=q;bi=i}});
 if(bd<(20/sc)**2)show(bi)});
CV.addEventListener('wheel',e=>{sc*=e.deltaY<0?1.2:.83;sc=Math.min(8,Math.max(.15,sc));e.preventDefault()},{passive:false});
function show(i){sel=i;const n=N[i],P=document.getElementById('p');P.style.display="block";
 const lk=E.filter(e=>e[0]==i||e[1]==i).slice(0,40).map(e=>N[e[0]==i?e[1]:e[0]][2]).join("<br>");
 P.innerHTML="<b style='color:#4da3ff'>"+n[2]+"</b> ["+n[1]+"]<br><span style='color:#7a8ca3'>"+n[3]+"</span><br>links: "+(DEG[i]||0)+"<br>"+lk}
const LOG=document.getElementById('log');function say(t){LOG.textContent+=t+"\n";LOG.scrollTop=1e9}
say("PATHOS CORE online • "+N.length+" nodes mapped • IPC mesh live");
document.getElementById('cin').onkeydown=e=>{if(e.key!="Enter")return;const c=e.target.value;e.target.value="";say("> "+c);
 const[a,...r]=c.split(" ");const q=r.join(" ");
 if(a=="help")say("cmds: count | focus <q> | links <q> | repos | agents | clear");
 else if(a=="count")say(document.getElementById('st').textContent);
 else if(a=="clear")LOG.textContent="";
 else if(a=="repos")say(N.filter(n=>n[1]=="repo").map(n=>n[2]).join(", "));
 else if(a=="agents")say(N.filter(n=>n[1]=="agent").map(n=>n[2]).join(", "));
 else if(a=="focus"||a=="links"){const i=N.findIndex(n=>n[2].toLowerCase().includes(q.toLowerCase()));
  if(i<0)say("no match");else{sel=i;show(i);px=-POS[i].x*sc;py=-POS[i].y*sc;say("locked: "+N[i][2])}}
 else say("unknown cmd - try help")};
document.getElementById('q').onkeydown=e=>{if(e.key=="Enter"){const i=N.findIndex(n=>n[2].toLowerCase().includes(e.target.value.toLowerCase()));
 if(i>=0){sel=i;show(i);px=-POS[i].x*sc;py=-POS[i].y*sc;sc=Math.max(sc,2)}}};
</script></body></html>
HTML2
cp "$OUT/universe.html" "$OUT/index.html"; rm -f "$NT" "$ET"
echo "[VENUS+PRISM] universe built: $(wc -c < "$OUT/universe.html") bytes"
