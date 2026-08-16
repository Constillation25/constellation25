#!/bin/bash
REPO_NAME="constellation25"   # Change if needed
BRANCH="main"

echo "🌌 Pushing Constellation25 to GitHub..."

# Initialize if not a git repo
if [ ! -d ".git" ]; then
  git init
  git branch -M $BRANCH
fi

git add .
git commit -m "Add agent orchestration, async task management, circuit breaker + ledger files - $(date '+%Y-%m-%d %H:%M')" || echo "Nothing new to commit"

# Add remote if not set
if ! git remote | grep -q origin; then
  git remote add origin https://github.com/Constillation25/$REPO_NAME.git
fi

git push -u origin $BRANCH

echo "✅ Done!"
