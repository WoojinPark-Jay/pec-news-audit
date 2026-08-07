# Artifact Guide

This guide explains what each public artifact is meant to support.

## Public Tables

The files in `reports/tables/` are aggregate outputs used to inspect manuscript-level claims. They are not row-level user traces.

Key examples:

- `analysis_summary.json`: headline denominators and core RQ1-RQ3 quantities.
- `rq1_figure_aggregate.json`: identifier-free inputs for the preference-consumption figure.
- `popularity_baseline_check.csv`: recommendation traceability compared with candidate-pool and popularity-aware baselines.
- `rq2_user_clustered_traceability_ci.csv`: user-clustered bootstrap interval for the observed-minus-baseline traceability gap.
- `defense_count_adjusted_entropy_summary.csv`: count-matched diversity checks.
- `rq4_advanced_model_cv_results.csv`: aggregate diagnostic-model validation results.
- `preference_weighted_label_proximity_sensitivity.csv`: sensitivity checks for profile-proximity concerns.

## Public Figures

The files in `reports/figures/` are final or release-safe figure artifacts. They are generated from aggregate tables or manually prepared framework diagrams. They do not contain user-level records.

## Synthetic Data

The files in `data/synthetic/` show the expected table structure with toy records. They are intended for learning the schema and running examples. They are not sampled user records and should not be interpreted as empirical findings.

## Notebooks

The notebooks are split by purpose:

- `00_release_artifact_tour.ipynb`: tour of the release-safe package.
- `01_metric_walkthrough_synthetic.ipynb`: metric examples on synthetic data.
- `02_private_pipeline_template.ipynb`: template showing how an approved internal rerun would be configured.
- `repro_deep/`: output-stripped notebooks documenting the step-by-step internal analysis sequence.

Public users can inspect the notebooks and run synthetic examples. Authorized private reruns require approved processed tables that are not included in this repository.

## Scripts

- `scripts/check_release_artifacts.py`: verifies that public aggregate files are readable and internally consistent with headline claims.
- `scripts/make_release_figures.py`: regenerates release-safe figures from aggregate tables.
- `scripts/check_private_processed_data.py`: schema gate for approved internal processed tables.
- `scripts/run_repro_deep_notebooks.py`: runs the documented notebook sequence in an approved environment.
- `scripts/run_rq2_clustered_uncertainty.py`: computes the user-clustered RQ2 uncertainty summary when approved processed inputs are available.

## Non-Public Materials

The following materials are intentionally excluded:

- raw operational exports,
- timestamped click histories,
- recommendation lists by user and date,
- real user profile snapshots,
- user-level model feature tables,
- production identifiers,
- reference PDFs,
- internal review notes.

The paper's contribution is an audit protocol and a bounded empirical analysis, not a public user-behavior dataset.
