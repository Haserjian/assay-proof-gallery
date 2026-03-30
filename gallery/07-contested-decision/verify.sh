#!/usr/bin/env bash
# Verify the contested-decision specimen: good pack should PASS, tampered should FAIL.
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
python3 -m pip install assay-ai -q
cd "$SCRIPT_DIR"

echo ""
echo "=== Verifying signed evidence packet (authentic) ==="
echo ""
set +e
assay verify-pack ./proof_pack
GOOD_EXIT=$?
set -e

echo ""
echo "=== Verifying tampered packet (one byte changed) ==="
echo ""
set +e
assay verify-pack ./tampered_pack
BAD_EXIT=$?
set -e

echo ""
PASS=true
if [ $GOOD_EXIT -eq 0 ]; then
  echo "✓ Authentic pack: exit 0 (PASS) — evidence is intact"
else
  echo "✗ Authentic pack: unexpected exit $GOOD_EXIT (expected 0)"
  PASS=false
fi

if [ $BAD_EXIT -eq 2 ]; then
  echo "✓ Tampered pack: exit 2 (TAMPERED) — alteration detected"
else
  echo "✗ Tampered pack: unexpected exit $BAD_EXIT (expected 2)"
  PASS=false
fi

echo ""
if [ "$PASS" = true ]; then
  echo "Specimen verified: authentic evidence passes, tampered evidence fails."
  exit 0
else
  echo "Specimen verification FAILED."
  exit 1
fi
