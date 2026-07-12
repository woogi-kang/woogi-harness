from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from harness_runtime_lib import (  # noqa: E402
    HarnessError,
    sha256_file,
    validate_execution_record,
    validate_process_outcome,
)


def load_sync_module():
    spec = importlib.util.spec_from_file_location(
        "harness_sync_adversarial", SCRIPTS / "harness-sync.py"
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


SYNC = load_sync_module()


class ExecutionEvidenceAdversarialTests(unittest.TestCase):
    def succeeded_record(self, evidence: dict) -> dict:
        return {
            "schema_version": "harness.execution.v1",
            "execution_id": "session:worker",
            "objective": "verify",
            "state": "succeeded",
            "attempt": 1,
            "success_criteria": ["tests passed"],
            "artifact_root": "artifacts",
            "evidence": [evidence],
            "checks": [{"criterion": "tests passed", "status": "passed"}],
            "history": [
                {"from": None, "to": "pending", "at": "2026-07-13T00:00:00Z"},
                {"from": "pending", "to": "running", "at": "2026-07-13T00:00:01Z"},
                {"from": "running", "to": "succeeded", "at": "2026-07-13T00:00:02Z"},
            ],
        }

    def typed_evidence(self, artifact: Path, raw_path: str) -> dict:
        return {
            "type": "test-log",
            "description": "focused test output",
            "producer": "pytest",
            "command": [sys.executable, "-m", "pytest", "tests"],
            "exit_code": 0,
            "status": "passed",
            "path": raw_path,
            "sha256": sha256_file(artifact),
            "bytes": artifact.stat().st_size,
        }

    def test_cli_does_not_write_succeeded_for_a_missing_artifact(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            outcome = Path(temporary) / "outcome.json"
            subprocess.run(
                [
                    sys.executable,
                    str(SCRIPTS / "harness-execution.py"),
                    "init",
                    "--file",
                    str(outcome),
                    "--id",
                    "session:worker",
                    "--objective",
                    "verify",
                    "--success-criterion",
                    "tests passed",
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            subprocess.run(
                [
                    sys.executable,
                    str(SCRIPTS / "harness-execution.py"),
                    "transition",
                    "--file",
                    str(outcome),
                    "--to",
                    "running",
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            evidence = json.dumps(
                {
                    "type": "test",
                    "description": "claimed test result",
                    "producer": "pytest",
                    "command": [sys.executable, "-m", "pytest"],
                    "exit_code": 0,
                    "status": "passed",
                    "path": "missing.log",
                    "sha256": "0" * 64,
                    "bytes": 0,
                }
            )
            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPTS / "harness-execution.py"),
                    "transition",
                    "--file",
                    str(outcome),
                    "--to",
                    "succeeded",
                    "--evidence",
                    evidence,
                    "--check",
                    "tests passed=passed",
                ],
                check=False,
                capture_output=True,
                text=True,
            )
            stored = json.loads(outcome.read_text(encoding="utf-8"))
        self.assertEqual(result.returncode, 2)
        self.assertIn("artifact is missing", result.stderr)
        self.assertEqual(stored["state"], "running")

    def test_self_described_evidence_cannot_promote_succeeded(self) -> None:
        record = {
            "schema_version": "harness.execution.v1",
            "execution_id": "session:worker",
            "objective": "pretend",
            "state": "succeeded",
            "attempt": 1,
            "success_criteria": ["real tests passed"],
            "artifact_root": "artifacts",
            "evidence": [{"type": "test", "description": "trust me"}],
            "checks": [{"criterion": "real tests passed", "status": "passed"}],
            "history": [
                {"from": None, "to": "pending", "at": "2026-07-13T00:00:00Z"},
                {"from": "pending", "to": "running", "at": "2026-07-13T00:00:01Z"},
                {"from": "running", "to": "succeeded", "at": "2026-07-13T00:00:02Z"},
            ],
        }
        errors = validate_execution_record(record, final=True)
        self.assertTrue(any("artifact path" in error for error in errors), errors)
        with tempfile.TemporaryDirectory() as temporary:
            outcome = Path(temporary) / "outcome.json"
            outcome.write_text(json.dumps(record) + "\n", encoding="utf-8")
            state, reason, _ = validate_process_outcome(0, outcome)
        self.assertEqual(state, "failed")
        self.assertIn("artifact path", reason)

    def test_artifact_hash_drift_cannot_promote_succeeded(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            artifact_root = root / "artifacts"
            artifact_root.mkdir()
            artifact = artifact_root / "test.log"
            artifact.write_text("passed\n", encoding="utf-8")
            record = {
                "schema_version": "harness.execution.v1",
                "execution_id": "session:worker",
                "objective": "verify",
                "state": "succeeded",
                "attempt": 1,
                "success_criteria": ["tests passed"],
                "artifact_root": "artifacts",
                "evidence": [
                    {
                        "type": "test-log",
                        "description": "focused test output",
                        "producer": "pytest",
                        "command": [sys.executable, "-m", "pytest", "tests"],
                        "exit_code": 0,
                        "status": "passed",
                        "path": artifact.name,
                        "sha256": sha256_file(artifact),
                        "bytes": artifact.stat().st_size,
                    }
                ],
                "checks": [{"criterion": "tests passed", "status": "passed"}],
                "history": [
                    {"from": None, "to": "pending", "at": "2026-07-13T00:00:00Z"},
                    {"from": "pending", "to": "running", "at": "2026-07-13T00:00:01Z"},
                    {
                        "from": "running",
                        "to": "succeeded",
                        "at": "2026-07-13T00:00:02Z",
                    },
                ],
            }
            outcome = root / "outcome.json"
            outcome.write_text(json.dumps(record) + "\n", encoding="utf-8")
            artifact.write_text("forged after outcome\n", encoding="utf-8")
            state, reason, _ = validate_process_outcome(0, outcome)
        self.assertEqual(state, "failed")
        self.assertIn("artifact", reason)

    def test_absolute_parent_traversal_and_symlink_artifacts_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            artifact_root = root / "artifacts"
            artifact_root.mkdir()
            local = artifact_root / "local.log"
            outside = root / "outside.log"
            local.write_text("passed\n", encoding="utf-8")
            outside.write_text("external\n", encoding="utf-8")

            cases = (
                (
                    self.typed_evidence(Path("/etc/hosts"), "/etc/hosts"),
                    "must be relative",
                ),
                (self.typed_evidence(outside, "../outside.log"), "must be relative"),
            )
            for evidence, message in cases:
                with self.subTest(path=evidence["path"]):
                    errors = validate_execution_record(
                        self.succeeded_record(evidence),
                        final=True,
                        artifact_root=artifact_root,
                    )
                    self.assertTrue(any(message in error for error in errors), errors)

            link = artifact_root / "linked.log"
            link.symlink_to(outside)
            errors = validate_execution_record(
                self.succeeded_record(self.typed_evidence(outside, link.name)),
                final=True,
                artifact_root=artifact_root,
            )
            self.assertTrue(
                any("symlink component" in error for error in errors), errors
            )

            outside_dir = root / "outside-dir"
            outside_dir.mkdir()
            nested_outside = outside_dir / "nested.log"
            nested_outside.write_text("external nested\n", encoding="utf-8")
            (artifact_root / "nested").symlink_to(outside_dir, target_is_directory=True)
            errors = validate_execution_record(
                self.succeeded_record(
                    self.typed_evidence(nested_outside, "nested/nested.log")
                ),
                final=True,
                artifact_root=artifact_root,
            )
            self.assertTrue(
                any("symlink component" in error for error in errors), errors
            )

    def test_succeeded_evidence_requires_typed_execution_provenance(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            artifact_root = Path(temporary) / "artifacts"
            artifact_root.mkdir()
            artifact = artifact_root / "test.log"
            artifact.write_text("passed\n", encoding="utf-8")
            evidence = {
                "type": "test-log",
                "description": "self-authored claim",
                "path": artifact.name,
                "sha256": sha256_file(artifact),
                "bytes": artifact.stat().st_size,
            }
            errors = validate_execution_record(
                self.succeeded_record(evidence),
                final=True,
                artifact_root=artifact_root,
            )
            for field in ("producer", "command", "exit_code", "status"):
                self.assertTrue(any(field in error for error in errors), errors)


class TelemetryAdversarialTests(unittest.TestCase):
    def test_semantically_invalid_event_is_rejected(self) -> None:
        event = {
            "schema_version": "harness.telemetry.v1",
            "timestamp": 42,
            "session_id": "",
            "provider": "",
            "event_type": "",
            "subject_type": "",
            "subject_id": "",
            "status": "",
            "duration_ms": -5,
            "context_bytes": True,
            "metadata": {},
        }
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "events.jsonl"
            path.write_text(json.dumps(event) + "\n", encoding="utf-8")
            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPTS / "harness-telemetry.py"),
                    "validate",
                    str(path),
                ],
                text=True,
                capture_output=True,
                check=False,
            )
        self.assertEqual(result.returncode, 1)
        self.assertIn("timestamp", result.stderr)
        self.assertIn("duration_ms", result.stderr)
        self.assertIn("context_bytes", result.stderr)


class SyncAdversarialTests(unittest.TestCase):
    def make_action(self, source: Path, target: Path, *, before: dict) -> dict:
        payload = source / "payload.txt"
        return {
            "project_id": "target",
            "project_path": str(target.resolve()),
            "path": "payload.txt",
            "desired": {
                "path": "payload.txt",
                "kind": "file",
                "sha256": sha256_file(payload),
                "bytes": payload.stat().st_size,
                "pack_id": "test",
            },
            "before": before,
            "operation": "create" if before["kind"] == "absent" else "update",
            "applied": False,
        }

    def test_source_drift_after_plan_is_rejected_before_write(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "source"
            target = root / "target"
            source.mkdir()
            target.mkdir()
            payload = source / "payload.txt"
            payload.write_text("planned", encoding="utf-8")
            action = self.make_action(source, target, before={"kind": "absent"})
            payload.write_text("drifted", encoding="utf-8")
            with self.assertRaisesRegex(
                HarnessError, "pack source changed after planning"
            ):
                SYNC.apply_actions(source, [action], "run")
            self.assertFalse((target / "payload.txt").exists())

    def test_tombstone_cannot_cross_pack_exclude_or_use_empty_allowlist(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            source = Path(temporary)
            (source / "owned").mkdir()
            excluded = {
                "schema_version": "harness.project-pack.v1",
                "id": "test",
                "paths": ["owned"],
                "exclude": ["owned/**"],
                "tombstones": [
                    {
                        "path": "owned/retired.txt",
                        "accepted_sha256": ["0" * 64],
                    }
                ],
            }
            with self.assertRaisesRegex(HarnessError, "excluded path"):
                SYNC.desired_tombstones(source, excluded)

            empty = {
                "schema_version": "harness.project-pack.v1",
                "id": "test",
                "paths": ["owned"],
                "tombstones": [
                    {
                        "path": "owned/retired.txt",
                        "accepted_sha256": [],
                        "accepted_symlink_targets": ["legacy-target"],
                    }
                ],
            }
            with self.assertRaisesRegex(HarnessError, "cannot be empty"):
                SYNC.desired_tombstones(source, empty)

            duplicate = {
                "schema_version": "harness.project-pack.v1",
                "id": "test",
                "paths": ["owned"],
                "tombstones": [
                    {
                        "path": "owned/retired.txt",
                        "accepted_sha256": ["0" * 64, "0" * 64],
                    }
                ],
            }
            with self.assertRaisesRegex(HarnessError, "has duplicates"):
                SYNC.desired_tombstones(source, duplicate)

            unknown = {
                "schema_version": "harness.project-pack.v1",
                "id": "test",
                "paths": ["owned"],
                "tombstones": [
                    {
                        "path": "owned/retired.txt",
                        "accepted_sha256": ["0" * 64],
                        "force": True,
                    }
                ],
            }
            with self.assertRaisesRegex(HarnessError, "unsupported tombstone fields"):
                SYNC.desired_tombstones(source, unknown)

    def test_tombstone_scope_cannot_be_owned_through_a_source_symlink(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "source"
            outside = root / "outside"
            source.mkdir()
            outside.mkdir()
            (source / "owned").symlink_to(outside, target_is_directory=True)
            pack = {
                "schema_version": "harness.project-pack.v1",
                "id": "test",
                "paths": ["owned"],
                "tombstones": [
                    {
                        "path": "owned/retired.txt",
                        "accepted_sha256": ["0" * 64],
                    }
                ],
            }
            with self.assertRaisesRegex(HarnessError, "outside pack-owned paths"):
                SYNC.desired_tombstones(source, pack)

    def test_copy_postcondition_mismatch_is_rolled_back(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "source"
            target = root / "target"
            source.mkdir()
            target.mkdir()
            payload = source / "payload.txt"
            payload.write_text("planned", encoding="utf-8")
            action = self.make_action(source, target, before={"kind": "absent"})

            original_write = SYNC.write_bytes_at

            def corrupt_write(parent_fd, name, content, mode, *, replace=True):
                return original_write(
                    parent_fd,
                    name,
                    b"corrupt",
                    mode,
                    replace=replace,
                )

            with mock.patch.object(SYNC, "write_bytes_at", side_effect=corrupt_write):
                with self.assertRaisesRegex(HarnessError, "sync postcondition failed"):
                    SYNC.apply_actions(source, [action], "run")
            self.assertFalse((target / "payload.txt").exists())
            self.assertFalse(action.get("rollback_incomplete", False))

    def test_tombstone_preserves_final_entry_swapped_after_backup(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "source"
            target = root / "target"
            source.mkdir()
            target.mkdir()
            destination = target / "retired.txt"
            destination.write_text("legacy", encoding="utf-8")
            action = {
                "project_id": "target",
                "project_path": str(target.resolve()),
                "path": "retired.txt",
                "desired": {
                    "path": "retired.txt",
                    "kind": "absent",
                    "accepted_sha256": [sha256_file(destination)],
                    "accepted_symlink_targets": [],
                    "pack_id": "test",
                },
                "before": SYNC.fingerprint(destination),
                "operation": "delete",
                "applied": False,
            }
            original_backup = SYNC.backup_existing

            def swap_after_backup(*args, **kwargs):
                result = original_backup(*args, **kwargs)
                parent_fd = args[1]
                self.assertIn(".quarantine", args[2])
                SYNC.write_bytes_at(
                    parent_fd,
                    "retired.txt",
                    b"project customization",
                    0o644,
                    replace=True,
                )
                return result

            with mock.patch.object(
                SYNC, "backup_existing", side_effect=swap_after_backup
            ):
                with self.assertRaisesRegex(HarnessError, "sync postcondition failed"):
                    SYNC.apply_actions(source, [action], "run")
            self.assertEqual(
                destination.read_text(encoding="utf-8"), "project customization"
            )
            self.assertFalse(action["applied"])
            self.assertTrue(action["rollback_incomplete"])
            self.assertTrue((target / action["recovery_quarantine"]).is_file())

    def test_legacy_manifest_fingerprint_without_mode_can_rollback(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            target = root / "target"
            target.mkdir(parents=True)
            destination = target / "payload.txt"
            destination.write_text("new", encoding="utf-8")
            backup = (
                target
                / ".claude"
                / "harness-backups"
                / "run"
                / "payload"
                / "payload.txt"
            )
            backup.parent.mkdir(parents=True)
            backup.write_text("old", encoding="utf-8")
            before = SYNC.fingerprint(backup)
            after = SYNC.fingerprint(destination)
            before.pop("mode")
            after.pop("mode")
            action = {
                "project_id": "target",
                "project_path": str(target.resolve()),
                "path": "payload.txt",
                "desired": {"kind": "file"},
                "before": before,
                "after": after,
                "operation": "update",
                "applied": True,
                "backup": str(backup),
            }
            self.assertTrue(SYNC.restore_action(action, require_after_match=True))
            self.assertEqual(destination.read_text(encoding="utf-8"), "old")

    def test_rollback_rejects_backup_payload_drift_before_mutation(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            target = root / "target"
            target.mkdir(parents=True)
            destination = target / "payload.txt"
            destination.write_text("new", encoding="utf-8")
            backup = (
                target
                / ".claude"
                / "harness-backups"
                / "run"
                / "payload"
                / "payload.txt"
            )
            backup.parent.mkdir(parents=True)
            backup.write_text("old", encoding="utf-8")
            action = {
                "project_id": "target",
                "project_path": str(target.resolve()),
                "path": "payload.txt",
                "desired": {"kind": "file"},
                "before": SYNC.fingerprint(backup),
                "after": SYNC.fingerprint(destination),
                "operation": "update",
                "applied": True,
                "backup": str(backup),
            }
            original_read = SYNC.read_file_at
            reads = 0

            def drift_third_read(parent_fd, name):
                nonlocal reads
                payload, mode = original_read(parent_fd, name)
                reads += 1
                if reads == 3:
                    return b"malicious", mode
                return payload, mode

            with mock.patch.object(SYNC, "read_file_at", side_effect=drift_third_read):
                self.assertFalse(SYNC.restore_action(action, require_after_match=True))
            self.assertEqual(destination.read_text(encoding="utf-8"), "new")
            self.assertEqual(backup.read_text(encoding="utf-8"), "old")

    def test_tombstone_source_revived_after_plan_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "source"
            target = root / "target"
            source.mkdir()
            target.mkdir()
            destination = target / "retired.txt"
            destination.write_text("legacy", encoding="utf-8")
            action = {
                "project_id": "target",
                "project_path": str(target.resolve()),
                "path": "retired.txt",
                "desired": {
                    "path": "retired.txt",
                    "kind": "absent",
                    "accepted_sha256": [sha256_file(destination)],
                    "accepted_symlink_targets": [],
                    "pack_id": "test",
                },
                "before": SYNC.fingerprint(destination),
                "operation": "delete",
                "applied": False,
            }
            (source / "retired.txt").write_text("revived", encoding="utf-8")
            with self.assertRaisesRegex(
                HarnessError, "tombstone source changed after planning"
            ):
                SYNC.apply_actions(source, [action], "run")
            self.assertEqual(destination.read_text(encoding="utf-8"), "legacy")

    def test_tombstone_rejects_backup_payload_drift(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "source"
            target = root / "target"
            source.mkdir()
            target.mkdir()
            destination = target / "retired.txt"
            destination.write_text("legacy", encoding="utf-8")
            action = {
                "project_id": "target",
                "project_path": str(target.resolve()),
                "path": "retired.txt",
                "desired": {
                    "path": "retired.txt",
                    "kind": "absent",
                    "accepted_sha256": [sha256_file(destination)],
                    "accepted_symlink_targets": [],
                    "pack_id": "test",
                },
                "before": SYNC.fingerprint(destination),
                "operation": "delete",
                "applied": False,
            }
            original_read = SYNC.read_file_at
            quarantine_reads = 0

            def drift_quarantine_read(parent_fd, name):
                nonlocal quarantine_reads
                payload, mode = original_read(parent_fd, name)
                if ".quarantine" in name:
                    quarantine_reads += 1
                    if quarantine_reads == 3:
                        return b"project customization", mode
                return payload, mode

            with mock.patch.object(
                SYNC, "read_file_at", side_effect=drift_quarantine_read
            ):
                with self.assertRaisesRegex(
                    HarnessError, "destination changed while reading backup"
                ):
                    SYNC.apply_actions(source, [action], "run")
            self.assertEqual(destination.read_text(encoding="utf-8"), "legacy")
            self.assertFalse(action.get("rollback_incomplete", False))

    def test_missing_backup_does_not_delete_applied_destination(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "source"
            target = root / "target"
            source.mkdir()
            target.mkdir()
            payload = source / "payload.txt"
            destination = target / "payload.txt"
            payload.write_text("new", encoding="utf-8")
            destination.write_text("old", encoding="utf-8")
            action = self.make_action(
                source, target, before=SYNC.fingerprint(destination)
            )
            SYNC.apply_actions(source, [action], "run")
            Path(action["backup"]).unlink()
            restored, skipped = SYNC.rollback_actions([action])
            self.assertEqual((restored, skipped), (0, 1))
            self.assertEqual(destination.read_text(encoding="utf-8"), "new")


if __name__ == "__main__":
    unittest.main()
