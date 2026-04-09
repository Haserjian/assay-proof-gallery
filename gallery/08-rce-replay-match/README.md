# 08 — RCE Replay Match

**Expected result:** MATCH (exit 0)

All recorded traces match receipt hashes under Tier A.
Evidence chain intact, claims hold.

## Verify

```bash
assay rce-verify . --out-dir ./replay_results
```
