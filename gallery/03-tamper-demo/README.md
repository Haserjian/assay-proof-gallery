# Scenario 03: DataCo Analytics — Tamper Detection

## Scenario

A DataCo analytics AI runs and produces a clean proof pack (exit 0). Someone
then modifies one byte in the receipt file — simulating what happens when an
operator tries to edit a receipt after the fact. The verifier catches it
immediately and returns exit 2.

## Buyer Question

> "What happens if someone on the vendor's side edits the evidence after the
> fact to make a failed run look clean?"

## Verdict

| Pack | Integrity | Exit |
|------|-----------|------|
| `good/` | **PASS** | `0` |
| `tampered/` | **FAIL** | `2` |

## What This Proves

- A single byte change to `receipt_pack.jsonl` causes a SHA-256 hash mismatch
  against the manifest
- The Ed25519 signature over the manifest was not updated (it can't be — the
  private key is not present at verify time)
- The verifier detects the mismatch and returns exit `2`, regardless of what
  the receipts claim
- The tamper is detectable offline, by anyone, with no access to the original
  system

## What This Does NOT Prove

- That the original signer key was secure
- That the clean pack's contents are correct or safe
- That this specific tamper scenario covers all possible tampering methods

## Run Locally

Verify the clean pack:

```bash
pip install assay-ai
assay verify-pack ./good
# Expected: exit 0 (PASS)
```

Verify the tampered pack:

```bash
assay verify-pack ./tampered
# Expected: exit 2 (INTEGRITY FAIL)
```

Or run the bundled script that checks both:

```bash
bash verify.sh
```

## Files in This Scenario

```
good/                       # Clean, signed proof pack
  pack_manifest.json
  pack_signature.sig
  receipt_pack.jsonl        # Original, unmodified
  verify_report.json
  verify_transcript.md

tampered/                   # Same pack, one byte changed in receipt_pack.jsonl
  pack_manifest.json        # Unchanged (signature still covers original hashes)
  pack_signature.sig        # Unchanged (private key not available to forger)
  receipt_pack.jsonl        # MODIFIED — one byte changed
  verify_report.json
  verify_transcript.md

SHA256SUMS.txt              # Checksums of both packs for reference
CHALLENGE.md                # Technical details of the tamper applied
```

## Why This Matters

The tamper demo makes the trust model concrete and auditable.

The claim is not "we use encryption." The claim is: *any third party can take
this pack, run one command, and confirm whether the bytes match the declared
hashes and the declared hashes match the signature.*

There is no vendor API call. There is no account login. There is no trust
required beyond the public key embedded in the manifest.

The exit code `2` is the system doing exactly what it says on the box.
