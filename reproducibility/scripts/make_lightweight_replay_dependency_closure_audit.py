#!/usr/bin/env python3
"""Audit imports for the lightweight replay gate.

The environment audit records which optional full-regeneration packages are
installed.  This companion audit checks a narrower claim: the lightweight
checker, environment audit, package self-replay script, and finite neural guard
builders do not import those optional full-regeneration packages.
"""

from __future__ import annotations

import ast
import csv
import hashlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "lightweight_replay_dependency_closure_audit.csv"

OPTIONAL_FULL_REGENERATION_IMPORTS = {
    "matplotlib",
    "numpy",
    "pandas",
    "seaborn",
    "torch",
}

LIGHTWEIGHT_SCRIPTS = [
    ("checker", "check_ndu_reproducibility.py"),
    ("environment_audit", "scripts/make_reproducibility_environment_audit.py"),
    ("package_self_replay", "scripts/make_package_self_replay_certificate.py"),
    ("finite_guard_chain", "scripts/make_neural_guard_refinement_stress_audit.py"),
    ("finite_guard_chain", "scripts/make_neural_guard_holdout_bootstrap_stability_audit.py"),
    ("finite_guard_chain", "scripts/make_neural_guard_concordance_audit.py"),
    ("finite_guard_chain", "scripts/make_neural_guard_leave_one_out_robustness_audit.py"),
    ("finite_guard_chain", "scripts/make_neural_bounded_composition_envelope_certificate.py"),
    ("finite_guard_chain", "scripts/make_neural_guard_stress_frontier_audit.py"),
]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def imported_modules(path: Path) -> list[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    modules: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                modules.add(alias.name.split(".", 1)[0])
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                modules.add(node.module.split(".", 1)[0])
    modules.discard("__future__")
    return sorted(modules)


def main() -> int:
    rows = []
    for component, rel in LIGHTWEIGHT_SCRIPTS:
        path = ROOT / rel
        modules = imported_modules(path)
        forbidden = sorted(set(modules) & OPTIONAL_FULL_REGENERATION_IMPORTS)
        rows.append(
            {
                "component": component,
                "script": rel,
                "sha256": sha256(path),
                "imported_top_level_modules": ";".join(modules),
                "forbidden_optional_full_regeneration_imports": ";".join(forbidden),
                "status": "PASS" if not forbidden else "FAIL",
                "boundary": (
                    "AST import closure for the lightweight gate only; "
                    "does not rerun full PyTorch/CEM regeneration and does not "
                    "evidence external review, submission, acceptance, or Strong Accept."
                ),
            }
        )

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    status = "PASS" if all(row["status"] == "PASS" for row in rows) else "FAIL"
    print(f"wrote {OUT.relative_to(ROOT)} status={status} rows={len(rows)}")
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
