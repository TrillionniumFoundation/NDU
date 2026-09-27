#!/usr/bin/env python3
"""Targeted inventory normalized-residual HBO/NBO audit.

The targeted residual-closing run reduced inventory native HJB and terminal losses but
increased the normalized residual because the sampled Hamiltonian scale became
small. This audit explicitly searches inventory-only configurations that reduce
normalized residual RMSE while preserving held-out welfare and reporting native
HJB/terminal tradeoffs.
"""
from __future__ import annotations

import argparse
import csv
import math
import statistics as stats
import sys
from pathlib import Path
from typing import Any

import numpy as np
import torch

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

import run_hbo_full_experiments as hbo  # noqa: E402
import run_nbo_full_ndu_solver as base  # noqa: E402

SEED_COUNT = 30
EVAL_BASE_SEED = 20260512


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as fh:
        return list(csv.DictReader(fh))


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    keys: list[str] = []
    for row in rows:
        for key in row:
            if key not in keys:
                keys.append(key)
    with path.open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=keys)
        writer.writeheader()
        writer.writerows(rows)


def eval_many(policy: hbo.HBOPolicy, metric: str = "mean_welfare") -> tuple[float, float]:
    vals = []
    for j in range(SEED_COUNT):
        seed = EVAL_BASE_SEED + 30000 + j + 1
        vals.append(float(hbo.eval_policy(policy, seed)[metric]))
    ci = 1.96 * stats.stdev(vals) / math.sqrt(len(vals)) if len(vals) > 1 else 0.0
    return float(np.mean(vals)), float(ci)


def baseline_rows() -> list[dict[str, Any]]:
    residual = {r["experiment"]: r for r in read_csv(DATA / "hbo_residual_diagnostics.csv")}
    metrics = {(r["experiment"], r["method"]): r for r in read_csv(DATA / "source_nbo_metrics.csv")}
    r = residual["inventory_service_level"]
    m = metrics[("inventory_service_level", "nbo_full_ndu_inventory")]
    rows: list[dict[str, Any]] = [{
        "experiment": "inventory_service_level",
        "method": "nbo_full_ndu_inventory",
        "audit_config": "headline_performance_run",
        "seed": "packaged_headline",
        "train_steps": r["iteration"],
        "width": 56,
        "depth": 2,
        "batch": 96,
        "omega": 1.0,
        "terminal_weight": 2.0,
        "actor_hjb_weight": 0.05,
        "actor_lr": 5e-6,
        "critic_lr": 0.0012,
        "native_hjb_loss": r["native_hjb_loss"],
        "residual_rmse": r["residual_rmse"],
        "mean_abs_residual": r["mean_abs_residual"],
        "mean_hamiltonian_abs": r["mean_hamiltonian_abs"],
        "normalized_residual_rmse": r["normalized_residual_rmse_over_one_plus_abs_mean_hamiltonian"],
        "terminal_boundary_loss": r["terminal_boundary_loss"],
        "primary_metric": "mean_welfare",
        "heldout_value": m["mean_welfare"],
        "heldout_ci95": 1.96 * float(m["mean_welfare_se"]),
        "certificate_gap_read": "headline_inventory_gap",
        "claim_status": "baseline_inventory_normalized_gap_visible",
    }]
    closing_path = DATA / "hbo_residual_closing_audit.csv"
    if closing_path.exists():
        closing = {(x["experiment"], x["audit_config"]): x for x in read_csv(closing_path)}
        best = closing.get(("inventory_service_level", "inventory_residual_certificate_balanced_2400"))
        if best:
            row = dict(best)
            row["certificate_gap_read"] = "best_native_residual_closure_reference"
            row.setdefault("claim_status", "native_residual_closed_reference")
            rows.append(row)
    return rows


def configs() -> list[dict[str, Any]]:
    spec = base.inv_spec("nbo_full_ndu_inventory")
    common = {"spec": spec, "primary_metric": "mean_welfare", "depth": 2, "grad_clip": 10.0, "init_mode": "safe"}
    raw = [
        ("inventory_norm_early_scale_60", 20303601, 64, 60, 128, 2.0, 8.0, 0.01, 4e-6, 0.0012),
        ("inventory_norm_early_scale_120", 20303602, 64, 120, 128, 2.0, 8.0, 0.01, 4e-6, 0.0012),
        ("inventory_norm_early_scale_240", 20303603, 64, 240, 128, 2.0, 8.0, 0.01, 4e-6, 0.0012),
        ("inventory_norm_early_guard_120", 20303604, 64, 120, 128, 4.0, 12.0, 0.03, 2e-6, 0.0012),
        ("inventory_norm_early_guard_240", 20303605, 64, 240, 128, 4.0, 12.0, 0.03, 2e-6, 0.0012),
        ("inventory_norm_early_guard_360", 20303606, 64, 360, 160, 4.0, 12.0, 0.03, 2e-6, 0.0012),
        ("inventory_norm_early_terminal_450", 20303607, 72, 450, 160, 4.0, 20.0, 0.02, 2e-6, 0.0010),
        ("inventory_norm_early_terminal_600", 20303608, 72, 600, 160, 4.0, 20.0, 0.02, 2e-6, 0.0010),
        ("inventory_norm_pareto_actor_900", 20303801, 64, 900, 160, 6.0, 14.0, 0.0, 5e-6, 0.0010),
        ("inventory_norm_pareto_actor_1200", 20303802, 64, 1200, 160, 6.0, 16.0, 0.0, 5e-6, 0.0010),
        ("inventory_norm_pareto_actor_1800", 20303803, 72, 1800, 192, 6.0, 16.0, 0.0, 5e-6, 0.0009),
        ("inventory_norm_pareto_resid_actor_1200", 20303804, 72, 1200, 192, 8.0, 16.0, 0.01, 5e-6, 0.0009),
        ("inventory_norm_pareto_scale_1200", 20303805, 72, 1200, 192, 4.0, 16.0, 0.0, 8e-6, 0.0010),
        ("inventory_norm_pareto_scale_1500", 20303806, 72, 1500, 192, 5.0, 18.0, 0.0, 8e-6, 0.0009),
        ("inventory_norm_guard_moderate_900", 20303501, 64, 900, 128, 4.0, 12.0, 0.03, 2e-6, 0.0012),
        ("inventory_norm_guard_balanced_1200", 20303502, 64, 1200, 160, 6.0, 16.0, 0.03, 2e-6, 0.0010),
        ("inventory_norm_hamiltonian_preserve_900", 20303503, 64, 900, 128, 2.0, 8.0, 0.01, 4e-6, 0.0012),
        ("inventory_norm_hamiltonian_preserve_1500", 20303504, 72, 1500, 160, 3.0, 10.0, 0.02, 3e-6, 0.0010),
        ("inventory_norm_terminal_guard_1800", 20303505, 80, 1800, 192, 4.0, 24.0, 0.02, 1e-6, 0.0008),
        ("inventory_norm_residual_scale_mix_2400", 20303506, 80, 2400, 192, 6.0, 24.0, 0.05, 1e-6, 0.0008),
        ("inventory_norm_critic_scale_1200", 20303507, 64, 1200, 160, 4.0, 12.0, 0.0, 0.0, 0.0010),
        ("inventory_norm_critic_scale_1800", 20303508, 72, 1800, 192, 6.0, 18.0, 0.0, 0.0, 0.0009),
    ]
    out = []
    for label, seed, width, train_steps, batch, omega, terminal_weight, actor_hjb_weight, actor_lr, critic_lr in raw:
        cfg = dict(common)
        cfg.update({
            "label": label,
            "seed": seed,
            "width": width,
            "train_steps": train_steps,
            "batch": batch,
            "omega": omega,
            "terminal_weight": terminal_weight,
            "actor_hjb_weight": actor_hjb_weight,
            "actor_lr": actor_lr,
            "critic_lr": critic_lr,
            "loss_mode": "standard",
        })
        out.append(cfg)
    for label, seed, width, train_steps, batch, omega, terminal_weight, actor_hjb_weight, actor_lr, critic_lr in [
        ("inventory_normloss_scaled_600", 20303701, 64, 600, 160, 20.0, 12.0, 0.05, 3e-6, 0.0010),
        ("inventory_normloss_scaled_1200", 20303702, 72, 1200, 192, 30.0, 18.0, 0.06, 2e-6, 0.0009),
        ("inventory_normloss_scaled_1800", 20303703, 80, 1800, 192, 40.0, 24.0, 0.08, 1e-6, 0.0008),
        ("inventory_normloss_scaled_actor_1200", 20303704, 72, 1200, 192, 20.0, 16.0, 0.02, 5e-6, 0.0009),
    ]:
        cfg = dict(common)
        cfg.update({
            "label": label,
            "seed": seed,
            "width": width,
            "train_steps": train_steps,
            "batch": batch,
            "omega": omega,
            "terminal_weight": terminal_weight,
            "actor_hjb_weight": actor_hjb_weight,
            "actor_lr": actor_lr,
            "critic_lr": critic_lr,
            "loss_mode": "normalized_scaled",
        })
        out.append(cfg)
    return out



def train_hbo_normalized_loss(
    spec: base.NBOSpec,
    *,
    seed: int,
    width: int,
    depth: int,
    train_steps: int,
    batch: int,
    omega: float,
    actor_lr: float,
    critic_lr: float,
    terminal_weight: float,
    actor_hjb_weight: float,
    grad_clip: float,
    init_mode: str,
) -> hbo.HBOPolicy:
    """Inventory-focused variant that trains on scaled residual loss."""
    rng = np.random.default_rng(seed)
    policy = hbo.init_policy(spec, seed, width, depth, init_mode)
    opt_a = torch.optim.Adam(policy.actor.parameters(), lr=actor_lr)
    opt_v = torch.optim.Adam(policy.critic.parameters(), lr=critic_lr)
    for it in range(1, train_steps + 1):
        step = int(rng.integers(0, spec.horizon))
        X = hbo.sample_states(spec, rng, batch)
        tt = torch.full((batch,), step / max(1, spec.horizon - 1), dtype=hbo.DTYPE, device=hbo.DEVICE)
        U_actor = policy.input_matrix_t(tt, X).detach()
        with torch.no_grad():
            A_detached = policy.action_t(U_actor).detach()
        opt_v.zero_grad(set_to_none=True)
        Hc, Rc, _ = hbo.hamiltonian_residual(policy, spec, step, X, A_detached)
        scale_c = torch.clamp(1.0 + torch.abs(Hc.detach()), min=1.0)
        XT = hbo.sample_states(spec, rng, max(16, batch // 2))
        UT = policy.input_matrix_t(torch.ones(XT.shape[0], dtype=hbo.DTYPE, device=hbo.DEVICE), XT)
        VT = policy.value_t(UT)
        targetT = hbo.terminal_value_t(spec, XT)
        terminal_loss = torch.mean((VT - targetT) ** 2)
        critic_loss = omega * torch.mean((Rc / scale_c) ** 2) + terminal_weight * terminal_loss
        critic_loss.backward()
        if grad_clip > 0:
            torch.nn.utils.clip_grad_norm_(policy.critic.parameters(), grad_clip)
        opt_v.step()
        for par in policy.critic.parameters():
            par.requires_grad_(False)
        opt_a.zero_grad(set_to_none=True)
        A = policy.action_t(U_actor)
        Ha, Ra, _ = hbo.hamiltonian_residual(policy, spec, step, X, A)
        scale_a = torch.clamp(1.0 + torch.abs(Ha.detach()), min=1.0)
        actor_loss = -torch.mean(Ha) + actor_hjb_weight * omega * torch.mean((Ra / scale_a) ** 2)
        actor_loss.backward()
        if grad_clip > 0:
            torch.nn.utils.clip_grad_norm_(policy.actor.parameters(), grad_clip)
        opt_a.step()
        for par in policy.critic.parameters():
            par.requires_grad_(True)
        if it == 1 or it % max(1, train_steps // 10) == 0 or it == train_steps:
            with torch.no_grad():
                A_mean = A.detach().mean(dim=0).cpu().numpy()
            policy.diagnostics.append({
                "experiment": spec.experiment,
                "method": spec.method,
                "iteration": it,
                "loss_perf": float((-Ha.detach().mean()).cpu()),
                "hjb_loss": float(torch.mean(Rc.detach() ** 2).cpu()),
                "terminal_loss": float(terminal_loss.detach().cpu()),
                "residual_mean_abs": float(torch.mean(torch.abs(Rc.detach())).cpu()),
                "mean_hamiltonian": float(torch.mean(Ha.detach()).cpu()),
                "mean_action": ";".join(f"{x:.6g}" for x in A_mean),
                "omega": omega,
                "algorithm": "hbo_inventory_normalized_residual_scaled_loss",
                "backend": f"torch-{torch.__version__}",
                "initialization": f"{init_mode}_constant_bias_random_mlp_no_bellman_pretraining",
                "ad_terms": "V_t_gradV_exact_state_Hessian_and_actor_Hamiltonian_gradients",
            })
    return policy

def run_config(cfg: dict[str, Any]) -> dict[str, Any]:
    train_kwargs = {k: cfg[k] for k in [
        "width", "depth", "train_steps", "batch", "omega", "actor_lr", "critic_lr", "terminal_weight", "actor_hjb_weight", "grad_clip", "init_mode"
    ]}
    if cfg.get("loss_mode") == "normalized_scaled":
        policy = train_hbo_normalized_loss(cfg["spec"], seed=cfg["seed"], **train_kwargs)
    else:
        policy = hbo.train_hbo(cfg["spec"], seed=cfg["seed"], **train_kwargs)
    diag = policy.diagnostics[-1]
    heldout, ci = eval_many(policy, cfg["primary_metric"])
    residual_rmse = math.sqrt(float(diag["hjb_loss"]))
    mean_h_abs = abs(float(diag["mean_hamiltonian"]))
    normalized = residual_rmse / (1.0 + mean_h_abs)
    return {
        "experiment": "inventory_service_level",
        "method": "nbo_full_ndu_inventory",
        "audit_config": cfg["label"],
        "seed": cfg["seed"],
        "train_steps": cfg["train_steps"],
        "width": cfg["width"],
        "depth": cfg["depth"],
        "batch": cfg["batch"],
        "omega": cfg["omega"],
        "terminal_weight": cfg["terminal_weight"],
        "actor_hjb_weight": cfg["actor_hjb_weight"],
        "actor_lr": cfg["actor_lr"],
        "critic_lr": cfg["critic_lr"],
        "loss_mode": cfg.get("loss_mode", "standard"),
        "native_hjb_loss": f"{float(diag['hjb_loss']):.12g}",
        "residual_rmse": f"{residual_rmse:.12g}",
        "mean_abs_residual": f"{float(diag['residual_mean_abs']):.12g}",
        "mean_hamiltonian_abs": f"{mean_h_abs:.12g}",
        "normalized_residual_rmse": f"{normalized:.12g}",
        "terminal_boundary_loss": f"{float(diag['terminal_loss']):.12g}",
        "primary_metric": cfg["primary_metric"],
        "heldout_value": f"{heldout:.12g}",
        "heldout_ci95": f"{ci:.12g}",
        "mean_action": diag["mean_action"],
        "certificate_gap_read": "inventory_normalized_residual_search",
    }


def annotate(rows: list[dict[str, Any]]) -> None:
    headline = next(r for r in rows if r["audit_config"] == "headline_performance_run")
    base_norm = float(headline["normalized_residual_rmse"])
    base_hjb = float(headline["native_hjb_loss"])
    base_term = float(headline["terminal_boundary_loss"])
    base_val = float(headline["heldout_value"])
    for r in rows:
        norm = float(r["normalized_residual_rmse"])
        hjb = float(r["native_hjb_loss"])
        term = float(r["terminal_boundary_loss"])
        val = float(r["heldout_value"])
        r["normalized_rmse_ratio_vs_headline"] = f"{norm / base_norm:.12g}"
        r["hjb_loss_ratio_vs_headline"] = f"{hjb / base_hjb:.12g}"
        r["terminal_loss_ratio_vs_headline"] = f"{term / base_term:.12g}"
        r["heldout_delta_vs_headline"] = f"{val - base_val:.12g}"
        if r["audit_config"] == "headline_performance_run":
            r["claim_status"] = "baseline_inventory_normalized_gap_visible"
        elif norm < base_norm and hjb < base_hjb and val >= base_val - 0.001:
            r["claim_status"] = "normalized_residual_improved_with_native_and_welfare_guard"
        elif norm < base_norm and val >= base_val - 0.001:
            r["claim_status"] = "normalized_residual_improved_with_native_tradeoff"
        elif hjb < base_hjb and val >= base_val - 0.001:
            r["claim_status"] = "native_residual_improved_normalized_not_closed"
        else:
            r["claim_status"] = "no_guarded_normalized_improvement"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--torch-threads", type=int, default=2)
    parser.add_argument("--out", default=str(DATA / "hbo_inventory_normalized_residual_audit.csv"))
    parser.add_argument("--quick", action="store_true")
    args = parser.parse_args()
    torch.set_num_threads(max(1, args.torch_threads))
    out_path = Path(args.out)
    if out_path.exists() and not args.quick:
        rows = read_csv(out_path)
        # Ensure any newly added baseline/reference rows are present.
        existing_labels = {r["audit_config"] for r in rows}
        for row in baseline_rows():
            if row["audit_config"] not in existing_labels:
                rows.append(row)
    else:
        rows = baseline_rows()
    annotate(rows)
    for cfg in configs():
        if args.quick:
            cfg = dict(cfg)
            cfg["train_steps"] = 20
            cfg["batch"] = 32
        if not args.quick and any(r["audit_config"] == cfg["label"] for r in rows):
            print(f"[inventory-normalized] skipping existing {cfg['label']}", flush=True)
            continue
        print(f"[inventory-normalized] running {cfg['label']}", flush=True)
        rows.append(run_config(cfg))
        annotate(rows)
        write_csv(out_path, rows)
        print(f"[inventory-normalized] wrote {args.out}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
