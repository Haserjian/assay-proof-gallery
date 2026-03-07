# Proof Pack Summary

**Pack ID:** `pack_20260307T060837_0fa00c86`
**Run ID:** `trace_20260307T060837_d020f6ca`
**Signed by:** `ci-assay-signer`

## Verdicts

| Check | Result |
|-------|--------|
| Integrity | **PASS** |
| Claims | **FAILED** |

> **Honest failure**: the evidence is authentic (not tampered with),
> and it proves this run violated the declared standards.

## What Happened

- **3 receipts** recorded: 1 guardian_verdict, 2 model_call
- **Providers:** anthropic
- **Models:** claude-sonnet-4-20250514
- **Total tokens:** 2,567
- **Time window:** 2026-03-07T06:08:37.721090+00:00 to 2026-03-07T06:08:37.721796+00:00

## Integrity Check

All file hashes match. The Ed25519 signature is valid.
This evidence has not been tampered with since creation.

## Claim Checks

| Claim | Result |
|-------|--------|
| `minimum_receipt_coverage` | **FAIL** |

## What This Proves

- The recorded evidence is authentic (signed, hash-verified)
- Some declared behavioral checks failed (see above)
- This is an honest failure: authentic evidence of a standards violation

## What This Does NOT Prove

- That every action was recorded (only recorded actions are in the pack)
- That model outputs are correct or safe
- That receipts were honestly created (tamper-evidence, not source attestation)
- That timestamps are externally anchored (local clock was used)
- That the signer key was not compromised

## Verify Independently

```bash
python3 -m pip install assay-ai && assay verify-pack /Users/timmybhaserjian/assay-proof-gallery/gallery/02-insurance-honest-fail/proof_pack
```
