# Project Structure

This repository is a release artifact package. It is organized around public
inspection of aggregate claims, synthetic examples, and reproducibility code.
It is not a raw-data repository.

## Source Code

- `src/pecgap/metrics.py`: implementations of the audit metrics, including
  Jaccard overlap, entropy, HHI, top-share, Jensen-Shannon divergence, and
  count-matched comparisons.
- `src/pecgap/artifacts.py`: helpers for reading release-safe aggregate tables
  and writing figures.
- `src/pecgap/preprocessing.py`: schema normalization helpers used by
  authorized private reruns.
- `src/pecgap/audit_pipeline.py`: PEC audit pipeline code for approved
  processed tables.
- `src/pecgap/modeling.py`: diagnostic model utilities.
- `src/pecgap/private_schema.py`: expected processed-table schemas for
  authorized private environments.

## Scripts

- `scripts/generate_public_synthetic_data.py`: creates the deterministic public
  toy cohort from explicit generation rules only.
- `scripts/run_public_synthetic_pipeline.py`: runs the end-to-end release-safe
  code path on bundled toy records and writes only ignored scratch outputs.
- `scripts/check_release_artifacts.py`: verifies that public aggregate tables
  are readable and consistent with headline audit quantities.
- `scripts/make_release_figures.py`: regenerates release-safe figures from
  aggregate tables.
- `scripts/check_private_processed_data.py`: checks schema compatibility for
  approved private processed inputs.
- `scripts/run_repro_deep_notebooks.py`: runs the documented notebook sequence
  in an approved environment.
- `scripts/run_rq2_clustered_uncertainty.py`: recomputes the user-clustered RQ2
  uncertainty summary when approved processed inputs are available.

## Data and Reports

- `data/synthetic/`: toy schema-compatible examples. These are not sampled user
  records.
- `tmp/public_synthetic_run/`: generated synthetic-run outputs; ignored by Git.
- `reports/tables/`: release-safe aggregate tables.
- `reports/figures/`: final and release-safe figure artifacts.

## Notebooks

- `notebooks/00_release_artifact_tour.ipynb`: tour of the release package.
- `notebooks/01_metric_walkthrough_synthetic.ipynb`: metric examples on
  synthetic data.
- `notebooks/02_private_pipeline_template.ipynb`: template for authorized
  private reruns.
- `notebooks/repro_deep/`: output-stripped step-by-step notebooks documenting
  the internal analysis sequence.

## Documentation

- `docs/DATA_RELEASE_POLICY.md`: public/private data boundary.
- `docs/REPRODUCIBILITY.md`: how release-safe and authorized-private
  reproducibility modes differ.
- `docs/METRIC_GUIDE.md`: metric definitions and claim boundaries.
- `docs/ARTIFACT_GUIDE.md`: what each public artifact supports.
- `docs/REPOSITORY_QUALITY_CHECKLIST.md`: pre-release checks.
