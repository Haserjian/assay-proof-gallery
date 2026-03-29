#!/usr/bin/env bash
# Verify this proof pack locally. Expected result: INTEGRITY FAIL (tampered) (exit 2)
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
python3 -m pip install assay-ai -q
echo ""
echo "Verifying tampered..."
echo ""
set +e
cd "$SCRIPT_DIR"
assay verify-pack ./tampered
EXIT=$?
set -e
echo ""
if [ $EXIT -eq 2 ]; then
  echo "✓ Got expected exit code 2 (INTEGRITY FAIL (tampered))"
else
  echo "✗ Unexpected exit code $EXIT (expected 2)"
  exit 1
fi
