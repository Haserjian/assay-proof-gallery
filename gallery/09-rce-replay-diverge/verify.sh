#!/usr/bin/env bash
# Verify this RCE episode pack. Expected: DIVERGE (exit 1)
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
echo "Verifying RCE episode pack..."
set +e
cd "$SCRIPT_DIR"
assay rce-verify . --out-dir ./replay_results --overwrite
EXIT=$?
set -e
echo ""
if [ $EXIT -eq 1 ]; then
  echo "Got expected exit code 1 (DIVERGE)"
else
  echo "Unexpected exit code $EXIT (expected 1)"
  exit 1
fi
