#!/usr/bin/env node
/**
 * C25 Unified Sovereign Gateway (The Main)
 * Owner: CyGeL White | Kre8tive Holdings
 * Architecture: Routes traffic to FacePrintPay (Retail) or Mybuyo (Online)
 */
'use strict';

const BioAuth = require('./core/bioauth');
const Ledger = require('./core/ledger');

class SovereignGateway {
  constructor() {
    this.bioauth = new BioAuth();
    this.ledger = new Ledger();
  }

  async processTransaction(payload) {
    const { channel, amount, user_id, biometric_data } = payload;
    
    console.log(`🚀 [C25-Apollo] Intercepting ${channel.toUpperCase()} transaction for $${amount}`);

    // 1. Unified BioAuth (Juno 👑)
    const is_verified = await this.bioauth.verify(user_id, biometric_data, channel);
    if (!is_verified) throw new Error('C25-BioAuth: VerseDNA Verification Failed.');

    // 2. Channel Routing
    let receipt;
    if (channel === 'retail') {
      const FacePrintPay = require('./retail/pos-engine');
      receipt = await FacePrintPay.executeInPerson(payload);
    } else if (channel === 'online') {
      const Mybuyo = require('./online/checkout-engine');
      receipt = await Mybuyo.executeEcommerce(payload);
    } else {
      throw new Error('C25-Apollo: Invalid transaction channel.');
    }

    // 3. Unified Ledger (Saturn 🪐)
    await this.ledger.record(receipt);
    return receipt;
  }
}

module.exports = SovereignGateway;
