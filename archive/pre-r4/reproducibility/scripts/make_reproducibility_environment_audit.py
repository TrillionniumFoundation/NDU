#!/usr/bin/env python3
"""Record the local environment used for package replay gates.

This audit is intentionally local and non-networked.  It records the Python
version, declared requirements availability, and system tools needed for the
lightweight checker/build/package gates.  Missing optional full-regeneration
packages are reported as a boundary rather than hidden.
"""

from __future__ import annotations

import importlib
import importlib.metadata
import json
import platform
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "reproducibility_environment_audit.json"
REQUIREMENTS = ROOT / "requirements.txt"

STDLIB_MODULES = [
    "csv",
    "hashlib",
    "importlib.metadata",
    "json",
    "math",
    "pathlib",
    "shutil",
    "subprocess",
    "zipfile",
]

REQUIRED_TOOLS = {
    "latexmk": ["latexmk", "--version"],
    "pdflatex": ["pdflatex", "--version"],
    "zip": ["zip", "-v"],
    "unzip": ["unzip", "-v"],
    "sha256sum": ["sha256sum", "--version"],
}


def normalize_version(version: str) -> tuple[int, ...]:
    parts = re.findall(r"\d+", version.split("+", 1)[0])
    return tuple(int(part) for part in parts[:4]) if parts else (0,)


def satisfies(version: str | None, spec: str) -> bool | None:
    if version is None:
        return False
    if not spec:
        return True
    match = re.fullmatch(r">=\s*([0-9][0-9A-Za-z.+-]*)", spec.strip())
    if not match:
        return None
    return normalize_version(version) >= normalize_version(match.group(1))


def parse_requirement(line: str) -> tuple[str, str]:
    clean = line.split("#", 1)[0].strip()
    if not clean:
        return "", ""
    match = re.match(r"^([A-Za-z0-9_.-]+)\s*(.*)$", clean)
    if not match:
        return clean, ""
    return match.group(1), match.group(2).strip()


def requirement_rows() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for raw in REQUIREMENTS.read_text().splitlines():
        package, spec = parse_requirement(raw)
        if not package:
            continue
        try:
            version = importlib.metadata.version(package)
            available = True
        except importlib.metadata.PackageNotFoundError:
            version = None
            available = False
        rows.append(
            {
                "package": package,
                "declared_spec": spec,
                "installed_version": version,
                "available": available,
                "satisfies_declared_spec": satisfies(version, spec),
                "scope": "optional_full_regeneration_dependency",
            }
        )
    return rows


def stdlib_rows() -> list[dict[str, Any]]:
    rows = []
    for module in STDLIB_MODULES:
        try:
            importlib.import_module(module)
            rows.append({"module": module, "available": True})
        except Exception as exc:  # pragma: no cover - diagnostic path
            rows.append({"module": module, "available": False, "error": repr(exc)})
    return rows


def tool_row(name: str, argv: list[str]) -> dict[str, Any]:
    path = shutil.which(argv[0])
    row: dict[str, Any] = {"tool": name, "available": path is not None}
    if path is None:
        return row
    row["path_basename"] = Path(path).name
    try:
        proc = subprocess.run(argv, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False, timeout=10)
        first_line = next((line.strip() for line in proc.stdout.splitlines() if line.strip()), "")
        row.update({"returncode": proc.returncode, "version_head": first_line[:160]})
    except Exception as exc:  # pragma: no cover - diagnostic path
        row.update({"returncode": None, "version_head": "", "error": repr(exc)})
    return row


def main() -> int:
    stdlib = stdlib_rows()
    tools = [tool_row(name, argv) for name, argv in REQUIRED_TOOLS.items()]
    requirements = requirement_rows()
    missing_optional = [row["package"] for row in requirements if not row["available"]]

    light_ready = (
        sys.version_info >= (3, 10)
        and all(row["available"] for row in stdlib)
        and all(row["available"] for row in tools)
    )

    report = {
        "audit": "reproducibility_environment_audit",
        "status": "PASS" if light_ready else "FAIL",
        "python": {
            "implementation": platform.python_implementation(),
            "version": platform.python_version(),
            "major_minor": f"{sys.version_info.major}.{sys.version_info.minor}",
        },
        "platform": {
            "system": platform.system(),
            "machine": platform.machine(),
            "processor": platform.processor(),
        },
        "stdlib_modules": stdlib,
        "toolchain": tools,
        "requirements": requirements,
        "lightweight_gate": {
            "status": "PASS" if light_ready else "FAIL",
            "minimum_python": "3.10",
            "required_stdlib_modules": STDLIB_MODULES,
            "required_tools": sorted(REQUIRED_TOOLS),
            "scope": "checker, LaTeX build, zip integrity, checksum, and extracted-package replay prerequisites",
        },
        "full_regeneration_dependency_boundary": {
            "declared_requirement_count": len(requirements),
            "missing_optional_in_current_interpreter": missing_optional,
            "status": "COMPLETE" if not missing_optional else "NOT_PROVEN_IN_CURRENT_INTERPRETER",
            "boundary": "The lightweight package gates pass here; this audit does not prove full optional PyTorch/pandas/matplotlib/seaborn regeneration in this interpreter.",
        },
        "external_boundary": "Local environment provenance only; no external review, submission, portal action, acceptance, or Strong Accept outcome is evidenced.",
    }

    OUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(
        "wrote "
        f"{OUT.relative_to(ROOT)} status={report['status']} "
        f"requirements={len(requirements)} missing_optional={len(missing_optional)}"
    )
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
