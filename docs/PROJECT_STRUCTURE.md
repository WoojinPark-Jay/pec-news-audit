# Project Structure

This document maps the repository layout to the research workflow: manuscript
review, release-safe artifact checks, and authorized private reruns.

## Source Code

- `src/pecgap/metrics.py`: transparent implementations of the audit metrics.
- `src/pecgap/preprocessing.py`: processed-table readers, profile-list parsers,
  boolean normalization, and standardization for click and recommendation rows.
- `src/pecgap/audit_pipeline.py`: command-line reusable implementation of the
  PEC audit: preference-consumption alignment, exposure-consumption
  traceability, random/popularity baselines, surface lift, diversity shift,
  and count-matched checks.
- `src/pecgap/modeling.py`: bounded high-divergence diagnostic feature building,
  cross-validation, and feature-importance utilities.
- `src/pecgap/artifacts.py`: release-safe aggregate table and figure loaders.
- `src/pecgap/private_schema.py`: expected columns for authorized private reruns.

## Scripts

- `scripts/check_release_artifacts.py`: confirms aggregate artifacts are readable
  and prints paper-level values.
- `scripts/make_release_figures.py`: regenerates release-safe figures from
  aggregate tables, including the popularity baseline, surface-lift diagnostic,
  and diversity-shift audit.
- `scripts/build_working_paper_pdf.py`: generates the current working PDF,
  Markdown, and compact LaTeX handoff source from release-safe aggregate tables.
- `scripts/run_private_pipeline.py`: checks whether private processed tables are
  present and schema-compatible.
- `scripts/run_full_private_audit_pipeline.py`: reruns the PEC audit from
  approved processed tables and writes private validation CSV/JSON outputs.
- `scripts/run_diagnostic_model.py`: reruns the RQ4 high-divergence diagnostic
  models from processed tables and writes private model validation outputs.

## Notebooks

- `00_release_artifact_tour.ipynb`: walks through paper artifacts and values.
- `01_metric_walkthrough_synthetic.ipynb`: explains the PEC metrics on synthetic data.
- `02_private_pipeline_template.ipynb`: shows the full rerun path for authorized private data.
- `03_paper_figure_gallery.ipynb`: reviews all paper/supporting figures with
  interpretation notes and visual tuning guidance.
- `repro_deep/`: output-stripped authorized rerun notebooks for EDA,
  preprocessing, PEC metrics, weighted preferences, surfaces, modeling, and
  artifact handoff.
- `repro_full_pipeline/`: one-pass authorized private rerun notebook.

## Reports

`reports/tables/` contains aggregate tables only. It intentionally excludes
user-level feature tables and timestamped traces.

`reports/figures/` contains paper figures and release-generated figures.

## Study Guides

- `docs/ENGLISH_KEY_TERMS_AND_SENTENCE_GUIDE.md`: English guide explaining the
  paper's key terms, major sentences, and global-audience framing.
- `docs/KOREAN_KEY_TERMS_AND_SENTENCE_GUIDE.md`: Korean guide explaining the
  paper's key terms, major sentences, and claim boundaries.
- `docs/METHODS_FORMULAS_TEACHING_GUIDE.md`: study notes for the PEC formulas,
  statistical checks, model diagnostics, and result interpretation.
- `docs/METHODS_FORMULAS_TEACHING_GUIDE.html`: browser-rendered companion to the
  English formula guide with MathJax equation rendering.
- `docs/METHODS_FORMULAS_TEACHING_GUIDE_KO.md`: Korean study notes for the PEC
  formulas, statistical checks, model diagnostics, and result interpretation.
- `docs/METHODS_FORMULAS_TEACHING_GUIDE_KO.html`: browser-rendered companion to
  the Korean formula guide with MathJax equation rendering.
- `docs/REFERENCE_EVIDENCE_AND_USAGE_GUIDE.md`: explanation of how each cited
  paper supports specific manuscript claims and interpretation boundaries.
- `docs/REFERENCE_EVIDENCE_AND_USAGE_GUIDE_KO.md`: Korean explanation of how
  each cited paper supports manuscript claims and interpretation boundaries.
- `docs/REFERENCE_DEEP_READING_NOTES_KO.md`: detailed Korean paper-by-paper
  reading notes explaining each cited work, the evidence borrowed from it, the
  manuscript claim it supports, and the claim boundary it should not exceed.
- `docs/COLLABORATOR_ONBOARDING.md`: recommended reading and execution path for
  new collaborators.
- `docs/REPOSITORY_QUALITY_CHECKLIST.md`: checks before collaboration,
  submission, or public release.

## Governance and Release Docs

- `CONTRIBUTING.md`: contribution rules, pull request expectations, notebook
  policy, and data boundary.
- `SECURITY.md`: sensitive artifact policy and response procedure.
- `.github/pull_request_template.md`: repository review checklist for pull
  requests.
- `docs/DATA_RELEASE_POLICY.md`: public/private data boundary.
- `docs/GITHUB_RELEASE_GUIDE.md`: GitHub setup and pre-release checks.
- `docs/REPRODUCIBILITY.md`: release-safe and authorized-private reproduction
  modes.
- `docs/NOTEBOOK_EXECUTION_AUDIT.md`: notebook execution status.
- `docs/REFERENCE_AUDIT.md` and `docs/REFERENCE_USAGE_AUDIT_V48.md`: reference
  metadata and citation-use checks.

## Paper

`paper/` contains the current blind PDF, compact LaTeX handoff, and full
Markdown manuscript. The active files keep the historical `v47` filename as a
stable path for scripts and notebooks, but they contain the latest pushed
manuscript, figure, checklist, and reference-polish updates. The final
submission package lives under `submission/aaai2026_official_template/` and
should still be visually checked after Overleaf compilation.
