#!/usr/bin/env bash
# Verify this proof pack locally. Expected result: HONEST FAIL (claims) (exit 1)
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
python3 -m pip install assay-ai -q
echo ""
echo "Verifying proof_pack..."
echo ""
set +e
cd "$SCRIPT_DIR"
assay verify-pack ./proof_pack --require-claim-pass
EXIT=$?
set -e
echo ""
if [ $EXIT -eq 1 ]; then
  echo "✓ Got expected exit code 1 (HONEST FAIL (claims))"
else
  echo "✗ Unexpected exit code $EXIT (expected 1)"
  exit 1
fi
