#!/bin/bash
# C25 Secure Vault Manager
# Usage: ./c25-vault.sh [lock|unlock|init]

VAULT_FILE="$HOME/constellation25/core/secrets.gpg"

case "$1" in
  init)
    echo "[C25 Vault] Initializing secure vault. Set a strong master passphrase."
    echo "Enter your Stripe Keys below (they will be encrypted immediately):"
    read -p "STRIPE_SECRET_KEY: " SK
    read -p "STRIPE_PUBLISHABLE_KEY: " PK
    
    # Encrypt and save
    echo -e "STRIPE_SECRET_KEY=$SK\nSTRIPE_PUBLISHABLE_KEY=$PK" | gpg --symmetric --cipher-algo AES256 -o "$VAULT_FILE"
    chmod 600 "$VAULT_FILE"
    echo "[C25 Vault] 🔒 Secrets encrypted and locked."
    ;;
  unlock)
    if [ -f "$VAULT_FILE" ]; then
      echo "[C25 Vault] 🔓 Decrypting secrets to memory..."
      gpg --decrypt "$VAULT_FILE" 2>/dev/null
    else
      echo "[C25 Vault] ❌ Vault not found. Run './c25-vault.sh init' first."
    fi
    ;;
  *)
    echo "Usage: $0 {init|unlock}"
    ;;
esac
