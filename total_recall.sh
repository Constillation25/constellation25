#!/bin/bash
# Total Recall — searches filesystem for artifact files matching a query
QUERY="${1:-constellation}"
echo "[Total Recall] Searching for: $QUERY"
find ~ -type f -iname "*${QUERY}*" 2>/dev/null | head -30
