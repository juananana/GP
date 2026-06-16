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
    no_new_threshold: int = 1
    safe_theta: float = 0.90


def ensure_dirs() -> None:
    for path in (RESULTS, FIGURES, DOCS):
        path.mkdir(parents=True, exist_ok=True)


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


def logdet_volume(matrix: np.ndarray, eps: float = 1e-6) -> float:
    if matrix.size == 0:
        return math.nan
    gram = matrix @ matrix.T
    sign, value = np.linalg.slogdet(gram + eps * np.eye(gram.shape[0]))
    return float(value) if sign > 0 else math.nan


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


def pairwise_cosine(matrix: np.ndarray) -> float:
    vals = []
    for i in range(matrix.shape[0]):
        for j in range(i + 1, matrix.shape[0]):
            denom = np.linalg.norm(matrix[i]) * np.linalg.norm(matrix[j])
            if denom > 0:
                vals.append(float(np.dot(matrix[i], matrix[j]) / denom))
    return float(np.mean(vals)) if vals else math.nan


def pairwise_jaccard(binary: np.ndarray) -> float:
    vals = []
    for i in range(binary.shape[0]):
        for j in range(i + 1, binary.shape[0]):
            inter = np.logical_and(binary[i] > 0, binary[j] > 0).sum()
            union = np.logical_or(binary[i] > 0, binary[j] > 0).sum()
            if union > 0:
                vals.append(float(inter / union))
    return float(np.mean(vals)) if vals else math.nan


def make_world(cfg: SimConfig, rng: np.random.Generator) -> dict:
    n_hard = max(1, int(round(cfg.n_strata * cfg.hard_fraction)))
    hard_strata = set(rng.choice(np.arange(cfg.n_strata), size=n_hard, replace=False).tolist())
    item_ids_by_stratum = {}
    all_items = []
    for s in range(cfg.n_strata):
        ids = [f"s{s:02d}_item{k:02d}" for k in range(cfg.items_per_stratum)]
        item_ids_by_stratum[s] = ids
        all_items.extend(ids)
    return {"hard_strata": hard_strata, "items": item_ids_by_stratum, "all_items": set(all_items)}


def distributions(cfg: SimConfig, world: dict, rng: np.random.Generator) -> np.ndarray:
    hard = np.array([s in world["hard_strata"] for s in range(cfg.n_strata)])
    easy = ~hard
    easy_base = np.where(easy, 1.0, 0.10)
    easy_base = easy_base / easy_base.sum()
    uniform = np.ones(cfg.n_strata) / cfg.n_strata

    dists = []
    for agent in range(cfg.n_agents):
        if cfg.condition == "homogeneous":
            agent_specific = easy_base
        elif cfg.condition == "prompt_diverse":
            noise = rng.gamma(shape=1.3, scale=1.0, size=cfg.n_strata)
            agent_specific = easy_base * (0.6 + noise)
            agent_specific = agent_specific / agent_specific.sum()
        elif cfg.condition == "route_partitioned":
            sector = np.zeros(cfg.n_strata)
            sector[agent::cfg.n_agents] = 1.0
            sector = sector + 0.08
            # Route partitioning still inherits some easy-basin bias.
            agent_specific = sector * np.where(easy, 1.0, 0.55)
            agent_specific = agent_specific / agent_specific.sum()
        elif cfg.condition == "residual_targeted":
            # Main agents begin with diverse exploration; the residual scout is
            # simulated later by targeting low-coverage strata.
            noise = rng.gamma(shape=1.3, scale=1.0, size=cfg.n_strata)
            agent_specific = easy_base * (0.6 + noise)
            agent_specific = agent_specific / agent_specific.sum()
        elif cfg.condition == "extended_audit":
            sector = np.zeros(cfg.n_strata)
            sector[agent::cfg.n_agents] = 1.0
            agent_specific = 0.5 * uniform + 0.5 * (sector / sector.sum())
        else:
            raise ValueError(f"unknown condition {cfg.condition}")

        dist = cfg.dependency * easy_base + (1 - cfg.dependency) * agent_specific
        dist = dist / dist.sum()
        dists.append(dist)
    return np.vstack(dists)


def discover_from_stratum(stratum: int, world: dict, seen: set[str], rng: np.random.Generator) -> str | None:
    candidates = [x for x in world["items"][stratum] if x not in seen]
    if not candidates:
        return None
    return candidates[int(rng.integers(0, len(candidates)))]


def simulate_run(cfg: SimConfig, seed: int) -> dict:
    rng = np.random.default_rng(seed)
    world = make_world(cfg, rng)
    dists = distributions(cfg, world, rng)

    agent_seen = [set() for _ in range(cfg.n_agents)]
    union_seen = set()
    coverage = np.zeros((cfg.n_agents, cfg.n_strata), dtype=float)
    visit = np.zeros((cfg.n_agents, cfg.n_strata), dtype=float)
    new_by_round = []

    stopped_round = cfg.max_rounds
    for round_id in range(1, cfg.max_rounds + 1):
        round_new = 0
        for agent in range(cfg.n_agents):
            for _ in range(cfg.actions_per_round):
                stratum = int(rng.choice(np.arange(cfg.n_strata), p=dists[agent]))
                visit[agent, stratum] += 1
                item = discover_from_stratum(stratum, world, agent_seen[agent], rng)
                if item is not None:
                    agent_seen[agent].add(item)
                    coverage[agent, stratum] += 1
                    if item not in union_seen:
                        union_seen.add(item)
                        round_new += 1
        new_by_round.append(round_new)
        if len(new_by_round) >= cfg.stop_patience and max(new_by_round[-cfg.stop_patience :]) <= cfg.no_new_threshold:
            stopped_round = round_id
            break

    scout_new = 0
    scout_true_new = 0
    scout_cost = 0
    if cfg.condition == "residual_targeted":
        union_counts = coverage.sum(axis=0)
        low_coverage = np.argsort(union_counts)[: max(3, cfg.n_strata // 4)]
        for stratum in low_coverage:
            for _ in range(cfg.actions_per_round):
                scout_cost += 1
                item = discover_from_stratum(int(stratum), world, union_seen, rng)
                if item is not None:
                    union_seen.add(item)
                    scout_new += 1
                    scout_true_new += 1
                    coverage[:, int(stratum)] += 1 / cfg.n_agents

    recall = len(union_seen) / len(world["all_items"])
    false_completion = recall < cfg.safe_theta
    erank, singular_values = entropy_effective_rank(coverage)
    normalized_erank = erank / min(coverage.shape) if min(coverage.shape) else math.nan
    conc = concentration(coverage.sum(axis=0))
    source_coverage_ratio = float((coverage.sum(axis=0) > 0).mean())
    route_jaccard = pairwise_jaccard(coverage)
    cosine = pairwise_cosine(coverage)
    volume = logdet_volume(coverage)
    visit_conc = concentration(visit.sum(axis=0))

    return {
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
        "source_coverage_ratio": source_coverage_ratio,
        "coverage_entropy": conc["entropy"],
        "coverage_hhi": conc["hhi"],
        "coverage_gini": conc["gini"],
        "visit_entropy": visit_conc["entropy"],
        "visit_hhi": visit_conc["hhi"],
        "source_normalized_effective_rank": normalized_erank,
        "source_logdet_volume": volume,
        "pairwise_route_jaccard": route_jaccard,
        "pairwise_cosine": cosine,
        "scout_new_items": scout_new,
        "scout_new_true_items": scout_true_new,
        "scout_cost": scout_cost,
        "scout_novelty_per_cost": scout_true_new / scout_cost if scout_cost else math.nan,
        "singular_values": ";".join(f"{x:.5g}" for x in singular_values),
    }


def run_grid() -> pd.DataFrame:
    rows = []
    conditions = ["homogeneous", "prompt_diverse", "route_partitioned", "residual_targeted", "extended_audit"]
    dependencies = [0.0, 0.25, 0.50, 0.75, 0.90, 0.98]
    worlds = [
        {"n_strata": 18, "items_per_stratum": 8, "hard_fraction": 0.25},
        {"n_strata": 30, "items_per_stratum": 6, "hard_fraction": 0.35},
        {"n_strata": 42, "items_per_stratum": 5, "hard_fraction": 0.40},
    ]
    seed = 0
    for world in worlds:
        for condition in conditions:
            for dependency in dependencies:
                for rep in range(40):
                    cfg = SimConfig(condition=condition, dependency=dependency, **world)
                    rows.append(simulate_run(cfg, seed=seed))
                    seed += 1
    return pd.DataFrame(rows)


def metric_screening(df: pd.DataFrame) -> pd.DataFrame:
    metrics = [
        "source_coverage_ratio",
        "coverage_entropy",
        "coverage_hhi",
        "coverage_gini",
        "visit_entropy",
        "visit_hhi",
        "source_normalized_effective_rank",
        "source_logdet_volume",
        "pairwise_route_jaccard",
        "pairwise_cosine",
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
        scores = x[mask].to_numpy(float)
        labels = y[mask].to_numpy(int)
        auc = roc_auc_score(labels, scores)
        auc = max(auc, 1 - auc)
        auprc = average_precision_score(labels, scores)
        rows.append({"metric": metric, "n": int(mask.sum()), "spearman_with_false": float(rho), "spearman_p": float(p), "auroc_abs_direction": float(auc), "auprc_raw_direction": float(auprc)})
    return pd.DataFrame(rows).sort_values("auroc_abs_direction", ascending=False, na_position="last")


def stability_screening(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for metric in [
        "source_coverage_ratio",
        "coverage_gini",
        "coverage_hhi",
        "coverage_entropy",
        "source_normalized_effective_rank",
        "source_logdet_volume",
        "pairwise_route_jaccard",
    ]:
        for n_strata, sub in df.groupby("n_strata"):
            x = pd.to_numeric(sub[metric], errors="coerce")
            y = sub["false_completion"].astype(int)
            mask = x.notna()
            if mask.sum() < 8 or y[mask].nunique() < 2:
                rho, auc = math.nan, math.nan
            else:
                rho, _ = spearmanr(x[mask], y[mask])
                raw_auc = roc_auc_score(y[mask], x[mask])
                auc = max(raw_auc, 1 - raw_auc)
            rows.append({"metric": metric, "n_strata": n_strata, "spearman_with_false": rho, "auroc_abs_direction": auc})
    return pd.DataFrame(rows)


def save_figures(df: pd.DataFrame, screen: pd.DataFrame) -> None:
    plt.figure(figsize=(7, 5))
    for condition, sub in df.groupby("condition"):
        grouped = sub.groupby("dependency")["recall"].mean()
        plt.plot(grouped.index, grouped.values, marker="o", label=condition)
    plt.xlabel("Exploration dependency")
    plt.ylabel("Mean oracle recall")
    plt.grid(alpha=0.25)
    plt.legend(fontsize=8)
    plt.tight_layout()
    plt.savefig(FIGURES / "controlled_recall_vs_dependency.png", dpi=180)
    plt.close()

    plt.figure(figsize=(7, 5))
    colors = df["false_completion"].map({True: "#c0392b", False: "#2c7fb8"})
    plt.scatter(df["source_coverage_ratio"], df["recall"], c=colors, alpha=0.45, edgecolors="none")
    plt.xlabel("Source coverage ratio")
    plt.ylabel("Oracle recall")
    plt.grid(alpha=0.25)
    plt.tight_layout()
    plt.savefig(FIGURES / "controlled_recall_vs_source_coverage.png", dpi=180)
    plt.close()

    plt.figure(figsize=(7, 5))
    colors = df["false_completion"].map({True: "#c0392b", False: "#2c7fb8"})
    plt.scatter(df["source_normalized_effective_rank"], df["recall"], c=colors, alpha=0.45, edgecolors="none")
    plt.xlabel("Normalized effective rank")
    plt.ylabel("Oracle recall")
    plt.grid(alpha=0.25)
    plt.tight_layout()
    plt.savefig(FIGURES / "controlled_recall_vs_erank.png", dpi=180)
    plt.close()

    plt.figure(figsize=(7, 5))
    top = screen.head(8).iloc[::-1]
    plt.barh(top["metric"], top["auroc_abs_direction"], color="#4d7c8a")
    plt.xlim(0.5, 1.0)
    plt.xlabel("AUROC, best direction")
    plt.tight_layout()
    plt.savefig(FIGURES / "controlled_metric_screening_auroc.png", dpi=180)
    plt.close()


def write_report(df: pd.DataFrame, screen: pd.DataFrame, stable: pd.DataFrame) -> None:
    label_counts = df["false_completion"].value_counts().rename_axis("false_completion").reset_index(name="count")
    by_condition = df.groupby("condition").agg(
        runs=("seed", "count"),
        false_rate=("false_completion", "mean"),
        mean_recall=("recall", "mean"),
        mean_source_coverage=("source_coverage_ratio", "mean"),
        mean_erank=("source_normalized_effective_rank", "mean"),
        mean_hhi=("coverage_hhi", "mean"),
        scout_gain=("scout_novelty_per_cost", "mean"),
    )
    lines = [
        "# Controlled Coverage-Geometry Simulation Report",
        "",
        "Status: controlled mechanism construction. This is not real-agent evidence and not a method claim.",
        "",
        "## Purpose",
        "",
        "We test whether a bottom-up closed-world discovery environment can exhibit false stopping controlled by measurable coverage geometry. This answers a necessary precondition: if geometry cannot be made predictive in a clean mechanism model, it is unlikely to be the right research core.",
        "",
        "## Construction",
        "",
        "- A world contains hidden target items distributed over source-route strata.",
        "- Easy strata are oversampled; hard strata contain valid items but are less likely under correlated exploration.",
        "- Three main agents sample strata over rounds and stop after repeated low novelty.",
        "- Conditions vary exploration dependence and route assignment.",
        "- Oracle recall is available only after the run.",
        "",
        "## Label Balance",
        "",
        label_counts.to_markdown(index=False),
        "",
        "## Condition Summary",
        "",
        by_condition.to_markdown(),
        "",
        "## Metric Screening",
        "",
        screen.head(10).to_markdown(index=False),
        "",
        "## Cross-World Stability",
        "",
        stable.to_markdown(index=False),
        "",
        "## Interpretation",
        "",
        "In this controlled construction, a geometry signal does exist, but it is mostly the simple geometry of source-route coverage localization. The strongest candidate control quantity is coverage Gini: discovered evidence becomes concentrated in a small subset of strata while the workflow's novelty signal is exhausted. Source coverage ratio is also useful. Effective rank and log-det are informative but weaker than this localization signal.",
        "",
        "This means the current best hypothesis is not yet a Grassmann/subspace theory. It is a coverage-localization or coverage-saturation theory: false stopping emerges when observed novelty is exhausted inside a locally concentrated explored region while global source-route coverage remains incomplete.",
        "",
        "## Go / No-Go",
        "",
        "Go for a small real-agent diagnostic, not yet for a geometry method paper.",
        "",
        "The next real experiment should test whether source-route coverage ratio, coverage concentration, and effective rank retain predictive value when generated by actual agent trajectories. If simple source coverage dominates, the paper should stay with safe stopping and evidence-ledger control rather than advanced geometry.",
    ]
    (DOCS / "controlled_geometry_simulation_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    ensure_dirs()
    df = run_grid()
    screen = metric_screening(df)
    stable = stability_screening(df)
    df.to_csv(RESULTS / "controlled_geometry_simulation_runs.csv", index=False)
    screen.to_csv(RESULTS / "controlled_geometry_metric_screening.csv", index=False)
    stable.to_csv(RESULTS / "controlled_geometry_cross_world_stability.csv", index=False)
    save_figures(df, screen)
    write_report(df, screen, stable)
    print(f"wrote {len(df)} simulated runs")
    print(f"report: {DOCS / 'controlled_geometry_simulation_report.md'}")


if __name__ == "__main__":
    main()
