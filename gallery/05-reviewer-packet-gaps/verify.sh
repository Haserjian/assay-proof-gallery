#!/usr/bin/env bash
set -euo pipefail

echo "Reviewer packet verdict"
assay reviewer verify ./reviewer_packet

echo
echo "Nested proof-pack verdict"
assay verify-pack ./reviewer_packet/proof_pack
