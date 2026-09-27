#!/usr/bin/env python3
"""Lightweight OR-positioning checker for the NDU Operations Research submission.

The checker is intentionally modest: it does not judge paper quality.  It guards
against the local referee-loop failure mode where the blind INFORMS/OR source
loses its operations framing, scope map, or reproducibility boundary while
retaining the current locked NDU title.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEX = ROOT / "main.tex"
OUT_JSON = ROOT / "artifact" / "ndu_or_positioning_results.json"
OUT_MD = ROOT / "artifact" / "ndu_or_positioning_results.md"


def strip_latex(text: str) -> str:
    text = re.sub(r"\\textbf\{([^{}]*)\}", r"\1", text)
    text = re.sub(r"\\[a-zA-Z]+\*?(?:\[[^\]]*\])?(?:\{([^{}]*)\})?", r"\1", text)
    text = re.sub(r"[{}$\\]", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def extract_macro(tex: str, macro: str) -> str:
    m = re.search(r"\\" + macro + r"\{(.*?)\}", tex, re.S)
    return m.group(1).strip() if m else ""


def main() -> None:
    tex = TEX.read_text(encoding="utf-8", errors="ignore")
    title = strip_latex(extract_macro(tex, "TITLE"))
    abstract_raw = re.search(r"\\ABSTRACT\{(.*?)\}\s*\\KEYWORDS", tex, re.S)
    abstract = strip_latex(abstract_raw.group(1)) if abstract_raw else ""
    keywords = strip_latex(extract_macro(tex, "KEYWORDS"))
    subject = strip_latex(extract_macro(tex, "SUBJECTCLASS"))
    intro = strip_latex(tex[tex.find(r"\section{Introduction}"):tex.find(r"\subsection{Related Literature}")])
    words = re.findall(r"[A-Za-z0-9]+(?:[-'][A-Za-z0-9]+)?", abstract)

    checks = []

    def check(name: str, ok: bool, detail: str) -> None:
        checks.append({"name": name, "ok": bool(ok), "detail": detail})

    title_low = title.lower()
    abs_low = abstract.lower()
    intro_low = intro.lower()
    key_low = keywords.lower()
    subj_low = subject.lower()

    check("title_locked_current", title == "NDU: A Generalization of Fixed-Preference Reinforcement Learning",
          f"title={title}")
    check("title_generalization_terms", "ndu" in title_low and "fixed-preference" in title_low and "reinforcement learning" in title_low,
          f"title={title}")
    check("abstract_word_limit", len(words) <= 250, f"abstract_words={len(words)}")
    check("abstract_opens_or", abstract.lower().startswith("many operations models"),
          abstract[:120])
    check("abstract_fixed_preference_as_limit", "fixed-preference" in abs_low and any(term in abs_low for term in ["frozen-valuation limit", "singular limit", "comparison case"]),
          "RL is framed as a limiting/comparison case")
    check("keywords_oriented", "stochastic control" in key_low and "endogenous valuation" in key_low and "reinforcement learning" not in key_low,
          f"keywords={keywords}")
    check("subjectclass_oriented", "dynamic programming" in subj_low and "simulation" in subj_low and "artificial intelligence" not in subj_low,
          f"subjectclass={subject}")
    check("or_interpretation_table", "tab:or_interpretation_map" in tex and "procurement" in intro_low and "queueing" in intro_low and "revenue management" in intro_low,
          "OR interpretation table and examples present before related literature")
    check("scope_guard_after_table", "only an interpretation map" in intro_low and "benchmark suite" in intro_low,
          "table is scoped as interpretation, not extra theorem/evidence")
    check("theorem_scope_table", "tab:theorem_scope_map" in tex and "Scope map for the main formal claims" in tex,
          "front-of-paper theorem scope map present")
    check("theorem_scope_labels", all(label in tex for label in ["thm:local_existence", "prop:weak_coupling", "prop:pmp_convergence", "prop:rl_limit", "cor:neural_empirical_envelope_guard", "sec:experiments"]),
          "main formal/computational result labels are represented")
    check("theorem_scope_boundaries", all(term in intro_low for term in ["operator-level", "frozen-face", "conditional", "compact-domain", "finite-cover", "validation-cover", "inventory-centered"]),
          "scope map names the major claim-boundary classes")

    failures = [c for c in checks if not c["ok"]]
    result = {
        "status": "PASS" if not failures else "FAIL",
        "checks": len(checks),
        "failures": len(failures),
        "abstract_words": len(words),
        "title": title,
        "keywords": keywords,
        "subjectclass": subject,
        "check_results": checks,
        "main_finding": "OR-positioning and theorem-scope guardrails pass: the manuscript is stochastic-control / operations framed, and its major formal claims are front-mapped with claim boundaries." if not failures else "OR-positioning/theorem-scope guardrails still fail.",
    }
    OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")
    lines = ["# NDU OR positioning check", "", f"Status: **{result['status']}**", "", f"Checks: {result['checks']}", f"Failures: {result['failures']}", f"Abstract words: {result['abstract_words']}", "", f"Title: {result['title']}", "", "## Check results", ""]
    for c in checks:
        lines.append(f"- {'PASS' if c['ok'] else 'FAIL'} `{c['name']}`: {c['detail']}")
    lines.append("")
    lines.append(result["main_finding"])
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps(result, indent=2))
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
