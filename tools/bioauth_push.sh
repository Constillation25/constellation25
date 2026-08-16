#!/bin/bash
# BioAuth GitHub Push
REPO_PATH=${1:-"$HOME/constellation25"}
COMMIT_MSG=${2:-"🤖 Bio-authorized push from Sovereign AI"}

echo "[*] BIO-AUTHORIZED GITHUB PUSH"
echo "[*] Target: $REPO_PATH"

# Biometric gate
echo "[*] Please scan your fingerprint..."
termux-toast "🔒 Scan fingerprint to authorize GitHub push..."
AUTH_RESULT=$(termux-fingerprint 2>/dev/null)

if echo "$AUTH_RESULT" | grep -q "AUTH_RESULT_SUCCESS"; then
    echo "✅ Identity verified."
    termux-toast "✅ BioAuth Verified: Preparing push..."
else
    echo "❌ Fingerprint auth failed. Access denied."
    termux-toast "❌ BioAuth Failed: Push aborted."
    exit 1
fi

# Token check
TOKEN_FILE="$HOME/.gh_token"
if [ ! -f "$TOKEN_FILE" ]; then
    echo "⚠️ GitHub token not found at $TOKEN_FILE"
    echo "Run: echo 'your_github_pat' > ~/.gh_token"
    termux-toast "⚠️ GitHub token missing. Push aborted."
    exit 1
fi

TOKEN=$(cat "$TOKEN_FILE" | tr -d '\r\n ')

# Repo validation
if [ ! -d "$REPO_PATH/.git" ]; then
    echo "❌ Not a valid git repository: $REPO_PATH"
    termux-toast "❌ Invalid repo path."
    exit 1
fi

cd "$REPO_PATH" || exit 1
rm -f .git/index.lock
git config user.email "cygel@kre8tive.space" >/dev/null 2>&1
git config user.name "CyGeL [BioAuth]" >/dev/null 2>&1

CURRENT_ORIGIN=$(git remote get-url origin 2>/dev/null | sed 's/.*github.com\///' | sed 's/\.git$//')
if [ -z "$CURRENT_ORIGIN" ]; then
    CURRENT_ORIGIN="FacePrintPay/constellation25"
fi

git remote set-url origin "https://${TOKEN}@github.com/${CURRENT_ORIGIN}.git"

echo "[*] Staging changes..."
git add .
echo "[*] Committing..."
git commit -m "$COMMIT_MSG" --allow-empty
echo "[*] Pushing to GitHub..."
PUSH_OUTPUT=$(git push origin main 2>&1)
PUSH_STATUS=$?

if [ $PUSH_STATUS -eq 0 ]; then
    echo "🚀 SUCCESS: Code pushed under sovereign identity."
    termux-toast "🚀 SUCCESS: Sovereign push complete!"
else
    echo "💥 FAILED: Push rejected."
    echo "$PUSH_OUTPUT"
    termux-toast "💥 FAILED: GitHub push rejected."
    exit 1
fi
