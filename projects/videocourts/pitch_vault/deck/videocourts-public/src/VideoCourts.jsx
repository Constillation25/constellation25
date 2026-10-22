import { useState } from "react";

export default function VideoCourts() {
  const [expanded, setExpanded] = useState(false);
  const sessions = [{ id:"s1", caseNumber:"CR-24-1087", title:"State v. Dalton", status:"live", judge:"Hon. Martinez" }];

  return (
    <div className="p-4 bg-slate-950 text-white min-h-screen font-mono">
      <h1 className="text-2xl font-bold text-emerald-400 mb-2">Judicial Session Console</h1>
      <p className="text-slate-400 mb-6">Sovereign Identity & Justice Platform</p>
      {sessions.map(s => (
        <div key={s.id} className="border border-slate-800 p-4 rounded-lg mb-4 bg-slate-900">
          <h2 className="text-lg font-bold">{s.title} ({s.caseNumber})</h2>
          <p className="text-sm text-slate-400">Judge: {s.judge} | Status: <span className="text-red-400">{s.status}</span></p>
          <button onClick={() => setExpanded(v => !v)} className="mt-3 w-full p-2 bg-transparent border border-slate-700 rounded text-xs text-slate-300 hover:bg-slate-800">
            {expanded ? "Hide Details" : "Show Details"}
          </button>
          {expanded && <div className="mt-3 p-3 bg-slate-950 border border-slate-800 rounded text-xs text-slate-400">Biometric: Verified | Recording: Active</div>}
        </div>
      ))}
    </div>
  );
}
