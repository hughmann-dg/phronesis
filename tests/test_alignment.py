from pathlib import Path
import shutil
import tempfile
import unittest

from phronesis.alignment import _load_flat_manifest, audit_repository


class AlignmentTests(unittest.TestCase):
    def test_repository_assets_and_executable_doctrines_are_aligned(self) -> None:
        report = audit_repository(Path("."))

        self.assertEqual(report["errors"], [], report)
        self.assertEqual(report["doctrine_count"], 9)
        self.assertEqual(report["manifest_source_count"], 20)
        self.assertGreaterEqual(report["verified_local_source_count"], 0)

    def test_audit_rejects_a_school_without_an_agent_descriptor(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            copied_root = Path(directory, "repository")
            shutil.copytree(
                Path("."),
                copied_root,
                ignore=shutil.ignore_patterns(".git", "build", "corpus", "*.egg-info", "__pycache__"),
            )
            Path(copied_root, "skills", "aristotelian-counsel", "agents", "openai.yaml").unlink()

            report = audit_repository(copied_root)

            self.assertIn(
                "doctrine aristotelian-counsel has no agent descriptor",
                report["errors"],
            )

    def test_manifest_parser_rejects_duplicate_fields(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory, "manifest.yaml")
            path.write_text(
                "sources:\n  - id: source-one\n    rights_status: restricted\n    rights_status: public-domain-verified\n",
                encoding="utf-8",
            )

            with self.assertRaisesRegex(ValueError, "duplicate manifest field"):
                _load_flat_manifest(path)


if __name__ == "__main__":
    unittest.main()
