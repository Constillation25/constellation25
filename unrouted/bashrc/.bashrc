# Run Obsidian consolidation script on startup
cd ~/storage/shared/Documents/ObsidianVault/ # Change this to your master vault path
bash consolidate_obsidian.sh
cd ~ # Return to home directory after running
[[ -f ~/.sync-termux.sh ]] && ~/.sync-termux.sh
