# Figures

The figures directory contains paper figures and release-generated diagnostic
figures.

Main manuscript figures:

- `pec_audit_framework.png` and `pec_audit_framework.pdf`: current PEC audit
  framework used by the v101 manuscript and Overleaf package. Regenerate it
  with `scripts/build_fig1_code_native_editorial_compact_v13.py`.
- The current polished RQ figures are generated under
  `output/figure_alternatives/v42_paper_style/`:
  - `rq1_interpretive_alignment_v42.png` and `.pdf`
  - `rq2_surface_traceability_v42.png` and `.pdf`
  - `rq3_diversity_audit_v42.png` and `.pdf`
  - `rq4_bounded_signal_v42.png` and `.pdf`
- The official-template manuscript uses renamed PDF copies in
  `submission/aaai2026_official_template/pec_gap_submission_overleaf/figures/`
  as `fig14_preference_alignment_paper_v42.pdf`,
  `fig15_surface_traceability_paper_v42.pdf`,
  `fig16_diversity_audit_paper_v42.pdf`, and
  `fig17_bounded_signal_paper_v42.pdf`.

Supplementary diagnostic figures:

- `fig22_user_gap_distributions_v35.png`: user-level diversity-gap
  distributions by click-history band.
- `fig23_diagnostic_feature_importance_v35.png`: diagnostic feature-importance
  summary.

Release sanity-check figures:

- `release_popularity_baseline.png`
- `release_surface_lift.png`

Regenerate release-safe diagnostic figures with:

```bash
python scripts/make_release_figures.py
```

Regenerate the polished paper-style manuscript figures with:

```bash
python scripts/build_paper_style_figures_v42.py
```

To rebuild all five v101 figures from inline code and inspect/download the
outputs, run `notebooks/05_final_manuscript_figure_rebuild_v101.ipynb`.

The main manuscript PDF uses the polished paper figures. The release figures
provide lightweight sanity checks from aggregate tables.

For figure-by-figure review, open
`notebooks/03_paper_figure_gallery.ipynb`. It displays the manuscript figures,
appendix diagnostics, and release sanity-check figures with reading notes,
source/generation notes, and tuning guidance.
