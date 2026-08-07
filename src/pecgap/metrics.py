"""Metric definitions for the Preference-Exposure-Consumption audit.

The functions in this module are intentionally small and transparent. They
mirror the paper's measurement definitions rather than implementing a new
ranking objective.
"""

from __future__ import annotations

from collections import Counter
from collections.abc import Callable, Iterable
import math

import numpy as np


def clean_labels(values: Iterable[object]) -> list[str]:
    """Return non-empty string labels from an iterable."""

    out: list[str] = []
    for value in values:
        if value is None:
            continue
        if isinstance(value, float) and math.isnan(value):
            continue
        label = str(value).strip()
        if label:
            out.append(label)
    return out


def jaccard(a: Iterable[object], b: Iterable[object]) -> float:
    """Set overlap: |A intersection B| / |A union B|."""

    a_set = set(clean_labels(a))
    b_set = set(clean_labels(b))
    union = a_set | b_set
    if not union:
        return float("nan")
    return len(a_set & b_set) / len(union)


def normalized_entropy(values: Iterable[object]) -> float:
    """Shannon entropy normalized to [0, 1] by log of observed support size."""

    labels = clean_labels(values)
    if not labels:
        return float("nan")
    counts = np.array(list(Counter(labels).values()), dtype=float)
    probs = counts / counts.sum()
    entropy = float(-(probs * np.log(probs)).sum())
    if len(counts) <= 1:
        return 0.0
    return entropy / math.log(len(counts))


def hhi(values: Iterable[object]) -> float:
    """Herfindahl-Hirschman concentration index over observed labels."""

    labels = clean_labels(values)
    if not labels:
        return float("nan")
    counts = np.array(list(Counter(labels).values()), dtype=float)
    probs = counts / counts.sum()
    return float(np.sum(probs * probs))


def top_share(values: Iterable[object]) -> float:
    """Share of the most frequent label."""

    labels = clean_labels(values)
    if not labels:
        return float("nan")
    return Counter(labels).most_common(1)[0][1] / len(labels)


def js_divergence(a_values: Iterable[object], b_values: Iterable[object]) -> float:
    """Jensen-Shannon divergence between two empirical label distributions.

    The result uses base-2 logarithms, so values are bounded between 0 and 1
    for discrete distributions.
    """

    a_labels = clean_labels(a_values)
    b_labels = clean_labels(b_values)
    if not a_labels or not b_labels:
        return float("nan")
    keys = sorted(set(a_labels) | set(b_labels))
    a_counts = Counter(a_labels)
    b_counts = Counter(b_labels)
    p = np.array([a_counts.get(k, 0) for k in keys], dtype=float)
    q = np.array([b_counts.get(k, 0) for k in keys], dtype=float)
    p = p / p.sum()
    q = q / q.sum()
    m = 0.5 * (p + q)

    def kl(x: np.ndarray, y: np.ndarray) -> float:
        mask = x > 0
        return float(np.sum(x[mask] * np.log2(x[mask] / y[mask])))

    return 0.5 * kl(p, m) + 0.5 * kl(q, m)


def count_matched_metric_gap(
    exposure_values: Iterable[object],
    click_values: Iterable[object],
    metric: Callable[[Iterable[object]], float] = normalized_entropy,
    *,
    n_iter: int = 300,
    seed: int = 17,
) -> float:
    """Estimate exposure-click metric gap after matching exposure count to clicks.

    For each user, this samples the user's exposure labels down to the number
    of observed click labels and compares the sampled exposure metric against
    the click metric. It is a measurement-validity check for sparse clicks.
    """

    exposure = clean_labels(exposure_values)
    clicks = clean_labels(click_values)
    if not exposure or not clicks or len(exposure) < len(clicks):
        return float("nan")
    rng = np.random.default_rng(seed)
    exposure_array = np.array(exposure, dtype=object)
    sampled_scores = []
    for _ in range(n_iter):
        sampled = rng.choice(exposure_array, size=len(clicks), replace=False)
        sampled_scores.append(metric(sampled.tolist()))
    return float(np.nanmean(sampled_scores) - metric(clicks))
