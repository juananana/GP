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


def ensure_dirs():
    for path in (RESULTS, FIGURES, DOCS):
        path.mkdir(parents=True, exist_ok=True)


def concentration(values: np.ndarray) -> dict[str, float]:
    total = float(values.sum())
    if total <= 0:
        return {"entropy": math.nan, "hhi": math.nan, "gini": math.nan}
    probs = values[values > 0] / total
    entropy = -float(np.sum(probs * np.log(probs))) if probs.size else 0.0
    hhi = float(np.sum(probs * probs)) if probs.size else 0.0
    sorted_vals = np.sort(values.astype(float))
    n = len(sorted_vals)
    if n == 0 or sorted_vals.sum() == 0:
        gini = math.nan
    else:
        gini = float((2 * np.sum(np.arange(1, n + 1) * sorted_vals) / (n * sorted_vals.sum())) - (n + 1) / n)
    return {"entropy": entropy, "hhi": hhi, "gini": gini}


def entropy_effective_rank(matrix: np.ndarray) -> tuple[float, list[float]]:
    if matrix.size == 0:
        return math.nan, []
    singular_values = np.linalg.svd(matrix, compute_uv=False)
    total = singular_values.sum()
    if total <= 0:
        return 0.0, singular_values.tolist()
    p = singular_values / total
    entropy = -float(np.sum([x * math.log(x) for x in p if x > 0]))
    return math.exp(entropy), singular_values.tolist()


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
        elif cfg.condition == "route_partitioned":
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


def coverage_metrics(coverage: np.ndarray, visit: np.ndarray) -> dict[str, float]:
    evidence = coverage.sum(axis=0)
    route_coverage = float((evidence > 0).mean())
    comp = concentration(evidence)
    visit_comp = concentration(visit.sum(axis=0))
    erank, _ = entropy_effective_rank(coverage)
    normalized_erank = erank / min(coverage.shape) if min(coverage.shape) else math.nan
    return {
        "source_coverage_ratio": route_coverage,
        "coverage_entropy": comp["entropy"],
        "coverage_hhi": comp["hhi"],
        "coverage_gini": comp["gini"],
        "visit_entropy": visit_comp["entropy"],
        "visit_hhi": visit_comp["hhi"],
        "source_normalized_effective_rank": normalized_erank,
    }


def lambda_risk(coverage: np.ndarray) -> float:
    evidence = coverage.sum(axis=0)
    comp = concentration(evidence)
    coverage_ratio = float((evidence > 0).mean())
    return float(comp["gini"] * (1 - coverage_ratio))


def simulate_run(cfg: SimConfig, seed: int) -> dict:
    rng = np.random.default_rng(seed)
    world = make_world(cfg, rng)
    dists = agent_distributions(cfg, world, rng)
    agent_seen = [set() for _ in range(cfg.n_agents)]
    union_seen = set()
    coverage = np.zeros((cfg.n_agents, cfg.n_strata), dtype=float)
    visit = np.zeros((cfg.n_agents, cfg.n_strata), dtype=float)
    novelty_by_round = []
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
                    coverage[agent, stratum] += 1
                    if item not in union_seen:
                        union_seen.add(item)
                        round_new += 1
        novelty_by_round.append(round_new)
        if len(novelty_by_round) >= cfg.stop_patience and max(novelty_by_round[-cfg.stop_patience :]) == 0:
            stopped_round = round_id
            break

    recall = len(union_seen) / len(world["all_items"])
    false_completion = recall < cfg.safe_theta
    metrics = coverage_metrics(coverage, visit)
    lrisk = lambda_risk(coverage)
    scout_mode = cfg.condition in {"route_partitioned", "extended_audit"}
    scout_new = 0
    scout_cost = 0
    scout_strategy = "none"
    if scout_mode:
        scout_strategy = "risk_weighted" if cfg.condition == "extended_audit" else "low_coverage"
        evidence = coverage.sum(axis=0)
        if scout_strategy == "low_coverage":
            targets = np.argsort(evidence)[: max(3, cfg.n_strata // 4)]
        else:
            scores = np.array([(1 - (1 if evidence[s] > 0 else 0)) * (1 + lrisk) for s in range(cfg.n_strata)], dtype=float)
            targets = np.argsort(scores)[::-1][: max(3, cfg.n_strata // 4)]
        for s in targets:
            for _ in range(cfg.actions_per_round):
                scout_cost += 1
                item = discover_item(int(s), world, union_seen, rng)
                if item is not None:
                    union_seen.add(item)
                    scout_new += 1

    metrics.update(
        {
            "seed": seed,
            "condition": cfg.condition,
            "dependency": cfg.dependency,
            "n_strata": cfg.n_strata,
            "items_per_stratum": cfg.items_per_stratum,
            "hard_fraction": cfg.hard_fraction,
            "stopped_round": stopped_round,
            "total_items": len(world["all_items"]),
            "found_items": len(union_seen),
            "recall": recall,
            "false_completion": false_completion,
            "coverage_risk_lambda": lrisk,
            "scout_strategy": scout_strategy,
            "scout_new_items": scout_new,
            "scout_cost": scout_cost,
            "scout_novelty_per_cost": scout_new / scout_cost if scout_cost else math.nan,
        }
    )
    return metrics


def run_grid() -> pd.DataFrame:
    rows = []
    conditions = ["homogeneous", "prompt_diverse", "route_partitioned", "extended_audit"]
    dependencies = [0.0, 0.25, 0.50, 0.75, 0.90, 0.98]
    worlds = [
        {"n_strata": 18, "items_per_stratum": 8, "hard_fraction": 0.25},
        {"n_strata": 30, "items_per_stratum": 6, "hard_fraction": 0.35},
        {"n_strata": 42, "items_per_stratum": 5, "hard_fraction": 0.40},
    ]
    seed = 10000
    for world in worlds:
        for condition in conditions:
            for dependency in dependencies:
                for _ in range(30):
                    cfg = SimConfig(condition=condition, dependency=dependency, **world)
                    rows.append(simulate_run(cfg, seed=seed))
                    seed += 1
    return pd.DataFrame(rows)


def metric_screening(df: pd.DataFrame) -> pd.DataFrame:
    metrics = [
        "coverage_risk_lambda",
        "coverage_gini",
        "source_coverage_ratio",
        "coverage_hhi",
        "coverage_entropy",
        "source_normalized_effective_rank",
        "stopped_round",
        "pairwise_source_placeholder",
        "scout_novelty_per_cost",
    ]
    # pairwise_source_placeholder is left out; keep schema compact.
    rows = []
    y = df["false_completion"].astype(int)
    for metric in metrics:
        if metric not in df.columns:
            continue
        x = pd.to_numeric(df[metric], errors="coerce")
        mask = x.notna()
        if mask.sum() < 8 or y[mask].nunique() < 2:
            rows.append({"metric": metric, "n": int(mask.sum()), "spearman_with_false": math.nan, "spearman_p": math.nan, "auroc_abs_direction": math.nan, "auprc_raw_direction": math.nan})
            continue
        rho, p = spearmanr(x[mask], y[mask])
        scores = x[mask].to_numpy(float)
        labels = y[mask].to_numpy(int)
        auc = roc_auc_score(labels, scores)
        auc = max(auc, 1 - auc)
        auprc = average_precision_score(labels, scores)
        rows.append({"metric": metric, "n": int(mask.sum()), "spearman_with_false": float(rho), "spearman_p": float(p), "auroc_abs_direction": float(auc), "auprc_raw_direction": float(auprc)})
    return pd.DataFrame(rows).sort_values("auroc_abs_direction", ascending=False, na_position="last")


def condition_table(df: pd.DataFrame) -> pd.DataFrame:
    return df.groupby("condition").agg(
        runs=("seed", "count"),
        false_rate=("false_completion", "mean"),
        mean_recall=("recall", "mean"),
        mean_risk=("coverage_risk_lambda", "mean"),
        mean_gini=("coverage_gini", "mean"),
        mean_coverage=("source_coverage_ratio", "mean"),
        mean_erank=("source_normalized_effective_rank", "mean"),
        scout_gain=("scout_novelty_per_cost", "mean"),
    )


def challenger_table(df: pd.DataFrame) -> pd.DataFrame:
    return df.groupby(["condition", "scout_strategy"]).agg(
        runs=("seed", "count"),
        false_rate=("false_completion", "mean"),
        mean_recall=("recall", "mean"),
        mean_gini=("coverage_gini", "mean"),
        mean_coverage=("source_coverage_ratio", "mean"),
        scout_new_items=("scout_new_items", "mean"),
        scout_gain=("scout_novelty_per_cost", "mean"),
    )


def saver(df: pd.DataFrame, screen: pd.DataFrame) -> None:
    plt.figure(figsize=(7, 5))
    plt.scatter(df["coverage_risk_lambda"], df["recall"], c=df["false_completion"].map({True: "#c0392b", False: "#2c7fb8"}), alpha=0.45)
    plt.xlabel("lambda = Gini * (1 - coverage ratio)")
    plt.ylabel("Oracle recall")
    plt.grid(alpha=0.25)
    plt.tight_layout()
    plt.savefig(FIGURES / "v2_recall_vs_lambda.png", dpi=180)
    plt.close()

    plt.figure(figsize=(7, 5))
    plt.scatter(df["coverage_gini"], df["recall"], c=df["false_completion"].map({True: "#c0392b", False: "#2c7fb8"}), alpha=0.45)
    plt.xlabel("Coverage Gini")
    plt.ylabel("Oracle recall")
    plt.grid(alpha=0.25)
    plt.tight_layout()
    plt.savefig(FIGURES / "v2_recall_vs_gini.png", dpi=180)
    plt.close()

    plt.figure(figsize=(7, 5))
    top = screen.head(8).iloc[::-1]
    plt.barh(top["metric"], top["auroc_abs_direction"], color="#5b7c99")
    plt.xlim(0.5, 1.0)
    plt.xlabel("AUROC, best direction")
    plt.tight_layout()
    plt.savefig(FIGURES / "v2_metric_screening_auroc.png", dpi=180)
    plt.close()


def report(df: pd.DataFrame, screen: pd.DataFrame, condition_df: pd.DataFrame, challenger_df: pd.DataFrame) -> None:
    by_dep = df.groupby("dependency").agg(
        false_rate=("false_completion", "mean"),
        mean_recall=("recall", "mean"),
        mean_lambda=("coverage_risk_lambda", "mean"),
        mean_gini=("coverage_gini", "mean"),
        mean_coverage=("source_coverage_ratio", "mean"),
    )
    lines = [
        "# Controlled Geometry Simulation v2",
        "",
        "This version isolates the candidate order parameter:",
        "",
        "> lambda = coverage_gini * (1 - source_coverage_ratio)",
        "",
        "It asks whether a simple coverage-localization risk quantity is stronger than the individual ingredients.",
        "",
        "## Condition Summary",
        "",
        condition_df.to_markdown(),
        "",
        "## Dependency Summary",
        "",
        by_dep.to_markdown(),
        "",
        "## Metric Screening",
        "",
        screen.head(10).to_markdown(index=False),
        "",
        "## Challenger Ablation",
        "",
        challenger_df.to_markdown(),
        "",
        "## Interpretation",
        "",
        "The compound lambda risk does not beat plain coverage Gini in this construction. The theory should therefore stay with plain coverage localization first, rather than overfitting a compound formula.",
        "",
        "The residual challenger is operationally defined by the same geometry: target source-route strata with low observed coverage under high localization. This turns the geometry into a search policy without claiming an advanced geometric controller.",
    ]
    (DOCS / "controlled_geometry_v2_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    ensure_dirs()
    df = run_grid()
    screen = metric_screening(df)
    cond = condition_table(df)
    challenger = challenger_table(df)
    df.to_csv(RESULTS / "controlled_geometry_v2_runs.csv", index=False)
    screen.to_csv(RESULTS / "controlled_geometry_v2_metric_screening.csv", index=False)
    cond.to_csv(RESULTS / "controlled_geometry_v2_condition_summary.csv")
    challenger.to_csv(RESULTS / "controlled_geometry_v2_challenger_ablation.csv")
    saver(df, screen)
    report(df, screen, cond, challenger)
    print(f"runs={len(df)}")
    print(f"report={DOCS / 'controlled_geometry_v2_report.md'}")


if __name__ == "__main__":
    main()
