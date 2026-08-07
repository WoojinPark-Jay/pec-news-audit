# Authorized Deep Reproduction Notebooks

These notebooks reconstruct the analysis step by step from private processed
tables. They are intentionally output-stripped for repository release.

Use this folder only in an approved internal environment where
`data/processed/` contains the authorized processed CSV files. The notebooks
should be read in order:

Current public/release repo note: this repository normally contains only
`data/synthetic/` toy data, not the private `data/processed/` folder. If the
private processed files live elsewhere, do not copy them into GitHub. Instead,
point the notebooks to the exact local folder:

```bash
export PEC_GAP_PROCESSED_DIR="/ABSOLUTE/PATH/TO/data/processed"
```

You can check a candidate folder without modifying anything:

```bash
python scripts/check_private_processed_data.py --data-dir "/ABSOLUTE/PATH/TO/data/processed"
```

To run the full step-by-step notebook sequence from the terminal:

```bash
PYTHONPATH=.python_packages MPLCONFIGDIR=/tmp/pecgap_mpl \
  python scripts/run_repro_deep_notebooks.py
```

Notebook-generated outputs should stay under `tmp/repro_deep/...` or a
deliberate private scratch path. Treat `reports/tables/`, `reports/figures/`,
and the Overleaf submission folder as manuscript-facing reference artifacts
unless you intentionally regenerate approved release outputs.

For private local reruns, keep approved processed tables outside the public
repository. A typical location is:

```text
<LOCAL_PRIVATE_DATA_DIR>/data/processed
```

Set `PEC_GAP_PRIVATE_ROOT=<LOCAL_PRIVATE_DATA_DIR>` before launching Jupyter, or
copy/symlink the approved tables into a repo-local `data/processed/` directory.

1. `00_data_eda_and_schema.ipynb` checks table coverage and basic data health.
2. `01_preprocessing_and_joining.ipynb` explains how user profiles,
   recommendation logs, click logs, surface fields, and article metadata are
   joined.
3. `02_pec_metrics_and_statistics.ipynb` recomputes the PEC audit metrics and
   robustness statistics.
4. `03_weighted_preferences_and_surface_paths.ipynb` analyzes weighted
   profile-state features and surface-specific click pathways.
5. `04_modeling_rq4_from_features.ipynb` runs the bounded diagnostic
   high-divergence models and validation checks.
6. `05_paper_handoff_and_artifacts.ipynb` maps regenerated artifacts back to
   manuscript tables and figures.

The notebooks are not intended to release raw logs. Commit only aggregate
outputs that pass the data-release policy in `docs/DATA_RELEASE_POLICY.md`.
