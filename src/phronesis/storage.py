"""Small crash-safe filesystem primitives shared by local stores."""

from __future__ import annotations

import os
from pathlib import Path
import tempfile


def atomic_write_text(target: Path, content: str) -> None:
    """Replace a UTF-8 text file only after its complete content reaches disk."""

    target.parent.mkdir(parents=True, exist_ok=True)
    temporary_name: str | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=target.parent,
            prefix=f".{target.name}-",
            suffix=".tmp",
            delete=False,
        ) as temporary:
            temporary_name = temporary.name
            temporary.write(content)
            temporary.flush()
            os.fsync(temporary.fileno())
        os.replace(temporary_name, target)
    finally:
        if temporary_name and os.path.exists(temporary_name):
            os.unlink(temporary_name)
