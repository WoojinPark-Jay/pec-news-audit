"""Diagnostic modeling utilities for the PEC audit.

The models here test whether high preference-consumption divergence is
structured by observable traces. They are diagnostic checks, not production
targeting models and not new recommendation algorithms.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from sklearn.ensemble import ExtraTreesClassifier, RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, roc_auc_score
from sklearn.model_selection import StratifiedKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


@dataclass(frozen=True)
class DiagnosticModelResult:
    """Container for diagnostic validation outputs."""

    cv_results: pd.DataFrame
    feature_importance: pd.DataFrame
    feature_table: pd.DataFrame


def build_user_feature_table(
    alignment: pd.DataFrame,
    diversity: pd.DataFrame,
    trace_rows: pd.DataFrame,
    *,
    label_quantile: float = 0.5,
) -> pd.DataFrame:
    """Build user-level features and a high-divergence diagnostic label."""

    if alignment.empty:
        return pd.DataFrame()

    trace_features = pd.DataFrame()
    if not trace_rows.empty:
        trace_features = (
            trace_rows.groupby("user_id")
            .agg(
                click_trace_count=("news_id", "size"),
                same_day_hit_rate=("same_day_hit", "mean"),
                ever_recommended_hit_rate=("ever_recommended_hit", "mean"),
                mean_same_day_rank=("same_day_rank", "mean"),
            )
            .reset_index()
        )

    cols = [
        "user_id",
        "click_count",
        "category_divergence",
        "preference_click_category_cosine",
        "preference_click_publisher_cosine",
        "n_pref_categories",
        "n_pref_publishers",
    ]
    features = alignment[[column for column in cols if column in alignment.columns]].copy()
    if not diversity.empty:
        diversity_features = diversity.drop(columns=["click_count"], errors="ignore")
        features = features.merge(diversity_features, on="user_id", how="left")
    if not trace_features.empty:
        features = features.merge(trace_features, on="user_id", how="left")

    # Empty stated-category sets have zero overlap with a non-empty clicked
    # set (J=0, hence D=1), matching the primary RQ1 set-overlap definition.
    features["divergence_score"] = features["category_divergence"].fillna(1.0)
    threshold = features["divergence_score"].quantile(label_quantile)
    features["high_divergence"] = features["divergence_score"] > threshold
    return features


def _candidate_feature_columns(feature_table: pd.DataFrame) -> list[str]:
    excluded = {
        "user_id",
        "high_divergence",
        "category_divergence",
        "divergence_score",
        "category_jaccard_top3",
        "publisher_jaccard_top3",
        "top_category_in_stated",
        "top_publisher_in_stated",
        "top_clicked_category",
        "top_clicked_publisher",
        # Direct preference-click alignment quantities are too close to the
        # diagnostic label and are excluded from the default bounded model.
        "preference_click_category_cosine",
        "preference_click_publisher_cosine",
        # Click-distribution and exposure-click gap quantities are outcome-side
        # audit results, not pre-interpretation model inputs.
        "click_category_entropy",
        "click_publisher_entropy",
        "category_entropy_gap",
        "count_matched_category_entropy_gap",
        "publisher_entropy_gap",
        "category_hhi_gap",
        "category_top_share_gap",
        "category_js_divergence",
        "publisher_js_divergence",
    }
    numeric_cols = feature_table.select_dtypes(include=[np.number, bool]).columns
    return [column for column in numeric_cols if column not in excluded]


def run_diagnostic_models(feature_table: pd.DataFrame, *, seed: int = 17) -> DiagnosticModelResult:
    """Run cross-validated high-divergence diagnostic models."""

    if feature_table.empty or "high_divergence" not in feature_table.columns:
        skipped = pd.DataFrame(
            [{"model": "skipped", "reason": "no feature table", "n_users": int(len(feature_table))}]
        )
        return DiagnosticModelResult(skipped, pd.DataFrame(), feature_table)

    feature_cols = _candidate_feature_columns(feature_table)
    data = feature_table.dropna(subset=["high_divergence"]).copy()
    y = data["high_divergence"].astype(int).to_numpy()
    class_counts = pd.Series(y).value_counts()
    if len(feature_cols) == 0 or len(class_counts) < 2 or int(class_counts.min()) < 2:
        skipped = pd.DataFrame(
            [
                {
                    "model": "skipped",
                    "reason": "insufficient features or class balance",
                    "n_users": int(len(data)),
                    "feature_count": int(len(feature_cols)),
                    "positive_rate": float(np.mean(y)) if len(y) else np.nan,
                }
            ]
        )
        return DiagnosticModelResult(skipped, pd.DataFrame(), feature_table)

    n_splits = int(min(5, class_counts.min()))
    cv = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=seed)
    models = {
        "logistic_regression": Pipeline(
            [
                ("imputer", SimpleImputer(strategy="median")),
                ("scaler", StandardScaler()),
                ("model", LogisticRegression(max_iter=1000, class_weight="balanced", random_state=seed)),
            ]
        ),
        "random_forest": Pipeline(
            [
                ("imputer", SimpleImputer(strategy="median")),
                (
                    "model",
                    RandomForestClassifier(
                        n_estimators=300,
                        min_samples_leaf=2,
                        class_weight="balanced",
                        random_state=seed,
                    ),
                ),
            ]
        ),
        "extra_trees": Pipeline(
            [
                ("imputer", SimpleImputer(strategy="median")),
                (
                    "model",
                    ExtraTreesClassifier(
                        n_estimators=300,
                        min_samples_leaf=2,
                        class_weight="balanced",
                        random_state=seed,
                    ),
                ),
            ]
        ),
    }

    x = data[feature_cols]
    rows = []
    for model_name, model in models.items():
        aucs = []
        auprcs = []
        for train_idx, test_idx in cv.split(x, y):
            model.fit(x.iloc[train_idx], y[train_idx])
            scores = model.predict_proba(x.iloc[test_idx])[:, 1]
            if len(np.unique(y[test_idx])) > 1:
                aucs.append(roc_auc_score(y[test_idx], scores))
            auprcs.append(average_precision_score(y[test_idx], scores))
        rows.append(
            {
                "model": model_name,
                "n_users": int(len(data)),
                "folds": n_splits,
                "feature_count": int(len(feature_cols)),
                "positive_rate": float(np.mean(y)),
                "auc_mean": float(np.nanmean(aucs)) if aucs else np.nan,
                "auc_std": float(np.nanstd(aucs)) if aucs else np.nan,
                "auprc_mean": float(np.nanmean(auprcs)) if auprcs else np.nan,
                "auprc_std": float(np.nanstd(auprcs)) if auprcs else np.nan,
            }
        )

    importance = compute_feature_importance(data, feature_cols, seed=seed)
    return DiagnosticModelResult(pd.DataFrame(rows), importance, feature_table)


def compute_feature_importance(feature_table: pd.DataFrame, feature_cols: list[str], *, seed: int = 17) -> pd.DataFrame:
    """Fit a release-safe feature-importance diagnostic on the full sample."""

    if not feature_cols:
        return pd.DataFrame()
    y = feature_table["high_divergence"].astype(int).to_numpy()
    if len(np.unique(y)) < 2:
        return pd.DataFrame()
    pipeline = Pipeline(
        [
            ("imputer", SimpleImputer(strategy="median")),
            (
                "model",
                ExtraTreesClassifier(
                    n_estimators=500,
                    min_samples_leaf=2,
                    class_weight="balanced",
                    random_state=seed,
                ),
            ),
        ]
    )
    pipeline.fit(feature_table[feature_cols], y)
    model = pipeline.named_steps["model"]
    return (
        pd.DataFrame({"feature": feature_cols, "importance": model.feature_importances_})
        .sort_values("importance", ascending=False)
        .reset_index(drop=True)
    )
