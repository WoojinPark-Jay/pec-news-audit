#!/usr/bin/env python3
"""Regenerate release-safe diagnostic figures from aggregate tables."""

from __future__ import annotations

from pathlib import Path
import sys
import json

ROOT = Path(__file__).resolve().parents[1]
PKG = ROOT / ".python_packages"


def local_package_cache_is_compatible(path: Path) -> bool:
    """Avoid importing binary wheels built for a different Python version."""

    if not path.exists():
        return False
    binary_modules = list(path.rglob("*.so"))
    if not binary_modules:
        return True
    version_tag = f"cpython-{sys.version_info.major}{sys.version_info.minor}"
    return any(version_tag in module.name for module in binary_modules)


if local_package_cache_is_compatible(PKG):
    sys.path.insert(0, str(PKG))
sys.path.insert(0, str(ROOT / "src"))

import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402

from pecgap.artifacts import figure_path, load_table  # noqa: E402


BLUE = "#2563eb"
TEAL = "#0f766e"
ORANGE = "#f97316"
PINK = "#e11d48"
GRAY = "#475569"
INK = "#111827"
MUTED = "#64748b"
GRID = "#e2e8f0"
LEGACY_NEWSROOM_SURFACE = "publisher" + "/newsroom"

plt.rcParams.update(
    {
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
        "font.family": "DejaVu Sans",
    }
)


def make_popularity_baseline() -> Path:
    df = load_table("popularity_baseline_check.csv")
    k_label = "all" if "all" in set(df["k"].astype(str)) else str(df["k"].iloc[-1])
    sample = df.loc[df["k"].astype(str) == k_label].copy()
    sample["label"] = sample["baseline"].replace(
        {
            "actual_recommendation": "Logged recommendation",
            "same_day_global_recommendation_popularity_leave_user_out": "Same-day recommendation popularity",
            "prior_1d_click_popularity": "Prior-day click popularity",
            "prior_3d_click_popularity": "Prior-3d click popularity",
            "prior_7d_click_popularity": "Prior-week click popularity",
        }
    )
    sample = sample.sort_values("hit_rate")

    fig, ax = plt.subplots(figsize=(7.0, 3.6), dpi=180)
    colors = [BLUE if b == "actual_recommendation" else TEAL for b in sample["baseline"]]
    bars = ax.barh(sample["label"], sample["hit_pct"], color=colors, alpha=0.92)
    axis_label = "Full-list hit rate (%)" if k_label == "all" else f"Top-{k_label} hit rate (%)"
    ax.set_xlabel(axis_label)
    ax.set_title("Logged recommendations exceed simple popularity baselines")
    ax.grid(axis="x", color="#e2e8f0", linewidth=0.8)
    for bar, value in zip(bars, sample["hit_pct"]):
        ax.text(value + 0.15, bar.get_y() + bar.get_height() / 2, f"{value:.2f}%", va="center", fontsize=8)
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.tick_params(axis="y", length=0)
    out = figure_path("release_popularity_baseline.png")
    fig.tight_layout()
    fig.savefig(out, bbox_inches="tight")
    plt.close(fig)
    return out


def make_surface_lift() -> Path:
    df = load_table("optimization_surface_lift.csv").sort_values("lift")
    df["surface_label"] = df["surface"].replace({LEGACY_NEWSROOM_SURFACE: "newsroom"})
    fig, ax = plt.subplots(figsize=(7.0, 3.4), dpi=180)
    ax.hlines(df["surface_label"], 1.0, df["lift"], color="#cbd5e1", linewidth=4)
    ax.scatter(df["lift"], df["surface_label"], s=90, color=ORANGE, edgecolor="white", linewidth=1.2, zorder=3)
    ax.axvline(1.0, color=GRAY, linestyle="--", linewidth=1)
    ax.set_xlabel("Lift over date-matched random baseline")
    ax.set_title("Traceability lift differs across app surfaces")
    for _, row in df.iterrows():
        ax.text(row["lift"] + 0.02, row["surface_label"], f"{row['lift']:.2f}x", va="center", fontsize=8)
    ax.grid(axis="x", color="#e2e8f0", linewidth=0.8)
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.tick_params(axis="y", length=0)
    out = figure_path("release_surface_lift.png")
    fig.tight_layout()
    fig.savefig(out, bbox_inches="tight")
    plt.close(fig)
    return out


def save_png_and_pdf(fig: plt.Figure, name: str) -> Path:
    """Save a figure as both high-resolution PNG and vector PDF."""

    out_png = figure_path(name)
    out_pdf = out_png.with_suffix(".pdf")
    fig.savefig(out_png, bbox_inches="tight", facecolor="white")
    fig.savefig(out_pdf, bbox_inches="tight", facecolor="white")
    return out_pdf


def make_surface_traceability_paper_figure() -> Path:
    """Regenerate Figure 2 in the v46 two-panel bar-chart style."""

    surface_summary = json.loads((ROOT / "reports" / "tables" / "deep_analysis_summary.json").read_text(encoding="utf-8"))
    df_top = pd.DataFrame(surface_summary["surface_pathways"]).copy()
    df_top["surface_label"] = df_top["surface"].replace(
        {
            LEGACY_NEWSROOM_SURFACE: "newsroom",
            "article-detail": "article detail",
            "other/unknown": "other",
        }
    )
    order = ["headline", "category", "home/feed", "newsroom", "article detail"]
    df_top["surface_label"] = pd.Categorical(df_top["surface_label"], categories=order, ordered=True)
    df_top = df_top.sort_values("surface_label").dropna(subset=["surface_label"]).copy()

    df = load_table("optimization_surface_lift.csv").copy()
    df["surface_label"] = df["surface"].replace(
        {
            LEGACY_NEWSROOM_SURFACE: "newsroom",
            "article-detail": "article detail",
            "other/unknown": "other",
        }
    )
    df = df.loc[df["comparable_clicks"] >= 50].copy()
    df["surface_label"] = pd.Categorical(df["surface_label"], categories=order, ordered=True)
    df = df.sort_values("surface_label").dropna(subset=["surface_label"]).copy()

    fig = plt.figure(figsize=(5.05, 5.95), dpi=260)
    gs = fig.add_gridspec(2, 1, height_ratios=[1.0, 1.10], hspace=0.82)
    ax_top = fig.add_subplot(gs[0, 0])
    ax_bottom = fig.add_subplot(gs[1, 0])

    fig.suptitle("Multi-surface click traceability", fontsize=14.0, fontweight="bold", color=INK, y=0.985)

    # Panel A: where comparable clicks enter.
    y_pos = list(range(len(df_top)))
    surface_colors = {
        "headline": "#f00446",
        "category": "#7c3aed",
        "home/feed": "#ef7d00",
        "newsroom": "#0f8275",
        "article detail": "#1f4592",
    }
    ax_top.barh(
        y_pos,
        df_top["click_share_pct"],
        color=[surface_colors.get(str(label), TEAL) for label in df_top["surface_label"]],
        height=0.62,
        alpha=0.98,
    )
    for yi, value in zip(y_pos, df_top["click_share_pct"]):
        ax_top.text(value + 0.45, yi, f"{value:.1f}%", va="center", fontsize=8.4, fontweight="bold", color=INK)
    ax_top.set_title("A. Clicks enter through multiple surfaces", fontsize=10.2, fontweight="bold", color=INK, pad=5)
    ax_top.set_yticks(y_pos, [str(x).title() if str(x) != "home/feed" else "Home/feed" for x in df_top["surface_label"]])
    ax_top.invert_yaxis()
    ax_top.set_xlabel("Share of matched clicks (%)", fontsize=8.0, color=INK, labelpad=6)
    ax_top.set_xlim(0, 76)
    ax_top.grid(axis="x", color=GRID, linewidth=0.7)
    ax_top.spines[["top", "right", "left"]].set_visible(False)
    ax_top.spines["bottom"].set_color("#cbd5e1")
    ax_top.tick_params(axis="y", length=0, labelsize=8.0, colors=MUTED)
    ax_top.tick_params(axis="x", labelsize=8.0, colors=MUTED)

    # Panel B: observed vs random traceability by surface.
    df2 = df.copy()
    ypos = list(range(len(df2)))
    random_pct = df2["random_hit_rate_mean"] * 100
    actual_pct = df2["actual_hit_rate"] * 100
    bar_h = 0.31
    ax_bottom.barh([y - bar_h / 1.25 for y in ypos], random_pct, height=bar_h, color="#cbd5e1")
    ax_bottom.barh([y + bar_h / 1.25 for y in ypos], actual_pct, height=bar_h, color="#0b6ff3")
    for yi, value, lift in zip(ypos, actual_pct, df2["lift"]):
        ax_bottom.text(value + 0.70, yi + bar_h / 1.25, f"{lift:.2f}x", va="center", fontsize=8.6, color=INK)
    ax_bottom.set_title("B. Logged exposure carries surface-dependent signal", fontsize=10.2, fontweight="bold", color=INK, pad=23)
    ax_bottom.scatter([0.43], [1.06], transform=ax_bottom.transAxes, marker="s", s=18, color="#cbd5e1", clip_on=False)
    ax_bottom.text(0.46, 1.06, "Date-matched random", transform=ax_bottom.transAxes, va="center", fontsize=6.7, color=INK)
    ax_bottom.scatter([0.76], [1.06], transform=ax_bottom.transAxes, marker="s", s=18, color="#0b6ff3", clip_on=False)
    ax_bottom.text(0.79, 1.06, "Observed same-day hit", transform=ax_bottom.transAxes, va="center", fontsize=6.7, color=INK)
    ax_bottom.set_yticks(ypos, [str(x).title() if str(x) != "home/feed" else "Home/feed" for x in df2["surface_label"]])
    ax_bottom.invert_yaxis()
    ax_bottom.set_xlabel("Hit rate among comparable clicks (%)", fontsize=8.0, color=INK, labelpad=6)
    ax_bottom.set_xlim(0, 25)
    ax_bottom.grid(axis="x", color=GRID, linewidth=0.7)
    ax_bottom.spines[["top", "right", "left"]].set_visible(False)
    ax_bottom.spines["bottom"].set_color("#cbd5e1")
    ax_bottom.tick_params(axis="y", length=0, labelsize=8.0, colors=MUTED)
    ax_bottom.tick_params(axis="x", labelsize=8.0, colors=MUTED)

    fig.tight_layout(rect=(0, 0, 1, 0.965))
    out = save_png_and_pdf(fig, "fig15_surface_traceability_liftplot_v37.png")
    plt.close(fig)
    return out


def make_bounded_audit_signal_paper_figure() -> Path:
    """Regenerate Figure 4 in the compact v46 AUC-bar style."""

    import json

    opt = load_table("optimization_model_grid.csv")
    base = load_table("rq4_advanced_model_cv_results.csv")
    weighted = load_table("preference_weighted_model_cv.csv")
    stress = load_table("preference_weighted_stress_cv.csv")
    optimization = json.loads((ROOT / "reports" / "tables" / "optimization_checks_summary.json").read_text(encoding="utf-8"))

    def first_auc(df: pd.DataFrame) -> tuple[float, float]:
        row = df.sort_values("auc_mean", ascending=False).iloc[0]
        return float(row["auc_mean"]), float(row.get("auc_std", 0.0))

    extreme = first_auc(
        opt[
            (opt["model"] == "random_forest")
            & (opt["cohort"] == "all_profile_click_users")
            & (opt["label"] == "extreme_quartile")
            & (opt["feature_set"] == "full_plus_surface")
        ]
    )
    unweighted = first_auc(base[(base["model"] == "RandomForest") & (base["feature_set"] == "full")])
    weighted_full = first_auc(weighted[(weighted["model"] == "RandomForest") & (weighted["feature_set"] == "full_plus_weighted_static")])
    weighted_only = first_auc(weighted[weighted["feature_set"] == "static_weighted_prefs"])
    top_mismatch = first_auc(stress[stress["task"] == "top_category_mismatch"])
    click5 = first_auc(stress[stress["task"] == "median_divergence_click_ge_5"])
    click10 = first_auc(stress[stress["task"] == "median_divergence_click_ge_10"])
    temporal_rows = pd.DataFrame(optimization["temporal_extreme"]["rows"])
    temporal = first_auc(temporal_rows[temporal_rows["label"] == "median"])

    rows = [
        ("Extreme mismatch\n/ upper-bound", extreme[0], "#ef7d00"),
        ("Full model +\nweighted profile", weighted_full[0], "#0b6ff3"),
        ("Full model without\nweighted profile", unweighted[0], "#1f4592"),
        ("Top-category\nmismatch", top_mismatch[0], "#1f4592"),
        ("Time-split\nvalidation", temporal[0], "#0f8275"),
        ("Users with\n>=10 clicks", click10[0], "#f00446"),
        ("Users with\n>=5 clicks", click5[0], "#f00446"),
        ("Weighted\nprofile only", weighted_only[0], "#7c3aed"),
    ]

    fig, ax = plt.subplots(figsize=(4.85, 5.10), dpi=260)
    y = list(range(len(rows)))[::-1]
    labels = [r[0] for r in rows]
    values = [r[1] for r in rows]
    colors = [r[2] for r in rows]

    ax.barh(y, [v - 0.48 for v in values], left=0.48, color=colors, height=0.58, alpha=0.98)
    for yi, v in zip(y, values):
        ax.text(v + 0.004, yi, f"{v:.3f}", va="center", ha="left", fontsize=7.4, color=INK)

    ax.axvline(0.5, color="#94a3b8", linestyle="--", linewidth=0.9)
    ax.set_yticks(y, labels)
    ax.set_xlim(0.48, 0.92)
    ax.set_xlabel("AUC", fontsize=8.0, color=INK, labelpad=6)
    ax.set_title("Bounded audit signal", fontsize=14.0, color=INK, pad=9)
    ax.grid(axis="x", color=GRID, linewidth=0.7)
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.spines["bottom"].set_color("#cbd5e1")
    ax.tick_params(axis="y", length=0, labelsize=6.4, colors=MUTED)
    ax.tick_params(axis="x", labelsize=7.5, colors=MUTED)

    fig.tight_layout()
    out = save_png_and_pdf(fig, "fig17_bounded_audit_signal_native_plotly_v21.png")
    plt.close(fig)
    return out


def _metric(summary: dict, key: str) -> float:
    value = summary[key]
    return float(value)


def make_diversity_transfer_audit() -> Path:
    """Create a publication-friendly Figure 3 from release-safe aggregates.

    The figure is intentionally explanatory rather than decorative. Panel A
    separates diversity metrics from concentration, Panel B shows why the raw
    entropy gap needs count matching, and Panel C shows the residual audit
    signal that remains after comparable observation scales.
    """

    import json

    tables_dir = ROOT / "reports" / "tables"
    summary = json.loads((tables_dir / "analysis_summary.json").read_text(encoding="utf-8"))
    diversity = pd.read_csv(tables_dir / "optimization_diversity_summary.csv")

    div_core = diversity.loc[diversity["cohort"] == "audit_eligible_core"].set_index("metric")
    div_click5 = diversity.loc[diversity["cohort"] == "click_ge_5"].set_index("metric")

    raw_category_gap = _metric(summary, "rq3_mean_rec_category_entropy") - _metric(
        summary, "rq3_mean_click_category_entropy"
    )
    count_click5 = float(div_click5.loc["entropy_gap_count_adjusted", "mean"])
    count_core = float(div_core.loc["entropy_gap_count_adjusted", "mean"])

    fig = plt.figure(figsize=(7.25, 6.55), dpi=300)
    gs = fig.add_gridspec(
        3,
        1,
        height_ratios=[1.08, 0.86, 0.86],
        hspace=0.60,
    )
    ax_a = fig.add_subplot(gs[0, 0])
    ax_b = fig.add_subplot(gs[1, 0])
    ax_c = fig.add_subplot(gs[2, 0])

    fig.suptitle("Diversity and Concentration Audit", fontsize=12.6, fontweight="bold", color=INK, y=0.988)
    fig.text(
        0.5,
        0.953,
        "Exposure is broad in logged lists, click consumption is more top-heavy, and count-matched checks identify the residual mismatch.",
        ha="center",
        va="center",
        fontsize=7.45,
        color=MUTED,
    )

    # Panel A: raw layer shift. Use arrows instead of grouped bars so the
    # direction of the layer-to-layer change is visually explicit.
    ax_a.set_title(
        "A. Raw layer shift",
        loc="left",
        fontsize=9.5,
        fontweight="bold",
        color=INK,
        pad=9,
    )
    rows = [
        ("Category entropy\nhigher = broader", _metric(summary, "rq3_mean_rec_category_entropy"), _metric(summary, "rq3_mean_click_category_entropy")),
        ("Publisher entropy\nhigher = broader", _metric(summary, "rq3_mean_rec_publisher_entropy"), _metric(summary, "rq3_mean_click_publisher_entropy")),
        ("Top-category share\nhigher = more concentrated", _metric(summary, "rq3_mean_rec_top_category_share"), _metric(summary, "rq3_mean_click_top_category_share")),
    ]
    y_positions = [2.0, 1.0, 0.0]
    for (label, exposure, click), y in zip(rows, y_positions):
        ax_a.hlines(y, 0.30, 0.96, color=GRID, linewidth=0.9, zorder=0)
        ax_a.annotate(
            "",
            xy=(click, y),
            xytext=(exposure, y),
            arrowprops=dict(arrowstyle="->", color=ORANGE if click > exposure else BLUE, linewidth=1.9, alpha=0.86),
            zorder=2,
        )
        ax_a.scatter([exposure], [y], s=74, color=BLUE, edgecolor="white", linewidth=1.0, zorder=4)
        ax_a.scatter([click], [y], s=74, color=ORANGE, edgecolor="white", linewidth=1.0, zorder=4)
        ax_a.text(
            exposure,
            y + 0.17,
            f"{exposure:.2f}",
            color=BLUE,
            fontsize=7.15,
            fontweight="bold",
            ha="center",
            bbox=dict(fc="white", ec="none", pad=0.12),
            zorder=5,
        )
        if click > exposure:
            click_x = min(click + 0.035, 0.985)
            click_y = y - 0.30
            click_ha = "left"
        else:
            click_x = click - 0.012
            click_y = y + 0.18
            click_ha = "right"
        ax_a.text(
            click_x,
            click_y,
            f"{click:.2f}",
            color=ORANGE,
            fontsize=7.15,
            fontweight="bold",
            ha=click_ha,
            bbox=dict(fc="white", ec="none", pad=0.12),
            zorder=5,
        )
    ax_a.scatter([], [], s=54, color=BLUE, label="logged exposure")
    ax_a.scatter([], [], s=54, color=ORANGE, label="click consumption")
    ax_a.legend(frameon=False, ncol=2, loc="upper right", bbox_to_anchor=(0.995, 1.16), fontsize=7.2, handletextpad=0.4)
    ax_a.set_xlim(0.28, 1.0)
    ax_a.set_ylim(-0.55, 2.45)
    ax_a.set_xlabel("Metric value", fontsize=7.0, color=GRAY, labelpad=2)
    ax_a.set_yticks(y_positions, [r[0] for r in rows])
    ax_a.grid(axis="x", color=GRID, linewidth=0.7)
    ax_a.spines[["top", "right", "left"]].set_visible(False)
    ax_a.spines["bottom"].set_color("#cbd5e1")
    ax_a.tick_params(axis="x", labelsize=6.5, colors=GRAY)
    ax_a.tick_params(axis="y", labelsize=6.9, colors=INK, length=0, pad=8)

    # Panel B: shrinking entropy gap.
    ax_b.set_title("B. Count matching isolates the sparse-click component", loc="left", fontsize=9.2, fontweight="bold", color=INK, pad=7)
    b_vals = [raw_category_gap, count_click5, count_core]
    b_labels = ["Raw category entropy gap", "Count-matched users with >=5 clicks", "Audit-core count-matched gap"]
    b_colors = [BLUE, TEAL, "#14b8a6"]
    ypos = [2, 1, 0]
    ax_b.barh(ypos, b_vals, color=b_colors, height=0.46, alpha=0.92)
    for yi, value in zip(ypos, b_vals):
        ax_b.text(value + 0.008, yi, f"{value:.3f}", va="center", fontsize=7.7, fontweight="bold", color=INK)
    shrink = 100 * (1 - count_click5 / raw_category_gap)
    ax_b.text(
        0.225,
        0.52,
        f"{shrink:.0f}% smaller after matching exposure count to click count",
        ha="center",
        va="center",
        fontsize=6.9,
        color=TEAL,
        bbox=dict(boxstyle="round,pad=0.28", fc="#ecfdf5", ec="#99f6e4", lw=0.8),
    )
    ax_b.set_yticks(ypos, b_labels)
    ax_b.set_xlim(0, 0.335)
    ax_b.set_xlabel("Exposure entropy - click entropy", fontsize=7.0, color=GRAY, labelpad=2)
    ax_b.grid(axis="x", color=GRID, linewidth=0.7)
    ax_b.spines[["top", "right", "left"]].set_visible(False)
    ax_b.spines["bottom"].set_color("#cbd5e1")
    ax_b.tick_params(axis="x", labelsize=6.5, colors=GRAY)
    ax_b.tick_params(axis="y", labelsize=6.8, colors=INK, length=0, pad=8)

    # Panel C: residual mismatch.
    ax_c.set_title("C. Residual mismatch remains after count matching", loc="left", fontsize=9.2, fontweight="bold", color=INK, pad=7)
    residuals = [
        ("HHI concentration gap", float(div_core.loc["hhi_concentration_gap_count_adjusted", "mean"]), BLUE),
        ("Top-share gap", float(div_core.loc["top_share_gap_count_adjusted", "mean"]), TEAL),
        ("JS divergence", float(div_core.loc["category_js_divergence", "mean"]), PINK),
    ]
    y = [2, 1, 0]
    for (label, value, color), yi in zip(residuals, y):
        ax_c.barh([yi], [value], color=color, height=0.42, alpha=0.90)
        ax_c.scatter([value], [yi], s=72, color=color, edgecolor="white", linewidth=1.0, zorder=3)
        ax_c.text(value + 0.012, yi, f"{value:.3f}", va="center", fontsize=7.7, fontweight="bold", color=INK)
    ax_c.set_yticks(y, [r[0] for r in residuals])
    ax_c.text(
        0.505,
        2.30,
        "audit-eligible cohort",
        ha="right",
        fontsize=7.0,
        color=MUTED,
    )
    ax_c.text(
        0.345,
        1.34,
        "concentration gaps are smaller,\nbut distributional mismatch remains",
        ha="center",
        va="center",
        fontsize=6.85,
        color=PINK,
        bbox=dict(boxstyle="round,pad=0.28", fc="#fff1f2", ec="#fda4af", lw=0.8),
    )
    ax_c.set_xlabel("Residual gap value", fontsize=7.0, color=GRAY, labelpad=2)
    ax_c.set_xlim(0, 0.53)
    ax_c.grid(axis="x", color=GRID, linewidth=0.7)
    ax_c.spines[["top", "right", "left"]].set_visible(False)
    ax_c.spines["bottom"].set_color("#cbd5e1")
    ax_c.tick_params(axis="y", labelsize=6.9, colors=INK, length=0, pad=8)
    ax_c.tick_params(axis="x", labelsize=6.5, colors=GRAY)

    out = figure_path("fig16_diversity_audit_v46.png")
    fig.savefig(out, bbox_inches="tight", facecolor="white")
    fig.savefig(out.with_suffix(".pdf"), bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return out.with_suffix(".pdf")


def main() -> None:
    outputs = [
        make_popularity_baseline(),
        make_surface_lift(),
        make_surface_traceability_paper_figure(),
        make_diversity_transfer_audit(),
        make_bounded_audit_signal_paper_figure(),
    ]
    print("Generated release figures:")
    for path in outputs:
        print(f"- {path}")


if __name__ == "__main__":
    main()
