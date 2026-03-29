#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
python3 -m pip install assay-ai -q

echo "Reviewer packet verdict"
cd "$SCRIPT_DIR"
PACKET_JSON=$(assay reviewer verify ./reviewer_packet --json)
export PACKET_JSON
export EXPECTED_SETTLEMENT="VERIFIED_WITH_GAPS"
python3 - <<'PY'
import json
import os
import sys

payload = json.loads(os.environ["PACKET_JSON"])
expected = os.environ["EXPECTED_SETTLEMENT"]
actual = payload.get("settlement_state")
if actual != expected:
    print(f"Unexpected settlement: {actual} (expected {expected})", file=sys.stderr)
    sys.exit(1)
print(f"✓ Got expected settlement {actual}")
PY

echo
echo "Nested proof-pack verdict"
assay verify-pack ./reviewer_packet/proof_pack
