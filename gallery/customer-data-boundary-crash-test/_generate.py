#!/usr/bin/env python3
"""Generate the customer-data-boundary crash-test artifact.

Run from a Python that has the assay-toolkit (>=ReceiptV2 binding+CLI on main)
importable. Local dev:

    ~/assay-toolkit/.venv/bin/python \\
        ~/assay-proof-gallery/gallery/customer-data-boundary-crash-test/_generate.py

What it does:
  1. Builds a synthetic support-agent trace with a declared customer-data
     boundary (in a governance_posture_snapshot receipt) and 3 mcp_tool_call
     receipts that touch only data classes inside the boundary, plus a final
     model_call summary.
  2. Calls ProofPack(emit_v2_receipts=True).build(...) so each receipt gets
     an attested v2 envelope under _unsigned/receipt_pack_v2.jsonl carrying
     pack_binding (pack_id, source_index, source_receipt_sha256,
     receipt_pack_sha256, pack_root_sha256).
  3. Publishes the result to authentic/proof_pack/.
  4. Clones it to tampered/proof_pack/ and modifies one line of
     receipt_pack.jsonl in place — leaves everything else (manifest, signature,
     v2 sidecar) intact. This is the post-emission tamper the verifier catches.

Identity / determinism:
  Pack IDs and timestamps are pinned via deterministic_ts so re-runs produce
  byte-identical artifacts. This is gallery hygiene; it does not affect the
  cryptographic claim.
"""
from __future__ import annotations

import json
import shutil
from pathlib import Path

from assay.keystore import AssayKeyStore
from assay.proof_pack import ProofPack

HERE = Path(__file__).resolve().parent
DETERMINISTIC_TS = "2026-04-25T09:00:00+00:00"
RUN_ID = "trace_20260425T090000_demo01"
SIGNER_ID = "assay-gallery-demo"

# Declared customer-data boundary for this support-agent workflow.
BOUNDARY = {
    "boundary_id": "support_agent.customer_account_data.v1",
    "data_classes_in_scope": [
        "customer_account_id",
        "customer_account_status",
        "customer_subscription_tier",
    ],
    "data_classes_forbidden": [
        "customer_payment_method",
        "customer_ssn",
        "customer_billing_history_full",
    ],
}


def _make_receipts() -> list[dict]:
    """Six receipts: session_metadata, governance_posture_snapshot,
    3x mcp_tool_call, final model_call. All within the declared boundary."""
    receipts: list[dict] = []

    receipts.append(
        {
            "receipt_id": "r_session_metadata_001",
            "type": "session_metadata",
            "timestamp": "2026-04-25T09:00:01+00:00",
            "schema_version": "3.0",
            "seq": 0,
            "_trace_id": RUN_ID,
            "workflow": "support_agent.account_status_lookup",
            "agent_id": "support_agent_v1",
            "user_intent": "check whether a specific account is in good standing",
        }
    )

    receipts.append(
        {
            "receipt_id": "r_governance_posture_002",
            "type": "governance_posture_snapshot",
            "timestamp": "2026-04-25T09:00:02+00:00",
            "schema_version": "3.0",
            "seq": 1,
            "_trace_id": RUN_ID,
            "policy": BOUNDARY,
            "enforcement_mode": "shadow",
        }
    )

    for idx, (tool_name, data_class) in enumerate(
        [
            ("crm.lookup_account_id", "customer_account_id"),
            ("crm.get_account_status", "customer_account_status"),
            ("crm.get_subscription_tier", "customer_subscription_tier"),
        ]
    ):
        receipts.append(
            {
                "receipt_id": f"r_tool_call_{idx + 1:03d}",
                "type": "mcp_tool_call",
                "timestamp": f"2026-04-25T09:00:{3 + idx:02d}+00:00",
                "schema_version": "3.0",
                "seq": 2 + idx,
                "_trace_id": RUN_ID,
                "tool_name": tool_name,
                "data_class_accessed": data_class,
                "result_redacted": True,
                "result_sha256": f"sha256:placeholder_{idx + 1:02d}",
            }
        )

    receipts.append(
        {
            "receipt_id": "r_model_call_006",
            "type": "model_call",
            "timestamp": "2026-04-25T09:00:06+00:00",
            "schema_version": "3.0",
            "seq": 5,
            "_trace_id": RUN_ID,
            "model_id": "claude-sonnet-4-20250514",
            "input_tokens": 412,
            "output_tokens": 73,
            "task": "summarize_account_status_for_user",
        }
    )

    return receipts


def _build(output_dir: Path, keys_dir: Path) -> Path:
    if output_dir.exists():
        shutil.rmtree(output_dir)
    ks = AssayKeyStore(keys_dir=keys_dir)
    ks.ensure_key(SIGNER_ID)

    pack = ProofPack(
        run_id=RUN_ID,
        entries=_make_receipts(),
        signer_id=SIGNER_ID,
        mode="shadow",
        emit_v2_receipts=True,
    )
    return pack.build(
        output_dir,
        keystore=ks,
        deterministic_ts=DETERMINISTIC_TS,
    )


def _tamper(authentic_dir: Path, tampered_dir: Path, *, target_line_index: int = 3) -> dict:
    """Clone the authentic pack and modify one v1 receipt_pack.jsonl line in
    place. Pack manifest, pack signature, and v2 sidecar are NOT regenerated —
    that is the post-emission tamper. Returns the line-1 metadata so we can
    bake expected_output.txt deterministically.
    """
    if tampered_dir.exists():
        shutil.rmtree(tampered_dir)
    shutil.copytree(authentic_dir, tampered_dir)

    receipt_pack_path = tampered_dir / "proof_pack" / "receipt_pack.jsonl"
    lines = receipt_pack_path.read_text().splitlines()
    target = json.loads(lines[target_line_index])
    # Tamper: change a non-binding field. Adversary inflates input_tokens to
    # rewrite history about how expensive a call was. (Or any field — point
    # is one byte changed in receipt_pack.jsonl after emission.)
    target_field = "data_class_accessed"
    target_old = target.get(target_field)
    target_new = "customer_payment_method"  # forbidden — but irrelevant to the
    # binding check; what matters is the byte-level change.
    target[target_field] = target_new
    # Re-serialize the line in JCS shape (sorted keys, no spaces, then bytes).
    # Use json.dumps(sort_keys=True, separators=(",", ":")) which matches the
    # JCS-on-flat-dict shape closely enough that the LINE IS DIFFERENT, which
    # is the only thing the binding check cares about.
    lines[target_line_index] = json.dumps(
        target, sort_keys=True, separators=(",", ":")
    )
    receipt_pack_path.write_text("\n".join(lines) + "\n")

    return {
        "target_line_index": target_line_index,
        "target_field": target_field,
        "target_old": target_old,
        "target_new": target_new,
    }


def main() -> None:
    keys_dir = HERE / "_keys"
    keys_dir.mkdir(exist_ok=True)
    authentic = HERE / "authentic"
    tampered = HERE / "tampered"

    print(f"[1/3] Building authentic pack in {authentic.name}/proof_pack/ ...")
    _build(authentic / "proof_pack", keys_dir=keys_dir)

    print(f"[2/3] Cloning + tampering -> {tampered.name}/proof_pack/ ...")
    info = _tamper(authentic, tampered)
    print(
        f"        tampered line {info['target_line_index']}, field "
        f"{info['target_field']!r}: {info['target_old']!r} -> {info['target_new']!r}"
    )

    print("[3/3] Done.")
    print()
    print("Files produced:")
    for p in sorted((HERE).rglob("*")):
        if p.is_file() and "_keys" not in p.parts:
            print(f"  {p.relative_to(HERE)}")


if __name__ == "__main__":
    main()
