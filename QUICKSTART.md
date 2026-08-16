# Quick Start Guide

## 1. Environment Setup
Ensure you are running **Termux** on Android or a Debian-based Linux environment.
`pkg install python git openssl`

## 2. Booting the Mesh
`bash ~/constellation25/start_agents.sh`

## 3. Interacting with Agents
Use the AI Assistant to query any file:
`python3 ~/constellation25/c25_assist.py <path_to_file>`

## 4. Reviewing Autonomous Tasks
The agents generate suggestions every 60 seconds. Review them here:
`cat ~/constellation25/logs/suggestions_queue.md`

## 5. Pushing to the Sovereign Cloud
`bash ~/constellation25/unified_push.sh`
