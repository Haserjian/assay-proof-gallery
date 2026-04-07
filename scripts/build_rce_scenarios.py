#!/usr/bin/env python3
"""Build the three RCE golden-path scenarios for the proof gallery.

Scenario 08: RCE Replay Match (exit 0)
Scenario 09: RCE Replay Divergence (exit 1)
Scenario 10: RCE Tampered Replay (exit 2)

Uses the real Assay ProofPack builder to produce valid manifests.
"""

import hashlib
import json
import shutil
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

sys.path.insert(0, str(Path.home() / "assay-toolkit" / "src"))

from assay._receipts.canonicalize import prepare_receipt_for_hashing
from assay._receipts.jcs import canonicalize as jcs_canonicalize
from assay.keystore import AssayKeyStore
from assay.proof_pack import ProofPack

GALLERY_DIR = Path(__file__).resolve().parent.parent / "gallery"
KEYS_DIR = Path(__file__).resolve().parent / ".gallery_keys"
SIGNER_ID = "gallery-signer"


def _sha256_prefixed(data: bytes) -> str:
    return f"sha256:{hashlib.sha256(data).hexdigest()}"


def _canonical_hash(payload: Any) -> str:
    return _sha256_prefixed(jcs_canonicalize(payload))


def _receipt_hash(receipt: dict) -> str:
    return _sha256_prefixed(jcs_canonicalize(prepare_receipt_for_hashing(dict(receipt))))


def _get_keystore() -> AssayKeyStore:
    ks = AssayKeyStore(KEYS_DIR)
    if not ks.has_key(SIGNER_ID):
        ks.generate_key(SIGNER_ID)
    return ks


def _make_receipt(
    *,
    receipt_id: str,
    receipt_type: str,
    seq: int,
    payload: dict,
    parent_hashes: list,
    timestamp: str = "2026-04-06T12:00:00+00:00",
) -> dict:
    receipt = {
        "receipt_id": receipt_id,
        "type": receipt_type,
        "timestamp": timestamp,
        "schema_version": "3.0",
        "seq": seq,
        "proof_tier": "core",
        "parent_hashes": parent_hashes,
        **payload,
    }
    receipt["receipt_hash"] = _receipt_hash(receipt)
    return receipt


def _episode_spec_hash(contract: dict) -> str:
    env = contract["environment"]
    return _canonical_hash({
        "inputs": contract["inputs"],
        "replay_script": contract["replay_script"],
        "replay_policy": contract["replay_policy"],
        "environment": {
            "provider": env["provider"],
            "model_id": env["model_id"],
            "tool_versions": env["tool_versions"],
            "container_digest": env["container_digest"],
        },
    })


def _build_contract_and_traces(
    input_data: dict, transform_output: dict
) -> Tuple[dict, dict, bytes]:
    """Build Episode Contract, traces dict, and input bytes."""
    input_bytes = json.dumps(input_data, separators=(",", ":"), sort_keys=True).encode()
    input_hash = _sha256_prefixed(input_bytes)

    environment = {
        "provider": "synthetic",
        "model_id": "golden-path-v0",
        "tool_versions": {"assay": "1.15.1"},
        "container_digest": None,
    }
    environment["env_fingerprint_hash"] = _canonical_hash(environment)
    environment["model_version_hint"] = None
    environment["system_fingerprint"] = None

    contract = {
        "schema_version": "rce/0.1",
        "episode_id": "ep_019d07dfe648e3636b986339",
        "objective": "Analyze input and emit structured claim",
        "inputs": [{"ref": "input.json", "hash": input_hash, "media_type": "application/json"}],
        "replay_script": {
            "schema_version": "replay_script/0.1",
            "steps": [
                {"step_id": "s01", "opcode": "LOAD_INPUT", "params": {"ref": "input.json"}, "depends_on": []},
                {
                    "step_id": "s02",
                    "opcode": "APPLY_TRANSFORM",
                    "params": {"transform": "analyze"},
                    "depends_on": ["s01"],
                },
                {
                    "step_id": "s03",
                    "opcode": "EMIT_OUTPUT",
                    "params": {"claim_type": "analysis", "output_ref": "s02"},
                    "depends_on": ["s02"],
                },
            ],
        },
        "replay_policy": {"replay_basis": "recorded_trace", "comparator_tier": "A"},
        "environment": environment,
    }

    traces = {
        "s01": input_data,
        "s02": transform_output,
        "s03": transform_output,  # EMIT_OUTPUT emits the claim
    }

    return contract, traces, input_bytes


def _build_receipts(contract: dict, traces: dict) -> List[dict]:
    """Build receipt chain from contract and traces."""
    episode_id = contract["episode_id"]
    spec_hash = _episode_spec_hash(contract)
    env = contract["environment"]

    s01_hash = _canonical_hash(traces["s01"])
    s02_hash = _canonical_hash(traces["s02"])
    s03_hash = _canonical_hash(traces["s03"])
    inputs_hash = _canonical_hash(contract["inputs"])
    script_hash = _canonical_hash(contract["replay_script"])
    outputs_hash = _canonical_hash([{"step_id": "s03", "output_hash": s03_hash}])

    open_r = _make_receipt(
        receipt_id="r_ep_open_001", receipt_type="rce.episode_open/v0", seq=0,
        parent_hashes=[],
        payload={
            "episode_id": episode_id, "episode_spec_hash": spec_hash,
            "objective": contract.get("objective", ""),
            "inputs_hash": inputs_hash, "script_hash": script_hash,
            "env_fingerprint_hash": env["env_fingerprint_hash"],
            "replay_basis": "recorded_trace", "comparator_tier": "A", "n_steps": 3,
        },
    )
    s1 = _make_receipt(
        receipt_id="r_ep_step_001", receipt_type="rce.episode_step/v0", seq=1,
        parent_hashes=[open_r["receipt_hash"]],
        payload={
            "episode_id": episode_id, "step_id": "s01", "opcode": "LOAD_INPUT",
            "step_status": "PASS", "input_hashes": [], "output_hash": s01_hash,
            "output_size_bytes": 50, "duration_ms": 1, "comparator_tier": "A",
        },
    )
    s2 = _make_receipt(
        receipt_id="r_ep_step_002", receipt_type="rce.episode_step/v0", seq=2,
        parent_hashes=[s1["receipt_hash"]],
        payload={
            "episode_id": episode_id, "step_id": "s02", "opcode": "APPLY_TRANSFORM",
            "step_status": "PASS", "input_hashes": [s01_hash], "output_hash": s02_hash,
            "output_size_bytes": 100, "duration_ms": 5, "comparator_tier": "A",
            "provider": "synthetic", "model_id": "golden-path-v0",
        },
    )
    s3 = _make_receipt(
        receipt_id="r_ep_step_003", receipt_type="rce.episode_step/v0", seq=3,
        parent_hashes=[s2["receipt_hash"]],
        payload={
            "episode_id": episode_id, "step_id": "s03", "opcode": "EMIT_OUTPUT",
            "step_status": "PASS", "input_hashes": [s02_hash], "output_hash": s03_hash,
            "output_size_bytes": 100, "duration_ms": 1, "comparator_tier": "A",
        },
    )
    close_r = _make_receipt(
        receipt_id="r_ep_close_001", receipt_type="rce.episode_close/v0", seq=4,
        parent_hashes=[s3["receipt_hash"]],
        payload={
            "episode_id": episode_id, "episode_spec_hash": spec_hash,
            "outputs_hash": outputs_hash,
            "n_steps_executed": 3, "n_steps_passed": 3, "all_steps_passed": True,
            "replay_basis": "recorded_trace", "comparator_tier": "A",
        },
    )
    return [open_r, s1, s2, s3, close_r]


def _write_pack(
    scenario_dir: Path, contract: dict, receipts: list,
    traces: dict, input_bytes: bytes, ks: AssayKeyStore,
) -> Path:
    """Build a real proof pack and add episode artifacts alongside it."""
    if scenario_dir.exists():
        shutil.rmtree(scenario_dir)

    pack_dir = ProofPack(
        run_id="trace_rce_gallery",
        entries=receipts,
        signer_id=SIGNER_ID,
    ).build(scenario_dir, keystore=ks)

    # Add episode artifacts
    (pack_dir / "episode_contract.json").write_text(
        json.dumps(contract, indent=2), encoding="utf-8"
    )
    (pack_dir / "inputs").mkdir(exist_ok=True)
    (pack_dir / "inputs" / "input.json").write_bytes(input_bytes)
    traces_dir = pack_dir / "recorded_traces"
    traces_dir.mkdir(exist_ok=True)
    for step_id, trace in traces.items():
        (traces_dir / f"{step_id}.json").write_text(
            json.dumps(trace), encoding="utf-8"
        )
    return pack_dir


def _write_readme(scenario_dir: Path, title: str, expected: str, exit_code: int, body: str):
    (scenario_dir / "README.md").write_text(
        f"# {title}\n\n**Expected result:** {expected} (exit {exit_code})\n\n{body}\n"
        f"## Verify\n\n```bash\nassay rce-verify . --out-dir ./replay_results\n```\n",
        encoding="utf-8",
    )


def _write_verify_sh(scenario_dir: Path, expected_exit: int, label: str):
    sh = scenario_dir / "verify.sh"
    sh.write_text(
        f"""#!/usr/bin/env bash
# Verify this RCE episode pack. Expected: {label} (exit {expected_exit})
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
echo "Verifying RCE episode pack..."
set +e
cd "$SCRIPT_DIR"
assay rce-verify . --out-dir ./replay_results --overwrite
EXIT=$?
set -e
echo ""
if [ $EXIT -eq {expected_exit} ]; then
  echo "Got expected exit code {expected_exit} ({label})"
else
  echo "Unexpected exit code $EXIT (expected {expected_exit})"
  exit 1
fi
""",
        encoding="utf-8",
    )
    sh.chmod(0o755)


def build_08_match(ks: AssayKeyStore):
    print("Building 08-rce-replay-match...")
    input_data = {"applicant": "Jane Doe", "amount": 50000, "score": 720}
    transform_output = {"decision": "approved", "confidence": 0.92, "reasoning": "Score above threshold."}
    contract, traces, input_bytes = _build_contract_and_traces(input_data, transform_output)
    receipts = _build_receipts(contract, traces)
    pack_dir = _write_pack(GALLERY_DIR / "08-rce-replay-match", contract, receipts, traces, input_bytes, ks)
    _write_readme(pack_dir, "08 — RCE Replay Match", "MATCH", 0,
        "All recorded traces match receipt hashes under Tier A.\n"
        "Evidence chain intact, claims hold.\n")
    _write_verify_sh(pack_dir, 0, "MATCH")
    print(f"  -> {pack_dir}")


def build_09_diverge(ks: AssayKeyStore):
    print("Building 09-rce-replay-diverge...")
    input_data = {"applicant": "Jane Doe", "amount": 50000, "score": 720}
    transform_output = {"decision": "approved", "confidence": 0.92, "reasoning": "Score above threshold."}
    contract, traces, input_bytes = _build_contract_and_traces(input_data, transform_output)
    receipts = _build_receipts(contract, traces)

    # Swap traces for s02 and s03 with alternate content
    alt_output = {"decision": "approved", "confidence": 0.89, "reasoning": "Minor concern noted."}
    traces["s02"] = alt_output
    traces["s03"] = alt_output

    pack_dir = _write_pack(GALLERY_DIR / "09-rce-replay-diverge", contract, receipts, traces, input_bytes, ks)
    _write_readme(pack_dir, "09 — RCE Replay Divergence", "DIVERGE — HONEST FAIL", 1,
        "Recorded traces for s02 and s03 differ from original receipts.\n"
        "Evidence intact (receipt_integrity: PASS), but replay comparison\n"
        "finds hash mismatches (claim_check: FAIL). Dispute payload\n"
        "identifies divergent steps.\n")
    _write_verify_sh(pack_dir, 1, "DIVERGE")
    print(f"  -> {pack_dir}")


def build_10_tampered(ks: AssayKeyStore):
    print("Building 10-rce-tampered-replay...")
    input_data = {"applicant": "Jane Doe", "amount": 50000, "score": 720}
    transform_output = {"decision": "approved", "confidence": 0.92, "reasoning": "Score above threshold."}
    contract, traces, input_bytes = _build_contract_and_traces(input_data, transform_output)
    receipts = _build_receipts(contract, traces)

    # Tamper: change inputs_hash in open receipt (breaks Phase 3)
    receipts[0]["inputs_hash"] = "sha256:" + ("aa" * 32)

    pack_dir = _write_pack(GALLERY_DIR / "10-rce-tampered-replay", contract, receipts, traces, input_bytes, ks)
    _write_readme(pack_dir, "10 — RCE Tampered Replay", "INTEGRITY_FAIL — TAMPERED", 2,
        "The episode_open receipt's inputs_hash was tampered.\n"
        "Verifier detects mismatch in Phase 3 before replay comparison.\n"
        "Verdict: INTEGRITY_FAIL (receipt_integrity: FAIL, claim_check: null).\n")
    _write_verify_sh(pack_dir, 2, "INTEGRITY_FAIL")
    print(f"  -> {pack_dir}")


if __name__ == "__main__":
    ks = _get_keystore()
    build_08_match(ks)
    build_09_diverge(ks)
    build_10_tampered(ks)
    print("\nDone. Three RCE scenarios built.")
