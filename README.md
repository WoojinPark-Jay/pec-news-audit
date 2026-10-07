# PEC News Audit

Release artifacts for the manuscript:

**When Exposure Is Not Attention: Auditing the Preference-Exposure-Consumption Gap in Personalized News Recommenders**

This repository accompanies a measurement audit of a deployed mobile news recommender. The paper separates four platform traces:

- **Preference (P):** stated preferences and observed profile-state distributions.
- **Exposure (E):** logged recommendation lists.
- **Surface pathways (S):** app entry paths such as headline, category, home/feed, newsroom, article detail, search, and notifications.
- **Consumption (C):** observed article clicks.

Project page: **[PEC News Audit](https://woojinpark-jay.github.io/pec-news-audit/)**

The main purpose of this repository is to make the public parts of the audit inspectable without releasing private user-level logs. It provides metric code, aggregate result tables, figure artifacts, release-safe notebooks, and synthetic schemas. Raw operational logs, row-level recommendation lists, user click histories, profile snapshots, and production identifiers are not included.

## What You Can Do With This Repository

1. Inspect the definitions behind the PEC audit metrics.
2. Rebuild release-safe figures and tables from aggregate artifacts.
3. Run synthetic examples that mirror the schema of the private platform logs.
4. Check that the published aggregate claims are internally consistent.
5. Understand which claims are supported by available traces and which claims remain outside the observability boundary.

This repository is not a public benchmark dataset and does not contain behavioral traces from real users.

## Public Release Status

This repository provides release-safe research artifacts for a manuscript
currently under review. The submitted manuscript remains anonymized in
accordance with the venue's double-blind review requirements. The repository
contains no raw operational logs or row-level behavioral data.

## Three Reproduction Levels

The repository keeps code, data access, and empirical claims separate:

1. **Public synthetic execution** runs the PEC code on bundled toy records. It
   verifies schemas, table normalization, metrics, traceability, diversity
   calculations, and diagnostic feature construction. Its numbers are
   illustrative and are not manuscript estimates.
2. **Public aggregate verification** checks approved, identifier-free tables
   and regenerates release-safe figures supporting the reported manuscript
   claims.
3. **Authorized private rerun** uses the same source modules and the
   output-stripped `repro_deep` notebooks with approved processed platform
   tables stored outside this repository.

The `repro_deep` notebooks are readable implementation walkthroughs, not
public-data demos. When authorized processed tables are unavailable, they show
one explanatory notice and skip private-data computation cells without an
error. Use `01_metric_walkthrough_synthetic.ipynb` or
`scripts/run_public_synthetic_pipeline.py` for a fully runnable public example.
Any repository or data path printed after local execution is computed from the
reader's own extraction directory; no author filesystem path is embedded in
the output-stripped notebooks.

The public demo is not a separately simplified analysis implementation. Both
public and authorized runs import the core modules under `src/pecgap/`; what
changes is the input contract and where outputs may be written.

| Level | Input | Core code | What the output establishes |
|---|---|---|---|
| Public synthetic | Deterministic toy rows in `data/synthetic/` | `src/pecgap/` | The released pipeline executes safely end to end |
| Public aggregate | Identifier-free tables in `reports/tables/` | Artifact checks and figure scripts | Approved manuscript quantities and figures are internally consistent |
| Authorized private | Processed platform tables outside the repository | `src/pecgap/` plus `notebooks/repro_deep/` | The analyses can be rerun against approved operational data |

## Quick Start

Create an environment with the test dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[test]'
```

Run the complete public code path on bundled synthetic records:

```bash
python scripts/run_public_synthetic_pipeline.py
```

Check release-safe aggregate artifacts:

```bash
python scripts/check_release_artifacts.py
```

Regenerate release-safe figures from aggregate tables:

```bash
python scripts/make_release_figures.py
```

Run tests:

```bash
python -m pytest
```

To open or execute the notebooks, install the notebook tools as well:

```bash
python -m pip install -e '.[notebook]'
```

## Repository Map

### How the code folders differ

- **`src/pecgap/`** contains the reusable Python source code. `src` is the
  conventional abbreviation for *source*; it is not a separate data type or a
  private-data folder. Metric definitions, preprocessing, audit calculations,
  and modeling helpers live here.
- **`scripts/`** contains command-line entry points that call the reusable
  code in `src/pecgap/`. Use these files to run a complete public demo, check
  released aggregates, rebuild figures, or validate an authorized input
  folder. They should not duplicate the core formulas.
- **`tests/`** contains automated checks of the source code. Tests use small
  hand-built or synthetic inputs and confirm that metrics, labels, and the
  public audit pipeline behave as expected. They are validation code, not
  research data and not additional analyses.
- **`notebooks/`** provides readable, ordered walkthroughs. Public notebooks
  run on bundled synthetic or aggregate artifacts; `repro_deep/` documents the
  authorized private rerun and skips private computations when those inputs
  are unavailable.
- **`data/synthetic/`** contains invented toy rows for execution examples,
  while **`reports/`** contains approved aggregate tables and figure files.

In short: `src` defines the analysis, `scripts` run it, `tests` verify it, and
`notebooks` explain it.

```text
src/pecgap/
  metrics.py              PEC metrics such as Jaccard, entropy, HHI, top-share, JS divergence
  artifacts.py            Helpers for loading release-safe tables and writing figures
  preprocessing.py        Schema normalization helpers for authorized reruns
  audit_pipeline.py       Audit pipeline code for processed internal tables
  modeling.py             Diagnostic model utilities
  private_schema.py       Expected processed-table schemas

data/
  synthetic/              Toy examples and schema-compatible sample data

reports/
  tables/                 Release-safe aggregate tables used to inspect paper claims
  figures/                Final paper figures and release-safe figure exports

notebooks/
  00_release_artifact_tour.ipynb
  01_metric_walkthrough_synthetic.ipynb
  02_private_pipeline_template.ipynb
  repro_deep/             Output-stripped notebooks for authorized internal reruns

scripts/
  generate_public_synthetic_data.py
  run_public_synthetic_pipeline.py
  check_release_artifacts.py
  make_release_figures.py
  check_private_processed_data.py
  run_repro_deep_notebooks.py
  run_rq2_clustered_uncertainty.py

tests/
  test_metrics.py                 Unit checks for PEC metric definitions
  test_modeling_labels.py         Checks for diagnostic-label construction
  test_synthetic_audit_pipeline.py End-to-end check on bundled toy records

docs/
  DATA_RELEASE_POLICY.md
  REPRODUCIBILITY.md
  METRIC_GUIDE.md
  ARTIFACT_GUIDE.md

requirements.txt          Runtime dependency list
pyproject.toml             Installable package and test configuration
```

## Release-Safe Data

The public package includes:

- aggregate result tables,
- synthetic schema examples,
- a one-command synthetic PEC pipeline,
- figure-generation inputs and outputs,
- metric and modeling code,
- output-stripped notebook walkthroughs.

The public package excludes:

- timestamped raw click logs,
- user-level recommendation lists,
- row-level joined click/exposure records,
- profile snapshots for real users,
- device, session, account, or production identifiers,
- internal review notes and reference PDFs.

See [docs/DATA_RELEASE_POLICY.md](docs/DATA_RELEASE_POLICY.md) and [docs/ARTIFACT_GUIDE.md](docs/ARTIFACT_GUIDE.md).

## How This Supports the Paper

The repository supports the paper's audit claims at the level that can be released safely:

- **P-C alignment:** aggregate preference-consumption overlap summaries.
- **E-C traceability:** same-day hit, candidate-pool baseline, popularity-aware baseline, and clustered uncertainty summaries.
- **E-C diversity shift:** aggregate entropy, HHI, top-share, and Jensen-Shannon summaries.
- **Structured divergence:** aggregate diagnostic model validation and sensitivity summaries.

These artifacts allow readers to inspect the measurement definitions and reproduce public figures and tables. They do not allow reconstruction of private user histories.

The synthetic pipeline and the aggregate checks answer different questions.
The former verifies that the released code executes end to end on safe toy
records; the latter verifies the approved manuscript-facing numbers. Neither
claims to reconstruct private row-level histories.

The committed toy cohort is generated deterministically by
`scripts/generate_public_synthetic_data.py`. Regeneration never reads private
data or manuscript result tables.

## Licenses

- Code is released under the MIT License. See [LICENSE](LICENSE).
- Release-safe aggregate tables and synthetic schema examples are released under CC BY 4.0. See [DATA_LICENSE.md](DATA_LICENSE.md).
- Raw operational data are not released and are not covered by either license.

## Citation

Citation metadata for this research artifact is provided in
[CITATION.cff](CITATION.cff). The manuscript is currently under review; do not
describe it as accepted or published unless its status changes.
