const stripe = require('stripe');
const { execSync } = require('child_process');

class C25SecureStripeGateway {
  constructor() {
    console.log('[C25 Apollo] Booting Secure Gateway...');
    // Decrypt secrets from Vault into memory only
    try {
      const secrets = execSync('~/constellation25/core/c25-vault.sh unlock', { encoding: 'utf8' });
      const env = {};
      secrets.split('\n').forEach(line => {
        const [key, val] = line.split('=');
        if (key && val) env[key] = val;
      });
      
      if (!env.STRIPE_SECRET_KEY) throw new Error("Vault empty or locked.");
      
      this.client = stripe(env.STRIPE_SECRET_KEY);
      console.log('[C25 Apollo] 🔓 Stripe Client Authenticated via Secure Vault.');
    } catch (e) {
      console.error('[C25 Apollo] ❌ FATAL: Vault access denied. Run c25-vault.sh unlock.');
      process.exit(1);
    }
  }

  async createIntent(amount) {
    return this.client.paymentIntents.create({ amount, currency: 'usd' });
  }
}

module.exports = new C25SecureStripeGateway();
