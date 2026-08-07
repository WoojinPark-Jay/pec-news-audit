#!/usr/bin/env python3
"""Compute user-clustered RQ2 traceability uncertainty checks.

This script uses private processed tables when available and writes only
aggregate, release-safe summaries. It does not modify manuscript inputs.
"""

from __future__ import annotations

import json
import math
import os
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
PRIVATE_ROOT = Path(os.environ.get("PEC_GAP_PRIVATE_ROOT", ROOT))
OUTPUT_ROOT = Path(os.environ.get("PEC_GAP_OUTPUT_ROOT", ROOT))
PROCESSED = PRIVATE_ROOT / "data" / "processed"
PRIVATE_TABLES = PRIVATE_ROOT / "reports" / "tables"
OUTPUT_TABLES = OUTPUT_ROOT / "reports" / "tables"


def truthy(series: pd.Series) -> pd.Series:
    return series.astype(str).str.lower().isin({"true", "1", "yes"})


def inclusion_probability_without_replacement(pool_n: int, multiplicity: int, draw_n: int) -> float:
    """Probability of drawing at least one matching article row from a duplicate pool."""
    if pool_n <= 0 or multiplicity <= 0 or draw_n <= 0:
        return 0.0
    draw_n = min(draw_n, pool_n)
    if pool_n - multiplicity < draw_n:
        return 1.0
    log_no_hit = 0.0
    for i in range(draw_n):
        log_no_hit += math.log((pool_n - multiplicity - i) / (pool_n - i))
    return 1.0 - math.exp(log_no_hit)


def build_row_differences(click_rows: pd.DataFrame, recs: pd.DataFrame, k_label: str) -> pd.DataFrame:
    rec_subset = recs.copy()
    if k_label != "all":
        rec_subset = rec_subset.loc[rec_subset["rank_num"] <= int(k_label)].copy()

    list_sizes = rec_subset.groupby(["user_id", "recommendation_date"]).size().rename("list_size")
    pool_sizes = rec_subset.groupby("recommendation_date").size().rename("pool_n")
    multiplicities = rec_subset.groupby(["recommendation_date", "news_id"]).size().rename("multiplicity")

    out = (
        click_rows.join(list_sizes, on=["user_id", "event_date"])
        .join(pool_sizes, on="event_date")
        .join(multiplicities, on=["event_date", "news_id"])
    )
    out["list_size"] = out["list_size"].fillna(0).astype(int)
    out["pool_n"] = out["pool_n"].fillna(0).astype(int)
    out["multiplicity"] = out["multiplicity"].fillna(0).astype(int)

    if k_label == "all":
        out["actual_hit"] = truthy(out["clicked_in_same_day_recs"]).astype(float)
    else:
        topk_keys = set(
            zip(
                rec_subset["user_id"].astype(str),
                rec_subset["recommendation_date"].astype(str),
                rec_subset["news_id"].astype(str),
            )
        )
        out["actual_hit"] = [
            float((user_id, date, news_id) in topk_keys)
            for user_id, date, news_id in zip(out["user_id"], out["event_date"], out["news_id"])
        ]

    out["baseline_prob"] = [
        inclusion_probability_without_replacement(pool_n, multiplicity, list_size)
        for pool_n, multiplicity, list_size in zip(out["pool_n"], out["multiplicity"], out["list_size"])
    ]
    out["paired_diff"] = out["actual_hit"] - out["baseline_prob"]
    return out[["user_id", "actual_hit", "baseline_prob", "paired_diff"]].copy()


def user_clustered_bootstrap(row_diffs: pd.DataFrame, rng: np.random.Generator, n_boot: int) -> dict:
    user_sums = (
        row_diffs.groupby("user_id", sort=True)
        .agg(
            n_rows=("paired_diff", "size"),
            actual_sum=("actual_hit", "sum"),
            baseline_sum=("baseline_prob", "sum"),
            diff_sum=("paired_diff", "sum"),
        )
        .reset_index()
    )
    values = user_sums[["n_rows", "actual_sum", "baseline_sum", "diff_sum"]].to_numpy(dtype=float)
    n_users = len(values)
    boot_actual = []
    boot_baseline = []
    boot_delta = []
    for _ in range(n_boot):
        idx = rng.integers(0, n_users, size=n_users)
        sample = values[idx]
        denom = sample[:, 0].sum()
        boot_actual.append(float(sample[:, 1].sum() / denom))
        boot_baseline.append(float(sample[:, 2].sum() / denom))
        boot_delta.append(float(sample[:, 3].sum() / denom))

    return {
        "n_bootstrap": n_boot,
        "cluster": "user_id",
        "n_users": int(n_users),
        "n_click_rows": int(len(row_diffs)),
        "observed_hit_rate": float(row_diffs["actual_hit"].mean()),
        "candidate_pool_expectation": float(row_diffs["baseline_prob"].mean()),
        "paired_delta": float(row_diffs["paired_diff"].mean()),
        "observed_hit_ci_low": float(np.percentile(boot_actual, 2.5)),
        "observed_hit_ci_high": float(np.percentile(boot_actual, 97.5)),
        "candidate_pool_ci_low": float(np.percentile(boot_baseline, 2.5)),
        "candidate_pool_ci_high": float(np.percentile(boot_baseline, 97.5)),
        "paired_delta_ci_low": float(np.percentile(boot_delta, 2.5)),
        "paired_delta_ci_high": float(np.percentile(boot_delta, 97.5)),
    }


def main() -> None:
    click_rows = pd.read_csv(PRIVATE_TABLES / "rq2_click_exposure_rows.csv", dtype=str).fillna("")
    recs = pd.read_csv(PROCESSED / "recommendation_items_enriched.csv", dtype=str).fillna("")
    click_rows = click_rows.loc[truthy(click_rows["has_same_day_recommendations"])].copy()
    recs = recs.loc[truthy(recs["news_matched"])].copy()
    click_rows["news_id"] = click_rows["news_id"].astype(str)
    recs["news_id"] = recs["news_id"].astype(str)
    recs["rank_num"] = pd.to_numeric(recs["rank"], errors="coerce")

    rng = np.random.default_rng(20260807)
    summaries = []
    for k_label in ["3", "5", "10", "20", "all"]:
        row_diffs = build_row_differences(click_rows, recs, k_label)
        summary = user_clustered_bootstrap(row_diffs, rng=rng, n_boot=5000)
        summary["k"] = k_label
        summaries.append(summary)

    out = pd.DataFrame(summaries)
    ordered = [
        "k",
        "n_click_rows",
        "n_users",
        "observed_hit_rate",
        "candidate_pool_expectation",
        "paired_delta",
        "paired_delta_ci_low",
        "paired_delta_ci_high",
        "observed_hit_ci_low",
        "observed_hit_ci_high",
        "candidate_pool_ci_low",
        "candidate_pool_ci_high",
        "n_bootstrap",
        "cluster",
    ]
    out = out[ordered]
    OUTPUT_TABLES.mkdir(parents=True, exist_ok=True)
    out_csv = OUTPUT_TABLES / "rq2_user_clustered_traceability_ci.csv"
    out_json = OUTPUT_TABLES / "rq2_user_clustered_traceability_ci.json"
    out.to_csv(out_csv, index=False)
    out_json.write_text(json.dumps({"rows": out.to_dict("records")}, indent=2), encoding="utf-8")
    print(out.to_string(index=False))
    print(f"\nWrote {out_csv}")
    print(f"Wrote {out_json}")


if __name__ == "__main__":
    main()
