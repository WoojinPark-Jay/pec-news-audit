# Aggregate Tables

These tables are release-safe summaries used to verify manuscript claims.

They intentionally exclude:

- raw event rows,
- timestamped user histories,
- recommendation item lists by user/date,
- user-level model feature tables.

Use `scripts/check_release_artifacts.py` to confirm the core tables are readable.

`rq1_figure_aggregate.json` contains only grouped Jaccard counts, label-support
summaries, and precomputed density curves. It is the identifier-free input used
to rebuild the final RQ1 figure; it does not contain user-level records.

`preference_weighted_label_proximity_sensitivity.csv` reports aggregate
cross-validation results for the headline RQ4 model, the nonempty stated-set
cohort, and a feature set that excludes category and publisher profile-support
counts. It contains no user-level predictions or identifiers.

The RQ4 candidate-grid tables evaluate four prespecified model families:
balanced logistic regression, Random Forest, Extra Trees, and gradient
boosting. Manuscript-facing task results report the candidate with the highest
mean user-level five-fold cross-validated AUC for that task. These files are
approved aggregate outputs from the authorized operational rerun; the bundled
synthetic pipeline verifies code execution but does not reproduce manuscript
AUCs.

Release-safe aggregate tables are licensed under CC BY 4.0 as described in
`../../DATA_LICENSE.md`. That license does not extend to raw or row-level
operational data, which are not included in this repository.
