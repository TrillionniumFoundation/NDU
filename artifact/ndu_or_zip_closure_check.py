#!/usr/bin/env python3
"""Audit the NDU OR submission ZIP closure.

The gate verifies the distributable `NDU_RL_OR.zip` against the live package
tree: expected source/evidence files are present, private draft/build/cache
material is absent, and all ZIP file bytes match the current root copies.
"""

from __future__ import annotations

import hashlib
import json
import zipfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ZIP_PATH = ROOT / "NDU_RL_OR.zip"
OUT_JSON = ROOT / "artifact" / "ndu_or_zip_closure_check_results.json"
OUT_MD = ROOT / "artifact" / "ndu_or_zip_closure_check_results.md"

TOP_LEVEL_FILES = {
    "main.tex",
    "main.pdf",
    "main.bib",
    "main.bbl",
    "informs3.cls",
    "ormsv080.bst",
    "fig_inventory_theta_policy_surface.png",
    "NDU_OR_submission_checklist.md",
}
RESULT_STEMS_EXCLUDED_FROM_ZIP = {
    "artifact/ndu_or_zip_closure_check_results.json",
    "artifact/ndu_or_zip_closure_check_results.md",
    "artifact/ndu_or_package_hash_ledger_check_results.json",
    "artifact/ndu_or_package_hash_ledger_check_results.md",
    "artifact/ndu_or_extracted_hash_ledger_replay_check_results.json",
    "artifact/ndu_or_extracted_hash_ledger_replay_check_results.md",
    "artifact/ndu_or_external_boundary_scan_check_results.json",
    "artifact/ndu_or_external_boundary_scan_check_results.md",
    "artifact/ndu_or_result_freshness_check_results.json",
    "artifact/ndu_or_result_freshness_check_results.md",
    "artifact/ndu_or_reviewer_handoff_index_check_results.json",
    "artifact/ndu_or_reviewer_handoff_index_check_results.md",
    "artifact/ndu_or_zip_source_result_partition_check_results.json",
    "artifact/ndu_or_zip_source_result_partition_check_results.md",
    "artifact/ndu_or_root_zip_forensic_parity_check_results.json",
    "artifact/ndu_or_root_zip_forensic_parity_check_results.md",
    "artifact/ndu_or_release_manifest_parity_check_results.json",
    "artifact/ndu_or_release_manifest_parity_check_results.md",
}
FORBIDDEN_PARTS = {"draft", "__pycache__", ".git", ".venv-nbo-ad", "_backups"}
FORBIDDEN_SUFFIXES = {".aux", ".blg", ".fdb_latexmk", ".fls", ".log", ".out", ".synctex.gz", ".pyc"}
REQUIRED_CRITICAL_ENTRIES = {
    "artifact/ndu_or_zip_closure_check.py",
    "artifact/ndu_or_package_hash_ledger_check.py",
    "artifact/ndu_or_extracted_hash_ledger_replay_check.py",
    "artifact/ndu_or_external_boundary_scan_check.py",
    "artifact/ndu_or_result_freshness_check.py",
    "artifact/ndu_or_reviewer_handoff_index.json",
    "artifact/ndu_or_reviewer_handoff_index_check.py",
    "artifact/ndu_or_zip_source_result_partition_check.py",
    "artifact/ndu_or_root_zip_forensic_parity_check.py",
    "artifact/ndu_or_release_manifest_parity_ledger.json",
    "artifact/ndu_or_release_manifest_parity_check.py",
    "artifact/ndu_or_positioning_check.py",
    "artifact/ndu_or_positioning_results.json",
    "reproducibility/README.md",
    "reproducibility/check_ndu_reproducibility.py",
    "reproducibility/check_ndu_reproducibility_results.json",
    "reproducibility/manifest.json",
    "reproducibility/data/reproducibility_environment_audit.json",
    "reproducibility/data/lightweight_replay_dependency_closure_audit.csv",
    "reproducibility/data/package_self_replay_certificate.json",
    "reproducibility/scripts/make_reproducibility_environment_audit.py",
    "reproducibility/scripts/make_lightweight_replay_dependency_closure_audit.py",
    "reproducibility/scripts/make_package_self_replay_certificate.py",
}


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def add(checks: list[dict[str, Any]], name: str, ok: bool, observed: Any, expected: Any) -> None:
    checks.append({"name": name, "ok": bool(ok), "observed": observed, "expected": expected})


def include_file(path: Path) -> bool:
    rel = path.relative_to(ROOT).as_posix()
    parts = set(path.relative_to(ROOT).parts)
    if parts & FORBIDDEN_PARTS:
        return False
    if rel in RESULT_STEMS_EXCLUDED_FROM_ZIP:
        return False
    if rel in TOP_LEVEL_FILES:
        return True
    if rel.startswith("artifact/"):
        return path.suffix in {".py", ".json", ".md"}
    if rel.startswith("reproducibility/"):
        return path.is_file() and path.suffix != ".pyc"
    return False


def expected_entries() -> dict[str, bytes]:
    entries: dict[str, bytes] = {}
    for rel in TOP_LEVEL_FILES:
        path = ROOT / rel
        if path.exists():
            entries[rel] = path.read_bytes()
    for path in sorted((ROOT / "artifact").rglob("*")):
        if path.is_file() and include_file(path):
            entries[path.relative_to(ROOT).as_posix()] = path.read_bytes()
    for path in sorted((ROOT / "reproducibility").rglob("*")):
        if path.is_file() and include_file(path):
            entries[path.relative_to(ROOT).as_posix()] = path.read_bytes()
    return entries


def read_zip() -> tuple[dict[str, bytes], list[str]]:
    files: dict[str, bytes] = {}
    errors: list[str] = []
    if not ZIP_PATH.exists():
        return files, ["missing NDU_RL_OR.zip"]
    with zipfile.ZipFile(ZIP_PATH) as zf:
        bad = zf.testzip()
        if bad is not None:
            errors.append(f"zip integrity failure at {bad}")
        for info in zf.infolist():
            if info.is_dir():
                continue
            files[info.filename.rstrip("/")] = zf.read(info)
    return files, errors


def forbidden_entries(names: set[str]) -> list[str]:
    bad: list[str] = []
    for rel in sorted(names):
        parts = set(Path(rel).parts)
        suffix = ".synctex.gz" if rel.endswith(".synctex.gz") else Path(rel).suffix
        if parts & FORBIDDEN_PARTS or suffix in FORBIDDEN_SUFFIXES:
            bad.append(rel)
    return bad


def main() -> int:
    expected = expected_entries()
    files, zip_errors = read_zip()
    present = set(files)
    expected_names = set(expected)
    missing = sorted(expected_names - present)
    extra = sorted(present - expected_names)
    critical_missing = sorted(REQUIRED_CRITICAL_ENTRIES - present)
    mismatched = sorted(
        rel for rel in expected_names & present if sha256_bytes(files[rel]) != sha256_bytes(expected[rel])
    )
    forbidden = forbidden_entries(present)

    checks: list[dict[str, Any]] = []
    add(checks, "zip_integrity", not zip_errors, zip_errors, [])
    add(checks, "required_entries_present", not missing, missing[:25], "no missing expected entries")
    add(checks, "no_unexpected_entries", not extra, extra[:25], "no entries outside generated closure filelist")
    add(checks, "critical_evidence_entries_present", not critical_missing, critical_missing, "all critical reproducibility/positioning/closure entries")
    add(checks, "no_private_or_build_entries", not forbidden, forbidden[:25], "no draft/cache/backup/build byproduct entries")
    add(checks, "zip_bytes_match_root_tree", not mismatched, mismatched[:25], "ZIP bytes match current root tree")

    failures = [check for check in checks if not check["ok"]]
    report = {
        "kind": "ndu_or_zip_closure_check",
        "status": "PASS" if not failures else "FAIL",
        "check_count": len(checks),
        "failure_count": len(failures),
        "zip_path": "NDU_RL_OR.zip",
        "zip_entries": len(present),
        "expected_entries": len(expected_names),
        "zip_sha256": sha256_bytes(ZIP_PATH.read_bytes()) if ZIP_PATH.exists() else None,
        "checks": checks,
        "nonclaim": "Local ZIP-closure/package-boundary audit only; not full PyTorch/CEM regeneration, independent reproduction, external review, submission, acceptance, or Strong Accept evidence.",
    }
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = [
        "# NDU OR ZIP closure check",
        "",
        f"Status: **{report['status']}**",
        "",
        f"- ZIP entries: `{report['zip_entries']}`",
        f"- Expected entries: `{report['expected_entries']}`",
        f"- ZIP SHA256: `{report['zip_sha256']}`",
        f"- Failures: `{report['failure_count']}`",
        "",
        "## Checks",
        "",
    ]
    for check in checks:
        marker = "PASS" if check["ok"] else "FAIL"
        lines.append(f"- **{marker}** `{check['name']}`")
    lines += ["", report["nonclaim"]]
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({k: report[k] for k in ["status", "check_count", "failure_count", "zip_entries", "expected_entries", "zip_sha256"]}, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
