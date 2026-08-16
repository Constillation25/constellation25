module.exports = {
  apps: [
    { name: "c25-master-orchestrator", script: "./orchestrator.js", watch: true },
    { name: "c25-mcp-gateway", script: "./mcp_gateway.js", watch: true },
    { name: "c25-frontend-sync", script: "./frontend_sync.js", watch: true }
  ]
}
