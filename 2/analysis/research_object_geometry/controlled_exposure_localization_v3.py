from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import spearmanr
from sklearn.metrics import average_precision_score, roc_auc_score


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "analysis" / "research_object_geometry"
RESULTS = OUT / "results"
FIGURES = OUT / "figures"
DOCS = OUT / "docs"


@dataclass(frozen=True)
class SimConfig:
    condition: str
    dependency: float
    n_strata: int
    items_per_stratum: int
    hard_fraction: float
    n_agents: int = 3
    max_rounds: int = 14
    actions_per_round: int = 8
    stop_patience: int = 3
    safe_theta: float = 0.90


def ensure_dirs() -> None:
    for path in (RESULTS, FIGURES, DOCS):
        path.mkdir(parents=True, exist_ok=True)


def concentration(values: np.ndarray) -> dict[str, float]:
    total = float(values.sum())
    if total <= 0:
        return {"entropy": math.nan, "hhi": math.nan, "gini": math.nan, "max_mass": math.nan}
    probs = values[values > 0] / total
    entropy = -float(np.sum(probs * np.log(probs))) if probs.size else 0.0
    hhi = float(np.sum(probs * probs)) if probs.size else 0.0
    max_mass = float(probs.max()) if probs.size else math.nan
    sorted_vals = np.sort(values.astype(float))
    n = len(sorted_vals)
    if n == 0 or sorted_vals.sum() == 0:
        gini = math.nan
    else:
        gini = float((2 * np.sum(np.arange(1, n + 1) * sorted_vals) / (n * sorted_vals.sum())) - (n + 1) / n)
    return {"entropy": entropy, "hhi": hhi, "gini": gini, "max_mass": max_mass}


def entropy_effective_rank(matrix: np.ndarray) -> float:
    sv = np.linalg.svd(matrix, compute_uv=False)
    total = sv.sum()
    if total <= 0:
        return 0.0
    p = sv / total
    entropy = -float(np.sum([x * math.log(x) for x in p if x > 0]))
    return math.exp(entropy)


def make_world(cfg: SimConfig, rng: np.random.Generator) -> dict:
    n_hard = max(1, int(round(cfg.n_strata * cfg.hard_fraction)))
    hard_strata = set(rng.choice(np.arange(cfg.n_strata), size=n_hard, replace=False).tolist())
    items = {s: [f"s{s:02d}_item{k:02d}" for k in range(cfg.items_per_stratum)] for s in range(cfg.n_strata)}
    return {"hard_strata": hard_strata, "items": items, "all_items": {x for ids in items.values() for x in ids}}


def agent_distributions(cfg: SimConfig, world: dict, rng: np.random.Generator) -> np.ndarray:
    hard = np.array([s in world["hard_strata"] for s in range(cfg.n_strata)])
    easy = ~hard
    easy_base = np.where(easy, 1.0, 0.10)
    easy_base = easy_base / easy_base.sum()
    uniform = np.ones(cfg.n_strata) / cfg.n_strata
    dists = []
    for agent in range(cfg.n_agents):
        if cfg.condition == "homogeneous":
            base = easy_base
        elif cfg.condition == "prompt_diverse":
            noise = rng.gamma(shape=1.3, scale=1.0, size=cfg.n_strata)
            base = easy_base * (0.5 + noise)
            base = base / base.sum()
        elif cfg.condition in {"route_partitioned", "low_exposure_challenger"}:
            sector = np.zeros(cfg.n_strata)
            sector[agent::cfg.n_agents] = 1.0
            sector = sector + 0.08
            base = sector * np.where(easy, 1.0, 0.55)
            base = base / base.sum()
        elif cfg.condition == "extended_audit":
            sector = np.zeros(cfg.n_strata)
            sector[agent::cfg.n_agents] = 1.0
            base = 0.45 * uniform + 0.55 * (sector / sector.sum())
        else:
            raise ValueError(cfg.condition)
        dist = cfg.dependency * easy_base + (1 - cfg.dependency) * base
        dists.append(dist / dist.sum())
    return np.vstack(dists)


def discover_item(stratum: int, world: dict, seen: set[str], rng: np.random.Generator) -> str | None:
    candidates = [x for x in world["items"][stratum] if x not in seen]
    if not candidates:
        return None
    return candidates[int(rng.integers(0, len(candidates)))]


def simulate(cfg: SimConfig, seed: int) -> dict:
    rng = np.random.default_rng(seed)
    world = make_world(cfg, rng)
    dists = agent_distributions(cfg, world, rng)
    visit = np.zeros((cfg.n_agents, cfg.n_strata), dtype=float)
    discovery = np.zeros((cfg.n_agents, cfg.n_strata), dtype=float)
    union_seen: set[str] = set()
    agent_seen = [set() for _ in range(cfg.n_agents)]
    novelty = []
    stopped_round = cfg.max_rounds

    for round_id in range(1, cfg.max_rounds + 1):
        round_new = 0
        for agent in range(cfg.n_agents):
            for _ in range(cfg.actions_per_round):
                stratum = int(rng.choice(np.arange(cfg.n_strata), p=dists[agent]))
                visit[agent, stratum] += 1
                item = discover_item(stratum, world, agent_seen[agent], rng)
                if item is not None:
                    agent_seen[agent].add(item)
                    discovery[agent, stratum] += 1
                    if item not in union_seen:
                        union_seen.add(item)
                        round_new += 1
        novelty.append(round_new)
        if len(novelty) >= cfg.stop_patience and max(novelty[-cfg.stop_patience:]) == 0:
            stopped_round = round_id
            break

    scout_strategy = "none"
    scout_new = 0
    scout_cost = 0
    if cfg.condition in {"low_exposure_challenger", "extended_audit"}:
        exposure = visit.sum(axis=0)
        discovery_counts = discovery.sum(axis=0)
        if cfg.condition == "low_exposure_challenger":
            scout_strategy = "low_exposure"
            targets = np.argsort(exposure)[: max(3, cfg.n_strata // 4)]
        else:
            scout_strategy = "low_discovery"
            targets = np.argsort(discovery_counts)[: max(3, cfg.n_strata // 4)]
        for s in targets:
            for _ in range(cfg.actions_per_round):
                scout_cost += 1
                item = discover_item(int(s), world, union_seen, rng)
                if item is not None:
                    union_seen.add(item)
                    scout_new += 1

    recall = len(union_seen) / len(world["all_items"])
    false_completion = recall < cfg.safe_theta

    exposure = visit.sum(axis=0)
    discoveries = discovery.sum(axis=0)
    exp_conc = concentration(exposure)
    disc_conc = concentration(discoveries)
    exposure_coverage = float((exposure > 0).mean())
    discovery_coverage = float((discoveries > 0).mean())
    erank_exp = entropy_effective_rank(visit) / min(visit.shape)
    erank_disc = entropy_effective_rank(discovery) / min(discovery.shape)
    discovery_per_exposure = discoveries.sum() / max(exposure.sum(), 1)
    no_new_rounds = 0
    for val in reversed(novelty):
        if val == 0:
            no_new_rounds += 1
        else:
            break

    return {
        "seed": seed,
        "condition": cfg.condition,
        "dependency": cfg.dependency,
        "n_strata": cfg.n_strata,
        "items_per_stratum": cfg.items_per_stratum,
        "hard_fraction": cfg.hard_fraction,
        "stopped_round": stopped_round,
        "no_new_rounds": no_new_rounds,
        "recall": recall,
        "false_completion": false_completion,
        "exposure_gini": exp_conc["gini"],
        "exposure_entropy": exp_conc["entropy"],
        "exposure_hhi": exp_conc["hhi"],
        "exposure_max_mass": exp_conc["max_mass"],
        "discovery_gini": disc_conc["gini"],
        "discovery_entropy": disc_conc["entropy"],
        "discovery_hhi": disc_conc["hhi"],
        "discovery_max_mass": disc_conc["max_mass"],
        "exposure_coverage_ratio": exposure_coverage,
        "discovery_coverage_ratio": discovery_coverage,
        "discovery_per_exposure": discovery_per_exposure,
        "effective_rank_exposure": erank_exp,
        "effective_rank_discovery": erank_disc,
        "scout_strategy": scout_strategy,
        "scout_new_items": scout_new,
        "scout_cost": scout_cost,
        "scout_novelty_per_cost": scout_new / scout_cost if scout_cost else math.nan,
    }


def run_grid() -> pd.DataFrame:
    rows = []
    conditions = ["homogeneous", "prompt_diverse", "route_partitioned", "low_exposure_challenger", "extended_audit"]
    dependencies = [0.0, 0.25, 0.50, 0.75, 0.90, 0.98]
    worlds = [
        {"n_strata": 18, "items_per_stratum": 8, "hard_fraction": 0.25},
        {"n_strata": 30, "items_per_stratum": 6, "hard_fraction": 0.35},
        {"n_strata": 42, "items_per_stratum": 5, "hard_fraction": 0.40},
    ]
    seed = 30000
    for world in worlds:
        for condition in conditions:
            for dependency in dependencies:
                for _ in range(30):
                    rows.append(simulate(SimConfig(condition=condition, dependency=dependency, **world), seed))
                    seed += 1
    return pd.DataFrame(rows)


def screen_metrics(df: pd.DataFrame) -> pd.DataFrame:
    metrics = [
        "exposure_gini",
        "discovery_gini",
        "exposure_coverage_ratio",
        "discovery_coverage_ratio",
        "exposure_hhi",
        "discovery_hhi",
        "exposure_entropy",
        "discovery_entropy",
        "exposure_max_mass",
        "discovery_max_mass",
        "discovery_per_exposure",
        "effective_rank_exposure",
        "effective_rank_discovery",
        "no_new_rounds",
        "stopped_round",
        "scout_novelty_per_cost",
    ]
    y = df["false_completion"].astype(int)
    rows = []
    for metric in metrics:
        x = pd.to_numeric(df[metric], errors="coerce")
        mask = x.notna()
        if mask.sum() < 8 or y[mask].nunique() < 2:
            rows.append({"metric": metric, "n": int(mask.sum()), "spearman_with_false": math.nan, "spearman_p": math.nan, "auroc_abs_direction": math.nan, "auprc_raw_direction": math.nan})
            continue
        rho, p = spearmanr(x[mask], y[mask])
        raw_auc = roc_auc_score(y[mask], x[mask])
        auc = max(raw_auc, 1 - raw_auc)
        auprc = average_precision_score(y[mask], x[mask])
        rows.append({"metric": metric, "n": int(mask.sum()), "spearman_with_false": float(rho), "spearman_p": float(p), "auroc_abs_direction": float(auc), "auprc_raw_direction": float(auprc)})
    return pd.DataFrame(rows).sort_values("auroc_abs_direction", ascending=False, na_position="last")


def leave_world_screen(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for metric in ["exposure_gini", "discovery_gini", "exposure_coverage_ratio", "discovery_coverage_ratio", "effective_rank_exposure", "effective_rank_discovery"]:
        for n_strata, sub in df.groupby("n_strata"):
            y = sub["false_completion"].astype(int)
            x = pd.to_numeric(sub[metric], errors="coerce")
            mask = x.notna()
            if mask.sum() < 8 or y[mask].nunique() < 2:
                auc = math.nan
                rho = math.nan
            else:
                rho, _ = spearmanr(x[mask], y[mask])
                raw_auc = roc_auc_score(y[mask], x[mask])
                auc = max(raw_auc, 1 - raw_auc)
            rows.append({"metric": metric, "n_strata": n_strata, "spearman_with_false": rho, "auroc_abs_direction": auc})
    return pd.DataFrame(rows)


def save_figures(df: pd.DataFrame, screen: pd.DataFrame) -> None:
    colors = df["false_completion"].map({True: "#c0392b", False: "#2c7fb8"})
    plt.figure(figsize=(7, 5))
    plt.scatter(df["exposure_gini"], df["recall"], c=colors, alpha=0.42, edgecolors="none")
    plt.xlabel("Exposure Gini")
    plt.ylabel("Oracle recall")
    plt.grid(alpha=0.25)
    plt.tight_layout()
    plt.savefig(FIGURES / "v3_recall_vs_exposure_gini.png", dpi=180)
    plt.close()

    plt.figure(figsize=(7, 5))
    plt.scatter(df["discovery_gini"], df["recall"], c=colors, alpha=0.42, edgecolors="none")
    plt.xlabel("Discovery Gini")
    plt.ylabel("Oracle recall")
    plt.grid(alpha=0.25)
    plt.tight_layout()
    plt.savefig(FIGURES / "v3_recall_vs_discovery_gini.png", dpi=180)
    plt.close()

    plt.figure(figsize=(7, 5))
    top = screen.head(10).iloc[::-1]
    plt.barh(top["metric"], top["auroc_abs_direction"], color="#637d5f")
    plt.xlim(0.5, 1.0)
    plt.xlabel("AUROC, best direction")
    plt.tight_layout()
    plt.savefig(FIGURES / "v3_metric_screening_auroc.png", dpi=180)
    plt.close()


def write_report(df: pd.DataFrame, screen: pd.DataFrame, stability: pd.DataFrame) -> None:
    cond = df.groupby(["condition", "scout_strategy"]).agg(
        runs=("seed", "count"),
        false_rate=("false_completion", "mean"),
        mean_recall=("recall", "mean"),
        exposure_gini=("exposure_gini", "mean"),
        discovery_gini=("discovery_gini", "mean"),
        exposure_coverage=("exposure_coverage_ratio", "mean"),
        discovery_coverage=("discovery_coverage_ratio", "mean"),
        scout_new_items=("scout_new_items", "mean"),
        scout_gain=("scout_novelty_per_cost", "mean"),
    )
    lines = [
        "# Exposure Localization Simulation v3",
        "",
        "This version tests the user's key refinement: distinguish search exposure localization from discovered-evidence localization.",
        "",
        "## Core Question",
        "",
        "> Is false stopping better explained by localized exposure than by localized discoveries?",
        "",
        "## Metric Screening",
        "",
        screen.head(14).to_markdown(index=False),
        "",
        "## Cross-World Stability",
        "",
        stability.to_markdown(index=False),
        "",
        "## Condition and Challenger Summary",
        "",
        cond.to_markdown(),
        "",
        "## Interpretation",
        "",
        "Exposure Gini measures where the workflow searched, including failed searches. Discovery Gini measures where it found items. If exposure Gini is stronger, the theory should be local exhaustion under localized search. If discovery Gini is stronger, the theory should remain evidence localization.",
        "",
        "The low-exposure challenger is the natural implementation: when no-new stopping is triggered under high exposure localization, audit the least-exposed strata rather than dispatching another free-search agent.",
    ]
    (DOCS / "exposure_localization_v3_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    ensure_dirs()
    df = run_grid()
    screen = screen_metrics(df)
    stability = leave_world_screen(df)
    df.to_csv(RESULTS / "exposure_localization_v3_runs.csv", index=False)
    screen.to_csv(RESULTS / "exposure_localization_v3_metric_screening.csv", index=False)
    stability.to_csv(RESULTS / "exposure_localization_v3_cross_world.csv", index=False)
    save_figures(df, screen)
    write_report(df, screen, stability)
    print(f"runs={len(df)}")
    print(DOCS / "exposure_localization_v3_report.md")


if __name__ == "__main__":
    main()
