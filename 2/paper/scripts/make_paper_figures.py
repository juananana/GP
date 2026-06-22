from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib import patches
from matplotlib.colors import LinearSegmentedColormap

import sys


ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT / "analysis" / "research_object_geometry" / "real_agent_pilot"))
from experiment_config import load_experiment_config, thresholds  # noqa: E402

PAPER = ROOT / "paper"
PILOT = ROOT / "analysis" / "research_object_geometry" / "real_agent_pilot"
SUPPLEMENT = PILOT / "credibility_supplement"
RESULTS = SUPPLEMENT / "results"
FIGURES = PAPER / "figures"

CONFIG = load_experiment_config()
THRESHOLDS = thresholds(CONFIG)
SAFE_SUPPORT_MIN = THRESHOLDS["tau_support"]
SAFE_RECALL_MIN = THRESHOLDS["eval_recall"]
FIG_DPI = 360

COLORS = {
    "ink": "#111827",
    "muted": "#4B5563",
    "grid": "#E5E7EB",
    "blue": "#2563EB",
    "blue_light": "#DBEAFE",
    "green": "#059669",
    "green_light": "#D1FAE5",
    "orange": "#D97706",
    "orange_light": "#FEF3C7",
    "red": "#DC2626",
    "red_light": "#FEE2E2",
    "gray": "#9CA3AF",
    "gray_light": "#F3F4F6",
    "purple": "#7C3AED",
    "teal": "#0F766E",
}


def set_style() -> None:
    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "font.size": 8,
            "axes.titlesize": 8.5,
            "axes.labelsize": 8,
            "xtick.labelsize": 7.5,
            "ytick.labelsize": 7.5,
            "legend.fontsize": 7,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.edgecolor": "#374151",
            "axes.linewidth": 0.7,
            "grid.color": COLORS["grid"],
            "grid.linewidth": 0.55,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
        }
    )


def save(fig: plt.Figure, stem: str) -> None:
    FIGURES.mkdir(parents=True, exist_ok=True)
    fig.savefig(FIGURES / f"{stem}.pdf", bbox_inches="tight")
    fig.savefig(FIGURES / f"{stem}.png", dpi=FIG_DPI, bbox_inches="tight")
    plt.close(fig)


def rounded_box(ax, xy, w, h, label, fc, ec, *, fontsize=7.8, weight="normal", radius=0.035):
    box = patches.FancyBboxPatch(
        xy,
        w,
        h,
        boxstyle=f"round,pad=0.010,rounding_size={radius}",
        linewidth=0.9,
        edgecolor=ec,
        facecolor=fc,
    )
    ax.add_patch(box)
    ax.text(
        xy[0] + w / 2,
        xy[1] + h / 2,
        label,
        ha="center",
        va="center",
        fontsize=fontsize,
        color=COLORS["ink"],
        weight=weight,
        linespacing=1.15,
    )
    return box


def arrow(ax, start, end, color=None, lw=1.0, style="-|>"):
    ax.annotate(
        "",
        xy=end,
        xytext=start,
        arrowprops=dict(arrowstyle=style, color=color or COLORS["muted"], lw=lw, shrinkA=2, shrinkB=2),
    )


def mini_heatmap(ax, x0, y0, w, h, mat, *, route_labels=True, cmap=None, border="#9CA3AF"):
    rows, cols = mat.shape
    cmap = cmap or LinearSegmentedColormap.from_list("exposure", ["#F8FAFC", "#BFDBFE", "#2563EB"])
    cell_w = w / cols
    cell_h = h / rows
    for r in range(rows):
        for c in range(cols):
            ax.add_patch(
                patches.Rectangle(
                    (x0 + c * cell_w, y0 + (rows - 1 - r) * cell_h),
                    cell_w,
                    cell_h,
                    facecolor=cmap(mat[r, c]),
                    edgecolor="white",
                    linewidth=0.55,
                )
            )
    ax.add_patch(patches.Rectangle((x0, y0), w, h, facecolor="none", edgecolor=border, linewidth=0.65))
    for r in range(rows):
        ax.text(x0 - 0.010, y0 + (rows - r - 0.5) * cell_h, f"S{r+1}", ha="right", va="center", fontsize=5.6, color=COLORS["muted"])
    if route_labels:
        for c in range(cols):
            ax.text(x0 + (c + 0.5) * cell_w, y0 + h + 0.012, f"R{c+1}", ha="center", va="bottom", fontsize=5.6, color=COLORS["muted"])


def plot_certificate_mismatch() -> None:
    set_style()
    fig, ax = plt.subplots(figsize=(3.35, 3.20))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    ax.text(0.02, 0.965, "Certificate mismatch", fontsize=9.2, weight="bold", ha="left", va="top")
    ax.text(0.02, 0.925, "Local no-new evidence is not a global completion certificate", fontsize=7.2, color=COLORS["muted"], ha="left", va="top")

    rounded_box(ax, (0.045, 0.765), 0.245, 0.095, "Observed\ncondition", COLORS["blue_light"], COLORS["blue"], weight="bold", fontsize=7.7)
    rounded_box(ax, (0.385, 0.765), 0.225, 0.095, "Local\nstop signal", COLORS["gray_light"], COLORS["gray"], weight="bold", fontsize=7.7)
    rounded_box(ax, (0.710, 0.765), 0.225, 0.095, "Global\nclaim", COLORS["red_light"], COLORS["red"], weight="bold", fontsize=7.7)
    arrow(ax, (0.290, 0.812), (0.385, 0.812), COLORS["muted"])
    arrow(ax, (0.610, 0.812), (0.710, 0.812), COLORS["muted"])

    mini_heatmap(
        ax,
        0.090,
        0.515,
        0.215,
        0.160,
        np.array(
            [
                [0.95, 0.00, 0.00, 0.00],
                [0.00, 0.88, 0.00, 0.00],
                [0.00, 0.00, 0.00, 0.00],
                [0.00, 0.00, 0.00, 0.82],
            ]
        ),
    )
    ax.text(0.198, 0.485, "evidence gathered in subset U", fontsize=6.4, color=COLORS["muted"], ha="center")

    for y, label in [(0.615, "no-new"), (0.540, "agreement"), (0.465, "confidence")]:
        rounded_box(ax, (0.405, y - 0.026), 0.185, 0.052, label, "#FFFFFF", COLORS["blue"], fontsize=6.8, radius=0.017)
        arrow(ax, (0.590, y), (0.690, 0.535), COLORS["muted"], lw=0.85)

    rounded_box(ax, (0.700, 0.475), 0.220, 0.120, "False\ncertification", COLORS["red_light"], COLORS["red"], fontsize=8.7, weight="bold")
    ax.text(
        0.810,
        0.425,
        r"$U \subset \Omega_{SR}$, so local evidence" + "\n" + "does not certify the full scope.",
        ha="center",
        va="top",
        fontsize=6.7,
        color=COLORS["muted"],
        linespacing=1.15,
    )
    ax.plot([0.06, 0.94], [0.300, 0.300], color=COLORS["grid"], lw=0.8)
    rounded_box(ax, (0.140, 0.205), 0.230, 0.075, "Evidence\ncondition", COLORS["orange_light"], COLORS["orange"], fontsize=7.0, weight="bold", radius=0.018)
    arrow(ax, (0.370, 0.242), (0.465, 0.242), COLORS["muted"])
    rounded_box(ax, (0.465, 0.205), 0.165, 0.075, "repair or\ncontinue", "#FFFFFF", COLORS["blue"], fontsize=7.0, radius=0.018)
    arrow(ax, (0.630, 0.242), (0.725, 0.242), COLORS["muted"])
    rounded_box(ax, (0.725, 0.205), 0.160, 0.075, "accept if\nmatched", COLORS["green_light"], COLORS["green"], fontsize=7.0, radius=0.018)
    ax.text(0.50, 0.112, "The missing check is whether evidence scope matches certificate scope.", fontsize=6.5, color=COLORS["muted"], ha="center")
    save(fig, "certificate_mismatch")


def plot_evidence_condition_controller() -> None:
    set_style()
    fig, ax = plt.subplots(figsize=(7.10, 2.10))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    xs = [0.035, 0.280, 0.525, 0.770]
    w = 0.190
    h = 0.700
    titles = [
        "Source-route\nexposure estimation",
        "Eligibility\ngate",
        "Residual-evidence\nrepair",
        "SAFE / CONTINUE /\nABSTAIN rule",
    ]
    heads = [COLORS["blue"], COLORS["teal"], COLORS["orange"], COLORS["green"]]
    fills = [COLORS["blue_light"], "#CCFBF1", COLORS["orange_light"], COLORS["green_light"]]
    bodies = [
        [r"Input: $E_t$, $S \times R$", r"Compute $v_t(s)$ and $p_t(s)$", "Output: support, Gini"],
        [r"Input: support, Gini", rf"support $\geq {SAFE_SUPPORT_MIN:.2f}$", rf"Gini $\leq {THRESHOLDS['tau_gini']:.2f}$"],
        ["Input: weak plausible gaps", "Priority = under-exposure", r"$\times$ runtime potential"],
        ["SAFE: eligible + clean", "CONTINUE: residual found", "ABSTAIN: no certificate"],
    ]

    for i, x in enumerate(xs):
        ax.add_patch(
            patches.FancyBboxPatch(
                (x, 0.205),
                w,
                h,
                boxstyle="round,pad=0.010,rounding_size=0.020",
                facecolor="#FFFFFF",
                edgecolor=heads[i],
                linewidth=0.9,
            )
        )
        ax.add_patch(
            patches.FancyBboxPatch(
                (x + 0.010, 0.780),
                w - 0.020,
                0.082,
                boxstyle="round,pad=0.006,rounding_size=0.016",
                facecolor=fills[i],
                edgecolor=heads[i],
                linewidth=0.7,
            )
        )
        ax.text(x + 0.023, 0.823, str(i + 1), fontsize=7.3, weight="bold", color=heads[i], ha="center", va="center")
        ax.text(x + 0.108, 0.823, titles[i], fontsize=5.9, weight="bold", color=COLORS["ink"], ha="center", va="center", linespacing=0.98)

        if i == 0:
            mini_heatmap(
                ax,
                x + 0.042,
                0.485,
                0.105,
                0.130,
                np.array([[0.9, 0.0, 0.2], [0.0, 0.7, 0.0], [0.1, 0.0, 0.85]]),
                route_labels=False,
            )
            ax.text(x + 0.095, 0.640, r"$\Omega_{SR}$", fontsize=5.8, color=COLORS["muted"], ha="center")
        elif i == 1:
            rounded_box(ax, (x + 0.025, 0.555), w - 0.050, 0.052, r"support $\geq \tau_s$", "#FFFFFF", heads[i], fontsize=5.9, radius=0.015)
            rounded_box(ax, (x + 0.025, 0.485), w - 0.050, 0.052, r"Gini $\leq \tau_g$", "#FFFFFF", heads[i], fontsize=5.9, radius=0.015)
            ax.text(x + w / 2, 0.425, "eligibility is not proof", fontsize=5.6, color=COLORS["muted"], ha="center")
        elif i == 2:
            mini_heatmap(
                ax,
                x + 0.050,
                0.505,
                0.092,
                0.105,
                np.array([[0.7, 0.2, 0.0], [0.1, 0.6, 0.2], [0.0, 0.1, 0.7]]),
                route_labels=False,
                cmap=LinearSegmentedColormap.from_list("repair", ["#FFF7ED", "#FDBA74", "#EA580C"]),
            )
            ax.add_patch(patches.Rectangle((x + 0.111, 0.542), 0.031, 0.035, fc="none", ec=COLORS["red"], lw=0.8, linestyle=(0, (2, 1))))
            ax.text(x + w / 2, 0.435, "probe residual evidence", fontsize=5.6, color=COLORS["muted"], ha="center")
        else:
            rounded_box(ax, (x + 0.025, 0.590), w - 0.050, 0.046, "SAFE", "#ECFDF5", COLORS["green"], fontsize=6.0, weight="bold", radius=0.014)
            rounded_box(ax, (x + 0.025, 0.525), w - 0.050, 0.046, "CONTINUE", "#FFF7ED", COLORS["orange"], fontsize=6.0, weight="bold", radius=0.014)
            rounded_box(ax, (x + 0.025, 0.460), w - 0.050, 0.046, "ABSTAIN", "#FEF2F2", COLORS["red"], fontsize=6.0, weight="bold", radius=0.014)

        if i < 3:
            arrow(ax, (x + w + 0.010, 0.545), (xs[i + 1] - 0.013, 0.545), COLORS["muted"], lw=0.9)

    arrow(ax, (xs[2] + w / 2, 0.165), (xs[1] + w / 2, 0.165), COLORS["orange"], lw=0.85, style="->")
    ax.text(0.520, 0.095, "residual evidence keeps the workflow in audit", fontsize=5.8, color=COLORS["orange"], ha="center")
    save(fig, "evidence_condition_controller")


def _condition_frame_for_overview() -> pd.DataFrame:
    files = [
        ("policy-docset", PILOT / "blind_tasks" / "policy_docset_v1" / "results" / "condition_metrics.csv"),
        ("code-repo", PILOT / "blind_tasks" / "code_repo_v1" / "results" / "condition_metrics.csv"),
        ("requests", PILOT / "external_validation_requests" / "results" / "external_requests_condition_metrics.csv"),
        ("urllib3", PILOT / "external_validation_v2" / "results" / "condition_summary.csv"),
    ]
    rows = []
    for task, path in files:
        df = pd.read_csv(path)
        for condition in ["homogeneous", "route_partitioned", "extended_audit"]:
            sub = df[df["condition"] == condition]
            if sub.empty:
                continue
            row = sub.iloc[0]
            rows.append(
                {
                    "task": task,
                    "condition": condition,
                    "support": float(row.get("source_route_coverage_ratio", row.get("support_ratio"))),
                    "recall": float(row["recall"]),
                    "gini": float(row["exposure_gini"]),
                }
            )
    return pd.DataFrame(rows)


def plot_main_results_overview() -> None:
    set_style()
    overview = _condition_frame_for_overview()
    ablation = pd.read_csv(RESULTS / "source_only_vs_source_route.csv")
    tasks = ["policy-docset", "code-repo", "requests", "urllib3"]
    labels = ["policy-docset", "code-repo", "requests", "urllib3"]
    ablation["short_task"] = ablation["task"].map({"policy_docset_v1": "policy-docset", "code_repo_v1": "code-repo", "requests": "requests", "urllib3": "urllib3"})
    ablation = ablation.set_index("short_task").reindex(tasks)

    fig, axes = plt.subplots(1, 2, figsize=(7.15, 2.65), constrained_layout=True)
    axes = axes.ravel()
    task_colors = {"policy-docset": COLORS["blue"], "code-repo": COLORS["teal"], "requests": COLORS["orange"], "urllib3": COLORS["purple"]}
    condition_order = ["homogeneous", "route_partitioned", "extended_audit"]
    markers = {"homogeneous": "o", "route_partitioned": "s", "extended_audit": "^"}
    condition_labels = {"homogeneous": "localized stop", "route_partitioned": "route-partitioned", "extended_audit": "extended audit"}
    x = np.arange(len(tasks))

    width = 0.30
    axes[0].bar(
        x - width / 2,
        ablation["source_only_support"],
        width,
        label="source-only support",
        color=COLORS["green"],
        alpha=0.88,
        edgecolor="white",
        linewidth=0.7,
    )
    axes[0].bar(
        x + width / 2,
        ablation["source_route_support"],
        width,
        label="source-route support",
        color=COLORS["purple"],
        alpha=0.88,
        edgecolor="white",
        linewidth=0.7,
    )
    axes[0].scatter(x, ablation["base_recall"], s=34, color=COLORS["red"], marker="D", zorder=4, label="post-hoc recall")
    for i, task in enumerate(tasks):
        source_only = float(ablation.loc[task, "source_only_support"])
        source_route = float(ablation.loc[task, "source_route_support"])
        axes[0].text(i - width / 2, source_only + 0.022, f"{source_only:.2f}", ha="center", va="bottom", fontsize=6.0, color=COLORS["muted"])
        axes[0].text(i + width / 2, source_route + 0.022, f"{source_route:.2f}", ha="center", va="bottom", fontsize=6.0, color=COLORS["muted"])
    axes[0].axhline(SAFE_SUPPORT_MIN, color=COLORS["red"], linestyle=(0, (4, 2)), linewidth=0.85)
    axes[0].set_title("(a) Source-only exposure can look complete", loc="left", fontweight="bold")
    axes[0].set_ylim(0, 1.18)
    axes[0].set_xticks(x, labels, rotation=18, ha="right")
    axes[0].set_ylabel("support / recall")
    handles0, labels0 = axes[0].get_legend_handles_labels()

    axes[1].fill_between(
        [SAFE_SUPPORT_MIN, 1.02],
        0,
        THRESHOLDS["tau_gini"],
        color=COLORS["green_light"],
        alpha=0.62,
        zorder=0,
        label="eligible region",
    )
    for task in tasks:
        sub = overview[overview["task"] == task].set_index("condition").reindex(condition_order)
        sub = sub.dropna(subset=["support", "gini"])
        if len(sub) > 1:
            axes[1].plot(
                sub["support"],
                sub["gini"],
                color=task_colors[task],
                lw=0.8,
                alpha=0.38,
                zorder=1,
            )
    for condition in condition_order:
        sub = overview[overview["condition"] == condition]
        for _, row in sub.iterrows():
            axes[1].scatter(
                row["support"],
                row["gini"],
                s=42,
                color=task_colors[row["task"]],
                marker=markers[condition],
                edgecolor="white",
                linewidth=0.75,
                zorder=3,
                alpha=0.95,
            )
            if condition == "homogeneous":
                axes[1].text(
                    row["support"] + 0.014,
                    min(0.985, row["gini"] + 0.018),
                    row["task"].split("-")[0],
                    fontsize=5.8,
                    color=task_colors[row["task"]],
                    ha="left",
                    va="bottom",
                )
    axes[1].axvline(SAFE_SUPPORT_MIN, color=COLORS["red"], linestyle=(0, (4, 2)), linewidth=0.85)
    axes[1].axhline(THRESHOLDS["tau_gini"], color=COLORS["red"], linestyle=(0, (4, 2)), linewidth=0.85)
    axes[1].annotate(
        "more complete\nless concentrated",
        xy=(0.92, 0.40),
        xytext=(0.46, 0.18),
        arrowprops=dict(arrowstyle="->", lw=0.8, color=COLORS["muted"]),
        fontsize=6.3,
        color=COLORS["muted"],
        ha="center",
        va="center",
    )
    axes[1].set_title("(b) Source-route geometry diagnoses the stop", loc="left", fontweight="bold")
    axes[1].set_xlim(0, 1.04)
    axes[1].set_ylim(0, 1.02)
    axes[1].set_xlabel("source-route support")
    axes[1].set_ylabel("exposure Gini")
    marker_handles = [
        plt.Line2D([0], [0], marker=markers[c], color="none", markerfacecolor=COLORS["gray"], markeredgecolor="white", markersize=6, label=condition_labels[c])
        for c in condition_order
    ]
    task_handles = [
        plt.Line2D([0], [0], marker="o", color="none", markerfacecolor=task_colors[t], markeredgecolor="white", markersize=5.5, label=labels[i])
        for i, t in enumerate(tasks)
    ]
    leg1 = axes[1].legend(handles=marker_handles, frameon=False, loc="upper right", handlelength=0.8, fontsize=6.1)
    axes[1].add_artist(leg1)
    axes[1].legend(handles=task_handles, frameon=False, loc="lower left", handlelength=0.8, fontsize=5.9, ncol=2, columnspacing=0.6)

    for ax in axes:
        ax.grid(axis="y", alpha=0.9)
        ax.set_axisbelow(True)
    fig.legend(handles0, labels0, frameon=False, loc="lower center", bbox_to_anchor=(0.29, -0.055), ncol=3, fontsize=6.5, handlelength=1.0, columnspacing=0.9)
    save(fig, "main_results_overview")


def plot_controller_decision_matrix() -> None:
    set_style()
    controller = pd.read_csv(RESULTS / "controller_decision_table.csv")
    rows = controller[
        (controller["task_group"] == "external repos")
        & (controller["evaluation_set"].isin(["seeded repairs", "seeded safe states"]))
    ].copy()
    rows["row_label"] = rows["evaluation_set"].map(
        {"seeded repairs": "unsafe repair states", "seeded safe states": "safe complete states"}
    )
    rows = rows.sort_values("evaluation_set", ascending=False)
    totals = rows["n"].to_numpy(dtype=float)
    safe = rows["safe"].to_numpy(dtype=float) / totals
    cont = rows["continue"].to_numpy(dtype=float) / totals
    abstain = rows["abstain"].to_numpy(dtype=float) / totals

    fig, ax = plt.subplots(figsize=(3.35, 2.05), constrained_layout=True)
    y = np.arange(len(rows))
    ax.barh(y, safe, color=COLORS["green"], label="SAFE", height=0.42)
    ax.barh(y, cont, left=safe, color=COLORS["orange"], label="CONTINUE", height=0.42)
    ax.barh(y, abstain, left=safe + cont, color=COLORS["gray"], label="ABSTAIN", height=0.42)
    for i, row in enumerate(rows.itertuples()):
        safe_pct = 100.0 * float(row.safe) / float(row.n)
        ax.text(0.03, i, f"{safe_pct:.0f}% SAFE", va="center", ha="left", fontsize=9.5, weight="bold", color="black")
        note = "oracle-safe states" if not np.isnan(float(row.safe_coverage)) else "oracle-unsafe states"
        ax.text(0.97, i + 0.19, note, va="center", ha="right", fontsize=6.8, color=COLORS["ink"])
    ax.set_yticks(y, list(rows["row_label"]))
    ax.set_xlim(0, 1)
    ax.set_xlabel("decision fraction")
    ax.legend(ncol=3, frameon=False, loc="lower center", bbox_to_anchor=(0.5, 1.02), handlelength=1.2)
    ax.grid(axis="x", alpha=0.9)
    ax.set_axisbelow(True)
    save(fig, "controller_decision_matrix")


def plot_repair_sensitivity_summary() -> None:
    set_style()
    repair_ci = pd.read_csv(RESULTS / "repair_policy_ci.csv")
    tasks = ["policy_docset_v1", "code_repo_v1", "requests", "urllib3"]
    labels = ["policy-docset", "code-repo", "requests", "urllib3"]
    fig, ax = plt.subplots(figsize=(3.35, 2.30), constrained_layout=True)
    x = np.arange(len(tasks))
    width = 0.24
    colors = {"residual_potential": COLORS["purple"], "high_potential": COLORS["blue"], "random": COLORS["gray"]}
    for offset, challenger in [(-width, "residual_potential"), (0, "high_potential"), (width, "random")]:
        sub = repair_ci[repair_ci["challenger"] == challenger].set_index("task").reindex(tasks)
        means = sub["mean_new_true_items"].to_numpy(dtype=float)
        lows = means - sub["new_true_ci95_low"].to_numpy(dtype=float)
        highs = sub["new_true_ci95_high"].to_numpy(dtype=float) - means
        ax.bar(x + offset, means, width, color=colors[challenger], label=challenger.replace("_", "-"))
        ax.errorbar(x + offset, means, yerr=[lows, highs], fmt="none", ecolor="#374151", elinewidth=0.75, capsize=2)
        if challenger == "residual_potential":
            for xi, mean in zip(x + offset, means):
                if mean >= 20:
                    ax.text(xi, mean + 8, f"{mean:.0f}", ha="center", va="bottom", fontsize=7)
    ax.set_title("Repair gain after a fixed stop state", loc="left", fontweight="bold")
    ax.set_xticks(x, labels, rotation=22, ha="right")
    ax.set_ylabel("new oracle items")
    ax.legend(frameon=False, loc="upper left", handlelength=1.2)
    ax.grid(axis="y", alpha=0.9)
    ax.set_axisbelow(True)
    save(fig, "repair_sensitivity_summary")


def controller_variant_summary() -> pd.DataFrame:
    detail = pd.read_csv(RESULTS / "controller_decision_detail.csv")
    safe_states = pd.read_csv(RESULTS / "seeded_safe_state_validation.csv")
    unsafe_repairs = detail[detail["condition"].str.startswith("repair:")].copy()

    def decision_counts(label: str, unsafe: pd.DataFrame, safe: pd.DataFrame, unsafe_decision: pd.Series, safe_decision: pd.Series, gain: float, cost: float) -> dict[str, float | int | str]:
        unsafe_n = int(len(unsafe))
        safe_n = int(len(safe))
        safe_on_unsafe = int((unsafe_decision == "SAFE").sum())
        safe_on_safe = int((safe_decision == "SAFE").sum())
        cont = int((unsafe_decision == "CONTINUE").sum())
        abstain = int((unsafe_decision == "ABSTAIN").sum())
        safe_cont = int((safe_decision == "CONTINUE").sum())
        safe_abstain = int((safe_decision == "ABSTAIN").sum())
        return {
            "policy": label,
            "unsafe_denominator": unsafe_n,
            "safe_denominator": safe_n,
            "safe_on_unsafe": safe_on_unsafe,
            "safe_on_safe": safe_on_safe,
            "continue_on_safe": safe_cont,
            "abstain_on_safe": safe_abstain,
            "false_certification_rate_seeded_unsafe": safe_on_unsafe / unsafe_n if unsafe_n else np.nan,
            "safe_coverage_seeded_safe": safe_on_safe / safe_n if safe_n else np.nan,
            "continue_rate_seeded_unsafe": cont / unsafe_n if unsafe_n else np.nan,
            "abstain_rate_seeded_unsafe": abstain / unsafe_n if unsafe_n else np.nan,
            "mean_repair_gain_seeded_unsafe": gain,
            "mean_cost_seeded_unsafe": cost,
        }

    rows = []
    residual_unsafe = unsafe_repairs[unsafe_repairs["condition"] == "repair:residual_potential"].copy()
    residual_safe = safe_states[safe_states["challenger"] == "residual_potential"].copy()
    for name, frame in [("residual unsafe repairs", residual_unsafe), ("residual safe states", residual_safe)]:
        if "runtime_residual_items" not in frame.columns:
            raise KeyError(f"runtime_residual_items is required for verifier-gate comparison in {name}")
    geom_unsafe = (residual_unsafe["support"] >= SAFE_SUPPORT_MIN) & (residual_unsafe["gini"] <= THRESHOLDS["tau_gini"])
    geom_safe = (residual_safe["after_support_ratio"] >= SAFE_SUPPORT_MIN) & (residual_safe["after_exposure_gini"] <= THRESHOLDS["tau_gini"])
    rows.append(decision_counts("Naive stop", residual_unsafe, residual_safe, pd.Series(["SAFE"] * len(residual_unsafe)), pd.Series(["SAFE"] * len(residual_safe)), np.nan, np.nan))
    rows.append(decision_counts("Source-only", residual_unsafe, residual_safe, pd.Series(["SAFE"] * len(residual_unsafe)), pd.Series(["SAFE"] * len(residual_safe)), np.nan, np.nan))
    unsafe_residual_signal = residual_unsafe["runtime_residual_items"].to_numpy(dtype=float) > 0
    safe_residual_signal = residual_safe["runtime_residual_items"].to_numpy(dtype=float) > 0
    verifier_unsafe = pd.Series(np.where(unsafe_residual_signal, "ABSTAIN", "SAFE"))
    verifier_safe = pd.Series(np.where(safe_residual_signal, "ABSTAIN", "SAFE"))
    rows.append(decision_counts("Verifier-gate", residual_unsafe, residual_safe, verifier_unsafe, verifier_safe, np.nan, np.nan))
    rows.append(decision_counts("Eligibility-only", residual_unsafe, residual_safe, pd.Series(np.where(geom_unsafe, "SAFE", "ABSTAIN")), pd.Series(np.where(geom_safe, "SAFE", "ABSTAIN")), np.nan, np.nan))
    rows.append(decision_counts("Full controller", residual_unsafe, residual_safe, residual_unsafe["decision"].reset_index(drop=True), residual_safe["decision"].reset_index(drop=True), float(residual_unsafe["repair_gain"].mean()), float(residual_unsafe["cost"].mean())))

    for label, repair_policy in [
        ("Random repair", "random"),
        ("High-potential repair", "high_potential"),
        ("Ours", "residual_potential"),
    ]:
        repair_rows = unsafe_repairs[unsafe_repairs["condition"] == f"repair:{repair_policy}"].copy()
        safe_rows = safe_states[safe_states["challenger"] == repair_policy].copy()
        rows.append(
            decision_counts(
                label,
                repair_rows,
                safe_rows,
                repair_rows["decision"].reset_index(drop=True),
                safe_rows["decision"].reset_index(drop=True),
                float(repair_rows["repair_gain"].mean()),
                float(repair_rows["cost"].mean()),
            )
        )
    out = pd.DataFrame(rows)
    out.to_csv(RESULTS / "controller_variant_comparison.csv", index=False)
    return out


def write_controller_variant_count_table(summary: pd.DataFrame) -> None:
    def f3(value: float) -> str:
        if pd.isna(value):
            return "--"
        return f"{float(value):.3f}"

    def f1(value: float) -> str:
        if pd.isna(value):
            return "--"
        return f"{float(value):.1f}"

    rows = []
    for _, row in summary.iterrows():
        rows.append(
            " & ".join(
                [
                    str(row["policy"]).replace("_", r"\_"),
                    str(int(row["unsafe_denominator"])),
                    str(int(row["safe_denominator"])),
                    str(int(row["safe_on_unsafe"])),
                    str(int(row["safe_on_safe"])),
                    f3(row["false_certification_rate_seeded_unsafe"]),
                    f3(row["safe_coverage_seeded_safe"]),
                    f3(row["continue_rate_seeded_unsafe"]),
                    f3(row["abstain_rate_seeded_unsafe"]),
                    f1(row["mean_repair_gain_seeded_unsafe"]),
                    f1(row["mean_cost_seeded_unsafe"]),
                ]
            )
            + r" \\"
        )
    text = r"""
\begin{table*}[t]
\centering
\caption{Controller variant count table. Unsafe denominators are seeded
oracle-unsafe repair states; safe denominators are seeded oracle-safe complete
states, so these denominators differ from the one-state eligibility boundary in
the main text. FCR is SAFE-on-unsafe divided by the unsafe denominator; safe
coverage is SAFE-on-safe divided by the safe denominator. Oracle safety labels
are used only for post-hoc scoring. Decision variants are evaluated on the
residual-potential seeded state set; repair target variants use the same seeds
and budgets with their named target rule.}
\label{tab:controller_variant_counts}
\resizebox{\textwidth}{!}{%
\begin{tabular}{lrrrrrrrrrr}
\toprule
Policy & Unsafe denom. & Safe denom. & SAFE-on-unsafe & SAFE-on-safe
& FCR & Safe cov. & CONTINUE & ABSTAIN & Repair gain & Repair cost \\
\midrule
""" + "\n".join(rows) + r"""
\bottomrule
\end{tabular}}
\end{table*}
"""
    (PAPER / "generated" / "table_controller_variant_counts.tex").write_text(text.strip() + "\n", encoding="utf-8")

    main = summary[summary["policy"].isin(["Naive stop", "Source-only", "Verifier-gate", "Eligibility-only", "Full controller"])].copy()
    main["policy"] = pd.Categorical(
        main["policy"],
        categories=["Naive stop", "Source-only", "Verifier-gate", "Eligibility-only", "Full controller"],
        ordered=True,
    )
    main = main.sort_values("policy")
    main_rows = []
    for _, row in main.iterrows():
        unsafe_sca = (
            f"{int(row['safe_on_unsafe'])}/"
            f"{int(round(float(row['continue_rate_seeded_unsafe'] * row['unsafe_denominator'])))}/"
            f"{int(round(float(row['abstain_rate_seeded_unsafe'] * row['unsafe_denominator'])))}"
        )
        complete_sca = (
            f"{int(row['safe_on_safe'])}/"
            f"{int(row['continue_on_safe'])}/"
            f"{int(row['abstain_on_safe'])}"
        )
        main_rows.append(
            " & ".join(
                [
                    str(row["policy"]).replace("Full controller", "Full"),
                    str(int(row["unsafe_denominator"])),
                    str(int(row["safe_denominator"])),
                    unsafe_sca,
                    complete_sca,
                    f3(row["false_certification_rate_seeded_unsafe"]),
                    f3(row["safe_coverage_seeded_safe"]),
                ]
            )
            + r" \\"
        )
    main_text = r"""
\begin{table}[t]
\centering
\small
\setlength{\tabcolsep}{2.8pt}
\caption{Seeded unsafe/complete controller decision counts. Unsafe and Complete
are the seeded
denominators; FCR is SAFE-on-unsafe divided by Unsafe, and safe coverage is
SAFE-on-complete divided by Complete. These denominators differ from the
one-state eligibility boundary in Table~\ref{tab:eligibility_boundary}. Oracle
labels are used only after decisions are fixed. S/C/A reports
SAFE/CONTINUE/ABSTAIN counts.}
\label{tab:main_controller_counts}
\resizebox{\columnwidth}{!}{%
\begin{tabular}{lrrrrrr}
\toprule
Decision rule & Unsafe & Complete & Unsafe S/C/A & Complete S/C/A & FCR & Safe cov. \\
\midrule
""" + "\n".join(main_rows) + r"""
\bottomrule
\end{tabular}}
\end{table}
"""
    (PAPER / "generated" / "table_main_controller_counts.tex").write_text(main_text.strip() + "\n", encoding="utf-8")

    write_per_task_decision_breakdown()
    write_eligibility_boundary_table()
    write_lightweight_baseline_table()


def _fmt_table_float(value: float, digits: int = 3) -> str:
    if pd.isna(value):
        return "--"
    return f"{float(value):.{digits}f}"


def _escape_tex(text: str) -> str:
    return str(text).replace("_", r"\_")


def write_per_task_decision_breakdown() -> None:
    detail = pd.read_csv(RESULTS / "controller_decision_detail.csv")
    observed = detail[detail["condition"].isin(["homogeneous", "route_partitioned", "extended_audit"])].copy()
    observed["oracle_safe"] = observed["recall"] >= SAFE_RECALL_MIN
    observed["geometry_ok"] = (observed["support"] >= SAFE_SUPPORT_MIN) & (observed["gini"] <= THRESHOLDS["tau_gini"])

    policies = [
        ("Naive stop", lambda df: pd.Series(["SAFE"] * len(df), index=df.index)),
        ("Source-only", lambda df: pd.Series(["SAFE"] * len(df), index=df.index)),
        (
            "Verifier-gate",
            lambda df: pd.Series(
                np.where(
                    df.get("residual_warning", pd.Series([False] * len(df), index=df.index)).astype(bool)
                    | df.get("unresolved_warning", pd.Series([False] * len(df), index=df.index)).astype(bool),
                    "ABSTAIN",
                    "SAFE",
                ),
                index=df.index,
            ),
        ),
        ("Eligibility-only", lambda df: pd.Series(np.where(df["geometry_ok"], "SAFE", "ABSTAIN"), index=df.index)),
        ("Full controller", lambda df: df["decision"]),
    ]
    rows = []
    for task in ["policy_docset_v1", "code_repo_v1", "requests", "urllib3"]:
        task_df = observed[observed["task"] == task].copy()
        unsafe = ~task_df["oracle_safe"]
        safe = task_df["oracle_safe"]
        for policy, decide in policies:
            decisions = decide(task_df)
            rows.append(
                {
                    "task": task,
                    "policy": policy,
                    "unsafe_n": int(unsafe.sum()),
                    "safe_n": int(safe.sum()),
                    "safe_on_unsafe": int(((decisions == "SAFE") & unsafe).sum()),
                    "fcr": float(((decisions == "SAFE") & unsafe).sum() / unsafe.sum()) if unsafe.sum() else np.nan,
                    "safe_coverage": float(((decisions == "SAFE") & safe).sum() / safe.sum()) if safe.sum() else np.nan,
                    "continue_rate": float((decisions == "CONTINUE").mean()) if len(decisions) else np.nan,
                    "abstain_rate": float((decisions == "ABSTAIN").mean()) if len(decisions) else np.nan,
                }
            )
    out = pd.DataFrame(rows)
    out.to_csv(RESULTS / "per_task_decision_breakdown.csv", index=False)

    labels = {
        "policy_docset_v1": "policy-docset",
        "code_repo_v1": "code-repo",
        "requests": "requests",
        "urllib3": "urllib3",
    }
    tex_rows = []
    for _, row in out.iterrows():
        tex_rows.append(
            " & ".join(
                [
                    _escape_tex(labels.get(row["task"], row["task"])),
                    _escape_tex(row["policy"]),
                    str(int(row["unsafe_n"])),
                    str(int(row["safe_n"])),
                    str(int(row["safe_on_unsafe"])),
                    _fmt_table_float(row["fcr"]),
                    _fmt_table_float(row["safe_coverage"]),
                    _fmt_table_float(row["continue_rate"]),
                    _fmt_table_float(row["abstain_rate"]),
                ]
            )
            + r" \\"
        )
    text = r"""
\begin{table*}[t]
\centering
\caption{Per-task decision breakdown on observed stop states. FCR is
SAFE-on-unsafe divided by oracle-unsafe stop states for that task; safe coverage
is SAFE-on-safe divided by oracle-safe stop states for that task. Oracle labels
are post-hoc only.}
\label{tab:per_task_decision_breakdown}
\resizebox{\textwidth}{!}{%
\begin{tabular}{llrrrrrrr}
\toprule
Task & Policy & Unsafe & Safe & SAFE-on-unsafe & FCR & Safe cov. & CONTINUE & ABSTAIN \\
\midrule
""" + "\n".join(tex_rows) + r"""
\bottomrule
\end{tabular}}
\end{table*}
"""
    (PAPER / "generated" / "table_per_task_decision_breakdown.tex").write_text(text.strip() + "\n", encoding="utf-8")


def write_eligibility_boundary_table() -> None:
    detail = pd.read_csv(RESULTS / "controller_decision_detail.csv")
    observed = detail[detail["condition"].isin(["homogeneous", "route_partitioned", "extended_audit"])].copy()
    observed["oracle_safe"] = observed["recall"] >= SAFE_RECALL_MIN
    observed["geometry_ok"] = (observed["support"] >= SAFE_SUPPORT_MIN) & (observed["gini"] <= THRESHOLDS["tau_gini"])
    boundary = observed[observed["geometry_ok"] & ~observed["oracle_safe"]].copy()

    oracle_totals = {}
    for task, path in [
        ("policy_docset_v1", PILOT / "blind_tasks" / "policy_docset_v1" / "results" / "condition_metrics.csv"),
        ("code_repo_v1", PILOT / "blind_tasks" / "code_repo_v1" / "results" / "condition_metrics.csv"),
        ("requests", PILOT / "external_validation_requests" / "results" / "external_requests_condition_metrics.csv"),
        ("urllib3", PILOT / "external_validation_v2" / "results" / "condition_summary.csv"),
    ]:
        if path.exists():
            frame = pd.read_csv(path)
            if "oracle_total" in frame:
                oracle_totals[task] = float(frame["oracle_total"].iloc[0])
    tex_rows = []
    csv_rows = []
    for _, row in boundary.iterrows():
        total = oracle_totals.get(row["task"], np.nan)
        missed = int(round((1.0 - float(row["recall"])) * total)) if not pd.isna(total) else np.nan
        eligibility_decision = "SAFE"
        full_decision = str(row["decision"])
        csv_rows.append(
            {
                "task": row["task"],
                "condition": row["condition"],
                "support": row["support"],
                "gini": row["gini"],
                "recall": row["recall"],
                "runtime_gap_positive": bool(row.get("weak_plausible_gap", 0) > 0 or row["decision"] == "CONTINUE"),
                "posthoc_missed_items": missed,
                "eligibility_only_decision": eligibility_decision,
                "full_controller_decision": full_decision,
            }
        )
        tex_rows.append(
            " & ".join(
                [
                    _escape_tex(row["task"].replace("policy_docset_v1", "policy-docset").replace("code_repo_v1", "code-repo")),
                    _escape_tex(row["condition"]),
                    _fmt_table_float(row["support"]),
                    _fmt_table_float(row["gini"]),
                    _fmt_table_float(row["recall"]),
                    "yes" if missed >= 0 else "--",
                    eligibility_decision,
                    full_decision,
                ]
            )
            + r" \\"
        )
    pd.DataFrame(csv_rows).to_csv(RESULTS / "eligibility_passed_unsafe_boundary.csv", index=False)
    text = r"""
\begin{table}[t]
\centering
\small
\setlength{\tabcolsep}{3.2pt}
\caption{Boundary case showing why eligibility is not proof. The state passes
the source-route eligibility gate, but post-hoc recall remains below the
completion threshold; runtime weak-gap control therefore returns CONTINUE
rather than SAFE.}
\label{tab:eligibility_boundary}
\resizebox{\columnwidth}{!}{%
\begin{tabular}{llrrrrll}
\toprule
Task & State & Support & Gini & Recall & Gap+ & Elig.-only & Full \\
\midrule
""" + "\n".join(tex_rows) + r"""
\bottomrule
\end{tabular}}
\end{table}
"""
    (PAPER / "generated" / "table_eligibility_boundary.tex").write_text(text.strip() + "\n", encoding="utf-8")


def write_lightweight_baseline_table() -> None:
    repair = pd.read_csv(RESULTS / "repair_policy_ci.csv")
    chao = pd.read_csv(RESULTS / "chao_singleton_proxy.csv")
    source = pd.read_csv(RESULTS / "source_only_vs_source_route.csv")

    rows = []
    for task in ["requests", "urllib3"]:
        source_row = source[source["task"] == task].iloc[0]
        rows.append(
            {
                "task": task,
                "baseline": "Source-only stop",
                "measurement": "FCR if accepted",
                "value": float(source_row["false_certification_if_source_only_safe"]),
                "cost": np.nan,
                "note": "accepts localized route evidence",
            }
        )
        for challenger in ["random", "high_potential", "residual_potential"]:
            row = repair[(repair["task"] == task) & (repair["challenger"] == challenger)].iloc[0]
            rows.append(
                {
                    "task": task,
                    "baseline": challenger.replace("_", "-") + " expansion",
                    "measurement": "mean repair gain",
                    "value": float(row["mean_new_true_items"]),
                    "cost": np.nan,
                    "note": "same budget, post-stop repair",
                }
            )
    for _, row in chao[chao["task"].isin(["requests", "urllib3"])].iterrows():
        rows.append(
            {
                "task": row["task"],
                "baseline": "Singleton/Chao scalar stop",
                "measurement": "would stop?",
                "value": float(row["scalar_stop_proxy"]),
                "cost": np.nan,
                "note": f"Chao1={float(row['chao1_estimate']):.1f}",
            }
        )
    out = pd.DataFrame(rows)
    out.to_csv(RESULTS / "lightweight_external_baselines.csv", index=False)

    tex_rows = []
    for _, row in out.iterrows():
        if row["measurement"] == "FCR if accepted":
            value = "1.000" if row["value"] else "0.000"
        elif row["measurement"] == "would stop?":
            value = "yes" if row["value"] else "no"
        else:
            value = _fmt_table_float(row["value"], 1)
        tex_rows.append(
            " & ".join(
                [
                    _escape_tex(row["task"]),
                    _escape_tex(row["baseline"]),
                    _escape_tex(row["measurement"]),
                    value,
                    _escape_tex(row["note"]),
                ]
            )
            + r" \\"
        )
    text = r"""
\begin{table*}[t]
\centering
\caption{Lightweight external baselines and sanity checks. These are not new
task suites: source-only is a direct stopping baseline, random/high-potential
are repair-target baselines under the same budget, and the scalar singleton/Chao
proxy is a negative control that ignores source-route geometry.}
\label{tab:lightweight_baselines}
\resizebox{\textwidth}{!}{%
\begin{tabular}{lllll}
\toprule
Task & Baseline & Measurement & Value & Note \\
\midrule
""" + "\n".join(tex_rows) + r"""
\bottomrule
\end{tabular}}
\end{table*}
"""
    (PAPER / "generated" / "table_lightweight_baselines.tex").write_text(text.strip() + "\n", encoding="utf-8")


def plot_controller_variant_comparison() -> None:
    set_style()
    summary = controller_variant_summary()
    write_controller_variant_count_table(summary)

    budget = pd.read_csv(RESULTS / "budget_sensitivity.csv")
    budget = budget[budget["challenger"].isin(["random", "high_potential", "residual_potential"])].copy()
    label_map = {"random": "Random", "high_potential": "High-potential", "residual_potential": "Residual-potential"}
    color_map = {"random": COLORS["gray"], "high_potential": COLORS["blue"], "residual_potential": COLORS["purple"]}

    fig, ax = plt.subplots(figsize=(7.15, 2.85), constrained_layout=True)

    for challenger in ["random", "high_potential", "residual_potential"]:
        task_sub = budget[budget["challenger"] == challenger].sort_values(["task", "budget"])
        for _, sub in task_sub.groupby("task"):
            ax.plot(
                sub["mean_cost"],
                sub["mean_repair_gain"],
                color=color_map[challenger],
                lw=0.7,
                alpha=0.20,
                zorder=1,
            )

    mean_budget = (
        budget.groupby(["challenger", "budget"], as_index=False)[["mean_cost", "mean_repair_gain", "continue_rate"]]
        .mean()
        .sort_values(["challenger", "budget"])
    )
    for challenger in ["random", "high_potential", "residual_potential"]:
        sub = mean_budget[mean_budget["challenger"] == challenger]
        ax.plot(
            sub["mean_cost"],
            sub["mean_repair_gain"],
            marker="o",
            markersize=4.0,
            lw=1.55,
            color=color_map[challenger],
            label=label_map[challenger],
            zorder=3,
        )
        for budget_id in [1, 4, 8]:
            point = sub[sub["budget"] == budget_id]
            if point.empty:
                continue
            row = point.iloc[0]
            ax.text(
                float(row["mean_cost"]),
                float(row["mean_repair_gain"]) + (8 if challenger != "random" else -11),
                str(budget_id),
                fontsize=6.0,
                color=color_map[challenger],
                ha="center",
                va="center",
                zorder=4,
            )

    main_points = summary[summary["policy"].isin(["Random repair", "High-potential repair", "Ours"])].copy()
    main_style = {
        "Random repair": ("random", "Random main"),
        "High-potential repair": ("high_potential", "High-pot. main"),
        "Ours": ("residual_potential", "Residual-pot. main"),
    }
    for row in main_points.itertuples():
        challenger, _ = main_style[row.policy]
        ax.scatter(
            float(row.mean_cost_seeded_unsafe),
            float(row.mean_repair_gain_seeded_unsafe),
            marker="*",
            s=92,
            color=color_map[challenger],
            edgecolor="white",
            linewidth=0.8,
            zorder=5,
        )

    ax.annotate(
        "higher audit budget",
        xy=(7850, 338),
        xytext=(5450, 318),
        arrowprops=dict(arrowstyle="->", lw=0.8, color=COLORS["muted"]),
        fontsize=6.7,
        color=COLORS["muted"],
        ha="center",
    )
    ax.text(0.015, 0.94, "numbers mark budgets 1, 4, 8; stars are the configured main-budget points", transform=ax.transAxes, fontsize=6.4, color=COLORS["muted"], va="top")
    ax.set_title("Repair frontier: residual evidence found versus audit cost", loc="left", fontweight="bold")
    ax.set_xlabel("mean post-stop repair cost")
    ax.set_ylabel("mean residual oracle items found")
    ax.set_xlim(350, 8850)
    ax.set_ylim(0, 365)
    ax.grid(alpha=0.9)
    ax.set_axisbelow(True)
    ax.legend(frameon=False, loc="lower right", ncol=3, handlelength=1.3, columnspacing=1.0)
    save(fig, "controller_variant_comparison")


def main() -> None:
    plot_evidence_condition_controller()
    plot_main_results_overview()
    plot_controller_decision_matrix()
    plot_repair_sensitivity_summary()
    plot_controller_variant_comparison()
    print(f"Wrote paper figures to {FIGURES}")


if __name__ == "__main__":
    main()
