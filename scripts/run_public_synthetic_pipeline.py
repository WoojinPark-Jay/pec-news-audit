#!/usr/bin/env python3
"""Run the public PEC audit path on deterministic synthetic records.

This command exercises the same preprocessing, metric, traceability,
diversity, and diagnostic-model modules used by authorized reruns. It does not
reproduce the manuscript estimates because the bundled records are synthetic.
All generated files are written under an ignored scratch directory by default.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from pecgap.audit_pipeline import run_pec_audit  # noqa: E402
from pecgap.modeling import build_user_feature_table, run_diagnostic_models  # noqa: E402


def display_path(path: Path) -> str:
    """Return a stable repository-relative path when possible."""

    resolved = path.resolve()
    try:
        return resolved.relative_to(ROOT).as_posix()
    except ValueError:
        return str(resolved)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run the release-safe PEC pipeline on bundled synthetic data."
    )
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=ROOT / "data" / "synthetic",
        help="Schema-compatible synthetic input directory.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=ROOT / "tmp" / "public_synthetic_run",
        help="Scratch output directory. The default is ignored by Git.",
    )
    parser.add_argument("--seed", type=int, default=17)
    args = parser.parse_args()

    data_dir = args.data_dir.expanduser().resolve()
    output_dir = args.output_dir.expanduser().resolve()
    audit_dir = output_dir / "audit"
    model_dir = output_dir / "model"
    model_dir.mkdir(parents=True, exist_ok=True)

    print("PEC public synthetic pipeline")
    print("=" * 36)
    print(f"Input:  {display_path(data_dir)}")
    print(f"Output: {display_path(output_dir)}")
    print("Mode:   synthetic demonstration; not manuscript-estimate reproduction\n")

    results = run_pec_audit(
        data_dir,
        output_dir=audit_dir,
        seed=args.seed,
        progress=print,
    )

    feature_table = build_user_feature_table(
        results["alignment"],
        results["diversity_audit"],
        results["click_traceability"],
    )
    model_result = run_diagnostic_models(feature_table, seed=args.seed)
    model_result.feature_table.to_csv(model_dir / "synthetic_user_features.csv", index=False)
    model_result.cv_results.to_csv(model_dir / "synthetic_model_cv.csv", index=False)
    model_result.feature_importance.to_csv(
        model_dir / "synthetic_feature_importance.csv", index=False
    )

    model_status = "completed"
    if not model_result.cv_results.empty and "reason" in model_result.cv_results.columns:
        model_status = "skipped_on_tiny_synthetic_cohort"

    manifest = {
        "artifact_mode": "public_synthetic_demo",
        "contains_real_user_data": False,
        "reproduces_manuscript_estimates": False,
        "input_directory": display_path(data_dir),
        "output_directory": display_path(output_dir),
        "seed": args.seed,
        "model_status": model_status,
        "input_rows": {
            "profiles": int(results["summary"]["users_with_profile_and_clicks"]),
            "clicks": int(results["summary"]["click_events"]),
            "exposure_click_users": int(
                results["summary"]["users_with_exposure_and_clicks"]
            ),
        },
        "outputs": {
            "audit": "audit/",
            "model": "model/",
        },
    }
    (output_dir / "RUN_MANIFEST.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )

    print("\nSynthetic audit summary")
    print(json.dumps(results["summary"], indent=2))
    if model_status != "completed":
        reason = model_result.cv_results.iloc[0].get("reason", "small synthetic sample")
        print(
            "\nRQ4 model validation was intentionally skipped because the bundled "
            f"toy cohort is too small ({reason}). The feature-construction path ran "
            "and its synthetic output was saved."
        )
    else:
        print(
            "\nRQ4 model validation completed on the engineered toy cohort. "
            "Its scores verify execution only and are not empirical performance claims."
        )
    print(f"\nOK: release-safe outputs written to {display_path(output_dir)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
