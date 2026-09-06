#!/data/data/com.termux/files/usr/bin/env bash
set -euo pipefail
echo "=== C25 INSTALLER ==="
echo "AVAIL before: $(df -h /data | awk "NR==2{print \$4}")"
pkg install -y python nodejs git sqlite proot-distro
npm install -g pm2 2>/dev/null || true
mkdir -p ~/constellation25/{db,map,logs} ~/c25_ipc/{pending,done}
pip install --force-reinstall ~/c25-package/dist/c25-*.whl --break-system-packages
echo "[+] C25 package installed"
echo "AVAIL after: $(df -h /data | awk "NR==2{print \$4}")"
echo "=== INSTALL COMPLETE ==="
