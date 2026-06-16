import csv
import json
import math
from collections import Counter, defaultdict
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import spearmanr
from sklearn.metrics import average_precision_score, roc_auc_score


ROOT = Path(__file__).resolve().parents[2]
EXP = ROOT / "liudang1" / "experiments" / "false_convergence_pilot"
OUT = ROOT / "analysis" / "coverage_geometry_diagnostics"
RESULTS = OUT / "results"
FIGURES = OUT / "figures"
DOCS = OUT / "docs"


def ensure_dirs():
    for path in (RESULTS, FIGURES, DOCS):
        path.mkdir(parents=True, exist_ok=True)


def load_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def source_family(file_path):
    if not file_path:
        return "unknown"
    path = file_path.replace("\\", "/")
    parts = [p for p in path.split("/") if p and p != "repo"]
    if len(parts) >= 2:
        return "/".join(parts[:2])
    return parts[0] if parts else "unknown"


def item_id(item):
    return f"{item.get('file_path', 'unknown')}:{item.get('line', '')}"


def run_file_for(score_path, run_id):
    base = score_path.parent
    candidates = [
        base / "runs" / f"{run_id}.json",
        base / "raw" / f"{run_id}_raw_response.json",
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    hits = list(base.rglob(f"{run_id}.json"))
    if hits:
        return hits[0]
    return None


def infer_repo(score_path, task_id):
    text = str(score_path).replace("\\", "/").lower()
    if "requests" in text or "requests" in task_id.lower():
        return "requests"
    if "click" in text or "click" in task_id.lower():
        return "click"
    if "itsdangerous" in text or "itsdangerous" in task_id.lower():
        return "itsdangerous"
    return "unknown"


def infer_condition(score_path):
    parent = score_path.parent.name
    if parent.startswith("seed"):
        return score_path.parent.parent.name
    return parent


def entropy_effective_rank(matrix):
    if matrix.size == 0:
        return float("nan"), []
    singular_values = np.linalg.svd(matrix, compute_uv=False)
    total = singular_values.sum()
    if total <= 0:
        return 0.0, singular_values.tolist()
    p = singular_values / total
    entropy = -float(np.sum([x * math.log(x) for x in p if x > 0]))
    return math.exp(entropy), singular_values.tolist()


def logdet_volume(matrix, eps=1e-6):
    if matrix.size == 0:
        return float("nan")
    gram = matrix @ matrix.T
    sign, value = np.linalg.slogdet(gram + eps * np.eye(gram.shape[0]))
    return float(value) if sign > 0 else float("nan")


def mean_pairwise_cosine(matrix):
    if matrix.shape[0] < 2:
        return float("nan")
    sims = []
    for i in range(matrix.shape[0]):
        for j in range(i + 1, matrix.shape[0]):
            a, b = matrix[i], matrix[j]
            denom = np.linalg.norm(a) * np.linalg.norm(b)
            sims.append(float(np.dot(a, b) / denom) if denom else float("nan"))
    vals = [v for v in sims if not math.isnan(v)]
    return float(np.mean(vals)) if vals else float("nan")


def concentration(values):
    total = sum(values)
    if total <= 0:
        return {"entropy": float("nan"), "hhi": float("nan"), "gini": float("nan")}
    probs = np.array([v / total for v in values if v > 0], dtype=float)
    entropy = -float(np.sum(probs * np.log(probs))) if probs.size else 0.0
    hhi = float(np.sum(probs * probs)) if probs.size else 0.0
    sorted_vals = np.sort(np.array(values, dtype=float))
    n = len(sorted_vals)
    if n == 0 or sorted_vals.sum() == 0:
        gini = float("nan")
    else:
        gini = float((2 * np.sum((np.arange(1, n + 1)) * sorted_vals) / (n * sorted_vals.sum())) - (n + 1) / n)
    return {"entropy": entropy, "hhi": hhi, "gini": gini}


def marginal_logdet_gain(matrix):
    if matrix.shape[0] < 2:
        return float("nan")
    gains = []
    prev = None
    for i in range(1, matrix.shape[0] + 1):
        current = logdet_volume(matrix[:i, :])
        if prev is not None and not math.isnan(current) and not math.isnan(prev):
            gains.append(current - prev)
        prev = current
    return float(np.mean(gains)) if gains else float("nan")


def collect_states():
    rows = []
    metric_rows = []
    missing_runs = []

    for score_path in sorted(EXP.rglob("score_summary.json")):
        data = load_json(score_path)
        task_id = data.get("task_id", "unknown")
        repo = infer_repo(score_path, task_id)
        condition = infer_condition(score_path)
        oracle_size = data.get("oracle_size")
        seed_summaries = data.get("seed_summaries") or []
        if not seed_summaries:
            continue
        seed_summary = seed_summaries[0]
        run_ids = seed_summary.get("g3_run_ids") or data.get("raw_run_ids") or []
        agents = []
        for rid in run_ids:
            run_path = run_file_for(score_path, rid)
            if not run_path:
                missing_runs.append({"score_summary": str(score_path), "run_id": rid})
                continue
            run = load_json(run_path)
            items = run.get("items") or []
            item_set = set(item_id(x) for x in items)
            source_counts = Counter(source_family(x.get("file_path")) for x in items)
            file_counts = Counter(x.get("file_path", "unknown") for x in items)
            agents.append(
                {
                    "run_id": rid,
                    "completion": run.get("self_reported_completion"),
                    "confidence": run.get("self_reported_confidence"),
                    "items": item_set,
                    "source_counts": source_counts,
                    "file_counts": file_counts,
                    "found": len(items),
                }
            )

        if not agents:
            continue

        strata = sorted(set().union(*(a["source_counts"].keys() for a in agents)))
        matrix = np.array([[a["source_counts"].get(s, 0) for s in strata] for a in agents], dtype=float)
        file_strata = sorted(set().union(*(a["file_counts"].keys() for a in agents)))
        file_matrix = np.array([[a["file_counts"].get(s, 0) for s in file_strata] for a in agents], dtype=float)

        erank, sv = entropy_effective_rank(matrix)
        file_erank, _ = entropy_effective_rank(file_matrix)
        denom = min(matrix.shape) if matrix.size else 0
        normalized_erank = erank / denom if denom else float("nan")
        volume = logdet_volume(matrix)
        gain = marginal_logdet_gain(matrix)
        source_cosine = mean_pairwise_cosine(matrix)

        union_items = set().union(*(a["items"] for a in agents))
        item_support = Counter()
        for a in agents:
            for item in a["items"]:
                item_support[item] += 1
        singleton_ratio = (
            sum(1 for c in item_support.values() if c == 1) / len(item_support)
            if item_support
            else float("nan")
        )
        item_jaccards = []
        source_jaccards = []
        for i in range(len(agents)):
            for j in range(i + 1, len(agents)):
                ai, aj = agents[i]["items"], agents[j]["items"]
                union = ai | aj
                item_jaccards.append(len(ai & aj) / len(union) if union else float("nan"))
                si, sj = set(agents[i]["source_counts"]), set(agents[j]["source_counts"])
                sunion = si | sj
                source_jaccards.append(len(si & sj) / len(sunion) if sunion else float("nan"))

        total_source_counts = Counter()
        for a in agents:
            total_source_counts.update(a["source_counts"])
        conc = concentration(list(total_source_counts.values()))
        row = {
            "state_id": str(score_path.relative_to(EXP)).replace("\\", "/").replace("/score_summary.json", ""),
            "score_summary_path": str(score_path.relative_to(ROOT)).replace("\\", "/"),
            "task_id": task_id,
            "repository": repo,
            "condition": condition,
            "seed": seed_summary.get("seed"),
            "num_agents": len(agents),
            "oracle_size": oracle_size,
            "mean_confidence": seed_summary.get("mean_confidence"),
            "all_agents_report_completion": all(a["completion"] is True for a in agents),
            "mean_pairwise_item_jaccard_from_runs": np.nanmean(item_jaccards) if item_jaccards else float("nan"),
            "mean_pairwise_item_jaccard_from_score": seed_summary.get("mean_pairwise_jaccard"),
            "mean_pairwise_source_jaccard": np.nanmean(source_jaccards) if source_jaccards else float("nan"),
            "source_coverage_count": len(strata),
            "file_coverage_count": len(file_strata),
            "union_found": (seed_summary.get("union") or {}).get("found"),
            "union_true_positive": (seed_summary.get("union") or {}).get("true_positive"),
            "union_recall": (seed_summary.get("union") or {}).get("recall"),
            "union_precision": (seed_summary.get("union") or {}).get("precision"),
            "consensus_recall": (seed_summary.get("consensus") or {}).get("recall"),
            "holdout_gain": seed_summary.get("holdout_gain"),
            "holdout_new_true_items": len(seed_summary.get("holdout_new_true_items") or []),
            "false_completion_theta_090": bool(all(a["completion"] is True for a in agents) and (seed_summary.get("union") or {}).get("recall", 0) < 0.90),
            "false_completion_theta_095": bool(all(a["completion"] is True for a in agents) and (seed_summary.get("union") or {}).get("recall", 0) < 0.95),
            "false_completion_theta_100": bool(all(a["completion"] is True for a in agents) and (seed_summary.get("union") or {}).get("recall", 0) < 1.00),
            "singleton_ratio_from_runs": singleton_ratio,
            "singleton_ratio_from_score": seed_summary.get("singleton_ratio"),
            "source_pairwise_cosine": source_cosine,
            "source_entropy_effective_rank": erank,
            "source_normalized_effective_rank": normalized_erank,
            "file_entropy_effective_rank": file_erank,
            "source_logdet_volume": volume,
            "source_marginal_logdet_gain": gain,
            "source_concentration_entropy": conc["entropy"],
            "source_concentration_hhi": conc["hhi"],
            "source_concentration_gini": conc["gini"],
            "singular_values": ";".join(f"{x:.6g}" for x in sv),
        }
        rows.append(row)

        for i, agent in enumerate(agents):
            for s in strata:
                metric_rows.append(
                    {
                        "state_id": row["state_id"],
                        "run_id": agent["run_id"],
                        "agent_index": i + 1,
                        "stratum_type": "source_family",
                        "stratum": s,
                        "discovered_item_count": agent["source_counts"].get(s, 0),
                    }
                )

    return pd.DataFrame(rows), pd.DataFrame(metric_rows), missing_runs


def auc_table(df):
    candidates = [
        "mean_pairwise_item_jaccard_from_score",
        "mean_pairwise_source_jaccard",
        "source_coverage_count",
        "singleton_ratio_from_score",
        "source_pairwise_cosine",
        "source_normalized_effective_rank",
        "source_logdet_volume",
        "source_marginal_logdet_gain",
        "source_concentration_entropy",
        "source_concentration_hhi",
        "source_concentration_gini",
        "mean_confidence",
    ]
    rows = []
    y = df["false_completion_theta_095"].astype(int)
    for col in candidates:
        vals = pd.to_numeric(df[col], errors="coerce")
        mask = vals.notna()
        if mask.sum() < 4 or y[mask].nunique() < 2:
            rows.append({"metric": col, "n": int(mask.sum()), "spearman_r": np.nan, "spearman_p": np.nan, "auroc_abs_direction": np.nan, "auprc_raw_direction": np.nan})
            continue
        rho, p = spearmanr(vals[mask], y[mask])
        score = vals[mask].to_numpy(dtype=float)
        labels = y[mask].to_numpy(dtype=int)
        try:
            auc = roc_auc_score(labels, score)
            auc = max(auc, 1 - auc)
        except ValueError:
            auc = np.nan
        try:
            auprc = average_precision_score(labels, score)
        except ValueError:
            auprc = np.nan
        rows.append({"metric": col, "n": int(mask.sum()), "spearman_r": rho, "spearman_p": p, "auroc_abs_direction": auc, "auprc_raw_direction": auprc})
    return pd.DataFrame(rows)


def per_repository_auc_table(df):
    tables = []
    for repo, subset in df.groupby("repository"):
        repo_table = auc_table(subset)
        repo_table.insert(0, "repository", repo)
        tables.append(repo_table)
    return pd.concat(tables, ignore_index=True) if tables else pd.DataFrame()


def save_plots(df):
    def scatter(x, y, color, path, xlabel, ylabel):
        plot_df = df[[x, y, color, "repository"]].copy()
        plot_df[x] = pd.to_numeric(plot_df[x], errors="coerce")
        plot_df[y] = pd.to_numeric(plot_df[y], errors="coerce")
        plot_df = plot_df.dropna(subset=[x, y])
        plt.figure(figsize=(7, 5))
        colors = plot_df[color].map({True: "#c0392b", False: "#2c7fb8"}).fillna("#777777")
        plt.scatter(plot_df[x], plot_df[y], c=colors, alpha=0.78, edgecolors="white", linewidths=0.5)
        for repo, grp in plot_df.groupby("repository"):
            plt.scatter([], [], label=repo)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.grid(alpha=0.25)
        plt.tight_layout()
        plt.savefig(path, dpi=180)
        plt.close()

    scatter(
        "source_normalized_effective_rank",
        "union_recall",
        "false_completion_theta_095",
        FIGURES / "false_completion_vs_erank.png",
        "Normalized source effective rank",
        "Union recall",
    )
    scatter(
        "source_marginal_logdet_gain",
        "union_recall",
        "false_completion_theta_095",
        FIGURES / "false_completion_vs_logdet_gain.png",
        "Mean marginal logdet gain",
        "Union recall",
    )
    scatter(
        "source_concentration_hhi",
        "union_recall",
        "false_completion_theta_095",
        FIGURES / "recall_vs_source_concentration.png",
        "Source concentration HHI",
        "Union recall",
    )
    scatter(
        "source_pairwise_cosine",
        "holdout_gain",
        "false_completion_theta_095",
        FIGURES / "scout_gain_vs_residual_projection.png",
        "Scout route proxy: main-agent source cosine",
        "Holdout gain",
    )

    safe = df[df["false_completion_theta_095"] == False]
    false = df[df["false_completion_theta_095"] == True]
    plt.figure(figsize=(7, 5))
    for label, subset, color in [("safe_or_not_false_095", safe, "#2c7fb8"), ("false_095", false, "#c0392b")]:
        spectra = []
        for val in subset["singular_values"].dropna():
            nums = [float(x) for x in str(val).split(";") if x]
            if nums:
                spectra.append(nums)
        if spectra:
            width = max(len(x) for x in spectra)
            arr = np.full((len(spectra), width), np.nan)
            for i, nums in enumerate(spectra):
                arr[i, : len(nums)] = nums
            plt.plot(np.arange(1, width + 1), np.nanmean(arr, axis=0), marker="o", color=color, label=label)
    plt.xlabel("Singular value index")
    plt.ylabel("Mean singular value")
    plt.grid(alpha=0.25)
    plt.legend()
    plt.tight_layout()
    plt.savefig(FIGURES / "singular_value_spectrum_safe_vs_false.png", dpi=180)
    plt.close()


def write_log_audit(df, missing_runs):
    incidence = EXP / "incidence_logs" / "line_a_incidence_log.csv"
    incidence_cols = []
    incidence_rows = 0
    if incidence.exists():
        with incidence.open(newline="", encoding="utf-8") as f:
            reader = csv.reader(f)
            incidence_cols = next(reader)
            incidence_rows = sum(1 for _ in reader)
    incidence_nonempty = {}
    if incidence.exists():
        inc_df = pd.read_csv(incidence)
        for col in ["round_id", "query_path", "source_bin", "source_id", "oracle_label", "self_reported_completion"]:
            if col in inc_df.columns:
                nonempty = inc_df[col].fillna("").astype(str).str.len().gt(0).sum()
                incidence_nonempty[col] = int(nonempty)

    run_files = list(EXP.rglob("runs/*.json"))
    score_files = list(EXP.rglob("score_summary.json"))
    fields = {
        "task_id": "score_summary.json; incidence log",
        "repo_id": "inferred from path/task_id; not a stable explicit field in score summaries",
        "run_id": "score_summary.json and run JSON",
        "agent_id": "parseable from run_id; incidence log has explicit agent_id",
        "round_id": "incidence column exists but is empty in line_a; online run JSON has no rounds",
        "item_id": "run JSON items as file_path:line; incidence log item_id",
        "oracle_label": "incidence log and score summaries after scoring only",
        "source_path": "run JSON items.file_path; incidence source_id",
        "source_family": "incidence source_bin; otherwise derived from source_path prefix and marked proxy",
        "search_route": "query_path column exists but is empty in line_a; not present in online run JSON; v2 offline features have search_strategy/path-overlap aggregates only",
        "query_text": "not present in online run JSON",
        "tool_name": "not present in online run JSON",
        "action_type": "not present in online run JSON",
        "timestamp": "not present in online run JSON",
        "self_reported_completion": "run JSON and incidence log",
        "self_reported_confidence": "run JSON and score summaries",
        "stop_reason": "schema only for run_log; not present in online run JSON inspected",
        "holdout_or_scout_id": "audit_policy_eval paths/runs imply policy; no uniform field",
        "scout_discovered_items": "seed_summary holdout_new_true_items for some runs; verifier run JSON item lists exist",
        "cost_or_token_count": "separate cost JSON files; not joined in this pilot",
        "latency": "schema/v2 aggregates only; not present in online run JSON",
    }
    lines = [
        "# Geometry Log Audit",
        "",
        "This audit checks what can be computed from existing logs without inventing fields.",
        "",
        "## Sources Inspected",
        "",
        f"- `score_summary.json` files: {len(score_files)}",
        f"- agent run JSON files under `runs/`: {len(run_files)}",
        f"- incidence log: `{incidence.relative_to(ROOT)}` with {incidence_rows} rows" if incidence.exists() else "- incidence log: missing",
        f"- states with usable G3 run item logs in this pilot: {len(df)}",
        f"- missing run files referenced by score summaries: {len(missing_runs)}",
        "",
        "## Field Availability",
        "",
        "| field | availability |",
        "|---|---|",
    ]
    for field, status in fields.items():
        lines.append(f"| `{field}` | {status} |")
    lines.extend(
        [
            "",
            "## Existing Incidence Columns",
            "",
            "`" + "`, `".join(incidence_cols) + "`" if incidence_cols else "No incidence columns found.",
            "",
            "## Non-empty Incidence Field Counts",
            "",
            "| field | non-empty rows |",
            "|---|---:|",
        ]
    )
    for field, count in incidence_nonempty.items():
        lines.append(f"| `{field}` | {count} |")
    lines.extend(
        [
            "",
            "## Directly Computable Metrics",
            "",
            "- Agent x source-family discovered-item count matrix from run JSON `items.file_path`.",
            "- Agent x item incidence matrix from run JSON `items.file_path:line`.",
            "- Pairwise item Jaccard, pairwise source Jaccard, singleton ratio.",
            "- Source/file coverage counts, source concentration entropy/HHI/Gini.",
            "- Coverage-matrix cosine similarity, singular values, entropy effective rank, logdet volume, marginal logdet gain.",
            "- Offline labels: union recall/precision and false-completion labels at theta 0.90, 0.95, and 1.00 from score summaries.",
            "",
            "## Approximate Metrics Only",
            "",
            "- `source_family` when absent is approximated by the first two path segments after `repo/`.",
            "- `source_route` is approximated only by source-path/source-family coverage; this is not an action trajectory.",
            "- `scout_gain_vs_residual_projection.png` uses main-agent source cosine as a route-similarity proxy; no true projection onto action trajectories is available.",
            "",
            "## Not Computable From Current Logs",
            "",
            "- Visit-count and action-count matrices by source-route stratum.",
            "- Query/action/tool sequence embeddings.",
            "- Principal angles over non-degenerate per-agent trajectory subspaces.",
            "- Timestamped no-new-item rounds for online runs.",
            "- Robust residual-direction scout projection metrics.",
            "",
            "## Minimal Re-run Fields Needed",
            "",
            "- Append one JSONL event per tool/action with `task_id`, `repo_id`, `run_id`, `agent_id`, `round_id`, `query_text`, `tool_name`, `action_type`, `source_path`, `timestamp`, and `new_items`.",
            "- Keep the current item ledger fields, including `oracle_label`, only for offline scoring after blind runs complete.",
            "- Log scout policy id and route/action events so residual-direction scout comparisons are not path-name proxies.",
        ]
    )
    (DOCS / "geometry_log_audit.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_report(df, auc_df):
    by_repo = df.groupby("repository").agg(
        states=("state_id", "count"),
        false_095=("false_completion_theta_095", "sum"),
        mean_recall=("union_recall", "mean"),
        mean_erank=("source_normalized_effective_rank", "mean"),
        mean_logdet_gain=("source_marginal_logdet_gain", "mean"),
        mean_source_hhi=("source_concentration_hhi", "mean"),
    )
    label_counts = []
    for theta, col in [
        ("0.90", "false_completion_theta_090"),
        ("0.95", "false_completion_theta_095"),
        ("1.00", "false_completion_theta_100"),
    ]:
        positives = int(df[col].sum())
        label_counts.append(
            {
                "theta": theta,
                "false_completion": positives,
                "not_false_completion": int(len(df) - positives),
            }
        )
    label_counts_df = pd.DataFrame(label_counts)
    best = auc_df.sort_values("auroc_abs_direction", ascending=False, na_position="last").head(6)
    has_label_variation = df["false_completion_theta_095"].nunique() > 1
    lines = [
        "# Coverage Geometry Diagnostic Report",
        "",
        "Status: mechanism diagnostic pilot only. This report does not introduce a new method or stopping certificate.",
        "",
        "## Data Used",
        "",
        f"- Usable states: {len(df)}",
        f"- Repositories: {', '.join(sorted(df['repository'].dropna().unique()))}",
        "- Runtime-observable features here are source/item ledger features; oracle recall is used only for offline labels.",
        "- False completion is defined as all inspected G3 agents self-reporting completion while union recall is below theta; confidence is not part of the label.",
        "- Action trajectory embeddings were not built because the inspected online logs do not contain query/action/tool sequences.",
        "",
        "## Repository Summary",
        "",
        by_repo.to_markdown(),
        "",
        "## False-Completion Label Counts",
        "",
        label_counts_df.to_markdown(index=False),
        "",
        "## Metric Association With False Completion at theta = 0.95",
        "",
        best.to_markdown(index=False),
        "",
        "Interpretation note: AUROC is reported with direction flipped to the better of metric or negative metric, so it is descriptive and optimistic for screening. It is not a trained classifier result.",
        "",
        "At theta = 0.95, the inspected historical states contain no safe-completion negative class. Metric screening is therefore undefined for this data slice; the table is retained only to show that the current logs are not sufficient for a discriminative geometry test.",
        "",
        "## RQ Answers",
        "",
        "### RQ1",
        "",
        "The existing logs support a source-path coverage version of the question, not full action-trajectory geometry. All inspected states are false completions even at theta = 0.90, so this pilot cannot compare false completions against safe completions. It can only describe the coverage geometry of failure states.",
        "",
        "### RQ2",
        "",
        "Not answered from the current data. Because the label has no negative class, effective rank, logdet volume, marginal volume gain, overlap, source coverage, no-new-item rounds, and confidence cannot be compared as predictors of false completion. A new diagnostic run must include both intentionally stopped states and safe or near-safe states.",
        "",
        "### RQ3",
        "",
        "Not answered. Current scout/holdout logs expose discovered items and some true-positive gains, but they do not expose enough route vectors to compute low-projection residual-direction scout metrics.",
        "",
        "### RQ4",
        "",
        "Partially assessable across Requests, Click, and itsdangerous score summaries. Stability remains unresolved because the feature representation is path-prefix based and not a true action trajectory.",
        "",
        "## Go / No-Go",
        "",
        "No-Go for making geometry the main line now.",
        "",
        "Reasons:",
        "",
        "- Current logs are sufficient for source/item coverage diagnostics but insufficient for action-trajectory geometry.",
        "- The cleaned false-completion definition marks every inspected state as false completion at theta 0.90, 0.95, and 1.00, leaving no safe-completion comparison group.",
        "- Residual-direction scout claims cannot be tested without query/action/tool route logs.",
        "- Any metric separation here is descriptive and not yet shown to dominate simple source coverage or singleton/evidence-ledger baselines under leave-one-repo validation.",
        "",
        "Recommended fallback for the paper line: simple source coverage + evidence ledger + lightweight audit controller.",
        "",
        "Minimum next re-run: for one seed each on Requests and Click, log per-round query/action/tool/source events for G3 plus one scout policy, and include at least one deliberately extended high-recall/audited run to create a safe or near-safe comparison state. Then repeat this script with true visit/action matrices.",
    ]
    (DOCS / "coverage_geometry_diagnostic_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    ensure_dirs()
    df, matrix_df, missing_runs = collect_states()
    df.to_csv(RESULTS / "run_level_summary.csv", index=False)
    matrix_df.to_csv(RESULTS / "coverage_geometry_metrics.csv", index=False)
    auc_df = auc_table(df)
    auc_df.to_csv(RESULTS / "metric_screening_summary.csv", index=False)
    repo_auc_df = per_repository_auc_table(df)
    repo_auc_df.to_csv(RESULTS / "metric_screening_by_repository.csv", index=False)
    if not df.empty:
        save_plots(df)
    write_log_audit(df, missing_runs)
    write_report(df, auc_df)
    (RESULTS / "missing_referenced_runs.json").write_text(json.dumps(missing_runs, indent=2), encoding="utf-8")
    print(f"Wrote {len(df)} state summaries to {RESULTS / 'run_level_summary.csv'}")
    print(f"Wrote {len(matrix_df)} matrix rows to {RESULTS / 'coverage_geometry_metrics.csv'}")


if __name__ == "__main__":
    main()
