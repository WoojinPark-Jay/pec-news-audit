#!/usr/bin/env python3
"""Check whether a folder contains the private processed CSVs needed for rerun.

This script is read-only. It does not write, move, copy, or modify data.
"""

from __future__ import annotations

import argparse
from pathlib import Path

REQUIRED = {
    "user_profiles_clean.csv": [
        "user_id",
        "interested_categories_user_selection",
        "interested_categories",
        "preferred_news_sources_user_selection",
        "preferred_news_sources",
    ],
    "behavior_events_dedup.csv": [
        "user_id",
        "event_name",
        "event_dt_kst",
        "event_date",
        "news_id",
        "firebase_screen",
    ],
    "click_events_enriched.csv": [
        "user_id",
        "event_date_iso",
        "news_id",
        "news_matched",
        "category_final",
        "publisher_id_final",
    ],
    "recommendation_items_enriched.csv": [
        "user_id",
        "recommendation_date",
        "news_id",
        "rank",
        "news_matched",
        "category",
        "publisher_id",
    ],
    "news_master.csv": [
        "news_id",
        "publisher_id",
        "category",
        "publisher_category",
        "language",
        "published_at",
    ],
}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--data-dir",
        type=Path,
        required=True,
        help="Directory expected to contain the private processed CSV files.",
    )
    args = parser.parse_args()

    data_dir = args.data_dir.expanduser().resolve()
    print(f"Checking private processed data directory: {data_dir}")
    print("This script is read-only; it will not change manuscript outputs.\n")

    if not data_dir.exists():
        print("ERROR: directory does not exist.")
        return 2
    if not data_dir.is_dir():
        print("ERROR: path exists but is not a directory.")
        return 2

    missing = []
    for filename in REQUIRED:
        path = data_dir / filename
        if path.exists():
            size_mb = path.stat().st_size / (1024 * 1024)
            print(f"OK      {filename:40s} {size_mb:9.2f} MB")
        else:
            print(f"MISSING {filename}")
            missing.append(filename)

    if missing:
        print("\nMissing files:")
        for filename in missing:
            print(f"- {filename}")
        return 1

    print("\nAll required private processed CSVs are present.")
    print("To use this folder without copying data into the repo, launch Jupyter with:")
    print(f'export PEC_GAP_PROCESSED_DIR="{data_dir}"')
    print("\nFor a no-impact script rerun, write outputs to /tmp, for example:")
    print(
        "python scripts/run_full_private_audit_pipeline.py "
        f'--data-dir "{data_dir}" --output-dir /tmp/pecgap_private_audit'
    )
    print(
        "python scripts/run_diagnostic_model.py "
        f'--data-dir "{data_dir}" --output-dir /tmp/pecgap_private_model'
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
