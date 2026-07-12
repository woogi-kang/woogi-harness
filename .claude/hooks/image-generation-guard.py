#!/usr/bin/env python3
"""Deny image-generation routes observable to Claude Code hooks.

Codex host-native ``image_gen__imagegen`` calls are outside this hook boundary.
They are governed by the explicit trusted-host contract in the image provider
registry; this hook never claims to attest the model selected by that host.
"""

from __future__ import annotations

import json
import re
import sys


BLOCKED = re.compile(
    r"(?<![\w-])(?:gpt-image-1(?:\.5)?|dall[ -]?e|imagen(?:\s*[234])?|"
    r"nano[ -]?banana|midjourney|stable diffusion|sdxl|flux(?:\.\d+)?|"
    r"adobe[ -]?firefly|ideogram|recraft|leonardo(?:\.ai)?|stability\.ai|"
    r"replicate)(?![\w-])",
    re.IGNORECASE,
)
DIRECT_IMAGE_TOOLS = frozenset(
    {
        "$imagegen",
        "imagegen",
        "image_gen",
        "image_gen.imagegen",
        "image_gen__imagegen",
    }
)
ALLOWED_COMPILER_SKILLS = frozenset({"image-prompt"})
GENERATION_VERB = r"(?:generate|create|render|synthesi[sz]e|edit|variation|upscale|invoke|predict|run)"
IMAGE_OBJECT = r"(?:images?|pictures?|photos?|illustrations?|art|artworks?|graphics?|posters?|logos?|icons?)"
OBSERVABLE_BASH_IMAGE_ROUTE = re.compile(
    r"(?:/v1/images(?:/generations|/edits)?\b|"
    r"\bimages\.(?:generate|edit)\s*\(|"
    r"\b(?:openai\s+)?images?\s+(?:generate|edit)\b|"
    r"\bimage_gen__imagegen\b|\bimagegen\s+(?:generate|edit)\b|"
    r"\b(?:replicate|fal|midjourney|ideogram|recraft|leonardo)\s+"
    r"(?:run|predict|generate|create|render|edit)\b)",
    re.IGNORECASE,
)
NAMED_IMAGE_GENERATION_ROUTE = re.compile(
    rf"(?:{GENERATION_VERB}[_-]?{IMAGE_OBJECT}|{IMAGE_OBJECT}[_-]?{GENERATION_VERB})",
    re.IGNORECASE,
)
KNOWN_MCP_IMAGE_PROVIDER = re.compile(
    r"(?:^|__)(?:fal|midjourney|stability|stable[_-]?diffusion|ideogram|recraft|"
    r"leonardo|imagen|replicate)(?:__|$)",
    re.IGNORECASE,
)
GENERATION_NAME = re.compile(GENERATION_VERB, re.IGNORECASE)


def deny(reason: str) -> None:
    print(
        json.dumps(
            {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "deny",
                    "permissionDecisionReason": reason,
                }
            },
            ensure_ascii=False,
        )
    )


def selected_skill(tool_input: object) -> str:
    if not isinstance(tool_input, dict):
        return ""
    return (
        str(
            tool_input.get("skill")
            or tool_input.get("name")
            or tool_input.get("id")
            or ""
        )
        .lower()
        .lstrip("$")
    )


def mcp_input_declares_generation(tool_input: object) -> bool:
    if not isinstance(tool_input, dict):
        return False
    operation = " ".join(
        str(tool_input.get(key, ""))
        for key in ("operation", "action", "task", "mode", "method")
    )
    media = " ".join(
        str(tool_input.get(key, ""))
        for key in ("media_type", "output_type", "artifact_type", "kind", "type")
    )
    return (
        GENERATION_NAME.search(operation) is not None
        and re.search(IMAGE_OBJECT, media, re.IGNORECASE) is not None
    )


def is_generation_route(tool_name: str, tool_input: object) -> bool:
    """Identify observable execution routes before inspecting provider/model text."""
    if tool_name in DIRECT_IMAGE_TOOLS:
        return True
    if tool_name == "bash":
        command = (
            str(tool_input.get("command", "")) if isinstance(tool_input, dict) else ""
        )
        return OBSERVABLE_BASH_IMAGE_ROUTE.search(command) is not None
    if tool_name == "skill":
        skill_name = selected_skill(tool_input)
        return skill_name in {value.lstrip("$") for value in DIRECT_IMAGE_TOOLS}

    normalized_name = tool_name.replace("-", "_").replace(".", "_")
    if NAMED_IMAGE_GENERATION_ROUTE.search(normalized_name):
        return True
    if tool_name.startswith("mcp__"):
        if KNOWN_MCP_IMAGE_PROVIDER.search(tool_name) and GENERATION_NAME.search(
            tool_name
        ):
            return True
        return mcp_input_declares_generation(tool_input)
    return False


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, UnicodeDecodeError):
        deny(
            "Image policy guard could not parse tool input; refusing an unverifiable call."
        )
        return 0

    tool_name = str(payload.get("tool_name", "")).lower()
    tool_input = payload.get("tool_input", {})
    if tool_name == "skill" and selected_skill(tool_input) in ALLOWED_COMPILER_SKILLS:
        return 0
    if not is_generation_route(tool_name, tool_input):
        return 0

    route_payload = json.dumps(
        {"tool_name": tool_name, "tool_input": tool_input},
        ensure_ascii=False,
        sort_keys=True,
    )
    match = BLOCKED.search(route_payload)
    if match:
        deny(
            f"Blocked alternate image provider/model '{match.group(0)}' on an observable "
            "image-generation route. Only the exact Gongnyang compiler and Codex "
            "trusted-host image contract are permitted."
        )
    else:
        deny(
            f"Observable image-generation route '{tool_name}' is forbidden inside the "
            "Claude hook boundary. Compile with Skill(image-prompt), then use Codex "
            "host-native $imagegen; no fallback is permitted."
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
