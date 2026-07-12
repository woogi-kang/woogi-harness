from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import tomllib
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from harness_runtime_lib import (  # noqa: E402
    build_asset_inventory,
    load_capabilities,
    load_data,
    merge_effective_capabilities,
    resolve_capabilities,
    resolve_provider_quality,
)


def load_stack_verifier():
    spec = importlib.util.spec_from_file_location(
        "verify_stack_registry", SCRIPTS / "verify-stack-registry.py"
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class VendoredSkillInventoryTests(unittest.TestCase):
    def test_image_prompt_is_resolvable_and_context_compilable(self) -> None:
        inventory = build_asset_inventory(ROOT)
        effective = merge_effective_capabilities(
            load_capabilities(ROOT / ".claude" / "registry"), inventory
        )
        resolved = resolve_capabilities(effective, ["image-prompt"])
        self.assertEqual(resolved[0]["source"], ".claude/skills/image-prompt/SKILL.md")

        result = subprocess.run(
            [
                sys.executable,
                str(SCRIPTS / "harness-context.py"),
                "--capability",
                "image-prompt",
                "--quality-tier",
                "fast_scan",
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
        )
        manifest = json.loads(result.stdout)
        selected = {item["path"] for item in manifest["selected"]}
        self.assertIn(".claude/skills/image-prompt/SKILL.md", selected)
        self.assertEqual(manifest["provider_binding"]["quality_tier"], "fast_scan")

    def test_inventory_ignores_skill_symlinks_outside_third_party(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            root = base / "repo"
            skill_root = root / ".claude" / "skills"
            trusted = root / "third_party" / "vendor" / "skills" / "trusted"
            escaped = base / "outside"
            trusted.mkdir(parents=True)
            escaped.mkdir()
            skill_root.mkdir(parents=True)
            (trusted / "SKILL.md").write_text(
                "---\nname: trusted-linked\n---\n", encoding="utf-8"
            )
            (escaped / "SKILL.md").write_text(
                "---\nname: escaped-linked\n---\n", encoding="utf-8"
            )
            (skill_root / "trusted").symlink_to(trusted)
            (skill_root / "escaped").symlink_to(escaped)

            sources = {
                item["source"] for item in build_asset_inventory(root)["entries"]
            }
            self.assertIn(".claude/skills/trusted/SKILL.md", sources)
            self.assertNotIn(".claude/skills/escaped/SKILL.md", sources)


class ProviderExecutionProfileTests(unittest.TestCase):
    def test_tiers_have_distinct_executable_profiles(self) -> None:
        registry = load_data(ROOT / ".claude" / "registry" / "providers" / "core.yaml")
        bindings = {
            tier: resolve_provider_quality(registry, "claude", tier)
            for tier in (
                "reasoning_high",
                "implementation",
                "fast_scan",
                "independent_critic",
            )
        }
        args = {
            tuple(binding["execution_profile"]["args"]) for binding in bindings.values()
        }
        self.assertEqual(len(args), 4)
        self.assertEqual(
            bindings["independent_critic"]["context_policy"], "fresh_required"
        )
        codex = resolve_provider_quality(registry, "codex", "implementation")
        self.assertEqual(
            codex["host_tool_contracts"],
            [
                {
                    "id": "codex.image-generation",
                    "tool": "image_gen__imagegen",
                    "alias": "$imagegen",
                    "schema_model_field": None,
                    "model_binding": "trusted-host-fixed",
                    "required_model": "gpt-image-2",
                    "hook_interception": False,
                }
            ],
        )

        manifest = subprocess.run(
            [
                sys.executable,
                str(SCRIPTS / "harness-context.py"),
                "--quality-tier",
                "independent_critic",
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
        )
        binding = json.loads(manifest.stdout)["provider_binding"]
        self.assertEqual(binding["context_policy"], "fresh_required")
        self.assertEqual(binding["execution_profile"]["args"], ["--effort", "max"])

    def test_orchestrator_consumes_profile_and_rejects_resume(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            plan = Path(temporary) / "plan.json"
            plan.write_text(
                json.dumps(
                    {
                        "session": "tier-profile",
                        "provider": "claude",
                        "quality_tier": "fast_scan",
                        "workers": [{"name": "one", "task": "scan"}],
                    }
                ),
                encoding="utf-8",
            )
            result = subprocess.run(
                [sys.executable, str(SCRIPTS / "orchestrate-worktrees.py"), str(plan)],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=True,
            )
            self.assertIn(
                "claude -p --effort low --no-session-persistence", result.stdout
            )

            plan.write_text(
                json.dumps(
                    {
                        "session": "resume-block",
                        "provider": "claude",
                        "quality_tier": "implementation",
                        "launcher": "claude -c -p",
                        "allow_custom_launcher": True,
                        "launcher_approval": "test",
                        "workers": [{"name": "one", "task": "work"}],
                    }
                ),
                encoding="utf-8",
            )
            blocked = subprocess.run(
                [sys.executable, str(SCRIPTS / "orchestrate-worktrees.py"), str(plan)],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertNotEqual(blocked.returncode, 0)
            self.assertIn("resuming a session", blocked.stderr)

        for command in ("multi-plan.md", "multi-execute.md"):
            content = (ROOT / ".claude" / "commands" / command).read_text(
                encoding="utf-8"
            )
            self.assertNotIn("codex-mini", content)
            self.assertIn("model: inherit", content)


class StackSemanticsTests(unittest.TestCase):
    def test_generated_dependency_lanes_match_recommended_compatibility(self) -> None:
        verifier = load_stack_verifier()
        web = verifier.yaml.load(
            (ROOT / ".claude/registry/tech-stacks/web-nextjs.yaml").read_text(
                encoding="utf-8"
            ),
            Loader=verifier.UniqueKeyLoader,
        )
        eslint = web["components"]["eslint"]
        self.assertEqual(eslint["latest_observed"]["version"], "10.7.0")
        self.assertEqual(eslint["recommended"]["version"], "9.39.5")

        boilerplate = ROOT / ".claude/skills/💻 개발/nextjs-boilerplate-skill"
        package = json.loads(
            (boilerplate / "templates/base/package.json.template")
            .read_text(encoding="utf-8")
            .replace("{{PROJECT_NAME}}", "compatibility-fixture")
        )
        self.assertEqual(package["devDependencies"]["eslint"], "^9.39.5")
        postcss = (
            boilerplate / "templates/base/postcss.config.mjs.template"
        ).read_text(encoding="utf-8")
        self.assertIn("const config = {", postcss)
        self.assertIn("export default config", postcss)
        self.assertNotIn("export default {", postcss)

        project_setup = (
            ROOT
            / ".claude/skills/💻 개발/fastapi-agent-skills/1-project-setup/SKILL.md"
        ).read_text(encoding="utf-8")
        pyproject_block = (
            project_setup.split("### pyproject.toml", 1)[1]
            .split("```toml", 1)[1]
            .split("```", 1)[0]
        )
        pyproject = tomllib.loads(pyproject_block)
        base = pyproject["project"]["dependencies"]
        self.assertFalse(any(item.startswith("redis") for item in base))
        self.assertFalse(any(item.startswith("celery") for item in base))
        self.assertFalse(any(item.startswith("arq") for item in base))

        extras = pyproject["project"]["optional-dependencies"]
        self.assertEqual(extras["redis-direct"], ["redis>=8.0.1,<9.0"])
        self.assertEqual(extras["broker-celery"], ["celery[redis]>=5.6.3,<6.0"])
        self.assertEqual(extras["broker-arq"], ["arq>=0.28.0,<0.29"])
        conflicts = {
            frozenset(next(iter(selector.items())) for selector in pair)
            for pair in pyproject["tool"]["uv"]["conflicts"]
        }
        self.assertEqual(
            conflicts,
            {
                frozenset({("extra", "redis-direct"), ("extra", "broker-celery")}),
                frozenset({("extra", "redis-direct"), ("extra", "broker-arq")}),
                frozenset({("extra", "broker-celery"), ("extra", "broker-arq")}),
            },
        )

    def test_version_parser_rejects_malformed_and_impossible_ranges(self) -> None:
        verifier = load_stack_verifier()
        self.assertIsNone(verifier.parse_version("latest"))
        self.assertIsNone(verifier.parse_version("1..2"))
        self.assertIsNotNone(verifier.parse_version("1.43.0/0.64b0"))

        component = {
            "latest_observed": {"version": "2.0.0", "channel": "stable"},
            "recommended": {"version": "1.9.0", "channel": "stable"},
            "compatibility_floor": {"version": "3.0.0", "channel": "stable"},
            "prerelease": None,
        }
        results = verifier.Results()
        verifier.validate_component_version_semantics(
            component, "test.component", results
        )
        self.assertTrue(
            any(
                "compatibility_floor cannot exceed recommended" in e
                for e in results.errors
            )
        )

        component["compatibility_floor"]["version"] = "1.0.0"
        component["prerelease"] = {"version": "2.1.0+build.1", "channel": "candidate"}
        results = verifier.Results()
        verifier.validate_component_version_semantics(
            component, "test.component", results
        )
        self.assertTrue(
            any("must include a prerelease suffix" in e for e in results.errors)
        )

    def test_current_api_regressions_are_absent_and_verifier_passes(self) -> None:
        scan_roots = [ROOT / ".claude" / "agents", ROOT / ".claude" / "skills"]
        content = "\n".join(
            path.read_text(encoding="utf-8", errors="replace")
            for scan_root in scan_roots
            for path in scan_root.rglob("*.md")
            if "_vendor" not in path.parts and "archive" not in path.parts
        )
        for stale in (
            ".valueOrNull",
            "CounterRef ref",
            ".queryParams['",
            "self._redis.close()",
        ):
            self.assertNotIn(stale, content)
        result = subprocess.run(
            [sys.executable, str(SCRIPTS / "verify-stack-registry.py"), "--all"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
        )
        self.assertIn("PASS stack-registry", result.stdout)


if __name__ == "__main__":
    unittest.main()
