# Scenario 01: FintechCo Loan Approval — PASS

## Scenario

A loan approval AI runs in production. The compliance team needs to demonstrate
that every decision cycle is covered by tamper-evident evidence before passing
an AI governance questionnaire.

## Buyer Question

> "Can you show us machine-verifiable evidence that your AI system's decisions
> are recorded and auditable — not just logs we have to trust you didn't edit?"

## Verdict

| Check | Result |
|-------|--------|
| Integrity | **PASS** |
| Claims | **PASS** |
| Verifier exit code | `0` |

## What This Proves

- 5 receipts were recorded during the run: 3 model calls, 1 guardian verdict, 1 capability use
- The receipt pack is signed with Ed25519 and all file hashes are verified
- The declared coverage claim passes: the recorded evidence meets the declared standard
- This evidence cannot be altered without breaking the signature

## What This Does NOT Prove

- That every action was recorded (only recorded actions are in the pack)
- That model outputs are correct or safe
- That the signer key was not compromised
- That timestamps are externally anchored (local clock was used)

## Run Locally

```bash
pip install assay-ai
assay verify-pack ./proof_pack
# Expected: exit 0 (PASS)
```

Or run the bundled script:

```bash
bash verify.sh
```

## Files in This Pack

```
proof_pack/
  pack_manifest.json      # SHA-256 hashes of all pack files + Ed25519 signature
  pack_signature.sig      # Raw Ed25519 signature bytes
  receipt_pack.jsonl      # Tamper-evident receipt chain (one receipt per line)
  verify_report.json      # Machine-readable verification result
  verify_transcript.md    # Human-readable verification transcript
```

## Ledger Anchor

This pack's fingerprint is recorded in the Assay public ledger with `witness_status: signature_verified`.

```
pack_root_sha256: 2226d98e2bc2b2f93337aaf82165eb8a4089abd97533971f5d28da34693445cb
```

Verify independently: https://haserjian.github.io/assay-ledger/

Search the ledger for the fingerprint above. The entry records the pack identity,
receipt count, and integrity result at submission time — separate from this repo.

## Why This Matters

A proof pack is not a report. A report is generated after the fact by the vendor.
A proof pack is sealed at execution time: the receipts are written as the agent
runs, then signed before the process exits. Editing the receipts after signing
breaks the signature. Editing the signature breaks the manifest hash. There is
no path to a forged passing result.

This is the answer to: *"How do we know you didn't just write a nice summary?"*
