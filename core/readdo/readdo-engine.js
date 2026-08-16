#!/usr/bin/env node
'use strict';

const fs = require('fs').promises;
const { exec } = require('child_process');
const util = require('util');
const path = require('path');
const crypto = require('crypto');

const execPromise = util.promisify(exec);

class ReadDoEngine {
  constructor(readdoPath, options = {}) {
    this.readdoPath = path.resolve(readdoPath);
    this.tasks = [];
    this.executionLog = [];
    this.forensicDir = options.forensicDir || path.join(process.env.HOME, 'constellation25', 'logs', 'forensic');
    this.bioAuthRequired = options.bioAuth !== false;
    this.dryRun = options.dryRun || false;
  }

  async parse() {
    console.log(`📋 [C25-Forge] Parsing ReadDo file: ${this.readdoPath}`);
    const content = await fs.readFile(this.readdoPath, 'utf8');
    this.tasks = this.extractTasks(content);
    console.log(`✓ Found ${this.tasks.length} tasks`);
    return this.tasks;
  }

  extractTasks(content) {
    const tasks = [];
    const taskPattern = /###\s*TASK-(\d+)\r?\n([\s\S]*?)(?=###\s*TASK-|\n##\s*|$)/g;
    let match;
    while ((match = taskPattern.exec(content)) !== null) {
      const [, id, body] = match;
      tasks.push({
        id: `TASK-${id}`,
        name: this.extractField(body, 'Name') || `Unnamed Task ${id}`,
        priority: this.extractField(body, 'Priority') || 'MEDIUM',
        type: this.extractField(body, 'Type') || 'GENERAL',
        bioauth: this.extractField(body, 'BioAuth'),
        dependencies: this.extractDependencies(body),
        actions: this.extractActions(body),
        verification: this.extractVerification(body),
        onSuccess: this.extractField(body, 'On Success'),
        onFailure: this.extractField(body, 'On Failure'),
        status: 'PENDING'
      });
    }
    return tasks;
  }

  extractField(body, fieldName) {
    const pattern = new RegExp(`\\*\\*${fieldName}\\*\\*:\\s*(.+?)(?:\\r?\\n|$)`, 'i');
    const match = body.match(pattern);
    return match ? match[1].trim() : null;
  }

  extractDependencies(body) {
    const match = body.match(/\*\*Dependencies\*\*:\s*(.+?)(?:\r?\n|$)/i);
    if (!match) return [];
    const deps = match[1].trim();
    if (deps.toLowerCase() === 'none') return [];
    return deps.split(',').map(d => d.trim());
  }

  extractActions(body) {
    const codeBlockPattern = /```(?:bash|sh)?\r?\n([\s\S]*?)```/g;
    const actions = [];
    let match;
    while ((match = codeBlockPattern.exec(body)) !== null) {
      const commands = match[1].trim().split(/\r?\n/)
        .filter(line => line.trim() && !line.trim().startsWith('#'));
      actions.push(...commands);
    }
    return actions;
  }

  extractVerification(body) {
    const verificationPattern = /\*\*Verification\*\*:\s*\r?\n((?:-\s*\[.\].*\r?\n?)+)/i;
    const match = body.match(verificationPattern);
    if (!match) return [];
    return match[1].split(/\r?\n/)
      .filter(line => line.includes('[ ]') || line.includes('[x]'))
      .map(line => line.replace(/^-\s*\[.\]\s*/, '').trim());
  }

  async execute() {
    console.log('\n🚀 [C25-Earth] Starting ReadDo execution...\n');
    if (this.dryRun) console.log('🔍 DRY RUN MODE - No commands will be executed\n');
    await fs.mkdir(this.forensicDir, { recursive: true });

    for (const task of this.tasks) {
      try {
        await this.executeTask(task);
      } catch (error) {
        console.error(`✗ Task ${task.id} failed: ${error.message}`);
        await this.handleFailure(task, error);
        if (task.priority === 'CRITICAL') {
          console.error('💥 Critical task failed. St
