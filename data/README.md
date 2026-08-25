# Data Directory

The data directory is split into two intended zones:

- `synthetic/`: safe toy examples committed to the repository.
- `processed/`: private processed platform tables, ignored by git.

Do not commit raw or row-level operational logs.

The committed synthetic CSVs use toy identifiers such as `u001`, `n001`, and
`p1`. They are generated examples, not transformed or sampled platform rows.
They can be regenerated deterministically without any private input:

```bash
python scripts/generate_public_synthetic_data.py
```

Run them through the public audit code with:

```bash
python scripts/run_public_synthetic_pipeline.py
```

Synthetic outputs are written under `tmp/public_synthetic_run/` and must not be
interpreted as the paper's empirical estimates.
