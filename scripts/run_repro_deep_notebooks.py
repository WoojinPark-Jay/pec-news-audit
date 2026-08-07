#!/usr/bin/env python3
"""Execute the authorized repro_deep notebooks in order.

This runner is intentionally simple: it executes code cells in each notebook
with a shared namespace per notebook, prints progress, and leaves each
notebook's own scratch-save cell to write outputs under tmp/repro_deep/.

It does not write to reports/tables, reports/figures, or Overleaf.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import traceback
from pathlib import Path


DEFAULT_NOTEBOOKS = [
    "00_data_eda_and_schema.ipynb",
    "01_preprocessing_and_joining.ipynb",
    "02_pec_metrics_and_statistics.ipynb",
    "03_weighted_preferences_and_surface_paths.ipynb",
    "04_modeling_rq4_from_features.ipynb",
    "05_paper_handoff_and_artifacts.ipynb",
]


def ensure_scientific_runtime() -> None:
    """Re-exec with the bundled fallback Python when the active Python lacks numpy/pandas."""
    try:
        import numpy  # noqa: F401
        import pandas  # noqa: F401
        return
    except ModuleNotFoundError:
        bundled = (
            Path.home()
            / ".cache"
            / "codex-runtimes"
            / "codex-primary-runtime"
            / "dependencies"
            / "python"
            / "bin"
            / "python3"
        )
        if bundled.exists() and Path(sys.executable).resolve() != bundled.resolve():
            print(f"Active Python lacks numpy/pandas; re-running with bundled runtime: {bundled}", flush=True)
            os.execv(str(bundled), [str(bundled), *sys.argv])
        raise


def find_repo_root() -> Path:
    for candidate in [Path.cwd(), *Path.cwd().parents]:
        if (candidate / "scripts").exists() and (candidate / "notebooks").exists():
            return candidate.resolve()
    return Path(__file__).resolve().parents[1]


def execute_notebook(path: Path) -> bool:
    print(f"\n=== RUN {path.name} ===", flush=True)
    nb = json.loads(path.read_text(encoding="utf-8"))
    namespace = {"__name__": "__main__"}
    for index, cell in enumerate(nb.get("cells", []), 1):
        if cell.get("cell_type") != "code":
            continue
        source = cell.get("source", "")
        code = "".join(source) if isinstance(source, list) else str(source)
        if not code.strip():
            continue
        try:
            exec(compile(code, str(path) + f":cell{index}", "exec"), namespace)
        except Exception as exc:  # pragma: no cover - this is a diagnostic runner
            print(f"FAIL {path.name} cell {index}: {type(exc).__name__}: {exc}", flush=True)
            traceback.print_exc(limit=4)
            print(f"=== DONE {path.name}: FAIL ===", flush=True)
            return False
    print(f"=== DONE {path.name}: OK ===", flush=True)
    return True


def main() -> int:
    ensure_scientific_runtime()

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--notebook",
        action="append",
        help="Run only the named notebook file under notebooks/repro_deep/. May be repeated.",
    )
    args = parser.parse_args()

    root = find_repo_root()
    os.environ.setdefault("MPLCONFIGDIR", "/tmp/pecgap_mpl")
    notebook_dir = root / "notebooks" / "repro_deep"
    names = args.notebook or DEFAULT_NOTEBOOKS

    results: list[tuple[str, bool]] = []
    for name in names:
        path = notebook_dir / name
        if not path.exists():
            print(f"MISSING {path}", flush=True)
            results.append((name, False))
            continue
        results.append((name, execute_notebook(path)))

    print("\nSUMMARY")
    for name, ok in results:
        print(f"{name}\t{'OK' if ok else 'FAIL'}")

    return 0 if all(ok for _, ok in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
