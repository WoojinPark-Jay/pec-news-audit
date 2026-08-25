from pathlib import Path

from pecgap.audit_pipeline import run_pec_audit


ROOT = Path(__file__).resolve().parents[1]


def test_synthetic_pipeline_writes_release_safe_outputs(tmp_path: Path) -> None:
    results = run_pec_audit(ROOT / "data" / "synthetic", output_dir=tmp_path, seed=17)

    summary = results["summary"]
    assert summary["users_with_profile_and_clicks"] > 0
    assert summary["click_events"] > 0
    assert summary["users_with_exposure_and_clicks"] > 0

    expected = {
        "alignment.csv",
        "click_traceability.csv",
        "date_matched_random_baseline.csv",
        "popularity_aware_baseline.csv",
        "topk_traceability.csv",
        "surface_traceability.csv",
        "diversity_audit.csv",
        "summary.json",
    }
    assert expected.issubset({path.name for path in tmp_path.iterdir()})

    alignment = results["alignment"]
    assert alignment["user_id"].str.fullmatch(r"u\d{3}").all()
