"""Locate repository assets in a checkout or an installed distribution."""

from __future__ import annotations

import sys
from pathlib import Path


def asset_root() -> Path:
    candidates = (
        Path(__file__).resolve().parents[2],
        Path(sys.prefix) / "share" / "phronesis",
        Path.cwd(),
    )
    for candidate in candidates:
        if (candidate / "schemas" / "decision-packet.schema.json").is_file():
            return candidate
    raise FileNotFoundError("cannot locate Phronesis schemas and skills; reinstall the complete distribution")


def asset_path(relative: str | Path) -> Path:
    return asset_root() / relative
