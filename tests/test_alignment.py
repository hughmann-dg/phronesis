from pathlib import Path
import shutil
import tempfile
import unittest

from phronesis.alignment import _load_flat_manifest, audit_repository


SKILLS_ROOT = Path("skills")
DISCOVERY_SKILLS_ROOT = Path(".agents", "skills")


def _copy_repository(parent: str) -> Path:
    copied_root = Path(parent, "repository")
    shutil.copytree(
        Path("."),
        copied_root,
        ignore=shutil.ignore_patterns(".git", "build", "corpus", "*.egg-info", "__pycache__"),
    )
    return copied_root


class AlignmentTests(unittest.TestCase):
    def test_repository_assets_and_executable_doctrines_are_aligned(self) -> None:
        report = audit_repository(Path("."))

        self.assertEqual(report["errors"], [], report)
        self.assertEqual(report["doctrine_count"], 10)
        self.assertEqual(report["manifest_source_count"], 21)
        self.assertGreaterEqual(report["verified_local_source_count"], 0)

    def test_audit_rejects_a_school_without_an_agent_descriptor(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            copied_root = _copy_repository(directory)
            Path(copied_root, SKILLS_ROOT, "aristotelian-counsel", "agents", "openai.yaml").unlink()

            report = audit_repository(copied_root)

            self.assertIn(
                "doctrine aristotelian-counsel has no agent descriptor",
                report["errors"],
            )

    def test_audit_rejects_council_without_independent_agent_protocol(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            copied_root = _copy_repository(directory)
            council_skill = Path(copied_root, SKILLS_ROOT, "council", "SKILL.md")
            council_skill.write_text(
                council_skill.read_text(encoding="utf-8").replace(
                    "advisor_context: fresh-per-school",
                    "advisor_context: shared",
                ),
                encoding="utf-8",
            )

            report = audit_repository(copied_root)

            self.assertIn(
                "council skill has no independent agent protocol",
                report["errors"],
            )

    def test_audit_rejects_voting_school_without_source_first_deliberation(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            copied_root = _copy_repository(directory)
            school_skill = Path(copied_root, SKILLS_ROOT, "aristotelian-counsel", "SKILL.md")
            school_skill.write_text(
                school_skill.read_text(encoding="utf-8").replace(
                    "source_order: before-option-evaluation",
                    "source_order: after-option-evaluation",
                ),
                encoding="utf-8",
            )

            report = audit_repository(copied_root)

            self.assertIn(
                "skill aristotelian-counsel has no source-first deliberation protocol",
                report["errors"],
            )

    def test_audit_rejects_host_manifests_that_do_not_share_the_canonical_tree(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            copied_root = _copy_repository(directory)
            claude_manifest = Path(copied_root, ".claude-plugin", "plugin.json")
            claude_manifest.write_text(
                '{"name": "phronesis", "skills": "./.agents/skills/"}',
                encoding="utf-8",
            )

            report = audit_repository(copied_root)

            self.assertIn(
                "Claude plugin manifest does not expose the canonical Phronesis skill tree",
                report["errors"],
            )

    def test_audit_rejects_nonportable_skill_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            copied_root = _copy_repository(directory)
            council_skill = Path(copied_root, SKILLS_ROOT, "council", "SKILL.md")
            council_skill.write_text(
                council_skill.read_text(encoding="utf-8").replace(
                    "name: council",
                    "name: Council Skill",
                ),
                encoding="utf-8",
            )

            report = audit_repository(copied_root)

            self.assertIn(
                "skill council has nonportable name metadata: Council Skill",
                report["errors"],
            )

    def test_audit_rejects_a_drifted_repository_discovery_adapter(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            copied_root = _copy_repository(directory)
            adapter = Path(copied_root, DISCOVERY_SKILLS_ROOT, "council", "SKILL.md")
            adapter.write_text(
                adapter.read_text(encoding="utf-8").replace(
                    "canonical `council` skill",
                    "canonical Council implementation",
                ),
                encoding="utf-8",
            )

            report = audit_repository(copied_root)

            self.assertIn(
                "skill council repository discovery adapter has drifted",
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
