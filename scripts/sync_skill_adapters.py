"""Generate thin repository-discovery adapters from canonical Phronesis skills."""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from phronesis.alignment import _discovery_adapter_text  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="fail when adapters are missing or stale")
    args = parser.parse_args()

    canonical_root = ROOT / "skills"
    adapter_root = ROOT / ".agents" / "skills"
    expected_names: set[str] = set()
    stale: list[str] = []

    for skill_path in sorted(canonical_root.glob("*/SKILL.md")):
        skill_name = skill_path.parent.name
        expected_names.add(skill_name)
        expected = _discovery_adapter_text(skill_name, skill_path.read_text(encoding="utf-8"))
        adapter_path = adapter_root / skill_name / "SKILL.md"
        actual = adapter_path.read_text(encoding="utf-8") if adapter_path.is_file() else None
        if actual == expected:
            continue
        if args.check:
            stale.append(skill_name)
            continue
        adapter_path.parent.mkdir(parents=True, exist_ok=True)
        adapter_path.write_text(expected, encoding="utf-8", newline="\n")

    extra_names = {path.parent.name for path in adapter_root.glob("*/SKILL.md")} - expected_names
    if args.check:
        stale.extend(f"extra:{name}" for name in sorted(extra_names))
    else:
        for name in sorted(extra_names):
            shutil.rmtree(adapter_root / name)
    if stale:
        print("Discovery adapters differ: " + ", ".join(stale), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
