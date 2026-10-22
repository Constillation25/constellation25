// NLP2CODE Interface for Total Recall Metadata Harvest
const API_BASE = 'http://localhost:8002';

class NLP2CodeInterface {
  constructor() {
    this.nlpInput = document.getElementById('nlpInput');
    this.generateBtn = document.getElementById('generateBtn');
    this.harvestBtn = document.getElementById('harvestBtn');
    this.codeOutput = document.getElementById('codeOutput');
    this.metadataOutput = document.getElementById('metadataOutput');
    this.statusOutput = document.getElementById('statusOutput');
    
    this.init();
  }
  
  init() {
    this.generateBtn.addEventListener('click', () => this.generateCode());
    this.harvestBtn.addEventListener('click', () => this.harvestMetadata());
    this.loadStatus();
  }
  
  async generateCode() {
    const prompt = this.nlpInput.value.trim();
    if (!prompt) {
      this.codeOutput.textContent = 'Error: Please enter a description';
      return;
    }
    
    this.codeOutput.textContent = 'Generating code...';
    
    try {
      const response = await fetch(`${API_BASE}/api/generate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt, mode: 'code' })
      });
      
      const data = await response.json();
      this.codeOutput.textContent = data.code || data.error || 'No code generated';
    } catch (err) {
      this.codeOutput.textContent = `Error: ${err.message}`;
    }
  }
  
  async harvestMetadata() {
    this.metadataOutput.textContent = 'Harvesting metadata from Total Recall...';
    
    try {
      const response = await fetch(`${API_BASE}/api/metadata`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          source: 'total_recall',
          include_hashes: true,
          include_chain: true
        })
      });
      
      const data = await response.json();
      this.metadataOutput.textContent = JSON.stringify(data, null, 2);
    } catch (err) {
      this.metadataOutput.textContent = `Error: ${err.message}`;
    }
  }
  
  async loadStatus() {
    try {
      const response = await fetch(`${API_BASE}/health`);
      const data = await response.json();
      
      this.statusOutput.innerHTML = '';
      Object.entries(data).forEach(([key, value]) => {
        const item = document.createElement('div');
        item.className = `status-item ${value.status || 'offline'}`;
        item.innerHTML = `<strong>${key}</strong><br>${JSON.stringify(value)}`;
        this.statusOutput.appendChild(item);
      });
    } catch (err) {
      this.statusOutput.innerHTML = '<div class="status-item offline">API offline</div>';
    }
  }
}

document.addEventListener('DOMContentLoaded', () => {
  new NLP2CodeInterface();
});
