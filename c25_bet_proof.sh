#!/usr/bin/env bash
set -euo pipefail

ARTIFACT="${1:?Usage: bash c25_bet_proof.sh /path/to/your_script.sh 'I am trying to accomplish ...'}"
OBJECTIVE="${2:?Provide the objective string.}"

[[ -f "$ARTIFACT" ]] || { echo "Artifact not found: $ARTIFACT"; exit 1; }

ROOT="$HOME/constellation25/prior_art"
IPC="$HOME/c25_ipc/pending"
mkdir -p "$ROOT" "$IPC"

STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
PROOF="$ROOT/c25_prior_art_${STAMP}.txt"
HASH_FILE="$PROOF.sha256"

ARTIFACT_SHA="$(sha256sum "$ARTIFACT" | awk '{print $1}')"
MOD_TIME="$(stat -c '%y' "$ARTIFACT" 2>/dev/null || stat -f '%Sm' -t '%Y-%m-%dT%H:%M:%SZ' "$ARTIFACT")"

GIT_DATE="none"
if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  GIT_DATE="$(git log -1 --format=%cI -- "$ARTIFACT" 2>/dev/null || echo none)"
fi

{
  echo "CLAIMANT: CyGeL White"
  echo "TARGET_BUILD: DevCoreXOfficial/core-termux"
  echo "TARGET_ORIGINAL_PUBLIC_MARKER: 2023-12-06T19:55:00Z"
  echo "OBJECTIVE: $OBJECTIVE"
  echo "ARTIFACT_PATH: $ARTIFACT"
  echo "ARTIFACT_SHA256: $ARTIFACT_SHA"
  echo "LOCAL_FILE_MTIME: $MOD_TIME"
  echo "GIT_COMMIT_DATE: $GIT_DATE"
  echo "PROOF_CREATED_UTC: $(date -u +%FT%TZ)"
} > "$PROOF"

sha256sum "$PROOF" > "$HASH_FILE"

cat > "$IPC/saturn_prior_art.json" <<EOF
{
  "agent": "Saturn",
  "task": "Anchor this prior-art proof hash into SCAF Vault / Total Recall Ledger.",
  "proof_file": "$PROOF",
  "proof_sha256": "$(awk '{print $1}' "$HASH_FILE")",
  "priority": "critical"
}
EOF

cat > "$IPC/neptune_similarity.json" <<EOF
{
  "agent": "Neptune",
  "task": "Compare the artifact against DevCoreXOfficial/core-termux and produce a functional similarity report.",
  "artifact": "$ARTIFACT",
  "target_repo": "https://github.com/DevCoreXOfficial/core-termux",
  "priority": "high"
}
EOF

echo "Proof package created:"
cat "$PROOF"
echo
echo "SHA256:"
cat "$HASH_FILE"
echo
echo "Tasks routed to Saturn and Neptune."
