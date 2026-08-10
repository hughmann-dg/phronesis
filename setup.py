"""Build hook that preserves Phronesis's non-code agent assets in wheels."""

from pathlib import Path

from setuptools import setup


PROJECT_ROOT = Path(__file__).parent
ASSET_ROOTS = (".agents", "benchmarks", "docs", "schemas", "skills", "sources")


def asset_data_files() -> list[tuple[str, list[str]]]:
    grouped: dict[str, list[str]] = {}
    for root_name in ASSET_ROOTS:
        root = PROJECT_ROOT / root_name
        for path in root.rglob("*"):
            if not path.is_file() or "corpus" in path.parts or path.name == ".gitkeep":
                continue
            relative = path.relative_to(PROJECT_ROOT)
            destination = (Path("share") / "phronesis" / relative.parent).as_posix()
            grouped.setdefault(destination, []).append(relative.as_posix())
    for manifest_directory in (".codex-plugin", ".claude-plugin"):
        plugin_manifest = PROJECT_ROOT / manifest_directory / "plugin.json"
        if plugin_manifest.is_file():
            grouped.setdefault(f"share/phronesis/{manifest_directory}", []).append(
                plugin_manifest.relative_to(PROJECT_ROOT).as_posix()
            )
    return [(destination, sorted(paths)) for destination, paths in sorted(grouped.items())]


setup(data_files=asset_data_files())
