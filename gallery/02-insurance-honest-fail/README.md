# Scenario 02: InsuranceTech Claims Review — HONEST FAIL

## Scenario

An insurance claims review AI runs three times. The compliance team previously
declared that a full claims audit requires 10 or more receipts per run. This run
recorded only 3. The evidence is authentic — and it proves the system violated
its own declared standard.

## Buyer Question

> "If your AI system fails to meet a declared governance standard, does the
> evidence show an honest failure — or can it be hidden or rewritten?"

## Verdict

| Check | Result |
|-------|--------|
| Integrity | **PASS** |
| Claims | **FAIL** |
| Verifier exit code | `1` |

Exit code `1` means: *the pack is authentic, and it proves a standards violation.*
This is not an error. This is the system working correctly.

## What This Proves

- The receipt pack is intact: signature valid, all hashes match, no tampering
- The declared coverage claim (`minimum_receipt_coverage`) failed: 3 receipts
  were recorded, 10 were required
- This failure is sealed into the pack at runtime. It cannot be edited without
  breaking the signature
- An auditor can verify this result independently, offline, without trusting the vendor

## What This Does NOT Prove

- That the AI system was behaving maliciously (the shortfall may be a workflow gap)
- That every action was recorded (only recorded actions are in the pack)
- That timestamps are externally anchored (local clock was used)
- That the signer key was not compromised

## Run Locally

```bash
pip install assay-ai
assay verify-pack ./proof_pack --require-claim-pass
# Expected: exit 1 (integrity PASS, claims FAIL)
```

The `--require-claim-pass` flag enforces that a claims failure returns a
non-zero exit code, making the result usable in CI gates.

Or run the bundled script:

```bash
bash verify.sh
```

## Files in This Pack

```
proof_pack/
  pack_manifest.json      # SHA-256 hashes of all pack files + Ed25519 signature
  pack_signature.sig      # Raw Ed25519 signature bytes
  receipt_pack.jsonl      # 3 receipts: 2 model_call, 1 guardian_verdict
  verify_report.json      # Machine-readable result (claim_check: FAIL)
  verify_transcript.md    # Human-readable transcript
```

## Ledger Anchor

This pack's fingerprint is recorded in the Assay public ledger with `witness_status: signature_verified`.
The entry confirms `claim_check: FAIL` — honest failure is a first-class ledger outcome.

```
pack_root_sha256: d2dfa04aed0697cfb038fc92d7f517f9c4f2264bb131898b9aafeaddcd4d2195
```

Verify independently: https://haserjian.github.io/assay-ledger/

The ledger records that this pack was witnessed with a verified Ed25519 signature,
integrity PASS, and claims FAIL — at a specific point in time, outside this repo.

## Why This Matters

The distinction between exit `1` and exit `2` is the trust model in one line:

- **Exit 1**: *The evidence is real. It shows a real failure. The failure cannot be hidden.*
- **Exit 2**: *The evidence was altered. Something tried to cover a failure.*

An observability tool can tell you what happened. Only a tamper-evident record
can prove to an external reviewer that the failure was real and unedited.

This scenario is the one procurement teams and auditors find most compelling:
it shows the system being honest about itself, without vendor intervention.
