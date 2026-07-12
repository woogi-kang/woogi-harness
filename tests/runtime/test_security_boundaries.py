from __future__ import annotations

import hashlib
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace


ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "scripts"
CONTEXT_GATE = SCRIPTS / "context-pack-gate.py"
DESIGN_DETECTOR = (
    ROOT
    / ".claude"
    / "skills"
    / "design-harness"
    / "scripts"
    / "detect-design-slop.mjs"
)
sys.path.insert(0, str(SCRIPTS))


def load_orchestrator():
    spec = importlib.util.spec_from_file_location(
        "orchestrate_security_boundaries", SCRIPTS / "orchestrate-worktrees.py"
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ORCHESTRATOR = load_orchestrator()


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class ContextPackSecurityTests(unittest.TestCase):
    def run_gate(self, repo: Path, target: str, name: str = "pack"):
        outdir = repo / ".orchestration" / "context-packs" / name
        result = subprocess.run(
            [
                sys.executable,
                str(CONTEXT_GATE),
                target,
                "--mode",
                "worker",
                "--outdir",
                str(outdir),
            ],
            cwd=repo,
            text=True,
            capture_output=True,
            check=False,
        )
        manifest = json.loads((outdir / "manifest.json").read_text(encoding="utf-8"))
        return result, outdir, manifest

    def test_external_file_and_parent_symlinks_are_never_packed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            repo = base / "repo"
            outside = base / "outside"
            repo.mkdir()
            outside.mkdir()
            secret = "nonpattern-sensitive-material-must-not-leak"
            (outside / "leak.tsx").write_text(secret, encoding="utf-8")
            (repo / "linked-file.tsx").symlink_to(outside / "leak.tsx")
            (repo / "linked-dir").symlink_to(outside, target_is_directory=True)

            for index, target in enumerate(("linked-file.tsx", "linked-dir/leak.tsx")):
                with self.subTest(target=target):
                    result, outdir, manifest = self.run_gate(
                        repo, target, f"blocked-{index}"
                    )
                    self.assertEqual(
                        result.returncode, 2, result.stdout + result.stderr
                    )
                    self.assertEqual(manifest["status"], "BLOCKED")
                    self.assertFalse((outdir / "context-pack.txt").exists())
                    self.assertTrue(
                        any(
                            item["reason"] == "symlink" for item in manifest["skipped"]
                        ),
                        manifest["skipped"],
                    )
                    rendered = "\n".join(
                        path.read_text(encoding="utf-8", errors="replace")
                        for path in outdir.iterdir()
                        if path.is_file()
                    )
                    self.assertNotIn(secret, rendered)

    def test_pass_manifest_binds_full_pack_and_report_hashes(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            repo = Path(temporary) / "repo"
            repo.mkdir()
            (repo / "safe.txt").write_text("bounded context\n", encoding="utf-8")
            result, outdir, manifest = self.run_gate(repo, "safe.txt")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertEqual(
                manifest["schema_version"], "harness.context-pack-manifest.v1"
            )
            self.assertEqual(manifest["status"], "PASS")
            self.assertEqual(
                manifest["pack_sha256"], sha256(outdir / "context-pack.txt")
            )
            self.assertEqual(manifest["report_sha256"], sha256(outdir / "report.md"))
            self.assertRegex(manifest["files"][0]["sha256"], r"^[0-9a-f]{64}$")


class OrchestratorContextPackTests(unittest.TestCase):
    run_gate = ContextPackSecurityTests.run_gate

    def make_pack(self, base: Path):
        repo = base / "repo"
        worktree = base / "worktree"
        repo.mkdir()
        worktree.mkdir()
        (repo / "safe.txt").write_text("worker context\n", encoding="utf-8")
        result, outdir, manifest = self.run_gate(repo, "safe.txt")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        worker = SimpleNamespace(
            context_pack=str((outdir / "report.md").relative_to(repo)),
            worktree_path=worktree,
            name="Reviewer",
        )
        return repo, worktree, outdir, manifest, worker

    def test_only_manifest_report_and_pack_are_copied(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            repo, worktree, outdir, _, worker = self.make_pack(Path(temporary))
            (outdir / "unapproved-secret.txt").write_text(
                "do not copy", encoding="utf-8"
            )
            ORCHESTRATOR.sync_context_pack_to_worktree(worker, repo)
            destination = worktree / outdir.relative_to(repo)
            self.assertEqual(
                {path.name for path in destination.iterdir()},
                {"manifest.json", "report.md", "context-pack.txt"},
            )
            for name in ("manifest.json", "report.md", "context-pack.txt"):
                self.assertEqual(sha256(destination / name), sha256(outdir / name))

    def test_tampering_blocked_status_and_symlink_references_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            repo, _, outdir, manifest, worker = self.make_pack(base)

            (outdir / "context-pack.txt").write_text("tampered\n", encoding="utf-8")
            with self.assertRaises(SystemExit):
                ORCHESTRATOR.sync_context_pack_to_worktree(worker, repo)

            (outdir / "context-pack.txt").write_text(
                "worker context\n", encoding="utf-8"
            )
            manifest["pack_sha256"] = sha256(outdir / "context-pack.txt")
            manifest["status"] = "BLOCKED"
            (outdir / "manifest.json").write_text(
                json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
            with self.assertRaises(SystemExit):
                ORCHESTRATOR.sync_context_pack_to_worktree(worker, repo)

            worker.context_pack = str((outdir / "report-link.md").relative_to(repo))
            (outdir / "report-link.md").symlink_to(outdir / "report.md")
            with self.assertRaises(SystemExit):
                ORCHESTRATOR.sync_context_pack_to_worktree(worker, repo)


class DesignDetectorSecurityTests(unittest.TestCase):
    def run_detector(self, repo: Path, target: str):
        return subprocess.run(
            [
                "node",
                str(DESIGN_DETECTOR),
                "--format",
                "json",
                "--fail-on",
                "none",
                target,
            ],
            cwd=repo,
            text=True,
            capture_output=True,
            check=False,
        )

    def test_nested_and_direct_external_symlinks_are_not_scanned(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            repo = base / "repo"
            outside = base / "outside"
            repo.mkdir()
            outside.mkdir()
            (repo / "safe.tsx").write_text(
                "export const Safe = () => <button>Save</button>\n"
            )
            secret = "EXTERNAL-SYMLINK-CONTENT-MUST-NOT-APPEAR"
            (outside / "leak.tsx").write_text(secret, encoding="utf-8")
            (repo / "linked").symlink_to(outside, target_is_directory=True)

            nested = self.run_detector(repo, ".")
            self.assertEqual(nested.returncode, 0, nested.stderr)
            nested_payload = json.loads(nested.stdout)
            self.assertEqual(nested_payload["files_scanned"], ["safe.tsx"])
            self.assertNotIn(secret, nested.stdout)

            direct = self.run_detector(repo, "linked/leak.tsx")
            self.assertEqual(direct.returncode, 2, direct.stderr)
            self.assertNotIn(secret, direct.stdout)
            self.assertTrue(json.loads(direct.stdout)["errors"])


if __name__ == "__main__":
    unittest.main()
