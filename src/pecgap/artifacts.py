"""Helpers for loading release-safe aggregate artifacts."""

from __future__ import annotations

from pathlib import Path
import json

import pandas as pd


def project_root() -> Path:
    """Return the repository root from an installed or source checkout."""

    return Path(__file__).resolve().parents[2]


def table_path(name: str, root: Path | None = None) -> Path:
    base = root or project_root()
    return base / "reports" / "tables" / name


def figure_path(name: str, root: Path | None = None) -> Path:
    base = root or project_root()
    return base / "reports" / "figures" / name


def load_table(name: str, root: Path | None = None) -> pd.DataFrame:
    return pd.read_csv(table_path(name, root))


def load_json(name: str, root: Path | None = None) -> dict:
    return json.loads(table_path(name, root).read_text(encoding="utf-8"))

