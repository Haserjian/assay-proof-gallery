#!/usr/bin/env bash
# Verify this RCE episode pack. Expected: INTEGRITY_FAIL (exit 2)
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
echo "Verifying RCE episode pack..."
set +e
cd "$SCRIPT_DIR"
assay rce-verify . --out-dir ./replay_results --overwrite
EXIT=$?
set -e
echo ""
if [ $EXIT -eq 2 ]; then
  echo "Got expected exit code 2 (INTEGRITY_FAIL)"
else
  echo "Unexpected exit code $EXIT (expected 2)"
  exit 1
fi
