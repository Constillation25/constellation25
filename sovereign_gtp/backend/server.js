const express = require('express');
const ws = require('ws');
const fs = require('fs');
const { exec } = require('child_process');
const app = express();
app.use(express.json());
const wss = new ws.Server({ port: 8080 });

wss.on('connection', ws => {
  ws.on('message', msg => {
    const { agent } = JSON.parse(msg);
    exec(`bash ~/sovereign_gtp/agents/${agent}.sh`, (err, out) => {
      ws.send(JSON.stringify({ [agent]: err ? 'Breach' : 'Domination', log: out, plan: '52f7b763 parsed' }));
    });
  });
});

app.post('/api/game-over', (req, res) => {
  res.json({ message: 'NDA locked — swarm yours' });
  // Weight load sim: console.log('Torch weights injected');
});

app.get('/api/proxy', (req, res) => {
  // Fake proxy for aimetaverse.cloud since no internet — but in real, curl it
  res.send('AiMetaverse content proxied — planetary agents owning it');
});

app.listen(3000, () => console.log('Backend domination on 3000'));
