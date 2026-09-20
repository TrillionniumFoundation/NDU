#!/usr/bin/env python3
"""Build a deterministic package self-replay certificate.

This is a light, reviewer-facing replay layer.  It checks that the recent
finite neural guard chain can be regenerated from the submitted package
without rerunning the expensive PyTorch training jobs.
"""

from __future__ import annotations

import csv
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUT = DATA / "package_self_replay_certificate.json"

COMMANDS = [
    {
        "name": "py_compile_self_replay_chain",
        "argv": [
            sys.executable,
            "-m",
            "py_compile",
            "check_ndu_reproducibility.py",
            "scripts/make_neural_guard_refinement_stress_audit.py",
            "scripts/make_neural_guard_holdout_bootstrap_stability_audit.py",
            "scripts/make_neural_guard_concordance_audit.py",
            "scripts/make_neural_guard_leave_one_out_robustness_audit.py",
            "scripts/make_neural_bounded_composition_envelope_certificate.py",
            "scripts/make_neural_guard_stress_frontier_audit.py",
        ],
    },
    {
        "name": "regenerate_refinement_stress",
        "argv": [sys.executable, "scripts/make_neural_guard_refinement_stress_audit.py"],
    },
    {
        "name": "regenerate_holdout_bootstrap",
        "argv": [sys.executable, "scripts/make_neural_guard_holdout_bootstrap_stability_audit.py"],
    },
    {
        "name": "regenerate_concordance",
        "argv": [sys.executable, "scripts/make_neural_guard_concordance_audit.py"],
    },
    {
        "name": "regenerate_leave_one_out",
        "argv": [sys.executable, "scripts/make_neural_guard_leave_one_out_robustness_audit.py"],
    },
    {
        "name": "regenerate_bounded_composition",
        "argv": [sys.executable, "scripts/make_neural_bounded_composition_envelope_certificate.py"],
    },
    {
        "name": "regenerate_stress_frontier",
        "argv": [sys.executable, "scripts/make_neural_guard_stress_frontier_audit.py"],
    },
]

ARTIFACTS = [
    "data/neural_guard_refinement_stress_audit.csv",
    "data/neural_guard_holdout_bootstrap_stability_audit.csv",
    "data/neural_guard_concordance_audit.csv",
    "data/neural_guard_leave_one_out_robustness_audit.csv",
    "data/neural_bounded_composition_envelope_certificate.csv",
    "data/neural_guard_stress_frontier_audit.csv",
]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def count_csv_rows(path: Path) -> int:
    with path.open(newline="") as fh:
        return sum(1 for _ in csv.DictReader(fh))


def run_command(spec: dict[str, Any]) -> dict[str, Any]:
    env = os.environ.copy()
    env["PYTHONHASHSEED"] = "0"
    proc = subprocess.run(
        spec["argv"],
        cwd=ROOT,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    result: dict[str, Any] = {
        "name": spec["name"],
        "argv": spec["argv"][1:],
        "returncode": proc.returncode,
        "status": "PASS" if proc.returncode == 0 else "FAIL",
    }
    if proc.stdout.strip():
        result["stdout"] = proc.stdout.strip()
    if proc.stderr.strip():
        result["stderr"] = proc.stderr.strip()
    return result


def main() -> int:
    commands = [run_command(spec) for spec in COMMANDS]
    artifacts = []
    for rel in ARTIFACTS:
        path = ROOT / rel
        artifacts.append(
            {
                "path": rel,
                "bytes": path.stat().st_size,
                "sha256": sha256(path),
                "rows": count_csv_rows(path),
            }
        )

    ok = all(command["status"] == "PASS" for command in commands)
    report = {
        "certificate": "package_self_replay_certificate",
        "status": "PASS" if ok else "FAIL",
        "command_count": len(commands),
        "artifact_count": len(artifacts),
        "commands": commands,
        "artifacts": artifacts,
        "scope": "deterministic local package self-replay over the finite neural guard chain",
        "boundary": "Does not rerun full PyTorch training and does not evidence external review, submission, acceptance, or Strong Accept.",
    }
    OUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(f"wrote {OUT.relative_to(ROOT)} status={report['status']} commands={len(commands)} artifacts={len(artifacts)}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
