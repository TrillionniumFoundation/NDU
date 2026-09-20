#!/usr/bin/env python3
"""Audit the NDU OR reviewer handoff index.

The handoff index is a local reviewer-facing map of package files, audit
results, replay order, ZIP sidecar, and boundary wording.  This checker verifies
that the map is internally usable and current against the local package tree.
It is not an external review or submission claim.
"""

from __future__ import annotations

import hashlib
import json
import zipfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
INDEX_PATH = ROOT / "artifact" / "ndu_or_reviewer_handoff_index.json"
OUT_JSON = ROOT / "artifact" / "ndu_or_reviewer_handoff_index_check_results.json"
OUT_MD = ROOT / "artifact" / "ndu_or_reviewer_handoff_index_check_results.md"
ZIP_PATH = ROOT / "NDU_RL_OR.zip"
ZIP_SIDECAR = ROOT / "NDU_RL_OR.zip.sha256"

REQUIRED_ROW_IDS = {
    "manuscript_tex_pdf",
    "reproducibility_gate",
    "or_positioning_gate",
    "zip_closure_gate",
    "external_boundary_scan_gate",
    "package_hash_ledger_gate",
    "extracted_hash_ledger_replay_gate",
    "result_freshness_gate",
    "reviewer_handoff_index_gate",
    "zip_source_result_partition_gate",
    "root_zip_forensic_parity_gate",
    "release_manifest_parity_gate",
    "zip_sidecar",
    "checklist_status",
}

REQUIRED_CHECKLIST_PHRASES = [
    "R86",
    "R88",
    "R89",
    "reviewer handoff index",
    "ZIP source/result partition",
    "release-manifest parity",
    "artifact/ndu_or_zip_source_result_partition_check.py",
    "artifact/ndu_or_root_zip_forensic_parity_check.py",
    "artifact/ndu_or_release_manifest_parity_check.py",
    "artifact/ndu_or_reviewer_handoff_index.json",
    "artifact/ndu_or_reviewer_handoff_index_check.py",
    "local package/evidence",
    "no external review",
    "submission",
    "upload",
    "acceptance",
    "Strong Accept",
]

REQUIRED_ZIP_ENTRIES = {
    "artifact/ndu_or_reviewer_handoff_index.json",
    "artifact/ndu_or_reviewer_handoff_index_check.py",
    "artifact/ndu_or_result_freshness_check.py",
    "artifact/ndu_or_zip_closure_check.py",
    "artifact/ndu_or_package_hash_ledger_check.py",
    "artifact/ndu_or_extracted_hash_ledger_replay_check.py",
    "artifact/ndu_or_external_boundary_scan_check.py",
    "artifact/ndu_or_zip_source_result_partition_check.py",
    "artifact/ndu_or_root_zip_forensic_parity_check.py",
    "artifact/ndu_or_release_manifest_parity_ledger.json",
    "artifact/ndu_or_release_manifest_parity_check.py",
    "reproducibility/check_ndu_reproducibility_results.json",
    "NDU_OR_submission_checklist.md",
    "main.tex",
    "main.pdf",
}

DEFERRED_RESULT_ROWS = {
    # This gate uses the handoff index result as one of its inputs, so the
    # handoff checker validates the row/files but leaves the result currentness
    # check to the final freshness gate.
    "root_zip_forensic_parity_gate",
}


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8", errors="replace"))


def add(checks: list[dict[str, Any]], name: str, ok: bool, observed: Any, expected: Any) -> None:
    checks.append({"name": name, "ok": bool(ok), "observed": observed, "expected": expected})


def status_passed(data: dict[str, Any]) -> bool:
    if data.get("status") != "PASS":
        return False
    failure_count = data.get("failure_count")
    if isinstance(failure_count, int) and failure_count != 0:
        return False
    failures = data.get("failures")
    if isinstance(failures, list) and failures:
        return False
    if isinstance(failures, int) and failures != 0:
        return False
    return True


def sidecar_line(zip_hash: str) -> str:
    return f"{zip_hash}  NDU_RL_OR.zip"


def zip_entries() -> tuple[set[str], list[str], str | None]:
    errors: list[str] = []
    if not ZIP_PATH.exists():
        return set(), ["missing NDU_RL_OR.zip"], None
    zip_hash = sha256(ZIP_PATH)
    names: set[str] = set()
    with zipfile.ZipFile(ZIP_PATH) as zf:
        bad = zf.testzip()
        if bad is not None:
            errors.append(f"zip integrity failure at {bad}")
        for info in zf.infolist():
            if not info.is_dir():
                names.add(info.filename.rstrip("/"))
    return names, errors, zip_hash


def main() -> int:
    checks: list[dict[str, Any]] = []
    index = read_json(INDEX_PATH) if INDEX_PATH.exists() else {}

    add(checks, "index_exists", INDEX_PATH.exists(), str(INDEX_PATH), "reviewer handoff index JSON exists")
    add(checks, "index_round_is_r89", index.get("round") == "R89", index.get("round"), "R89")

    rows = index.get("handoff_rows", [])
    rows_by_id = {row.get("id"): row for row in rows if isinstance(row, dict)}
    missing_rows = sorted(REQUIRED_ROW_IDS - set(rows_by_id))
    add(checks, "required_rows_present", not missing_rows, missing_rows, "all reviewer handoff rows present")

    replay_order = index.get("replay_order", [])
    missing_replay = sorted(REQUIRED_ROW_IDS - set(replay_order))
    add(checks, "replay_order_covers_rows", not missing_replay, missing_replay, "replay order covers all required rows")

    all_files: set[str] = set()
    missing_files: list[str] = []
    for row in rows_by_id.values():
        for rel in row.get("files", []):
            all_files.add(rel)
            if not (ROOT / rel).exists():
                missing_files.append(rel)
    add(checks, "handoff_files_exist", not missing_files, missing_files, "all files referenced by handoff rows exist")

    result_statuses: dict[str, Any] = {}
    stale_zip_results: list[dict[str, Any]] = []
    current_zip_hash = sha256(ZIP_PATH) if ZIP_PATH.exists() else None
    for row_id, row in sorted(rows_by_id.items()):
        result_rel = row.get("result_json")
        if not result_rel:
            continue
        result_path = ROOT / result_rel
        if not result_path.exists():
            result_statuses[row_id] = {"missing": result_rel}
            continue
        result = read_json(result_path)
        result_statuses[row_id] = {
            "result": result_rel,
            "status": result.get("status"),
            "failure_count": result.get("failure_count"),
        }
        if row_id in DEFERRED_RESULT_ROWS:
            continue
        if row.get("zip_bound") and current_zip_hash and result.get("zip_sha256") != current_zip_hash:
            stale_zip_results.append(
                {
                    "row": row_id,
                    "result": result_rel,
                    "observed": result.get("zip_sha256"),
                    "expected": current_zip_hash,
                }
            )
    result_failures = [
        {"row": row_id, **summary}
        for row_id, summary in result_statuses.items()
        if row_id not in DEFERRED_RESULT_ROWS
        if summary.get("missing") or summary.get("status") != "PASS" or summary.get("failure_count") not in (0, None)
    ]
    add(checks, "referenced_results_pass", not result_failures, result_failures, "all referenced result JSON files report PASS")
    add(checks, "zip_bound_results_current", not stale_zip_results, stale_zip_results, "zip-bound result JSON files use current ZIP SHA256")

    sidecar_text = ZIP_SIDECAR.read_text(encoding="utf-8", errors="replace").strip() if ZIP_SIDECAR.exists() else ""
    add(
        checks,
        "zip_sidecar_matches_current_zip",
        bool(current_zip_hash and sidecar_text == sidecar_line(current_zip_hash)),
        sidecar_text,
        sidecar_line(current_zip_hash or "<missing-zip>"),
    )

    package_ledger = read_json(ROOT / "artifact" / "ndu_or_package_hash_ledger_check_results.json")
    ledger_files = set(package_ledger.get("files", {}))
    required_ledger_files = {
        "artifact/ndu_or_reviewer_handoff_index.json",
        "artifact/ndu_or_reviewer_handoff_index_check.py",
        "artifact/ndu_or_zip_source_result_partition_check.py",
        "artifact/ndu_or_root_zip_forensic_parity_check.py",
        "artifact/ndu_or_release_manifest_parity_ledger.json",
        "artifact/ndu_or_release_manifest_parity_check.py",
        "artifact/ndu_or_zip_source_result_partition_check_results.json",
    }
    add(
        checks,
        "package_hash_ledger_lists_handoff_files",
        required_ledger_files <= ledger_files,
        sorted(required_ledger_files - ledger_files),
        "handoff index and checker listed in package hash ledger",
    )
    add(
        checks,
        "package_hash_ledger_passed",
        status_passed(package_ledger),
        {"status": package_ledger.get("status"), "failure_count": package_ledger.get("failure_count")},
        "PASS with zero failures",
    )

    names, zip_errors, zip_hash = zip_entries()
    missing_zip_entries = sorted(REQUIRED_ZIP_ENTRIES - names)
    result_output_entries = sorted(
        name for name in names if name.startswith("artifact/ndu_or_reviewer_handoff_index_check_results.")
    )
    add(checks, "zip_integrity", not zip_errors, zip_errors, [])
    add(checks, "zip_contains_handoff_sources", not missing_zip_entries, missing_zip_entries, "all required handoff source entries present")
    add(checks, "zip_excludes_handoff_result_outputs", not result_output_entries, result_output_entries, "mutable handoff result outputs excluded from ZIP")

    checklist = (ROOT / "NDU_OR_submission_checklist.md").read_text(encoding="utf-8", errors="replace")
    missing_checklist_phrases = [phrase for phrase in REQUIRED_CHECKLIST_PHRASES if phrase not in checklist]
    add(
        checks,
        "checklist_mentions_r89_handoff_boundary",
        not missing_checklist_phrases,
        missing_checklist_phrases,
        "R89 release-manifest parity, reviewer handoff index, and local-only boundary phrases",
    )

    nonclaim_text = " ".join(
        [
            str(index.get("purpose", "")),
            str(index.get("nonclaim", "")),
            " ".join(index.get("required_boundary_phrases", [])),
        ]
    )
    missing_boundary = [
        phrase
        for phrase in ["local package/evidence", "no external review", "submission", "upload", "acceptance", "Strong Accept"]
        if phrase not in nonclaim_text
    ]
    add(checks, "index_boundary_phrases_present", not missing_boundary, missing_boundary, "index preserves boundary phrases")

    failures = [check for check in checks if not check["ok"]]
    report = {
        "kind": "ndu_or_reviewer_handoff_index_check",
        "status": "PASS" if not failures else "FAIL",
        "check_count": len(checks),
        "failure_count": len(failures),
        "zip_sha256": zip_hash,
        "zip_sidecar_sha256": sha256(ZIP_SIDECAR) if ZIP_SIDECAR.exists() else None,
        "index_sha256": sha256(INDEX_PATH) if INDEX_PATH.exists() else None,
        "checker_sha256": sha256(ROOT / "artifact" / "ndu_or_reviewer_handoff_index_check.py"),
        "package_hash_ledger_sha256": sha256(ROOT / "artifact" / "ndu_or_package_hash_ledger_check_results.json"),
        "referenced_results": result_statuses,
        "checks": checks,
        "nonclaim": "Local reviewer handoff index audit only; not full PyTorch/CEM regeneration, independent reproduction, external validation, external review, submission, upload, acceptance, or Strong Accept evidence.",
    }
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    lines = [
        "# NDU OR reviewer handoff index check",
        "",
        f"Status: **{report['status']}**",
        "",
        f"- Checks: `{report['check_count']}`",
        f"- Failures: `{report['failure_count']}`",
        f"- ZIP SHA256: `{report['zip_sha256']}`",
        f"- Index SHA256: `{report['index_sha256']}`",
        "",
        "## Checks",
        "",
    ]
    for check in checks:
        marker = "PASS" if check["ok"] else "FAIL"
        lines.append(f"- **{marker}** `{check['name']}`")
    lines += ["", report["nonclaim"]]
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({k: report[k] for k in ["status", "check_count", "failure_count", "zip_sha256"]}, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
