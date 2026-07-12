from __future__ import annotations

import importlib.util
import json
import re
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
POLICY = ROOT / ".claude" / "registry" / "providers" / "image-generation.yaml"
CORE = ROOT / ".claude" / "registry" / "providers" / "core.yaml"
GUARD = ROOT / ".claude" / "hooks" / "image-generation-guard.py"
VERIFIER = ROOT / "scripts" / "verify-image-generation-policy.py"
SETTINGS = ROOT / ".claude" / "settings.json"


class ImagePolicyBoundaryTests(unittest.TestCase):
    def guard(self, payload: dict) -> str:
        result = subprocess.run(
            [sys.executable, str(GUARD)],
            cwd=ROOT,
            input=json.dumps(payload),
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        return result.stdout

    def test_codex_policy_declares_host_trust_without_fake_hook_support(self) -> None:
        policy = json.loads(POLICY.read_text(encoding="utf-8"))
        core = json.loads(CORE.read_text(encoding="utf-8"))
        generation = policy["generation"]
        self.assertEqual(generation["host_tool"], "image_gen__imagegen")
        self.assertEqual(generation["input_mapping"], {"full_prompt": "prompt"})
        self.assertEqual(
            generation["allowed_host_fields"],
            ["prompt", "referenced_image_paths", "num_last_images_to_include"],
        )
        self.assertEqual(generation["required_model"], "gpt-image-2")
        self.assertFalse(generation["model_binding"]["locally_observable"])
        self.assertEqual(
            policy["assurance"]["model"], "trusted-host-not-locally-observable"
        )
        self.assertEqual(
            policy["assurance"]["forbidden_provenance_claim"], "verified_gpt_image_2"
        )
        self.assertEqual(
            policy["artifact_manifest_contract"],
            {
                "required_model": "gpt-image-2",
                "model_binding": "trusted-host-fixed",
                "local_model_verification": "unavailable",
                "host_reported_model": None,
                "pre_generation_assurance": "pending_trusted_host_generation",
                "post_generation_assurance": "generated_under_trusted_host_contract",
                "forbidden_fields": ["model"],
            },
        )
        self.assertTrue(
            all(item["provider"] == "claude" for item in policy["runtime_hooks"])
        )
        guard_hook = next(
            item
            for item in policy["runtime_hooks"]
            if item["command"].endswith("image-generation-guard.py")
        )
        self.assertEqual(guard_hook["matcher"], "Bash|Skill|mcp__.*")
        settings = json.loads(SETTINGS.read_text(encoding="utf-8"))
        configured = next(
            item
            for item in settings["hooks"]["PreToolUse"]
            if any(
                hook.get("command", "").endswith("image-generation-guard.py")
                for hook in item.get("hooks", [])
            )
        )
        self.assertEqual(configured["matcher"], "Bash|Skill|mcp__.*")

        codex = next(item for item in core["providers"] if item["id"] == "codex")
        self.assertEqual(codex["hook_support"], [])
        contract = next(
            item
            for item in codex["host_tool_contracts"]
            if item["id"] == "codex.image-generation"
        )
        self.assertEqual(contract["tool"], "image_gen__imagegen")
        self.assertIsNone(contract["schema_model_field"])
        self.assertFalse(contract["hook_interception"])

    def test_active_manifest_surfaces_do_not_claim_local_model_attestation(
        self,
    ) -> None:
        surfaces = (
            ".claude/skills/banner-design/SKILL.md",
            ".claude/skills/brand/references/asset-organization.md",
            ".claude/skills/design/SKILL.md",
            ".claude/skills/design/scripts/cip/generate.py",
            ".claude/skills/design/scripts/logo/generate.py",
            ".claude/skills/logo-creator/SKILL.md",
            ".claude/skills/📝 콘텐츠/future-slide-skills/future-slide-asset-gen/SKILL.md",
            ".claude/skills/📝 콘텐츠/future-slide-skills/future-slide-qa/references/replacement-rubric.md",
            ".claude/skills/📝 콘텐츠/future-slide-skills/future-slide-qa/scripts/check-tightened-deck.cjs",
            ".claude/skills/📝 콘텐츠/presentation-agent-skills/10-export-pptx/SKILL.md",
            ".claude/skills/📝 콘텐츠/presentation-agent-skills/7-image-gen/SKILL.md",
            ".claude/skills/📝 콘텐츠/social-media-agent-skills/5-visual/SKILL.md",
        )
        markers = (
            "image_gen__imagegen",
            "required_model",
            "gpt-image-2",
            "model_binding",
            "trusted-host-fixed",
            "local_model_verification",
            "unavailable",
            "generation_assurance",
            "generated_under_trusted_host_contract",
            "host_reported_model",
        )
        for relative in surfaces:
            with self.subTest(relative=relative):
                content = (ROOT / relative).read_text(encoding="utf-8")
                self.assertIsNone(
                    re.search(
                        r'(?m)(?:["\x27]model["\x27]|^\s*model)\s*:\s*["\x27]gpt-image-2["\x27]',
                        content,
                    )
                )
                for marker in markers:
                    self.assertIn(marker, content)

    def test_policy_verifier_rejects_a_synthetic_local_model_claim(self) -> None:
        spec = importlib.util.spec_from_file_location("image_policy_verifier", VERIFIER)
        self.assertIsNotNone(spec)
        self.assertIsNotNone(spec.loader)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        errors: list[str] = []
        module.validate_manifest_contract(
            ".claude/skills/banner-design/SKILL.md",
            '{"model": "gpt-image-2"}',
            errors,
        )
        self.assertTrue(
            any("locally unverifiable model field" in error for error in errors)
        )
        self.assertTrue(
            any("image manifest contract incomplete" in error for error in errors)
        )

    def test_claude_observable_generation_routes_are_denied(self) -> None:
        cases = (
            {
                "tool_name": "Skill",
                "tool_input": {"skill": "imagegen", "model": "gpt-image-2"},
            },
            {"tool_name": "image_gen__imagegen", "tool_input": {"prompt": "synthetic"}},
            {
                "tool_name": "Bash",
                "tool_input": {
                    "command": "curl https://api.openai.com/v1/images/generations -d model=gpt-image-2"
                },
            },
            {"tool_name": "mcp__foo__create_picture", "tool_input": {"prompt": "x"}},
            {"tool_name": "mcp__fal__generate", "tool_input": {"prompt": "x"}},
            {
                "tool_name": "mcp__openai__images_generate",
                "tool_input": {"prompt": "x"},
            },
            {"tool_name": "mcp__foo__render_art", "tool_input": {"prompt": "x"}},
            {
                "tool_name": "mcp__media__invoke",
                "tool_input": {"operation": "generate", "type": "image", "prompt": "x"},
            },
        )
        for payload in cases:
            with self.subTest(payload=payload):
                self.assertIn('"permissionDecision": "deny"', self.guard(payload))

    def test_gongnyang_compiler_skill_is_allowed(self) -> None:
        output = self.guard(
            {
                "tool_name": "Skill",
                "tool_input": {
                    "skill": "image-prompt",
                    "args": "compile this request and avoid a Stable Diffusion look",
                },
            }
        )
        self.assertEqual(output, "")

    def test_read_only_image_references_and_analysis_routes_are_allowed(self) -> None:
        cases = (
            {
                "tool_name": "Skill",
                "tool_input": {
                    "skill": "review-security",
                    "args": "Audit references to DALL-E without generating images",
                },
            },
            {
                "tool_name": "Bash",
                "tool_input": {"command": "rg -n 'stable diffusion' docs"},
            },
            {
                "tool_name": "mcp__vision__analyze_image",
                "tool_input": {"prompt": "Check whether this says generate image"},
            },
            {
                "tool_name": "mcp__catalog__search_images",
                "tool_input": {"query": "poster"},
            },
        )
        for payload in cases:
            with self.subTest(payload=payload):
                self.assertEqual(self.guard(payload), "")

    def test_strict_model_attestation_fails_closed(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts" / "harness-doctor.py"),
                "--require-host-model-attestation",
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("blocked_imagegen_model_unverifiable", result.stdout)


if __name__ == "__main__":
    unittest.main()
