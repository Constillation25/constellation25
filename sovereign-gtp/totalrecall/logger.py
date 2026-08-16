#!/usr/bin/env python3
"""TotalRecall Forensic Logger"""
import json, hashlib, os, sys, time
from datetime import datetime
from pathlib import Path

class TotalRecallLogger:
    def __init__(self, logs_dir: str):
        self.logs_dir = Path(logs_dir)
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        self.log_file = self.logs_dir / "totalrecall.log"
        self.manifest_file = self.logs_dir / "totalrecall_mesh.manifest"
        self.chain_file = self.logs_dir / "totalrecall.chain"
        if not self.chain_file.exists():
            genesis = {
                "block_index": 0,
                "timestamp": datetime.now().isoformat(),
                "previous_hash": "0" * 64,
                "data": "Genesis block - Constellation25 SovereignGTP initialized",
                "nonce": 0
            }
            genesis["hash"] = self._calculate_hash(genesis)
            with open(self.chain_file, "w") as f:
                json.dump([genesis], f, indent=2)
    
    def _calculate_hash(self, block: dict) -> str:
        block_copy = block.copy()
        block_copy.pop("hash", None)
        block_string = json.dumps(block_copy, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()
    
    def log_event(self, agent: str, event_type: str, data: dict, output_file: str = None):
        with open(self.chain_file) as f:
            chain = json.load(f)
        prev_hash = chain[-1]["hash"] if chain else "0" * 64
        block = {
            "block_index": len(chain),
            "timestamp": datetime.now().isoformat(),
            "previous_hash": prev_hash,
            "agent": agent,
            "event_type": event_type,
            "data": data,
            "output_file": output_file,
            "nonce": 0
        }
        while not block["hash"].startswith("000"):
            block["nonce"] += 1
            block["hash"] = self._calculate_hash(block)
        chain.append(block)
        with open(self.chain_file, "w") as f:
            json.dump(chain, f, indent=2)
        log_entry = f"{block['timestamp']} | {agent.upper()} | {event_type} | {data.get('task_id', 'N/A')}"
        with open(self.log_file, "a") as f:
            f.write(log_entry + "\n")
        if output_file:
            with open(self.manifest_file, "a") as f:
                f.write(f"{block['timestamp']} | {agent.upper()} | {data.get('task_type', 'N/A')} -> {Path(output_file).name}\n")
        return block["hash"]
    
    def verify_chain(self) -> bool:
        with open(self.chain_file) as f:
            chain = json.load(f)
        for i in range(1, len(chain)):
            if chain[i]["previous_hash"] != chain[i-1]["hash"]:
                print(f"❌ Chain broken at block {i}")
                return False
            if self._calculate_hash(chain[i]) != chain[i]["hash"]:
                print(f"❌ Hash mismatch at block {i}")
                return False
        print(f"✅ Chain verified: {len(chain)} blocks")
        return True
    
    def export_audit(self, start_time: str = None, end_time: str = None) -> list:
        with open(self.chain_file) as f:
            chain = json.load(f)
        audit = []
        for block in chain[1:]:
            if start_time and block["timestamp"] < start_time: continue
            if end_time and block["timestamp"] > end_time: continue
            audit.append({
                "timestamp": block["timestamp"],
                "agent": block["agent"],
                "event": block["event_type"],
                "task_id": block["data"].get("task_id"),
                "output": block.get("output_file"),
                "hash": block["hash"]
            })
        return audit

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--daemon", action="store_true")
    parser.add_argument("--verify", action="store_true")
    parser.add_argument("--export")
    args = parser.parse_args()
    logs_dir = os.getenv("C25_LOGS", f"{os.path.expanduser('~')}/constellation25/sovereign-gtp/logs")
    logger = TotalRecallLogger(logs_dir)
    if args.verify:
        logger.verify_chain()
        return
    if args.export:
        audit = logger.export_audit()
        with open(args.export, "w") as f:
            json.dump(audit, f, indent=2)
        print(f"✅ Exported {len(audit)} events")
        return
    if args.daemon:
        print(f"🔐 TotalRecall daemon started")
        while True: time.sleep(60)
    print("TotalRecall Interactive Mode")
    print("Commands: verify, export <file>, exit")
    while True:
        cmd = input("> ").strip().split()
        if not cmd: continue
        if cmd[0] == "verify": logger.verify_chain()
        elif cmd[0] == "export" and len(cmd) > 1:
            audit = logger.export_audit()
            with open(cmd[1], "w") as f: json.dump(audit, f, indent=2)
            print(f"✅ Exported {len(audit)} events")
        elif cmd[0] == "exit": break
        else: print("Unknown command")

if __name__ == "__main__":
    main()
