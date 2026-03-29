#!/usr/bin/env python3
"""
Build all gallery scenarios from scratch using real Assay tooling.
Generates deterministic, verifiable proof packs for each scenario.

Usage:
    python scripts/build_gallery.py
    python scripts/build_gallery.py --scenario 01-fintech-pass
    python scripts/build_gallery.py --clean
"""

import argparse
import json
import os
import re
import shutil
import signal
import subprocess
import sys
import tempfile
import threading
import time
from pathlib import Path

GALLERY_ROOT = Path(__file__).parent.parent / "gallery"
ASSAY_CMD = "assay"

SCENARIOS = {
    "01-fintech-pass": {
        "exit_code": 0,
        "integrity": "PASS",
        "claims": "PASS",
        "description": "FintechCo loan approval AI -- all evidence present, all claims pass",
        "scenario_class": "tutorial_demo",
        "primary_audience": ["engineer", "buyer"],
        "claim_class": "proof_pack_pass",
        "verification_command": "verify_pack",
        "primary_artifact_path": "proof_pack",
    },
    "02-insurance-honest-fail": {
        "exit_code": 1,
        "integrity": "PASS",
        "claims": "FAIL",
        "description": "InsuranceTech claims review -- evidence intact, declared coverage claim fails",
        "scenario_class": "engineering_verification",
        "primary_audience": ["engineer", "reviewer"],
        "claim_class": "honest_fail",
        "verification_command": "verify_pack",
        "primary_artifact_path": "proof_pack",
    },
    "03-tamper-demo": {
        "exit_code": 2,
        "integrity": "FAIL",
        "claims": None,
        "description": "DataCo analytics AI -- tampered pack (one byte changed), integrity fails",
        "also_has_good": True,
        "scenario_class": "tutorial_demo",
        "primary_audience": ["engineer", "buyer"],
        "claim_class": "tamper_detection",
        "verification_command": "verify_pack",
        "primary_artifact_path": "tampered",
    },
    "04-mcp-notary-proxy": {
        "exit_code": 0,
        "integrity": "PASS",
        "claims": None,
        "description": "LogisticsCo supply chain agent -- MCP tool calls notarized via proxy, integrity verified",
        "scenario_class": "engineering_verification",
        "primary_audience": ["engineer", "security"],
        "claim_class": "mcp_notary",
        "verification_command": "verify_pack",
        "primary_artifact_path": "proof_pack",
    },
    "05-reviewer-packet-gaps": {
        "exit_code": 0,
        "integrity": "PASS",
        "claims": "PASS",
        "description": "AcmeSaaS support workflow reviewer packet -- authentic packet with explicit coverage gaps",
        "scenario_class": "reviewer_packet",
        "primary_audience": ["buyer", "reviewer"],
        "claim_class": "reviewer_packet",
        "verification_command": "reviewer_verify",
        "primary_artifact_path": "reviewer_packet",
        "expected_reviewer_settlement": "VERIFIED_WITH_GAPS",
        "expected_nested_pack_exit_code": 0,
    },
    "06-naic-aiset-mapping": {
        "exit_code": 0,
        "integrity": "PASS",
        "claims": "PASS",
        "description": "NAIC AISET reviewer packet -- insurance control mapping backed by proof-pack evidence",
        "scenario_class": "regulatory_control_mapping",
        "primary_audience": ["buyer", "compliance"],
        "claim_class": "naic_aiset_mapping",
        "verification_command": "reviewer_verify",
        "primary_artifact_path": "reviewer_packet",
        "expected_reviewer_settlement": "VERIFIED_WITH_GAPS",
        "expected_nested_pack_exit_code": 0,
    },
}


def run(cmd, cwd=None, check=True, capture=False):
    """Run a shell command."""
    kwargs = {"cwd": cwd, "check": check}
    if capture:
        kwargs["capture_output"] = True
        kwargs["text"] = True
    print(f"  $ {' '.join(str(c) for c in cmd)}")
    return subprocess.run(cmd, **kwargs)


def normalize_pack_summary(pack_dir: Path, verify_subpath: str, extra_flags: str = ""):
    """Rewrite absolute verify commands in PACK_SUMMARY.md to repo-relative paths."""
    summary_path = pack_dir / "PACK_SUMMARY.md"
    if not summary_path.exists():
        return

    command = f"python3 -m pip install assay-ai && assay verify-pack ./{verify_subpath}"
    if extra_flags:
        command += f" {extra_flags}"

    text = summary_path.read_text()
    normalized = re.sub(
        r"python3 -m pip install assay-ai && assay verify-pack .+",
        command,
        text,
        count=1,
    )
    if normalized != text:
        summary_path.write_text(normalized)


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_fintech_agent(path: Path):
    """Write a synthetic FintechCo loan approval agent script."""
    path.write_text(
        '''\
"""
Synthetic FintechCo loan approval agent.
Emits realistic receipts representing a governed AI system.
No real API calls -- all receipts are synthetic but schema-valid.
"""
from assay.store import emit_receipt

# Model call: initial application analysis
r1 = emit_receipt("model_call", {
    "model_id": "claude-sonnet-4-20250514",
    "provider": "anthropic",
    "total_tokens": 2341,
    "input_tokens": 1847,
    "output_tokens": 494,
    "latency_ms": 1203,
    "task": "loan_application_analysis",
})

# Guardian check: PII handling
emit_receipt("guardian_verdict", {
    "verdict": "allow",
    "tool": "credit_bureau_query",
    "risk_score": 0.18,
    "dignity_gate": "pass",
    "rationale": "Authorized credit check within consent scope",
}, parent_receipt_id=r1["receipt_id"])

# Model call: decision synthesis
r2 = emit_receipt("model_call", {
    "model_id": "claude-sonnet-4-20250514",
    "provider": "anthropic",
    "total_tokens": 981,
    "input_tokens": 743,
    "output_tokens": 238,
    "latency_ms": 847,
    "task": "decision_synthesis",
})

# Capability use: output structured decision
emit_receipt("capability_use", {
    "capability": "file_write",
    "target": "/output/loan_decision.json",
    "authorized": True,
}, parent_receipt_id=r2["receipt_id"])

# Model call: explanation generation
emit_receipt("model_call", {
    "model_id": "claude-sonnet-4-20250514",
    "provider": "anthropic",
    "total_tokens": 612,
    "input_tokens": 489,
    "output_tokens": 123,
    "latency_ms": 521,
    "task": "adverse_action_explanation",
})

print("FintechCo agent: 5 receipts emitted")
'''
    )


def write_fintech_runcard(path: Path):
    """Write a run-card that the fintech agent easily satisfies (5 receipts >= 3)."""
    card = {
        "card_id": "fintech_coverage_claim",
        "name": "FintechCo Coverage Claim",
        "description": "Loan approval workflow must have at least 3 receipts for audit coverage",
        "claims": [
            {
                "claim_id": "minimum_receipt_coverage",
                "description": "At least 3 receipts required for loan approval audit coverage",
                "check": "receipt_count_ge",
                "params": {"min_count": 3},
            }
        ],
    }
    path.write_text(json.dumps(card, indent=2))


def write_insurance_agent(path: Path):
    """Write a synthetic InsuranceTech claims review agent script."""
    path.write_text(
        '''\
"""
Synthetic InsuranceTech claims review agent.
Emits realistic receipts -- but fewer than the declared coverage claim requires.
This produces exit code 1: integrity PASS, claims FAIL (honest failure).
"""
from assay.store import emit_receipt

# Only 3 receipts -- the run-card will require 10 for full coverage claim
r1 = emit_receipt("model_call", {
    "model_id": "claude-sonnet-4-20250514",
    "provider": "anthropic",
    "total_tokens": 1823,
    "input_tokens": 1401,
    "output_tokens": 422,
    "latency_ms": 1089,
    "task": "claims_document_review",
})

emit_receipt("guardian_verdict", {
    "verdict": "allow",
    "tool": "claims_database_read",
    "risk_score": 0.09,
    "dignity_gate": "pass",
    "rationale": "Read-only access to authorized claims data",
}, parent_receipt_id=r1["receipt_id"])

emit_receipt("model_call", {
    "model_id": "claude-sonnet-4-20250514",
    "provider": "anthropic",
    "total_tokens": 744,
    "input_tokens": 612,
    "output_tokens": 132,
    "latency_ms": 634,
    "task": "coverage_determination",
})

print("InsuranceTech agent: 3 receipts emitted (coverage claim requires 10)")
'''
    )


def write_insurance_runcard(path: Path):
    """Write a run-card that declares more receipts than emitted (honest fail)."""
    card = {
        "card_id": "insurance_coverage_claim",
        "name": "Insurance Coverage Claim",
        "description": "Claims review must have full coverage: 10+ receipts required",
        "claims": [
            {
                "claim_id": "minimum_receipt_coverage",
                "description": "At least 10 receipts required for full claims review audit",
                "check": "receipt_count_ge",
                "params": {"min_count": 10},
            }
        ],
    }
    path.write_text(json.dumps(card, indent=2))


def build_scenario_01(scenario_dir: Path):
    """Scenario 01: FintechCo PASS (exit 0)."""
    print("\n[01] Building FintechCo PASS scenario...")
    pack_dir = scenario_dir / "proof_pack"

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        agent_script = tmp_path / "fintech_agent.py"
        run_card = tmp_path / "fintech_claim.json"
        temp_pack_dir = tmp_path / "proof_pack"
        write_fintech_agent(agent_script)
        write_fintech_runcard(run_card)

        result = run(
            [ASSAY_CMD, "run", "-c", str(run_card), "-o", str(temp_pack_dir), "--", "python3", str(agent_script)],
            check=False,
            capture=True,
        )
        print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)

        if temp_pack_dir.is_dir():
            if pack_dir.exists():
                shutil.rmtree(pack_dir)
            shutil.copytree(temp_pack_dir, pack_dir)

    # Verify and capture output
    verify = run(
        [ASSAY_CMD, "verify-pack", str(pack_dir), "--json"],
        check=False,
        capture=True,
    )
    result_data = json.loads(verify.stdout) if verify.stdout.strip().startswith("{") else {}
    print(f"  exit={verify.returncode}  integrity={result_data.get('receipt_integrity','?')}  claims={result_data.get('claim_check','?')}")

    # Generate HTML report
    run([ASSAY_CMD, "report", ".", "--output", str(scenario_dir / "report.html")], check=False)
    normalize_pack_summary(pack_dir, "gallery/01-fintech-pass/proof_pack")

    return verify.returncode


def build_scenario_02(scenario_dir: Path):
    """Scenario 02: InsuranceTech HONEST FAIL (exit 1)."""
    print("\n[02] Building InsuranceTech HONEST FAIL scenario...")
    pack_dir = scenario_dir / "proof_pack"

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        agent_script = tmp_path / "insurance_agent.py"
        run_card = tmp_path / "coverage_claim.json"
        temp_pack_dir = tmp_path / "proof_pack"
        write_insurance_agent(agent_script)
        write_insurance_runcard(run_card)

        result = run(
            [
                ASSAY_CMD, "run",
                "-c", str(run_card),
                "-o", str(temp_pack_dir),
                "--",
                "python3", str(agent_script),
            ],
            check=False,
            capture=True,
        )
        print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)

        if temp_pack_dir.is_dir():
            if pack_dir.exists():
                shutil.rmtree(pack_dir)
            shutil.copytree(temp_pack_dir, pack_dir)

    verify = run(
        [ASSAY_CMD, "verify-pack", str(pack_dir), "--json", "--require-claim-pass"],
        check=False,
        capture=True,
    )
    result_data = json.loads(verify.stdout) if verify.stdout.strip().startswith("{") else {}
    integrity = "PASS" if result_data.get("passed") else result_data.get("receipt_integrity", "?")
    print(f"  exit={verify.returncode}  integrity={integrity}  claims={result_data.get('claim_check','?')}")
    normalize_pack_summary(pack_dir, "gallery/02-insurance-honest-fail/proof_pack", "--require-claim-pass")

    return verify.returncode


def build_scenario_03(scenario_dir: Path):
    """Scenario 03: Tamper demo (exit 2 for tampered, exit 0 for good)."""
    print("\n[03] Building Tamper Demo scenario...")
    good_dir = scenario_dir / "good"
    tampered_dir = scenario_dir / "tampered"

    run(
        [ASSAY_CMD, "demo-challenge", "--output", str(scenario_dir)],
        check=False,
    )

    # Verify good (expect 0)
    good_verify = run(
        [ASSAY_CMD, "verify-pack", str(good_dir)],
        check=False,
        capture=True,
    )
    # Verify tampered (expect 2)
    bad_verify = run(
        [ASSAY_CMD, "verify-pack", str(tampered_dir)],
        check=False,
        capture=True,
    )
    print(f"  good exit={good_verify.returncode}  tampered exit={bad_verify.returncode}")
    normalize_pack_summary(good_dir, "gallery/03-tamper-demo/good")
    normalize_pack_summary(tampered_dir, "gallery/03-tamper-demo/tampered")
    return bad_verify.returncode  # tampered is the primary artifact


def build_scenario_04(scenario_dir: Path):
    """Scenario 04: MCP Notary Proxy (exit 0)."""
    print("\n[04] Building MCP Notary Proxy scenario...")
    pack_dir = scenario_dir / "proof_pack"
    server_script = scenario_dir / "demo_server.py"

    if not server_script.exists():
        print(f"  FAIL: demo_server.py not found at {server_script}", file=sys.stderr)
        return -1

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        audit_dir = tmp_path / "mcp_audit"

        # MCP JSON-RPC requests: initialize, list tools, then 3 tool calls
        requests = [
            {"jsonrpc": "2.0", "method": "initialize", "id": 1,
             "params": {"protocolVersion": "2024-11-05", "capabilities": {},
                        "clientInfo": {"name": "gallery-client", "version": "0.1.0"}}},
            {"jsonrpc": "2.0", "method": "notifications/initialized"},
            {"jsonrpc": "2.0", "method": "tools/list", "id": 2, "params": {}},
            {"jsonrpc": "2.0", "method": "tools/call", "id": 3,
             "params": {"name": "get_weather", "arguments": {"city": "Seattle"}}},
            {"jsonrpc": "2.0", "method": "tools/call", "id": 4,
             "params": {"name": "check_inventory", "arguments": {"product_id": "SKU-7291"}}},
            {"jsonrpc": "2.0", "method": "tools/call", "id": 5,
             "params": {"name": "calculate_risk",
                        "arguments": {"amount": 15000, "category": "international_transfer"}}},
        ]

        # Start proxy wrapping the demo MCP server
        proc = subprocess.Popen(
            [ASSAY_CMD, "mcp-proxy",
             "--audit-dir", str(audit_dir),
             "--store-args", "--store-results",
             "--server-id", "gallery-demo-server",
             "--", sys.executable, str(server_script)],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=str(tmp_path),
        )

        # Drain stdout/stderr in background to prevent pipe deadlock
        stdout_buf = []
        stderr_buf = []

        def drain(pipe, buf):
            for line in pipe:
                buf.append(line)

        t_out = threading.Thread(target=drain, args=(proc.stdout, stdout_buf), daemon=True)
        t_err = threading.Thread(target=drain, args=(proc.stderr, stderr_buf), daemon=True)
        t_out.start()
        t_err.start()

        # Send NDJSON requests with small delays for server processing
        for req in requests:
            proc.stdin.write((json.dumps(req) + "\n").encode())
            proc.stdin.flush()
            time.sleep(0.3)

        # Close stdin to signal session end
        proc.stdin.close()

        # Wait for proxy to shut down and build pack
        try:
            proc.wait(timeout=30)
        except subprocess.TimeoutExpired:
            proc.send_signal(signal.SIGINT)
            try:
                proc.wait(timeout=10)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait()

        t_out.join(timeout=5)
        t_err.join(timeout=5)

        stderr_text = b"".join(stderr_buf).decode(errors="replace").strip()
        print(f"  proxy exit={proc.returncode}")
        if stderr_text:
            # Show just the pack line if present
            for line in stderr_text.splitlines():
                if "Pack built" in line or "error" in line.lower():
                    print(f"  {line.strip()}")

        # Find and copy the built pack
        packs_dir = audit_dir / "packs"
        built_pack = None
        if packs_dir.exists():
            pack_dirs = sorted(packs_dir.iterdir())
            if pack_dirs:
                built_pack = pack_dirs[-1]

        if built_pack and built_pack.is_dir():
            if pack_dir.exists():
                shutil.rmtree(pack_dir)
            shutil.copytree(built_pack, pack_dir)
            print(f"  pack copied: {built_pack.name}")
        else:
            print("  FAIL: no proof pack produced", file=sys.stderr)
            return -1

    # Verify
    verify = run(
        [ASSAY_CMD, "verify-pack", str(pack_dir), "--json"],
        check=False,
        capture=True,
    )
    if verify.stdout.strip().startswith("{"):
        result_data = json.loads(verify.stdout)
        print(f"  exit={verify.returncode}  integrity={'PASS' if result_data.get('passed') else 'FAIL'}")
    else:
        print(f"  exit={verify.returncode}")

    normalize_pack_summary(pack_dir, "gallery/04-mcp-notary-proxy/proof_pack")

    return verify.returncode


def build_reviewer_packet_scenario(scenario_id: str, scenario_dir: Path):
    """Scenario 05/06: rebuild reviewer packet deterministically from packet inputs."""
    from assay.reviewer_packet_compile import compile_reviewer_packet

    print(f"\n[{scenario_id[:2]}] Building reviewer packet scenario...")
    reviewer_dir = scenario_dir / "reviewer_packet"
    proof_pack_dir = reviewer_dir / "proof_pack"
    packet_inputs_path = reviewer_dir / "PACKET_INPUTS.json"
    packet_manifest_path = reviewer_dir / "PACKET_MANIFEST.json"

    if not proof_pack_dir.is_dir():
        print(f"  FAIL: proof_pack not found at {proof_pack_dir}", file=sys.stderr)
        return -1
    if not packet_inputs_path.exists():
        print(f"  FAIL: PACKET_INPUTS.json not found at {packet_inputs_path}", file=sys.stderr)
        return -1

    packet_inputs = _load_json(packet_inputs_path)
    existing_manifest = _load_json(packet_manifest_path) if packet_manifest_path.exists() else {}
    generated_at = (
        existing_manifest.get("attestation", {}).get("generated_at")
        or packet_inputs.get("boundary_payload", {}).get("generated_at")
    )

    with tempfile.TemporaryDirectory() as tmp:
        tmp_proof_pack = Path(tmp) / "proof_pack"
        shutil.copytree(proof_pack_dir, tmp_proof_pack)
        result = compile_reviewer_packet(
            proof_pack_dir=tmp_proof_pack,
            boundary_payload=packet_inputs["boundary_payload"],
            mapping_payload=packet_inputs["mapping_payload"],
            out_dir=reviewer_dir,
            packet_overrides={"generated_at": generated_at} if generated_at else None,
        )

    reviewer_verify = run(
        [ASSAY_CMD, "reviewer", "verify", str(reviewer_dir), "--json"],
        check=False,
        capture=True,
    )
    nested_verify = run(
        [ASSAY_CMD, "verify-pack", str(proof_pack_dir), "--json"],
        check=False,
        capture=True,
    )

    reviewer_data = json.loads(reviewer_verify.stdout) if reviewer_verify.stdout.strip().startswith("{") else {}
    nested_data = json.loads(nested_verify.stdout) if nested_verify.stdout.strip().startswith("{") else {}
    print(
        "  "
        f"exit={reviewer_verify.returncode}  "
        f"settlement={reviewer_data.get('settlement_state', result.get('settlement_state', '?'))}  "
        f"nested_integrity={'PASS' if nested_data.get('passed') else nested_data.get('receipt_integrity', '?')}"
    )

    return reviewer_verify.returncode


def write_verify_sh(scenario_dir: Path, pack_subpath: str, expected_exit: int, extra_flags: str = ""):
    """Write verify.sh for a scenario."""
    label = {0: "PASS", 1: "HONEST FAIL (claims)", 2: "INTEGRITY FAIL (tampered)"}.get(
        expected_exit, "UNKNOWN"
    )
    verify_cmd = f"assay verify-pack ./{pack_subpath}"
    if extra_flags:
        verify_cmd += f" {extra_flags}"
    script = f"""\
#!/usr/bin/env bash
# Verify this proof pack locally. Expected result: {label} (exit {expected_exit})
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
python3 -m pip install assay-ai -q
echo ""
echo "Verifying {pack_subpath}..."
echo ""
set +e
cd "$SCRIPT_DIR"
{verify_cmd}
EXIT=$?
set -e
echo ""
if [ $EXIT -eq {expected_exit} ]; then
  echo "✓ Got expected exit code {expected_exit} ({label})"
else
  echo "✗ Unexpected exit code $EXIT (expected {expected_exit})"
  exit 1
fi
"""
    (scenario_dir / "verify.sh").write_text(script)
    (scenario_dir / "verify.sh").chmod(0o755)


def write_reviewer_verify_sh(scenario_dir: Path, expected_settlement: str):
    """Write verify.sh for reviewer-packet scenarios."""
    script = f"""\
#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
python3 -m pip install assay-ai -q

echo "Reviewer packet verdict"
cd "$SCRIPT_DIR"
PACKET_JSON=$(assay reviewer verify ./reviewer_packet --json)
export PACKET_JSON
export EXPECTED_SETTLEMENT="{expected_settlement}"
python3 - <<'PY'
import json
import os
import sys

payload = json.loads(os.environ["PACKET_JSON"])
expected = os.environ["EXPECTED_SETTLEMENT"]
actual = payload.get("settlement_state")
if actual != expected:
    print(f"Unexpected settlement: {{actual}} (expected {{expected}})", file=sys.stderr)
    sys.exit(1)
print(f"✓ Got expected settlement {{actual}}")
PY

echo
echo "Nested proof-pack verdict"
assay verify-pack ./reviewer_packet/proof_pack
"""
    (scenario_dir / "verify.sh").write_text(script, encoding="utf-8")
    (scenario_dir / "verify.sh").chmod(0o755)


def update_scenarios_json(results: dict):
    """Update scenarios.json with build results."""
    out = Path(__file__).parent.parent / "scenarios.json"
    existing = {}
    if out.exists():
        existing = {entry["id"]: entry for entry in json.loads(out.read_text()).get("scenarios", [])}

    manifest = {"scenarios": []}
    for scenario_id, data in SCENARIOS.items():
        previous = existing.get(scenario_id, {})
        entry = {
            "id": scenario_id,
            "description": data["description"],
            "scenario_class": data["scenario_class"],
            "primary_audience": data["primary_audience"],
            "claim_class": data["claim_class"],
            "verification_command": data["verification_command"],
            "primary_artifact_path": data["primary_artifact_path"],
            "expected_verification_exit_code": data["exit_code"],
            "expected_integrity": data["integrity"],
            "expected_claims": data["claims"],
            "expected_reviewer_settlement": data.get("expected_reviewer_settlement"),
            "expected_nested_pack_exit_code": data.get("expected_nested_pack_exit_code"),
            "built": results.get(scenario_id, {}).get("built", previous.get("built", False)),
            "actual_exit_code": results.get(scenario_id, {}).get("exit_code", previous.get("actual_exit_code")),
        }
        manifest["scenarios"].append(entry)

    out.write_text(json.dumps(manifest, indent=2))
    print(f"\nWrote {out}")


def main():
    parser = argparse.ArgumentParser(description="Build Assay Proof Gallery")
    parser.add_argument("--scenario", help="Build only this scenario ID")
    parser.add_argument("--clean", action="store_true", help="Remove all generated packs first")
    args = parser.parse_args()

    if args.clean:
        for s in SCENARIOS:
            d = GALLERY_ROOT / s / "proof_pack"
            if d.exists():
                shutil.rmtree(d)
                print(f"Cleaned {d}")
            for sub in ["good", "tampered"]:
                d2 = GALLERY_ROOT / s / sub
                if d2.exists():
                    shutil.rmtree(d2)
                    print(f"Cleaned {d2}")

    results = {}
    to_build = [args.scenario] if args.scenario else list(SCENARIOS.keys())

    for scenario_id in to_build:
        if scenario_id not in SCENARIOS:
            print(f"Unknown scenario: {scenario_id}", file=sys.stderr)
            sys.exit(1)

        scenario_dir = GALLERY_ROOT / scenario_id
        scenario_dir.mkdir(parents=True, exist_ok=True)
        data = SCENARIOS[scenario_id]

        if scenario_id == "01-fintech-pass":
            exit_code = build_scenario_01(scenario_dir)
            write_verify_sh(scenario_dir, "proof_pack", 0)
        elif scenario_id == "02-insurance-honest-fail":
            exit_code = build_scenario_02(scenario_dir)
            write_verify_sh(scenario_dir, "proof_pack", 1, extra_flags="--require-claim-pass")
        elif scenario_id == "03-tamper-demo":
            exit_code = build_scenario_03(scenario_dir)
            write_verify_sh(scenario_dir, "tampered", 2)
        elif scenario_id == "04-mcp-notary-proxy":
            exit_code = build_scenario_04(scenario_dir)
            write_verify_sh(scenario_dir, "proof_pack", 0)
        elif scenario_id == "05-reviewer-packet-gaps":
            exit_code = build_reviewer_packet_scenario(scenario_id, scenario_dir)
            write_reviewer_verify_sh(scenario_dir, "VERIFIED_WITH_GAPS")
        elif scenario_id == "06-naic-aiset-mapping":
            exit_code = build_reviewer_packet_scenario(scenario_id, scenario_dir)
            write_reviewer_verify_sh(scenario_dir, "VERIFIED_WITH_GAPS")

        results[scenario_id] = {
            "built": True,
            "exit_code": exit_code,
            "expected": data["exit_code"],
            "ok": exit_code == data["exit_code"],
        }

    update_scenarios_json(results)

    print("\n--- Gallery Build Summary ---")
    all_ok = True
    for scenario_id, r in results.items():
        status = "✓" if r["ok"] else "✗"
        print(f"  {status} {scenario_id}: exit={r['exit_code']} (expected {r['expected']})")
        if not r["ok"]:
            all_ok = False

    if not all_ok:
        print("\nSome scenarios produced unexpected exit codes.", file=sys.stderr)
        sys.exit(1)

    print("\nAll scenarios built and verified.")


if __name__ == "__main__":
    main()
