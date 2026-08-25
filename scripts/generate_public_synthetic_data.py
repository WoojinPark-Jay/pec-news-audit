#!/usr/bin/env python3
"""Generate deterministic, schema-compatible toy inputs for the public demo.

Every identifier and event produced here is artificial. The generator does not
read private files, aggregate tables, or manuscript outputs.
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CATEGORIES = ["politics", "economy", "society", "sports", "technology", "culture"]
SURFACES = ["headline", "category", "home/feed", "newsroom", "article-detail"]


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def build_rows(user_count: int = 24) -> dict[str, list[dict[str, object]]]:
    news_rows: list[dict[str, object]] = []
    news_by_category: dict[str, list[dict[str, object]]] = {category: [] for category in CATEGORIES}
    for category_index, category in enumerate(CATEGORIES):
        publisher = f"p{category_index + 1}"
        for item_index in range(4):
            news_id = f"n{category_index * 4 + item_index + 1:03d}"
            row = {
                "news_id": news_id,
                "publisher_id": publisher,
                "category": category,
                "publisher_category": category,
                "language": "en",
                "published_at": f"2026-01-{item_index + 3:02d} 08:00:00",
                "headline_flag": str(item_index == 0).lower(),
                "is_breaking": str(item_index == 1).lower(),
            }
            news_rows.append(row)
            news_by_category[category].append(row)

    profile_rows: list[dict[str, object]] = []
    click_rows: list[dict[str, object]] = []
    exposure_rows: list[dict[str, object]] = []

    for user_index in range(user_count):
        user_id = f"u{user_index + 1:03d}"
        date = f"2026-01-{user_index % 4 + 3:02d}"
        first_pref = CATEGORIES[user_index % len(CATEGORIES)]
        second_pref = CATEGORIES[(user_index + 1) % len(CATEGORIES)]
        pref_categories = [first_pref, second_pref]
        pref_publishers = [
            news_by_category[first_pref][0]["publisher_id"],
            news_by_category[second_pref][0]["publisher_id"],
        ]
        profile_rows.append(
            {
                "user_id": user_id,
                "interested_categories_user_selection": json.dumps(pref_categories),
                "preferred_news_sources_user_selection": json.dumps(pref_publishers),
                "tier": "PREMIUM" if user_index % 3 == 0 else "BASIC",
                "platform": "ios" if user_index % 2 == 0 else "android",
                "preferred_language": "en",
            }
        )

        high_divergence = user_index % 2 == 1
        if high_divergence:
            click_categories = [
                CATEGORIES[(user_index + 3) % len(CATEGORIES)],
                CATEGORIES[(user_index + 4) % len(CATEGORIES)],
            ]
        else:
            click_categories = pref_categories

        clicked_items: list[dict[str, object]] = []
        click_count = 3 + user_index % 3
        for click_index in range(click_count):
            category = click_categories[click_index % len(click_categories)]
            item = news_by_category[category][(user_index + click_index) % 4]
            clicked_items.append(item)
            click_rows.append(
                {
                    "user_id": user_id,
                    "event_date_iso": date,
                    "news_id": item["news_id"],
                    "news_matched": "true",
                    "category_final": item["category"],
                    "publisher_id_final": item["publisher_id"],
                    "surface": SURFACES[(user_index + click_index) % len(SURFACES)],
                }
            )

        list_size = 5 + user_index % 3
        recommendation_items: list[dict[str, object]] = []
        if user_index % 3 != 0:
            recommendation_items.append(clicked_items[0])
        candidate_offset = 0
        while len(recommendation_items) < list_size:
            category = CATEGORIES[(user_index + candidate_offset) % len(CATEGORIES)]
            item = news_by_category[category][(user_index + candidate_offset) % 4]
            if item["news_id"] not in {row["news_id"] for row in recommendation_items}:
                recommendation_items.append(item)
            candidate_offset += 1

        for rank, item in enumerate(recommendation_items, start=1):
            exposure_rows.append(
                {
                    "user_id": user_id,
                    "recommendation_date": date,
                    "news_id": item["news_id"],
                    "rank": rank,
                    "news_matched": "true",
                    "category": item["category"],
                    "publisher_id": item["publisher_id"],
                }
            )

    return {
        "news": news_rows,
        "profiles": profile_rows,
        "clicks": click_rows,
        "exposures": exposure_rows,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate public PEC toy CSVs.")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=ROOT / "data" / "synthetic",
        help="Destination for generated toy CSV files.",
    )
    parser.add_argument("--users", type=int, default=24)
    args = parser.parse_args()
    if args.users < 12:
        parser.error("--users must be at least 12 so the RQ4 demo has both classes.")

    output_dir = args.output_dir.expanduser().resolve()
    rows = build_rows(args.users)
    write_csv(
        output_dir / "news_master.csv",
        [
            "news_id",
            "publisher_id",
            "category",
            "publisher_category",
            "language",
            "published_at",
            "headline_flag",
            "is_breaking",
        ],
        rows["news"],
    )
    write_csv(
        output_dir / "user_profiles_clean.csv",
        [
            "user_id",
            "interested_categories_user_selection",
            "preferred_news_sources_user_selection",
            "tier",
            "platform",
            "preferred_language",
        ],
        rows["profiles"],
    )
    write_csv(
        output_dir / "click_events_enriched.csv",
        [
            "user_id",
            "event_date_iso",
            "news_id",
            "news_matched",
            "category_final",
            "publisher_id_final",
            "surface",
        ],
        rows["clicks"],
    )
    write_csv(
        output_dir / "recommendation_items_enriched.csv",
        [
            "user_id",
            "recommendation_date",
            "news_id",
            "rank",
            "news_matched",
            "category",
            "publisher_id",
        ],
        rows["exposures"],
    )

    manifest = {
        "data_mode": "deterministic_synthetic",
        "contains_real_user_data": False,
        "generator": "scripts/generate_public_synthetic_data.py",
        "users": len(rows["profiles"]),
        "clicks": len(rows["clicks"]),
        "recommendation_items": len(rows["exposures"]),
        "news_items": len(rows["news"]),
    }
    (output_dir / "SYNTHETIC_DATA_MANIFEST.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(manifest, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
