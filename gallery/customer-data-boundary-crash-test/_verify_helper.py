#!/usr/bin/env python3
"""Customer-data boundary crash-test verifier.

Runs four checks against an Assay proof pack with a v2 sidecar and prints a
structured report. Exits 0 if all four pass, 1 otherwise.

Checks:
  1. packet root              — runs `assay verify-pack` (v1 5-file kernel)
  2. receipt lineage          — receipt_pack.jsonl parses and is ordered
  3. v2 source bindings       — every line in _unsigned/receipt_pack_v2.jsonl
                                has its attested pack_binding.source_receipt_sha256
                                match the recomputed sha256 of the v1 line at
                                pack_binding.source_index
  4. observed boundary claim  — exactly one governance_posture_snapshot exists,
                                its policy declares a boundary_id and an
                                in-scope/forbidden split, and every
                                mcp_tool_call's data_class_accessed is in
                                the in-scope set

Public claim language:
  "The observed evidence trail stayed within the declared customer-data
  boundary. When that evidence trail was altered, verification caught the
  alteration and identified the broken source binding."

Does NOT claim safety, factual correctness, court admissibility, or
guarantee that unobserved actions did not occur outside the captured surface.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Optional


def _sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _v1_lines(pack_dir: Path) -> list[str]:
    raw = (pack_dir / "receipt_pack.jsonl").read_text()
    return [ln for ln in raw.splitlines() if ln.strip()]


def _v2_envelopes(pack_dir: Path) -> list[dict]:
    sidecar = pack_dir / "_unsigned" / "receipt_pack_v2.jsonl"
    if not sidecar.exists():
        return []
    raw = sidecar.read_text()
    return [json.loads(ln) for ln in raw.splitlines() if ln.strip()]


def _check_packet_root(pack_dir: Path) -> tuple[bool, Optional[str]]:
    assay = shutil.which("assay")
    if assay is None:
        return False, "assay CLI not on PATH (pip install assay-ai)"
    proc = subprocess.run(
        [assay, "verify-pack", str(pack_dir)],
        capture_output=True,
        text=True,
    )
    if proc.returncode == 0:
        return True, None
    return False, (
        f"`assay verify-pack` exited {proc.returncode} — "
        "v1 5-file kernel detected mismatch"
    )


def _check_receipt_lineage(pack_dir: Path) -> tuple[bool, Optional[str]]:
    try:
        lines = _v1_lines(pack_dir)
    except OSError as exc:
        return False, f"cannot read receipt_pack.jsonl: {exc}"
    if not lines:
        return False, "receipt_pack.jsonl is empty"
    last_seq = -1
    for idx, line in enumerate(lines):
        try:
            obj = json.loads(line)
        except json.JSONDecodeError as exc:
            return False, f"line {idx} is not valid JSON: {exc.msg}"
        seq = obj.get("seq")
        if seq is None:
            return False, f"line {idx} missing seq"
        if seq < last_seq:
            return False, f"line {idx} seq={seq} regressed from {last_seq}"
        last_seq = seq
    return True, None


def _check_v2_source_bindings(pack_dir: Path) -> tuple[bool, list[str]]:
    """Returns (overall_pass, output_lines). Output lines are printed verbatim
    so the failing case includes source_index / expected / actual."""
    out: list[str] = []
    envelopes = _v2_envelopes(pack_dir)
    if not envelopes:
        return False, ["    no v2 sidecar found at _unsigned/receipt_pack_v2.jsonl"]

    try:
        v1 = _v1_lines(pack_dir)
    except OSError as exc:
        return False, [f"    cannot read receipt_pack.jsonl: {exc}"]

    overall = True
    for env in envelopes:
        binding = env.get("pack_binding") or {}
        idx = binding.get("source_index")
        attested = binding.get("source_receipt_sha256")
        if idx is None or attested is None:
            overall = False
            out.append(f"    envelope {env.get('receipt_id', '?')}: missing pack_binding")
            continue
        if not (0 <= idx < len(v1)):
            overall = False
            out.append(f"    source_index {idx} out of range (v1 has {len(v1)} lines)")
            continue
        actual = _sha256_hex(v1[idx].encode("utf-8"))
        if actual != attested:
            overall = False
            out.append("    source_index: " + str(idx))
            out.append("    expected: " + str(attested))
            out.append("    actual:   " + actual)
    return overall, out


def _check_observed_boundary_claim(pack_dir: Path) -> tuple[bool, Optional[str]]:
    try:
        lines = _v1_lines(pack_dir)
    except OSError as exc:
        return False, f"cannot read receipt_pack.jsonl: {exc}"
    parsed = [json.loads(ln) for ln in lines]

    snapshots = [r for r in parsed if r.get("type") == "governance_posture_snapshot"]
    if len(snapshots) != 1:
        return False, f"expected exactly one governance_posture_snapshot, found {len(snapshots)}"
    snap = snapshots[0]
    policy = snap.get("policy") or {}
    if not policy.get("boundary_id"):
        return False, "governance_posture_snapshot.policy.boundary_id missing"
    in_scope = set(policy.get("data_classes_in_scope") or [])
    forbidden = set(policy.get("data_classes_forbidden") or [])
    if not in_scope or not forbidden:
        return False, "policy must declare both data_classes_in_scope and data_classes_forbidden"

    tool_calls = [r for r in parsed if r.get("type") == "mcp_tool_call"]
    for tc in tool_calls:
        cls = tc.get("data_class_accessed")
        if cls is None:
            return False, f"mcp_tool_call {tc.get('receipt_id', '?')} missing data_class_accessed"
        if cls in forbidden:
            return False, (
                f"mcp_tool_call {tc.get('receipt_id', '?')} accessed forbidden data class "
                f"{cls!r} (boundary {policy['boundary_id']!r})"
            )
        if cls not in in_scope:
            return False, (
                f"mcp_tool_call {tc.get('receipt_id', '?')} accessed undeclared data class "
                f"{cls!r} (not in scope, not in forbidden)"
            )
    return True, f"boundary {policy['boundary_id']!r}, {len(tool_calls)} tool calls in scope"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--pack", required=True, help="path to a proof_pack/ directory")
    parser.add_argument("--label", default=None, help="label to prefix the report")
    args = parser.parse_args()

    pack_dir = Path(args.pack).resolve()
    if not pack_dir.is_dir():
        print(f"error: not a directory: {pack_dir}", file=sys.stderr)
        return 2

    label = args.label or pack_dir.parent.name

    print(f"crash test: {label}")
    print()

    # 1. packet root
    ok1, err1 = _check_packet_root(pack_dir)
    print(f"[1/4] packet root: {'PASS' if ok1 else 'FAIL'}")
    if err1:
        print(f"      {err1}")

    # 2. receipt lineage
    ok2, err2 = _check_receipt_lineage(pack_dir)
    print(f"[2/4] receipt lineage: {'PASS' if ok2 else 'FAIL'}")
    if err2:
        print(f"      {err2}")

    # 3. v2 source bindings — failure body must contain source_index /
    #    expected / actual lines per the gallery contract.
    ok3, lines3 = _check_v2_source_bindings(pack_dir)
    if ok3:
        print("[3/4] v2 source bindings: PASS")
    else:
        print("[3/4] FAIL v2 source binding mismatch")
        for ln in lines3:
            print(ln)

    # 4. observed boundary claim
    ok4, err4 = _check_observed_boundary_claim(pack_dir)
    print(f"[4/4] observed boundary claim: {'PASS' if ok4 else 'FAIL'}")
    if err4:
        print(f"      {err4}")

    print()
    overall = ok1 and ok2 and ok3 and ok4
    print(f"OVERALL: {'PASS' if overall else 'FAIL'}")
    return 0 if overall else 1


if __name__ == "__main__":
    sys.exit(main())
