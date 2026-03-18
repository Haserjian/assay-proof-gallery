# Gallery Vocabulary

This gallery demonstrates Assay verification outcomes using real artifacts.
The vocabulary here follows the [Canonical Evidence Semantics Matrix](https://github.com/Haserjian/assay/blob/main/docs/CANONICAL_EVIDENCE_SEMANTICS_MATRIX.md).

## What verification proves

| Term | Meaning | What it does NOT mean |
|------|---------|----------------------|
| **verified** | Cryptographic integrity check passed (hashes + signature match) | Not "approved," "trusted," or "accepted" |
| **honest fail** | Evidence is intact but declared behavioral claims did not pass | Not tool failure; not tamper; the system is working correctly |
| **tampered** | Evidence bytes were altered after signing; integrity is broken | Not a claim failure; the evidence itself cannot be trusted |
| **proof pack** | A signed, verifiable bundle of receipts with attestation | Not a safety certificate; not a guarantee of correct AI behavior |

## What verification does NOT prove

A passing verification proves the evidence was not altered. It does not prove:
- The evidence was honestly created in the first place
- The AI system is "safe" in any universal sense
- Timestamps are from a trusted source
- The signer is authorized for any particular purpose

Those are separate concerns handled by the [trust evaluation layer](https://github.com/Haserjian/assay/blob/main/docs/TRUST_POLICY_CONSTITUTION.md).

## Gallery exit codes

| Exit | Verdict | Plane | What happened |
|------|---------|-------|---------------|
| `0` | PASS | Verification | Integrity intact, all declared claims pass |
| `1` | HONEST_FAIL | Verification | Integrity intact, behavioral claims failed — sealed, cannot be rewritten |
| `2` | TAMPERED | Verification | Evidence bytes altered after signing — integrity broken |

Exit 1 is **not tool failure**. It is the tool working correctly to report that
the AI system did not meet its own declared standards.

## Terms NOT used in this gallery

These words have specific meanings elsewhere in the Assay ecosystem and are
intentionally not used loosely in gallery descriptions:

| Avoided term | Why | Use instead |
|-------------|-----|-------------|
| "trusted" | Implies acceptance for a purpose | "verified" (integrity checked) |
| "approved" | Implies governance decision | "passed" (claims satisfied) |
| "safe" | Implies universal judgment | "integrity intact" or "claims passed" |
| "certified" | Implies authority endorsement | "signed and verifiable" |
| "valid" (alone) | Ambiguous — structure? signature? claims? | Be specific: "signature valid," "claims passed" |

## Relationship to trust evaluation

Verification and trust are separate layers:
- **Verification** (this gallery): "Is the evidence intact?"
- **Trust** (not demonstrated here yet): "Is the signer authorized? Is this acceptable for my target?"

A future gallery scenario may demonstrate trust rejection (exit 0 from
verification, but rejected by trust policy for a specific target).
