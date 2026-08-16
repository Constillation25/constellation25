<div align="center">

# 🌌 Constellation25

### The 17-Agent Sovereign AI Platform

[![Version](https://img.shields.io/badge/version-1.0.0-00ff88.svg)](https://github.com/Constillation25/constellation25)
[![Platform](https://img.shields.io/badge/platform-Termux%20%7C%20Linux%20%7C%20macOS-blue.svg)](https://github.com/Constillation25/constellation25)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Author](https://img.shields.io/badge/author-Cygel%20White-orange.svg)](https://github.com/Constillation25)

**Built by Cygel White | Kre8tive Konceptz | MrGGTP**

[Install](#installation) • [Agents](#agents) • [ReadDo](#readdo-format) • [BioAuth](#bioauth) • [Docs](docs/)

</div>

---

## 🚀 One-Line Install

```bash
curl -sSL https://raw.githubusercontent.com/Constillation25/constellation25/main/install.sh | bash
```

Or on Termux:
```bash
curl -sSL https://raw.githubusercontent.com/Constillation25/constellation25/main/install.sh | bash
source ~/.bashrc
c25
```

---

## 🌟 What is Constellation25?

Constellation25 is a **17-agent sovereign AI platform** that runs entirely on your device — no cloud required. It provides specialized AI agents for every development task, integrated with:

- 🔐 **BioAuth** — Biometric verification for critical actions
- 📋 **ReadDo** — Executable documentation format
- 🔍 **TotalRecall** — Forensic evidence collection and analysis
- 🌐 **YesQuidPro** — Natural language to bash pipeline
- 🔗 **MCP** — Model Context Protocol integration

---

## 🌌 The 17 Planetary Agents

| # | Agent | Specialty | Command |
|---|-------|-----------|---------|
| 1 | 🌍 Earth | Code structure & scaffolding | `c25 earth <task>` |
| 2 | 🌙 Moon | Bug fixes & syntax errors | `c25 moon <task>` |
| 3 | ☀️ Sun | Performance optimization | `c25 sun <task>` |
| 4 | ☿ Mercury | Unit tests & coverage | `c25 mercury <task>` |
| 5 | ♀ Venus | Regression & integration tests | `c25 venus <task>` |
| 6 | ♂ Mars | Security & vulnerabilities | `c25 mars <task>` |
| 7 | ♃ Jupiter | Docs & code analysis | `c25 jupiter <task>` |
| 8 | ♄ Saturn | Refactor & modernize | `c25 saturn <task>` |
| 9 | ♅ Uranus | NLP & intent parsing | `c25 uranus <task>` |
| 10 | ♆ Neptune | Dedup & consolidate | `c25 neptune <task>` |
| 11 | 🦢 Cygnus | AI models & LLM | `c25 cygnus <task>` |
| 12 | 🏹 Orion | UI/UX & frontend | `c25 orion <task>` |
| 13 | 🌌 Andromeda | API & integrations | `c25 andromeda <task>` |
| 14 | ✨ Pleiades | Env & dependencies | `c25 pleiades <task>` |
| 15 | ⭐ Sirius | Deploy & scaling | `c25 sirius <task>` |
| 16 | 🐕 Canis Major | Tech debt & legacy | `c25 canismajor <task>` |
| 17 | 🐉 Hydra | CI/CD pipelines | `c25 hydra <task>` |

---

## 📦 Installation

### Requirements
- Node.js 16+
- Python 3.8+
- Git
- curl

### Quick Install
```bash
# Clone
git clone https://github.com/Constillation25/constellation25.git
cd constellation25

# Install
bash install.sh

# Launch
source ~/.bashrc
c25
```

### Termux (Android)
```bash
pkg install nodejs git python curl
curl -sSL https://raw.githubusercontent.com/Constillation25/constellation25/main/install.sh | bash
source ~/.bashrc
c25
```

### Docker
```bash
docker pull ghcr.io/constillation25/constellation25:latest
docker run -it constellation25
```

---

## 🎯 Quick Start

```bash
# Open Master Control
c25

# Start all 17 agents
c25start

# Check agent status
c25status

# Run TotalRecall forensic scan
c25recall

# Push to GitHub
c25push

# View task queue
c25tasks
```

---

## 📋 ReadDo Format

Constellation25 introduces the **ReadDo** format — documentation that executes:

```markdown
# READDO.md

### [TASK-001] Initialize Project
**Priority**: HIGH
**BioAuth**: Not Required
**Dependencies**: None

**Actions**:
```bash
git init
npm install
```

**Verification**:
- [ ] Repository initialized
- [ ] Dependencies installed
```

Run it:
```bash
node readdo-engine.js READDO.md
# or with dry run:
node readdo-engine.js READDO.md --dry-run
```

---

## 🔐 BioAuth Integration

Constellation25 supports biometric verification for critical actions:

```bash
# Any action marked [BIOAUTH] requires biometric confirmation
c25 deploy production  # → Triggers fingerprint/FaceID prompt
c25 push main          # → BioAuth required
c25 delete database    # → BioAuth required
```

Every BioAuth event is logged to the forensic vault with SHA-256 hash.

---

## 🔍 TotalRecall

Forensic evidence collection and analysis:

```bash
# Quick scan
c25recall

# Full forensic analysis
bash ~/total_recall_fast.sh

# View report
cat ~/TOTAL_RECALL_*/FORENSIC_SUMMARY.txt
```

---

## 🏗️ Architecture

```
constellation25/
├── install.sh              # One-line installer
├── c25_master_control.sh   # Master control menu
├── start_all_agents.sh     # Launch all 17 agents
├── stop_all_agents.sh      # Stop all agents
├── status_agents.sh        # Agent status dashboard
├── task_box.sh             # ReadDo task queue
├── c25_orchestrator.py     # Python orchestration engine
├── agents/
│   ├── execute_task.py     # Task execution engine
│   ├── listener.sh         # IPC listener
│   ├── history_scanner.sh  # Command history analysis
│   └── recover_scripts.sh  # Auto-recovery system
├── scripts/
│   ├── start-agents.sh
│   ├── ollama-agent.sh     # Local LLM integration
│   └── qwen-agent.sh       # Qwen model integration
├── docs/
│   ├── QUICKSTART.md
│   ├── AGENTS.md
│   ├── READDO.md
│   ├── BIOAUTH.md
│   └── API.md
├── logs/                   # All agent logs
├── incoming/               # Task drop folder
└── c25_ipc/               # Inter-process communication
    ├── pending/
    └── completed/
```

---

## 🆚 Constellation25 vs Alternatives

| Feature | Constellation25 | OpenClaw | AutoGPT | LangChain |
|---------|----------------|----------|---------|-----------|
| Specialized Agents | 17 | 1 | 1 | Varies |
| BioAuth | ✅ | ❌ | ❌ | ❌ |
| Forensic Logging | ✅ | ❌ | ❌ | ❌ |
| ReadDo Format | ✅ | ❌ | ❌ | ❌ |
| Termux Native | ✅ | ❌ | ❌ | ❌ |
| Offline First | ✅ | ❌ | ❌ | ❌ |
| TotalRecall | ✅ | ❌ | ❌ | ❌ |
| Open Source | ✅ | ✅ | ✅ | ✅ |

---

## 🤝 Contributing

```bash
# Fork and clone
git clone https://github.com/YOUR_USERNAME/constellation25.git
cd constellation25

# Create feature branch
git checkout -b feature/new-agent

# Make changes, then push
git push origin feature/new-agent

# Open PR at github.com/Constillation25/constellation25
```

---

## 📜 License

MIT License — Free to use, modify, and distribute.

---

## 👤 Author

**Cygel White**
- GitHub: [@Constillation25](https://github.com/Constillation25)
- Also Known As: MrGGTP, AiKi
- Organization: Kre8tive Konceptz
- Location: Greensboro, NC
- Email: CyGeL.co@gmail.com

---

<div align="center">

**🌌 Constellation25 — Because specialization beats generalization**

*17 agents. 17 specialties. Zero compromises.*

</div>
