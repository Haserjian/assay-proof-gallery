# Scenario 06 — NAIC AISET Mapping

A reviewer packet compiled against the NAIC AI Systems Evaluation Tool (AISET)
question structure. This is the first vertical mapping: insurance-specific
questionnaire answers backed by proof-pack evidence.

## What this demonstrates

The AISET is a 4-part questionnaire being piloted by the NAIC for insurance
market conduct examinations:

1. **AI Use** — Quantifying AI adoption and deployment scope
2. **Governance & Risk** — Governance structure, risk management, oversight
3. **High-Risk Model Details** — Model documentation for high-risk use cases
4. **Model & Data Details** — Data provenance, training, validation

This packet maps 14 AISET-aligned questions to proof-pack evidence.

## Coverage breakdown

| Status | Count | Meaning |
|--------|-------|---------|
| EVIDENCED | 8 | Machine-provable from the signed proof pack |
| PARTIAL | 1 | Instrumentation coverage is 5/6 (boundary-declared) |
| HUMAN_ATTESTED | 3 | Organizational policy — requires human documentation |
| OUT_OF_SCOPE | 2 | Training data provenance, legal compliance |

**Settlement: `VERIFIED_WITH_GAPS`** — The packet is authentic and useful, but
some coverage remains partial or human-attested.

## Verify

```bash
# Verify the nested proof pack
assay verify-pack ./reviewer_packet/proof_pack

# Or verify the full reviewer packet
assay reviewer verify ./reviewer_packet
```

## What this is NOT

- Not a claim of NAIC compliance
- Not a substitute for legal counsel
- Not an official NAIC product or endorsement
- Not a promise that every AISET question can be machine-proven

It is a way to say: here is what we can prove from signed evidence, here is
what is partial, here is what is out of scope, and here is what still requires
human attestation.
