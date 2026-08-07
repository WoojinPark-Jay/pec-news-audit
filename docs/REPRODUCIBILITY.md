# Reproducibility

The repository separates release-safe artifact reproduction from authorized
private operational reruns. This separation is part of the research design:
paper claims can be inspected through aggregate artifacts, while private
row-level behavior traces remain outside version control.

## Two Reproduction Modes

This project separates public reproducibility from private operational reruns.

### Mode 1: Release-safe artifact reproduction

This mode requires only the files included in this repository.

```bash
python scripts/check_release_artifacts.py
python scripts/make_release_figures.py
```

It verifies aggregate values, checks popularity-aware baseline outputs, and
regenerates release-safe figures from non-user-level tables.

### Mode 2: Authorized private rerun

This mode requires internal processed tables under `data/processed/`.

```bash
python scripts/run_private_pipeline.py
```

The script checks whether the expected private tables and columns are present.
For private local reruns, approved processed tables should be kept outside the
public repository, preferably in a machine-local folder outside cloud-synced
storage:

```text
<LOCAL_PRIVATE_DATA_DIR>/data/processed
```

Either copy or symlink the approved tables into `data/processed/`, or pass that
absolute path through `--data-dir` in the commands below. The repository should
not contain private processed tables.

After the schema gate passes, run:

```bash
python scripts/run_full_private_audit_pipeline.py --data-dir data/processed --output-dir reports/private/audit_pipeline
python scripts/run_diagnostic_model.py --data-dir data/processed --output-dir reports/private/diagnostic_model
```

These commands reconstruct:

1. profile-state traces,
2. clicked-article traces,
3. recommendation exposure traces,
4. surface assignment,
5. PEC metrics,
6. candidate-pool and popularity-aware traceability baselines,
7. robustness and count-matched checks,
8. diagnostic high-divergence models,
9. private validation tables under `reports/private/`.

For a release-safe smoke test that does not require private data:

```bash
python -m pip install -e '.[test]'
pytest -q
python scripts/check_release_artifacts.py
```

```bash
python scripts/run_full_private_audit_pipeline.py --synthetic --output-dir /tmp/pecgap_synthetic_audit
python scripts/run_diagnostic_model.py --synthetic --output-dir /tmp/pecgap_synthetic_model
```

The synthetic model may skip cross-validation if the toy sample is too small;
that is expected and still verifies that the code path imports and runs.

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
