#!/usr/bin/env bash
set -euo pipefail

# Sync canonical verifier bundle from assay-verify-ts
SOURCE_REPO="Haserjian/assay-verify-ts"
SOURCE_DIR="${ASSAY_VERIFY_TS_DIR:-$HOME/assay-verify-ts}"
BUNDLE_SRC="$SOURCE_DIR/browser/assay-verify.js"
BUNDLE_DST="docs/assay-verify.js"
PROVENANCE_DST="docs/VERIFIER_PROVENANCE.json"

if [ ! -f "$BUNDLE_SRC" ]; then
  echo "ERROR: canonical bundle not found at $BUNDLE_SRC"
  echo "Run 'npm run build:browser' in assay-verify-ts first."
  exit 1
fi

# Copy bundle
cp "$BUNDLE_SRC" "$BUNDLE_DST"

# Compute provenance
BUNDLE_SHA256=$(shasum -a 256 "$BUNDLE_DST" | cut -d' ' -f1)
SOURCE_COMMIT=$(git -C "$SOURCE_DIR" rev-parse HEAD)
SYNCED_AT=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

cat > "$PROVENANCE_DST" << EOF
{
  "source_repo": "$SOURCE_REPO",
  "source_commit": "$SOURCE_COMMIT",
  "bundle_sha256": "$BUNDLE_SHA256",
  "synced_at": "$SYNCED_AT",
  "contract_version": "Assay JCS Profile v1"
}
EOF

echo "Vendored: $BUNDLE_SRC → $BUNDLE_DST"
echo "SHA-256:  $BUNDLE_SHA256"
echo "Commit:   $SOURCE_COMMIT"
echo "Wrote:    $PROVENANCE_DST"
