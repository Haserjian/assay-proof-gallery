# Customer-Data Boundary Crash Test

A support-agent workflow has a declared customer-data boundary: it may read account ID, account status, and subscription tier; it may not touch payment method, SSN, or full billing history. Two packets are shipped. One is authentic. One has been tampered with after emission. Verification catches the tamper, names the broken source binding, and tells you exactly which receipt line drifted.

## Run the crash test

```bash
cd gallery/customer-data-boundary-crash-test
./verify.sh authentic    # expected exit code: 0
./verify.sh tampered     # expected exit code: 1
```

Requires `python3` and `pip`. The script installs `assay-ai` automatically if it is not already on PATH. No knowledge of any other Assay constellation component is required.

## Authentic packet — expected output

```
crash test: authentic

[1/4] packet root: PASS
[2/4] receipt lineage: PASS
[3/4] v2 source bindings: PASS
[4/4] observed boundary claim: PASS
      boundary 'support_agent.customer_account_data.v1', 3 tool calls in scope

OVERALL: PASS
```

## Tampered packet — expected output

```
crash test: tampered

[1/4] packet root: FAIL
      `assay verify-pack` exited 2 — v1 5-file kernel detected mismatch
[2/4] receipt lineage: PASS
[3/4] FAIL v2 source binding mismatch
    source_index: 3
    expected: 3277950d28710a0c7cf0f59cb5012c649dffd7081b32d93187818d280be49881
    actual:   7a244f6abcf3cff4d43847056bbdd89f45afec74826afb98b1bcc3edfe5ff87b
[4/4] observed boundary claim: FAIL
      mcp_tool_call r_tool_call_002 accessed forbidden data class 'customer_payment_method' (boundary 'support_agent.customer_account_data.v1')

OVERALL: FAIL
```

The `tampered/` packet is byte-identical to `authentic/` except for one line in `receipt_pack.jsonl` — overwritten in place after emission. The pack manifest, the pack-level signature, and the v2 sidecar are not regenerated. That is the post-emission tamper a portable verifier has to catch.

## What this proves

- The bound packet evidence surface was unchanged in the authentic packet.
- The observed tool-call receipts match the declared boundary policy.
- The tampered packet was altered after emission.
- The verifier can identify the broken source binding (source_index, expected hash, actual hash).

## What this does not prove

- The model's answer was factually correct.
- The system is generally safe.
- Legal or compliance approval is automatic.
- Unobserved actions did not occur outside the captured surface.

The full claim/non-claim list is in [`PROVES_AND_DOES_NOT_PROVE.md`](./PROVES_AND_DOES_NOT_PROVE.md).

## Why v2 source binding matters

A signature without subject binding is a signature, not provenance. A v1 signed proof pack proves "this whole bundle has not been tampered with." A v2 envelope with `pack_binding` proves more: each individual receipt line carries an attested back-reference to its exact location in the pack — `pack_id`, `source_index`, `source_receipt_sha256`, `receipt_pack_sha256`, `pack_root_sha256`. A reviewer can reread the v1 file, compute the line hash, and compare to the attested binding. If they diverge, the verifier names the index and both hashes.

The v1 5-file kernel also catches this particular tamper, because the pack manifest covers `receipt_pack.jsonl` via its `files[].sha256`. The point of the v2 binding is that the diagnostic is *specific*: it tells you which receipt drifted, not just that the bundle is broken. That specificity is what lets a reviewer escalate to "show me the original line" rather than "your packet is invalid, start over."

## Public claim language

> The observed evidence trail stayed within the declared customer-data boundary. When that evidence trail was altered, verification caught the alteration and identified the broken source binding.

Cryptographically verifiable. Tamper-evident. Portable. Independently checkable. A bounded claim about an observed evidence trail.

## Regenerate the artifact

The shipped `authentic/` and `tampered/` directories are static outputs of `_generate.py`. To rebuild from scratch (requires `assay-toolkit` ≥ ReceiptV2 binding+CLI on `main`):

```bash
~/assay-toolkit/.venv/bin/python _generate.py
```

The `_keys/` directory is regenerated on demand and is not committed.
