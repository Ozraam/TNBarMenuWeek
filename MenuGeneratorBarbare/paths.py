"""Path utilities for locating writable directories."""

from __future__ import annotations

import os
import tempfile
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent


def _resolve_base(path_value: str | None) -> Path:
    """Return a path located under the project unless already absolute."""
    if not path_value:
        return PROJECT_ROOT / "build"
    candidate = Path(path_value)
    if not candidate.is_absolute():
        candidate = PROJECT_ROOT / candidate
    return candidate


def _ensure_writable(target: Path) -> Path:
    """Return a writable directory, falling back to tmp if needed."""
    try:
        target.mkdir(parents=True, exist_ok=True)
    except PermissionError:
        # Directory exists but might not be writable; continue to access check.
        pass

    if os.access(target, os.W_OK | os.X_OK):
        return target

    fallback_root = Path(os.getenv("MENU_FALLBACK_DIR", tempfile.gettempdir()))
    fallback = fallback_root / "tnbarmenuweek-build"
    fallback.mkdir(parents=True, exist_ok=True)
    if os.access(fallback, os.W_OK | os.X_OK):
        return fallback

    raise RuntimeError(
        "Unable to find a writable directory for build artifacts; "
        "set MENU_BUILD_DIR to a writable location."
    )


def get_build_dir() -> Path:
    """Compute the directory used to store generated assets."""
    base = _resolve_base(os.getenv("MENU_BUILD_DIR"))
    return _ensure_writable(base)
