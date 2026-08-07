"""Expected private processed-table schemas.

These schemas document the columns consumed by the full private pipeline.
They are deliberately separated from the release-safe aggregate artifacts.
"""

PRIVATE_TABLES: dict[str, list[str]] = {
    "user_profiles_clean.csv": [
        "user_id",
        "interested_categories_user_selection",
        "interested_categories",
        "preferred_news_sources_user_selection",
        "preferred_news_sources",
        "tier",
        "platform",
        "preferred_language",
    ],
    "behavior_events_dedup.csv": [
        "user_id",
        "event_name",
        "event_dt_kst",
        "event_date",
        "news_id",
        "firebase_screen",
        "message_type",
        "p_source",
        "section",
        "is_headline",
        "position",
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
        "headline_flag",
        "is_breaking",
    ],
}


def missing_columns(table_name: str, columns: list[str]) -> list[str]:
    """Return required columns absent from a concrete table."""

    required = PRIVATE_TABLES.get(table_name, [])
    return [col for col in required if col not in columns]
