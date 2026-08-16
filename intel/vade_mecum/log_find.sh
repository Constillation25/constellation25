#!/data/data/com.termux/files/usr/bin/bash
# Usage: ./log_find.sh <zone> "<description>"
ZONE=$1
DESC=$2

if [ -z "$ZONE" ] || [ -z "$DESC" ]; then
    echo "Usage: $0 <zone> '<description>'"
    exit 1
fi

# Fetch current GPS via Termux:API
LOC=$(termux-location 2>/dev/null)
LAT=$(echo $LOC | grep -o '"latitude":[0-9.-]*' | cut -d: -f2)
LON=$(echo $LOC | grep -o '"longitude":[0-9.-]*' | cut -d: -f2)

if [ -z "$LAT" ] || [ -z "$LON" ]; then
    echo "[!] GPS failed. Enter manually or install termux-api."
    read -p "Lat: " LAT
    read -p "Lon: " LON
fi

sqlite3 ~/constellation25/intel/vade_mecum/db/finds.db < <(echo "INSERT INTO magnet_finds (latitude, longitude, zone, object_description) VALUES ($LAT, $LON, '$ZONE', '$DESC');")
echo "[✓] Logged: $DESC at $ZONE ($LAT, $LON)"
