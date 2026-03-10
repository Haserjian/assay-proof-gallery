# Proof Pack Summary

**Pack ID:** `pack_20260307T060831_1de9465d`
**Run ID:** `trace_20260307T060831_9f640976`
**Signed by:** `ci-assay-signer`

## Verdicts

| Check | Result |
|-------|--------|
| Integrity | **PASS** |
| Claims | **PASSED** |

## What Happened

- **5 receipts** recorded: 1 capability_use, 1 guardian_verdict, 3 model_call
- **Providers:** anthropic
- **Models:** claude-sonnet-4-20250514
- **Total tokens:** 3,934
- **Time window:** 2026-03-07T06:08:31.483376+00:00 to 2026-03-07T06:08:31.483772+00:00

## Integrity Check

All file hashes match. The Ed25519 signature is valid.
This evidence has not been tampered with since creation.

## Claim Checks

| Claim | Result |
|-------|--------|
| `minimum_receipt_coverage` | **PASS** |

## What This Proves

- The recorded evidence is authentic (signed, hash-verified)
- All declared behavioral checks passed

## What This Does NOT Prove

- That every action was recorded (only recorded actions are in the pack)
- That model outputs are correct or safe
- That receipts were honestly created (tamper-evidence, not source attestation)
- That timestamps are externally anchored (local clock was used)
- That the signer key was not compromised

## Verify Independently

```bash
python3 -m pip install assay-ai && assay verify-pack ./gallery/01-fintech-pass/proof_pack
```
