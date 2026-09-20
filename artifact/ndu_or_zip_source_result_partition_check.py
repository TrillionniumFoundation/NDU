#!/usr/bin/env python3
"""Audit the NDU OR ZIP source/result partition.

The gate verifies that the distributable ZIP carries source-side audit scripts,
static handoff ledgers, manuscript files, and approved reproducibility evidence,
while mutable local result-output files remain root-side only.  It is a local
package-boundary check, not an external review or submission claim.
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
OUT_JSON = ROOT / "artifact" / "ndu_or_zip_source_result_partition_check_results.json"
OUT_MD = ROOT / "artifact" / "ndu_or_zip_source_result_partition_check_results.md"

REQUIRED_SOURCE_ENTRIES = {
    "main.tex",
    "main.pdf",
    "NDU_OR_submission_checklist.md",
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
    "artifact/ndu_or_positioning_results.md",
    "reproducibility/check_ndu_reproducibility.py",
    "reproducibility/check_ndu_reproducibility_results.json",
    "reproducibility/manifest.json",
}

ROOT_ONLY_RESULT_OUTPUTS = {
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

REQUIRED_CHECKLIST_PHRASES = [
    "R87",
    "R88",
    "R89",
    "ZIP source/result partition",
    "root/ZIP forensic parity",
    "release-manifest parity",
    "artifact/ndu_or_zip_source_result_partition_check.py",
    "artifact/ndu_or_root_zip_forensic_parity_check.py",
    "artifact/ndu_or_release_manifest_parity_check.py",
    "local package/evidence",
    "no external review",
    "submission",
    "upload",
    "acceptance",
    "Strong Accept",
]


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def add(checks: list[dict[str, Any]], name: str, ok: bool, observed: Any, expected: Any) -> None:
    checks.append({"name": name, "ok": bool(ok), "observed": observed, "expected": expected})


def sidecar_line(zip_hash: str) -> str:
    return f"{zip_hash}  NDU_RL_OR.zip"


def read_zip() -> tuple[dict[str, bytes], list[str], str | None]:
    files: dict[str, bytes] = {}
    errors: list[str] = []
    if not ZIP_PATH.exists():
        return files, ["missing NDU_RL_OR.zip"], None
    zip_hash = sha256(ZIP_PATH)
    with zipfile.ZipFile(ZIP_PATH) as zf:
        bad = zf.testzip()
        if bad is not None:
            errors.append(f"zip integrity failure at {bad}")
        for info in zf.infolist():
            if not info.is_dir():
                files[info.filename.rstrip("/")] = zf.read(info)
    return files, errors, zip_hash


def is_mutable_result_output(name: str) -> bool:
    return name.startswith("artifact/ndu_or_") and (
        name.endswith("_check_results.json") or name.endswith("_check_results.md")
    )


def main() -> int:
    files, zip_errors, zip_hash = read_zip()
    present = set(files)
    checks: list[dict[str, Any]] = []

    add(checks, "zip_integrity", not zip_errors, zip_errors, [])

    sidecar_text = ZIP_SIDECAR.read_text(encoding="utf-8", errors="replace").strip() if ZIP_SIDECAR.exists() else ""
    add(
        checks,
        "zip_sidecar_matches_current_zip",
        bool(zip_hash and sidecar_text == sidecar_line(zip_hash)),
        sidecar_text,
        sidecar_line(zip_hash or "<missing-zip>"),
    )

    missing_source = sorted(REQUIRED_SOURCE_ENTRIES - present)
    add(checks, "required_source_entries_present", not missing_source, missing_source, "all required source-side entries in ZIP")

    leaked_results = sorted(ROOT_ONLY_RESULT_OUTPUTS & present)
    add(checks, "root_only_result_outputs_excluded", not leaked_results, leaked_results, "mutable local result outputs are not in ZIP")

    unexpected_mutable = sorted(name for name in present if is_mutable_result_output(name) and name not in ROOT_ONLY_RESULT_OUTPUTS)
    add(checks, "no_unclassified_mutable_result_outputs", not unexpected_mutable, unexpected_mutable, "no unclassified mutable result outputs in ZIP")

    missing_root_results = sorted(
        rel
        for rel in ROOT_ONLY_RESULT_OUTPUTS
        if not rel.endswith("zip_source_result_partition_check_results.json")
        and not rel.endswith("zip_source_result_partition_check_results.md")
        and not rel.endswith("root_zip_forensic_parity_check_results.json")
        and not rel.endswith("root_zip_forensic_parity_check_results.md")
        and not rel.endswith("release_manifest_parity_check_results.json")
        and not rel.endswith("release_manifest_parity_check_results.md")
        and not (ROOT / rel).exists()
    )
    add(checks, "root_side_result_outputs_present", not missing_root_results, missing_root_results, "non-self root-only result outputs exist at root")

    mismatched_source_hashes: list[dict[str, Any]] = []
    for rel in sorted(REQUIRED_SOURCE_ENTRIES & present):
        root_path = ROOT / rel
        if not root_path.exists():
            mismatched_source_hashes.append({"path": rel, "root": "missing", "zip": sha256_bytes(files[rel])})
            continue
        root_hash = sha256(root_path)
        zip_entry_hash = sha256_bytes(files[rel])
        if root_hash != zip_entry_hash:
            mismatched_source_hashes.append({"path": rel, "root": root_hash, "zip": zip_entry_hash})
    add(checks, "source_entry_bytes_match_root", not mismatched_source_hashes, mismatched_source_hashes[:25], "required source entries match root bytes")

    checklist = (ROOT / "NDU_OR_submission_checklist.md").read_text(encoding="utf-8", errors="replace")
    missing_phrases = [phrase for phrase in REQUIRED_CHECKLIST_PHRASES if phrase not in checklist]
    add(checks, "checklist_mentions_r89_partition_boundary", not missing_phrases, missing_phrases, "R89 release-manifest parity, R87 partition, and local-only boundary phrases")

    failures = [check for check in checks if not check["ok"]]
    report = {
        "kind": "ndu_or_zip_source_result_partition_check",
        "status": "PASS" if not failures else "FAIL",
        "check_count": len(checks),
        "failure_count": len(failures),
        "zip_sha256": zip_hash,
        "zip_sidecar_sha256": sha256(ZIP_SIDECAR) if ZIP_SIDECAR.exists() else None,
        "checker_sha256": sha256(ROOT / "artifact" / "ndu_or_zip_source_result_partition_check.py"),
        "zip_entries": len(present),
        "required_source_entries": sorted(REQUIRED_SOURCE_ENTRIES),
        "root_only_result_outputs": sorted(ROOT_ONLY_RESULT_OUTPUTS),
        "checks": checks,
        "nonclaim": "Local ZIP source/result partition audit only; not full PyTorch/CEM regeneration, independent reproduction, external validation, external review, submission, upload, acceptance, or Strong Accept evidence.",
    }
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    lines = [
        "# NDU OR ZIP source/result partition check",
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
