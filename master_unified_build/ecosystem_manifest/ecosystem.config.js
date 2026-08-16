module.exports = {
  apps: [
    { name: "c25-orchestrator", script: "./backend/orchestrator.js", watch: true },
    { name: "c25-forensics", script: "./backend/main.py", interpreter: "python3", watch: true }
  ]
}
