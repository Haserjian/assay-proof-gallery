#!/usr/bin/env bash
# Customer-data boundary crash test.
#
# Verifies one of two packets and prints a structured report:
#   ./verify.sh authentic   -> expected exit 0 (PASS)
#   ./verify.sh tampered    -> expected exit 1 (FAIL on v2 source binding)
#
# Defaults to authentic when no arg is given.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PACKET="${1:-authentic}"

case "$PACKET" in
  authentic|tampered) ;;
  *)
    echo "usage: $0 [authentic|tampered]" >&2
    exit 2
    ;;
esac

PACK_DIR="$SCRIPT_DIR/$PACKET/proof_pack"
if [ ! -d "$PACK_DIR" ]; then
  echo "error: pack directory not found: $PACK_DIR" >&2
  exit 2
fi

# Ensure assay-ai (v1 5-file kernel verifier) is available.
if ! command -v assay >/dev/null 2>&1; then
  python3 -m pip install --quiet assay-ai
fi

exec python3 "$SCRIPT_DIR/_verify_helper.py" --pack "$PACK_DIR" --label "$PACKET"
