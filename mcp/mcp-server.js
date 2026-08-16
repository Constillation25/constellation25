const http = require('http');
const server = http.createServer((req, res) => {
  res.writeHead(200, { 'Content-Type': 'application/json' });
  res.end(JSON.stringify({ status: 'C25 MCP Server Online', agent: 'Nexus' }));
});
server.listen(3000, () => console.log('[C25 MCP] Listening on port 3000'));
