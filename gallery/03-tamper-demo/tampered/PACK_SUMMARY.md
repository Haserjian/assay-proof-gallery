# Proof Pack Summary

**Pack ID:** `pack_20260307T060838_e3df25c7`
**Run ID:** `challenge-run`
**Signed by:** `challenge`

## Verdicts

| Check | Result |
|-------|--------|
| Integrity | **PASS** |
| Claims | **PASSED** |

## What Happened

- **3 receipts** recorded: 1 guardian_verdict, 2 model_call
- **Providers:** openai
- **Models:** gpt-4
- **Total tokens:** 4,400
- **Time window:** 2026-02-10T12:00:00Z to 2026-02-10T12:00:02Z

## Integrity Check

All file hashes match. The Ed25519 signature is valid.
This evidence has not been tampered with since creation.

## Claim Checks

| Claim | Result |
|-------|--------|
| `has_model_calls` | **PASS** |
| `guardian_enforced` | **PASS** |

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
python3 -m pip install assay-ai && assay verify-pack /var/folders/f6/qdgmkgd166j03b200mvl854c0000gn/T/tmprt218k_w/good
```
