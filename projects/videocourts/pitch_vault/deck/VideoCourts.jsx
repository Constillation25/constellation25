import { useState, useEffect, useRef } from "react";

// ─── Data ───────────────────────────────────────────────────────────────────
const initialSessions = [
  {
    id: "s1", caseNumber: "CR-24-1087", title: "State v. Dalton",
    status: "live", type: "Arraignment", mode: "Remote", time: "09:00",
    elapsed: 754, judge: "Hon. Martinez", clerk: "R. Chen",
    circuit: "3rd Judicial Circuit", courtroom: "4B",
    recording: true, remote: true, legyc: true,
    biometric: "Verified", transcript: "Draft Live",
    nextMatter: "State v. Jordan (09:45)",
    participants: ["Hon. Martinez", "R. Chen", "Def. Dalton", "Att. Johnson", "Att. Rivera"],
    notes: "Defendant present via remote link. Counsel appearing in person."
  },
  {
    id: "s2", caseNumber: "CR-24-1122", title: "State v. Jordan",
    status: "scheduled", type: "Bond Review", mode: "JailCourt", time: "09:45",
    judge: "Hon. Martinez", clerk: "R. Chen",
    circuit: "3rd Judicial Circuit", courtroom: "4B",
    jailcourt: true, biometric: "Pending",
    participants: ["Hon. Martinez", "Def. Jordan", "Att. Williams"],
    notes: "Defendant in custody at County Detention Center."
  },
  {
    id: "s3", caseNumber: "CV-24-0198", title: "Smith v. Ortega",
    status: "scheduled", type: "Civil Motion", mode: "Live", time: "10:30",
    judge: "Hon. Martinez", clerk: "T. Park",
    circuit: "3rd Judicial Circuit", courtroom: "4B",
    remote: true,
    participants: ["Hon. Martinez", "T. Park", "Att. Smith", "Att. Ortega"],
    notes: "Motion for summary judgment. Discovery closes Friday."
  },
  {
    id: "s4", caseNumber: "EDU-24-0003", title: "Mock: Rivera v. State",
    status: "mock", type: "Training", mode: "Remote", time: "11:30",
    judge: "AI Trainer", clerk: "—",
    circuit: "Mock Trial Lab", courtroom: "EDU-1",
    mock: true,
    participants: ["AI Trainer", "Student A", "Student B"],
    notes: "Law school mock session. Full recording for review."
  }
];

const initialCases = [
  { id: "c1", caseNumber: "CR-24-1087", title: "State v. Dalton", status: "active", type: "Criminal", filed: "2024-01-15", judge: "Hon. Martinez", circuit: "3rd Judicial Circuit", docket: 12 },
  { id: "c2", caseNumber: "CR-24-1122", title: "State v. Jordan", status: "active", type: "Criminal", filed: "2024-02-01", judge: "Hon. Martinez", circuit: "3rd Judicial Circuit", docket: 8 },
  { id: "c3", caseNumber: "CV-24-0198", title: "Smith v. Ortega", status: "active", type: "Civil", filed: "2024-01-28", judge: "Hon. Martinez", circuit: "3rd Judicial Circuit", docket: 21 },
  { id: "c4", caseNumber: "CR-23-0991", title: "State v. Webb", status: "closed", type: "Criminal", filed: "2023-11-10", judge: "Hon. Chen", circuit: "3rd Judicial Circuit", docket: 34 },
  { id: "c5", caseNumber: "FAM-24-0044", title: "Brooks v. Brooks", status: "active", type: "Family", filed: "2024-03-02", judge: "Hon. Johnson", circuit: "Family Court", docket: 5 }
];

const initialEvidence = [
  { id: "e1", caseId: "c1", caseNumber: "CR-24-1087", fileName: "evidence_video.mp4", hash: "a3f5d8c2e1b9f4a7c6e2d1f8a9b3c5e7d4f6a8b2c9e3d1f5a7c4b6e8d2f9a1c3", uploadedBy: "Officer Davis", status: "verified", size: "24.5 MB", uploadDate: "2025-02-14", type: "video" },
  { id: "e2", caseId: "c1", caseNumber: "CR-24-1087", fileName: "witness_statement.pdf", hash: "b4f6e9d3c2a1e5f7b8c9d2e1a3f4b5c6e7d8f9a2b3c4e5f6a7b8c9d0e1f2a3b4", uploadedBy: "Att. Johnson", status: "verified", size: "1.2 MB", uploadDate: "2025-02-15", type: "document" },
  { id: "e3", caseId: "c2", caseNumber: "CR-24-1122", fileName: "booking_photo.jpg", hash: "c5d7f9a1b3e5c7d9f1a3b5c7d9e1a3c5f7b9d1f3a5c7e9b1d3f5a7c9e1b3d5f7", uploadedBy: "Det. Rodriguez", status: "verified", size: "0.8 MB", uploadDate: "2025-02-01", type: "image" },
  { id: "e4", caseId: "c3", caseNumber: "CV-24-0198", fileName: "contract_exhibit_A.pdf", hash: "d6e8f0a2b4c6d8e0f2a4b6c8d0e2f4a6b8c0d2e4f6a8b0c2d4e6f8a0b2c4d6e8", uploadedBy: "Att. Smith", status: "pending", size: "3.4 MB", uploadDate: "2025-03-01", type: "document" }
];

const initialNotifications = [
  { id: "n1", type: "alert", level: "warn", message: "Biometric verification pending: State v. Jordan (09:45)", time: "08:52", read: false },
  { id: "n2", type: "filing", level: "info", message: "CM/ECF: 3 new filings queued for CR-24-1087", time: "08:57", read: false },
  { id: "n3", type: "chain", level: "success", message: "LEGyC chain synchronized — node VC-ND-07 canonical", time: "09:03", read: false },
  { id: "n4", type: "sms", level: "warn", message: "SMS batch: 1 notification failed — Jordan (invalid number)", time: "09:05", read: true },
  { id: "n5", type: "system", level: "info", message: "TotalRecall streaming — last hash 0x92a3...df0c", time: "09:07", read: true },
  { id: "n6", type: "filing", level: "info", message: "Tyler Technologies sync complete — docket updated", time: "08:57", read: true }
];

const initialAuditLog = [
  { id: "a1", ts: "09:12:34", event: "Session Recording Started", actor: "R. Chen", case: "CR-24-1087", hash: "0x92a3df0c..." },
  { id: "a2", ts: "09:10:11", event: "Biometric Verified: Dalton", actor: "System", case: "CR-24-1087", hash: "0x7f2b1e4a..." },
  { id: "a3", ts: "09:08:55", event: "Remote Participant Joined", actor: "Att. Johnson", case: "CR-24-1087", hash: "0x4c9d3f8b..." },
  { id: "a4", ts: "09:03:22", event: "LEGyC Canonical Sync", actor: "VC-ND-07", case: "ALL", hash: "0x1a5e7c2f..." },
  { id: "a5", ts: "08:57:01", event: "CM/ECF Filing Queued", actor: "Clerk System", case: "CR-24-1087", hash: "0x9b4d6e1c..." }
];

// ─── Helpers ─────────────────────────────────────────────────────────────────
const fmtElapsed = (s) => {
  const h = Math.floor(s / 3600).toString().padStart(2, "0");
  const m = Math.floor((s % 3600) / 60).toString().padStart(2, "0");
  const sec = (s % 60).toString().padStart(2, "0");
  return `${h}:${m}:${sec}`;
};

const typeIcon = (t) => ({ video: "🎥", document: "📄", image: "🖼️" }[t] ?? "📎");

// ─── UI Atoms ────────────────────────────────────────────────────────────────
const Badge = ({ variant = "default", pulse, children, className = "" }) => {
  const v = {
    live:      "bg-red-500/20 text-red-300 border-red-500/40",
    recording: "bg-blue-500/20 text-blue-300 border-blue-500/40",
    remote:    "bg-sky-500/20 text-sky-300 border-sky-500/40",
    scheduled: "bg-indigo-500/20 text-indigo-300 border-indigo-500/40",
    verified:  "bg-emerald-500/20 text-emerald-300 border-emerald-500/40",
    pending:   "bg-amber-500/20 text-amber-300 border-amber-500/40",
    mock:      "bg-purple-500/20 text-purple-300 border-purple-500/40",
    jailcourt: "bg-teal-500/20 text-teal-300 border-teal-500/40",
    default:   "bg-slate-700/50 text-slate-300 border-slate-600/40",
    success:   "bg-emerald-500/20 text-emerald-300 border-emerald-500/40",
    warn:      "bg-amber-500/20 text-amber-300 border-amber-500/40",
    info:      "bg-cyan-500/20 text-cyan-300 border-cyan-500/40",
    closed:    "bg-slate-700/30 text-slate-500 border-slate-700/40",
  };
  return (
    <span className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-semibold border ${v[variant] ?? v.default} ${className}`}>
      {pulse && <span className="w-1.5 h-1.5 rounded-full bg-current animate-pulse" />}
      {children}
    </span>
  );
};

const Btn = ({ variant = "primary", size = "md", onClick, children, className = "", disabled }) => {
  const base = "inline-flex items-center justify-center gap-2 font-semibold rounded-lg transition-all active:scale-95 disabled:opacity-40 disabled:cursor-not-allowed";
  const sz = { sm: "px-3 py-1.5 text-xs", md: "px-5 py-2.5 text-sm", lg: "px-7 py-3 text-base" };
  const v = {
    primary:   "bg-gradient-to-r from-cyan-600 to-cyan-500 hover:from-cyan-500 hover:to-cyan-400 text-white shadow-lg shadow-cyan-900/30",
    secondary: "bg-slate-800 hover:bg-slate-700 border border-slate-700 text-slate-200",
    danger:    "bg-red-600/20 hover:bg-red-600/30 border border-red-500/40 text-red-300",
    success:   "bg-emerald-600/20 hover:bg-emerald-600/30 border border-emerald-500/40 text-emerald-300",
    ghost:     "bg-transparent hover:bg-slate-800 text-slate-400 hover:text-slate-200",
  };
  return (
    <button disabled={disabled} onClick={onClick} className={`${base} ${sz[size]} ${v[variant]} ${className}`}>
      {children}
    </button>
  );
};

const Input = ({ label, ...props }) => (
  <div>
    {label && <label className="block text-xs text-slate-500 mb-1">{label}</label>}
    <input className="w-full bg-slate-800 border border-slate-700 rounded-lg px-4 py-2.5 text-white text-sm placeholder-slate-600 focus:border-cyan-500 focus:outline-none focus:ring-1 focus:ring-cyan-500/30 transition-colors" {...props} />
  </div>
);

const Select = ({ label, options, ...props }) => (
  <div>
    {label && <label className="block text-xs text-slate-500 mb-1">{label}</label>}
    <select className="w-full bg-slate-800 border border-slate-700 rounded-lg px-4 py-2.5 text-white text-sm focus:border-cyan-500 focus:outline-none transition-colors" {...props}>
      {options.map(o => <option key={o.value ?? o} value={o.value ?? o}>{o.label ?? o}</option>)}
    </select>
  </div>
);

const Card = ({ children, className = "", onClick }) => (
  <div onClick={onClick} className={`bg-slate-800/80 border border-slate-700/60 rounded-xl p-5 ${onClick ? "cursor-pointer hover:border-cyan-500/60 hover:shadow-lg hover:shadow-cyan-900/20" : ""} transition-all ${className}`}>
    {children}
  </div>
);

const SectionHeader = ({ title, subtitle, action }) => (
  <div className="flex items-start justify-between mb-6">
    <div>
      <h2 className="text-xl font-bold text-white">{title}</h2>
      {subtitle && <p className="text-sm text-slate-500 mt-0.5">{subtitle}</p>}
    </div>
    {action}
  </div>
);

const StatCard = ({ label, value, color = "text-cyan-400", sub }) => (
  <Card>
    <div className={`text-3xl font-extrabold mb-0.5 tabular-nums ${color}`}>{value}</div>
    <div className="text-sm text-slate-400">{label}</div>
    {sub && <div className="text-xs text-slate-600 mt-1">{sub}</div>}
  </Card>
);

// ─── Modal Shell ─────────────────────────────────────────────────────────────
const Modal = ({ title, onClose, children, wide }) => (
  <div className="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center z-50 p-4" onClick={onClose}>
    <div
      onClick={e => e.stopPropagation()}
      className={`bg-slate-900 border border-slate-700 rounded-2xl shadow-2xl flex flex-col max-h-[90vh] w-full ${wide ? "max-w-4xl" : "max-w-lg"}`}
    >
      <div className="flex items-center justify-between px-6 py-4 border-b border-slate-800 shrink-0">
        <h3 className="text-lg font-bold">{title}</h3>
        <button onClick={onClose} className="text-slate-500 hover:text-white transition-colors text-xl leading-none">✕</button>
      </div>
      <div className="overflow-y-auto flex-1 px-6 py-5">{children}</div>
    </div>
  </div>
);

// ─── Live Session Panel ───────────────────────────────────────────────────────
const LiveSessionPanel = ({ session, elapsed, recording, setRecording, onClose }) => {
  const [tab, setTab] = useState("video");
  const transcriptLines = [
    "HON. MARTINEZ: This court is now in session for the arraignment of State v. Dalton.",
    "HON. MARTINEZ: Mr. Dalton, you are charged under NC Gen. Stat. § 14-39. How do you plead?",
    "DEF. DALTON: Not guilty, Your Honor.",
    "ATT. JOHNSON: Defense requests bail be set at $25,000, Your Honor.",
    "ATT. RIVERA: The State objects. Defendant is a flight risk.",
    "HON. MARTINEZ: Bail is set at $50,000 with electronic monitoring.",
  ];

  return (
    <Modal title={`🔴 LIVE — ${session.title}`} onClose={onClose} wide>
      <div className="grid grid-cols-2 gap-4 mb-4">
        <div className="space-y-1 text-sm">
          <p><span className="text-slate-500">Case:</span> <span className="text-cyan-400">{session.caseNumber}</span></p>
          <p><span className="text-slate-500">Court:</span> {session.circuit} • Courtroom {session.courtroom}</p>
          <p><span className="text-slate-500">Judge:</span> {session.judge} &nbsp;|&nbsp; <span className="text-slate-500">Clerk:</span> {session.clerk}</p>
        </div>
        <div className="space-y-1 text-sm text-right">
          <p className="text-green-400 font-mono text-xl font-bold">{fmtElapsed(elapsed)}</p>
          <p className="text-slate-500 text-xs">Session elapsed</p>
          <div className="flex gap-2 justify-end flex-wrap">
            <Badge variant="live" pulse>LIVE</Badge>
            {recording && <Badge variant="recording" pulse>🎥 REC</Badge>}
            <Badge variant="verified">⛓ Chain Protected</Badge>
          </div>
        </div>
      </div>

      {/* Tab Bar */}
      <div className="flex gap-1 mb-4 bg-slate-800/50 p-1 rounded-lg">
        {["video","transcript","participants","evidence"].map(t => (
          <button key={t} onClick={() => setTab(t)}
            className={`flex-1 py-1.5 text-xs font-semibold rounded capitalize transition-colors ${tab === t ? "bg-slate-700 text-white" : "text-slate-500 hover:text-slate-300"}`}>
            {t}
          </button>
        ))}
      </div>

      {tab === "video" && (
        <div>
          <div className="bg-slate-950 rounded-xl aspect-video flex flex-col items-center justify-center border border-slate-800 mb-4 relative overflow-hidden">
            <div className="absolute inset-0 bg-gradient-to-br from-slate-900 to-slate-950" />
            <div className="relative text-center">
              <div className="text-6xl mb-3 opacity-40">🎥</div>
              <p className="text-slate-400 text-sm font-medium">Courtroom 4B — Live Stream</p>
              <p className="text-slate-600 text-xs mt-1">Bench, parties, and observers visible on connection</p>
            </div>
            {recording && (
              <div className="absolute top-3 right-3 flex items-center gap-2 bg-red-600/90 px-3 py-1 rounded-full text-xs font-bold">
                <span className="w-2 h-2 rounded-full bg-white animate-pulse" /> REC
              </div>
            )}
            <div className="absolute bottom-3 left-3 text-xs font-mono text-green-400 opacity-70">
              LEGyC: {session.caseNumber}/session-01 • Segment-04
            </div>
          </div>
          <div className="flex gap-3">
            <Btn variant="primary" className="flex-1" onClick={() => alert("Joining courtroom video…")}>▶ Join Courtroom</Btn>
            <Btn variant={recording ? "danger" : "success"} onClick={() => setRecording(r => !r)}>
              {recording ? "⏸ Pause Recording" : "⏺ Start Recording"}
            </Btn>
            <Btn variant="secondary" onClick={() => alert("Opening audit trail…")}>📋 Audit Trail</Btn>
          </div>
        </div>
      )}

      {tab === "transcript" && (
        <div className="space-y-3">
          <div className="flex items-center gap-2 mb-3">
            <Badge variant="warn" pulse>Draft Live</Badge>
            <span className="text-xs text-slate-500">AI-assisted — verify against recording</span>
          </div>
          {transcriptLines.map((line, i) => (
            <div key={i} className="bg-slate-800/50 rounded-lg p-3 text-sm text-slate-300 font-mono border border-slate-700/40">{line}</div>
          ))}
          <Btn variant="secondary" size="sm" onClick={() => alert("Downloading transcript draft…")}>⬇ Download Draft</Btn>
        </div>
      )}

      {tab === "participants" && (
        <div className="space-y-2">
          {session.participants.map((p, i) => (
            <div key={i} className="flex items-center justify-between bg-slate-800/50 rounded-lg px-4 py-3 border border-slate-700/40">
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 rounded-full bg-gradient-to-br from-cyan-600 to-slate-700 flex items-center justify-center text-xs font-bold">{p[0]}</div>
                <span className="text-sm text-slate-200">{p}</span>
              </div>
              <div className="flex gap-2">
                <Badge variant="verified" >✓ Verified</Badge>
                <Badge variant="live" pulse>Online</Badge>
              </div>
            </div>
          ))}
        </div>
      )}

      {tab === "evidence" && (
        <div>
          <p className="text-sm text-slate-400 mb-3">Evidence admitted in {session.caseNumber}</p>
          {initialEvidence.filter(e => e.caseNumber === session.caseNumber).map(e => (
            <div key={e.id} className="flex items-center gap-3 bg-slate-800/50 rounded-lg px-4 py-3 border border-slate-700/40 mb-2">
              <span className="text-2xl">{typeIcon(e.type)}</span>
              <div className="flex-1">
                <p className="text-sm font-medium text-slate-200">{e.fileName}</p>
                <p className="text-xs font-mono text-cyan-400 mt-0.5">{e.hash.slice(0, 24)}…</p>
              </div>
              <Badge variant={e.status === "verified" ? "verified" : "pending"}>
                {e.status === "verified" ? "✓ Verified" : "⏳ Pending"}
              </Badge>
            </div>
          ))}
        </div>
      )}
    </Modal>
  );
};

// ─── Schedule Modal ───────────────────────────────────────────────────────────
const ScheduleModal = ({ onClose, onSave }) => {
  const [form, setForm] = useState({ title: "", caseNumber: "", type: "Arraignment", date: "", time: "", judge: "Hon. Martinez", mode: "Live", courtroom: "4B" });
  const up = (k, v) => setForm(f => ({ ...f, [k]: v }));
  return (
    <Modal title="Schedule Hearing" onClose={onClose}>
      <div className="space-y-4">
        <div className="grid grid-cols-2 gap-3">
          <Input label="Case Title" placeholder="State v. …" value={form.title} onChange={e => up("title", e.target.value)} />
          <Input label="Case Number" placeholder="CR-24-XXXX" value={form.caseNumber} onChange={e => up("caseNumber", e.target.value)} />
        </div>
        <div className="grid grid-cols-2 gap-3">
          <Select label="Hearing Type" value={form.type} onChange={e => up("type", e.target.value)}
            options={["Arraignment","Bond Review","Motion Hearing","Plea Hearing","Trial","Civil Motion","Status Conference","Sentencing"]} />
          <Select label="Mode" value={form.mode} onChange={e => up("mode", e.target.value)} options={["Live","Remote","JailCourt","Mock"]} />
        </div>
        <div className="grid grid-cols-2 gap-3">
          <Input label="Date" type="date" value={form.date} onChange={e => up("date", e.target.value)} />
          <Input label="Time" type="time" value={form.time} onChange={e => up("time", e.target.value)} />
        </div>
        <div className="grid grid-cols-2 gap-3">
          <Select label="Judge" value={form.judge} onChange={e => up("judge", e.target.value)}
            options={["Hon. Martinez","Hon. Chen","Hon. Johnson","Hon. Williams"]} />
          <Input label="Courtroom" placeholder="4B" value={form.courtroom} onChange={e => up("courtroom", e.target.value)} />
        </div>
        <div className="flex gap-3 pt-2">
          <Btn variant="primary" className="flex-1" onClick={() => { onSave(form); onClose(); }}>Create Hearing</Btn>
          <Btn variant="secondary" onClick={onClose}>Cancel</Btn>
        </div>
      </div>
    </Modal>
  );
};

// ─── New Case Modal ───────────────────────────────────────────────────────────
const NewCaseModal = ({ onClose, onSave }) => {
  const [form, setForm] = useState({ title: "", caseNumber: "", type: "Criminal", judge: "Hon. Martinez", circuit: "3rd Judicial Circuit" });
  const up = (k, v) => setForm(f => ({ ...f, [k]: v }));
  return (
    <Modal title="Create New Case" onClose={onClose}>
      <div className="space-y-4">
        <Input label="Case Title" placeholder="Plaintiff v. Defendant" value={form.title} onChange={e => up("title", e.target.value)} />
        <Input label="Case Number" placeholder="CR-24-XXXX" value={form.caseNumber} onChange={e => up("caseNumber", e.target.value)} />
        <div className="grid grid-cols-2 gap-3">
          <Select label="Case Type" value={form.type} onChange={e => up("type", e.target.value)} options={["Criminal","Civil","Family","Probate","Juvenile"]} />
          <Select label="Circuit" value={form.circuit} onChange={e => up("circuit", e.target.value)} options={["3rd Judicial Circuit","Municipal Court","Family Court","Superior Court"]} />
        </div>
        <Select label="Assigned Judge" value={form.judge} onChange={e => up("judge", e.target.value)}
          options={["Hon. Martinez","Hon. Chen","Hon. Johnson","Hon. Williams"]} />
        <div className="flex gap-3 pt-2">
          <Btn variant="primary" className="flex-1" onClick={() => { onSave(form); onClose(); }}>Create Case</Btn>
          <Btn variant="secondary" onClick={onClose}>Cancel</Btn>
        </div>
      </div>
    </Modal>
  );
};

// ─── Upload Evidence Modal ────────────────────────────────────────────────────
const UploadEvidenceModal = ({ cases: caseList, onClose, onSave }) => {
  const [form, setForm] = useState({ caseId: "c1", fileName: "", uploadedBy: "", type: "document" });
  const up = (k, v) => setForm(f => ({ ...f, [k]: v }));
  return (
    <Modal title="Upload Evidence" onClose={onClose}>
      <div className="space-y-4">
        <Select label="Case" value={form.caseId} onChange={e => up("caseId", e.target.value)}
          options={caseList.map(c => ({ value: c.id, label: `${c.caseNumber} — ${c.title}` }))} />
        <Input label="File Name" placeholder="evidence_001.mp4" value={form.fileName} onChange={e => up("fileName", e.target.value)} />
        <div className="grid grid-cols-2 gap-3">
          <Select label="Type" value={form.type} onChange={e => up("type", e.target.value)} options={["document","video","image","audio"]} />
          <Input label="Uploaded By" placeholder="Officer Name" value={form.uploadedBy} onChange={e => up("uploadedBy", e.target.value)} />
        </div>
        <div className="bg-slate-800/50 border-2 border-dashed border-slate-700 rounded-xl p-8 text-center">
          <div className="text-4xl mb-2">📎</div>
          <p className="text-sm text-slate-400">Drag & drop or click to select file</p>
          <p className="text-xs text-slate-600 mt-1">SHA-256 hash generated automatically</p>
        </div>
        <div className="flex gap-3 pt-2">
          <Btn variant="primary" className="flex-1" onClick={() => { onSave(form); onClose(); }}>Upload & Hash</Btn>
          <Btn variant="secondary" onClick={onClose}>Cancel</Btn>
        </div>
      </div>
    </Modal>
  );
};

// ─── Session Card ─────────────────────────────────────────────────────────────
const SessionCard = ({ session, elapsed, onClick }) => (
  <Card onClick={onClick}>
    <div className="flex justify-between items-start mb-3">
      <div className="flex-1 min-w-0">
        <div className="flex gap-2 flex-wrap mb-2">
          {session.status === "live"      && <Badge variant="live"      pulse>🔴 LIVE</Badge>}
          {session.status === "scheduled" && <Badge variant="scheduled">⏰ Scheduled</Badge>}
          {session.status === "mock"      && <Badge variant="mock">🎭 Mock</Badge>}
          {session.recording              && <Badge variant="recording" pulse>🎥 REC</Badge>}
          {session.remote                 && <Badge variant="remote">🌐 Remote</Badge>}
          {session.jailcourt              && <Badge variant="jailcourt">🏛 JailCourt</Badge>}
        </div>
        <h4 className="text-base font-bold text-white truncate">{session.title}</h4>
        <p className="text-xs text-slate-500 mt-0.5">{session.caseNumber} · {session.circuit}</p>
      </div>
      <div className="text-right ml-3 shrink-0">
        <p className="text-xs text-slate-500">{session.time} · {session.type}</p>
        {session.status === "live" && (
          <p className="text-xs text-green-400 font-mono mt-1">⏱ {fmtElapsed(elapsed)}</p>
        )}
      </div>
    </div>
    <div className="flex gap-4 pt-3 border-t border-slate-700/40 text-sm">
      <div>
        <p className="text-xs text-slate-600">Judge</p>
        <p className="text-slate-300 text-sm">{session.judge}</p>
      </div>
      {session.clerk && session.clerk !== "—" && (
        <div>
          <p className="text-xs text-slate-600">Clerk</p>
          <p className="text-slate-300 text-sm">{session.clerk}</p>
        </div>
      )}
      {session.mode && (
        <div className="ml-auto">
          <p className="text-xs text-slate-600">Mode</p>
          <p className="text-slate-300 text-sm">{session.mode}</p>
        </div>
      )}
    </div>
  </Card>
);

// ─── Views ────────────────────────────────────────────────────────────────────
const DashboardView = ({ sessions, cases, elapsed, onOpenSession, onSchedule }) => {
  const [circuitFilter, setCircuitFilter] = useState("all");
  const [judgeFilter, setJudgeFilter]     = useState("all");
  const [modeFilter, setModeFilter]       = useState("All");

  const filtered = sessions.filter(s =>
    (circuitFilter === "all" || s.circuit === circuitFilter) &&
    (judgeFilter   === "all" || s.judge   === judgeFilter) &&
    (modeFilter    === "All" || (modeFilter === "Live" && !s.remote && !s.jailcourt && !s.mock) ||
      (modeFilter === "Remote" && s.remote) ||
      (modeFilter === "JailCourt" && s.jailcourt) ||
      (modeFilter === "Mock" && s.mock))
  );

  return (
    <div>
      <SectionHeader
        title="Court Day Overview"
        subtitle="Bench: 3rd Judicial Circuit · Morning Docket"
        action={<Btn onClick={onSchedule}>+ Schedule Hearing</Btn>}
      />

      {/* Stats */}
      <div className="grid grid-cols-4 gap-4 mb-6">
        <StatCard label="Total Today"  value={sessions.length} color="text-cyan-400" />
        <StatCard label="Live Now"     value={sessions.filter(s => s.status === "live").length}      color="text-green-400" />
        <StatCard label="Scheduled"    value={sessions.filter(s => s.status === "scheduled").length} color="text-blue-400" />
        <StatCard label="Active Cases" value={cases.filter(c => c.status === "active").length}       color="text-amber-400" />
      </div>

      {/* Filters */}
      <div className="flex gap-3 mb-5 flex-wrap">
        <select className="bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm text-slate-200"
          value={circuitFilter} onChange={e => setCircuitFilter(e.target.value)}>
          <option value="all">All Circuits</option>
          <option value="3rd Judicial Circuit">3rd Judicial Circuit</option>
          <option value="Family Court">Family Court</option>
        </select>
        <select className="bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm text-slate-200"
          value={judgeFilter} onChange={e => setJudgeFilter(e.target.value)}>
          <option value="all">All Judges</option>
          <option value="Hon. Martinez">Hon. Martinez</option>
          <option value="Hon. Chen">Hon. Chen</option>
        </select>
        <div className="flex gap-1 bg-slate-800 border border-slate-700 rounded-lg p-1">
          {["All","Live","Remote","JailCourt","Mock"].map(m => (
            <button key={m} onClick={() => setModeFilter(m)}
              className={`px-3 py-1 rounded text-xs font-semibold transition-colors ${modeFilter === m ? "bg-slate-600 text-white" : "text-slate-500 hover:text-slate-300"}`}>{m}</button>
          ))}
        </div>
      </div>

      {/* Session List */}
      <div className="space-y-3">
        {filtered.map(s => (
          <SessionCard key={s.id} session={s} elapsed={elapsed} onClick={() => onOpenSession(s)} />
        ))}
        {filtered.length === 0 && (
          <div className="text-center py-12 text-slate-600">No sessions match current filters.</div>
        )}
      </div>
    </div>
  );
};

const CasesView = ({ cases, onNewCase, onViewCase }) => {
  const [search, setSearch] = useState("");
  const [typeFilter, setTypeFilter] = useState("All");
  const filtered = cases.filter(c =>
    (c.title.toLowerCase().includes(search.toLowerCase()) || c.caseNumber.toLowerCase().includes(search.toLowerCase())) &&
    (typeFilter === "All" || c.type === typeFilter)
  );
  return (
    <div>
      <SectionHeader title="Cases & Dockets" subtitle="Manage court cases and filings"
        action={<Btn onClick={onNewCase}>+ New Case</Btn>} />
      <div className="flex gap-3 mb-5">
        <input className="flex-1 bg-slate-800 border border-slate-700 rounded-lg px-4 py-2.5 text-sm text-white placeholder-slate-600 focus:border-cyan-500 focus:outline-none"
          placeholder="Search case number or title…" value={search} onChange={e => setSearch(e.target.value)} />
        <select className="bg-slate-800 border border-slate-700 rounded-lg px-3 py-2.5 text-sm text-slate-200"
          value={typeFilter} onChange={e => setTypeFilter(e.target.value)}>
          {["All","Criminal","Civil","Family","Probate"].map(t => <option key={t}>{t}</option>)}
        </select>
      </div>
      <div className="space-y-3">
        {filtered.map(c => (
          <Card key={c.id} onClick={() => onViewCase(c)}>
            <div className="flex justify-between items-start">
              <div>
                <h4 className="font-bold text-white">{c.title}</h4>
                <p className="text-xs text-slate-500 mt-0.5">{c.caseNumber} · {c.type} · Filed {c.filed}</p>
                <p className="text-xs text-slate-500 mt-0.5">{c.judge} · {c.circuit}</p>
              </div>
              <div className="flex flex-col items-end gap-2">
                <Badge variant={c.status === "active" ? "verified" : "closed"}>{c.status}</Badge>
                <span className="text-xs text-slate-600">{c.docket} docket entries</span>
              </div>
            </div>
            <div className="flex gap-2 mt-4" onClick={e => e.stopPropagation()}>
              <Btn size="sm" onClick={() => onViewCase(c)}>View Details</Btn>
              <Btn size="sm" variant="secondary">Schedule Hearing</Btn>
              <Btn size="sm" variant="secondary">CM/ECF Filing</Btn>
            </div>
          </Card>
        ))}
      </div>
    </div>
  );
};

const HearingsView = ({ sessions, elapsed, onOpenSession, onSchedule }) => (
  <div>
    <SectionHeader title="Hearings & Calendar" subtitle="All scheduled and past hearings"
      action={<Btn onClick={onSchedule}>+ Schedule Hearing</Btn>} />
    <div className="grid grid-cols-3 gap-4 mb-6">
      {["Today, Apr 10","Tomorrow, Apr 11","Apr 14–18"].map((d, i) => (
        <Card key={i} className={i === 0 ? "border-cyan-500/40" : ""}>
          <p className="text-xs text-slate-500 mb-1">{d}</p>
          <p className="text-2xl font-bold text-white">{[sessions.length, 2, 7][i]}</p>
          <p className="text-xs text-slate-600">hearings</p>
        </Card>
      ))}
    </div>
    <div className="space-y-3">
      {sessions.map(s => (
        <SessionCard key={s.id} session={s} elapsed={elapsed} onClick={() => onOpenSession(s)} />
      ))}
    </div>
  </div>
);

const JailCourtView = ({ sessions, elapsed, onOpenSession }) => {
  const jailSessions = sessions.filter(s => s.jailcourt);
  return (
    <div>
      <SectionHeader title="JailCourt Management" subtitle="Remote appearances from correctional facilities" />
      <div className="bg-teal-500/10 border border-teal-500/20 rounded-xl p-5 mb-6">
        <div className="flex items-center gap-3 mb-2">
          <span className="text-2xl">🏛</span>
          <div>
            <h3 className="font-bold text-teal-300">JailCourt Active</h3>
            <p className="text-xs text-slate-400">Biometric verification required before session entry. All sessions are encrypted and chain-logged.</p>
          </div>
        </div>
        <div className="grid grid-cols-3 gap-3 mt-4">
          <div className="bg-teal-900/30 rounded-lg p-3 text-center">
            <p className="text-xl font-bold text-teal-300">{jailSessions.length}</p>
            <p className="text-xs text-slate-500">Scheduled</p>
          </div>
          <div className="bg-amber-900/20 rounded-lg p-3 text-center">
            <p className="text-xl font-bold text-amber-300">1</p>
            <p className="text-xs text-slate-500">Bio Pending</p>
          </div>
          <div className="bg-emerald-900/20 rounded-lg p-3 text-center">
            <p className="text-xl font-bold text-emerald-300">0</p>
            <p className="text-xs text-slate-500">Active Now</p>
          </div>
        </div>
      </div>

      {jailSessions.length === 0 ? (
        <div className="text-center py-10 text-slate-600">No JailCourt sessions scheduled.</div>
      ) : (
        <div className="space-y-3">
          {jailSessions.map(s => (
            <SessionCard key={s.id} session={s} elapsed={elapsed} onClick={() => onOpenSession(s)} />
          ))}
        </div>
      )}

      {/* Biometric Queue */}
      <div className="mt-6">
        <h3 className="font-semibold text-slate-300 mb-3">Biometric Verification Queue</h3>
        <Card>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <span className="text-2xl">🔐</span>
              <div>
                <p className="font-medium">Jordan — CR-24-1122</p>
                <p className="text-xs text-slate-500">JailCourt · 09:45 · County Detention Center</p>
              </div>
            </div>
            <div className="flex gap-2">
              <Badge variant="pending" pulse>Pending</Badge>
              <Btn size="sm" onClick={() => alert("Initiating FacePrint biometric check…")}>🔐 Verify Now</Btn>
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
};

const EvidenceView = ({ evidence, cases: caseList, onUpload }) => {
  const [selected, setSelected] = useState(null);
  const [caseFilter, setCaseFilter] = useState("all");

  const filtered = evidence.filter(e => caseFilter === "all" || e.caseId === caseFilter);

  return (
    <div>
      <SectionHeader title="Evidence Vault" subtitle="Forensic evidence with blockchain chain-of-custody"
        action={<Btn onClick={onUpload}>+ Upload Evidence</Btn>} />
      <div className="flex gap-3 mb-5">
        <select className="bg-slate-800 border border-slate-700 rounded-lg px-3 py-2.5 text-sm text-slate-200"
          value={caseFilter} onChange={e => setCaseFilter(e.target.value)}>
          <option value="all">All Cases</option>
          {caseList.map(c => <option key={c.id} value={c.id}>{c.caseNumber}</option>)}
        </select>
        <Badge variant="verified" className="self-center">⛓ Chain Verified</Badge>
      </div>
      <div className="space-y-3">
        {filtered.map(e => (
          <Card key={e.id} onClick={() => setSelected(e)}>
            <div className="flex items-start gap-4">
              <span className="text-4xl">{typeIcon(e.type)}</span>
              <div className="flex-1 min-w-0">
                <div className="flex justify-between items-start mb-1">
                  <div>
                    <h4 className="font-semibold text-white">{e.fileName}</h4>
                    <p className="text-xs text-slate-500">{e.uploadedBy} · {e.uploadDate} · {e.size} · {e.caseNumber}</p>
                  </div>
                  <Badge variant={e.status === "verified" ? "verified" : "pending"}>
                    {e.status === "verified" ? "✓ Verified" : "⏳ Pending"}
                  </Badge>
                </div>
                <div className="bg-slate-900 rounded-lg p-2.5 mt-2">
                  <p className="text-xs text-slate-600 mb-1">SHA-256</p>
                  <p className="text-xs font-mono text-cyan-400 break-all">{e.hash}</p>
                </div>
                <div className="flex gap-2 mt-3" onClick={ev => ev.stopPropagation()}>
                  <Btn size="sm" onClick={() => alert(`Downloading ${e.fileName}…`)}>⬇ Download</Btn>
                  <Btn size="sm" variant="secondary" onClick={() => alert("Verifying chain…")}>⛓ Verify Chain</Btn>
                  <Btn size="sm" variant="secondary" onClick={() => setSelected(e)}>Details</Btn>
                </div>
              </div>
            </div>
          </Card>
        ))}
      </div>

      {/* Evidence Detail Modal */}
      {selected && (
        <Modal title={`Evidence: ${selected.fileName}`} onClose={() => setSelected(null)}>
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-3 text-sm">
              <div><p className="text-xs text-slate-500">Case</p><p>{selected.caseNumber}</p></div>
              <div><p className="text-xs text-slate-500">Uploaded By</p><p>{selected.uploadedBy}</p></div>
              <div><p className="text-xs text-slate-500">Date</p><p>{selected.uploadDate}</p></div>
              <div><p className="text-xs text-slate-500">Size</p><p>{selected.size}</p></div>
              <div><p className="text-xs text-slate-500">Type</p><p className="capitalize">{selected.type}</p></div>
              <div><p className="text-xs text-slate-500">Status</p>
                <Badge variant={selected.status === "verified" ? "verified" : "pending"}>{selected.status}</Badge>
              </div>
            </div>
            <div className="bg-slate-800 rounded-xl p-4">
              <p className="text-xs text-slate-500 mb-1">SHA-256 Hash</p>
              <p className="text-xs font-mono text-cyan-400 break-all">{selected.hash}</p>
            </div>
            <div className="bg-emerald-900/20 border border-emerald-500/20 rounded-xl p-4">
              <p className="text-xs font-bold text-emerald-400 mb-1">⛓ LEGyC Chain Status</p>
              <p className="text-xs text-slate-400">Block confirmed · Immutable · Court-admissible</p>
              <p className="text-xs font-mono text-slate-500 mt-1">Node: VC-ND-07 · Segment: {selected.id}</p>
            </div>
            <div className="flex gap-3">
              <Btn variant="primary" className="flex-1" onClick={() => alert("Downloading…")}>⬇ Download</Btn>
              <Btn variant="secondary" onClick={() => setSelected(null)}>Close</Btn>
            </div>
          </div>
        </Modal>
      )}
    </div>
  );
};

const MockTrialView = () => {
  const [scenario, setScenario] = useState("arraignment");
  const [running, setRunning] = useState(false);
  const [log, setLog] = useState([]);

  const scenarios = [
    { id: "arraignment", label: "Arraignment Procedure", difficulty: "Beginner" },
    { id: "bond",        label: "Bond Hearing",          difficulty: "Intermediate" },
    { id: "motion",      label: "Motion to Suppress",    difficulty: "Advanced" },
    { id: "trial",       label: "Full Criminal Trial",   difficulty: "Expert" },
  ];

  const startMock = () => {
    setRunning(true);
    setLog(["🎭 Mock session initialized…", "📋 Loading scenario: " + scenarios.find(s => s.id === scenario)?.label, "🤖 AI Judge ready — waiting for participants…"]);
  };

  return (
    <div>
      <SectionHeader title="Mock Trial Lab" subtitle="AI-powered courtroom training simulations" />
      <div className="grid grid-cols-2 gap-4 mb-6">
        {scenarios.map(s => (
          <Card key={s.id} onClick={() => setScenario(s.id)}
            className={scenario === s.id ? "border-purple-500/60 bg-purple-900/10" : ""}>
            <div className="flex justify-between items-start">
              <div>
                <h4 className="font-semibold">{s.label}</h4>
                <p className="text-xs text-slate-500 mt-1">Difficulty: {s.difficulty}</p>
              </div>
              {scenario === s.id && <Badge variant="mock">Selected</Badge>}
            </div>
          </Card>
        ))}
      </div>
      <Card>
        <div className="flex justify-between items-center mb-4">
          <h3 className="font-semibold">Session Console</h3>
          <div className="flex gap-2">
            {!running ? (
              <Btn variant="primary" onClick={startMock}>▶ Start Mock Session</Btn>
            ) : (
              <Btn variant="danger" onClick={() => { setRunning(false); setLog(l => [...l, "Session ended."]); }}>⏹ End Session</Btn>
            )}
          </div>
        </div>
        <div className="bg-slate-950 rounded-xl p-4 min-h-40 font-mono text-xs space-y-1">
          {log.length === 0 && <p className="text-slate-700">Select a scenario and press Start…</p>}
          {log.map((l, i) => <p key={i} className="text-green-400">{l}</p>)}
          {running && <p className="text-cyan-400 animate-pulse">▋</p>}
        </div>
      </Card>
    </div>
  );
};

const AISyncView = () => (
  <div>
    <SectionHeader title="AI / GTP Sync" subtitle="Constellation25 agent integration and GTP state" />
    <div className="grid grid-cols-3 gap-4 mb-6">
      {[
        { label: "Pathos Engine",   status: "Online",   color: "text-green-400",  port: 3100 },
        { label: "DeployAgent",     status: "Synced",   color: "text-cyan-400",   port: 8001 },
        { label: "TotalRecall",     status: "Streaming",color: "text-blue-400",   port: 8005 },
      ].map((a, i) => (
        <Card key={i}>
          <div className="flex items-center gap-2 mb-2">
            <span className={`w-2 h-2 rounded-full bg-current ${a.color} animate-pulse`} />
            <p className="text-xs text-slate-500">{a.status}</p>
          </div>
          <p className="font-bold">{a.label}</p>
          <p className="text-xs text-slate-600 mt-1">:{a.port}</p>
        </Card>
      ))}
    </div>
    <Card>
      <h3 className="font-semibold mb-3">LEGyC Chain Status</h3>
      <div className="space-y-2 text-sm">
        {[
          { label: "Node ID",       val: "VC-ND-07" },
          { label: "Chain Status",  val: "Canonical · Synchronized" },
          { label: "Last Hash",     val: "0x92a3df0c1e5b7f4a..." },
          { label: "Updated",       val: "3s ago" },
        ].map(r => (
          <div key={r.label} className="flex justify-between border-b border-slate-800 pb-2">
            <span className="text-slate-500">{r.label}</span>
            <span className="text-cyan-400 font-mono text-xs">{r.val}</span>
          </div>
        ))}
      </div>
    </Card>
  </div>
);

const AuditView = ({ auditLog }) => (
  <div>
    <SectionHeader title="TotalRecall / LEGyC" subtitle="Immutable chain-of-custody audit trail" />
    <div className="flex gap-2 mb-5">
      <Badge variant="success" pulse>Streaming</Badge>
      <Badge variant="verified">⛓ Canonical</Badge>
      <Badge variant="info">Node VC-ND-07</Badge>
    </div>
    <div className="space-y-2">
      {auditLog.map(entry => (
        <Card key={entry.id} className="!py-3">
          <div className="flex items-start gap-4">
            <span className="text-xs font-mono text-slate-600 mt-0.5 shrink-0">{entry.ts}</span>
            <div className="flex-1">
              <p className="text-sm font-semibold text-white">{entry.event}</p>
              <p className="text-xs text-slate-500">{entry.actor} · {entry.case}</p>
            </div>
            <p className="text-xs font-mono text-cyan-400 shrink-0">{entry.hash}</p>
          </div>
        </Card>
      ))}
    </div>
  </div>
);

const NotificationsView = ({ notifications, setNotifications }) => {
  const markAll = () => setNotifications(n => n.map(x => ({ ...x, read: true })));
  return (
    <div>
      <SectionHeader title="Notifications" subtitle="System alerts, filings, and SMS status"
        action={<Btn variant="secondary" size="sm" onClick={markAll}>Mark All Read</Btn>} />
      <div className="space-y-2">
        {notifications.map(n => (
          <Card key={n.id} className={`!py-3 ${!n.read ? "border-cyan-700/40" : ""}`}
            onClick={() => setNotifications(ns => ns.map(x => x.id === n.id ? { ...x, read: true } : x))}>
            <div className="flex items-center gap-3">
              {!n.read && <span className="w-2 h-2 rounded-full bg-cyan-400 shrink-0" />}
              <div className="flex-1">
                <p className="text-sm text-slate-200">{n.message}</p>
                <p className="text-xs text-slate-600 mt-0.5">{n.time}</p>
              </div>
              <Badge variant={n.level}>{n.level}</Badge>
            </div>
          </Card>
        ))}
      </div>
    </div>
  );
};

const CaseDetailModal = ({ c, onClose }) => (
  <Modal title={c.title} onClose={onClose}>
    <div className="space-y-4">
      <div className="grid grid-cols-2 gap-3 text-sm">
        <div><p className="text-xs text-slate-500">Case Number</p><p className="text-cyan-400 font-mono">{c.caseNumber}</p></div>
        <div><p className="text-xs text-slate-500">Type</p><p>{c.type}</p></div>
        <div><p className="text-xs text-slate-500">Filed</p><p>{c.filed}</p></div>
        <div><p className="text-xs text-slate-500">Status</p><Badge variant={c.status === "active" ? "verified" : "closed"}>{c.status}</Badge></div>
        <div><p className="text-xs text-slate-500">Judge</p><p>{c.judge}</p></div>
        <div><p className="text-xs text-slate-500">Circuit</p><p>{c.circuit}</p></div>
        <div><p className="text-xs text-slate-500">Docket Entries</p><p>{c.docket}</p></div>
      </div>
      <div className="bg-slate-800/50 rounded-xl p-4">
        <p className="text-xs text-slate-500 mb-2">Quick Actions</p>
        <div className="flex gap-2 flex-wrap">
          <Btn size="sm" onClick={() => alert("Opening docket…")}>📋 View Docket</Btn>
          <Btn size="sm" variant="secondary" onClick={() => alert("CM/ECF filing…")}>📎 CM/ECF Filing</Btn>
          <Btn size="sm" variant="secondary" onClick={() => alert("Scheduling hearing…")}>📅 Schedule Hearing</Btn>
          <Btn size="sm" variant="secondary" onClick={() => alert("Opening evidence vault…")}>🔐 Evidence</Btn>
        </div>
      </div>
      <Btn variant="secondary" onClick={onClose} className="w-full">Close</Btn>
    </div>
  </Modal>
);

// ─── Right Panel ──────────────────────────────────────────────────────────────
const RightPanel = ({ notifications, liveSession, elapsed, recording }) => {
  const unread = notifications.filter(n => !n.read).length;
  return (
    <div className="w-72 bg-slate-900 border-l border-slate-800 flex flex-col overflow-y-auto">
      <div className="p-5 border-b border-slate-800">
        <p className="text-xs text-slate-500 mb-0.5">Live Session Context</p>
        <p className="font-bold text-white">Hon. Alex Martinez</p>
        <p className="text-xs text-slate-500">Judge · Courtroom 4B</p>
        <div className="mt-3"><Badge variant="verified">✓ All Systems Green</Badge></div>
      </div>

      <div className="flex-1 p-5 space-y-5">
        {/* Active Session */}
        {liveSession && (
          <div>
            <p className="text-xs font-semibold text-slate-500 mb-2 uppercase tracking-wider">Active Session</p>
            <div className="bg-slate-800/80 rounded-xl p-3 space-y-1.5">
              <div className="flex justify-between items-center">
                <p className="text-xs text-slate-400">Chain Protected</p>
                <span className="w-2 h-2 rounded-full bg-green-400 animate-pulse" />
              </div>
              <p className="text-xs font-mono text-green-400">✓ Recording & LEGyC Active</p>
              <p className="text-xs font-mono text-cyan-400">{fmtElapsed(elapsed)}</p>
              {liveSession.nextMatter && (
                <div className="pt-1 border-t border-slate-700">
                  <p className="text-xs text-slate-500">Next matter</p>
                  <p className="text-xs text-slate-300">{liveSession.nextMatter}</p>
                </div>
              )}
            </div>
          </div>
        )}

        {/* TotalRecall */}
        <div>
          <p className="text-xs font-semibold text-slate-500 mb-2 uppercase tracking-wider">TotalRecall</p>
          <div className="bg-emerald-900/20 border border-emerald-500/20 rounded-xl p-3">
            <div className="flex items-center gap-2 mb-1">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
              <p className="text-xs font-bold text-emerald-400">Streaming</p>
            </div>
            <p className="text-xs text-slate-500">Last event hash:</p>
            <p className="text-xs font-mono text-cyan-400 break-all mt-0.5">0x92a3...df0c</p>
            <p className="text-xs text-emerald-400 mt-1">Updated 3s ago</p>
          </div>
        </div>

        {/* LEGyC */}
        <div>
          <p className="text-xs font-semibold text-slate-500 mb-2 uppercase tracking-wider">LEGyC Chain</p>
          <div className="bg-cyan-900/20 border border-cyan-500/20 rounded-xl p-3">
            <div className="flex items-center justify-between mb-1">
              <p className="text-xs font-bold text-cyan-400">Canonical</p>
              <Badge variant="verified" className="text-[10px]">✓</Badge>
            </div>
            <p className="text-xs text-slate-500">Z-path</p>
            <p className="text-xs font-mono text-slate-400">/dalton/session-01/segment-04</p>
            <p className="text-xs text-slate-500 mt-1">Notarized</p>
          </div>
        </div>

        {/* CM/ECF */}
        <div>
          <p className="text-xs font-semibold text-slate-500 mb-2 uppercase tracking-wider">CM/ECF & Tyler</p>
          <div className="bg-slate-800/50 border border-slate-700/40 rounded-xl p-3">
            <p className="text-xs font-bold text-cyan-400 mb-1">Connected</p>
            <p className="text-xs text-slate-500">Last sync: 08:57 · 3 filings queued</p>
            <button className="text-xs text-cyan-400 hover:underline mt-2">View Queue →</button>
          </div>
        </div>

        {/* Biometric */}
        <div>
          <p className="text-xs font-semibold text-slate-500 mb-2 uppercase tracking-wider">Biometric Gateway</p>
          <div className="bg-amber-900/20 border border-amber-500/20 rounded-xl p-3">
            <p className="text-xs font-bold text-amber-400 mb-1">Pending: 1</p>
            <p className="text-xs text-slate-500">Jordan · JailCourt · 09:45</p>
            <button className="text-xs text-cyan-400 hover:underline mt-2">Next Verification →</button>
          </div>
        </div>

        {/* Notifications */}
        <div>
          <p className="text-xs font-semibold text-slate-500 mb-2 uppercase tracking-wider">Notifications</p>
          <div className="text-xs text-slate-400 space-y-1">
            <p>{unread} unread · {notifications.length} total</p>
            <p className="text-slate-600">+24 min SMS batch</p>
          </div>
        </div>
      </div>
    </div>
  );
};

// ─── App Root ─────────────────────────────────────────────────────────────────
export default function VideoCourts() {
  const [view, setView]                 = useState("dashboard");
  const [sessions, setSessions]         = useState(initialSessions);
  const [cases, setCases]               = useState(initialCases);
  const [evidence, setEvidence]         = useState(initialEvidence);
  const [notifications, setNotifications] = useState(initialNotifications);
  const [auditLog]                      = useState(initialAuditLog);

  const [openSession, setOpenSession]   = useState(null);
  const [modal, setModal]               = useState(null); // "schedule" | "newcase" | "upload"
  const [caseDetail, setCaseDetail]     = useState(null);

  // Live timer
  const [elapsed, setElapsed]           = useState(754);
  const [recording, setRecording]       = useState(true);
  const liveSession                     = sessions.find(s => s.status === "live");

  useEffect(() => {
    const t = setInterval(() => setElapsed(e => e + 1), 1000);
    return () => clearInterval(t);
  }, []);

  const unread = notifications.filter(n => !n.read).length;

  const navItems = [
    { id: "dashboard",     icon: "📊", label: "Dashboard" },
    { id: "cases",         icon: "📁", label: "Cases & Dockets" },
    { id: "hearings",      icon: "📅", label: "Hearings & Calendar" },
    { id: "jailcourt",     icon: "🏛", label: "JailCourt" },
    { id: "evidence",      icon: "🔐", label: "Evidence Vault" },
    { id: "notifications", icon: "🔔", label: "Notifications", badge: unread || null },
  ];
  const secondaryItems = [
    { id: "mock", icon: "🎭", label: "Mock Trial Lab" },
    { id: "ai",   icon: "🤖", label: "AI / GTP Sync" },
  ];
  const complianceItems = [
    { id: "audit", icon: "🛡", label: "TotalRecall / LEGyC" },
  ];

  const addSession = (form) => {
    const newS = {
      id: `s${Date.now()}`, ...form,
      status: "scheduled", elapsed: 0,
      circuit: "3rd Judicial Circuit",
      participants: [form.judge],
      notes: ""
    };
    setSessions(s => [...s, newS]);
  };

  const addCase = (form) => {
    const newC = {
      id: `c${Date.now()}`, ...form,
      status: "active", filed: new Date().toISOString().split("T")[0], docket: 0
    };
    setCases(c => [...c, newC]);
  };

  const addEvidence = (form) => {
    const c = cases.find(x => x.id === form.caseId);
    const newE = {
      id: `e${Date.now()}`, ...form,
      caseNumber: c?.caseNumber ?? "—",
      hash: Array.from({ length: 64 }, () => Math.floor(Math.random() * 16).toString(16)).join(""),
      status: "pending", size: "—", uploadDate: new Date().toISOString().split("T")[0]
    };
    setEvidence(e => [...e, newE]);
    setNotifications(n => [{
      id: `n${Date.now()}`, type: "filing", level: "info",
      message: `Evidence uploaded: ${form.fileName} — pending verification`,
      time: new Date().toLocaleTimeString("en-US", { hour: "2-digit", minute: "2-digit" }),
      read: false
    }, ...n]);
  };

  const renderView = () => {
    switch (view) {
      case "dashboard":     return <DashboardView sessions={sessions} cases={cases} elapsed={elapsed} onOpenSession={setOpenSession} onSchedule={() => setModal("schedule")} />;
      case "cases":         return <CasesView cases={cases} onNewCase={() => setModal("newcase")} onViewCase={setCaseDetail} />;
      case "hearings":      return <HearingsView sessions={sessions} elapsed={elapsed} onOpenSession={setOpenSession} onSchedule={() => setModal("schedule")} />;
      case "jailcourt":     return <JailCourtView sessions={sessions} elapsed={elapsed} onOpenSession={setOpenSession} />;
      case "evidence":      return <EvidenceView evidence={evidence} cases={cases} onUpload={() => setModal("upload")} />;
      case "notifications": return <NotificationsView notifications={notifications} setNotifications={setNotifications} />;
      case "mock":          return <MockTrialView />;
      case "ai":            return <AISyncView />;
      case "audit":         return <AuditView auditLog={auditLog} />;
      default:              return null;
    }
  };

  return (
    <div className="flex h-screen bg-slate-950 text-white overflow-hidden font-sans">
      {/* ── Sidebar ── */}
      <div className="w-64 bg-slate-900 border-r border-slate-800 flex flex-col shrink-0">
        {/* Logo */}
        <div className="p-5 border-b border-slate-800">
          <div className="flex items-center gap-3 mb-3">
            <div className="w-9 h-9 rounded-lg bg-gradient-to-br from-cyan-500 to-amber-500 flex items-center justify-center text-lg font-black">V</div>
            <div>
              <h1 className="font-extrabold text-base leading-tight">VideoCourts™</h1>
              <p className="text-xs text-slate-500">Judicial Session Console</p>
            </div>
          </div>
          <div className="flex gap-2 flex-wrap">
            <Badge variant="verified" pulse>System Online</Badge>
            <Badge variant="default">MVP · Chain-Aware</Badge>
          </div>
        </div>

        {/* Nav */}
        <nav className="flex-1 py-3 overflow-y-auto">
          <div className="px-4 py-2"><p className="text-xs text-slate-700 font-semibold uppercase tracking-wider">Navigation</p></div>
          {navItems.map(item => (
            <button key={item.id} onClick={() => setView(item.id)}
              className={`w-full flex items-center justify-between px-4 py-2.5 text-sm transition-colors ${view === item.id ? "bg-slate-800 text-cyan-400" : "text-slate-400 hover:bg-slate-800/60 hover:text-slate-200"}`}>
              <span className="flex items-center gap-3"><span>{item.icon}</span><span>{item.label}</span></span>
              {item.badge ? <span className="bg-red-500 text-white text-[10px] font-bold px-1.5 py-0.5 rounded-full">{item.badge}</span> : null}
            </button>
          ))}

          <div className="px-4 py-2 mt-3"><p className="text-xs text-slate-700 font-semibold uppercase tracking-wider">Education & AI</p></div>
          {secondaryItems.map(item => (
            <button key={item.id} onClick={() => setView(item.id)}
              className={`w-full flex items-center gap-3 px-4 py-2.5 text-sm transition-colors ${view === item.id ? "bg-slate-800 text-cyan-400" : "text-slate-400 hover:bg-slate-800/60 hover:text-slate-200"}`}>
              <span>{item.icon}</span><span>{item.label}</span>
            </button>
          ))}

          <div className="px-4 py-2 mt-3"><p className="text-xs text-slate-700 font-semibold uppercase tracking-wider">Audit & Compliance</p></div>
          {complianceItems.map(item => (
            <button key={item.id} onClick={() => setView(item.id)}
              className={`w-full flex items-center gap-3 px-4 py-2.5 text-sm transition-colors ${view === item.id ? "bg-slate-800 text-cyan-400" : "text-slate-400 hover:bg-slate-800/60 hover:text-slate-200"}`}>
              <span>{item.icon}</span><span>{item.label}</span>
            </button>
          ))}
        </nav>

        {/* Footer */}
        <div className="p-4 border-t border-slate-800 text-xs space-y-1 text-slate-500">
          <div className="flex justify-between">
            <span>LEGyC Chain:</span>
            <span className="text-emerald-400 font-semibold">Synchronized</span>
          </div>
          <div className="flex justify-between">
            <span>Node:</span>
            <span className="font-mono">VC-ND-07</span>
          </div>
          <button className="text-cyan-400 hover:underline mt-1" onClick={() => setView("audit")}>View Log →</button>
        </div>
      </div>

      {/* ── Main ── */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Top bar */}
        <header className="bg-slate-900 border-b border-slate-800 px-8 py-4 flex items-center justify-between shrink-0">
          <div>
            <h2 className="text-xl font-extrabold capitalize">
              {navItems.find(n => n.id === view)?.label ??
               secondaryItems.find(n => n.id === view)?.label ??
               complianceItems.find(n => n.id === view)?.label ?? view}
            </h2>
            {liveSession && (
              <div className="flex items-center gap-2 mt-0.5">
                <Badge variant="live" pulse>LIVE</Badge>
                <span className="text-xs text-slate-500">{liveSession.title} · {fmtElapsed(elapsed)}</span>
              </div>
            )}
          </div>
          <div className="flex gap-3">
            {view === "dashboard" && <Btn onClick={() => setModal("schedule")}>+ Schedule Hearing</Btn>}
            {view === "cases"     && <Btn onClick={() => setModal("newcase")}>+ New Case</Btn>}
            {view === "evidence"  && <Btn onClick={() => setModal("upload")}>+ Upload Evidence</Btn>}
            {view === "hearings"  && <Btn onClick={() => setModal("schedule")}>+ Schedule Hearing</Btn>}
            {liveSession && (
              <Btn variant="danger" onClick={() => setOpenSession(liveSession)}>
                🔴 {fmtElapsed(elapsed)} · Join Live
              </Btn>
            )}
          </div>
        </header>

        {/* Content */}
        <main className="flex-1 overflow-y-auto p-8">
          {renderView()}
        </main>

        {/* Footer */}
        <footer className="bg-slate-900 border-t border-slate-800 px-8 py-2.5 flex justify-between items-center text-xs text-slate-600 shrink-0">
          <span>Court-grade recording · TotalRecall & LEGyC enforced</span>
          <span>By proceeding, all participants consent to recording and biometric-linked identity checks.</span>
          <span>Build: VC-MVP-0.2.0</span>
        </footer>
      </div>

      {/* ── Right Panel ── */}
      <RightPanel notifications={notifications} liveSession={liveSession} elapsed={elapsed} recording={recording} />

      {/* ── Modals ── */}
      {openSession && (
        <LiveSessionPanel
          session={openSession}
          elapsed={elapsed}
          recording={recording}
          setRecording={setRecording}
          onClose={() => setOpenSession(null)}
        />
      )}
      {modal === "schedule" && <ScheduleModal onClose={() => setModal(null)} onSave={addSession} />}
      {modal === "newcase"  && <NewCaseModal  onClose={() => setModal(null)} onSave={addCase} />}
      {modal === "upload"   && <UploadEvidenceModal cases={cases} onClose={() => setModal(null)} onSave={addEvidence} />}
      {caseDetail && <CaseDetailModal c={caseDetail} onClose={() => setCaseDetail(null)} />}
    </div>
  );
}
