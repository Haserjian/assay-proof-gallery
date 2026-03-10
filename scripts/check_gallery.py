#!/usr/bin/env python3
"""
Verify the Assay Proof Gallery contract.

Reads scenarios.json, checks that each scenario's pack exists and
verifies with the expected exit code. Does NOT rebuild -- checks the
committed artifacts as-is.

Usage:
    python scripts/check_gallery.py          # check all scenarios
    python scripts/check_gallery.py --verbose

Exit codes:
    0  all scenarios match their contract
    1  one or more scenarios failed
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
GALLERY = ROOT / "gallery"
ASSAY_CMD = "assay"

# Flags required per-scenario when verifying.
# scenario 02 requires --require-claim-pass to enforce exit 1 on claims FAIL.
SCENARIO_VERIFY_FLAGS: dict[str, list[str]] = {
    "02-insurance-honest-fail": ["--require-claim-pass"],
}

# Which subpath holds the primary verifiable pack per scenario.
SCENARIO_PACK_SUBPATH: dict[str, str] = {
    "01-fintech-pass": "proof_pack",
    "02-insurance-honest-fail": "proof_pack",
    "03-tamper-demo": "tampered",  # tampered is the exit-2 artifact
    "04-mcp-notary-proxy": "proof_pack",
}

REQUIRED_PACK_FILES = [
    "pack_manifest.json",
    "pack_signature.sig",
    "receipt_pack.jsonl",
    "verify_report.json",
    "verify_transcript.md",
]


def check_scenario(scenario: dict, verbose: bool) -> bool:
    sid = scenario["id"]
    expected_exit = scenario["expected_verification_exit_code"]
    scenario_dir = GALLERY / sid

    print(f"\n[{sid}]")

    # 1. Scenario directory must exist
    if not scenario_dir.is_dir():
        print(f"  FAIL: directory not found: {scenario_dir}")
        return False

    # 2. Pack path must exist
    pack_subpath = SCENARIO_PACK_SUBPATH.get(sid, "proof_pack")
    pack_dir = scenario_dir / pack_subpath
    if not pack_dir.is_dir():
        print(f"  FAIL: pack directory not found: {pack_dir}")
        return False

    # 3. Required pack files must exist
    missing = [f for f in REQUIRED_PACK_FILES if not (pack_dir / f).exists()]
    if missing:
        print(f"  FAIL: missing pack files: {missing}")
        return False

    # 4. verify.sh must exist
    if not (scenario_dir / "verify.sh").exists():
        print(f"  FAIL: verify.sh not found")
        return False

    # 5. verify_transcript.md must be non-empty
    transcript = pack_dir / "verify_transcript.md"
    if transcript.stat().st_size == 0:
        print(f"  FAIL: verify_transcript.md is empty")
        return False

    # 6. Run assay verify-pack and assert expected exit code
    extra_flags = SCENARIO_VERIFY_FLAGS.get(sid, [])
    cmd = [ASSAY_CMD, "verify-pack", str(pack_dir)] + extra_flags
    if verbose:
        print(f"  $ {' '.join(cmd)}")

    result = subprocess.run(cmd, capture_output=True, text=True)
    actual_exit = result.returncode

    if actual_exit == expected_exit:
        label = {0: "PASS", 1: "HONEST FAIL", 2: "TAMPERED"}.get(actual_exit, str(actual_exit))
        print(f"  OK  exit={actual_exit} ({label})  [expected {expected_exit}]")
        if verbose and result.stdout.strip():
            print(f"      stdout: {result.stdout.strip()[:200]}")
        return True
    else:
        print(f"  FAIL  exit={actual_exit}  [expected {expected_exit}]")
        if result.stdout.strip():
            print(f"      stdout: {result.stdout.strip()[:400]}")
        if result.stderr.strip():
            print(f"      stderr: {result.stderr.strip()[:200]}")
        return False


def check_scenario_03_good(verbose: bool) -> bool:
    """Scenario 03: also verify the 'good' pack returns exit 0."""
    sid = "03-tamper-demo"
    good_dir = GALLERY / sid / "good"
    if not good_dir.is_dir():
        print(f"  FAIL: good pack directory not found: {good_dir}")
        return False

    cmd = [ASSAY_CMD, "verify-pack", str(good_dir)]
    if verbose:
        print(f"  $ {' '.join(cmd)}")

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        print(f"  OK  good pack exit=0 (PASS)")
        return True
    else:
        print(f"  FAIL  good pack exit={result.returncode} [expected 0]")
        return False


def check_clean_tampered_differ() -> bool:
    """Assert good and tampered receipt_pack.jsonl differ (the tampered byte).

    The manifest/signature are identical by design -- the tamper is applied
    to receipt_pack.jsonl, which is what causes the hash mismatch on verify.
    """
    sid = "03-tamper-demo"
    good_data = GALLERY / sid / "good" / "receipt_pack.jsonl"
    bad_data = GALLERY / sid / "tampered" / "receipt_pack.jsonl"

    if not good_data.exists() or not bad_data.exists():
        print("  SKIP: cannot compare good/tampered receipt_pack.jsonl (missing files)")
        return True  # not a failure, just can't check

    good_bytes = good_data.read_bytes()
    bad_bytes = bad_data.read_bytes()
    if good_bytes == bad_bytes:
        print("  FAIL: good and tampered receipt_pack.jsonl are identical (tamper not applied)")
        return False

    print("  OK  good/tampered receipt_pack.jsonl differ (tamper applied)")
    return True


def main():
    parser = argparse.ArgumentParser(description="Check Assay Proof Gallery contract")
    parser.add_argument("--verbose", "-v", action="store_true")
    args = parser.parse_args()

    scenarios_path = ROOT / "scenarios.json"
    if not scenarios_path.exists():
        print(f"ERROR: {scenarios_path} not found", file=sys.stderr)
        sys.exit(1)

    scenarios = json.loads(scenarios_path.read_text())["scenarios"]
    print(f"Checking {len(scenarios)} scenarios against scenarios.json contract...")

    failures = 0

    for scenario in scenarios:
        ok = check_scenario(scenario, verbose=args.verbose)
        if not ok:
            failures += 1

    # Extra checks for scenario 03
    print(f"\n[03-tamper-demo extra checks]")
    if not check_scenario_03_good(verbose=args.verbose):
        failures += 1
    if not check_clean_tampered_differ():
        failures += 1

    print(f"\n{'=' * 50}")
    if failures == 0:
        print(f"All {len(scenarios)} scenarios pass contract checks.")
        sys.exit(0)
    else:
        print(f"{failures} scenario(s) FAILED contract checks.", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
