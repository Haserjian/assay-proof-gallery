# Reviewer Packet Manual QA Checklist

Use `gallery/05-reviewer-packet-gaps/reviewer_packet/` as the base artifact for
browser and CLI verification checks.

## 1. Valid Reviewer Packet

- Open the browser verifier and load the reviewer packet sample
- Expected:
  - reviewer verdict is `VERIFIED_WITH_GAPS`
  - nested proof pack verifies
  - coverage summary includes `EVIDENCED`, `PARTIAL`, and `OUT_OF_SCOPE`

## 2. Packet-Layer Tamper

- Copy the sample packet to a scratch directory
- Edit `COVERAGE_MATRIX.md` or `SETTLEMENT.json` without updating `PACKET_MANIFEST.json`
- Expected:
  - reviewer verdict becomes `TAMPERED`
  - failure reason points to packet-layer tamper

## 3. Nested Proof-Pack Tamper

- Copy the sample packet to a scratch directory
- Edit `proof_pack/receipt_pack.jsonl`
- Expected:
  - nested proof pack verification fails
  - reviewer verdict becomes `TAMPERED`

## 4. Stale Packet

- Copy the sample packet to a scratch directory
- Set `SETTLEMENT.json.generated_at` to an old timestamp beyond `valid_for`
- Update `PACKET_MANIFEST.json` so its attested hashes match the edited packet
- Expected:
  - reviewer verifier reports `freshness_state: STALE`
  - settlement stays authentic but no longer appears fresh

## 5. Unsigned Packet Manifest Warning

- Verify the unmodified sample packet
- Expected:
  - packet verification succeeds
  - warning mentions that `PACKET_MANIFEST.json` is unsigned and only hash-checked
