#!/usr/bin/env bash
set -o pipefail; export LC_ALL=C
PROFILE="$HOME/constellation25/platform_profiles/wellfound_profile.md"
echo "=== WELLFOUND SUBMISSION CHECKLIST ==="
echo "1. Go to: https://wellfound.com/companies/new"
echo "2. Copy founder profile content:"
cat "$PROFILE"
echo ""
echo "3. Paste into Wellfound company form"
echo "4. Set funding ask: \$500K seed at \$5M pre-money"
echo "5. Add traction metrics: \$8.5K revenue, 4 customers, 300K assets"
echo "6. Submit for investor review"
echo ""
echo "✅ Profile ready. Submit now."
