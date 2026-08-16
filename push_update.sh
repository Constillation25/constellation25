#!/bin/bash

# Constellation25 Push Script
BRANCH=${1:-main}  # Default to main, or pass branch name

echo "🌌 Pushing Constellation25 updates to branch: $BRANCH"

# Add all changes
git add .

# Commit with timestamp
commit_message="Update: Agent orchestration + async task management - $(date '+%Y-%m-%d %H:%M:%S')"
git commit -m "$commit_message" || echo "No new changes to commit"

# Push
git push origin $BRANCH

echo "✅ Push complete to $BRANCH"
echo "📊 Status:"
git status --short
