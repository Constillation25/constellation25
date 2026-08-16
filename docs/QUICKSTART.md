# Constellation25 Quick Start Guide

## 30-Second Install

```bash
curl -sSL https://raw.githubusercontent.com/Constillation25/constellation25/main/install.sh | bash
source ~/.bashrc
c25
```

## Essential Commands

| Command | Action |
|---------|--------|
| `c25` | Open Master Control |
| `c25start` | Start all 17 agents |
| `c25stop` | Stop all agents |
| `c25status` | Check agent status |
| `c25recall` | Run TotalRecall scan |
| `c25push` | Push to GitHub |
| `c25tasks` | View task queue |
| `c25help` | Show this guide |

## Your First Task

```bash
# 1. Start agents
c25start

# 2. Drop a task file
cat > ~/constellation25/incoming/task.json << EOF
{
  "task": "Review my code for security issues",
  "agent": "mars",
  "priority": "high"
}
EOF

# 3. Check status
c25status

# 4. View logs
tail -f ~/constellation25/logs/orchestrator_bg.log
```

## Agent Selection Guide

| I need to... | Use Agent |
|-------------|-----------|
| Start a new project | 🌍 Earth |
| Fix a bug | 🌙 Moon |
| Make it faster | ☀️ Sun |
| Write tests | ☿ Mercury |
| Check security | ♂ Mars |
| Write docs | ♃ Jupiter |
| Clean up code | ♄ Saturn |
| Deploy it | ⭐ Sirius |
| Set up CI/CD | 🐉 Hydra |

## Troubleshooting

```bash
# Agents not starting?
c25stop && c25start

# Check logs
tail -50 ~/constellation25/logs/stalker_global.log

# Reset everything
bash ~/constellation25/scripts/sovereign-final-clean-rebuild.sh

# Check storage
c25  # → Option 8
```
