const path = require('path');
const home = process.env.HOME || '/data/data/com.termux/files/home';

module.exports = {
  apps: [
    {
      name: "c25-mcp-server",
      script: path.join(home, "constellation25/mcp/mcp-server.js"),
      interpreter: "node",
      env: { NODE_ENV: "production" }
    },
    {
      name: "c25-agent-mesh",
      script: path.join(home, "constellation25/core/c25-dispatcher.sh"),
      interpreter: "bash",
      watch: [path.join(home, "c25_ipc/pending/")],
      env: { C25_MODE: "mesh" }
    }
  ]
};
