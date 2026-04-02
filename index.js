const http = require('http');
const fs = require('fs');
const path = require('path');
const PORT = process.env.PORT || 3000;

const server = http.createServer((req, res) => {
  const url = req.url.split('?')[0];
  res.setHeader('Content-Type', 'application/json');

  if (req.method === 'POST' && url === '/api/webhook') {
    let body = '';
    req.on('data', c => body += c);
    req.on('end', () => {
      console.log(`[WEBHOOK] ${body.substring(0, 200)}`);
      res.writeHead(200); res.end(JSON.stringify({received: true, ts: Date.now()}));
    });
    return;
  }

  if (url === '/api/proxy' || url === '/health' || url === '/') {
    res.writeHead(200);
    res.end(JSON.stringify({
      system: "Constellation25",
      status: "online",
      pathos: "connected",
      agents: 25,
      endpoints: { proxy: "/api/proxy", health: "/health", webhook: "/api/webhook" },
      timestamp: new Date().toISOString()
    }));
    return;
  }

  if (url === '/api/agents') {
    const agents = fs.readdirSync('./agents').map(f => f.replace('.json',''));
    res.writeHead(200); res.end(JSON.stringify({count: agents.length, agents}));
    return;
  }

  if (url === '/api/ai/prompt' && req.method === 'POST') {
    let body = '';
    req.on('data', c => body += c);
    req.on('end', () => res.end(JSON.stringify({ai_response: "processed_by_pathos", prompt: body})));
    return;
  }

  res.writeHead(404); res.end(JSON.stringify({error: "route_not_found"}));
});

server.listen(PORT, () => console.log(`🚀 C25 Sovereign Stack Live on :${PORT}`));
