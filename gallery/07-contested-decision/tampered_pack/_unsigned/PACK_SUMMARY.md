# Proof Pack Summary

**Pack ID:** `pack_20260330T210728_9710cb47`
**Run ID:** `trace_20260330T210728_7a38b8e2`
**Signed by:** `assay-local`

## Verdicts

| Check | Result |
|-------|--------|
| Integrity | **PASS** |
| Claims | **PASSED** |

## What Happened

- **3 receipts** recorded: 1 capability_use, 1 guardian_verdict, 1 model_call
- **Providers:** anthropic
- **Models:** claude-sonnet-4-20250514
- **Total tokens:** 3,102
- **Time window:** 2026-03-30T21:07:28.735150+00:00 to 2026-03-30T21:07:28.735688+00:00

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
python3 -m pip install assay-ai && assay verify-pack /var/folders/5z/vxkrcf690tlf71r_6dnzkx1h0000gn/T/tmpehv4z9ux/.assay_pack_staging_kc30ibq1
```
