# NAIC AISET: What the Evidence Proves

A buyer-readable map from AISET questions to proof-pack evidence.

---

## Part 1: AI Use

| Question | Status | What answers it |
|----------|--------|-----------------|
| Does the system use AI/ML? | **EVIDENCED** | Proof pack contains receipts from an AI workflow execution. If receipts exist, AI is in use. |
| Are model calls documented? | **EVIDENCED** | Each receipt in `receipt_pack.jsonl` records the model called, arguments, response, latency, and timestamp. |
| What is instrumentation coverage? | **PARTIAL** | The boundary declares 6 call sites identified, 5 instrumented. Coverage ratio is explicit. |

## Part 2: Governance & Risk

| Question | Status | What answers it |
|----------|--------|-----------------|
| Is there a governance framework? | **HUMAN_ATTESTED** | Organizational fact — requires your documentation. Assay records runtime controls but not board governance. |
| Are runtime controls applied? | **EVIDENCED** | `claim_verification.passed` in the verify report proves controls ran and their outcomes were recorded. |
| Is there an independent audit trail? | **EVIDENCED** | The proof pack itself is the audit trail — signed, hash-chained, verifiable offline by anyone. |
| Can evidence be verified offline? | **EVIDENCED** | No server access needed. Ed25519 signature + SHA-256 hashes. Run `assay verify-pack` on your own machine. |
| Is tamper detection in place? | **EVIDENCED** | Core Assay property. Change one byte after signing → verification fails. JCS canonicalization prevents reordering attacks. |

## Part 3: High-Risk Model Details

| Question | Status | What answers it |
|----------|--------|-----------------|
| Is model identity recorded? | **EVIDENCED** | Each model call receipt includes model name, version, and provider. |
| Are risk classifications documented? | **HUMAN_ATTESTED** | Risk classification is organizational judgment. Assay records which models were used, not their risk tier. |
| Is there model validation evidence? | **EVIDENCED** | `claim_check` in the attestation records whether declared behavioral standards passed or failed at runtime. |

## Part 4: Model & Data Details

| Question | Status | What answers it |
|----------|--------|-----------------|
| Is training data provenance documented? | **OUT OF SCOPE** | Training data is pre-deployment. Assay covers post-deployment runtime evidence. |
| Are data retention policies in place? | **HUMAN_ATTESTED** | Organizational policy. Assay records what was processed but does not enforce retention schedules. |
| Does this establish legal compliance? | **OUT OF SCOPE** | This packet provides evidence, not legal conclusions. Compliance requires legal counsel. |

---

## Summary

| Status | Count | Meaning |
|--------|-------|---------|
| EVIDENCED | 8 | Machine-provable from the signed proof pack |
| PARTIAL | 1 | Declared coverage ratio is less than 100% |
| HUMAN_ATTESTED | 3 | Organizational fact — requires human documentation |
| OUT_OF_SCOPE | 2 | Pre-deployment or legal — outside runtime evidence |

**Settlement: `VERIFIED_WITH_GAPS`**

The packet is authentic and useful. Some questions require human documentation or are outside runtime evidence scope. The boundary between machine-proven and human-attested is explicit.

---

## Reproduce this packet

```bash
pip install assay-ai
git clone https://github.com/Haserjian/assay-proof-gallery

# Compile the NAIC AISET reviewer packet
assay vendorq export-reviewer \
  --proof-pack ./assay-proof-gallery/gallery/01-fintech-pass/proof_pack \
  --boundary ./boundary.json \
  --mapping ./assay-toolkit/src/assay/mappings/naic_aiset/question_mapping.json \
  --out ./my_aiset_packet

# Verify the nested proof pack
assay verify-pack ./my_aiset_packet/proof_pack

# Read the coverage matrix
cat ./my_aiset_packet/COVERAGE_MATRIX.md
```
