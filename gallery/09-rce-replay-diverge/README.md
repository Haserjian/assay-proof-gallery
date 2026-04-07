# 09 — RCE Replay Divergence

**Expected result:** DIVERGE — HONEST FAIL (exit 1)

Recorded traces for s02 and s03 differ from original receipts.
Evidence intact (receipt_integrity: PASS), but replay comparison
finds hash mismatches (claim_check: FAIL). Dispute payload
identifies divergent steps.

## Verify

```bash
assay rce-verify . --out-dir ./replay_results
```
