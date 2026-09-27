#!/usr/bin/env python3
"""Replay the NDU OR package hash ledger after ZIP extraction."""

from __future__ import annotations

import hashlib
import json
import tempfile
import zipfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ZIP_PATH = ROOT / "NDU_RL_OR.zip"
ZIP_SIDECAR = ROOT / "NDU_RL_OR.zip.sha256"
HASH_LEDGER_JSON = ROOT / "artifact" / "ndu_or_package_hash_ledger_check_results.json"
ZIP_CLOSURE_JSON = ROOT / "artifact" / "ndu_or_zip_closure_check_results.json"
OUT_JSON = ROOT / "artifact" / "ndu_or_extracted_hash_ledger_replay_check_results.json"
OUT_MD = ROOT / "artifact" / "ndu_or_extracted_hash_ledger_replay_check_results.md"

CRITICAL_ZIP_ENTRIES = {
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
    "artifact/ndu_or_positioning_results.json",
    "reproducibility/check_ndu_reproducibility_results.json",
    "reproducibility/manifest.json",
    "NDU_OR_submission_checklist.md",
    "main.tex",
    "main.pdf",
}


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8", errors="replace"))


def add(checks: list[dict[str, Any]], name: str, ok: bool, observed: Any, expected: Any) -> None:
    checks.append({"name": name, "ok": bool(ok), "observed": observed, "expected": expected})


def sidecar_expected_line(zip_hash: str) -> str:
    return f"{zip_hash}  NDU_RL_OR.zip"


def read_zip_bytes() -> tuple[dict[str, bytes], list[str]]:
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


def extracted_hashes(zip_entries: dict[str, bytes]) -> dict[str, str]:
    with tempfile.TemporaryDirectory(prefix="ndu_or_r83_extract_") as tmp:
        extract_root = Path(tmp)
        with zipfile.ZipFile(ZIP_PATH) as zf:
            zf.extractall(extract_root)
        return {
            rel: sha256(extract_root / rel)
            for rel in sorted(zip_entries)
            if (extract_root / rel).is_file()
        }


def main() -> int:
    checks: list[dict[str, Any]] = []
    zip_hash = sha256(ZIP_PATH) if ZIP_PATH.exists() else None
    sidecar_text = ZIP_SIDECAR.read_text(encoding="utf-8", errors="replace").strip() if ZIP_SIDECAR.exists() else ""

    add(
        checks,
        "root_zip_sidecar_matches_zip",
        bool(zip_hash and sidecar_text == sidecar_expected_line(zip_hash)),
        sidecar_text,
        sidecar_expected_line(zip_hash or "<missing-zip>"),
    )

    ledger = read_json(HASH_LEDGER_JSON) if HASH_LEDGER_JSON.exists() else {}
    add(
        checks,
        "root_package_hash_ledger_passed",
        ledger.get("status") == "PASS" and ledger.get("failure_count") == 0,
        {"status": ledger.get("status"), "failure_count": ledger.get("failure_count")},
        "PASS with zero failures",
    )

    ledger_files = ledger.get("files", {})
    stale_ledger_entries: list[dict[str, Any]] = []
    for rel, meta in sorted(ledger_files.items()):
        path = ROOT / rel
        if not path.exists():
            stale_ledger_entries.append({"path": rel, "observed": "missing", "expected": meta})
            continue
        observed = {"bytes": path.stat().st_size, "sha256": sha256(path)}
        if observed != {"bytes": meta.get("bytes"), "sha256": meta.get("sha256")}:
            stale_ledger_entries.append({"path": rel, "observed": observed, "expected": meta})
    add(checks, "ledger_file_hashes_match_root", not stale_ledger_entries, stale_ledger_entries[:25], "all ledger file hashes match current root files")

    closure = read_json(ZIP_CLOSURE_JSON) if ZIP_CLOSURE_JSON.exists() else {}
    add(
        checks,
        "zip_closure_record_matches_zip",
        closure.get("status") == "PASS" and closure.get("failure_count") == 0 and closure.get("zip_sha256") == zip_hash,
        {"status": closure.get("status"), "failure_count": closure.get("failure_count"), "zip_sha256": closure.get("zip_sha256")},
        {"status": "PASS", "failure_count": 0, "zip_sha256": zip_hash},
    )

    zip_entries, zip_errors = read_zip_bytes()
    extracted = extracted_hashes(zip_entries) if not zip_errors else {}
    add(
        checks,
        "zip_integrity_and_temporary_extraction",
        not zip_errors and len(extracted) == len(zip_entries),
        {"zip_errors": zip_errors, "zip_entries": len(zip_entries), "extracted_files": len(extracted)},
        "ZIP test passes and every file extracts",
    )

    root_mismatches: list[dict[str, Any]] = []
    for rel, data in sorted(zip_entries.items()):
        root_path = ROOT / rel
        if not root_path.exists():
            root_mismatches.append({"path": rel, "observed": "missing from root", "expected": "root copy exists"})
            continue
        zip_entry_hash = sha256_bytes(data)
        root_hash = sha256(root_path)
        extracted_hash = extracted.get(rel)
        if zip_entry_hash != root_hash or extracted_hash != root_hash:
            root_mismatches.append(
                {
                    "path": rel,
                    "zip_entry_sha256": zip_entry_hash,
                    "extracted_sha256": extracted_hash,
                    "root_sha256": root_hash,
                }
            )
    add(checks, "zip_entries_match_root_and_extracted_bytes", not root_mismatches, root_mismatches[:25], "all ZIP, extracted, and root bytes match")

    present = set(zip_entries)
    missing_critical = sorted(CRITICAL_ZIP_ENTRIES - present)
    add(checks, "critical_hash_ledger_entries_present_in_zip", not missing_critical, missing_critical, "all critical ledger/replay/source entries present")

    ledger_zip_targets: list[str] = []
    ledger_zip_mismatches: list[dict[str, Any]] = []
    ledger_root_only_targets: list[str] = []
    for rel, meta in sorted(ledger_files.items()):
        if rel in present:
            ledger_zip_targets.append(rel)
            extracted_hash = extracted.get(rel)
            if extracted_hash != meta.get("sha256"):
                ledger_zip_mismatches.append({"path": rel, "extracted_sha256": extracted_hash, "ledger_sha256": meta.get("sha256")})
        else:
            ledger_root_only_targets.append(rel)
    add(checks, "ledger_zip_targets_match_extracted_hashes", not ledger_zip_mismatches and bool(ledger_zip_targets), ledger_zip_mismatches[:25], "ledger targets inside ZIP match extracted hashes")

    expected_root_only = {
        "NDU_RL_OR.zip",
        "NDU_RL_OR.zip.sha256",
        "artifact/ndu_or_zip_closure_check_results.json",
        "artifact/ndu_or_external_boundary_scan_check_results.json",
        "artifact/ndu_or_zip_source_result_partition_check_results.json",
    }
    add(
        checks,
        "ledger_root_only_targets_are_not_zip_entries",
        expected_root_only.issubset(set(ledger_root_only_targets)) and not (expected_root_only & present),
        ledger_root_only_targets,
        sorted(expected_root_only),
    )

    failures = [check for check in checks if not check["ok"]]
    report = {
        "kind": "ndu_or_extracted_hash_ledger_replay_check",
        "status": "PASS" if not failures else "FAIL",
        "check_count": len(checks),
        "failure_count": len(failures),
        "zip_sha256": zip_hash,
        "zip_sidecar_sha256": sha256(ZIP_SIDECAR) if ZIP_SIDECAR.exists() else None,
        "package_hash_ledger_sha256": sha256(HASH_LEDGER_JSON) if HASH_LEDGER_JSON.exists() else None,
        "zip_entries": len(zip_entries),
        "ledger_zip_targets": ledger_zip_targets,
        "ledger_root_only_targets": ledger_root_only_targets,
        "checks": checks,
        "nonclaim": "Local extracted ZIP hash-ledger replay only; not full PyTorch/CEM regeneration, independent reproduction, external review, submission, acceptance, or Strong Accept evidence.",
    }
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    lines = [
        "# NDU OR extracted hash-ledger replay check",
        "",
        f"Status: **{report['status']}**",
        "",
        f"- Checks: `{report['check_count']}`",
        f"- Failures: `{report['failure_count']}`",
        f"- ZIP entries: `{report['zip_entries']}`",
        f"- ZIP SHA256: `{report['zip_sha256']}`",
        f"- ZIP sidecar SHA256: `{report['zip_sidecar_sha256']}`",
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

    print(json.dumps({k: report[k] for k in ["status", "check_count", "failure_count", "zip_entries", "zip_sha256"]}, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
