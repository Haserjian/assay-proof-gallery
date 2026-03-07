#!/usr/bin/env bash
# Verify this proof pack locally. Expected result: HONEST FAIL (claims) (exit 1)
set -e
pip install assay-ai -q
echo ""
echo "Verifying proof_pack..."
echo ""
assay verify-pack ./proof_pack --require-claim-pass
EXIT=$?
echo ""
if [ $EXIT -eq 1 ]; then
  echo "✓ Got expected exit code 1 (HONEST FAIL (claims))"
else
  echo "✗ Unexpected exit code $EXIT (expected 1)"
  exit 1
fi
