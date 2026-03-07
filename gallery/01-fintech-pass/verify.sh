#!/usr/bin/env bash
# Verify this proof pack locally. Expected result: PASS (exit 0)
set -e
pip install assay-ai -q
echo ""
echo "Verifying proof_pack..."
echo ""
assay verify-pack ./proof_pack
EXIT=$?
echo ""
if [ $EXIT -eq 0 ]; then
  echo "✓ Got expected exit code 0 (PASS)"
else
  echo "✗ Unexpected exit code $EXIT (expected 0)"
  exit 1
fi
