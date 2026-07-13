from __future__ import annotations

import json
import os
import shutil
import stat
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
INSTALLER = ROOT / "scripts" / "install.sh"


class InstallScriptTests(unittest.TestCase):
    def run_installer(
        self,
        home: Path,
        *args: str,
        extra_env: dict[str, str] | None = None,
    ) -> subprocess.CompletedProcess[str]:
        env = os.environ.copy()
        env["HOME"] = str(home)
        if extra_env:
            env.update(extra_env)
        return subprocess.run(
            ["bash", str(INSTALLER), *args],
            cwd=ROOT,
            env=env,
            check=False,
            capture_output=True,
            text=True,
        )

    def test_default_install_is_a_read_only_dry_run(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            home = Path(temp_dir)
            result = self.run_installer(home, "--copy")

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("Mode: dry-run", result.stdout)
            self.assertIn("Re-run with --apply", result.stdout)
            self.assertFalse((home / ".claude").exists())
            self.assertFalse((home / ".agents").exists())

    def test_dry_run_rejects_destructive_or_source_overlapping_roots(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            home = Path(temp_dir)
            cases = (
                {"CLAUDE_CRAFT_DEST": "/"},
                {"CLAUDE_CRAFT_DEST": str(ROOT)},
                {"CLAUDE_CRAFT_DEST": str(ROOT / ".claude-runtime")},
                {"CLAUDE_CRAFT_SHARED_SKILLS_LINK": str(ROOT)},
                {"CLAUDE_CRAFT_SHARED_SKILLS_LINK": str(home)},
            )
            for extra_env in cases:
                with self.subTest(extra_env=extra_env):
                    result = self.run_installer(home, "--copy", extra_env=extra_env)
                    self.assertNotEqual(result.returncode, 0)
                    self.assertIn("unsafe", result.stderr.lower())

    def test_copy_apply_installs_a_runnable_runtime_closure(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            home = Path(temp_dir)
            runtime_root = home / ".claude"
            runtime_root.mkdir()
            settings = runtime_root / "settings.json"
            settings.write_text('{"userSetting": true}\n', encoding="utf-8")

            result = self.run_installer(home, "--copy", "--apply")
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(
                settings.read_text(encoding="utf-8"), '{"userSetting": true}\n'
            )

            expected_paths = (
                runtime_root
                / ".claude"
                / "registry"
                / "design"
                / "design-run.schema.json",
                runtime_root / ".claude" / "project-packs" / "default" / "pack.json",
                runtime_root
                / ".claude"
                / "rules"
                / "common"
                / "agent-orchestration.md",
                runtime_root / ".claude" / "evals" / "ui-design" / "grader.py",
                runtime_root / "scripts" / "harness-doctor.py",
                runtime_root / "scripts" / "harness-registry.py",
                runtime_root
                / ".claude"
                / "skills"
                / "design-harness"
                / "scripts"
                / "design-runtime.py",
                runtime_root
                / "third_party"
                / "gongnyang-prompt-kit"
                / "skills"
                / "image-prompt"
                / "SKILL.md",
            )
            for path in expected_paths:
                self.assertTrue(path.is_file(), path)

            prompt_link = runtime_root / ".claude" / "skills" / "image-prompt"
            prompt_target = (
                runtime_root
                / "third_party"
                / "gongnyang-prompt-kit"
                / "skills"
                / "image-prompt"
            )
            self.assertTrue(prompt_link.is_symlink())
            self.assertEqual(
                prompt_link.resolve(strict=True), prompt_target.resolve(strict=True)
            )

            self.assertEqual(os.readlink(runtime_root / "AGENTS.md"), "CLAUDE.md")
            self.assertEqual(os.readlink(runtime_root / "GEMINI.md"), "CLAUDE.md")
            self.assertEqual(
                os.readlink(runtime_root / ".agents" / "skills"), "../.claude/skills"
            )
            self.assertEqual(os.readlink(runtime_root / "skills"), ".claude/skills")
            self.assertEqual(
                os.readlink(home / ".agents" / "skills"), "../.claude/skills"
            )

            ownership_manifest = (
                runtime_root / ".claude" / ".claude-craft-install-manifest.json"
            )
            self.assertTrue(ownership_manifest.is_file())
            ownership = json.loads(ownership_manifest.read_text(encoding="utf-8"))
            self.assertEqual(
                ownership["schema_version"],
                "claude-craft.install-ownership.v1",
            )
            self.assertEqual(ownership["runtime_root"], str(runtime_root))
            self.assertIn(".claude/skills", ownership["owned_paths"]["runtime"])
            self.assertIn("skills", ownership["owned_paths"]["runtime"])
            self.assertIn(
                str(home / ".agents" / "skills"),
                ownership["owned_paths"]["external"],
            )

            doctor = subprocess.run(
                [
                    sys.executable,
                    str(runtime_root / "scripts" / "harness-doctor.py"),
                    "--root",
                    str(runtime_root),
                    "--json",
                ],
                cwd=runtime_root,
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(doctor.returncode, 0, doctor.stderr or doctor.stdout)
            checks = json.loads(doctor.stdout)["checks"]
            self.assertTrue(all(check["status"] == "pass" for check in checks), checks)

            registry = subprocess.run(
                [
                    sys.executable,
                    str(runtime_root / "scripts" / "harness-registry.py"),
                    "validate",
                ],
                cwd=runtime_root,
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(registry.returncode, 0, registry.stderr or registry.stdout)

    def test_apply_refuses_unowned_skill_paths_without_deleting_keep_files(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            home = Path(temp_dir)
            runtime_root = home / ".claude"
            keep_files = (
                runtime_root / "skills" / "keep.txt",
                runtime_root / ".claude" / "skills" / "keep.txt",
                home / ".agents" / "skills" / "keep.txt",
            )
            for index, path in enumerate(keep_files, start=1):
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(f"keep-{index}\n", encoding="utf-8")

            result = self.run_installer(home, "--copy", "--apply")

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("not owned by this installer", result.stderr)
            for index, path in enumerate(keep_files, start=1):
                self.assertEqual(path.read_text(encoding="utf-8"), f"keep-{index}\n")
            self.assertFalse(
                (
                    runtime_root / ".claude" / ".claude-craft-install-manifest.json"
                ).exists()
            )

    def test_update_fails_closed_when_owned_skill_tree_contains_user_content(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            home = Path(temp_dir)
            first = self.run_installer(home, "--copy", "--apply")
            self.assertEqual(first.returncode, 0, first.stderr)

            runtime_root = home / ".claude"
            canonical_keep = runtime_root / ".claude" / "skills" / "keep.txt"
            canonical_keep.write_text("preserve me\n", encoding="utf-8")

            result = self.run_installer(home, "--copy", "--apply")

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("owned path changed since installation", result.stderr)
            aliases = (
                runtime_root / "skills" / "keep.txt",
                canonical_keep,
                home / ".agents" / "skills" / "keep.txt",
            )
            for path in aliases:
                self.assertEqual(path.read_text(encoding="utf-8"), "preserve me\n")

    def test_failed_update_rolls_back_every_committed_owned_path(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            home = Path(temp_dir)
            first = self.run_installer(home, "--copy", "--apply")
            self.assertEqual(first.returncode, 0, first.stderr)

            runtime_root = home / ".claude"
            manifest = runtime_root / ".claude" / ".claude-craft-install-manifest.json"
            manifest_before = manifest.read_bytes()
            claude_before = (runtime_root / "CLAUDE.md").read_bytes()
            registry_before = (
                runtime_root / ".claude" / "registry" / "providers" / "core.yaml"
            ).read_bytes()
            link_targets_before = {
                path: os.readlink(path)
                for path in (
                    runtime_root / "AGENTS.md",
                    runtime_root / "skills",
                    home / ".agents" / "skills",
                )
            }

            failed = self.run_installer(
                home,
                "--copy",
                "--apply",
                extra_env={
                    "CLAUDE_CRAFT_TESTING": "1",
                    "CLAUDE_CRAFT_TEST_FAIL_AFTER_COMMIT": "4",
                },
            )

            self.assertNotEqual(failed.returncode, 0)
            self.assertIn("injected installer transaction failure", failed.stderr)
            self.assertIn("rolling back owned paths", failed.stderr)
            self.assertEqual(manifest.read_bytes(), manifest_before)
            self.assertEqual((runtime_root / "CLAUDE.md").read_bytes(), claude_before)
            self.assertEqual(
                (
                    runtime_root / ".claude" / "registry" / "providers" / "core.yaml"
                ).read_bytes(),
                registry_before,
            )
            for path, target in link_targets_before.items():
                self.assertTrue(path.is_symlink(), path)
                self.assertEqual(os.readlink(path), target)
            self.assertEqual(list(runtime_root.glob(".claude-craft-install.*")), [])
            self.assertEqual(
                list((home / ".agents").glob("skills.claude-craft-backup.*")),
                [],
            )

            retry = self.run_installer(home, "--copy", "--apply")
            self.assertEqual(retry.returncode, 0, retry.stderr)

    def test_link_apply_keeps_the_canonical_runtime_live(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            home = Path(temp_dir)
            result = self.run_installer(home, "--link", "--apply")
            self.assertEqual(result.returncode, 0, result.stderr)

            runtime_root = home / ".claude"
            registry_link = runtime_root / ".claude" / "registry"
            scripts_link = runtime_root / "scripts" / "harness-doctor.py"
            self.assertTrue(registry_link.is_symlink())
            self.assertEqual(
                registry_link.resolve(strict=True),
                (ROOT / ".claude" / "registry").resolve(),
            )
            self.assertTrue(scripts_link.is_symlink())
            self.assertEqual(
                scripts_link.resolve(strict=True),
                (ROOT / "scripts" / "harness-doctor.py").resolve(),
            )
            self.assertTrue(
                (
                    runtime_root / ".claude" / "skills" / "image-prompt" / "SKILL.md"
                ).is_file()
            )

            update = self.run_installer(home, "--link", "--apply")
            self.assertEqual(update.returncode, 0, update.stderr)
            self.assertEqual(
                registry_link.resolve(strict=True),
                (ROOT / ".claude" / "registry").resolve(),
            )

    @unittest.skipUnless(shutil.which("zip"), "zip is required for package export")
    def test_export_preserves_runtime_and_provider_symlinks(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp = Path(temp_dir)
            home = temp / "home"
            dist = temp / "dist"
            home.mkdir()
            result = self.run_installer(
                home,
                "--export",
                "--apply",
                extra_env={
                    "CLAUDE_CRAFT_DIST_DIR": str(dist),
                    "CLAUDE_CRAFT_PACKAGE_DATE": "fixture",
                },
            )
            self.assertEqual(result.returncode, 0, result.stderr)

            archive = dist / "woogi-harness-fixture.zip"
            self.assertTrue(archive.is_file())
            with zipfile.ZipFile(archive) as package:
                names = set(package.namelist())
                self.assertIn("scripts/harness-doctor.py", names)
                self.assertIn(".claude/registry/design/design-run.schema.json", names)
                self.assertIn(
                    "third_party/gongnyang-prompt-kit/skills/image-prompt/SKILL.md",
                    names,
                )
                expected_links = {
                    ".claude/skills/image-prompt": "../../third_party/gongnyang-prompt-kit/skills/image-prompt",
                    "AGENTS.md": "CLAUDE.md",
                    "GEMINI.md": "CLAUDE.md",
                    ".agents/skills": "../.claude/skills",
                }
                for name, target in expected_links.items():
                    info = package.getinfo(name)
                    self.assertTrue(stat.S_ISLNK(info.external_attr >> 16), name)
                    self.assertEqual(package.read(name).decode("utf-8"), target)


if __name__ == "__main__":
    unittest.main()
