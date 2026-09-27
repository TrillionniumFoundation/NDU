#!/usr/bin/env python3
"""Cross-artifact consistency audit for large sampled neural guard rows.

This deterministic audit ties together the validation-cover HJB tuple, replay
certificate, empirical envelope, interval-domain certificate,
interval-sensitivity audit, bounded-architecture budget, and budget stress
audit.  It does not turn sampled neural evidence into an analytic full-domain
Lipschitz certificate; it checks that the finite guard artifacts agree on the
same experiment identifiers and boundary interpretation.
"""

from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUT = DATA / "neural_guard_cross_artifact_consistency_audit.csv"


def read_csv(name: str) -> list[dict[str, str]]:
    with (DATA / name).open(newline="") as fh:
        return list(csv.DictReader(fh))


def by_experiment(name: str) -> dict[str, dict[str, str]]:
    return {row["experiment"]: row for row in read_csv(name)}


def main() -> int:
    validation = by_experiment("neural_validation_cover_hjb_gap_audit.csv")
    replay = by_experiment("neural_validation_cover_replay_certificate.csv")
    envelope = by_experiment("neural_empirical_envelope_audit.csv")
    interval = by_experiment("neural_interval_domain_certificate.csv")
    sensitivity_rows = read_csv("neural_interval_sensitivity_audit.csv")
    budget_rows = read_csv("bounded_architecture_lipschitz_budget_audit.csv")
    stress_rows = read_csv("bounded_architecture_budget_stress_audit.csv")

    experiments = sorted(set(validation) & set(replay) & set(envelope) & set(interval))
    sensitivity_by_exp: dict[str, list[dict[str, str]]] = {}
    for row in sensitivity_rows:
        sensitivity_by_exp.setdefault(row["experiment"], []).append(row)

    budget_components = sorted({row["component"] for row in budget_rows})
    stress_scenarios = sorted({row["scenario"] for row in stress_rows})
    min_budget_stress_margin = min(float(row["margin"]) for row in stress_rows)
    max_stressed_budget_product = max(float(row["stressed_budget_product"]) for row in stress_rows)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "experiment",
        "required_artifacts_present",
        "validation_cover_status",
        "replay_certificate_status",
        "empirical_envelope_status",
        "interval_certificate_status",
        "interval_sensitivity_rows",
        "max_interval_sensitivity_score",
        "budget_component_count",
        "budget_stress_scenario_count",
        "min_budget_stress_margin",
        "max_stressed_budget_product",
        "native_hjb_ratio_vs_headline",
        "greedy_tail_ratio_sup_over_p95",
        "heldout_delta_vs_headline",
        "validation_cover_route",
        "consistency_status",
        "interpretation",
    ]
    with OUT.open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        for experiment in experiments:
            sens = sensitivity_by_exp.get(experiment, [])
            max_sensitivity_score = max(float(row["sensitivity_score"]) for row in sens)
            required_present = int(bool(validation.get(experiment)) and bool(replay.get(experiment)) and bool(envelope.get(experiment)) and bool(interval.get(experiment)) and bool(sens) and bool(budget_rows) and bool(stress_rows))
            all_guards = [
                validation[experiment]["guard_status"] == "validation_cover_gap_tuple_closed",
                replay[experiment]["certificate_status"] == "deterministic_replay_certificate_pass",
                envelope[experiment]["envelope_status"] == "empirical_envelope_guard_pass",
                interval[experiment]["interval_certificate_status"] == "interval_domain_certificate_pass",
                all(row["sensitivity_status"] == "interval_sensitivity_guard_pass" for row in sens),
                min_budget_stress_margin >= 0.75,
                max_stressed_budget_product <= 11.25,
            ]
            status = "cross_artifact_guard_pass" if required_present and all(all_guards) else "cross_artifact_guard_fail"
            writer.writerow(
                {
                    "experiment": experiment,
                    "required_artifacts_present": required_present,
                    "validation_cover_status": validation[experiment]["guard_status"],
                    "replay_certificate_status": replay[experiment]["certificate_status"],
                    "empirical_envelope_status": envelope[experiment]["envelope_status"],
                    "interval_certificate_status": interval[experiment]["interval_certificate_status"],
                    "interval_sensitivity_rows": len(sens),
                    "max_interval_sensitivity_score": f"{max_sensitivity_score:.12g}",
                    "budget_component_count": len(budget_components),
                    "budget_stress_scenario_count": len(stress_scenarios),
                    "min_budget_stress_margin": f"{min_budget_stress_margin:.6f}",
                    "max_stressed_budget_product": f"{max_stressed_budget_product:.6f}",
                    "native_hjb_ratio_vs_headline": validation[experiment]["native_hjb_ratio_vs_headline"],
                    "greedy_tail_ratio_sup_over_p95": envelope[experiment]["greedy_tail_ratio_sup_over_p95"],
                    "heldout_delta_vs_headline": validation[experiment]["heldout_delta_vs_headline"],
                    "validation_cover_route": "validation-cover_not_global_lipschitz",
                    "consistency_status": status,
                    "interpretation": "All finite neural guard artifacts agree on the experiment id, pass status, budget margin, and sampled validation-cover route; this is not an analytic full-domain neural certificate.",
                }
            )
    print(f"wrote {OUT.relative_to(ROOT)} rows={len(experiments)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
