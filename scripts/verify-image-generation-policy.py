#!/usr/bin/env python3
"""Verify every active image-generation surface against the Gongnyang policy."""

from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / ".claude/registry/providers/image-generation.yaml"
PROVIDER_CORE = ROOT / ".claude/registry/providers/core.yaml"
PACK = ROOT / ".claude/project-packs/image-generation/pack.json"
DEFAULT_PACK = ROOT / ".claude/project-packs/default/pack.json"
DESIGN_RUNTIME_PACK = ROOT / ".claude/project-packs/design-runtime/pack.json"
CANONICAL_SOURCE_MARKER = ROOT / ".claude/project-packs/.canonical-source"
FULL_SCOPE_MARKER = ROOT / ".claude/project-packs/default.scope.json"
DESIGN_SCOPE_MARKER = ROOT / ".claude/project-packs/design-runtime.scope.json"
MODEL_GUARD = ROOT / ".claude/hooks/image-generation-guard.py"
VENDOR_LOCK = ROOT / "third_party/gongnyang-prompt-kit/UPSTREAM.lock.json"

SCAN_ROOTS = (
    ".claude/agents",
    ".claude/skills",
    ".claude/rules",
    ".claude/commands",
    "contexts",
    "scripts",
)
TEXT_SUFFIXES = {
    ".cjs",
    ".js",
    ".json",
    ".jsx",
    ".md",
    ".mjs",
    ".py",
    ".sh",
    ".toml",
    ".ts",
    ".tsx",
    ".txt",
    ".yaml",
    ".yml",
}
EXCLUDED_PARTS = {"archive", "plans", "__pycache__"}
POLICY_TEST_FILES = {
    "scripts/test-gongnyang-image-path.sh",
    "scripts/verify-gongnyang-prompt-kit.sh",
    "scripts/verify-image-generation-policy.py",
}

MANIFEST_SURFACES = {
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
}

MANIFEST_CONTRACT_MARKERS = (
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

REQUIRED_SURFACES = (
    ".claude/agents/🎨 디자인/ui-design-agent/ui-design-agent-unified.md",
    ".claude/agents/📝 콘텐츠/emoticon/emoticon-animation-agent.md",
    ".claude/agents/📝 콘텐츠/emoticon/emoticon-concept-agent.md",
    ".claude/agents/📝 콘텐츠/emoticon/emoticon-orchestrator.md",
    ".claude/agents/📝 콘텐츠/presentation-agent.md",
    ".claude/agents/📝 콘텐츠/social-media-agent.md",
    ".claude/rules/common/imagegen-marketing-assets.md",
    ".claude/rules/common/presentation-quality-gate.md",
    ".claude/skills/banner-design/SKILL.md",
    ".claude/skills/brand/references/asset-organization.md",
    ".claude/skills/brand/references/update.md",
    ".claude/skills/brand/scripts/inject-brand-context.cjs",
    ".claude/skills/brand/templates/brand-guidelines-starter.md",
    ".claude/skills/design-harness/SKILL.md",
    ".claude/skills/design/SKILL.md",
    ".claude/skills/design/references/cip-design.md",
    ".claude/skills/design/references/cip-prompt-engineering.md",
    ".claude/skills/design/references/design-routing.md",
    ".claude/skills/design/references/icon-design.md",
    ".claude/skills/design/references/logo-design.md",
    ".claude/skills/design/references/logo-prompt-engineering.md",
    ".claude/skills/design/references/social-photos-design.md",
    ".claude/skills/design/scripts/cip/generate.py",
    ".claude/skills/design/scripts/logo/generate.py",
    ".claude/skills/logo-creator/SKILL.md",
    ".claude/skills/logo-creator/scripts/batch.py",
    ".claude/skills/📝 콘텐츠/future-slide-skills/future-slide-asset-gen/SKILL.md",
    ".claude/skills/📝 콘텐츠/future-slide-skills/future-slide-design/SKILL.md",
    ".claude/skills/📝 콘텐츠/future-slide-skills/future-slide-qa/references/replacement-rubric.md",
    ".claude/skills/📝 콘텐츠/future-slide-skills/future-slide-qa/scripts/check-tightened-deck.cjs",
    ".claude/skills/📝 콘텐츠/future-slide-skills/future-tightened-slide/SKILL.md",
    ".claude/skills/📝 콘텐츠/presentation-agent-skills/10-export-pptx/SKILL.md",
    ".claude/skills/📝 콘텐츠/presentation-agent-skills/7-image-gen/SKILL.md",
    ".claude/skills/📝 콘텐츠/social-media-agent-skills/3-compliance/SKILL.md",
    ".claude/skills/📝 콘텐츠/social-media-agent-skills/5-visual/SKILL.md",
    ".claude/skills/📣 마케팅/marketing-agent-skills/5-strategy/SKILL.md",
    ".claude/skills/📣 마케팅/seo-orchestrator-skills/2-content-optimizer/SKILL.md",
    ".claude/skills/📣 마케팅/seo-orchestrator-skills/5-social-scheduler/SKILL.md",
)

HIGH_SIGNAL_ALTERNATE = re.compile(
    r"gpt-image-1(?:\.5|\b)|dall[ -]?e|google[ -]?imagen|\bimagen(?:\s*[234])?\b|"
    r"nano[ -]?banana|midjourney|stable diffusion|\bsdxl\b|\bflux(?:\.\d+)?\b|"
    r"leonardo(?:\.ai)?|adobe[ -]?firefly|\bideogram\b|\brecraft\b|"
    r"stability\.ai|fal\.ai|replicate.{0,40}(?:image|flux|sdxl)",
    re.IGNORECASE,
)
GENERATION_INTENT = re.compile(
    r"\bimage[ -]?(?:gen|generation|generator)\b|"
    r"\bgenerat(?:e|es|ing)\s+(?:an?\s+)?(?:raster\s+)?"
    r"(?:image|graphic|infographic|illustration|logo|icon|banner|hero (?:asset|visual)|keyframe)s?\b|"
    r"(?:이미지|로고|아이콘|배너|비주얼|인포그래픽|일러스트|키프레임)\s*(?:를|을)?\s*생성|"
    r"생성형\s*(?:raster|이미지|비주얼)|AI\s*이미지",
    re.IGNORECASE,
)
AMBIGUOUS_PROVIDER = re.compile(r"\bgemini(?:-[\w.]+)?\b", re.IGNORECASE)
LOCAL_IMAGE_PROMPT = re.compile(
    r"^\s*(?:ai_?prompts?|image_?prompts?|negative_?prompt)\s*[:=]|"
    r"\[(?:AI\s*(?:image\s*)?prompt|AI\s*이미지\s*프롬프트)\]",
    re.IGNORECASE | re.MULTILINE,
)
POST_TEXT_COMMAND = re.compile(
    r"\bImageDraw\b|\bImageFont\b|\bdrawtext\b|"
    r"(?:magick|convert|mogrify)[^\n|;&]*(?:caption:|label:|pango:|-annotate\b)|"
    r"-draw\s+[^\n|;&]{0,100}\btext\b",
    re.IGNORECASE,
)
LEGACY_ATTESTED_MODEL_FIELD = re.compile(
    r"(?:[\"'`]model[\"'`]?|\bmodel)\s*:\s*[\"']gpt-image-2[\"']",
    re.IGNORECASE,
)

DETERMINISTIC_EXEMPTIONS = {
    ".claude/skills/💻 개발/flutter-agent-skills/16-golden-test/SKILL.md": (
        "flutter golden baseline",
        ("--update-goldens",),
    ),
    ".claude/skills/💻 개발/nextjs-agent-skills/25-seo/SKILL.md": (
        "Next.js ImageResponse",
        ("next/og", "ImageResponse"),
    ),
    ".claude/skills/📝 콘텐츠/presentation-agent-skills/6-visual/SKILL.md": (
        "Vega-Lite chart specification",
        ("Vega-Lite", "chart_generate"),
    ),
}


def line_for(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


def has_positive_generation_intent(text: str) -> bool:
    """Ignore matches that only prohibit image creation."""
    negative = re.compile(
        r"\b(?:do not|does not|must not|never|forbid(?:den)?|prohibit(?:ed)?)\b|"
        r"금지|생성하지\s*않|생성\s*불가|생성\s*없음",
        re.IGNORECASE,
    )
    for match in GENERATION_INTENT.finditer(text):
        line_start = text.rfind("\n", 0, match.start()) + 1
        line_end = text.find("\n", match.end())
        if line_end < 0:
            line_end = len(text)
        if not negative.search(text[line_start:line_end]):
            return True
    return False


def validate_manifest_contract(relative: str, content: str, errors: list[str]) -> None:
    """Reject model attestation claims and require the explicit host-trust contract."""
    legacy_model_field = LEGACY_ATTESTED_MODEL_FIELD.search(content)
    if legacy_model_field:
        errors.append(
            f"locally unverifiable model field in {relative}:"
            f"{line_for(content, legacy_model_field.start())}: "
            f"use required_model plus trusted-host assurance fields"
        )

    if relative not in MANIFEST_SURFACES:
        return
    missing_markers = [
        marker for marker in MANIFEST_CONTRACT_MARKERS if marker not in content
    ]
    if missing_markers:
        errors.append(
            f"image manifest contract incomplete in {relative}: "
            f"missing {', '.join(missing_markers)}"
        )


def read_json(path: Path) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(
            f"cannot read JSON-compatible policy {path.relative_to(ROOT)}: {exc}"
        ) from exc
    if not isinstance(value, dict):
        raise ValueError(f"policy root must be an object: {path.relative_to(ROOT)}")
    return value


def iter_active_files() -> list[tuple[str, Path]]:
    files: list[tuple[str, Path]] = []
    for root_name in SCAN_ROOTS:
        scan_root = ROOT / root_name
        if not scan_root.exists():
            continue
        for current, directories, names in os.walk(scan_root, followlinks=False):
            directories[:] = [
                name
                for name in directories
                if name not in EXCLUDED_PARTS
                and not (Path(current) / name).is_symlink()
            ]
            current_path = Path(current)
            if EXCLUDED_PARTS.intersection(current_path.parts):
                continue
            for name in names:
                path = current_path / name
                if path.is_symlink() or path.suffix.lower() not in TEXT_SUFFIXES:
                    continue
                relative = path.relative_to(ROOT).as_posix()
                files.append((relative, path))
    return sorted(files)


def validate_registry(errors: list[str]) -> None:
    try:
        policy = read_json(REGISTRY)
    except ValueError as exc:
        errors.append(str(exc))
        return

    expected = {
        "schema_version": "harness.image-generation-policy.v2",
        "id": "provider.image-generation",
    }
    for key, value in expected.items():
        if policy.get(key) != value:
            errors.append(f"provider registry {key} must be {value!r}")

    compiler = policy.get("prompt_compiler", {})
    try:
        vendor_lock = read_json(VENDOR_LOCK)
    except ValueError as exc:
        errors.append(str(exc))
        return
    compiler_expected = {
        "id": "image-prompt",
        "version": vendor_lock.get("skill_version"),
        "skill": ".claude/skills/image-prompt/SKILL.md",
        "validator": "third_party/gongnyang-prompt-kit/skills/image-prompt/scripts/check_prompt.mjs",
        "vendor_commit": vendor_lock.get("commit"),
        "local_patches": [],
        "upstream_provider_instructions_authoritative": False,
    }
    for key, value in compiler_expected.items():
        if compiler.get(key) != value:
            errors.append(f"provider registry prompt_compiler.{key} must be {value!r}")

    generation = policy.get("generation", {})
    generation_expected = {
        "provider": "codex",
        "tool_alias": "$imagegen",
        "host_tool": "image_gen__imagegen",
        "required_model": "gpt-image-2",
        "fallback": [],
        "input_mapping": {"full_prompt": "prompt"},
        "allowed_host_fields": [
            "prompt",
            "referenced_image_paths",
            "num_last_images_to_include",
        ],
        "model_binding": {
            "mode": "trusted-host-fixed",
            "parameter": None,
            "locally_observable": False,
            "enforcement_owner": "codex-host",
            "on_reported_mismatch": "block",
            "on_strict_without_attestation": "blocked_imagegen_model_unverifiable",
        },
    }
    for key, value in generation_expected.items():
        if generation.get(key) != value:
            errors.append(f"provider registry generation.{key} must be {value!r}")
    transparency = generation.get("transparency", {})
    if transparency != {"supported": False, "policy": "use-opaque-background-or-block"}:
        errors.append(
            "provider registry must mark transparency unsupported and use opaque-or-block policy"
        )
    assurance_expected = {
        "vendor_bytes": "locally-verified",
        "prompt_validation": "locally-verified",
        "active_routes": "static-scan-and-observable-route-denial",
        "model": "trusted-host-not-locally-observable",
        "allowed_provenance_claim": "generated_under_trusted_host_contract",
        "forbidden_provenance_claim": "verified_gpt_image_2",
    }
    if policy.get("assurance") != assurance_expected:
        errors.append("provider registry assurance boundary drifted")
    manifest_contract_expected = {
        "required_model": "gpt-image-2",
        "model_binding": "trusted-host-fixed",
        "local_model_verification": "unavailable",
        "host_reported_model": None,
        "pre_generation_assurance": "pending_trusted_host_generation",
        "post_generation_assurance": "generated_under_trusted_host_contract",
        "forbidden_fields": ["model"],
    }
    if policy.get("artifact_manifest_contract") != manifest_contract_expected:
        errors.append("provider registry artifact_manifest_contract drifted")

    try:
        provider_core = read_json(PROVIDER_CORE)
    except ValueError as exc:
        errors.append(str(exc))
        provider_core = {}
    codex = next(
        (
            item
            for item in provider_core.get("providers", [])
            if item.get("id") == "codex"
        ),
        {},
    )
    expected_host_contract = {
        "id": "codex.image-generation",
        "tool": "image_gen__imagegen",
        "alias": "$imagegen",
        "schema_model_field": None,
        "model_binding": "trusted-host-fixed",
        "required_model": "gpt-image-2",
        "hook_interception": False,
    }
    if codex.get("execution_adapter", {}).get("kind") != "host-native":
        errors.append("Codex image provider must use a host-native execution adapter")
    if codex.get("hook_support") != []:
        errors.append("Codex image policy must not claim local hook interception")
    if expected_host_contract not in codex.get("host_tool_contracts", []):
        errors.append(
            "Codex provider is missing the exact host image-generation contract"
        )

    expected_blocked_providers = {
        "adobe-firefly",
        "gemini-image-generation",
        "ideogram",
        "leonardo-ai",
        "midjourney",
        "recraft",
        "replicate",
        "stability-ai",
    }
    expected_blocked_models = {
        "dall-e",
        "flux",
        "gpt-image-1",
        "gpt-image-1.5",
        "imagen",
        "nano-banana",
        "sdxl",
    }
    if (
        set(policy.get("blocked_generation_providers", []))
        != expected_blocked_providers
    ):
        errors.append("provider registry blocked_generation_providers set drifted")
    if set(policy.get("blocked_generation_models", [])) != expected_blocked_models:
        errors.append("provider registry blocked_generation_models set drifted")

    expected_hooks = [
        {
            "provider": "claude",
            "scope": "observable-bash-routes-only",
            "event": "PreToolUse",
            "matcher": "Bash",
            "command": "$CLAUDE_PROJECT_DIR/third_party/gongnyang-prompt-kit/hooks/block-text-overlay.sh",
        },
        {
            "provider": "claude",
            "scope": "observable-bash-skill-mcp-routes",
            "event": "PreToolUse",
            "matcher": "Bash|Skill|mcp__.*",
            "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/image-generation-guard.py",
        },
    ]
    if policy.get("runtime_hooks") != expected_hooks:
        errors.append("provider registry runtime_hooks drifted")
    if not MODEL_GUARD.is_file() or not os.access(MODEL_GUARD, os.X_OK):
        errors.append("image model guard is missing or not executable")


def validate_pack(errors: list[str]) -> None:
    try:
        pack = read_json(PACK)
    except ValueError as exc:
        errors.append(str(exc))
        return
    required_paths = {
        ".claude/project-packs/image-generation/pack.json",
        "third_party/gongnyang-prompt-kit",
        ".claude/hooks/image-generation-guard.py",
        ".claude/skills/image-prompt",
        ".claude/rules/common/imagegen-marketing-assets.md",
        ".claude/registry/providers/image-generation.yaml",
        "scripts/verify-gongnyang-prompt-kit.sh",
        "scripts/verify-image-generation-policy.py",
        "scripts/test-gongnyang-image-path.sh",
        "scripts/update-gongnyang-prompt-kit.sh",
    }
    missing = sorted(required_paths - set(pack.get("paths", [])))
    if missing:
        errors.append(f"image-generation pack missing paths: {', '.join(missing)}")
    merges = pack.get("settings_merges", [])
    if len(merges) != 2:
        errors.append("image-generation pack must declare exactly two settings merges")
        return
    commands = set()
    for merge in merges:
        if (
            merge.get("operation") != "append-if-missing"
            or merge.get("target") != ".claude/settings.json"
        ):
            errors.append(
                "image-generation settings merges must be idempotent append-if-missing"
            )
        commands.add(merge.get("value", {}).get("command"))
    expected = {
        "$CLAUDE_PROJECT_DIR/third_party/gongnyang-prompt-kit/hooks/block-text-overlay.sh",
        "$CLAUDE_PROJECT_DIR/.claude/hooks/image-generation-guard.py",
    }
    if commands != expected:
        errors.append("image-generation settings merge hooks drifted")


def validate_scope_marker(
    path: Path, expected: dict[str, str], errors: list[str]
) -> bool:
    if not path.is_file():
        return False
    try:
        marker = read_json(path)
    except ValueError as exc:
        errors.append(str(exc))
        return True
    if marker != expected:
        errors.append(f"installation scope marker drifted: {path.relative_to(ROOT)}")
    return True


def required_surfaces_for_installation(errors: list[str]) -> tuple[str, ...]:
    """Bind required routes to a recognized full or selective distribution pack."""
    full = validate_scope_marker(
        FULL_SCOPE_MARKER,
        {
            "schema": "harness.installation-scope.v1",
            "scope": "full",
            "base_pack": "default",
        },
        errors,
    )
    selective = validate_scope_marker(
        DESIGN_SCOPE_MARKER,
        {
            "schema": "harness.installation-scope.v1",
            "scope": "selective-design-runtime",
            "base_pack": "design-runtime",
        },
        errors,
    )
    canonical_source = CANONICAL_SOURCE_MARKER.is_file()
    if canonical_source:
        if not full or not DEFAULT_PACK.is_file():
            errors.append(
                "canonical source is missing the full installation scope contract"
            )
            return ()
        return REQUIRED_SURFACES
    if full and selective:
        errors.append(
            "ambiguous image-policy installation: both full and selective base packs are present"
        )
        return ()
    if full:
        if not DEFAULT_PACK.is_file():
            errors.append("full installation scope is missing the default pack")
            return ()
        return REQUIRED_SURFACES
    if not selective:
        errors.append(
            "image-policy verifier requires a full default pack or the selective design-runtime pack"
        )
        return ()
    if not DESIGN_RUNTIME_PACK.is_file():
        errors.append(
            "selective design-runtime scope is missing its declared base pack"
        )
        return ()

    try:
        design_pack = read_json(DESIGN_RUNTIME_PACK)
    except ValueError as exc:
        errors.append(str(exc))
        return ()
    declared = design_pack.get("image_policy_required_surfaces")
    if not isinstance(declared, list) or not declared:
        errors.append(
            "selective design-runtime pack must declare image_policy_required_surfaces"
        )
        return ()
    if any(not isinstance(path, str) for path in declared):
        errors.append("selective image-policy routes must be strings")
        return ()
    unknown = sorted(set(declared) - set(REQUIRED_SURFACES))
    if unknown:
        errors.append(
            "selective design-runtime pack declares unknown image-policy routes: "
            + ", ".join(unknown)
        )
    return tuple(dict.fromkeys(declared))


def main() -> int:
    errors: list[str] = []
    generative_surfaces: set[str] = set()
    deterministic_exemptions_used: dict[str, str] = {}

    validate_registry(errors)
    validate_pack(errors)
    required_surfaces = required_surfaces_for_installation(errors)

    for relative in required_surfaces:
        path = ROOT / relative
        if not path.is_file():
            errors.append(f"missing required image-policy surface: {relative}")
            continue
        if "image-prompt" not in path.read_text(encoding="utf-8"):
            errors.append(
                f"required surface does not reference image-prompt: {relative}"
            )

    for relative, path in iter_active_files():
        try:
            content = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        policy_test = relative in POLICY_TEST_FILES

        if not policy_test:
            validate_manifest_contract(relative, content, errors)

            alternate = HIGH_SIGNAL_ALTERNATE.search(content)
            if alternate:
                errors.append(
                    f"alternate image generation provider/model in {relative}:"
                    f"{line_for(content, alternate.start())}: {alternate.group(0)}"
                )

            for provider in AMBIGUOUS_PROVIDER.finditer(content):
                window = content[max(0, provider.start() - 240) : provider.end() + 240]
                if has_positive_generation_intent(window):
                    errors.append(
                        f"alternate image-generation provider in {relative}:"
                        f"{line_for(content, provider.start())}: {provider.group(0)}"
                    )
                    break

            prompt_definition = LOCAL_IMAGE_PROMPT.search(content)
            if prompt_definition:
                errors.append(
                    f"local image prompt definition in {relative}:"
                    f"{line_for(content, prompt_definition.start())}: {prompt_definition.group(0).strip()}"
                )

            overlay = POST_TEXT_COMMAND.search(content)
            if overlay:
                errors.append(
                    f"post-generation text command in {relative}:"
                    f"{line_for(content, overlay.start())}: {overlay.group(0)}"
                )

        if not has_positive_generation_intent(content):
            continue
        generative_surfaces.add(relative)
        if "image-prompt" in content or "imagegen-marketing-assets.md" in content:
            continue
        exemption = DETERMINISTIC_EXEMPTIONS.get(relative)
        if exemption and all(marker in content for marker in exemption[1]):
            deterministic_exemptions_used[relative] = exemption[0]
            continue
        errors.append(
            f"generative image surface does not route through image-prompt: {relative}"
        )

    if errors:
        print("IMAGE GENERATION POLICY: FAIL", file=sys.stderr)
        for error in sorted(set(errors)):
            print(f"- {error}", file=sys.stderr)
        return 1

    print(
        "LOCAL IMAGE CONTROLS: PASS "
        f"({len(generative_surfaces)} active generative surfaces; "
        f"{len(required_surfaces)} required routes; "
        f"{len(deterministic_exemptions_used)} deterministic exemptions)"
    )
    for relative, reason in sorted(deterministic_exemptions_used.items()):
        print(f"EXEMPT deterministic: {relative} ({reason})")
    print(
        "HOST MODEL BOUNDARY: TRUSTED, NOT LOCALLY OBSERVABLE "
        "(Codex image_gen__imagegen contract requires gpt-image-2; no fallback)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
