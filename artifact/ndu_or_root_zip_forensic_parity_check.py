#!/usr/bin/env python3
"""Audit root/ZIP forensic parity for the NDU OR package.

This local gate cross-checks the current root package tree, distributable ZIP,
ZIP sidecar, package hash ledger, and reviewer handoff route. It is not an
external review, upload, submission, acceptance, or
Strong Accept claim.
"""

from __future__ import annotations

import hashlib
import json
import zipfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ZIP_PATH = ROOT / "NDU_RL_OR.zip"
ZIP_SIDECAR = ROOT / "NDU_RL_OR.zip.sha256"
OUT_JSON = ROOT / "artifact" / "ndu_or_root_zip_forensic_parity_check_results.json"
OUT_MD = ROOT / "artifact" / "ndu_or_root_zip_forensic_parity_check_results.md"

REQUIRED_ROOT_FILES = {
    "main.tex",
    "main.pdf",
    "NDU_RL_OR.zip",
    "NDU_RL_OR.zip.sha256",
    "NDU_OR_submission_checklist.md",
    "artifact/ndu_or_root_zip_forensic_parity_check.py",
    "artifact/ndu_or_zip_source_result_partition_check.py",
    "artifact/ndu_or_release_manifest_parity_ledger.json",
    "artifact/ndu_or_release_manifest_parity_check.py",
    "artifact/ndu_or_reviewer_handoff_index.json",
    "artifact/ndu_or_reviewer_handoff_index_check.py",
    "artifact/ndu_or_result_freshness_check.py",
    "artifact/ndu_or_package_hash_ledger_check.py",
    "artifact/ndu_or_extracted_hash_ledger_replay_check.py",
    "artifact/ndu_or_external_boundary_scan_check.py",
    "reproducibility/check_ndu_reproducibility.py",
    "reproducibility/check_ndu_reproducibility_results.json",
}

ZIP_BYTE_MATCH_ENTRIES = {
    "main.tex",
    "main.pdf",
    "NDU_OR_submission_checklist.md",
    "artifact/ndu_or_root_zip_forensic_parity_check.py",
    "artifact/ndu_or_zip_source_result_partition_check.py",
    "artifact/ndu_or_release_manifest_parity_ledger.json",
    "artifact/ndu_or_release_manifest_parity_check.py",
    "artifact/ndu_or_reviewer_handoff_index.json",
    "artifact/ndu_or_reviewer_handoff_index_check.py",
    "artifact/ndu_or_result_freshness_check.py",
    "artifact/ndu_or_package_hash_ledger_check.py",
    "artifact/ndu_or_extracted_hash_ledger_replay_check.py",
    "artifact/ndu_or_external_boundary_scan_check.py",
    "reproducibility/check_ndu_reproducibility.py",
    "reproducibility/check_ndu_reproducibility_results.json",
}

PASS_RESULTS = {
    "artifact/ndu_or_zip_source_result_partition_check_results.json",
    "artifact/ndu_or_reviewer_handoff_index_check_results.json",
    "artifact/ndu_or_zip_closure_check_results.json",
    "artifact/ndu_or_package_hash_ledger_check_results.json",
    "artifact/ndu_or_extracted_hash_ledger_replay_check_results.json",
    "artifact/ndu_or_external_boundary_scan_check_results.json",
    "artifact/ndu_or_positioning_results.json",
    "reproducibility/check_ndu_reproducibility_results.json",
}

REQUIRED_CHECKLIST_PHRASES = [
    "R88",
    "R89",
    "root/ZIP forensic parity",
    "release-manifest parity",
    "artifact/ndu_or_root_zip_forensic_parity_check.py",
    "artifact/ndu_or_release_manifest_parity_check.py",
    "local package/evidence",
    "no external review",
    "submission",
    "upload",
    "acceptance",
    "Strong Accept",
]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_json(rel: str) -> dict[str, Any]:
    return json.loads((ROOT / rel).read_text(encoding="utf-8", errors="replace"))


def add(checks: list[dict[str, Any]], name: str, ok: bool, observed: Any, expected: Any) -> None:
    checks.append({"name": name, "ok": bool(ok), "observed": observed, "expected": expected})


def status_passed(data: dict[str, Any]) -> bool:
    status = data.get("status") or (data.get("summary") or {}).get("status")
    failures = data.get("failure_count", data.get("failures", 0))
    if isinstance(failures, list):
        failures = len(failures)
    return status == "PASS" and failures in (0, None)


def read_zip() -> tuple[dict[str, bytes], list[str], str | None]:
    if not ZIP_PATH.exists():
        return {}, ["missing NDU_RL_OR.zip"], None
    files: dict[str, bytes] = {}
    errors: list[str] = []
    with zipfile.ZipFile(ZIP_PATH) as zf:
        bad = zf.testzip()
        if bad is not None:
            errors.append(f"zip integrity failure at {bad}")
        for info in zf.infolist():
            if not info.is_dir():
                files[info.filename.rstrip("/")] = zf.read(info)
    return files, errors, sha256(ZIP_PATH)


def main() -> int:
    checks: list[dict[str, Any]] = []
    files, zip_errors, zip_hash = read_zip()
    present = set(files)

    missing_root = sorted(rel for rel in REQUIRED_ROOT_FILES if not (ROOT / rel).exists())
    add(checks, "required_root_files_exist", not missing_root, missing_root, "all root forensic-parity files exist")
    add(checks, "zip_integrity", not zip_errors, zip_errors, [])

    sidecar_text = ZIP_SIDECAR.read_text(encoding="utf-8", errors="replace").strip() if ZIP_SIDECAR.exists() else ""
    expected_sidecar = f"{zip_hash}  NDU_RL_OR.zip"
    add(checks, "zip_sidecar_matches_current_zip", bool(zip_hash and sidecar_text == expected_sidecar), sidecar_text, expected_sidecar)

    missing_zip_entries = sorted(ZIP_BYTE_MATCH_ENTRIES - present)
    add(checks, "zip_contains_forensic_sources", not missing_zip_entries, missing_zip_entries, "all forensic source entries present in ZIP")

    mismatched: list[dict[str, Any]] = []
    for rel in sorted(ZIP_BYTE_MATCH_ENTRIES & present):
        root_path = ROOT / rel
        if root_path.exists():
            root_hash = sha256(root_path)
            zip_entry_hash = sha256_bytes(files[rel])
            if root_hash != zip_entry_hash:
                mismatched.append({"path": rel, "root": root_hash, "zip": zip_entry_hash})
    add(checks, "zip_source_bytes_match_root", not mismatched, mismatched[:25], "required ZIP source entries match root bytes")

    result_summary: dict[str, Any] = {}
    bad_results: list[dict[str, Any]] = []
    for rel in sorted(PASS_RESULTS):
        path = ROOT / rel
        if not path.exists():
            bad_results.append({"path": rel, "status": "MISSING"})
            continue
        data = read_json(rel)
        result_summary[rel] = {
            "status": data.get("status") or (data.get("summary") or {}).get("status"),
            "failure_count": data.get("failure_count", data.get("failures")),
        }
        if not status_passed(data):
            bad_results.append({"path": rel, **result_summary[rel]})
    add(checks, "referenced_results_pass", not bad_results, bad_results, "all referenced local result JSON files report PASS")

    package_ledger = read_json("artifact/ndu_or_package_hash_ledger_check_results.json")
    ledger_files = package_ledger.get("files", {})
    missing_ledger = sorted(REQUIRED_ROOT_FILES - set(ledger_files))
    stale_ledger: list[dict[str, Any]] = []
    for rel in sorted(REQUIRED_ROOT_FILES & set(ledger_files)):
        current = {"bytes": (ROOT / rel).stat().st_size, "sha256": sha256(ROOT / rel)}
        ledger = ledger_files[rel]
        if {"bytes": ledger.get("bytes"), "sha256": ledger.get("sha256")} != current:
            stale_ledger.append({"path": rel, "ledger": ledger, "current": current})
    add(checks, "package_hash_ledger_covers_r89_sources", not missing_ledger, missing_ledger, "package hash ledger lists R89 release-manifest parity targets")
    add(checks, "package_hash_ledger_matches_current_files", not stale_ledger, stale_ledger[:25], "package hash ledger hashes match current root files")

    checklist = (ROOT / "NDU_OR_submission_checklist.md").read_text(encoding="utf-8", errors="replace")
    status_text = (ROOT / "draft" / "referee-loop-status.md").read_text(encoding="utf-8", errors="replace")
    missing_phrases = [phrase for phrase in REQUIRED_CHECKLIST_PHRASES if phrase not in checklist + "\n" + status_text]
    add(checks, "checklist_status_mentions_r89_boundary", not missing_phrases, missing_phrases, "R89 release-manifest parity, R88 forensic parity, and local-only boundary phrases")

    failures = [check for check in checks if not check["ok"]]
    report = {
        "kind": "ndu_or_root_zip_forensic_parity_check",
        "status": "PASS" if not failures else "FAIL",
        "check_count": len(checks),
        "failure_count": len(failures),
        "zip_sha256": zip_hash,
        "zip_sidecar_sha256": sha256(ZIP_SIDECAR) if ZIP_SIDECAR.exists() else None,
        "checker_sha256": sha256(ROOT / "artifact" / "ndu_or_root_zip_forensic_parity_check.py"),
        "zip_entries": len(present),
        "checks": checks,
        "nonclaim": "Local root/ZIP forensic parity audit only; not full PyTorch/CEM regeneration, independent reproduction, external validation, external review, submission, upload, acceptance, or Strong Accept evidence.",
    }
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = [
        "# NDU OR root/ZIP forensic parity check",
        "",
        f"Status: **{report['status']}**",
        "",
        f"- Checks: `{report['check_count']}`",
        f"- Failures: `{report['failure_count']}`",
        f"- ZIP entries: `{report['zip_entries']}`",
        f"- ZIP SHA256: `{report['zip_sha256']}`",
        "",
        "## Checks",
        "",
    ]
    for check in checks:
        marker = "PASS" if check["ok"] else "FAIL"
        lines.append(f"- **{marker}** `{check['name']}`")
    lines += ["", report["nonclaim"]]
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({k: report[k] for k in ["status", "check_count", "failure_count", "zip_entries", "zip_sha256"]}, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
