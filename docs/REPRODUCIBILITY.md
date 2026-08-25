# Reproducibility

The repository separates release-safe artifact reproduction from authorized
private operational reruns. This separation is part of the research design:
paper claims can be inspected through aggregate artifacts, while private
row-level behavior traces remain outside version control.

## Three Reproduction Levels

This project separates executable public examples, manuscript-facing aggregate
checks, and private operational reruns.

The core analysis package under `src/pecgap/` is shared across public synthetic
and authorized private execution. The repository does not replace the private
analysis with a mock implementation. Instead, the synthetic generator supplies
schema-compatible artificial rows, while an authorized rerun supplies approved
processed platform tables from an external path. Public aggregate verification
is intentionally separate because row-level private results cannot be published.

### Level 1: Public synthetic execution

This level requires only the bundled toy CSV files. It runs the same public
preprocessing and audit modules used by authorized reruns, but its numerical
outputs are illustrative rather than manuscript estimates.

```bash
python scripts/run_public_synthetic_pipeline.py
```

Outputs are written to `tmp/public_synthetic_run/`, which is ignored by Git.
The generated `RUN_MANIFEST.json` explicitly records that the run contains no
real user data and does not reproduce paper estimates. RQ4 model scores from
the deliberately structured toy cohort verify execution only; they are not
empirical performance claims and should not be compared with manuscript AUCs.

### Level 2: Release-safe aggregate verification

This mode requires only the files included in this repository.

```bash
python scripts/check_release_artifacts.py
python scripts/make_release_figures.py
```

It verifies aggregate values, checks popularity-aware baseline outputs, and
regenerates release-safe figures from non-user-level tables.

### Level 3: Authorized private rerun

This mode requires internal processed tables under `data/processed/`.

First check whether the expected private tables are present. For private local
reruns, approved processed tables should be kept outside the
public repository, preferably in a machine-local folder outside cloud-synced
storage:

```text
<LOCAL_PRIVATE_DATA_DIR>/data/processed
```

Do not copy those tables into the public repository. Point the notebook runner
to the approved directory through an environment variable:

```bash
python scripts/check_private_processed_data.py --data-dir "/ABSOLUTE/PATH/TO/data/processed"
export PEC_GAP_PROCESSED_DIR="/ABSOLUTE/PATH/TO/data/processed"
python scripts/run_repro_deep_notebooks.py
```

The runner executes the six output-stripped notebooks under
`notebooks/repro_deep/` in order and writes scratch outputs under
`tmp/repro_deep/`. It does not overwrite `reports/tables/`,
`reports/figures/`, or manuscript files.

The notebooks walk through the authorized row-level reconstruction of:

1. profile-state traces,
2. clicked-article traces,
3. recommendation exposure traces,
4. surface assignment,
5. PEC metrics,
6. candidate-pool and popularity-aware traceability baselines,
7. robustness and count-matched checks,
8. same-window, dense-history, and extreme-mismatch diagnostic models,
9. private validation tables under an ignored scratch directory.

The final future-window and alternative-label candidate grids are distributed
only as approved aggregate tables in `reports/tables/`. Every manuscript RQ4
task compares the same four prespecified model families: balanced logistic
regression, Random Forest, Extra Trees, and gradient boosting. The reported
task-level value is the highest mean user-level five-fold cross-validated AUC;
it is a descriptive model-selection estimate, not an unbiased external-test
performance estimate.

For a release-safe smoke test that does not require private data:

```bash
python -m pip install -e '.[test]'
pytest -q
python scripts/run_public_synthetic_pipeline.py
python scripts/check_release_artifacts.py
```

## Determinism

The metric code is deterministic except for count matching and stochastic model
validation. Random seeds should be fixed for:

- count-matched exposure sampling,
- cross-validation splits,
- tree-based diagnostic models,
- bootstrap confidence intervals.

The reported paper values are generated from fixed analysis artifacts. Small
differences can occur if private row-level data are regenerated after deduping
or schema-normalization changes.

## Release Boundary

Do not commit:

- raw event logs,
- row-level recommendation lists,
- row-level clicks,
- user-level feature tables,
- timestamped user traces,
- credentials or Cloud SQL exports.

Commit only:

- metric code,
- preprocessing, audit, and diagnostic modeling code,
- aggregate tables,
- approved figures,
- synthetic schema examples,
- manuscript files,
- documentation.

## Recommended Review Order

For collaborators reviewing the release-safe artifact package:

1. `python scripts/check_release_artifacts.py`
2. `notebooks/00_release_artifact_tour.ipynb`
3. `notebooks/01_metric_walkthrough_synthetic.ipynb`
4. `python scripts/make_release_figures.py`

For authorized internal reruns, follow the notebook order in
`notebooks/repro_deep/README.md`.
