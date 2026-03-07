#!/usr/bin/env bash
# Verify this proof pack locally. Expected result: INTEGRITY FAIL (tampered) (exit 2)
set -e
pip install assay-ai -q
echo ""
echo "Verifying tampered..."
echo ""
assay verify-pack ./tampered
EXIT=$?
echo ""
if [ $EXIT -eq 2 ]; then
  echo "✓ Got expected exit code 2 (INTEGRITY FAIL (tampered))"
else
  echo "✗ Unexpected exit code $EXIT (expected 2)"
  exit 1
fi
