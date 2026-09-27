#!/usr/bin/env python3
"""Audit the NDU OR release-manifest parity ledger.

This local gate freezes the release-facing package surface: manuscript files,
ZIP/sidecar, source/result partition, root/ZIP forensic parity, package hash
ledger, reviewer handoff route, reproducibility result, OR-positioning result,
and retained nonclaim boundaries. It is not an external review, upload,
submission, acceptance, or Strong Accept claim.
"""

from __future__ import annotations

import hashlib
import json
import zipfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
LEDGER_PATH = ROOT / "artifact" / "ndu_or_release_manifest_parity_ledger.json"
ZIP_PATH = ROOT / "NDU_RL_OR.zip"
ZIP_SIDECAR = ROOT / "NDU_RL_OR.zip.sha256"
OUT_JSON = ROOT / "artifact" / "ndu_or_release_manifest_parity_check_results.json"
OUT_MD = ROOT / "artifact" / "ndu_or_release_manifest_parity_check_results.md"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def read_json(rel_or_path: str | Path) -> dict[str, Any]:
    path = rel_or_path if isinstance(rel_or_path, Path) else ROOT / rel_or_path
    return json.loads(path.read_text(encoding="utf-8", errors="replace"))


def add(checks: list[dict[str, Any]], name: str, ok: bool, observed: Any, expected: Any) -> None:
    checks.append({"name": name, "ok": bool(ok), "observed": observed, "expected": expected})


def status_passed(data: dict[str, Any]) -> bool:
    if data.get("status") != "PASS":
        return False
    failures = data.get("failure_count", data.get("failures", 0))
    if isinstance(failures, list):
        failures = len(failures)
    return failures in (0, None)


def sidecar_line(zip_hash: str) -> str:
    return f"{zip_hash}  NDU_RL_OR.zip"


def read_zip() -> tuple[dict[str, bytes], list[str], str | None]:
    if not ZIP_PATH.exists():
        return {}, ["missing NDU_RL_OR.zip"], None
    files: dict[str, bytes] = {}
    errors: list[str] = []
    zip_hash = sha256(ZIP_PATH)
    with zipfile.ZipFile(ZIP_PATH) as zf:
        bad = zf.testzip()
        if bad is not None:
            errors.append(f"zip integrity failure at {bad}")
        for info in zf.infolist():
            if not info.is_dir():
                files[info.filename.rstrip("/")] = zf.read(info)
    return files, errors, zip_hash


def main() -> int:
    checks: list[dict[str, Any]] = []
    ledger = read_json(LEDGER_PATH) if LEDGER_PATH.exists() else {}
    zip_files, zip_errors, zip_hash = read_zip()
    present = set(zip_files)

    add(checks, "ledger_exists", LEDGER_PATH.exists(), str(LEDGER_PATH), "release-manifest parity ledger exists")
    add(checks, "ledger_round_is_r89", ledger.get("round") == "R89", ledger.get("round"), "R89")
    add(
        checks,
        "ledger_package_label_current",
        ledger.get("package_label") == "NDU_RL_OR_R89_release_manifest_parity",
        ledger.get("package_label"),
        "NDU_RL_OR_R89_release_manifest_parity",
    )

    root_files = set(ledger.get("required_root_files", []))
    missing_root = sorted(rel for rel in root_files if not (ROOT / rel).exists())
    add(checks, "required_root_files_exist", not missing_root, missing_root, "all release-manifest root files exist")

    add(checks, "zip_integrity", not zip_errors, zip_errors, [])
    sidecar_text = ZIP_SIDECAR.read_text(encoding="utf-8", errors="replace").strip() if ZIP_SIDECAR.exists() else ""
    add(
        checks,
        "zip_sidecar_matches_current_zip",
        bool(zip_hash and sidecar_text == sidecar_line(zip_hash)),
        sidecar_text,
        sidecar_line(zip_hash or "<missing-zip>"),
    )

    required_zip_entries = set(ledger.get("required_zip_entries", []))
    missing_zip = sorted(required_zip_entries - present)
    add(checks, "required_zip_entries_present", not missing_zip, missing_zip, "all release-manifest ZIP entries present")

    mismatched_zip_bytes: list[dict[str, Any]] = []
    for rel in sorted(required_zip_entries & present):
        root_path = ROOT / rel
        if not root_path.exists():
            mismatched_zip_bytes.append({"path": rel, "root": "missing", "zip": sha256_bytes(zip_files[rel])})
            continue
        root_hash = sha256(root_path)
        zip_entry_hash = sha256_bytes(zip_files[rel])
        if root_hash != zip_entry_hash:
            mismatched_zip_bytes.append({"path": rel, "root": root_hash, "zip": zip_entry_hash})
    add(checks, "required_zip_entry_bytes_match_root", not mismatched_zip_bytes, mismatched_zip_bytes[:25], "required ZIP entries match root bytes")

    bad_results: list[dict[str, Any]] = []
    stale_zip_bound_results: list[dict[str, Any]] = []
    result_summary: dict[str, Any] = {}
    for rel in sorted(ledger.get("required_pass_results", [])):
        path = ROOT / rel
        if not path.exists():
            bad_results.append({"path": rel, "status": "MISSING"})
            continue
        data = read_json(path)
        result_summary[rel] = {"status": data.get("status"), "failure_count": data.get("failure_count", data.get("failures"))}
        if not status_passed(data):
            bad_results.append({"path": rel, **result_summary[rel]})
        if rel.startswith("artifact/ndu_or_") and "zip_sha256" in data and data.get("zip_sha256") != zip_hash:
            stale_zip_bound_results.append({"path": rel, "observed": data.get("zip_sha256"), "expected": zip_hash})
    add(checks, "required_pass_results_pass", not bad_results, bad_results, "all referenced local result JSON files report PASS")
    add(checks, "zip_bound_results_use_current_zip", not stale_zip_bound_results, stale_zip_bound_results, "ZIP-bound results use current ZIP SHA256")

    package_ledger = read_json("artifact/ndu_or_package_hash_ledger_check_results.json")
    ledger_files = package_ledger.get("files", {})
    required_hash_rows = {
        "artifact/ndu_or_release_manifest_parity_ledger.json",
        "artifact/ndu_or_release_manifest_parity_check.py",
        "artifact/ndu_or_root_zip_forensic_parity_check.py",
        "artifact/ndu_or_zip_source_result_partition_check.py",
        "artifact/ndu_or_reviewer_handoff_index.json",
    }
    missing_hash_rows = sorted(required_hash_rows - set(ledger_files))
    stale_hash_rows: list[dict[str, Any]] = []
    for rel in sorted(required_hash_rows & set(ledger_files)):
        current = {"bytes": (ROOT / rel).stat().st_size, "sha256": sha256(ROOT / rel)}
        recorded = ledger_files[rel]
        if {"bytes": recorded.get("bytes"), "sha256": recorded.get("sha256")} != current:
            stale_hash_rows.append({"path": rel, "ledger": recorded, "current": current})
    add(checks, "package_hash_ledger_lists_release_sources", not missing_hash_rows, missing_hash_rows, "release-manifest sources listed in package hash ledger")
    add(checks, "package_hash_ledger_hashes_current", not stale_hash_rows, stale_hash_rows[:25], "release-manifest ledger rows match current files")
    add(
        checks,
        "package_hash_ledger_passed",
        status_passed(package_ledger),
        {"status": package_ledger.get("status"), "failure_count": package_ledger.get("failure_count")},
        "PASS with zero failures",
    )

    handoff = read_json("artifact/ndu_or_reviewer_handoff_index.json")
    handoff_rows = {row.get("id"): row for row in handoff.get("handoff_rows", []) if isinstance(row, dict)}
    release_row = handoff_rows.get("release_manifest_parity_gate", {})
    add(checks, "reviewer_handoff_lists_release_gate", bool(release_row), release_row, "release_manifest_parity_gate row present")
    add(checks, "reviewer_handoff_round_is_r89", handoff.get("round") == "R89", handoff.get("round"), "R89")

    checklist = (ROOT / "NDU_OR_submission_checklist.md").read_text(encoding="utf-8", errors="replace")
    status_text = (ROOT / "draft" / "referee-loop-status.md").read_text(encoding="utf-8", errors="replace")
    combined = checklist + "\n" + status_text + "\n" + json.dumps(ledger, sort_keys=True)
    missing_phrases = [phrase for phrase in ledger.get("required_boundary_phrases", []) if phrase not in combined]
    add(checks, "boundary_phrases_present", not missing_phrases, missing_phrases, "R89 release-manifest parity and local-only boundary phrases")

    failures = [check for check in checks if not check["ok"]]
    report = {
        "kind": "ndu_or_release_manifest_parity_check",
        "status": "PASS" if not failures else "FAIL",
        "check_count": len(checks),
        "failure_count": len(failures),
        "zip_sha256": zip_hash,
        "zip_sidecar_sha256": sha256(ZIP_SIDECAR) if ZIP_SIDECAR.exists() else None,
        "ledger_sha256": sha256(LEDGER_PATH) if LEDGER_PATH.exists() else None,
        "checker_sha256": sha256(ROOT / "artifact" / "ndu_or_release_manifest_parity_check.py"),
        "package_hash_ledger_sha256": sha256(ROOT / "artifact" / "ndu_or_package_hash_ledger_check_results.json"),
        "referenced_results": result_summary,
        "zip_entries": len(present),
        "checks": checks,
        "nonclaim": "Local release-manifest parity audit only; not full PyTorch/CEM regeneration, independent reproduction, external validation, external review, submission, upload, acceptance, or Strong Accept evidence.",
    }
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    lines = [
        "# NDU OR release-manifest parity check",
        "",
        f"Status: **{report['status']}**",
        "",
        f"- Checks: `{report['check_count']}`",
        f"- Failures: `{report['failure_count']}`",
        f"- ZIP entries: `{report['zip_entries']}`",
        f"- ZIP SHA256: `{report['zip_sha256']}`",
        f"- Ledger SHA256: `{report['ledger_sha256']}`",
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
