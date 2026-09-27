#!/usr/bin/env python3
"""Focused greedy-action-gap audit for selected HBO/NBO policies.

The audit trains selected PyTorch-AD HBO/NBO policies and evaluates, on sampled
state/time validation pairs, the actor-induced residual, the discrete action-grid
optimal Hamiltonian residual, and the greedy action gap max_a H - H_actor.  The
grid maximum is a discrete lower-bound proxy for the continuous-control greedy
gap, so the resulting table is a diagnostic audit rather than a mathematical
certificate.
"""
from __future__ import annotations

import argparse
import csv
import io
import math
import statistics as stats
import sys
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

try:
    import torch
    import run_hbo_full_experiments as hbo  # noqa: E402
    import run_nbo_full_ndu_solver as base  # noqa: E402
except ModuleNotFoundError as exc:  # pragma: no cover - exercised on minimal artifact hosts.
    torch = None  # type: ignore[assignment]
    hbo = None  # type: ignore[assignment]
    base = None  # type: ignore[assignment]
    TORCH_IMPORT_ERROR: ModuleNotFoundError | None = exc
else:
    TORCH_IMPORT_ERROR = None

DTYPE = hbo.DTYPE if hbo is not None else None
DEVICE = hbo.DEVICE if hbo is not None else None

ARCHIVED_AUDIT_CSV = """experiment,method,audit_config,claim_status,train_steps,width,batch,omega,terminal_weight,actor_hjb_weight,actor_lr,critic_lr,final_train_hjb_loss,final_train_residual_rmse,final_train_terminal_loss,final_train_mean_action,primary_metric,heldout_eval_seed_count,heldout_value,heldout_ci95,validation_pairs,terminal_grid_points,action_grid_size,actor_residual_l2,actor_residual_sup_abs,grid_opt_residual_l2,grid_opt_residual_sup_abs,greedy_gap_mean,greedy_gap_p95,greedy_gap_sup,greedy_gap_frac_positive,actor_hamiltonian_mean,grid_hamiltonian_mean,terminal_error_l2,terminal_error_sup_abs
exp1_habit_portfolio,nbo_full_ndu,headline_like_exp1_full_ndu_450,headline_sampled_gap_visible,450,56,96,1.0,2.0,0.05,5e-06,0.0012,2125.082527716191,46.09861741653638,85.17061204423864,0.346849;0.169986;0.0800918,mean_utility,0,nan,nan,720,143,125,50.604628833118355,105.12571397930562,51.25368955764679,104.9624986754299,1.8226798048591841,7.608898156728079,11.972385146928296,1.0,-38.490877656080514,-36.66819785122133,8.988974028674056,16.632934748606406
inventory_service_level,nbo_full_ndu_inventory,headline_like_inventory_full_ndu_450,headline_sampled_gap_visible,450,56,96,1.0,2.0,0.05,5e-06,0.0012,62574.13431044171,250.14822467977203,2062.008626372904,36.006;2.19984,mean_welfare,0,nan,nan,720,180,24,204.63431043336323,805.6222849647322,416.9963063589668,1315.919365680181,201.65158768462288,1257.673488934215,1556.628995601493,0.8125,-68.60426694714303,133.04732073747985,45.597534609208694,75.13641421319521
exp1_habit_portfolio,nbo_full_ndu,exp1_actor_lr_gap_reduced_900,greedy_gap_reduced_but_terminal_gap_visible,900,56,96,1.0,2.0,0.0,0.0001,0.0012,1124.7748616140072,33.537663329665754,168.38469151024708,0.383679;0.169987;0.0810484,mean_utility,10,-3.276931088262189,0.06411761879012173,360,143,125,41.514570715587446,98.63885984764242,41.44291532575201,98.15040912252029,0.7953477090657189,2.7768137772292065,4.134567795771121,0.9944444444444445,-34.1758899041672,-33.38054219510147,11.419298874566651,26.001292538978
inventory_service_level,nbo_full_ndu_inventory,inventory_actor_lr_gap_reduced_900,greedy_gap_reduced_but_terminal_gap_visible,900,56,96,1.0,2.0,0.0,0.0003,0.0012,3040.1867761159815,55.13788875279848,1526.3958070122433,41.0301;2.19986,mean_welfare,10,-3.6420255622384574,0.01423790610542876,360,180,24,46.34878811248784,167.63802974059877,53.163970629057175,167.6128130677896,-11.230620062886109,29.326960415048728,120.0404907198687,0.5138888888888888,-8.452989372279257,-19.683609435165366,40.233440312339454,75.04813946050278
exp1_habit_portfolio,nbo_full_ndu,strong_exp1_residual_terminal_critic_2400,residual_improved_greedy_gap_not_closed,2400,72,192,10.0,18.0,0.0,0.0,0.0009,295.3884434497098,17.18686834329366,42.54966870752022,0.35;0.169986;0.080092,mean_utility,0,nan,nan,720,143,125,31.980815102986977,103.28983968657198,29.54506519797043,102.55234981246616,6.793327765455621,47.26198160632497,110.70965470482147,0.9986111111111111,-35.384459724146936,-28.59113195869132,6.1446464646710455,11.742214799703824
inventory_service_level,nbo_full_ndu_inventory,strong_inventory_residual_balanced_2400,residual_improved_greedy_gap_not_closed,2400,80,192,16.0,32.0,0.1,1e-06,0.0008,12035.602048741044,109.70689152802136,1945.9502095974765,36.006;2.19984,mean_welfare,0,nan,nan,720,180,24,139.11077383346483,642.7464196049312,429.4853419381324,1336.4560399161596,225.6376181506986,1357.4971003933701,1652.0763999975022,0.8472222222222222,-44.99655915208381,180.64105899861474,42.14510231109712,72.35371583637853
"""


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    keys: list[str] = []
    for row in rows:
        for k in row:
            if k not in keys:
                keys.append(k)
    with path.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=keys)
        w.writeheader()
        w.writerows(rows)


def archived_rows() -> list[dict[str, str]]:
    return list(csv.DictReader(io.StringIO(ARCHIVED_AUDIT_CSV)))


def write_archived_audit(path: Path) -> None:
    write_csv(path, archived_rows())


def validation_pairs(spec: base.NBOSpec, n: int, seed: int) -> tuple[np.ndarray, np.ndarray]:
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, spec.state_grid.shape[0], size=n)
    times = rng.integers(0, spec.horizon, size=n)
    if n >= spec.horizon:
        times[: spec.horizon] = np.arange(spec.horizon)
        rng.shuffle(times)
    return times.astype(int), np.asarray(spec.state_grid[idx], dtype=float)


def hamiltonian_from_derivatives(spec: base.NBOSpec, step: int, X: torch.Tensor, A: torch.Tensor, grad_x: torch.Tensor, hess: torch.Tensor) -> torch.Tensor:
    flow, drift, cov = hbo.transition_moments_t(spec, step, X, A)
    diff = 0.5 * torch.einsum("bij,bij->b", cov, hess)
    return flow + torch.sum(grad_x * drift, dim=1) + diff


def audit_policy(policy: hbo.HBOPolicy, spec: base.NBOSpec, *, val_pairs: int, seed: int, action_chunk: int = 64) -> dict[str, float]:
    times, states = validation_pairs(spec, val_pairs, seed)
    actions = torch.as_tensor(spec.actions, dtype=DTYPE, device=DEVICE)
    actor_resid: list[np.ndarray] = []
    grid_resid: list[np.ndarray] = []
    gaps: list[np.ndarray] = []
    actor_hs: list[np.ndarray] = []
    grid_hs: list[np.ndarray] = []
    for step in sorted(set(int(t) for t in times)):
        mask = times == step
        X = torch.as_tensor(states[mask], dtype=DTYPE, device=DEVICE)
        B, dim = X.shape
        tt = torch.full((B,), step / max(1, spec.horizon - 1), dtype=DTYPE, device=DEVICE)
        U = policy.input_matrix_t(tt, X)
        _V, Vt, grad_x, hess = hbo.value_derivatives(policy, U)
        Vt = Vt.detach(); grad_x = grad_x.detach(); hess = hess.detach()
        with torch.no_grad():
            A_actor = policy.action_t(U).detach()
            H_actor = hamiltonian_from_derivatives(spec, step, X, A_actor, grad_x, hess)
            Hmax = torch.full((B,), -float("inf"), dtype=DTYPE, device=DEVICE)
            for a0 in range(0, actions.shape[0], action_chunk):
                Achunk = actions[a0:a0+action_chunk]
                C = Achunk.shape[0]
                Xrep = X[None, :, :].expand(C, B, dim).reshape(C * B, dim)
                Arep = Achunk[:, None, :].expand(C, B, actions.shape[1]).reshape(C * B, actions.shape[1])
                Grep = grad_x[None, :, :].expand(C, B, dim).reshape(C * B, dim)
                Hrep = hess[None, :, :, :].expand(C, B, dim, dim).reshape(C * B, dim, dim)
                H = hamiltonian_from_derivatives(spec, step, Xrep, Arep, Grep, Hrep).reshape(C, B)
                Hmax = torch.maximum(Hmax, torch.max(H, dim=0).values)
            gap = Hmax - H_actor
            actor_resid.append((-Vt - H_actor).cpu().numpy())
            grid_resid.append((-Vt - Hmax).cpu().numpy())
            gaps.append(gap.cpu().numpy())
            actor_hs.append(H_actor.cpu().numpy())
            grid_hs.append(Hmax.cpu().numpy())
    actor_r = np.concatenate(actor_resid)
    grid_r = np.concatenate(grid_resid)
    gap = np.concatenate(gaps)
    actor_h = np.concatenate(actor_hs)
    grid_h = np.concatenate(grid_hs)
    XT = torch.as_tensor(spec.state_grid, dtype=DTYPE, device=DEVICE)
    UT = policy.input_matrix_t(torch.ones(XT.shape[0], dtype=DTYPE, device=DEVICE), XT)
    with torch.no_grad():
        terr = (policy.value_t(UT) - hbo.terminal_value_t(spec, XT)).detach().cpu().numpy()
    return {
        "validation_pairs": val_pairs,
        "terminal_grid_points": int(spec.state_grid.shape[0]),
        "action_grid_size": int(spec.actions.shape[0]),
        "actor_residual_l2": float(np.sqrt(np.mean(actor_r * actor_r))),
        "actor_residual_sup_abs": float(np.max(np.abs(actor_r))),
        "grid_opt_residual_l2": float(np.sqrt(np.mean(grid_r * grid_r))),
        "grid_opt_residual_sup_abs": float(np.max(np.abs(grid_r))),
        "greedy_gap_mean": float(np.mean(gap)),
        "greedy_gap_p95": float(np.quantile(gap, 0.95)),
        "greedy_gap_sup": float(np.max(gap)),
        "greedy_gap_frac_positive": float(np.mean(gap > 0.0)),
        "actor_hamiltonian_mean": float(np.mean(actor_h)),
        "grid_hamiltonian_mean": float(np.mean(grid_h)),
        "terminal_error_l2": float(np.sqrt(np.mean(terr * terr))),
        "terminal_error_sup_abs": float(np.max(np.abs(terr))),
    }


def eval_primary(policy: hbo.HBOPolicy, metric: str, seeds: int) -> tuple[float, float]:
    vals = []
    for j in range(seeds):
        vals.append(float(hbo.eval_policy(policy, 20260512 + 30_000 + j + 1)[metric]))
    ci = 1.96 * stats.stdev(vals) / math.sqrt(len(vals)) if len(vals) > 1 else 0.0
    return float(np.mean(vals)), float(ci)


def configs() -> list[dict[str, Any]]:
    return [
        {"audit_config": "headline_like_exp1_full_ndu_450", "spec": base.exp1_spec("nbo_full_ndu"), "metric": "mean_utility", "seed": 20260512, "train_steps": 450, "width": 56, "batch": 96, "omega": 1.0, "terminal_weight": 2.0, "actor_hjb_weight": 0.05, "actor_lr": 5e-6, "critic_lr": 1.2e-3, "val_pairs": 720, "claim_status": "headline_sampled_gap_visible"},
        {"audit_config": "headline_like_inventory_full_ndu_450", "spec": base.inv_spec("nbo_full_ndu_inventory"), "metric": "mean_welfare", "seed": 20260512 + 30_000, "train_steps": 450, "width": 56, "batch": 96, "omega": 1.0, "terminal_weight": 2.0, "actor_hjb_weight": 0.05, "actor_lr": 5e-6, "critic_lr": 1.2e-3, "val_pairs": 720, "claim_status": "headline_sampled_gap_visible"},
        {"audit_config": "exp1_actor_lr_gap_reduced_900", "spec": base.exp1_spec("nbo_full_ndu"), "metric": "mean_utility", "seed": 20260512 + 45001, "train_steps": 900, "width": 56, "batch": 96, "omega": 1.0, "terminal_weight": 2.0, "actor_hjb_weight": 0.0, "actor_lr": 1e-4, "critic_lr": 1.2e-3, "val_pairs": 360, "claim_status": "greedy_gap_reduced_but_terminal_gap_visible"},
        {"audit_config": "inventory_actor_lr_gap_reduced_900", "spec": base.inv_spec("nbo_full_ndu_inventory"), "metric": "mean_welfare", "seed": 20260512 + 45004, "train_steps": 900, "width": 56, "batch": 96, "omega": 1.0, "terminal_weight": 2.0, "actor_hjb_weight": 0.0, "actor_lr": 3e-4, "critic_lr": 1.2e-3, "val_pairs": 360, "claim_status": "greedy_gap_reduced_but_terminal_gap_visible"},
        {"audit_config": "strong_exp1_residual_terminal_critic_2400", "spec": base.exp1_spec("nbo_full_ndu"), "metric": "mean_utility", "seed": 20260512 + 41002, "train_steps": 2400, "width": 72, "batch": 192, "omega": 10.0, "terminal_weight": 18.0, "actor_hjb_weight": 0.0, "actor_lr": 0.0, "critic_lr": 9e-4, "val_pairs": 720, "claim_status": "residual_improved_greedy_gap_not_closed"},
        {"audit_config": "strong_inventory_residual_balanced_2400", "spec": base.inv_spec("nbo_full_ndu_inventory"), "metric": "mean_welfare", "seed": 20260512 + 42001, "train_steps": 2400, "width": 80, "batch": 192, "omega": 16.0, "terminal_weight": 32.0, "actor_hjb_weight": 0.10, "actor_lr": 1e-6, "critic_lr": 8e-4, "val_pairs": 720, "claim_status": "residual_improved_greedy_gap_not_closed"},
    ]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--quick", action="store_true")
    ap.add_argument(
        "--require-torch",
        action="store_true",
        help="fail instead of writing the deterministic archived audit when PyTorch is unavailable",
    )
    args = ap.parse_args()
    if torch is None:
        if args.require_torch:
            print(f"PyTorch audit unavailable: {TORCH_IMPORT_ERROR}", file=sys.stderr)
            return 2
        out = DATA / "hbo_greedy_gap_audit.csv"
        write_archived_audit(out)
        print(f"{out} (deterministic archived replay; PyTorch unavailable: {TORCH_IMPORT_ERROR})")
        return 0
    torch.set_num_threads(2)
    rows: list[dict[str, Any]] = []
    for cfg in configs():
        if args.quick:
            cfg = dict(cfg)
            cfg["train_steps"] = min(30, int(cfg["train_steps"]))
            cfg["val_pairs"] = min(80, int(cfg["val_pairs"]))
        spec = cfg["spec"]
        policy = hbo.train_hbo(
            spec,
            seed=int(cfg["seed"]),
            width=int(cfg["width"]),
            depth=2,
            train_steps=int(cfg["train_steps"]),
            batch=int(cfg["batch"]),
            omega=float(cfg["omega"]),
            actor_lr=float(cfg["actor_lr"]),
            critic_lr=float(cfg["critic_lr"]),
            terminal_weight=float(cfg["terminal_weight"]),
            actor_hjb_weight=float(cfg["actor_hjb_weight"]),
            grad_clip=10.0,
            init_mode="safe",
        )
        diag = policy.diagnostics[-1]
        audit = audit_policy(policy, spec, val_pairs=int(cfg["val_pairs"]), seed=int(cfg["seed"]) + 919)
        held, held_ci = eval_primary(policy, str(cfg["metric"]), 10 if not args.quick else 0) if not args.quick else (float("nan"), float("nan"))
        row = {
            "experiment": spec.experiment,
            "method": spec.method,
            "audit_config": cfg["audit_config"],
            "claim_status": cfg["claim_status"],
            "train_steps": cfg["train_steps"],
            "width": cfg["width"],
            "batch": cfg["batch"],
            "omega": cfg["omega"],
            "terminal_weight": cfg["terminal_weight"],
            "actor_hjb_weight": cfg["actor_hjb_weight"],
            "actor_lr": cfg["actor_lr"],
            "critic_lr": cfg["critic_lr"],
            "final_train_hjb_loss": float(diag["hjb_loss"]),
            "final_train_residual_rmse": math.sqrt(float(diag["hjb_loss"])),
            "final_train_terminal_loss": float(diag["terminal_loss"]),
            "final_train_mean_action": diag["mean_action"],
            "primary_metric": cfg["metric"],
            "heldout_eval_seed_count": 10 if not args.quick else 0,
            "heldout_value": held,
            "heldout_ci95": held_ci,
            **audit,
        }
        rows.append(row)
        write_csv(DATA / "hbo_greedy_gap_audit.csv", rows)
    print(DATA / "hbo_greedy_gap_audit.csv")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
