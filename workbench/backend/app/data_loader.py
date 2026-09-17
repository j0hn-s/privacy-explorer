"""Load T0-T4 reference data from the repo's /data/*.yaml at request time.

Files are read on each call so workshop participants can edit YAML on the host
and see the change without restarting the backend.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import yaml


DATA_FILES = {
    "exposure_problems": "exposure_problems.yaml",
    "primitives": "primitives.yaml",
    "pairings": "pairings.yaml",
    "stacks": "stacks.yaml",
    "sectors": "sectors.yaml",
}


def load_yaml(repo_root: Path, key: str) -> dict:
    """Load one of the T0-T4 YAML files from /repo/data/.

    Raises KeyError if `key` is not one of the recognised reference files.
    Raises FileNotFoundError if the YAML file is missing on disk.
    """
    if key not in DATA_FILES:
        raise KeyError(f"Unknown reference key: {key!r}. Expected one of {list(DATA_FILES)}.")
    path = repo_root / "data" / DATA_FILES[key]
    if not path.exists():
        raise FileNotFoundError(f"Reference file not found: {path}")
    return yaml.safe_load(path.read_text())


def load_rules(repo_root: Path) -> list[dict]:
    """Load the canonical rules.yaml — list-typed for compatibility with the engine."""
    path = repo_root / "yaps" / "rules" / "rules.yaml"
    if not path.exists():
        raise FileNotFoundError(f"Rules file not found: {path}")
    raw = yaml.safe_load(path.read_text())
    return raw.get("rules") or []


@lru_cache(maxsize=8)
def _cached_load(repo_root_str: str, key: str, mtime_ns: int) -> dict:
    """Cache key includes mtime so edits invalidate naturally."""
    return load_yaml(Path(repo_root_str), key)


def load_with_mtime_cache(repo_root: Path, key: str) -> dict:
    """Like load_yaml but cached by mtime so repeated reads in a single request
    cycle do not re-parse YAML. Across requests, an edit on disk invalidates."""
    path = repo_root / "data" / DATA_FILES[key]
    mtime_ns = path.stat().st_mtime_ns if path.exists() else 0
    return _cached_load(str(repo_root), key, mtime_ns)
