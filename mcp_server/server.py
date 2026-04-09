import http.server, json, os, time
from pathlib import Path

Q = Path(os.getenv("C25_Q", str(Path.home()/.c25_agent_queue)))
P = int(os.getenv("C25_P", "8765"))

def run():
    rev=0.0; cnt=0
    for f in Q.glob("*.json"):
        try:
            d=json.loads(f.read_text())
            if d.get("status") in ("completed","processing"): continue
            d["status"]="processing"; f.write_text(json.dumps(d))
            t=d.get("task","")
            b=float(str(d.get("budget","0")).replace("$","").replace(",","") or "0")
            r = b*0.01 if t=="invoice" else (0.05 if "draft" in t else 0.02)
            d["status"]="completed"; d["revenue_accrued"]=r
            d["processed_at"]=time.strftime("%Y-%m-%dT%H:%M:%SZ")
            f.write_text(json.dumps(d)); rev+=r; cnt+=1
            print(f"[MCP] {d.get('agent','?')} | {t} | +${r:.2f}")
        except Exception as e: print(f"[MCP] err: {e}")
    return cnt, rev

class H(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200); self.send_header("Content-type","application/json"); self.end_headers()
        p=sum(1 for f in Q.glob("*.json") if '"pending"' in f.read_text())
        self.wfile.write(json.dumps({"pending":p,"port":P}).encode())
    def do_POST(self):
        if self.path=="/process":
            c,r=run()
            self.send_response(200); self.send_header("Content-type","application/json"); self.end_headers()
            self.wfile.write(json.dumps({"processed":c,"revenue":r}).encode())
        else: self.send_response(404); self.end_headers()
    def log_message(self,*a): pass

if __name__=="__main__":
    print(f"[MCP] Start :{P} | Q:{Q}")
    http.server.HTTPServer(("0.0.0.0",P),H).serve_forever()
