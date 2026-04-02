#!/data/data/com.termux/files/usr/bin/bash
echo "🚀 C25 Full Deploy Sequence..."
git add -A
git commit -m "feat: c25 full deployment package $(date +%s)" || echo "⚠️ Nothing to commit"
git push origin main
npx vercel --prod --force --yes
echo "✅ Deploy complete. Check vercel logs."
