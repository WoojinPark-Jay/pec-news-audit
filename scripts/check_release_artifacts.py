#!/usr/bin/env python3
"""Sanity-check release-safe artifacts against the manuscript claims."""

from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from pecgap.artifacts import load_json, load_table  # noqa: E402


def pct(x: float) -> str:
    return f"{100 * x:.2f}%"


def main() -> None:
    analysis = load_json("analysis_summary.json")
    rq1_figure = load_json("rq1_figure_aggregate.json")
    popularity = load_table("popularity_baseline_check.csv")
    surface_lift = load_table("optimization_surface_lift.csv")
    topk_robustness = load_table("robustness_topk_click_thresholds.csv")
    model = load_table("deep_tuned_model_cv_results.csv")
    importance = load_table("rq4_feature_importance.csv")
    label_proximity = load_table("preference_weighted_label_proximity_sensitivity.csv")
    rq4_candidate_tables = {
        "weighted same-window": load_table("preference_weighted_model_cv.csv"),
        "weighted stress tests": load_table("preference_weighted_stress_cv.csv"),
        "unweighted feature families": load_table("rq4_advanced_model_cv_results.csv"),
    }

    print("PEC release artifact check")
    print("=" * 32)
    print(f"RQ1 users: {analysis.get('rq1_users')}")
    if rq1_figure.get("n_users") != analysis.get("rq1_users"):
        raise ValueError("RQ1 figure aggregate uses a different user denominator")
    if rq1_figure.get("jaccard_users") != 698:
        raise ValueError("RQ1 figure aggregate does not preserve the Jaccard denominator")
    if rq1_figure.get("jaccard_nonempty_sensitivity_users") != 679:
        raise ValueError("RQ1 figure aggregate does not preserve the non-empty sensitivity cohort")
    print(
        "RQ1 figure aggregate: "
        f"{rq1_figure.get('n_users')} users, "
        f"{rq1_figure.get('jaccard_users')} primary Jaccard values, "
        f"{rq1_figure.get('jaccard_nonempty_sensitivity_users')} non-empty sensitivity users"
    )
    print(f"Top category in stated preference: {analysis.get('rq1_top_category_in_stated_pct')}%")
    print(f"Same-day recommendation hit: {analysis.get('rq2_same_day_hit_pct')}%")
    for min_clicks, expected_n, expected_jaccard in [(5, 302, 0.3004415011), (10, 175, 0.3103889444)]:
        row = topk_robustness.loc[
            (topk_robustness["min_clicks"] == min_clicks)
            & (topk_robustness["top_k"] == 3)
        ]
        if len(row) != 1:
            raise ValueError(f"Missing top-3 Jaccard robustness row for click >= {min_clicks}")
        if int(row.iloc[0]["n_users"]) != expected_n:
            raise ValueError(f"Unexpected robustness denominator for click >= {min_clicks}")
        if abs(float(row.iloc[0]["mean_jaccard"]) - expected_jaccard) > 1e-9:
            raise ValueError(f"Unexpected robustness Jaccard for click >= {min_clicks}")
        print(
            f"Top-3 Jaccard, click >= {min_clicks}: "
            f"{float(row.iloc[0]['mean_jaccard']):.4f} (n={expected_n})"
        )
    rec_entropy = analysis.get("rq3_mean_rec_category_entropy")
    click_entropy = analysis.get("rq3_mean_click_category_entropy")
    if rec_entropy is not None and click_entropy is not None:
        print(f"Raw category entropy gap: {rec_entropy - click_entropy:.4f}")

    actual = popularity.loc[popularity["baseline"] == "actual_recommendation"].copy()
    candidate_pool = popularity.loc[
        popularity["baseline"].str.contains("random", case=False, na=False)
    ].copy()
    if not actual.empty and not candidate_pool.empty:
        k_label = "all" if "all" in set(actual["k"].astype(str)) else str(actual["k"].iloc[-1])
        actual_k = actual.loc[actual["k"].astype(str) == k_label, "hit_rate"].iloc[0]
        candidate_pool_k = candidate_pool.loc[
            candidate_pool["k"].astype(str) == k_label, "hit_rate"
        ].iloc[0]
        label = "Full-list" if k_label == "all" else f"Top-{k_label}"
        print(f"{label} actual recommendation hit: {pct(actual_k)}")
        print(f"{label} date-matched candidate-pool hit: {pct(candidate_pool_k)}")

    best_surface = surface_lift.sort_values("lift", ascending=False).iloc[0]
    best_model = model.sort_values("auc_mean", ascending=False).iloc[0]
    top_feature = importance.sort_values("importance", ascending=False).iloc[0]
    print(f"Highest surface lift: {best_surface['surface']} ({best_surface['lift']:.2f}x)")
    print(f"Best unweighted diagnostic model: {best_model['model']} AUC={best_model['auc_mean']:.3f}")
    print(f"Top feature-importance row: {top_feature.to_dict()}")
    expected_sensitivity = {
        "primary_full": (698, 0.8593025533),
        "exclude_empty_stated_category_sets": (679, 0.8526836158),
        "exclude_profile_support_counts": (698, 0.8621984649),
    }
    for setting, (expected_n, expected_auc) in expected_sensitivity.items():
        row = label_proximity.loc[label_proximity["setting"] == setting]
        if len(row) != 1:
            raise ValueError(f"Missing RQ4 label-proximity sensitivity: {setting}")
        if int(row.iloc[0]["n_users"]) != expected_n:
            raise ValueError(f"Unexpected RQ4 sensitivity denominator: {setting}")
        if abs(float(row.iloc[0]["auc_mean"]) - expected_auc) > 1e-9:
            raise ValueError(f"Unexpected RQ4 sensitivity AUC: {setting}")
        print(f"RQ4 sensitivity {setting}: AUC={expected_auc:.3f} (n={expected_n})")

    expected_models = {"Logistic", "RandomForest", "ExtraTrees", "GradientBoosting"}
    for label, table in rq4_candidate_tables.items():
        observed_models = set(table["model"].dropna().astype(str))
        missing = expected_models - observed_models
        if missing:
            raise ValueError(f"{label} table is missing model families: {sorted(missing)}")
        print(f"RQ4 {label}: all four prespecified model families present")
    print("\nOK: release-safe aggregate artifacts are readable.")


if __name__ == "__main__":
    main()
