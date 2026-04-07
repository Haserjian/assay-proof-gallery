# 10 — RCE Tampered Replay

**Expected result:** INTEGRITY_FAIL — TAMPERED (exit 2)

The episode_open receipt's inputs_hash was tampered.
Verifier detects mismatch in Phase 3 before replay comparison.
Verdict: INTEGRITY_FAIL (receipt_integrity: FAIL, claim_check: null).

## Verify

```bash
assay rce-verify . --out-dir ./replay_results
```
