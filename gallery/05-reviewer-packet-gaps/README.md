# Scenario 05: AcmeSaaS Support Workflow Reviewer Packet — VERIFIED WITH GAPS

## Scenario

This sample shows the buyer-facing Reviewer Packet layer on top of a signed
Assay proof pack. The nested proof pack verifies cleanly, but the packet
settlement remains `VERIFIED_WITH_GAPS` because one declared workflow boundary
is only partially covered.

## Buyer Question

> "Can you hand us one artifact we can forward internally, verify ourselves,
> and use to see what is in scope, what is covered, and what gaps remain?"

## Verdict

| Layer | Result |
|------|--------|
| Reviewer Packet | `VERIFIED_WITH_GAPS` |
| Nested proof pack integrity | **PASS** |
| Nested proof pack claims | **PASS** |

## What This Proves

- The packet wraps a real signed proof pack another reviewer can verify offline
- Scope, coverage, freshness, and settlement are explicit at the packet layer
- The packet is still useful even when coverage is partial
- The reviewer can challenge both the packet layer and the nested proof pack

## What This Does NOT Prove

- That the packet establishes legal or regulatory compliance
- That every production path is covered
- That the unsigned packet manifest has cryptographic attestation
- That the nested proof pack signer key was not compromised

## Run Locally

```bash
pip install assay-ai
assay reviewer verify ./reviewer_packet
# Expected: VERIFIED_WITH_GAPS with an unsigned packet-manifest warning
```

Verify the nested proof pack directly:

```bash
assay verify-pack ./reviewer_packet/proof_pack
# Expected: exit 0 (PASS)
```

Or run the bundled script:

```bash
bash verify.sh
```

## Files in This Scenario

```
reviewer_packet/
  SETTLEMENT.json
  SCOPE_MANIFEST.json
  COVERAGE_MATRIX.md
  REVIEWER_GUIDE.md
  EXECUTIVE_SUMMARY.md
  VERIFY.md
  CHALLENGE.md
  PACKET_INPUTS.json
  PACKET_MANIFEST.json      # Hash inventory for packet-layer files
  proof_pack/
    pack_manifest.json
    pack_signature.sig
    receipt_pack.jsonl
    verify_report.json
    verify_transcript.md
    PACK_SUMMARY.md
```

## Why This Matters

The proof pack is the trust kernel. The Reviewer Packet is the thing another
team can actually use. This sample shows the handoff artifact: useful,
challengeable, and explicit about its remaining gaps.
