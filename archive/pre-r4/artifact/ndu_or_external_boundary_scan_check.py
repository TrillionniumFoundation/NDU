#!/usr/bin/env python3
"""Audit external-process boundary wording for the NDU OR package.

The checker looks for unnegated claims of upload, submission, external review,
acceptance, or Strong Accept outcomes in the current package and in the
distributable ZIP.  It also verifies that the key status files preserve the
local-only boundary wording.
"""

from __future__ import annotations

import hashlib
import json
import re
import zipfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ZIP_PATH = ROOT / "NDU_RL_OR.zip"
OUT_JSON = ROOT / "artifact" / "ndu_or_external_boundary_scan_check_results.json"
OUT_MD = ROOT / "artifact" / "ndu_or_external_boundary_scan_check_results.md"

TEXT_SUFFIXES = {".bib", ".bst", ".cls", ".csv", ".json", ".md", ".py", ".tex", ".txt"}
SCAN_ROOT_FILES = {
    "main.tex",
    "NDU_OR_submission_checklist.md",
    "reproducibility/README.md",
    "reproducibility/manifest.json",
    "reproducibility/data/lightweight_replay_dependency_closure_audit.csv",
    "reproducibility/data/package_self_replay_certificate.json",
    "reproducibility/data/reproducibility_environment_audit.json",
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
}
REQUIRED_ZIP_ENTRIES = {
    "main.tex",
    "NDU_OR_submission_checklist.md",
    "artifact/ndu_or_external_boundary_scan_check.py",
    "artifact/ndu_or_zip_closure_check.py",
    "artifact/ndu_or_package_hash_ledger_check.py",
    "artifact/ndu_or_extracted_hash_ledger_replay_check.py",
    "artifact/ndu_or_result_freshness_check.py",
    "artifact/ndu_or_reviewer_handoff_index.json",
    "artifact/ndu_or_reviewer_handoff_index_check.py",
    "artifact/ndu_or_zip_source_result_partition_check.py",
    "artifact/ndu_or_root_zip_forensic_parity_check.py",
    "artifact/ndu_or_release_manifest_parity_ledger.json",
    "artifact/ndu_or_release_manifest_parity_check.py",
    "reproducibility/data/reproducibility_environment_audit.json",
}
REQUIRED_BOUNDARY_PHRASES = {
    "main.tex": [
        "does not assert that external reviewers have accepted",
        "not external referee acceptance",
        "review, submission, or acceptance evidence",
    ],
    "NDU_OR_submission_checklist.md": [
        "R86",
        "R87",
        "R88",
        "R89",
        "reviewer handoff index",
        "ZIP source/result partition",
        "root/ZIP forensic parity",
        "release-manifest parity",
        "R84",
        "external-boundary scan",
        "local package/evidence",
        "no external review",
        "submission",
        "acceptance",
        "Strong Accept",
    ],
    "reproducibility/data/reproducibility_environment_audit.json": [
        "Local environment provenance only",
        "no external review",
        "Strong Accept outcome",
    ],
    "reproducibility/data/package_self_replay_certificate.json": [
        "Does not rerun full PyTorch training",
        "does not evidence external review",
        "Strong Accept",
    ],
}

NEGATION_HINTS = [
    "no ",
    "not ",
    "not a ",
    "not an ",
    "does not ",
    "do not ",
    "did not ",
    "without ",
    "cannot ",
    "is not ",
    "are not ",
    "was not ",
    "were not ",
    "doesn't ",
    "local-only; no ",
]
FORBIDDEN_PATTERNS = [
    re.compile(r"\b(?:has|have|was|were|is|been)\s+(?:externally\s+)?(?:accepted|reviewed|submitted|uploaded)\b", re.IGNORECASE),
    re.compile(r"\bexternal\s+review(?:er|ers)?\s+(?:accepted|approved|endorsed)\b", re.IGNORECASE),
    re.compile(r"\bportal\s+(?:submission|upload)\s+(?:complete|completed|done|accepted)\b", re.IGNORECASE),
    re.compile(r"\bsubmission\s+(?:complete|completed|accepted|confirmed)\b", re.IGNORECASE),
    re.compile(r"\baccepted\s+(?:by|at)\s+(?:Operations\s+Research|OR|INFORMS)\b", re.IGNORECASE),
    re.compile(r"\bdecision\s*:\s*(?:accept|strong\s+accept)\b", re.IGNORECASE),
    re.compile(r"\bStrong\s+Accept\s+(?:evidence|outcome|decision|recommendation)\b", re.IGNORECASE),
]


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def add(checks: list[dict[str, Any]], name: str, ok: bool, observed: Any, expected: Any) -> None:
    checks.append({"name": name, "ok": bool(ok), "observed": observed, "expected": expected})


def is_text_name(name: str) -> bool:
    path = Path(name)
    suffix = ".synctex.gz" if name.endswith(".synctex.gz") else path.suffix
    return suffix in TEXT_SUFFIXES


def decode_text(data: bytes) -> str | None:
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError:
        return None


def negated(text: str, start: int) -> bool:
    prefix = text[max(0, start - 240) : start].lower()
    return any(hint in prefix for hint in NEGATION_HINTS)


def forbidden_hits(label: str, text: str) -> list[dict[str, Any]]:
    hits: list[dict[str, Any]] = []
    for pattern in FORBIDDEN_PATTERNS:
        for match in pattern.finditer(text):
            if negated(text, match.start()):
                continue
            line_no = text.count("\n", 0, match.start()) + 1
            line_start = text.rfind("\n", 0, match.start()) + 1
            line_end = text.find("\n", match.end())
            if line_end == -1:
                line_end = len(text)
            hits.append(
                {
                    "path": label,
                    "line": line_no,
                    "pattern": pattern.pattern,
                    "snippet": text[line_start:line_end].strip()[:240],
                }
            )
    return hits


def root_texts() -> tuple[dict[str, str], list[str]]:
    texts: dict[str, str] = {}
    missing: list[str] = []
    for rel in sorted(SCAN_ROOT_FILES):
        path = ROOT / rel
        if not path.exists():
            missing.append(rel)
            continue
        decoded = decode_text(path.read_bytes())
        if decoded is None:
            missing.append(f"{rel}: not UTF-8 text")
            continue
        texts[rel] = decoded
    return texts, missing


def zip_texts() -> tuple[dict[str, str], list[str], list[str], str | None]:
    texts: dict[str, str] = {}
    errors: list[str] = []
    names: list[str] = []
    zip_hash: str | None = None
    if not ZIP_PATH.exists():
        return texts, ["missing NDU_RL_OR.zip"], names, zip_hash
    zip_hash = sha256(ZIP_PATH)
    with zipfile.ZipFile(ZIP_PATH) as zf:
        bad = zf.testzip()
        if bad is not None:
            errors.append(f"zip integrity failure at {bad}")
        for info in zf.infolist():
            if info.is_dir():
                continue
            name = info.filename.rstrip("/")
            names.append(name)
            if not is_text_name(name):
                continue
            decoded = decode_text(zf.read(info))
            if decoded is not None:
                texts[name] = decoded
    return texts, errors, names, zip_hash


def required_phrase_failures(texts: dict[str, str]) -> list[dict[str, Any]]:
    failures: list[dict[str, Any]] = []
    for rel, phrases in REQUIRED_BOUNDARY_PHRASES.items():
        text = texts.get(rel, "")
        for phrase in phrases:
            if phrase not in text:
                failures.append({"path": rel, "missing_phrase": phrase})
    return failures


def main() -> int:
    root_docs, root_missing = root_texts()
    zip_docs, zip_errors, zip_names, zip_hash = zip_texts()

    root_hits: list[dict[str, Any]] = []
    for rel, text in sorted(root_docs.items()):
        root_hits.extend(forbidden_hits(rel, text))

    zip_hits: list[dict[str, Any]] = []
    for rel, text in sorted(zip_docs.items()):
        zip_hits.extend(forbidden_hits(f"zip:{rel}", text))

    required_failures = required_phrase_failures(root_docs)
    missing_zip_required = sorted(REQUIRED_ZIP_ENTRIES - set(zip_names))
    result_entries = sorted(name for name in zip_names if name.startswith("artifact/ndu_or_external_boundary_scan_check_results."))

    checks: list[dict[str, Any]] = []
    add(checks, "root_boundary_scan_files_present", not root_missing, root_missing, "all scan roots present and UTF-8")
    add(checks, "required_boundary_phrases_present", not required_failures, required_failures, "all required local-only boundary phrases")
    add(checks, "root_scan_has_no_unnegated_external_overclaim", not root_hits, root_hits[:25], "no unnegated upload/review/acceptance/Strong Accept claims")
    add(checks, "zip_integrity", not zip_errors, zip_errors, [])
    add(checks, "zip_required_boundary_entries_present", not missing_zip_required, missing_zip_required, "all required boundary entries in ZIP")
    add(checks, "zip_scan_has_no_unnegated_external_overclaim", not zip_hits, zip_hits[:25], "no unnegated upload/review/acceptance/Strong Accept claims in ZIP text entries")
    add(checks, "zip_excludes_boundary_scan_result_files", not result_entries, result_entries, "root-only generated result files are excluded from ZIP")

    failures = [check for check in checks if not check["ok"]]
    report = {
        "kind": "ndu_or_external_boundary_scan_check",
        "status": "PASS" if not failures else "FAIL",
        "check_count": len(checks),
        "failure_count": len(failures),
        "root_text_files_scanned": len(root_docs),
        "zip_text_files_scanned": len(zip_docs),
        "zip_entries": len(zip_names),
        "zip_sha256": zip_hash,
        "checker_sha256": sha256(ROOT / "artifact" / "ndu_or_external_boundary_scan_check.py"),
        "checks": checks,
        "nonclaim": "Local external-boundary wording scan only; not full PyTorch/CEM regeneration, independent reproduction, external review, submission, upload, acceptance, or Strong Accept evidence.",
    }
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    lines = [
        "# NDU OR external-boundary scan check",
        "",
        f"Status: **{report['status']}**",
        "",
        f"- Checks: `{report['check_count']}`",
        f"- Failures: `{report['failure_count']}`",
        f"- Root text files scanned: `{report['root_text_files_scanned']}`",
        f"- ZIP text files scanned: `{report['zip_text_files_scanned']}`",
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
