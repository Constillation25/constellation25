#!/data/data/com.termux/files/usr/bin/bash
# ToolX v2.1 - C25 Security Toolkit Installer

echo "🛡️ ToolX v2.1 - C25 Sovereign Security Kit"
echo "==========================================="

install_category() {
    local category=$1
    echo "Installing category $category..."
    
    case $category in
        1) pkg install nmap dnsutils ;;
        2) pkg install nikto sqlmap ;;
        3) echo "Metasploit requires manual setup" ;;
        4) pkg install aircrack-ng ;;
        5) pkg install autopsy ;;
        6) pkg install zaproxy ;;
        7) pkg install stress-ng apache-benchmark ;;
        8) pkg install wireshark-cli tcpdump ;;
        9) pkg install hashcat john ;;
        10) echo "Backdoor tools - security review required" ;;
        11) pkg install traceroute mtr geoip ;;
        12) pkg install python go rust nodejs ;;
        13) echo "DDOS tools - ethical use only" ;;
        14) pkg install nginx ;;
        15) pkg install termux-api ;;
    esac
}

echo "Select category (1-15) or 'all':"
read choice

if [ "$choice" = "all" ]; then
    for i in {1..15}; do
        install_category $i
    done
else
    install_category $choice
fi

echo "✅ ToolX installation complete"
