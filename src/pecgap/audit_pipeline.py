"""Core Preference-Exposure-Consumption audit pipeline.

This module turns approved processed tables into user-level audit quantities
and aggregate summaries. It is not a recommender-system ranker; it implements
the measurement protocol described in the manuscript.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from collections.abc import Callable
import json
import math
import time

import numpy as np
import pandas as pd

from .metrics import (
    count_matched_metric_gap,
    hhi,
    jaccard,
    js_divergence,
    normalized_entropy,
    top_share,
)
from .preprocessing import (
    load_processed_tables,
    profile_preference_table,
    standardize_clicks,
    standardize_exposures,
)


@dataclass(frozen=True)
class AuditInputs:
    """Normalized inputs for the PEC audit."""

    profiles: pd.DataFrame
    clicks: pd.DataFrame
    exposures: pd.DataFrame


def load_audit_inputs(data_dir: Path) -> AuditInputs:
    """Load and normalize processed private or synthetic tables."""

    tables = load_processed_tables(data_dir)
    return AuditInputs(
        profiles=profile_preference_table(tables["profiles"]),
        clicks=standardize_clicks(tables["clicks"]),
        exposures=standardize_exposures(tables["exposures"]),
    )


def _top_labels(values: list[object], k: int = 3) -> list[str]:
    labels = [str(value).strip() for value in values if str(value).strip()]
    return [label for label, _count in Counter(labels).most_common(k)]


def _empirical_cosine(a_values: list[str], b_values: list[str]) -> float:
    if not a_values or not b_values:
        return float("nan")
    keys = sorted(set(a_values) | set(b_values))
    a_counts = Counter(a_values)
    b_counts = Counter(b_values)
    a = np.array([a_counts.get(key, 0) for key in keys], dtype=float)
    b = np.array([b_counts.get(key, 0) for key in keys], dtype=float)
    if a.sum() == 0 or b.sum() == 0:
        return float("nan")
    a = a / a.sum()
    b = b / b.sum()
    denom = float(np.linalg.norm(a) * np.linalg.norm(b))
    return float(np.dot(a, b) / denom) if denom else float("nan")


def compute_preference_consumption_alignment(
    profiles: pd.DataFrame,
    clicks: pd.DataFrame,
    *,
    top_k: int = 3,
) -> pd.DataFrame:
    """Compute P-C alignment at the user level."""

    click_groups = clicks.groupby("user_id")
    rows = []
    profile_by_user = profiles.set_index("user_id")
    for user_id, group in click_groups:
        if user_id not in profile_by_user.index:
            continue
        profile = profile_by_user.loc[user_id]
        pref_categories = list(profile["pref_categories"])
        pref_publishers = list(profile["pref_publishers"])
        click_categories = group["category"].dropna().astype(str).tolist()
        click_publishers = group["publisher_id"].dropna().astype(str).tolist()
        top_categories = _top_labels(click_categories, top_k)
        top_publishers = _top_labels(click_publishers, top_k)
        top_category = top_categories[0] if top_categories else None
        top_publisher = top_publishers[0] if top_publishers else None

        category_jaccard = jaccard(pref_categories, top_categories)
        publisher_jaccard = jaccard(pref_publishers, top_publishers)
        rows.append(
            {
                "user_id": user_id,
                "click_count": int(len(group)),
                "top_clicked_category": top_category,
                "top_clicked_publisher": top_publisher,
                "top_category_in_stated": bool(top_category in set(pref_categories)) if top_category else False,
                "top_publisher_in_stated": bool(top_publisher in set(pref_publishers)) if top_publisher else False,
                "category_jaccard_top3": category_jaccard,
                "publisher_jaccard_top3": publisher_jaccard,
                "preference_click_category_cosine": _empirical_cosine(pref_categories, click_categories),
                "preference_click_publisher_cosine": _empirical_cosine(pref_publishers, click_publishers),
                "category_divergence": 1.0 - category_jaccard if not math.isnan(category_jaccard) else float("nan"),
                "n_pref_categories": int(profile["n_pref_categories"]),
                "n_pref_publishers": int(profile["n_pref_publishers"]),
            }
        )
    return pd.DataFrame(rows)


def compute_click_traceability(exposures: pd.DataFrame, clicks: pd.DataFrame) -> pd.DataFrame:
    """Trace click-consumption events to same-day and historical exposure logs."""

    same_day = set(zip(exposures["user_id"], exposures["date"], exposures["news_id"], strict=False))
    ever = set(zip(exposures["user_id"], exposures["news_id"], strict=False))
    user_dates = set(zip(exposures["user_id"], exposures["date"], strict=False))
    rank_lookup = {
        (row.user_id, row.date, row.news_id): row.rank
        for row in exposures.itertuples(index=False)
    }
    rows = []
    for row in clicks.itertuples(index=False):
        key = (row.user_id, row.date, row.news_id)
        rows.append(
            {
                "user_id": row.user_id,
                "date": row.date,
                "news_id": row.news_id,
                "surface": row.surface,
                "has_same_day_recommendations": (row.user_id, row.date) in user_dates,
                "same_day_hit": key in same_day,
                "ever_recommended_hit": (row.user_id, row.news_id) in ever,
                "same_day_rank": rank_lookup.get(key, np.nan),
            }
        )
    return pd.DataFrame(rows)


def compute_date_matched_random_baseline(exposures: pd.DataFrame, clicks: pd.DataFrame) -> pd.DataFrame:
    """Estimate same-day random traceability using date-matched exposure pools."""

    date_pool = exposures.groupby("date")["news_id"].agg(lambda x: set(x.dropna().astype(str)))
    user_date_size = exposures.groupby(["user_id", "date"])["news_id"].nunique()
    median_size_by_date = user_date_size.groupby(level="date").median().to_dict()
    rows = []
    for row in clicks.itertuples(index=False):
        pool = date_pool.get(row.date, set())
        if not pool:
            probability = np.nan
        else:
            list_size = user_date_size.get((row.user_id, row.date), median_size_by_date.get(row.date, 0))
            probability = min(float(list_size) / len(pool), 1.0) if row.news_id in pool else 0.0
        rows.append({"user_id": row.user_id, "date": row.date, "news_id": row.news_id, "random_hit_prob": probability})
    return pd.DataFrame(rows)


def compute_popularity_aware_baseline(
    exposures: pd.DataFrame,
    clicks: pd.DataFrame,
    *,
    progress: Callable[[str], None] | None = None,
) -> pd.DataFrame:
    """Compute a same-day recommendation-popularity baseline.

    For each click with a same-day recommendation list, this asks whether the
    clicked item would appear in a same-sized list of the most globally
    recommended items on that date after removing the focal user's own list.
    This is a popularity-aware exposure baseline, not a click oracle.
    """

    rec_size = exposures.groupby(["user_id", "date"])["news_id"].nunique().to_dict()
    date_counts: dict[str, Counter[str]] = {}
    for date, group in exposures.groupby("date"):
        date_counts[date] = Counter(group["news_id"].dropna().astype(str))
    user_date_items = (
        exposures.groupby(["user_id", "date"])["news_id"]
        .agg(lambda x: Counter(x.dropna().astype(str)))
        .to_dict()
    )

    needed_pairs = sorted({(row.user_id, row.date) for row in clicks.itertuples(index=False) if (row.user_id, row.date) in rec_size})
    popular_sets: dict[tuple[str, str], set[str]] = {}
    total_pairs = len(needed_pairs)
    if progress is not None:
        progress(f"    building popularity cache for {total_pairs:,} user-date pairs")
    for idx, pair in enumerate(needed_pairs, start=1):
        user_id, date = pair
        adjusted = date_counts.get(date, Counter()).copy()
        for item, count in user_date_items.get(pair, Counter()).items():
            adjusted[item] -= count
            if adjusted[item] <= 0:
                del adjusted[item]
        k = max(int(rec_size.get(pair, 1)), 1)
        popular_sets[pair] = {
            item
            for item, _count in sorted(adjusted.items(), key=lambda item_count: (-item_count[1], item_count[0]))[:k]
        }
        if progress is not None and (idx % 500 == 0 or idx == total_pairs):
            progress(f"    cached {idx:,}/{total_pairs:,} user-date popularity lists")

    rows = [
        {
            "user_id": row.user_id,
            "date": row.date,
            "news_id": row.news_id,
            "popularity_hit": row.news_id in popular_sets.get((row.user_id, row.date), set()),
        }
        for row in clicks.itertuples(index=False)
    ]
    return pd.DataFrame(rows)


def compute_topk_traceability(exposures: pd.DataFrame, clicks: pd.DataFrame, ks: tuple[int, ...] = (1, 3, 5, 10, 20)) -> pd.DataFrame:
    """Summarize click traceability for top-k recommendation prefixes."""

    rows = []
    for k in ks:
        topk = exposures[exposures["rank"] <= k]
        keys = set(zip(topk["user_id"], topk["date"], topk["news_id"], strict=False))
        actual = [
            (row.user_id, row.date, row.news_id) in keys
            for row in clicks.itertuples(index=False)
        ]
        rows.append({"k": k, "hit_rate": float(np.mean(actual)) if actual else np.nan, "clicks": len(actual)})
    return pd.DataFrame(rows)


def compute_surface_traceability(trace_rows: pd.DataFrame) -> pd.DataFrame:
    """Summarize same-day traceability by app surface."""

    if trace_rows.empty:
        return pd.DataFrame(columns=["surface", "clicks", "same_day_hit_rate", "lift_vs_overall"])
    overall = trace_rows["same_day_hit"].mean()
    grouped = (
        trace_rows.groupby("surface", dropna=False)
        .agg(clicks=("news_id", "size"), same_day_hit_rate=("same_day_hit", "mean"))
        .reset_index()
    )
    grouped["lift_vs_overall"] = grouped["same_day_hit_rate"] / overall if overall else np.nan
    return grouped.sort_values(["same_day_hit_rate", "clicks"], ascending=[False, False])


def compute_diversity_audit(
    exposures: pd.DataFrame,
    clicks: pd.DataFrame,
    *,
    seed: int = 17,
) -> pd.DataFrame:
    """Compute user-level E-C diversity and concentration gaps."""

    exposure_groups = exposures.groupby("user_id")
    click_groups = clicks.groupby("user_id")
    users = sorted(set(exposure_groups.groups) & set(click_groups.groups))
    rows = []
    for user_id in users:
        exp = exposure_groups.get_group(user_id)
        clk = click_groups.get_group(user_id)
        exp_cat = exp["category"].dropna().astype(str).tolist()
        clk_cat = clk["category"].dropna().astype(str).tolist()
        exp_pub = exp["publisher_id"].dropna().astype(str).tolist()
        clk_pub = clk["publisher_id"].dropna().astype(str).tolist()
        rows.append(
            {
                "user_id": user_id,
                "exposure_count": len(exp),
                "click_count": len(clk),
                "exposure_category_entropy": normalized_entropy(exp_cat),
                "click_category_entropy": normalized_entropy(clk_cat),
                "category_entropy_gap": normalized_entropy(exp_cat) - normalized_entropy(clk_cat),
                "count_matched_category_entropy_gap": count_matched_metric_gap(exp_cat, clk_cat, normalized_entropy, seed=seed),
                "exposure_publisher_entropy": normalized_entropy(exp_pub),
                "click_publisher_entropy": normalized_entropy(clk_pub),
                "publisher_entropy_gap": normalized_entropy(exp_pub) - normalized_entropy(clk_pub),
                "category_hhi_gap": hhi(clk_cat) - hhi(exp_cat),
                "category_top_share_gap": top_share(clk_cat) - top_share(exp_cat),
                "category_js_divergence": js_divergence(exp_cat, clk_cat),
                "publisher_js_divergence": js_divergence(exp_pub, clk_pub),
            }
        )
    return pd.DataFrame(rows)


def summarize_audit(
    alignment: pd.DataFrame,
    trace_rows: pd.DataFrame,
    random_rows: pd.DataFrame,
    popularity_rows: pd.DataFrame,
    diversity: pd.DataFrame,
) -> dict[str, float | int | None]:
    """Create compact aggregate values for paper-claim checks."""

    def mean_or_none(series: pd.Series) -> float | None:
        value = series.dropna().mean()
        return None if pd.isna(value) else float(value)

    summary: dict[str, float | int | None] = {
        "users_with_profile_and_clicks": int(len(alignment)),
        "top_category_match_rate": mean_or_none(alignment["top_category_in_stated"].astype(float)) if not alignment.empty else None,
        "category_jaccard_mean": mean_or_none(alignment["category_jaccard_top3"]) if not alignment.empty else None,
        "preference_click_category_cosine_mean": mean_or_none(alignment["preference_click_category_cosine"]) if not alignment.empty else None,
        "click_events": int(len(trace_rows)),
        "same_day_available_rows": int(trace_rows["has_same_day_recommendations"].sum()) if not trace_rows.empty else 0,
        "same_day_hit_rate": (
            mean_or_none(trace_rows.loc[trace_rows["has_same_day_recommendations"], "same_day_hit"].astype(float))
            if not trace_rows.empty
            else None
        ),
        "ever_recommended_hit_rate": mean_or_none(trace_rows["ever_recommended_hit"].astype(float)) if not trace_rows.empty else None,
        "date_matched_random_hit_rate": (
            mean_or_none(random_rows.loc[trace_rows["has_same_day_recommendations"], "random_hit_prob"])
            if not random_rows.empty and not trace_rows.empty
            else None
        ),
        "popularity_aware_hit_rate": (
            mean_or_none(popularity_rows.loc[trace_rows["has_same_day_recommendations"], "popularity_hit"].astype(float))
            if not popularity_rows.empty and not trace_rows.empty
            else None
        ),
        "users_with_exposure_and_clicks": int(len(diversity)),
        "category_entropy_gap_mean": mean_or_none(diversity["category_entropy_gap"]) if not diversity.empty else None,
        "count_matched_category_entropy_gap_mean": mean_or_none(diversity["count_matched_category_entropy_gap"]) if not diversity.empty else None,
        "category_hhi_gap_mean": mean_or_none(diversity["category_hhi_gap"]) if not diversity.empty else None,
        "category_top_share_gap_mean": mean_or_none(diversity["category_top_share_gap"]) if not diversity.empty else None,
        "category_js_divergence_mean": mean_or_none(diversity["category_js_divergence"]) if not diversity.empty else None,
    }
    return summary


def run_pec_audit(
    data_dir: Path,
    *,
    output_dir: Path | None = None,
    seed: int = 17,
    progress: Callable[[str], None] | None = None,
) -> dict[str, pd.DataFrame | dict]:
    """Run the full measurement-audit pipeline from processed tables."""

    started = time.perf_counter()

    def log(step: str) -> None:
        if progress is not None:
            progress(f"[{time.perf_counter() - started:6.1f}s] {step}")

    log("1/9 loading and standardizing processed tables")
    inputs = load_audit_inputs(data_dir)
    log(
        "loaded "
        f"{len(inputs.profiles):,} profiles, "
        f"{len(inputs.clicks):,} matched clicks, "
        f"{len(inputs.exposures):,} matched recommendation items"
    )
    log("2/9 computing preference-consumption alignment")
    alignment = compute_preference_consumption_alignment(inputs.profiles, inputs.clicks)
    log(f"alignment users: {len(alignment):,}")
    log("3/9 tracing clicks to same-day and historical recommendations")
    trace_rows = compute_click_traceability(inputs.exposures, inputs.clicks)
    log(
        "traceability rows: "
        f"{len(trace_rows):,}; available same-day rows: "
        f"{int(trace_rows['has_same_day_recommendations'].sum()):,}"
    )
    log("4/9 computing date-matched random baseline")
    random_rows = compute_date_matched_random_baseline(inputs.exposures, inputs.clicks)
    log("5/9 computing popularity-aware exposure baseline")
    popularity_rows = compute_popularity_aware_baseline(inputs.exposures, inputs.clicks, progress=log)
    log("6/9 computing top-k traceability")
    topk = compute_topk_traceability(inputs.exposures, inputs.clicks)
    log("7/9 computing surface traceability")
    surfaces = compute_surface_traceability(trace_rows)
    log("8/9 computing diversity and count-matched audit")
    diversity = compute_diversity_audit(inputs.exposures, inputs.clicks, seed=seed)
    log(f"diversity users: {len(diversity):,}")
    log("9/9 summarizing audit outputs")
    summary = summarize_audit(alignment, trace_rows, random_rows, popularity_rows, diversity)

    results: dict[str, pd.DataFrame | dict] = {
        "alignment": alignment,
        "click_traceability": trace_rows,
        "date_matched_random_baseline": random_rows,
        "popularity_aware_baseline": popularity_rows,
        "topk_traceability": topk,
        "surface_traceability": surfaces,
        "diversity_audit": diversity,
        "summary": summary,
    }
    if output_dir is not None:
        log(f"writing outputs to {output_dir}")
        write_audit_outputs(results, output_dir)
    log("done")
    return results


def write_audit_outputs(results: dict[str, pd.DataFrame | dict], output_dir: Path) -> None:
    """Write pipeline outputs to CSV/JSON files."""

    output_dir.mkdir(parents=True, exist_ok=True)
    for name, value in results.items():
        if isinstance(value, pd.DataFrame):
            value.to_csv(output_dir / f"{name}.csv", index=False)
        else:
            (output_dir / f"{name}.json").write_text(json.dumps(value, indent=2), encoding="utf-8")
