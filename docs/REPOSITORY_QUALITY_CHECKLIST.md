# Repository Quality Checklist

Use this checklist before inviting collaborators, submitting the artifact, or
making any part of the repository public.

## Before Inviting Collaborators

- [ ] `README.md` points to the current manuscript, figure gallery, and metric
      guide.
- [ ] `docs/COLLABORATOR_ONBOARDING.md` describes the review path.
- [ ] `CONTRIBUTING.md` explains the data boundary and pull request process.
- [ ] `SECURITY.md` explains how to handle accidental private-data exposure.
- [ ] `.github/pull_request_template.md` is present.
- [ ] No private data files are tracked by Git.

## Before Manuscript Submission

- [ ] The manuscript PDF and Markdown refer to the same version.
- [ ] Main figures are visually checked in the PDF.
- [ ] Appendix tables are not split awkwardly across pages.
- [ ] References are author-year style and checked against the audit document.
- [ ] `docs/REFERENCE_USAGE_AUDIT_V48.md` maps each reference to manuscript use.
- [ ] Checklist, ethics, and data-availability text match the current claims.

## Before Public Release

- [ ] Run `python scripts/check_release_artifacts.py`.
- [ ] Run `python scripts/make_release_figures.py` if figures changed.
- [ ] Run `git status --short --ignored` and inspect ignored private folders.
- [ ] Run `git ls-files | rg "data/(raw|processed|private)|email|password|secret|token|credential"`.
- [ ] Confirm only synthetic examples include toy user identifiers.
- [ ] Confirm `data/raw/`, `data/processed/`, and `data/private/` are absent
      from tracked files.
- [ ] Confirm notebook outputs do not expose private row-level data.
- [ ] Replace the citation placeholder after a preprint or proceedings citation
      is available.

## Good Repository Hygiene

- Keep code under `src/` and executable workflows under `scripts/`.
- Keep paper-supporting aggregate outputs under `reports/tables/`.
- Keep paper and supporting figures under `reports/figures/`.
- Keep research explanations under `docs/`.
- Keep public walkthrough notebooks separate from authorized private rerun
  notebooks.
