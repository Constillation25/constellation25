-- C25 Ceres 🪨: Unified Ledger Migration (FacePrintPay + Mybuyo)
CREATE TABLE IF NOT EXISTS sovereign_transactions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  channel VARCHAR(20) NOT NULL CHECK (channel IN ('retail', 'online')),
  user_id UUID NOT NULL,
  amount DECIMAL(19, 4) NOT NULL,
  currency VARCHAR(3) DEFAULT 'USD',
  bioauth_hash VARCHAR(64) NOT NULL,
  status VARCHAR(20) DEFAULT 'PENDING',
  created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_channel_status ON sovereign_transactions(channel, status);
