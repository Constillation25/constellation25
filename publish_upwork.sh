#!/usr/bin/env bash
set -o pipefail; export LC_ALL=C
PROFILE="$HOME/constellation25/platform_profiles/upwork_agent_profile.md"
echo "=== UPWORK SUBMISSION CHECKLIST ==="
echo "1. Go to: https://www.upwork.com/freelancers/~create"
echo "2. Copy profile content:"
cat "$PROFILE"
echo ""
echo "3. Paste into Upwork profile form"
echo "4. Set hourly rate: \$50 (or project pricing)"
echo "5. Add portfolio links: https://github.com/Faceprintpay/constellation25"
echo "6. Submit for review"
echo ""
echo "✅ Profile ready. Submit now."
