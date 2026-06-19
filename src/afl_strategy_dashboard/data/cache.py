"""Small CSV-based cache helpers for API and processed data."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"


def ensure_cache_dirs() -> None:
    """Create cache directories if they do not already exist."""
    RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)


def cache_path(name: str, layer: str = "raw", suffix: str = ".csv") -> Path:
    """Return a project-local cache path.

    Parameters
    ----------
    name:
        File stem or file name.
    layer:
        Either `raw` or `processed`.
    suffix:
        File suffix to use when `name` has no suffix.
    """
    ensure_cache_dirs()
    base_dir = RAW_DATA_DIR if layer == "raw" else PROCESSED_DATA_DIR
    path = base_dir / name
    if not path.suffix:
        path = path.with_suffix(suffix)
    return path


def read_dataframe(name: str, layer: str = "raw") -> pd.DataFrame | None:
    """Read a cached DataFrame if present."""
    path = cache_path(name, layer=layer)
    if not path.exists():
        return None
    return pd.read_csv(path)


def write_dataframe(df: pd.DataFrame, name: str, layer: str = "raw") -> Path:
    """Write a DataFrame to cache and return the written path."""
    path = cache_path(name, layer=layer)
    df.to_csv(path, index=False)
    return path


def get_or_create_dataframe(
    name: str,
    fetcher,
    *,
    layer: str = "raw",
    refresh: bool = False,
) -> pd.DataFrame:
    """Return cached data unless refresh is requested, otherwise call fetcher."""
    if not refresh:
        cached = read_dataframe(name, layer=layer)
        if cached is not None:
            return cached

    df = fetcher()
    write_dataframe(df, name, layer=layer)
    return df
