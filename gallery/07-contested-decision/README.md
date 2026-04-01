# Scenario 07: Contested Vendor Decision

## Buyer question

> When a vendor disputes an AI-assisted procurement decision, can you show
> exactly what happened at decision time — and can the vendor verify it
> independently?

## The difference

Without a signed decision record, the team reconstructs from Slack, email,
dashboards, and memory. That takes hours and still ends with caveats.

With a signed decision packet, the team opens the packet, verifies it, and
forwards a record the vendor can check offline.

**Path A reconstructs. Path B verifies.**

## Verdict

| Check | Result |
|-------|--------|
| Integrity | **PASS** |
| Claims | **PASS** |
| Verifier exit code | `0` |

## What this packet proves

### 1. Integrity proof

The packet has not been altered since signing.
- Manifest hashes match
- Ed25519 signature verifies
- Changing any byte causes verification failure (see `tampered_pack/`)

### 2. Execution proof

This evaluation run occurred as recorded.
- Timestamp sealed at execution time
- Task: `vendor_proposal_evaluation`
- Model: `claude-sonnet-4-20250514` via Anthropic
- Token counts: 3102 (2580 in, 522 out)
- Output: `/output/vendor_decision.json`, authorized

### 3. Governance proof

The recorded policy gate allowed the action under declared scope at runtime.
- Policy gate: `procurement_policy_gate`
- Policy: `vendor_scoring_rubric` v2.1
- Policy digest: `sha256:a4f1c9e2...`
- Verdict: allow
- Risk score: 0.12
- Scope: "Evaluation within declared procurement scope, no PII in proposals"

## What this packet does NOT prove

- That every action in the system was recorded (only recorded actions are in the pack)
- That the vendor proposals were authentic or unmodified in the real world
- That the model's recommendation was correct, fair, or unbiased
- That this was the only evaluation ever run
- That the signer key was never compromised
- That timestamps were externally anchored (local clock was used)
- That upstream business inputs were true, unless those inputs were themselves authenticated

It proves what was recorded and signed at execution time, not the real-world
truth of upstream inputs.

## Trust boundary

| Role (RATS) | In this scenario |
|---|---|
| **Attester** | The instrumented evaluation system (`assay-local` signer) |
| **Verifier** | `assay verify-pack` CLI or [browser verifier](https://haserjian.github.io/assay-proof-gallery/verify.html) |
| **Relying Party** | The disputing vendor, auditor, or reviewer |

| | |
|---|---|
| **Signed by** | `assay-local` (operator-held key) |
| **Trust assumption** | Attester faithfully recorded the episode at execution time |
| **Topology** | Passport Model — the signed packet travels with the decision |
| **Not covered unless separately authenticated** | Upstream documents, real-world facts, input authenticity |

## "How do I know this wasn't assembled later?"

The signed manifest contains SHA-256 hashes of every file in the pack. The
Ed25519 signature covers the manifest. If any byte in any file changes after
signing, verification fails. The tampered pack in this scenario demonstrates
exactly that: one byte changed, verification returns exit 2 with
`E_MANIFEST_TAMPER`.

## Run locally

```bash
pip install assay-ai

# Verify the authentic decision packet
assay verify-pack ./proof_pack
# Expected: exit 0 (PASS)

# Verify the tampered packet (one byte changed)
assay verify-pack ./tampered_pack
# Expected: exit 2 (TAMPERED — integrity failure)
```

Or run the bundled script:

```bash
bash verify.sh
```

> **Note on signer-not-pinned warning:** Demo packs show a
> `Signature valid for supplied key material; signer identity not pinned`
> advisory. This means the signature is cryptographically valid but the
> verifier has not been told to trust only one specific key. In production,
> use `assay lock init` to pin the signer identity — pinned verification
> removes the advisory and adds explicit key-trust enforcement.

## Files in this scenario

```
proof_pack/                 Signed decision packet
  pack_manifest.json        SHA-256 hashes + Ed25519 signature
  pack_signature.sig        Raw signature bytes
  receipt_pack.jsonl        3 receipts from the evaluation run
  verify_report.json        Machine-readable verification result
  verify_transcript.md      Human-readable verification transcript

tampered_pack/              Copy with one byte altered — exits 2
  (same files)

dispute_packet.md           Before vs after reconstruction comparison
verify.sh                   Verifies both packs, confirms expected exit codes
```

## Why this matters

Most teams record what the system says about itself — logs, dashboards,
event streams. When a decision is disputed, they reconstruct from those
sources. The reconstruction takes hours and ends with a caveat.

A signed decision packet is different. The execution record was sealed at
runtime. The disputing party can verify it offline without trusting the
operator.

The question is not "do you have logs?"
The question is: "can the other party verify what happened without trusting you?"

**See [`dispute_packet.md`](dispute_packet.md) for the full side-by-side.**
