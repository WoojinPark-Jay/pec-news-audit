# PEC News Audit

Release artifacts for the manuscript:

**When Exposure Is Not Attention: Auditing the Preference-Exposure-Consumption Gap in Personalized News Recommenders**

This repository accompanies a measurement audit of a deployed mobile news recommender. The paper separates four platform traces:

- **Preference (P):** stated preferences and observed profile-state distributions.
- **Exposure (E):** logged recommendation lists.
- **Surface pathways (S):** app entry paths such as headline, category, home/feed, newsroom, article detail, search, and notifications.
- **Consumption (C):** observed article clicks.

The main purpose of this repository is to make the public parts of the audit inspectable without releasing private user-level logs. It provides metric code, aggregate result tables, figure artifacts, release-safe notebooks, and synthetic schemas. Raw operational logs, row-level recommendation lists, user click histories, profile snapshots, and production identifiers are not included.

## What You Can Do With This Repository

1. Inspect the definitions behind the PEC audit metrics.
2. Rebuild release-safe figures and tables from aggregate artifacts.
3. Run synthetic examples that mirror the schema of the private platform logs.
4. Check that the published aggregate claims are internally consistent.
5. Understand which claims are supported by available traces and which claims remain outside the observability boundary.

This repository is not a public benchmark dataset and does not contain behavioral traces from real users.

## Quick Start

Create an environment:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
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

## Repository Map

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
  check_release_artifacts.py
  make_release_figures.py
  check_private_processed_data.py
  run_repro_deep_notebooks.py
  run_rq2_clustered_uncertainty.py

docs/
  DATA_RELEASE_POLICY.md
  REPRODUCIBILITY.md
  METRIC_GUIDE.md
  ARTIFACT_GUIDE.md
```

## Release-Safe Data

The public package includes:

- aggregate result tables,
- synthetic schema examples,
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

## Licenses

- Code is released under the MIT License. See [LICENSE](LICENSE).
- Release-safe aggregate tables and synthetic schema examples are released under CC BY 4.0. See [DATA_LICENSE.md](DATA_LICENSE.md).
- Raw operational data are not released and are not covered by either license.

## Citation

Please cite the associated manuscript once a preprint, proceedings version, or accepted citation is available. A placeholder citation file is provided in [CITATION.cff](CITATION.cff).
