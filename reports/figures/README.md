# Figures

This directory contains final manuscript figures and release-safe diagnostic
figures.

## Main Manuscript Figures

- `pec_audit_framework.pdf` and `.png`: PEC audit framework.
- `fig14_preference_alignment_paper_v42.pdf`: preference-consumption alignment.
- `fig15_surface_traceability_paper_v42.pdf`: multi-surface traceability.
- `fig16_diversity_audit_paper_v42.pdf`: diversity and concentration audit.
- `fig17_bounded_signal_paper_v42.pdf`: diagnostic model audit.

## Release-Safe Diagnostic Figures

- `release_popularity_baseline.png`
- `release_surface_lift.png`
- `fig15_surface_traceability_liftplot_v37.pdf`
- `fig16_diversity_audit_v46.pdf`
- `fig17_bounded_audit_signal_native_plotly_v21.pdf`

Regenerate release-safe diagnostic figures with:

```bash
python scripts/make_release_figures.py
```

The release-generated figures use aggregate tables and do not require raw or
row-level operational logs.
