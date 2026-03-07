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
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

GALLERY_ROOT = Path(__file__).parent.parent / "gallery"
ASSAY_CMD = "assay"

SCENARIOS = {
    "01-fintech-pass": {
        "exit_code": 0,
        "integrity": "PASS",
        "claims": "PASS",
        "description": "FintechCo loan approval AI -- all evidence present, all claims pass",
    },
    "02-insurance-honest-fail": {
        "exit_code": 1,
        "integrity": "PASS",
        "claims": "FAIL",
        "description": "InsuranceTech claims review -- evidence intact, declared coverage claim fails",
    },
    "03-tamper-demo": {
        "exit_code": 2,
        "integrity": "FAIL",
        "claims": None,
        "description": "DataCo analytics AI -- tampered pack (one byte changed), integrity fails",
        "also_has_good": True,
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
    pack_dir.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory() as tmp:
        agent_script = Path(tmp) / "fintech_agent.py"
        write_fintech_agent(agent_script)

        result = run(
            [ASSAY_CMD, "run", "-o", str(pack_dir), "--", "python3", str(agent_script)],
            check=False,
            capture=True,
        )
        print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)

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

    return verify.returncode


def build_scenario_02(scenario_dir: Path):
    """Scenario 02: InsuranceTech HONEST FAIL (exit 1)."""
    print("\n[02] Building InsuranceTech HONEST FAIL scenario...")
    pack_dir = scenario_dir / "proof_pack"
    pack_dir.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory() as tmp:
        agent_script = Path(tmp) / "insurance_agent.py"
        run_card = Path(tmp) / "coverage_claim.json"
        write_insurance_agent(agent_script)
        write_insurance_runcard(run_card)

        result = run(
            [
                ASSAY_CMD, "run",
                "-c", str(run_card),
                "-o", str(pack_dir),
                "--",
                "python3", str(agent_script),
            ],
            check=False,
            capture=True,
        )
        print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)

    verify = run(
        [ASSAY_CMD, "verify-pack", str(pack_dir), "--json", "--require-claim-pass"],
        check=False,
        capture=True,
    )
    result_data = json.loads(verify.stdout) if verify.stdout.strip().startswith("{") else {}
    integrity = "PASS" if result_data.get("passed") else result_data.get("receipt_integrity", "?")
    print(f"  exit={verify.returncode}  integrity={integrity}  claims={result_data.get('claim_check','?')}")

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
    return bad_verify.returncode  # tampered is the primary artifact


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
set -e
pip install assay-ai -q
echo ""
echo "Verifying {pack_subpath}..."
echo ""
{verify_cmd}
EXIT=$?
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


def update_scenarios_json(results: dict):
    """Update scenarios.json with build results."""
    manifest = {"scenarios": []}
    for scenario_id, data in SCENARIOS.items():
        entry = {
            "id": scenario_id,
            "description": data["description"],
            "expected_verification_exit_code": data["exit_code"],
            "expected_integrity": data["integrity"],
            "expected_claims": data["claims"],
            "built": results.get(scenario_id, {}).get("built", False),
            "actual_exit_code": results.get(scenario_id, {}).get("exit_code", None),
        }
        manifest["scenarios"].append(entry)

    out = Path(__file__).parent.parent / "scenarios.json"
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
