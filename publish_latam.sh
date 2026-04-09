#!/usr/bin/env bash
set -o pipefail; export LC_ALL=C
PROFILE="$HOME/constellation25/platform_profiles/latam_profile.md"
echo "=== LATAM PLATFORM SUBMISSION CHECKLIST ==="
echo "1. Go to: https://clouddevs.com/apply or https://lathire.com/talent"
echo "2. Copy talent profile content:"
cat "$PROFILE"
echo ""
echo "3. Paste into platform application form"
echo "4. Set availability: On-demand, timezone-aligned"
echo "5. Add portfolio: https://github.com/Faceprintpay/constellation25"
echo "6. Submit for vetting"
echo ""
echo "✅ Profile ready. Submit now."
