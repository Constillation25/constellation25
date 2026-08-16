#!/usr/bin/env node
const { Command } = require('commander');
const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

const program = new Command();
const HOME = process.env.HOME;
const C25_ROOT = path.join(HOME, 'constellation25');

program.name('c25').description('Constellation25 Master CLI').version('1.0.0');

// Auto-heal function for PM2
function ensurePM2() {
  try {
    execSync('pm2 ping', { stdio: 'ignore' });
  } catch (e) {
    console.log('[C25] PM2 daemon down. Auto-healing...');
    execSync('pm2 resurrect || pm2 start ' + path.join(C25_ROOT, 'pm2/ecosystem.config.js'), { stdio: 'inherit' });
  }
}

program
  .command('status')
  .description('Check PM2, IPC, and Vault status')
  .action(() => {
    ensurePM2();
    console.log('\n--- [C25] Mesh Status ---');
    execSync('pm2 status', { stdio: 'inherit' });
    
    const pending = fs.readdirSync(path.join(HOME, 'c25_ipc/pending')).filter(f => f.endsWith('.json')).length;
    console.log(`\n[IPC Queue] ${pending} tasks pending.`);
  });

program
  .command('route <agent> <task>')
  .description('Route a task to a specific Planetary Agent')
  .action((agent, task) => {
    const payload = { agent, task, timestamp: new Date().toISOString() };
    const file = path.join(HOME, `c25_ipc/pending/task_${agent.toLowerCase()}_${Date.now()}.json`);
    fs.writeFileSync(file, JSON.stringify(payload, null, 2));
    console.log(`[C25] Task routed to ${agent}: ${task}`);
  });

program
  .command('vault <action>')
  .description('Manage the secure GPG vault (init|unlock)')
  .action((action) => {
    const vaultScript = path.join(C25_ROOT, 'core/c25-vault.sh');
    if (fs.existsSync(vaultScript)) {
      execSync(`${vaultScript} ${action}`, { stdio: 'inherit' });
    } else {
      console.error('[C25] Vault script missing. Run incident response protocol.');
    }
  });

program
  .command('logs')
  .description('Tail the C25 dispatcher logs')
  .action(() => {
    const logFile = path.join(C25_ROOT, 'logs/dispatcher.log');
    if (fs.existsSync(logFile)) {
      execSync(`tail -n 20 ${logFile}`, { stdio: 'inherit' });
    } else {
      console.log('[C25] No logs found yet.');
    }
  });

program.parse();
