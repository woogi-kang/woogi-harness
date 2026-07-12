from __future__ import annotations

import hashlib
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from harness_runtime_lib import (  # noqa: E402
    HarnessError,
    build_asset_inventory,
    load_capabilities,
    load_data,
    merge_effective_capabilities,
    new_execution_record,
    parse_frontmatter,
    provider_registry_errors,
    read_json_stream,
    transition_execution,
    resolve_capabilities,
    resolve_provider_quality,
    sha256_file,
    validate_process_outcome,
    validate_registry,
    write_json,
)


def write_minimal_provider_registry(root: Path) -> None:
    provider_dir = root / ".claude" / "registry" / "providers"
    provider_dir.mkdir(parents=True, exist_ok=True)
    write_json(
        provider_dir / "core.yaml",
        {
            "schema_version": "harness.providers.v1",
            "quality_classes": [
                {
                    "id": "implementation",
                    "required_capabilities": ["code"],
                    "required_tools": ["filesystem"],
                    "context_policy": "isolated",
                }
            ],
            "providers": [
                {
                    "id": "claude",
                    "quality_classes": ["implementation"],
                    "quality_capabilities": ["code"],
                    "tools": ["filesystem"],
                    "tool_adapter": "native",
                    "execution_adapter": {
                        "kind": "host-native",
                        "profile": "claude-native",
                    },
                    "quality_adapter": {
                        "strategy": "provider-native",
                        "bindings": {
                            "implementation": {
                                "selection": "implementation",
                                "context_policy": "isolated",
                                "execution_profile": {
                                    "kind": "host-native",
                                    "profile": "claude-native:implementation",
                                },
                            }
                        },
                    },
                }
            ],
        },
    )


class RegistryTests(unittest.TestCase):
    def test_inventory_build_writes_bounded_identity_snapshot(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "inventory.json"
            subprocess.run(
                [
                    sys.executable,
                    str(SCRIPTS / "harness-registry.py"),
                    "build",
                    "--output",
                    str(output),
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=True,
            )
            inventory = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(inventory["schema_version"], "harness.asset-inventory.v1")
            schema = json.loads(
                (
                    ROOT / ".claude/registry/contracts/asset-inventory.schema.json"
                ).read_text(encoding="utf-8")
            )
            allowed_kinds = schema["properties"]["entries"]["items"]["properties"][
                "kind"
            ]["enum"]
            self.assertTrue(
                {entry["kind"] for entry in inventory["entries"]} <= set(allowed_kinds)
            )
            self.assertGreaterEqual(inventory["asset_count"], 340)
            self.assertTrue(
                all(
                    "source" in item and "frontmatter_name" in item
                    for item in inventory["entries"]
                )
            )

    def test_generated_inventory_qualifies_duplicate_framework_skills(self) -> None:
        static = load_capabilities(ROOT / ".claude" / "registry")
        inventory = build_asset_inventory(ROOT)
        effective = merge_effective_capabilities(static, inventory)
        self.assertGreaterEqual(inventory["asset_count"], 340)

        with self.assertRaises(HarnessError):
            resolve_capabilities(effective, ["architecture"])
        with self.assertRaises(HarnessError):
            resolve_capabilities(effective, ["project-setup"])

        resolved = resolve_capabilities(
            effective,
            [
                "skill:fastapi-agent-skills/architecture",
                "skill:flutter-agent-skills/architecture",
                "skill:nextjs-agent-skills/project-setup",
                "skill:fastapi-agent-skills/project-setup",
                "design-harness",
                "eval-harness",
                "context-pack-gate",
            ],
        )
        sources = {item["source"] for item in resolved}
        self.assertTrue(
            any("fastapi-agent-skills/2-architecture" in path for path in sources)
        )
        self.assertTrue(
            any("flutter-agent-skills/2-architecture" in path for path in sources)
        )
        self.assertTrue(
            any("nextjs-agent-skills/1-project-setup" in path for path in sources)
        )
        self.assertTrue(
            any("fastapi-agent-skills/1-project-setup" in path for path in sources)
        )
        self.assertIn(".claude/skills/design-harness/SKILL.md", sources)
        self.assertIn(".claude/skills/eval-harness/SKILL.md", sources)
        self.assertIn(".claude/skills/context-pack-gate/SKILL.md", sources)

    def test_supporting_agent_docs_are_not_callable_and_active_agents_have_tiers(
        self,
    ) -> None:
        static = load_capabilities(ROOT / ".claude" / "registry")
        inventory = build_asset_inventory(ROOT)
        entries = inventory["entries"]
        usage_guide = next(
            item
            for item in entries
            if item["source"].endswith("figma-to-nextjs/USAGE-GUIDE.md")
        )
        self.assertEqual(usage_guide["status"], "supporting")
        self.assertTrue(any(item["kind"] == "command" for item in entries))
        effective = merge_effective_capabilities(static, inventory)
        with self.assertRaises(HarnessError):
            resolve_capabilities(effective, ["Figma to Next.js Usage Guide"])

        allowed_tiers = {
            "reasoning_high",
            "implementation",
            "fast_scan",
            "independent_critic",
        }
        active_agents = [
            item
            for item in entries
            if item["kind"] == "agent" and item["status"] == "active"
        ]
        self.assertGreaterEqual(len(active_agents), 25)
        for item in active_agents:
            frontmatter = parse_frontmatter(ROOT / item["source"])
            self.assertEqual(frontmatter.get("model"), "inherit", item["source"])
            self.assertIn(
                frontmatter.get("quality_tier"), allowed_tiers, item["source"]
            )

    def test_active_capability_skill_agent_name_collision_is_classified_as_fatal(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            registry = root / ".claude" / "registry"
            (registry / "capabilities").mkdir(parents=True)
            (registry / "skills").mkdir(parents=True)
            (registry / "agents").mkdir(parents=True)
            write_json(
                registry / "capabilities" / "core.json",
                {
                    "capabilities": [
                        {
                            "id": "one",
                            "kind": "workflow",
                            "aliases": ["shared"],
                            "status": "stable",
                        },
                    ]
                },
            )
            write_json(
                registry / "skills" / "core.json",
                {"skills": [{"id": "two", "aliases": ["shared"], "status": "stable"}]},
            )
            write_json(
                registry / "agents" / "core.json",
                {
                    "agents": [
                        {"id": "three", "aliases": ["shared"], "status": "stable"}
                    ]
                },
            )
            _, issues = validate_registry(root, registry)
            active = [
                issue for issue in issues if issue.code == "active_name_collision"
            ]
            self.assertEqual(len(active), 2)
            self.assertTrue(all(issue.severity == "error" for issue in active))
            messages = " ".join(issue.message for issue in active)
            self.assertIn("skill", messages)
            self.assertIn("agent", messages)

    def test_context_compiler_fails_selected_frontmatter_collision(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for segment in ("a", "b"):
                skill = root / ".claude" / "skills" / segment / "SKILL.md"
                skill.parent.mkdir(parents=True, exist_ok=True)
                skill.write_text("---\nname: duplicate\n---\n", encoding="utf-8")
            capability_dir = root / ".claude" / "registry" / "capabilities"
            capability_dir.mkdir(parents=True)
            write_minimal_provider_registry(root)
            write_json(
                capability_dir / "core.json",
                {
                    "capabilities": [
                        {
                            "id": "duplicate.skill",
                            "source": ".claude/skills/a/SKILL.md",
                            "frontmatter_name": "duplicate",
                            "context_files": [],
                        }
                    ]
                },
            )
            profile = root / "profile.json"
            write_json(
                profile,
                {
                    "schema_version": "harness.project-profile.v1",
                    "id": "test",
                    "pack": "pack.json",
                    "providers": ["claude"],
                    "selected_provider": "claude",
                    "default_quality_tier": "implementation",
                    "capabilities": ["duplicate.skill"],
                    "context_budget_bytes": 1024,
                    "overlays": [],
                },
            )
            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPTS / "harness-context.py"),
                    "--root",
                    str(root),
                    "--project-profile",
                    str(profile),
                ],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("frontmatter name", result.stderr)


class ContextTests(unittest.TestCase):
    def test_context_compiler_resolves_generated_qualified_and_unique_aliases(
        self,
    ) -> None:
        result = subprocess.run(
            [
                sys.executable,
                str(SCRIPTS / "harness-context.py"),
                "--capability",
                "skill:fastapi-agent-skills/architecture",
                "--capability",
                "skill:flutter-agent-skills/project-setup",
                "--capability",
                "design-harness",
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
        )
        manifest = json.loads(result.stdout)
        selected_paths = {item["path"] for item in manifest["selected"]}
        self.assertTrue(
            any(
                "fastapi-agent-skills/2-architecture" in path for path in selected_paths
            )
        )
        self.assertTrue(
            any(
                "flutter-agent-skills/1-project-setup" in path
                for path in selected_paths
            )
        )
        self.assertIn(".claude/skills/design-harness/SKILL.md", selected_paths)

    def test_missing_profile_argument_uses_safe_default_profile(self) -> None:
        result = subprocess.run(
            [sys.executable, str(SCRIPTS / "harness-context.py")],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
        )
        manifest = json.loads(result.stdout)
        self.assertEqual(manifest["profile"], "default")
        self.assertGreater(len(manifest["selected"]), 0)
        self.assertLessEqual(manifest["total_bytes"], manifest["budget_bytes"])

    def test_optional_context_is_skipped_at_budget(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "small.txt").write_text("1234", encoding="utf-8")
            (root / "large.txt").write_text("x" * 100, encoding="utf-8")
            capability_dir = root / ".claude" / "registry" / "capabilities"
            capability_dir.mkdir(parents=True)
            write_minimal_provider_registry(root)
            write_json(
                capability_dir / "core.json",
                {
                    "capabilities": [
                        {
                            "id": "optional",
                            "source": "small.txt",
                            "context_files": ["large.txt"],
                            "required_context": False,
                        }
                    ]
                },
            )
            profile = root / "profile.json"
            write_json(
                profile,
                {
                    "schema_version": "harness.project-profile.v1",
                    "id": "test",
                    "pack": "pack.json",
                    "providers": ["claude"],
                    "selected_provider": "claude",
                    "default_quality_tier": "implementation",
                    "capabilities": ["optional"],
                    "context_budget_bytes": 10,
                    "overlays": [],
                },
            )
            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPTS / "harness-context.py"),
                    "--root",
                    str(root),
                    "--project-profile",
                    str(profile),
                ],
                text=True,
                capture_output=True,
                check=True,
            )
            manifest = json.loads(result.stdout)
            self.assertEqual(
                [item["path"] for item in manifest["selected"]], ["small.txt"]
            )
            self.assertEqual(manifest["skipped"][0]["reason"], "budget-exceeded")


class ExecutionTests(unittest.TestCase):
    def test_orchestrator_does_not_promote_evidenceless_exit_zero(self) -> None:
        spec = importlib.util.spec_from_file_location(
            "orchestrate_worktrees", SCRIPTS / "orchestrate-worktrees.py"
        )
        self.assertIsNotNone(spec)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        with tempfile.TemporaryDirectory() as temporary:
            repo = Path(temporary) / "repo"
            repo.mkdir()
            worker = module.WorkerInfo(
                {"name": "Worker", "task": "work", "success_criteria": ["verified"]},
                0,
                {"session": "test", "launcher": "true"},
                repo,
            )
            state, reason, _, _ = module.worker_exit_outcome(worker, 0)
            self.assertEqual(state, "failed")
            self.assertIn("no outcome", reason)

    def test_exit_zero_requires_valid_evidence_outcome(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            outcome = Path(temporary) / "outcome.json"
            artifact_root = Path(temporary) / "artifacts"
            artifact_root.mkdir()
            artifact = artifact_root / "unittest.log"
            artifact.write_text("unittest passed\n", encoding="utf-8")
            state, reason, _ = validate_process_outcome(0, outcome)
            self.assertEqual(state, "failed")
            self.assertIn("no outcome", reason)

            record = new_execution_record("session:worker", "do work", ["tests pass"])
            record = transition_execution(record, "running", reason="started")
            record = transition_execution(
                record,
                "succeeded",
                evidence=[
                    {
                        "type": "test-log",
                        "description": "unittest passed",
                        "producer": "python-unittest",
                        "command": [sys.executable, "-m", "unittest"],
                        "exit_code": 0,
                        "status": "passed",
                        "path": artifact.name,
                        "sha256": sha256_file(artifact),
                        "bytes": artifact.stat().st_size,
                    }
                ],
                checks=[{"criterion": "tests pass", "status": "passed"}],
            )
            write_json(outcome, record)
            state, _, loaded = validate_process_outcome(0, outcome)
            self.assertEqual(state, "succeeded")
            self.assertEqual(loaded["attempt"], 1)

    def test_exit_zero_preserves_valid_blocked_outcome(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            outcome = Path(temporary) / "outcome.json"
            record = new_execution_record("session:worker", "do work", ["tests pass"])
            record = transition_execution(record, "running", reason="started")
            record = transition_execution(
                record,
                "blocked",
                stop_reason="test service unavailable",
            )
            write_json(outcome, record)
            state, reason, _ = validate_process_outcome(0, outcome)
            self.assertEqual(state, "blocked")
            self.assertEqual(reason, "test service unavailable")

    def test_dangerous_launcher_needs_explicit_approval_boundary(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            plan = Path(temporary) / "plan.json"
            write_json(
                plan,
                {
                    "session": "unsafe",
                    "launcher": "claude --dangerously-skip-permissions -p x",
                    "workers": [{"name": "one", "task": "x"}],
                },
            )
            result = subprocess.run(
                [sys.executable, str(SCRIPTS / "orchestrate-worktrees.py"), str(plan)],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("allow_dangerous_permissions", result.stderr)

    def test_orchestrator_consumes_registered_cli_binding_and_blocks_host_native(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            plan = Path(temporary) / "plan.json"
            write_json(
                plan,
                {
                    "session": "provider-binding",
                    "provider": "claude",
                    "quality_tier": "implementation",
                    "workers": [{"name": "one", "task": "x"}],
                },
            )
            resolved = subprocess.run(
                [sys.executable, str(SCRIPTS / "orchestrate-worktrees.py"), str(plan)],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(resolved.returncode, 0, resolved.stderr)
            self.assertIn(
                "claude -p --effort high --no-session-persistence", resolved.stdout
            )

            write_json(
                plan,
                {
                    "session": "provider-binding",
                    "provider": "codex",
                    "quality_tier": "implementation",
                    "workers": [{"name": "one", "task": "x"}],
                },
            )
            blocked = subprocess.run(
                [sys.executable, str(SCRIPTS / "orchestrate-worktrees.py"), str(plan)],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertNotEqual(blocked.returncode, 0)
            self.assertIn("host-native execution", blocked.stderr)


class TelemetryTests(unittest.TestCase):
    def test_legacy_pretty_objects_are_read_as_a_stream(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            log = Path(temporary) / "usage.jsonl"
            log.write_text(
                json.dumps({"tool": "agent", "name": "a"}, indent=2)
                + "\n"
                + json.dumps({"tool": "skill", "name": "b"}, indent=2)
                + "\n",
                encoding="utf-8",
            )
            self.assertEqual(len(read_json_stream(log)), 2)

    def test_corrupt_stream_is_rejected_without_resynchronizing(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            log = Path(temporary) / "usage.jsonl"
            log.write_text(
                "not-json\n" + json.dumps({"tool": "agent", "name": "a"}) + "\n",
                encoding="utf-8",
            )
            with self.assertRaisesRegex(HarnessError, "invalid JSON stream"):
                read_json_stream(log)

    def test_telemetry_validate_returns_parse_error_for_corrupt_log(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            log = Path(temporary) / "usage.jsonl"
            log.write_text(
                json.dumps({"tool": "agent", "name": "a"}) + "\ntrailing-garbage\n",
                encoding="utf-8",
            )
            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPTS / "harness-telemetry.py"),
                    "validate",
                    str(log),
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(result.returncode, 2)
            self.assertIn("invalid JSON stream", result.stderr)
            self.assertNotIn("PASS", result.stdout)


class ProviderRegistryTests(unittest.TestCase):
    def test_quality_classes_are_provider_neutral_and_tool_bounded(self) -> None:
        provider = load_data(ROOT / ".claude" / "registry" / "providers" / "core.yaml")
        classes = {item["id"]: item for item in provider["quality_classes"]}
        self.assertEqual(
            set(classes),
            {"reasoning_high", "implementation", "fast_scan", "independent_critic"},
        )
        self.assertTrue(
            all(
                item["required_capabilities"] and item["required_tools"]
                for item in classes.values()
            )
        )
        self.assertTrue(
            all(
                set(item["quality_classes"]) == set(classes)
                for item in provider["providers"]
            )
        )
        serialized = json.dumps(provider).lower()
        for pinned_name in ("opus", "sonnet", "haiku"):
            self.assertNotIn(pinned_name, serialized)
        self.assertTrue(provider["model_policy"]["disallow_hardcoded_general_models"])
        self.assertEqual(provider_registry_errors(provider), [])
        binding = resolve_provider_quality(provider, "codex", "implementation")
        self.assertEqual(binding["status"], "supported")
        self.assertEqual(binding["selection"], "implementation")
        self.assertEqual(binding["execution_adapter"]["kind"], "host-native")
        self.assertRegex(binding["binding_hash"], r"^[a-f0-9]{64}$")

    def test_provider_binding_fails_when_declared_requirements_are_missing(
        self,
    ) -> None:
        provider = load_data(ROOT / ".claude" / "registry" / "providers" / "core.yaml")
        provider["providers"][0]["tools"].remove("shell")
        errors = provider_registry_errors(provider)
        self.assertTrue(any("missing tools: shell" in error for error in errors))
        with self.assertRaises(HarnessError):
            resolve_provider_quality(provider, "claude", "implementation")

    def test_provider_registry_rejects_arbitrary_bindings_and_missing_adapters(
        self,
    ) -> None:
        for mutation in ("blank", "arbitrary", "missing-tool-adapter"):
            provider = load_data(
                ROOT / ".claude" / "registry" / "providers" / "core.yaml"
            )
            if mutation == "blank":
                provider["providers"][0]["quality_adapter"]["bindings"][
                    "implementation"
                ]["selection"] = "   "
            elif mutation == "arbitrary":
                provider["providers"][0]["quality_adapter"]["bindings"][
                    "implementation"
                ]["selection"] = "not-a-runtime-selector"
            else:
                del provider["providers"][0]["tool_adapter"]
            self.assertTrue(provider_registry_errors(provider), mutation)


class SyncTests(unittest.TestCase):
    def test_fresh_target_pack_is_self_contained_and_doctor_clean(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "target"
            target.mkdir()
            manifest = Path(temporary) / "fresh-apply.json"
            subprocess.run(
                [
                    sys.executable,
                    str(SCRIPTS / "harness-sync.py"),
                    str(target),
                    "--apply",
                    "--manifest-out",
                    str(manifest),
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=True,
            )
            for required in (
                "scripts/context-pack-gate.py",
                "scripts/orchestrate-worktrees.py",
                "scripts/verify-stack-registry.py",
                "scripts/brain-memory.sh",
                "scripts/brain-memory-qa.sh",
                "scripts/brain-pilot.sh",
                "scripts/sprint-reset-loop.sh",
            ):
                self.assertTrue((target / required).is_file(), required)
            doctor = subprocess.run(
                [
                    sys.executable,
                    str(target / "scripts/harness-doctor.py"),
                    "--root",
                    str(target),
                    "--strict",
                ],
                cwd=target,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(doctor.returncode, 0, doctor.stdout + doctor.stderr)

    def test_sync_rejects_symlink_escape_forged_rollback_and_unwritable_manifest(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            source = base / "source"
            target = base / "target"
            outside = base / "outside"
            source.mkdir()
            target.mkdir()
            outside.mkdir()
            (source / "linked").mkdir()
            (source / "linked" / "payload.txt").write_text("new", encoding="utf-8")
            (target / "linked").symlink_to(outside, target_is_directory=True)
            pack = source / "pack.json"
            profile = source / "profile.json"
            projects = source / "projects.json"
            write_json(
                pack,
                {
                    "schema_version": "harness.project-pack.v1",
                    "id": "security-test",
                    "paths": ["linked"],
                    "links": {},
                    "exclude": [],
                },
            )
            write_json(
                profile,
                {
                    "schema_version": "harness.project-profile.v1",
                    "pack": str(pack),
                    "protected_paths": [],
                },
            )
            write_json(
                projects,
                {
                    "projects": [
                        {
                            "id": "target",
                            "path": str(target),
                            "profile": str(profile),
                            "enabled": True,
                        }
                    ]
                },
            )
            command = [
                sys.executable,
                str(SCRIPTS / "harness-sync.py"),
                "--root",
                str(source),
                "--registry",
                str(projects),
                "--project",
                "target",
                "--apply",
                "--manifest-out",
                str(base / "escape.json"),
            ]
            escaped = subprocess.run(
                command, text=True, capture_output=True, check=False
            )
            self.assertEqual(escaped.returncode, 2)
            self.assertFalse((outside / "payload.txt").exists())

            victim = base / "victim.txt"
            victim.write_text("keep", encoding="utf-8")
            forged = base / "forged.json"
            write_json(
                forged,
                {
                    "schema_version": "harness.sync-manifest.v1",
                    "run_id": "forged",
                    "mode": "apply",
                    "actions": [
                        {
                            "project_id": "target",
                            "project_path": str(target.resolve()),
                            "path": str(victim.resolve()),
                            "before": {"kind": "absent"},
                            "desired": {"kind": "file"},
                            "operation": "create",
                            "applied": True,
                            "after": {"kind": "file", "sha256": sha256_file(victim)},
                        }
                    ],
                },
            )
            rollback = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPTS / "harness-sync.py"),
                    "--rollback",
                    str(forged),
                ],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(rollback.returncode, 2)
            self.assertEqual(victim.read_text(encoding="utf-8"), "keep")

            (target / "linked").unlink()
            (target / "linked").mkdir()
            old = target / "linked" / "payload.txt"
            old.write_text("old", encoding="utf-8")
            manifest_directory = base / "manifest-directory"
            manifest_directory.mkdir()
            failed_manifest = subprocess.run(
                [*command[:-1], str(manifest_directory)],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(failed_manifest.returncode, 2)
            self.assertEqual(old.read_text(encoding="utf-8"), "old")

    def test_pack_overlay_materializes_settings_hook_once_and_rolls_back(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            source = base / "source"
            target = base / "target"
            hook = (
                source / "third_party" / "gongnyang" / "hooks" / "block-text-overlay.sh"
            )
            hook.parent.mkdir(parents=True)
            hook.write_text("#!/bin/sh\n", encoding="utf-8")
            (target / ".claude").mkdir(parents=True)
            original_settings = {
                "env": {"KEEP": "yes"},
                "hooks": {
                    "PreToolUse": [
                        {
                            "matcher": "Bash",
                            "hooks": [{"type": "command", "command": "existing-hook"}],
                        }
                    ]
                },
            }
            write_json(target / ".claude" / "settings.json", original_settings)

            base_pack = source / "base-pack.json"
            overlay_pack = source / "image-pack.json"
            profile = source / "profile.json"
            projects = source / "projects.json"
            write_json(
                base_pack,
                {
                    "schema_version": "harness.project-pack.v1",
                    "id": "base",
                    "paths": [],
                    "links": {},
                    "exclude": [],
                },
            )
            hook_command = (
                "$CLAUDE_PROJECT_DIR/third_party/gongnyang/hooks/block-text-overlay.sh"
            )
            write_json(
                overlay_pack,
                {
                    "schema_version": "harness.project-pack.v1",
                    "id": "image-generation",
                    "paths": ["third_party/gongnyang"],
                    "settings_merges": [
                        {
                            "target": ".claude/settings.json",
                            "format": "json",
                            "operation": "append-if-missing",
                            "path": ["hooks", "PreToolUse"],
                            "match": {"matcher": "Bash"},
                            "append_path": ["hooks"],
                            "value": {"type": "command", "command": hook_command},
                        }
                    ],
                    "exclude": [],
                },
            )
            write_json(
                profile,
                {
                    "schema_version": "harness.project-profile.v1",
                    "pack": str(base_pack),
                    "pack_overlays": [str(overlay_pack)],
                    "protected_paths": [".claude/settings.json"],
                },
            )
            write_json(
                projects,
                {
                    "projects": [
                        {
                            "id": "target",
                            "path": str(target),
                            "profile": str(profile),
                            "enabled": True,
                        }
                    ]
                },
            )
            command = [
                sys.executable,
                str(SCRIPTS / "harness-sync.py"),
                "--root",
                str(source),
                "--registry",
                str(projects),
                "--project",
                "target",
            ]
            subprocess.run(command, text=True, capture_output=True, check=True)
            self.assertEqual(
                json.loads((target / ".claude" / "settings.json").read_text()),
                original_settings,
            )
            self.assertFalse((target / "third_party" / "gongnyang").exists())

            manifest = base / "image-apply.json"
            subprocess.run(
                [*command, "--apply", "--manifest-out", str(manifest)],
                text=True,
                capture_output=True,
                check=True,
            )
            merged = json.loads((target / ".claude" / "settings.json").read_text())
            self.assertEqual(merged["env"], {"KEEP": "yes"})
            manifest_text = manifest.read_text(encoding="utf-8")
            self.assertNotIn('"KEEP"', manifest_text)
            self.assertNotIn("existing-hook", manifest_text)
            commands = [
                item["command"] for item in merged["hooks"]["PreToolUse"][0]["hooks"]
            ]
            self.assertEqual(commands.count(hook_command), 1)
            self.assertTrue(
                (
                    target
                    / "third_party"
                    / "gongnyang"
                    / "hooks"
                    / "block-text-overlay.sh"
                ).is_file()
            )

            second_manifest = base / "image-apply-second.json"
            subprocess.run(
                [*command, "--apply", "--manifest-out", str(second_manifest)],
                text=True,
                capture_output=True,
                check=True,
            )
            merged_again = json.loads(
                (target / ".claude" / "settings.json").read_text()
            )
            commands_again = [
                item["command"]
                for item in merged_again["hooks"]["PreToolUse"][0]["hooks"]
            ]
            self.assertEqual(commands_again.count(hook_command), 1)

            subprocess.run(
                [
                    sys.executable,
                    str(SCRIPTS / "harness-sync.py"),
                    "--rollback",
                    str(manifest),
                ],
                text=True,
                capture_output=True,
                check=True,
            )
            restored = json.loads((target / ".claude" / "settings.json").read_text())
            self.assertEqual(restored, original_settings)
            self.assertFalse(
                (
                    target
                    / "third_party"
                    / "gongnyang"
                    / "hooks"
                    / "block-text-overlay.sh"
                ).exists()
            )

    def test_dry_run_apply_and_rollback_are_non_destructive(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            source = base / "source"
            target = base / "target"
            source.mkdir()
            target.mkdir()
            (source / "owned").mkdir()
            (source / "payload.txt").write_text("new", encoding="utf-8")
            (target / "payload.txt").write_text("old", encoding="utf-8")
            (target / "target-only.txt").write_text("keep", encoding="utf-8")
            (target / "owned").mkdir()
            (target / "owned" / "retired.txt").write_text("legacy", encoding="utf-8")

            pack = source / "pack.json"
            profile = source / "profile.json"
            projects = source / "projects.json"
            write_json(
                pack,
                {
                    "schema_version": "harness.project-pack.v1",
                    "id": "test",
                    "paths": ["payload.txt", "owned"],
                    "tombstones": [
                        {
                            "path": "owned/retired.txt",
                            "accepted_sha256": [hashlib.sha256(b"legacy").hexdigest()],
                        }
                    ],
                    "links": {},
                    "exclude": [],
                },
            )
            write_json(
                profile,
                {
                    "schema_version": "harness.project-profile.v1",
                    "pack": str(pack),
                    "protected_paths": [],
                },
            )
            write_json(
                projects,
                {
                    "projects": [
                        {
                            "id": "target",
                            "path": str(target),
                            "profile": str(profile),
                            "enabled": True,
                            "canary": True,
                        }
                    ]
                },
            )
            base_command = [
                sys.executable,
                str(SCRIPTS / "harness-sync.py"),
                "--root",
                str(source),
                "--registry",
                str(projects),
                "--project",
                "target",
            ]
            dry_run = subprocess.run(
                base_command, text=True, capture_output=True, check=True
            )
            self.assertIn('"mode": "dry-run"', dry_run.stdout)
            self.assertEqual(
                (target / "payload.txt").read_text(encoding="utf-8"), "old"
            )

            manifest = base / "manifest.json"
            subprocess.run(
                [*base_command, "--apply", "--manifest-out", str(manifest)],
                text=True,
                capture_output=True,
                check=True,
            )
            self.assertEqual(
                (target / "payload.txt").read_text(encoding="utf-8"), "new"
            )
            self.assertTrue((target / "target-only.txt").is_file())
            self.assertFalse((target / "owned" / "retired.txt").exists())

            subprocess.run(
                [
                    sys.executable,
                    str(SCRIPTS / "harness-sync.py"),
                    "--rollback",
                    str(manifest),
                ],
                text=True,
                capture_output=True,
                check=True,
            )
            self.assertEqual(
                (target / "payload.txt").read_text(encoding="utf-8"), "old"
            )
            self.assertTrue((target / "target-only.txt").is_file())
            self.assertEqual(
                (target / "owned" / "retired.txt").read_text(encoding="utf-8"),
                "legacy",
            )

    def test_tombstone_refuses_to_delete_unowned_content(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            source = base / "source"
            target = base / "target"
            source.mkdir()
            target.mkdir()
            (source / "owned").mkdir()
            custom = target / "owned" / "retired.txt"
            custom.parent.mkdir()
            custom.write_text("project customization", encoding="utf-8")

            pack = source / "pack.json"
            profile = source / "profile.json"
            projects = source / "projects.json"
            write_json(
                pack,
                {
                    "schema_version": "harness.project-pack.v1",
                    "id": "test",
                    "paths": ["owned"],
                    "tombstones": [
                        {
                            "path": "owned/retired.txt",
                            "accepted_sha256": [
                                hashlib.sha256(b"known harness file").hexdigest()
                            ],
                        }
                    ],
                },
            )
            write_json(
                profile,
                {
                    "schema_version": "harness.project-profile.v1",
                    "pack": str(pack),
                    "protected_paths": [],
                },
            )
            write_json(
                projects,
                {
                    "projects": [
                        {
                            "id": "target",
                            "path": str(target),
                            "profile": str(profile),
                            "enabled": True,
                        }
                    ]
                },
            )
            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPTS / "harness-sync.py"),
                    "--root",
                    str(source),
                    "--registry",
                    str(projects),
                    "--project",
                    "target",
                ],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(result.returncode, 1)
            self.assertIn("conflict-tombstone-unowned", result.stdout)
            self.assertEqual(
                custom.read_text(encoding="utf-8"), "project customization"
            )

    def test_legacy_shell_wrapper_accepts_positional_target_and_stays_dry_run(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary)
            sentinel = target / "CLAUDE.md"
            sentinel.write_text("project-owned", encoding="utf-8")
            result = subprocess.run(
                ["bash", str(SCRIPTS / "sync-to-projects.sh"), str(target)],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=True,
            )
            self.assertIn('"mode": "dry-run"', result.stdout)
            self.assertIn("Dry-run only", result.stdout)
            self.assertEqual(sentinel.read_text(encoding="utf-8"), "project-owned")


if __name__ == "__main__":
    unittest.main()
