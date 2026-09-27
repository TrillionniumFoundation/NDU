#!/usr/bin/env python3
"""Audit the NDU OR package hash ledger and ZIP sidecar."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
OUT_JSON = ROOT / "artifact" / "ndu_or_package_hash_ledger_check_results.json"
OUT_MD = ROOT / "artifact" / "ndu_or_package_hash_ledger_check_results.md"
ZIP_SIDECAR = ROOT / "NDU_RL_OR.zip.sha256"

TARGETS = [
    "main.tex",
    "main.pdf",
    "NDU_RL_OR.zip",
    "NDU_RL_OR.zip.sha256",
    "NDU_OR_submission_checklist.md",
    "reproducibility/manifest.json",
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
]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def add(checks: list[dict[str, Any]], name: str, ok: bool, observed: Any, expected: Any) -> None:
    checks.append({"name": name, "ok": bool(ok), "observed": observed, "expected": expected})


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8", errors="replace"))


def main() -> int:
    files: dict[str, dict[str, Any]] = {}
    missing: list[str] = []
    for rel in TARGETS:
        path = ROOT / rel
        if not path.exists():
            missing.append(rel)
            continue
        files[rel] = {"bytes": path.stat().st_size, "sha256": sha256(path)}

    checks: list[dict[str, Any]] = []
    add(checks, "target_files_exist", not missing, missing, "all package hash-ledger targets exist")

    zip_hash = files.get("NDU_RL_OR.zip", {}).get("sha256")
    sidecar_text = ZIP_SIDECAR.read_text(encoding="utf-8", errors="replace") if ZIP_SIDECAR.exists() else ""
    add(checks, "zip_sidecar_matches_zip", bool(zip_hash and zip_hash in sidecar_text and "NDU_RL_OR.zip" in sidecar_text), sidecar_text.strip(), f"{zip_hash}  NDU_RL_OR.zip")

    repro = read_json(ROOT / "reproducibility" / "check_ndu_reproducibility_results.json")
    add(checks, "reproducibility_checker_passed", repro.get("status") == "PASS" and not repro.get("failures"), {"status": repro.get("status"), "failures": len(repro.get("failures", []))}, "PASS with zero failures")

    positioning = read_json(ROOT / "artifact" / "ndu_or_positioning_results.json")
    add(checks, "or_positioning_passed", positioning.get("status") == "PASS" and positioning.get("failures") == 0, {"status": positioning.get("status"), "failures": positioning.get("failures")}, "PASS with zero failures")

    zip_closure = read_json(ROOT / "artifact" / "ndu_or_zip_closure_check_results.json")
    add(checks, "zip_closure_passed", zip_closure.get("status") == "PASS" and zip_closure.get("failure_count") == 0, {"status": zip_closure.get("status"), "failure_count": zip_closure.get("failure_count"), "zip_sha256": zip_closure.get("zip_sha256")}, "PASS with zero failures")
    add(checks, "zip_closure_hash_matches_sidecar", zip_closure.get("zip_sha256") == zip_hash, zip_closure.get("zip_sha256"), zip_hash)

    boundary = read_json(ROOT / "artifact" / "ndu_or_external_boundary_scan_check_results.json")
    add(
        checks,
        "external_boundary_scan_passed",
        boundary.get("status") == "PASS" and boundary.get("failure_count") == 0,
        {"status": boundary.get("status"), "failure_count": boundary.get("failure_count")},
        "PASS with zero failures",
    )

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
        "R84",
        "external-boundary scan",
        "extracted hash-ledger replay",
        "package hash ledger",
        "local package/evidence",
        "no external review",
        "submission",
        "acceptance",
        "Strong Accept",
    ]
    missing_phrases = [phrase for phrase in required_phrases if phrase not in checklist]
    add(checks, "checklist_mentions_r89_release_boundary", not missing_phrases, missing_phrases, "R89 release-manifest parity, R86 reviewer handoff, R85 result-freshness gate, R84 external-boundary scan, and boundary phrases")

    failures = [check for check in checks if not check["ok"]]
    report = {
        "kind": "ndu_or_package_hash_ledger_check",
        "status": "PASS" if not failures else "FAIL",
        "check_count": len(checks),
        "failure_count": len(failures),
        "files": files,
        "checks": checks,
        "nonclaim": "Local package hash-ledger, sidecar, release-manifest parity, external-boundary, result-freshness, and reviewer handoff index audit only; not full PyTorch/CEM regeneration, independent reproduction, external review, submission, acceptance, or Strong Accept evidence.",
    }
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = [
        "# NDU OR package hash ledger check",
        "",
        f"Status: **{report['status']}**",
        "",
        f"- Checks: `{report['check_count']}`",
        f"- Failures: `{report['failure_count']}`",
        f"- ZIP SHA256: `{zip_hash}`",
        "",
        "## Files",
        "",
    ]
    for rel, meta in files.items():
        lines.append(f"- `{rel}`: `{meta['sha256']}` ({meta['bytes']} bytes)")
    lines += ["", report["nonclaim"]]
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({k: report[k] for k in ["status", "check_count", "failure_count"]}, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
