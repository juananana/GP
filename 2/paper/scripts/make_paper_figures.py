from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib import patches
from matplotlib.colors import LinearSegmentedColormap


ROOT = Path(__file__).resolve().parents[2]
PAPER = ROOT / "paper"
PILOT = ROOT / "analysis" / "research_object_geometry" / "real_agent_pilot"
SUPPLEMENT = PILOT / "credibility_supplement"
RESULTS = SUPPLEMENT / "results"
FIGURES = PAPER / "figures"

SAFE_SUPPORT_MIN = 0.75
SAFE_RECALL_MIN = 0.90
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
    fig, ax = plt.subplots(figsize=(7.05, 3.70))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    ax.text(0.015, 0.975, "Evidence-condition geometry and controller", fontsize=10, weight="bold", ha="left", va="top")

    panels = [
        (0.035, "Localized exposure", COLORS["red"], COLORS["red_light"], np.array([[0.95, 0, 0, 0], [0, 0.85, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0.80]]), "Not eligible\nrepair or abstain"),
        (0.360, "Broad but productive", COLORS["orange"], COLORS["orange_light"], np.array([[0.10, 0.45, 0.20, 0.10], [0.18, 0.55, 0.15, 0.22], [0.25, 0.22, 0.08, 0.12], [0.15, 0.26, 0.20, 0.18]]), "Eligible, but residual\nevidence appears"),
        (0.685, "Broad and stable", COLORS["green"], COLORS["green_light"], np.array([[0.38, 0.40, 0.44, 0.42], [0.39, 0.43, 0.36, 0.41], [0.44, 0.40, 0.39, 0.37], [0.41, 0.38, 0.42, 0.45]]), "Eligible and\nno residual evidence"),
    ]

    for i, (x, title, color, light, mat, outcome) in enumerate(panels):
        ax.add_patch(patches.FancyBboxPatch((x, 0.535), 0.28, 0.375, boxstyle="round,pad=0.008,rounding_size=0.025", fc="#FFFFFF", ec=color, lw=0.9))
        ax.text(x + 0.014, 0.878, f"({chr(97+i)}) {title}", color=color, fontsize=7.6, weight="bold", ha="left")
        mini_heatmap(ax, x + 0.066, 0.660, 0.134, 0.138, mat)
        if i == 1:
            ax.add_patch(patches.Rectangle((x + 0.123, 0.716), 0.066, 0.048, facecolor="none", edgecolor=COLORS["orange"], linewidth=0.9, linestyle=(0, (2, 1))))
            ax.text(x + 0.238, 0.730, "weak gaps\nremain", fontsize=5.7, color=COLORS["muted"], ha="center", va="center")
        rounded_box(ax, (x + 0.043, 0.568), 0.195, 0.052, outcome, light, color, fontsize=6.7, weight="bold", radius=0.018)

    ax.text(0.035, 0.430, "Controller", fontsize=7.6, weight="bold", ha="left")
    y0 = 0.335
    rounded_box(ax, (0.060, y0), 0.100, 0.060, "Stop\nclaim", "#FFFFFF", COLORS["blue"], fontsize=6.9, radius=0.018)
    arrow(ax, (0.160, y0 + 0.030), (0.225, y0 + 0.030), COLORS["muted"])
    rounded_box(ax, (0.225, y0), 0.165, 0.060, "Condition\ncheck", COLORS["blue_light"], COLORS["blue"], fontsize=7.0, weight="bold", radius=0.018)
    arrow(ax, (0.390, y0 + 0.030), (0.455, y0 + 0.030), COLORS["muted"])
    rounded_box(ax, (0.455, y0), 0.150, 0.060, "Repair /\naudit", COLORS["orange_light"], COLORS["orange"], fontsize=7.0, weight="bold", radius=0.018)
    arrow(ax, (0.605, y0 + 0.030), (0.675, y0 + 0.030), COLORS["muted"])
    rounded_box(ax, (0.675, y0), 0.245, 0.060, "SAFE / CONTINUE / ABSTAIN", COLORS["green_light"], COLORS["green"], fontsize=7.0, weight="bold", radius=0.018)
    arrow(ax, (0.530, y0), (0.307, y0), COLORS["orange"], lw=0.85, style="->")
    ax.text(0.418, 0.288, "residual evidence sends the workflow back to audit", fontsize=6.2, color=COLORS["orange"], ha="center")

    rounded_box(ax, (0.085, 0.148), 0.210, 0.058, r"$p_t(s)=v_t(s)/\sum_{s'}v_t(s')$", "#FFFFFF", COLORS["gray"], fontsize=7.0, radius=0.018)
    rounded_box(ax, (0.365, 0.148), 0.255, 0.058, r"eligible: support $\geq \tau_s$, Gini $\leq \tau_g$", "#FFFFFF", COLORS["gray"], fontsize=7.0, radius=0.018)
    rounded_box(ax, (0.685, 0.148), 0.230, 0.058, r"repair: under-exposure $\times$ potential", "#FFFFFF", COLORS["gray"], fontsize=6.9, radius=0.018)
    ax.text(0.50, 0.060, "Broad exposure gives completion eligibility, not completion proof.", fontsize=7.6, weight="bold", color=COLORS["ink"], ha="center")
    save(fig, "evidence_condition_controller")


def _condition_frame_for_overview() -> pd.DataFrame:
    files = [
        ("policy", PILOT / "blind_tasks" / "policy_docset_v1" / "results" / "condition_metrics.csv"),
        ("code", PILOT / "blind_tasks" / "code_repo_v1" / "results" / "condition_metrics.csv"),
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
    tasks = ["policy", "code", "requests", "urllib3"]
    labels = ["policy", "code", "requests", "urllib3"]
    x = np.arange(len(tasks))
    base = overview[overview["condition"] == "homogeneous"].set_index("task").reindex(tasks)
    broad = overview[overview["condition"] == "route_partitioned"].set_index("task").reindex(tasks)
    extended = overview[overview["condition"] == "extended_audit"].set_index("task")
    ablation["short_task"] = ablation["task"].map({"policy_docset_v1": "policy", "code_repo_v1": "code", "requests": "requests", "urllib3": "urllib3"})
    ablation = ablation.set_index("short_task").reindex(tasks)

    fig, axes = plt.subplots(1, 3, figsize=(7.10, 2.34), constrained_layout=True)
    width = 0.32
    axes[0].bar(x - width / 2, base["support"], width, label="homogeneous", color=COLORS["gray"])
    axes[0].bar(x + width / 2, broad["support"], width, label="route-partitioned", color=COLORS["blue"])
    axes[0].axhline(SAFE_SUPPORT_MIN, color=COLORS["red"], linestyle=(0, (4, 2)), linewidth=0.9)
    axes[0].text(3.45, SAFE_SUPPORT_MIN + 0.025, r"$\tau_s=0.75$", color=COLORS["red"], fontsize=7, ha="right")
    axes[0].set_title("(a) Support eligibility", loc="left", fontweight="bold")
    axes[0].set_ylim(0, 1.05)
    axes[0].set_xticks(x, labels, rotation=22, ha="right")
    axes[0].set_ylabel("source-route support")
    axes[0].legend(frameon=False, loc="upper left", handlelength=1.2)

    axes[1].bar(x - width / 2, ablation["source_only_support"], width, label="source-only", color=COLORS["green"])
    axes[1].bar(x + width / 2, ablation["source_route_support"], width, label="source-route", color=COLORS["purple"])
    axes[1].axhline(SAFE_SUPPORT_MIN, color=COLORS["red"], linestyle=(0, (4, 2)), linewidth=0.9)
    axes[1].set_title("(b) Route granularity matters", loc="left", fontweight="bold")
    axes[1].set_ylim(0, 1.05)
    axes[1].set_xticks(x, labels, rotation=22, ha="right")
    axes[1].legend(frameon=False, loc="lower left", handlelength=1.2)

    vals = [
        float(broad.loc["urllib3", "recall"]),
        float(extended.loc["urllib3", "recall"]) if "urllib3" in extended.index else np.nan,
    ]
    axes[2].bar([0, 1], vals, 0.50, color=[COLORS["orange"], COLORS["green"]])
    axes[2].axhline(SAFE_RECALL_MIN, color=COLORS["red"], linestyle=(0, (4, 2)), linewidth=0.9)
    axes[2].text(0, vals[0] + 0.025, f"{vals[0]:.3f}", ha="center", va="bottom", fontsize=7.2, color=COLORS["ink"])
    axes[2].text(1, vals[1] - 0.035, f"{vals[1]:.3f}", ha="center", va="top", fontsize=7.2, color=COLORS["ink"])
    axes[2].text(0.55, SAFE_RECALL_MIN + 0.025, "0.90 evaluation threshold", color=COLORS["red"], fontsize=6.8, ha="center")
    axes[2].set_title("(c) urllib3 boundary", loc="left", fontweight="bold")
    axes[2].set_ylim(0, 1.05)
    axes[2].set_xticks([0, 1], ["route-\npartitioned", "extended\naudit"])
    axes[2].set_ylabel("bounded-oracle recall")

    for ax in axes:
        ax.grid(axis="y", alpha=0.9)
        ax.set_axisbelow(True)
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
    labels = ["policy", "code", "requests", "urllib3"]
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


def main() -> None:
    plot_main_results_overview()
    plot_controller_decision_matrix()
    plot_repair_sensitivity_summary()
    print(f"Wrote paper figures to {FIGURES}")


if __name__ == "__main__":
    main()
