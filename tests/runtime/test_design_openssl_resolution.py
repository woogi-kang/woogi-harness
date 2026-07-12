from __future__ import annotations

import base64
import importlib.util
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[2]
RUNTIME_PATH = ROOT / ".claude/skills/design-harness/scripts/design-runtime.py"
GRADER_PATH = ROOT / ".claude/evals/ui-design/grader.py"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class DesignOpenSSLResolutionTests(unittest.TestCase):
    def test_runtime_resolver_skips_incapable_binary_and_caches(self) -> None:
        runtime = load_module("design_runtime_openssl_test", RUNTIME_PATH)
        runtime.resolve_openssl_ed25519.cache_clear()

        def which(name: str) -> str | None:
            return {"openssl": "/incapable", "openssl3": "/capable"}.get(name)

        calls: list[list[str]] = []

        def run(command: list[str], **kwargs):
            calls.append(command)
            self.assertIn("timeout", kwargs)
            return subprocess.CompletedProcess(
                command, 1 if command[0] == "/incapable" else 0
            )

        with (
            mock.patch.object(runtime.shutil, "which", side_effect=which),
            mock.patch.object(runtime.subprocess, "run", side_effect=run),
        ):
            self.assertEqual(runtime.resolve_openssl_ed25519(), "/capable")
            first_call_count = len(calls)
            self.assertEqual(runtime.resolve_openssl_ed25519(), "/capable")

        self.assertEqual(first_call_count, 5)
        self.assertEqual(len(calls), first_call_count)

    def test_runtime_resolver_recovers_from_timeout_and_can_return_none(self) -> None:
        runtime = load_module("design_runtime_openssl_timeout_test", RUNTIME_PATH)
        runtime.resolve_openssl_ed25519.cache_clear()

        def which(name: str) -> str | None:
            return {"openssl": "/timeout", "openssl3": "/capable"}.get(name)

        def timed_run(command: list[str], **kwargs):
            if command[0] == "/timeout":
                raise subprocess.TimeoutExpired(command, kwargs["timeout"])
            return subprocess.CompletedProcess(command, 0)

        with (
            mock.patch.object(runtime.shutil, "which", side_effect=which),
            mock.patch.object(runtime.subprocess, "run", side_effect=timed_run),
        ):
            self.assertEqual(runtime.resolve_openssl_ed25519(), "/capable")

        runtime.resolve_openssl_ed25519.cache_clear()
        with (
            mock.patch.object(runtime.shutil, "which", return_value=None),
            mock.patch.object(
                runtime.subprocess,
                "run",
                return_value=subprocess.CompletedProcess([], 1),
            ),
        ):
            self.assertIsNone(runtime.resolve_openssl_ed25519())

    def test_runtime_verify_reports_cached_binary_execution_failure(self) -> None:
        runtime = load_module("design_runtime_openssl_verify_test", RUNTIME_PATH)
        with tempfile.TemporaryDirectory() as temporary:
            public = Path(temporary) / "public.pem"
            public.write_text("invalid", encoding="utf-8")
            with (
                mock.patch.object(
                    runtime, "resolve_openssl_ed25519", return_value="/broken"
                ),
                mock.patch.object(runtime.subprocess, "run", side_effect=OSError),
            ):
                errors = runtime.verify_ed25519_signature(
                    public, {"payload": True}, base64.b64encode(b"sig").decode()
                )
        self.assertTrue(any("OpenSSL" in error for error in errors))

    def test_grader_verify_fails_closed_on_cached_binary_execution_failure(
        self,
    ) -> None:
        grader = load_module("design_grader_openssl_verify_test", GRADER_PATH)
        with tempfile.TemporaryDirectory() as temporary:
            public = Path(temporary) / "public.pem"
            public.write_text("invalid", encoding="utf-8")
            with (
                mock.patch.object(
                    grader, "resolve_openssl_ed25519", return_value="/broken"
                ),
                mock.patch.object(grader.subprocess, "run", side_effect=OSError),
            ):
                verified = grader.verify_signature(
                    public, {"payload": True}, base64.b64encode(b"sig").decode()
                )
        self.assertFalse(verified)


if __name__ == "__main__":
    unittest.main()
