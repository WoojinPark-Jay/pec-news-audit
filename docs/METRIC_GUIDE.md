# PEC Metric Guide

The audit separates four observable traces:

- **Preference**: stated categories, stated sources, and weighted profile state.
- **Logged exposure**: user-date recommendation lists recorded by the system.
- **Surface pathways**: app pathways through which a click is observed.
- **Consumption**: clicked articles linked to metadata.

PEC is not one composite score. It is a relation-specific audit protocol. Each
metric below specifies which traces are compared, which rows are eligible for
the denominator, and what interpretation is permitted by the available logs.

## Preference-Consumption Alignment

### Category Jaccard

Category Jaccard compares the user's stated category set with the user's
top-clicked category set:

```text
J(u) = |P_cat(u) intersection C_top_cat(u)| / |P_cat(u) union C_top_cat(u)|
```

It asks whether the categories users explicitly state overlap with the
categories they most often click.

### Divergence

```text
D(u) = 1 - J(u)
```

Higher divergence means lower overlap between stated preference and observed
click categories. The diagnostic model uses this as an audit label, not as a
production targeting objective.

### Weighted Preference-Click Cosine

When a weighted profile-state vector is available, cosine similarity compares
the profile distribution to the click-consumption distribution. This is useful
because it treats preference as a weighted state rather than only a set.

## Exposure-Consumption Traceability

### Same-day hit

Same-day hit asks whether a clicked article appeared in that user's logged
recommendation list on the same date.

This is not CTR. It is a traceability measure conditioned on observed clicks
and logged recommendation user-days.

### Top-k lift

Top-k lift compares logged recommendation hit rate against a date-matched
random baseline:

```text
Lift@k = Hit@k_logged / Hit@k_random
```

Popularity-aware checks compare logged recommendation hit rates against
non-personalized popularity baselines.

## Diversity and Concentration

### Normalized entropy

Entropy is higher when a distribution is broader:

```text
H(X) = - sum_x p_x log(p_x) / log(|X|)
```

The paper computes this separately for exposure and click consumption.

### HHI

HHI is a concentration measure:

```text
HHI(X) = sum_x p_x^2
```

Higher HHI means a distribution is more concentrated.

### Top-share

Top-share is the share of the most frequent category or publisher:

```text
TopShare(X) = max_x p_x
```

Higher top-share means more top-heavy behavior.

### Jensen-Shannon divergence

Jensen-Shannon divergence compares two empirical distributions:

```text
JS(p, q) = 0.5 KL(p || m) + 0.5 KL(q || m), where m = 0.5(p + q)
```

It is symmetric and finite when some categories appear in one distribution but
not the other. In this paper, JS helps show residual distributional mismatch
after count matching.

## Count Matching

Count matching samples exposure items down to the user's number of observed
clicks, then recomputes diversity or concentration metrics:

```text
Delta_M(u) = M(E'_u) - M(C_u), where |E'_u| = |C_u|
```

This distinguishes gaps caused by sparse click observation from gaps that
remain after exposure and consumption are compared on the same count scale.
