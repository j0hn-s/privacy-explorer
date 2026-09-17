"""GET T0-T4 reference data. Read at request time from /repo/data/*.yaml."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request

from app.data_loader import DATA_FILES, load_with_mtime_cache

router = APIRouter()


@router.get("/")
async def list_reference_keys() -> dict:
    """Enumerate the reference keys this workbench knows about."""
    return {"keys": list(DATA_FILES.keys())}


@router.get("/{key}")
async def get_reference(request: Request, key: str) -> dict:
    """Return the parsed YAML for one of the T0-T4 reference files.

    Mtime-cached: edits on disk invalidate the cache automatically.
    """
    if key not in DATA_FILES:
        raise HTTPException(404, f"Unknown reference key: {key!r}")
    try:
        return load_with_mtime_cache(request.app.state.repo_root, key)
    except FileNotFoundError as exc:
        raise HTTPException(500, str(exc)) from exc
