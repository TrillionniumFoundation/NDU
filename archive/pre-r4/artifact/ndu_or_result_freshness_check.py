#!/usr/bin/env python3
"""Audit freshness of generated NDU OR result ledgers.

The gate verifies that local audit result JSON files still refer to the
current checker scripts, current ZIP hash, current ZIP sidecar, and current
package hash ledger.  It is a local anti-staleness check, not an external
review or regeneration claim.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
OUT_JSON = ROOT / "artifact" / "ndu_or_result_freshness_check_results.json"
OUT_MD = ROOT / "artifact" / "ndu_or_result_freshness_check_results.md"
ZIP_PATH = ROOT / "NDU_RL_OR.zip"
ZIP_SIDECAR = ROOT / "NDU_RL_OR.zip.sha256"
PACKAGE_LEDGER_JSON = ROOT / "artifact" / "ndu_or_package_hash_ledger_check_results.json"

RESULT_PAIRS = {
    "reproducibility": (
        "reproducibility/check_ndu_reproducibility.py",
        "reproducibility/check_ndu_reproducibility_results.json",
    ),
    "or_positioning": (
        "artifact/ndu_or_positioning_check.py",
        "artifact/ndu_or_positioning_results.json",
    ),
    "zip_closure": (
        "artifact/ndu_or_zip_closure_check.py",
        "artifact/ndu_or_zip_closure_check_results.json",
    ),
    "package_hash_ledger": (
        "artifact/ndu_or_package_hash_ledger_check.py",
        "artifact/ndu_or_package_hash_ledger_check_results.json",
    ),
    "extracted_hash_ledger_replay": (
        "artifact/ndu_or_extracted_hash_ledger_replay_check.py",
        "artifact/ndu_or_extracted_hash_ledger_replay_check_results.json",
    ),
    "external_boundary_scan": (
        "artifact/ndu_or_external_boundary_scan_check.py",
        "artifact/ndu_or_external_boundary_scan_check_results.json",
    ),
    "reviewer_handoff_index": (
        "artifact/ndu_or_reviewer_handoff_index_check.py",
        "artifact/ndu_or_reviewer_handoff_index_check_results.json",
    ),
    "zip_source_result_partition": (
        "artifact/ndu_or_zip_source_result_partition_check.py",
        "artifact/ndu_or_zip_source_result_partition_check_results.json",
    ),
    "root_zip_forensic_parity": (
        "artifact/ndu_or_root_zip_forensic_parity_check.py",
        "artifact/ndu_or_root_zip_forensic_parity_check_results.json",
    ),
    "release_manifest_parity": (
        "artifact/ndu_or_release_manifest_parity_check.py",
        "artifact/ndu_or_release_manifest_parity_check_results.json",
    ),
}

HASH_LEDGER_REQUIRED_TARGETS = {
    "main.tex",
    "main.pdf",
    "NDU_RL_OR.zip",
    "NDU_RL_OR.zip.sha256",
    "NDU_OR_submission_checklist.md",
    "reproducibility/check_ndu_reproducibility.py",
    "reproducibility/check_ndu_reproducibility_results.json",
    "artifact/ndu_or_positioning_check.py",
    "artifact/ndu_or_positioning_results.json",
    "artifact/ndu_or_zip_closure_check.py",
    "artifact/ndu_or_zip_closure_check_results.json",
    "artifact/ndu_or_package_hash_ledger_check.py",
    "artifact/ndu_or_extracted_hash_ledger_replay_check.py",
    "artifact/ndu_or_external_boundary_scan_check.py",
    "artifact/ndu_or_external_boundary_scan_check_results.json",
    "artifact/ndu_or_result_freshness_check.py",
    "artifact/ndu_or_reviewer_handoff_index.json",
    "artifact/ndu_or_reviewer_handoff_index_check.py",
    "artifact/ndu_or_zip_source_result_partition_check.py",
    "artifact/ndu_or_zip_source_result_partition_check_results.json",
    "artifact/ndu_or_root_zip_forensic_parity_check.py",
    "artifact/ndu_or_release_manifest_parity_ledger.json",
    "artifact/ndu_or_release_manifest_parity_check.py",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8", errors="replace"))


def add(checks: list[dict[str, Any]], name: str, ok: bool, observed: Any, expected: Any) -> None:
    checks.append({"name": name, "ok": bool(ok), "observed": observed, "expected": expected})


def status_passed(data: dict[str, Any]) -> bool:
    if data.get("status") != "PASS":
        return False
    if data.get("failure_count", 0) not in (0, None):
        return False
    failures = data.get("failures")
    if isinstance(failures, list) and failures:
        return False
    if isinstance(failures, int) and failures != 0:
        return False
    return True


def current_file_meta(rel: str) -> dict[str, Any] | None:
    path = ROOT / rel
    if not path.exists():
        return None
    return {"bytes": path.stat().st_size, "sha256": sha256(path)}


def sidecar_line(zip_hash: str) -> str:
    return f"{zip_hash}  NDU_RL_OR.zip"


def main() -> int:
    checks: list[dict[str, Any]] = []
    scripts_missing: list[str] = []
    results_missing: list[str] = []
    result_data: dict[str, dict[str, Any]] = {}

    for name, (script_rel, result_rel) in RESULT_PAIRS.items():
        if not (ROOT / script_rel).exists():
            scripts_missing.append(script_rel)
        result_path = ROOT / result_rel
        if not result_path.exists():
            results_missing.append(result_rel)
        else:
            result_data[name] = read_json(result_path)

    add(checks, "checker_scripts_exist", not scripts_missing, scripts_missing, "all freshness target checker scripts exist")
    add(checks, "result_json_files_exist", not results_missing, results_missing, "all freshness target result JSON files exist")

    status_summary = {
        name: {
            "status": data.get("status"),
            "failure_count": data.get("failure_count", len(data.get("failures", [])) if isinstance(data.get("failures"), list) else data.get("failures")),
        }
        for name, data in sorted(result_data.items())
    }
    add(checks, "all_target_results_passed", all(status_passed(data) for data in result_data.values()) and len(result_data) == len(RESULT_PAIRS), status_summary, "PASS with zero failures for every target result")

    zip_hash = sha256(ZIP_PATH) if ZIP_PATH.exists() else None
    sidecar_text = ZIP_SIDECAR.read_text(encoding="utf-8", errors="replace").strip() if ZIP_SIDECAR.exists() else ""
    add(
        checks,
        "zip_sidecar_matches_current_zip",
        bool(zip_hash and sidecar_text == sidecar_line(zip_hash)),
        sidecar_text,
        sidecar_line(zip_hash or "<missing-zip>"),
    )

    zip_bound_results = {
        "zip_closure": result_data.get("zip_closure", {}),
        "external_boundary_scan": result_data.get("external_boundary_scan", {}),
        "extracted_hash_ledger_replay": result_data.get("extracted_hash_ledger_replay", {}),
        "reviewer_handoff_index": result_data.get("reviewer_handoff_index", {}),
        "zip_source_result_partition": result_data.get("zip_source_result_partition", {}),
        "root_zip_forensic_parity": result_data.get("root_zip_forensic_parity", {}),
        "release_manifest_parity": result_data.get("release_manifest_parity", {}),
    }
    add(
        checks,
        "zip_bound_results_use_current_zip_hash",
        all(data.get("zip_sha256") == zip_hash for data in zip_bound_results.values()),
        {name: data.get("zip_sha256") for name, data in sorted(zip_bound_results.items())},
        zip_hash,
    )

    external = result_data.get("external_boundary_scan", {})
    add(
        checks,
        "external_boundary_result_uses_current_checker",
        external.get("checker_sha256") == sha256(ROOT / "artifact" / "ndu_or_external_boundary_scan_check.py"),
        external.get("checker_sha256"),
        sha256(ROOT / "artifact" / "ndu_or_external_boundary_scan_check.py"),
    )

    extracted = result_data.get("extracted_hash_ledger_replay", {})
    package_ledger_hash = sha256(PACKAGE_LEDGER_JSON) if PACKAGE_LEDGER_JSON.exists() else None
    add(
        checks,
        "extracted_replay_uses_current_package_hash_ledger",
        extracted.get("package_hash_ledger_sha256") == package_ledger_hash,
        extracted.get("package_hash_ledger_sha256"),
        package_ledger_hash,
    )

    package_ledger = result_data.get("package_hash_ledger", {})
    ledger_files = package_ledger.get("files", {})
    missing_targets = sorted(HASH_LEDGER_REQUIRED_TARGETS - set(ledger_files))
    stale_targets: list[dict[str, Any]] = []
    for rel in sorted(set(ledger_files) | HASH_LEDGER_REQUIRED_TARGETS):
        meta = ledger_files.get(rel)
        current = current_file_meta(rel)
        if rel in HASH_LEDGER_REQUIRED_TARGETS and meta is None:
            continue
        if meta is None or current is None:
            stale_targets.append({"path": rel, "ledger": meta, "current": current})
            continue
        if {"bytes": meta.get("bytes"), "sha256": meta.get("sha256")} != current:
            stale_targets.append({"path": rel, "ledger": meta, "current": current})
    add(checks, "package_hash_ledger_lists_r89_targets", not missing_targets, missing_targets, "all R89 release-manifest/handoff/freshness targets listed in package hash ledger")
    add(checks, "package_hash_ledger_hashes_match_current_files", not stale_targets, stale_targets[:25], "ledger hashes and byte counts match current files")

    checklist = (ROOT / "NDU_OR_submission_checklist.md").read_text(encoding="utf-8", errors="replace")
    required_phrases = [
        "R85",
        "R86",
        "R87",
        "R88",
        "R89",
        "reviewer handoff index",
        "ZIP source/result partition",
        "root/ZIP forensic parity",
        "release-manifest parity",
        "artifact/ndu_or_zip_source_result_partition_check.py",
        "artifact/ndu_or_root_zip_forensic_parity_check.py",
        "artifact/ndu_or_release_manifest_parity_check.py",
        "artifact/ndu_or_reviewer_handoff_index.json",
        "result-freshness gate",
        "current checker/result hashes",
        "local package/evidence",
        "no external review",
        "submission",
        "acceptance",
        "Strong Accept",
    ]
    missing_phrases = [phrase for phrase in required_phrases if phrase not in checklist]
    add(checks, "checklist_mentions_r89_handoff_freshness_boundary", not missing_phrases, missing_phrases, "R89 release-manifest parity, R88 forensic parity, R85 freshness gate, and local-only boundary phrases")

    failures = [check for check in checks if not check["ok"]]
    report = {
        "kind": "ndu_or_result_freshness_check",
        "status": "PASS" if not failures else "FAIL",
        "check_count": len(checks),
        "failure_count": len(failures),
        "zip_sha256": zip_hash,
        "zip_sidecar_sha256": sha256(ZIP_SIDECAR) if ZIP_SIDECAR.exists() else None,
        "package_hash_ledger_sha256": package_ledger_hash,
        "checker_sha256": sha256(ROOT / "artifact" / "ndu_or_result_freshness_check.py"),
        "target_results": {
            name: {
                "script": script_rel,
                "script_sha256": sha256(ROOT / script_rel) if (ROOT / script_rel).exists() else None,
                "result": result_rel,
                "result_sha256": sha256(ROOT / result_rel) if (ROOT / result_rel).exists() else None,
                "status": result_data.get(name, {}).get("status"),
            }
            for name, (script_rel, result_rel) in sorted(RESULT_PAIRS.items())
        },
        "checks": checks,
        "nonclaim": "Local result-freshness, release-manifest parity, reviewer handoff, and anti-staleness audit only; not full PyTorch/CEM regeneration, independent reproduction, external review, submission, upload, acceptance, or Strong Accept evidence.",
    }
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    lines = [
        "# NDU OR result-freshness check",
        "",
        f"Status: **{report['status']}**",
        "",
        f"- Checks: `{report['check_count']}`",
        f"- Failures: `{report['failure_count']}`",
        f"- ZIP SHA256: `{report['zip_sha256']}`",
        f"- Package hash-ledger JSON SHA256: `{report['package_hash_ledger_sha256']}`",
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
