"""Preprocessing helpers for authorized PEC audit reruns.

The public repository does not ship private row-level logs. These helpers
document how approved processed tables are normalized before computing the
Preference-Exposure-Consumption audit quantities.
"""

from __future__ import annotations

import ast
import json
from pathlib import Path
from typing import Any

import pandas as pd


def parse_list_cell(value: Any) -> list[str]:
    """Parse a list-like CSV cell into cleaned string labels.

    Private processed tables may store profile selections as JSON arrays,
    Python-list strings, pipe-separated strings, comma-separated strings, or
    empty cells. This parser keeps the downstream metric code independent of
    that storage detail.
    """

    if value is None or pd.isna(value):
        return []
    if isinstance(value, list | tuple | set):
        raw_values = list(value)
    else:
        text = str(value).strip()
        if not text or text.lower() in {"nan", "none", "null", "[]"}:
            return []
        raw_values: list[Any]
        try:
            parsed = json.loads(text)
            if isinstance(parsed, dict):
                raw_values = list(parsed.keys())
            else:
                raw_values = parsed if isinstance(parsed, list) else [parsed]
        except Exception:
            try:
                parsed = ast.literal_eval(text)
                if isinstance(parsed, dict):
                    raw_values = list(parsed.keys())
                else:
                    raw_values = parsed if isinstance(parsed, list | tuple | set) else [parsed]
            except Exception:
                delimiter = "|" if "|" in text else ","
                raw_values = text.split(delimiter)

    cleaned = []
    for item in raw_values:
        label = str(item).strip().strip("\"'")
        if label:
            cleaned.append(label)
    return cleaned


def normalize_bool_series(series: pd.Series) -> pd.Series:
    """Return a boolean Series from common CSV boolean encodings."""

    if series.dtype == bool:
        return series.fillna(False)
    return (
        series.astype(str)
        .str.strip()
        .str.lower()
        .isin({"true", "1", "yes", "y", "t"})
    )


def _first_existing(row: pd.Series, columns: list[str]) -> Any:
    for column in columns:
        if column in row.index and not pd.isna(row[column]):
            value = row[column]
            if str(value).strip():
                return value
    return None


def read_csv_table(data_dir: Path, filename: str, *, nrows: int | None = None) -> pd.DataFrame:
    """Read a processed CSV table from a data directory."""

    path = data_dir / filename
    if not path.exists():
        raise FileNotFoundError(f"Missing required table: {path}")
    return pd.read_csv(path, nrows=nrows, low_memory=False)


def normalize_id_value(value: Any) -> str:
    """Normalize item/user identifiers that may arrive as int, float, or string."""

    if value is None or pd.isna(value):
        return ""
    text = str(value).strip()
    if text.endswith(".0"):
        text = text[:-2]
    return text


def derive_surface(row: pd.Series) -> str:
    """Derive a coarse app-surface label from available click metadata."""

    for column in ["surface", "surface_final", "surface_group"]:
        if column in row.index and not pd.isna(row[column]) and str(row[column]).strip():
            return str(row[column]).strip()

    screen = str(row.get("firebase_screen", "")).strip().lower()
    source = str(row.get("p_source", "")).strip().lower()
    section = str(row.get("section", "")).strip().lower()
    is_headline = str(row.get("is_headline", "")).strip().lower() in {"true", "1", "yes"}

    if "newsroom" in screen or "newsroom" in source:
        return "newsroom"
    if "podcast" in screen or "podcast" in source:
        return "podcast"
    if "headline" in section or is_headline:
        return "headline"
    if section.startswith("category_") or screen in {"topicdetail", "issuedetail"}:
        return "category"
    if "detail" in screen:
        return "article-detail"
    if source == "home" or screen == "newshome":
        return "home/feed"
    if source:
        return source
    if screen:
        return screen
    return "unknown"


def load_processed_tables(data_dir: Path) -> dict[str, pd.DataFrame]:
    """Load the processed tables required for the core PEC audit."""

    required = {
        "profiles": "user_profiles_clean.csv",
        "clicks": "click_events_enriched.csv",
        "exposures": "recommendation_items_enriched.csv",
    }
    tables = {name: read_csv_table(data_dir, filename) for name, filename in required.items()}
    news_path = data_dir / "news_master.csv"
    if news_path.exists():
        tables["news"] = pd.read_csv(news_path)
    return tables


def profile_preference_table(profiles: pd.DataFrame) -> pd.DataFrame:
    """Normalize user preference/profile columns for P-layer metrics."""

    rows = []
    for _, row in profiles.iterrows():
        categories = parse_list_cell(
            _first_existing(row, ["interested_categories_user_selection", "interested_categories"])
        )
        publishers = parse_list_cell(
            _first_existing(row, ["preferred_news_sources_user_selection", "preferred_news_sources"])
        )
        rows.append(
            {
                "user_id": row["user_id"],
                "pref_categories": categories,
                "pref_publishers": publishers,
                "n_pref_categories": len(categories),
                "n_pref_publishers": len(publishers),
            }
        )
    return pd.DataFrame(rows)


def standardize_clicks(clicks: pd.DataFrame) -> pd.DataFrame:
    """Normalize click-consumption rows used by the C and S layers."""

    out = clicks.copy()
    if "news_matched" in out.columns:
        out = out[normalize_bool_series(out["news_matched"])].copy()
    rename = {
        "event_date_iso": "date",
        "category_final": "category",
        "publisher_id_final": "publisher_id",
    }
    out = out.rename(columns={k: v for k, v in rename.items() if k in out.columns})
    if "date" not in out.columns and "event_date" in out.columns:
        out["date"] = out["event_date"]
    if "surface" not in out.columns:
        out["surface"] = out.apply(derive_surface, axis=1)
    required = ["user_id", "date", "news_id", "category", "publisher_id", "surface"]
    missing = [column for column in required if column not in out.columns]
    if missing:
        raise ValueError(f"Click table is missing normalized columns: {missing}")
    out["date"] = pd.to_datetime(out["date"]).dt.date.astype(str)
    out["user_id"] = out["user_id"].map(normalize_id_value)
    out["news_id"] = out["news_id"].map(normalize_id_value)
    return out[required].copy()


def standardize_exposures(exposures: pd.DataFrame) -> pd.DataFrame:
    """Normalize recommendation exposure rows used by the E layer."""

    out = exposures.copy()
    if "news_matched" in out.columns:
        out = out[normalize_bool_series(out["news_matched"])].copy()
    rename = {"recommendation_date": "date"}
    out = out.rename(columns={k: v for k, v in rename.items() if k in out.columns})
    if "rank" not in out.columns:
        out["rank"] = 1
    required = ["user_id", "date", "news_id", "rank", "category", "publisher_id"]
    missing = [column for column in required if column not in out.columns]
    if missing:
        raise ValueError(f"Recommendation table is missing normalized columns: {missing}")
    out["date"] = pd.to_datetime(out["date"]).dt.date.astype(str)
    out["rank"] = pd.to_numeric(out["rank"], errors="coerce")
    out["user_id"] = out["user_id"].map(normalize_id_value)
    out["news_id"] = out["news_id"].map(normalize_id_value)
    return out[required].copy()
