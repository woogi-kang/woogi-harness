#!/usr/bin/env python3
"""Design Runtime v3: create, collect, and validate evidence-backed design runs.

The script intentionally uses only the Python standard library so project packs can
run it before application dependencies are installed. It does not render UI itself;
browser and Flutter adapters create artifacts, and this runtime verifies provenance,
coverage, critic independence, and bounded repair state.
"""

from __future__ import annotations

import argparse
import base64
import binascii
import datetime as dt
import hashlib
import json
import os
import re
import secrets
import shutil
import struct
import subprocess
import sys
import tempfile
import zlib
from pathlib import Path
from typing import Any


SCHEMA_RUN = "design-run-v3"
SCHEMA_EVIDENCE = "design-evidence-manifest-v1"
SCHEMA_CRITIC = "design-critic-result-v1"
RUNTIME_DIR = Path(__file__).resolve().parents[3]
PLATFORM_REGISTRY = RUNTIME_DIR / "registry" / "design" / "platforms.json"
SOURCE_POLICY = RUNTIME_DIR / "registry" / "design" / "source-policy.json"
PROVIDER_REGISTRY = RUNTIME_DIR / "registry" / "providers" / "core.yaml"
DETECTOR = (
    RUNTIME_DIR / "skills" / "design-harness" / "scripts" / "detect-design-slop.mjs"
)
GRADER = RUNTIME_DIR / "evals" / "ui-design" / "grader.py"
TRUSTED_PRODUCERS = {
    "capture-web-evidence@1",
    "capture-flutter-evidence@1",
    "design-runtime-detector@1",
    "ui-design-grader@3",
}
_SOURCE_POLICY_DATA = json.loads(SOURCE_POLICY.read_text(encoding="utf-8"))
SKIP_PARTS = set(_SOURCE_POLICY_DATA["skip_directories"])
FINGERPRINT_NAMES = {
    "package.json",
    "pubspec.yaml",
    "components.json",
    "tailwind.config.js",
    "tailwind.config.ts",
    "vite.config.js",
    "vite.config.ts",
    "next.config.js",
    "next.config.mjs",
    "next.config.ts",
    "analysis_options.yaml",
    "theme.dart",
    "app_theme.dart",
    "design.md",
    "DESIGN.md",
    "PRODUCT.md",
}
FINGERPRINT_SUFFIXES = (
    "tokens.css",
    "theme.css",
    "globals.css",
    "colors.dart",
    "typography.dart",
)
UI_SOURCE_SUFFIXES = set(_SOURCE_POLICY_DATA["extensions"])
REVIEW_PACKET_SCHEMA = "design-review-packet-v1"
CRITIC_ATTESTATION_SCHEMA = "design-critic-attestation-v1"
CAPTURE_ATTESTATION_SCHEMA = "design-capture-attestation-v1"
DESIGN_TRUST_STORE = RUNTIME_DIR / "registry" / "design" / "trusted-authorities.json"


def utc_now() -> str:
    return (
        dt.datetime.now(dt.timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    temporary.replace(path)


def read_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot read JSON {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise ValueError(f"expected JSON object: {path}")
    return payload


def path_is_within(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
    except ValueError:
        return False
    return True


def canonical_capture_adapter(platform: str) -> Path:
    if platform == "web":
        return (
            RUNTIME_DIR
            / "skills"
            / "design-harness"
            / "scripts"
            / "capture-web-evidence.mjs"
        )
    if platform == "flutter":
        return (
            RUNTIME_DIR
            / "skills"
            / "design-harness"
            / "scripts"
            / "capture-flutter-evidence.py"
        )
    raise ValueError(f"no trusted capture adapter for platform: {platform}")


def trusted_critic_binding(public_key: Path) -> dict[str, str]:
    """Resolve a key only through the runtime-distributed authority registry."""
    requested_store = DESIGN_TRUST_STORE
    if requested_store.is_symlink():
        raise ValueError("critic trust store may not be a symlink")
    store_path = requested_store.resolve()
    if not store_path.is_file():
        raise ValueError(f"critic trust store does not exist: {store_path}")
    store = read_json(store_path)
    if store.get("schema") != "design-critic-trust-store-v1":
        raise ValueError(
            "critic trust store schema must be design-critic-trust-store-v1"
        )
    key_hash = sha256_file(public_key)
    authorities = store.get("authorities")
    if not isinstance(authorities, list):
        raise ValueError("critic trust store authorities must be an array")
    matches = [
        authority
        for authority in authorities
        if isinstance(authority, dict)
        and authority.get("status") == "active"
        and authority.get("public_key_sha256") == key_hash
    ]
    if len(matches) != 1:
        raise ValueError(
            "critic public key is not uniquely pinned as active in the canonical runtime trust store; "
            "an init-supplied key or caller-selected store is not a trust root"
        )
    authority = matches[0]
    authority_id = authority.get("id")
    if not isinstance(authority_id, str) or len(authority_id.strip()) < 3:
        raise ValueError("trusted critic authority id is invalid")
    purposes = authority.get("purposes")
    if not isinstance(purposes, list) or not {"capture", "critic"}.issubset(
        {str(value) for value in purposes}
    ):
        raise ValueError(
            "trusted authority must be pinned for both capture and critic purposes"
        )
    return {
        "authority_id": authority_id,
        "trust_store": str(store_path),
        "trust_store_sha256": sha256_file(store_path),
        "public_key_sha256": key_hash,
    }


def validate_trust_policy(run: dict[str, Any]) -> list[str]:
    policy = run.get("trust_policy")
    if not isinstance(policy, dict):
        return ["critic trust policy is missing"]
    public_key_raw = str(policy.get("public_key", ""))
    if not public_key_raw:
        return ["external critic public key is missing"]
    public_key = Path(public_key_raw).expanduser().resolve()
    if not public_key.is_file() or sha256_file(public_key) != policy.get(
        "public_key_sha256"
    ):
        return ["configured critic public key is missing or hash-drifted"]
    try:
        binding = trusted_critic_binding(public_key)
    except ValueError as exc:
        return [str(exc)]
    errors: list[str] = []
    for field in (
        "authority_id",
        "trust_store",
        "trust_store_sha256",
        "public_key_sha256",
    ):
        if policy.get(field) != binding[field]:
            errors.append(
                f"critic trust policy {field} differs from the active host trust store"
            )
    return errors


def registered_provider_binding(provider_id: str, quality_tier: str) -> dict[str, Any]:
    """Rebuild the canonical binding so a critic cannot invent its own profile."""
    registry = read_json(PROVIDER_REGISTRY)
    quality_class = next(
        (
            item
            for item in registry.get("quality_classes", [])
            if item.get("id") == quality_tier
        ),
        None,
    )
    provider = next(
        (
            item
            for item in registry.get("providers", [])
            if item.get("id") == provider_id
        ),
        None,
    )
    if quality_class is None or provider is None:
        raise ValueError("critic provider binding is not registered")
    binding = provider.get("quality_adapter", {}).get("bindings", {}).get(quality_tier)
    if not isinstance(binding, dict):
        raise ValueError("critic quality binding is not registered")
    payload = {
        "schema_version": "harness.provider-binding.v1",
        "provider": provider_id,
        "quality_tier": quality_tier,
        "selection": binding.get("selection"),
        "context_policy": binding.get("context_policy"),
        "required_capabilities": list(quality_class.get("required_capabilities", [])),
        "required_tools": list(quality_class.get("required_tools", [])),
        "adapter": provider.get("tool_adapter"),
        "execution_adapter": provider.get("execution_adapter"),
        "execution_profile": binding.get("execution_profile"),
        "host_tool_contracts": list(provider.get("host_tool_contracts", [])),
        "status": "supported",
    }
    payload["binding_hash"] = hashlib.sha256(
        json.dumps(
            payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")
        ).encode("utf-8")
    ).hexdigest()
    return payload


def critic_context_errors(context: dict[str, Any]) -> list[str]:
    """Validate a compiler-shaped, fresh independent-critic context manifest."""
    errors: list[str] = []
    required = {
        "schema_version",
        "generated_at",
        "repository",
        "profile",
        "profile_path",
        "provider_binding",
        "capabilities",
        "inventory_hash",
        "budget_bytes",
        "total_bytes",
        "selected",
        "skipped",
    }
    missing = sorted(required - set(context))
    if missing:
        errors.append("critic context manifest missing fields: " + ", ".join(missing))
    if context.get("schema_version") != "harness.context-manifest.v1":
        errors.append("critic context must be a harness.context-manifest.v1 artifact")
    for field in ("generated_at", "repository", "profile", "profile_path"):
        if (
            not isinstance(context.get(field), str)
            or not context.get(field, "").strip()
        ):
            errors.append(f"critic context {field} must be a non-empty string")
    inventory_hash = context.get("inventory_hash")
    if (
        not isinstance(inventory_hash, str)
        or re.fullmatch(r"[0-9a-f]{64}", inventory_hash) is None
    ):
        errors.append("critic context inventory_hash must be a lowercase SHA-256")
    capabilities = context.get("capabilities")
    if (
        not isinstance(capabilities, list)
        or not capabilities
        or any(
            not isinstance(value, str) or not value.strip() for value in capabilities
        )
    ):
        errors.append("critic context capabilities must be a non-empty string array")
    budget = context.get("budget_bytes")
    total = context.get("total_bytes")
    if not isinstance(budget, int) or isinstance(budget, bool) or budget < 1:
        errors.append("critic context budget_bytes must be a positive integer")
    if not isinstance(total, int) or isinstance(total, bool) or total < 1:
        errors.append("critic context total_bytes must be a positive integer")
    elif isinstance(budget, int) and not isinstance(budget, bool) and total > budget:
        errors.append("critic context total_bytes exceeds budget_bytes")
    if not isinstance(context.get("skipped"), list):
        errors.append("critic context skipped must be an array")

    binding = context.get("provider_binding")
    if not isinstance(binding, dict):
        errors.append("critic context provider_binding is missing")
    else:
        if binding.get("schema_version") != "harness.provider-binding.v1":
            errors.append("critic context provider binding schema is invalid")
        if (
            binding.get("quality_tier") != "independent_critic"
            or binding.get("selection") != "independent_critic"
        ):
            errors.append(
                "critic context must use the independent_critic quality binding"
            )
        if binding.get("context_policy") != "fresh_required":
            errors.append("critic context provider binding must require fresh context")
        if binding.get("adapter") != "native" or binding.get("status") != "supported":
            errors.append(
                "critic context provider binding is not a supported native adapter"
            )
        if (
            not isinstance(binding.get("provider"), str)
            or not binding.get("provider", "").strip()
        ):
            errors.append("critic context provider binding requires a provider")
        if not isinstance(binding.get("execution_adapter"), dict):
            errors.append(
                "critic context provider binding requires an execution adapter"
            )
        required_capabilities = binding.get("required_capabilities")
        if (
            not isinstance(required_capabilities, list)
            or any(not isinstance(value, str) for value in required_capabilities)
            or not {"independent_context", "structured_output"}.issubset(
                set(required_capabilities)
            )
        ):
            errors.append(
                "critic context provider binding lacks independent critic capabilities"
            )
        required_tools = binding.get("required_tools")
        if (
            not isinstance(required_tools, list)
            or any(not isinstance(value, str) for value in required_tools)
            or not {"filesystem_read", "evaluation"}.issubset(set(required_tools))
        ):
            errors.append(
                "critic context provider binding lacks independent critic tools"
            )
        binding_hash = binding.get("binding_hash")
        unsigned = {
            key: value for key, value in binding.items() if key != "binding_hash"
        }
        expected_hash = hashlib.sha256(
            json.dumps(
                unsigned, ensure_ascii=False, sort_keys=True, separators=(",", ":")
            ).encode("utf-8")
        ).hexdigest()
        if binding_hash != expected_hash:
            errors.append("critic context provider binding hash is invalid")
        try:
            registered = registered_provider_binding(
                str(binding.get("provider", "")),
                str(binding.get("quality_tier", "")),
            )
        except ValueError as exc:
            errors.append(str(exc))
        else:
            if binding != registered:
                errors.append(
                    "critic context provider binding differs from the canonical provider registry"
                )

    selected = context.get("selected")
    repository_raw = context.get("repository")
    repository = (
        Path(repository_raw).expanduser().resolve()
        if isinstance(repository_raw, str) and repository_raw.strip()
        else None
    )
    selected_total = 0
    if not isinstance(selected, list) or not selected:
        errors.append("critic context selected artifacts must be non-empty")
    else:
        for index, item in enumerate(selected):
            if not isinstance(item, dict):
                errors.append(f"critic context selected[{index}] must be an object")
                continue
            raw_path = item.get("path")
            expected_sha = item.get("sha256")
            expected_bytes = item.get("bytes")
            if not isinstance(raw_path, str) or not raw_path.strip():
                errors.append(f"critic context selected[{index}] requires a path")
                continue
            relative = Path(raw_path)
            if relative.is_absolute() or ".." in relative.parts or repository is None:
                errors.append(
                    f"critic context selected[{index}] path must stay repository-relative"
                )
                continue
            artifact = (repository / relative).resolve()
            try:
                artifact.relative_to(repository)
            except ValueError:
                errors.append(
                    f"critic context selected[{index}] path escapes repository"
                )
                continue
            if artifact.is_symlink() or not artifact.is_file():
                errors.append(f"critic context selected[{index}] artifact is missing")
                continue
            if (
                not isinstance(expected_bytes, int)
                or isinstance(expected_bytes, bool)
                or expected_bytes < 0
            ):
                errors.append(f"critic context selected[{index}] bytes is invalid")
                continue
            selected_total += expected_bytes
            if artifact.stat().st_size != expected_bytes:
                errors.append(f"critic context selected[{index}] artifact size changed")
            if (
                not isinstance(expected_sha, str)
                or sha256_file(artifact) != expected_sha
            ):
                errors.append(f"critic context selected[{index}] artifact hash changed")
            if (
                not isinstance(item.get("capability"), str)
                or not item.get("capability", "").strip()
            ):
                errors.append(f"critic context selected[{index}] capability is missing")
            if not isinstance(item.get("required"), bool):
                errors.append(
                    f"critic context selected[{index}] required flag is invalid"
                )
    if (
        isinstance(total, int)
        and not isinstance(total, bool)
        and selected_total != total
    ):
        errors.append("critic context total_bytes does not match selected artifacts")
    return errors


def fingerprint_candidates(root: Path) -> list[Path]:
    candidates: list[Path] = []
    for current, directories, files in os.walk(root):
        directories[:] = sorted(
            directory for directory in directories if directory not in SKIP_PARTS
        )
        current_path = Path(current)
        for filename in files:
            path = current_path / filename
            if (
                filename not in FINGERPRINT_NAMES
                and not filename.endswith(FINGERPRINT_SUFFIXES)
                and path.suffix.lower() not in UI_SOURCE_SUFFIXES
            ):
                continue
            if path.is_symlink() or path.stat().st_size > 1_000_000:
                continue
            candidates.append(path)
    return sorted(candidates, key=lambda item: item.relative_to(root).as_posix())


def build_fingerprint(root: Path) -> dict[str, Any]:
    files = [
        {"path": path.relative_to(root).as_posix(), "sha256": sha256_file(path)}
        for path in fingerprint_candidates(root)
    ]
    joined = "\n".join(f"{item['path']}:{item['sha256']}" for item in files).encode()
    stack_markers: list[str] = []
    existing_systems: list[str] = []
    names = {item["path"] for item in files}
    if "pubspec.yaml" in names:
        stack_markers.append("flutter")
    if "package.json" in names:
        stack_markers.append("node")
        package = root / "package.json"
        try:
            package_text = package.read_text(encoding="utf-8")
        except OSError:
            package_text = ""
        for marker in ("next", "react", "@angular", "vue", "svelte", "tailwindcss"):
            if f'"{marker}"' in package_text:
                stack_markers.append(marker)
        for system in (
            "@mui/",
            "@fluentui/",
            "@carbon/",
            "@shopify/polaris",
            "@primer/",
            "@atlaskit/",
            "radix",
            "shadcn",
        ):
            if system.lower() in package_text.lower():
                existing_systems.append(system.rstrip("/"))
    components = root / "components.json"
    if components.exists():
        existing_systems.append("shadcn")
    return {
        "digest": hashlib.sha256(joined).hexdigest(),
        "files": files,
        "candidate_count": len(files),
        "truncated": False,
        "stack_markers": sorted(set(stack_markers)),
        "existing_systems": sorted(set(existing_systems)),
    }


def canonical_bytes(payload: dict[str, Any]) -> bytes:
    return json.dumps(
        payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


def sha256_payload(payload: dict[str, Any]) -> str:
    return hashlib.sha256(canonical_bytes(payload)).hexdigest()


def review_manifest_digest(manifest: dict[str, Any]) -> str:
    review_view = dict(manifest)
    review_view.pop("generated_at", None)
    review_view["items"] = [
        item
        for item in manifest.get("items", [])
        if item.get("kind") != "evaluation-result"
    ]
    return sha256_payload(review_view)


def verify_ed25519_signature(
    public_key: Path, payload: dict[str, Any], signature_b64: str
) -> list[str]:
    errors: list[str] = []
    if not public_key.is_file():
        return [f"critic attestation public key missing: {public_key}"]
    try:
        signature = base64.b64decode(signature_b64, validate=True)
    except (ValueError, binascii.Error):
        return ["critic attestation signature is not valid base64"]
    try:
        with tempfile.TemporaryDirectory(prefix="design-attestation-") as temporary:
            payload_path = Path(temporary) / "payload.json"
            signature_path = Path(temporary) / "signature.bin"
            payload_path.write_bytes(canonical_bytes(payload))
            signature_path.write_bytes(signature)
            process = subprocess.run(
                [
                    "openssl",
                    "pkeyutl",
                    "-verify",
                    "-pubin",
                    "-inkey",
                    str(public_key),
                    "-rawin",
                    "-in",
                    str(payload_path),
                    "-sigfile",
                    str(signature_path),
                ],
                check=False,
                capture_output=True,
                text=True,
            )
        if process.returncode != 0:
            errors.append("critic attestation Ed25519 signature verification failed")
    except FileNotFoundError:
        errors.append("openssl is required to verify critic attestations")
    return errors


def load_platform_registry() -> dict[str, Any]:
    return read_json(PLATFORM_REGISTRY)


def detect_platform(root: Path) -> tuple[str, list[str]]:
    markers: list[str] = []
    if (root / "pubspec.yaml").exists():
        markers.append("pubspec.yaml")
        return "flutter", markers
    if (root / "package.json").exists():
        markers.append("package.json")
        for name in (
            "next.config.ts",
            "next.config.mjs",
            "next.config.js",
            "vite.config.ts",
            "vite.config.js",
        ):
            if (root / name).exists():
                markers.append(name)
        return "web", markers
    return "unknown", markers


def parse_dials(raw: str) -> dict[str, int]:
    names = ("distinction", "motion", "density", "evidence", "systemness")
    try:
        values = [int(value.strip()) for value in raw.split(",")]
    except ValueError as exc:
        raise ValueError("--dials must contain five comma-separated integers") from exc
    if len(values) != 5 or any(value < 1 or value > 10 for value in values):
        raise ValueError(
            "--dials must be DISTINCTION,MOTION,DENSITY,EVIDENCE,SYSTEMNESS in range 1..10"
        )
    return dict(zip(names, values, strict=True))


def slug(value: str) -> str:
    normalized = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return normalized[:38] or "surface"


def parse_viewport(raw: str) -> dict[str, Any]:
    match = re.fullmatch(r"([a-zA-Z0-9_-]+):(\d+)x(\d+)(?:@(\d+(?:\.\d+)?))?", raw)
    if not match:
        raise ValueError(f"invalid viewport {raw!r}; use name:WIDTHxHEIGHT[@DSF]")
    name, width, height, scale = match.groups()
    return {
        "name": name,
        "width": int(width),
        "height": int(height),
        "device_scale_factor": float(scale or 1),
    }


def validate_artifact_content(kind: str, path: Path) -> list[str]:
    """Reject placeholder files that cannot be evidence for the declared kind."""
    errors: list[str] = []
    if kind in {"baseline-screenshot", "result-screenshot"}:
        data = path.read_bytes()
        if len(data) < 24 or data[:8] != b"\x89PNG\r\n\x1a\n":
            return [f"{kind} must be a real PNG artifact: {path}"]
        position = 8
        width = height = 0
        color_type = bit_depth = interlace = -1
        compressed = bytearray()
        saw_end = False
        try:
            while position + 12 <= len(data):
                length = struct.unpack(">I", data[position : position + 4])[0]
                chunk_type = data[position + 4 : position + 8]
                chunk_data = data[position + 8 : position + 8 + length]
                crc_offset = position + 8 + length
                if crc_offset + 4 > len(data):
                    raise ValueError("truncated chunk")
                expected_crc = struct.unpack(">I", data[crc_offset : crc_offset + 4])[0]
                if binascii.crc32(chunk_type + chunk_data) & 0xFFFFFFFF != expected_crc:
                    raise ValueError("chunk CRC mismatch")
                if chunk_type == b"IHDR":
                    if length != 13:
                        raise ValueError("invalid IHDR")
                    width, height, bit_depth, color_type, _, _, interlace = (
                        struct.unpack(">IIBBBBB", chunk_data)
                    )
                elif chunk_type == b"IDAT":
                    compressed.extend(chunk_data)
                elif chunk_type == b"IEND":
                    saw_end = True
                    break
                position = crc_offset + 4
            if not saw_end or not compressed or interlace != 0:
                raise ValueError("missing IEND/IDAT or unsupported interlace")
            channels = {0: 1, 2: 3, 3: 1, 4: 2, 6: 4}.get(color_type)
            if channels is None or bit_depth not in {8, 16}:
                raise ValueError("unsupported PNG color format")
            raw = zlib.decompress(bytes(compressed))
            expected_minimum = height * (1 + ((width * channels * bit_depth + 7) // 8))
            if len(raw) != expected_minimum:
                raise ValueError("decoded scanline length mismatch")
        except (ValueError, zlib.error, struct.error) as exc:
            return [f"{kind} PNG is corrupt or unverifiable ({exc}): {path}"]
        if width < 100 or height < 100:
            errors.append(f"{kind} dimensions are too small ({width}x{height}): {path}")
    elif kind == "accessibility-tree":
        text = path.read_text(encoding="utf-8", errors="replace")
        if len(text.strip()) < 12 or not re.search(
            r"\b(main|button|heading|link|textbox|dialog|table|semantics|label|role)\b",
            text,
            re.IGNORECASE,
        ):
            errors.append(f"accessibility evidence lacks a semantic tree: {path}")
    elif kind == "state-assertion":
        payload = read_json(path)
        if payload.get("schema") != "design-state-assertion-result-v1":
            errors.append(f"state assertion schema is invalid: {path}")
        if payload.get("status") != "passed":
            errors.append(f"state assertion did not pass: {path}")
        assertions = payload.get("assertions")
        if (
            not isinstance(assertions, list)
            or not assertions
            or any(
                not isinstance(item, dict) or item.get("status") != "passed"
                for item in assertions
            )
        ):
            errors.append(f"state assertion results are missing or failed: {path}")
    elif kind == "source-scan":
        payload = read_json(path)
        if payload.get("schema") != "design-slop-scan-v2":
            errors.append(f"source scan schema is not design-slop-scan-v2: {path}")
        if not payload.get("files_scanned"):
            errors.append(f"source scan did not inspect any files: {path}")
        hashes = payload.get("file_hashes")
        if not isinstance(hashes, dict) or set(hashes) != set(
            payload.get("files_scanned", [])
        ):
            errors.append(f"source scan file hash map is incomplete: {path}")
        counts = payload.get("counts")
        if not isinstance(counts, dict) or not isinstance(counts.get("hard-fail"), int):
            errors.append(f"source scan counts are invalid: {path}")
    elif kind == "evaluation-result":
        payload = read_json(path)
        if (
            payload.get("schema") != "evaluation-result-v1"
            or payload.get("result", {}).get("status") != "pass"
        ):
            errors.append(
                f"evaluation result is not a passing evaluation-result-v1: {path}"
            )
    elif path.stat().st_size == 0:
        errors.append(f"empty evidence artifact: {path}")
    return errors


def evidence_tuple(
    route: str | None, state: str | None, viewport: str | None
) -> str | None:
    if not route or not state or not viewport:
        return None
    return f"{route}|{state}|{viewport}"


def run_live_detector(run: dict[str, Any], output: Path) -> dict[str, Any]:
    root = Path(run["project_root"]).expanduser().resolve()
    process = subprocess.run(
        ["node", str(DETECTOR), "--format", "json", "--fail-on", "none", str(root)],
        cwd=root,
        check=False,
        capture_output=True,
        text=True,
    )
    if process.returncode != 0:
        raise ValueError(
            process.stderr.strip()
            or process.stdout.strip()
            or "design-slop detector failed"
        )
    try:
        payload = json.loads(process.stdout)
    except json.JSONDecodeError as exc:
        raise ValueError(f"design-slop detector returned invalid JSON: {exc}") from exc
    if payload.get("schema") != "design-slop-scan-v2" or not payload.get(
        "files_scanned"
    ):
        raise ValueError(
            "design-slop detector did not produce a verifiable source scan"
        )
    write_json(output, payload)
    return payload


def upsert_runtime_evidence(
    manifest: dict[str, Any],
    *,
    evidence_id: str,
    kind: str,
    path: Path,
    producer: str,
    supports: list[str],
) -> None:
    manifest["items"] = [
        item for item in manifest.get("items", []) if item.get("id") != evidence_id
    ]
    manifest["items"].append(
        {
            "id": evidence_id,
            "kind": kind,
            "path": str(path),
            "sha256": sha256_file(path),
            "captured_at": utc_now(),
            "supports": supports,
            "verdict": "pass",
            "provenance": {"trust": "runtime", "producer": producer},
        }
    )
    manifest["generated_at"] = utc_now()


def command_init(args: argparse.Namespace) -> int:
    root = Path(args.root).expanduser().resolve()
    if not root.is_dir():
        raise ValueError(f"project root does not exist: {root}")
    platform_kind, detected_from = detect_platform(root)
    if args.platform != "auto":
        platform_kind = args.platform
        detected_from.append("explicit --platform")
    registry = load_platform_registry()["platforms"]
    platform_spec = registry.get(platform_kind, registry["unknown"])
    run_id = (
        args.run_id
        or f"{dt.datetime.now().strftime('%Y%m%d%H%M%S')}-{slug(args.surface)}"
    )
    output = (
        Path(args.out).expanduser().resolve()
        if args.out
        else root / ".design-runs" / run_id
    )
    manifest_path = output / "evidence-manifest.json"
    viewports = [parse_viewport(value) for value in args.viewport]
    if not viewports:
        viewports = platform_spec["recommended_viewports"]
    routes = list(
        dict.fromkeys(
            args.route or (["/"] if platform_kind == "web" else [args.surface])
        )
    )
    states = list(
        dict.fromkeys(args.state or ["default", "loading", "empty", "error", "focus"])
    )
    baseline_fingerprint = build_fingerprint(root)
    critic_public_key = ""
    critic_public_key_sha256 = ""
    critic_trust_binding = {
        "authority_id": "",
        "trust_store": "",
        "trust_store_sha256": "",
        "public_key_sha256": "",
    }
    if args.critic_public_key:
        public_key_path = Path(args.critic_public_key).expanduser().resolve()
        if not public_key_path.is_file():
            raise ValueError(f"critic public key does not exist: {public_key_path}")
        critic_trust_binding = trusted_critic_binding(public_key_path)
        critic_public_key = str(public_key_path)
        critic_public_key_sha256 = sha256_file(public_key_path)
    run = {
        "schema": SCHEMA_RUN,
        "run_id": run_id,
        "created_at": utc_now(),
        "project_root": str(root),
        "implementation_actor_id": args.implementation_actor_id
        or f"implementer:{run_id}",
        "mode": args.mode,
        "surface": args.surface,
        "register": args.register,
        "platform": {
            "kind": platform_kind,
            "adapter": platform_spec["adapter"],
            "detected_from": detected_from,
        },
        "design_read": args.design_read,
        "audience": args.audience or "",
        "scene": args.scene or "",
        "visual_stance": args.visual_stance or "",
        "anti_reference": list(dict.fromkeys(args.anti_reference)),
        "dials": parse_dials(args.dials),
        "slop_risks": list(dict.fromkeys(args.slop_risk)),
        "routes": routes,
        "states": states,
        "viewports": viewports,
        "design_read_fingerprint": baseline_fingerprint,
        "project_fingerprint": baseline_fingerprint,
        "capture_receipts": [],
        "capture_attestation": "",
        "capture_attestation_sha256": "",
        "review_packet": "",
        "review_packet_sha256": "",
        "critic_attestation": "",
        "trust_policy": {
            "critic_attestation": "ed25519-detached-v1",
            "public_key": critic_public_key,
            "public_key_sha256": critic_public_key_sha256,
            "authority_id": critic_trust_binding["authority_id"],
            "trust_store": critic_trust_binding["trust_store"],
            "trust_store_sha256": critic_trust_binding["trust_store_sha256"],
        },
        "validation": {
            "source_scan": False,
            "visual_evidence": False,
            "state_coverage": False,
            "accessibility": False,
            "independent_critic": False,
            "evaluation": False,
        },
        "repair_policy": {
            "max_rounds": 2,
            "same_failure_limit": 3,
            "critic_must_be_independent": True,
        },
        "status": "draft",
        "evidence_manifest": str(manifest_path),
        "critic_result": "",
        "repair_history": [],
        "final_evaluation": "",
        "waivers": [],
    }
    evidence = {
        "schema": SCHEMA_EVIDENCE,
        "run_id": run_id,
        "project_root": str(root),
        "project_fingerprint_digest": run["project_fingerprint"]["digest"],
        "generated_at": utc_now(),
        "items": [],
        "coverage": {
            "routes": [],
            "states": [],
            "viewports": [],
            "tuples": [],
            "source_scan": False,
            "accessibility": False,
            "critic": False,
        },
    }
    write_json(output / "design-run.json", run)
    write_json(manifest_path, evidence)
    print(
        json.dumps(
            {
                "run": str(output / "design-run.json"),
                "evidence": str(manifest_path),
                "platform": platform_kind,
            },
            ensure_ascii=False,
        )
    )
    return 0


def command_add_evidence(args: argparse.Namespace) -> int:
    manifest_path = Path(args.manifest).expanduser().resolve()
    manifest = read_json(manifest_path)
    if manifest.get("schema") != SCHEMA_EVIDENCE:
        raise ValueError(f"unsupported evidence schema: {manifest.get('schema')}")
    artifact = Path(args.path).expanduser().resolve()
    if not artifact.is_file():
        raise ValueError(f"evidence artifact does not exist: {artifact}")
    artifact_errors = validate_artifact_content(args.kind, artifact)
    if artifact_errors:
        raise ValueError("; ".join(artifact_errors))
    evidence_id = args.id or f"E{len(manifest['items']) + 1}"
    if any(item.get("id") == evidence_id for item in manifest["items"]):
        raise ValueError(f"duplicate evidence id: {evidence_id}")
    item: dict[str, Any] = {
        "id": evidence_id,
        "kind": args.kind,
        "path": str(artifact),
        "sha256": sha256_file(artifact),
        "captured_at": utc_now(),
        "supports": list(dict.fromkeys(args.supports)),
        "provenance": {"trust": "manual", "producer": "manual-add-evidence"},
    }
    for key in (
        "route",
        "state",
        "viewport",
        "platform",
        "command",
        "verdict",
        "notes",
    ):
        value = getattr(args, key, None)
        if value:
            item[key] = value
    if args.finding_count:
        counts: dict[str, int] = {}
        for raw in args.finding_count:
            name, separator, value = raw.partition("=")
            if not separator:
                raise ValueError("--finding-count must be NAME=INTEGER")
            counts[name] = int(value)
        item["finding_counts"] = counts
    manifest["items"].append(item)
    coverage = manifest["coverage"]
    if args.route:
        coverage["routes"] = sorted(set(coverage["routes"] + [args.route]))
    if args.state:
        coverage["states"] = sorted(set(coverage["states"] + [args.state]))
    if args.viewport:
        coverage["viewports"] = sorted(set(coverage["viewports"] + [args.viewport]))
    tuple_key = evidence_tuple(args.route, args.state, args.viewport)
    if tuple_key:
        coverage["tuples"] = sorted(set(coverage["tuples"] + [tuple_key]))
    manifest["generated_at"] = utc_now()
    write_json(manifest_path, manifest)
    print(json.dumps(item, ensure_ascii=False))
    return 0


def validate_capture_spec_binding(
    run: dict[str, Any], spec: dict[str, Any]
) -> tuple[str, dict[str, tuple[str, str, str, str, bool]]]:
    platform = run.get("platform", {}).get("kind")
    expected: dict[str, tuple[str, str, str, str, bool]] = {}
    phases_by_tuple: dict[str, set[str]] = {}
    if platform == "web":
        if spec.get("schema") != "design-web-capture-v1":
            raise ValueError("web capture requires design-web-capture-v1")
        from urllib.parse import urlparse

        base = urlparse(str(spec.get("base_url", "")))
        if base.scheme not in {"http", "https"} or base.hostname not in {
            "127.0.0.1",
            "localhost",
            "::1",
        }:
            raise ValueError(
                "trusted web capture must target a loopback project server"
            )
        for case in spec.get("cases", []):
            route = str(case.get("path", ""))
            if (
                not route.startswith("/")
                or route.startswith("//")
                or "\\" in route
                or any(ord(character) < 32 for character in route)
            ):
                raise ValueError(
                    "trusted web capture paths must be same-origin relative paths"
                )
            viewport = case.get("viewport", {}).get("name")
            case_id = str(case.get("id", ""))
            if not case_id or not viewport:
                raise ValueError("web capture case id/viewport is missing")
            state = str(case.get("state", ""))
            assertions = case.get("assertions", [])
            assertion_required = state != "default"
            if assertion_required and (
                not isinstance(assertions, list) or not assertions
            ):
                raise ValueError(
                    f"non-default capture case {case_id} requires typed state assertions"
                )
            phase = str(case.get("phase", "result"))
            if phase not in {"baseline", "result"}:
                raise ValueError(f"capture case {case_id} has an invalid phase")
            expected[case_id] = (
                route,
                state,
                str(viewport),
                f"{phase}:web+aria"
                if case.get("capture_aria") is not False
                else f"{phase}:web",
                assertion_required,
            )
            tuple_key = evidence_tuple(route, state, str(viewport))
            if tuple_key:
                phases_by_tuple.setdefault(tuple_key, set()).add(phase)
    elif platform == "flutter":
        if spec.get("schema") != "design-flutter-capture-v1":
            raise ValueError("Flutter capture requires design-flutter-capture-v1")
        for artifact in spec.get("artifacts", []):
            artifact_id = str(artifact.get("id", ""))
            expected[artifact_id] = (
                str(artifact.get("screen", "")),
                str(artifact.get("state", "")),
                str(artifact.get("viewport", "")),
                str(artifact.get("kind", "")),
                False,
            )
    else:
        raise ValueError(f"no trusted capture adapter for platform: {platform}")
    if not expected:
        raise ValueError("capture spec contains no cases")
    requested = {
        evidence_tuple(route, state, viewport.get("name"))
        for route in run.get("routes", [])
        for state in run.get("states", [])
        for viewport in run.get("viewports", [])
    }
    declared = {
        evidence_tuple(route, state, viewport)
        for route, state, viewport, _, _ in expected.values()
    }
    if requested != declared:
        raise ValueError(
            "capture spec cases must exactly match the run route/state/viewport matrix"
        )
    if platform == "web" and run.get("mode") == "redesign":
        incomplete = sorted(
            tuple_key
            for tuple_key in requested
            if phases_by_tuple.get(str(tuple_key), set()) != {"baseline", "result"}
        )
        if incomplete:
            raise ValueError(
                "redesign capture requires comparable baseline and result cases for every tuple: "
                + ", ".join(str(value) for value in incomplete)
            )
    return platform, expected


def ingest_capture_index(
    manifest: dict[str, Any],
    index_path: Path,
    *,
    trusted: bool,
    expected_run: dict[str, Any] | None = None,
    expected_nonce: str = "",
    adapter_sha256: str = "",
    fingerprint_digest: str = "",
    allow_failed_index: bool = False,
    command: str = "",
) -> list[str]:
    capture = read_json(index_path)
    if manifest.get("schema") != SCHEMA_EVIDENCE:
        raise ValueError(f"unsupported evidence schema: {manifest.get('schema')}")
    if capture.get("schema") != "design-capture-index-v1":
        raise ValueError(f"unsupported capture index schema: {capture.get('schema')}")
    expected_producer = {
        "web": "capture-web-evidence@1",
        "flutter": "capture-flutter-evidence@1",
    }.get(capture.get("platform"))
    if capture.get("producer") != expected_producer:
        raise ValueError(f"untrusted capture producer: {capture.get('producer')}")
    project_root = Path(str(manifest.get("project_root", ""))).expanduser().resolve()
    if (
        Path(str(capture.get("project_root", ""))).expanduser().resolve()
        != project_root
    ):
        raise ValueError("capture index project_root does not match the design run")
    spec_path = Path(str(capture.get("spec", ""))).expanduser().resolve()
    if not spec_path.is_file() or sha256_file(spec_path) != capture.get("spec_sha256"):
        raise ValueError("capture index spec is missing or hash-drifted")
    if not capture.get("generated_at"):
        raise ValueError("capture index generated_at is required")
    if capture.get("status") != "passed" and not allow_failed_index:
        raise ValueError(
            "capture index did not pass; fix capture failures before importing"
        )
    expected_cases: dict[str, tuple[str, str, str, str, bool]] = {}
    if trusted:
        if expected_run is None:
            raise ValueError("trusted capture requires a design run")
        _, expected_cases = validate_capture_spec_binding(
            expected_run, read_json(spec_path)
        )
        if capture.get("run_id") != expected_run.get("run_id"):
            raise ValueError("capture run_id does not match")
        if capture.get("nonce") != expected_nonce:
            raise ValueError("capture nonce does not match the runtime invocation")
        if capture.get("adapter_sha256") != adapter_sha256:
            raise ValueError(
                "capture adapter hash does not match the canonical adapter"
            )
        if capture.get("source_fingerprint_digest") != fingerprint_digest:
            raise ValueError(
                "capture source fingerprint is not bound to the runtime invocation"
            )
        result_ids = {
            str(result.get("id"))
            for result in capture.get("results", [])
            if str(result.get("id")) in expected_cases
        }
        if result_ids != set(expected_cases):
            raise ValueError("capture results do not exactly match declared spec cases")
    existing = {str(item.get("id")) for item in manifest.get("items", [])}
    imported: list[str] = []
    coverage = manifest["coverage"]
    screenshot_hashes: dict[str, str] = {}
    screenshot_paths: set[str] = set()
    semantic_hashes: dict[tuple[str, str, str], str] = {}
    for result in capture.get("results", []):
        if result.get("status") != "passed" and not allow_failed_index:
            continue
        result_id = str(result.get("id", "capture"))
        expected_case = expected_cases.get(result_id)
        result_artifacts = result.get("artifacts", [])
        if trusted and expected_case:
            route, state, viewport, expected_kind, assertion_required = expected_case
            if capture.get("platform") == "web":
                phase, web_evidence = expected_kind.split(":", 1)
                screenshot_kind = (
                    "baseline-screenshot"
                    if phase == "baseline"
                    else "result-screenshot"
                )
            else:
                web_evidence = ""
                screenshot_kind = expected_kind
            screenshots = [
                artifact
                for artifact in result_artifacts
                if artifact.get("kind") == screenshot_kind
            ]
            aria = [
                artifact
                for artifact in result_artifacts
                if artifact.get("kind") == "accessibility-tree"
            ]
            assertions = [
                artifact
                for artifact in result_artifacts
                if artifact.get("kind") == "state-assertion"
            ]
            if capture.get("platform") == "web":
                if len(screenshots) != 1 or (
                    web_evidence == "web+aria" and len(aria) != 1
                ):
                    raise ValueError(
                        f"capture case {result_id} lacks its exact screenshot/accessibility artifacts"
                    )
                if assertion_required and len(assertions) != 1:
                    raise ValueError(
                        f"non-default capture case {result_id} lacks a passing state-assertion artifact"
                    )
                if not assertion_required and len(assertions) > 1:
                    raise ValueError(
                        f"capture case {result_id} has duplicate state-assertion artifacts"
                    )
                expected_artifacts = screenshots + aria + assertions
            else:
                expected_artifacts = [
                    artifact
                    for artifact in result_artifacts
                    if artifact.get("kind") == expected_kind
                ]
                if len(expected_artifacts) != 1:
                    raise ValueError(
                        f"capture case {result_id} lacks its declared {expected_kind} artifact"
                    )
            if len(expected_artifacts) != len(result_artifacts):
                raise ValueError(
                    f"capture case {result_id} contains undeclared evidence artifacts"
                )
            for artifact in expected_artifacts:
                if (
                    artifact.get("route"),
                    artifact.get("state"),
                    artifact.get("viewport"),
                ) != (route, state, viewport):
                    raise ValueError(
                        f"capture case {result_id} artifact metadata differs from its spec"
                    )
        for position, artifact in enumerate(result_artifacts, start=1):
            path = Path(str(artifact.get("path", ""))).expanduser().resolve()
            if not path.is_file():
                raise ValueError(f"capture artifact missing: {path}")
            try:
                path.relative_to(index_path.parent.resolve())
            except ValueError as exc:
                raise ValueError(
                    f"capture artifact escapes the runtime-owned output: {path}"
                ) from exc
            actual_hash = sha256_file(path)
            if artifact.get("sha256") != actual_hash:
                raise ValueError(f"capture artifact hash drift: {path}")
            kind = str(artifact.get("kind", ""))
            artifact_errors = validate_artifact_content(kind, path)
            if artifact_errors:
                raise ValueError("; ".join(artifact_errors))
            tuple_key = evidence_tuple(
                artifact.get("route"), artifact.get("state"), artifact.get("viewport")
            )
            if trusted and kind == "result-screenshot":
                if str(path) in screenshot_paths:
                    raise ValueError(
                        "a screenshot path cannot satisfy multiple capture cases"
                    )
                other_tuple = screenshot_hashes.get(actual_hash)
                if other_tuple and other_tuple != tuple_key:
                    raise ValueError(
                        "an identical screenshot cannot satisfy multiple route/state/viewport tuples"
                    )
                screenshot_paths.add(str(path))
                screenshot_hashes[actual_hash] = str(tuple_key)
            if trusted and kind == "accessibility-tree":
                semantic_key = (
                    str(artifact.get("route", "")),
                    str(artifact.get("viewport", "")),
                    actual_hash,
                )
                current_state = str(artifact.get("state", ""))
                other_state = semantic_hashes.get(semantic_key)
                if other_state and other_state != current_state:
                    raise ValueError(
                        "different declared states cannot share identical accessibility semantics"
                    )
                semantic_hashes[semantic_key] = current_state
            base_id = re.sub(r"[^A-Za-z0-9._-]+", "-", f"{result_id}-{position}").strip(
                "-"
            )
            evidence_id = base_id or f"capture-{len(existing) + 1}"
            suffix = 2
            while evidence_id in existing:
                evidence_id = f"{base_id}-{suffix}"
                suffix += 1
            item: dict[str, Any] = {
                "id": evidence_id,
                "kind": kind,
                "path": str(path),
                "sha256": actual_hash,
                "captured_at": utc_now(),
                "supports": list(
                    dict.fromkeys(artifact.get("supports", ["platform-verification"]))
                ),
                "platform": artifact.get(
                    "platform", capture.get("platform", "unknown")
                ),
                "verdict": "pass" if result.get("status") == "passed" else "fail",
                "command": command or f"diagnostic capture index: {index_path}",
                "provenance": {
                    "trust": "runtime-adapter" if trusted else "diagnostic-import",
                    "producer": capture["producer"],
                    "source_index": str(index_path),
                    "source_index_sha256": sha256_file(index_path),
                    "spec": str(spec_path),
                    "spec_sha256": capture["spec_sha256"],
                    "capture_nonce": expected_nonce if trusted else "",
                    "adapter_sha256": adapter_sha256 if trusted else "",
                    "source_fingerprint_digest": fingerprint_digest if trusted else "",
                },
            }
            for key in ("route", "state", "viewport"):
                if artifact.get(key):
                    item[key] = artifact[key]
            manifest["items"].append(item)
            existing.add(evidence_id)
            imported.append(evidence_id)
            if trusted:
                if item.get("route"):
                    coverage["routes"] = sorted(
                        set(coverage["routes"] + [item["route"]])
                    )
                if item.get("state"):
                    coverage["states"] = sorted(
                        set(coverage["states"] + [item["state"]])
                    )
                if item.get("viewport"):
                    coverage["viewports"] = sorted(
                        set(coverage["viewports"] + [item["viewport"]])
                    )
                if tuple_key:
                    coverage["tuples"] = sorted(set(coverage["tuples"] + [tuple_key]))
                if kind == "accessibility-tree" and item["verdict"] == "pass":
                    coverage["accessibility"] = True
    if not imported:
        raise ValueError("capture index contains no importable artifacts")
    manifest["generated_at"] = utc_now()
    return imported


def command_import_index(args: argparse.Namespace) -> int:
    manifest_path = Path(args.manifest).expanduser().resolve()
    index_path = Path(args.index).expanduser().resolve()
    manifest = read_json(manifest_path)
    imported = ingest_capture_index(
        manifest,
        index_path,
        trusted=False,
        allow_failed_index=args.allow_failed_index,
        command=args.command or "diagnostic import; never satisfies promotion gates",
    )
    write_json(manifest_path, manifest)
    print(
        json.dumps(
            {
                "manifest": str(manifest_path),
                "imported": imported,
                "trust": "diagnostic-only",
            },
            ensure_ascii=False,
        )
    )
    return 0


def command_capture(args: argparse.Namespace) -> int:
    run_path = Path(args.run).expanduser().resolve()
    run = read_json(run_path)
    manifest_path = (
        Path(args.evidence or run.get("evidence_manifest", "")).expanduser().resolve()
    )
    manifest = read_json(manifest_path)
    root = Path(run["project_root"]).expanduser().resolve()
    spec_path = Path(args.spec).expanduser().resolve()
    spec = read_json(spec_path)
    platform, _ = validate_capture_spec_binding(run, spec)
    adapter = canonical_capture_adapter(platform)
    fingerprint = build_fingerprint(root)
    nonce = secrets.token_hex(24)
    output = (
        Path(args.out).expanduser().resolve()
        if args.out
        else run_path.parent / "capture" / nonce
    )
    try:
        output.relative_to(run_path.parent.resolve())
    except ValueError as exc:
        raise ValueError(
            "trusted capture output must stay inside the design run directory"
        ) from exc
    if output.exists() and any(output.iterdir()):
        raise ValueError(f"trusted capture output must be empty: {output}")
    output.mkdir(parents=True, exist_ok=True)
    bound_spec_path = output / "capture-spec.json"
    shutil.copy2(spec_path, bound_spec_path)
    command = (
        ["node", str(adapter)] if platform == "web" else [sys.executable, str(adapter)]
    ) + [
        "--root",
        str(root),
        "--spec",
        str(bound_spec_path),
        "--out",
        str(output),
        "--run-id",
        str(run["run_id"]),
        "--nonce",
        nonce,
        "--source-fingerprint",
        fingerprint["digest"],
    ]
    process = subprocess.run(
        command, cwd=root, check=False, capture_output=True, text=True
    )
    if process.returncode != 0:
        raise ValueError(
            process.stderr.strip()
            or process.stdout.strip()
            or "trusted capture adapter failed"
        )
    index_path = output / "capture-index.json"
    if not index_path.is_file():
        raise ValueError("trusted capture adapter did not create capture-index.json")
    if build_fingerprint(root) != fingerprint:
        raise ValueError("UI source changed while capture was running")
    manifest["items"] = [
        item
        for item in manifest.get("items", [])
        if item.get("provenance", {}).get("trust") != "runtime-adapter"
    ]
    manifest["coverage"] = {
        "routes": [],
        "states": [],
        "viewports": [],
        "tuples": [],
        "source_scan": False,
        "accessibility": False,
        "critic": False,
    }
    run["project_fingerprint"] = fingerprint
    manifest["project_fingerprint_digest"] = fingerprint["digest"]
    adapter_hash = sha256_file(adapter)
    imported = ingest_capture_index(
        manifest,
        index_path,
        trusted=True,
        expected_run=run,
        expected_nonce=nonce,
        adapter_sha256=adapter_hash,
        fingerprint_digest=fingerprint["digest"],
        command=" ".join(command),
    )
    receipt = {
        "schema": "design-capture-receipt-v1",
        "run_id": run["run_id"],
        "nonce": nonce,
        "adapter": str(adapter),
        "adapter_sha256": adapter_hash,
        "spec": str(bound_spec_path),
        "spec_sha256": sha256_file(bound_spec_path),
        "index": str(index_path),
        "index_sha256": sha256_file(index_path),
        "source_fingerprint_digest": fingerprint["digest"],
        "evidence_projection_sha256": capture_projection_digest(manifest),
        "captured_at": utc_now(),
    }
    receipt["receipt_sha256"] = sha256_payload(receipt)
    run["capture_receipts"] = [receipt]
    run["capture_attestation"] = ""
    run["capture_attestation_sha256"] = ""
    run["review_packet"] = ""
    run["review_packet_sha256"] = ""
    run["critic_attestation"] = ""
    run["status"] = "running"
    write_json(manifest_path, manifest)
    write_json(run_path, run)
    print(
        json.dumps(
            {"index": str(index_path), "imported": imported, "receipt": receipt},
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


def capture_item_projection(item: dict[str, Any]) -> dict[str, Any]:
    return {
        key: item.get(key)
        for key in (
            "kind",
            "path",
            "sha256",
            "supports",
            "platform",
            "verdict",
            "route",
            "state",
            "viewport",
            "provenance",
        )
        if key in item
    }


def capture_projection_digest(manifest: dict[str, Any]) -> str:
    items = sorted(
        (
            capture_item_projection(item)
            for item in manifest.get("items", [])
            if item.get("provenance", {}).get("trust") == "runtime-adapter"
        ),
        key=lambda item: (str(item.get("path")), str(item.get("kind"))),
    )
    return sha256_payload({"schema": "design-capture-projection-v1", "items": items})


def validate_capture_receipts(run: dict[str, Any]) -> list[str]:
    """Rebuild the adapter projection instead of trusting a self-hashed receipt."""
    receipts = run.get("capture_receipts")
    if not isinstance(receipts, list):
        return ["capture_receipts must be an array"]
    if len(receipts) > 1:
        return ["a design run may have only one active canonical capture receipt"]
    errors: list[str] = []
    if not receipts:
        return errors
    receipt = receipts[0]
    if (
        not isinstance(receipt, dict)
        or receipt.get("schema") != "design-capture-receipt-v1"
    ):
        return ["capture_receipts[0] has an invalid schema"]
    canonical = {
        key: value for key, value in receipt.items() if key != "receipt_sha256"
    }
    if receipt.get("receipt_sha256") != sha256_payload(canonical):
        errors.append("capture_receipts[0] hash is invalid")
    if receipt.get("run_id") != run.get("run_id"):
        errors.append("capture receipt run_id differs from the design run")
    nonce = str(receipt.get("nonce", ""))
    if re.fullmatch(r"[a-f0-9]{48}", nonce) is None:
        errors.append("capture receipt nonce is invalid")
    platform = str(run.get("platform", {}).get("kind", ""))
    try:
        adapter = canonical_capture_adapter(platform).resolve()
    except ValueError as exc:
        errors.append(str(exc))
        return errors
    receipt_adapter = Path(str(receipt.get("adapter", ""))).expanduser().resolve()
    if receipt_adapter != adapter or not adapter.is_file():
        errors.append("capture receipt adapter is not the canonical runtime adapter")
    elif receipt.get("adapter_sha256") != sha256_file(adapter):
        errors.append("capture receipt canonical adapter hash drifted")

    run_root = Path(str(run.get("evidence_manifest", ""))).expanduser().resolve().parent
    spec_path = Path(str(receipt.get("spec", ""))).expanduser()
    index_path = Path(str(receipt.get("index", ""))).expanduser()
    for label, path, expected_name in (
        ("spec", spec_path, "capture-spec.json"),
        ("index", index_path, "capture-index.json"),
    ):
        if path.is_symlink():
            errors.append(f"capture receipt {label} may not be a symlink")
            continue
        resolved = path.resolve()
        if not resolved.is_file() or not path_is_within(resolved, run_root):
            errors.append(f"capture receipt {label} must be a runtime-owned file")
        if resolved.name != expected_name:
            errors.append(f"capture receipt {label} has a non-canonical filename")
    spec_path = spec_path.resolve()
    index_path = index_path.resolve()
    if spec_path.parent != index_path.parent:
        errors.append(
            "capture receipt spec and index must share the canonical capture directory"
        )
    if errors:
        return errors
    if sha256_file(spec_path) != receipt.get("spec_sha256"):
        errors.append("capture receipt spec hash drifted")
    if sha256_file(index_path) != receipt.get("index_sha256"):
        errors.append("capture receipt index hash drifted")
    if receipt.get("source_fingerprint_digest") != run.get(
        "project_fingerprint", {}
    ).get("digest"):
        errors.append("capture receipt source fingerprint differs from the design run")
    try:
        index = read_json(index_path)
        if index.get("status") != "passed":
            errors.append("canonical capture index did not pass")
        exact_bindings = {
            "run_id": run.get("run_id"),
            "nonce": nonce,
            "adapter_sha256": receipt.get("adapter_sha256"),
            "source_fingerprint_digest": receipt.get("source_fingerprint_digest"),
            "spec": str(spec_path),
            "spec_sha256": receipt.get("spec_sha256"),
            "project_root": str(
                Path(str(run.get("project_root", ""))).expanduser().resolve()
            ),
        }
        for field, expected in exact_bindings.items():
            actual = index.get(field)
            if field in {"spec", "project_root"}:
                actual = str(Path(str(actual)).expanduser().resolve())
            if actual != expected:
                errors.append(
                    f"capture index {field} differs from its canonical receipt binding"
                )
        manifest_path = (
            Path(str(run.get("evidence_manifest", ""))).expanduser().resolve()
        )
        manifest = read_json(manifest_path)
        fresh_manifest = {
            "schema": SCHEMA_EVIDENCE,
            "run_id": run.get("run_id"),
            "project_root": str(
                Path(str(run.get("project_root", ""))).expanduser().resolve()
            ),
            "project_fingerprint_digest": run.get("project_fingerprint", {}).get(
                "digest"
            ),
            "generated_at": utc_now(),
            "items": [],
            "coverage": {
                "routes": [],
                "states": [],
                "viewports": [],
                "tuples": [],
                "source_scan": False,
                "accessibility": False,
                "critic": False,
            },
        }
        ingest_capture_index(
            fresh_manifest,
            index_path,
            trusted=True,
            expected_run=run,
            expected_nonce=nonce,
            adapter_sha256=str(receipt.get("adapter_sha256", "")),
            fingerprint_digest=str(receipt.get("source_fingerprint_digest", "")),
            command="canonical-revalidation",
        )
        expected_projection = sorted(
            (capture_item_projection(item) for item in fresh_manifest["items"]),
            key=lambda item: (str(item.get("path")), str(item.get("kind"))),
        )
        actual_projection = sorted(
            (
                capture_item_projection(item)
                for item in manifest.get("items", [])
                if item.get("provenance", {}).get("trust") == "runtime-adapter"
            ),
            key=lambda item: (str(item.get("path")), str(item.get("kind"))),
        )
        if actual_projection != expected_projection:
            errors.append(
                "runtime-adapter evidence is not the canonical projection of the capture index"
            )
        projection_digest = capture_projection_digest(manifest)
        if receipt.get("evidence_projection_sha256") != projection_digest:
            errors.append(
                "capture receipt evidence projection hash differs from the manifest"
            )
    except (OSError, ValueError) as exc:
        errors.append(f"canonical capture receipt revalidation failed: {exc}")
    return errors


def validate_capture_attestation(
    run: dict[str, Any],
    manifest: dict[str, Any],
    attestation_path: Path | None = None,
) -> list[str]:
    if attestation_path is None:
        raw = str(run.get("capture_attestation", ""))
        attestation_path = Path(raw).expanduser().resolve() if raw else None
    if (
        attestation_path is None
        or not attestation_path.is_file()
        or attestation_path.is_symlink()
    ):
        return ["external capture attestation is missing"]
    stored_path = str(run.get("capture_attestation", ""))
    if (
        stored_path
        and Path(stored_path).expanduser().resolve() != attestation_path.resolve()
    ):
        return ["capture attestation path differs from the frozen design run"]
    stored_hash = str(run.get("capture_attestation_sha256", ""))
    if stored_hash and stored_hash != sha256_file(attestation_path):
        return ["capture attestation is hash-drifted"]
    attestation = read_json(attestation_path)
    if attestation.get("schema") != CAPTURE_ATTESTATION_SCHEMA:
        return [f"unsupported capture attestation schema: {attestation.get('schema')}"]
    payload = attestation.get("payload")
    if not isinstance(payload, dict):
        return ["capture attestation payload is missing"]
    receipts = run.get("capture_receipts", [])
    if len(receipts) != 1 or not isinstance(receipts[0], dict):
        return ["exactly one canonical capture receipt is required for attestation"]
    receipt = receipts[0]
    policy = run.get("trust_policy", {})
    expected = {
        "schema": "design-capture-attestation-payload-v1",
        "run_id": run.get("run_id"),
        "issuer": payload.get("issuer"),
        "execution_id": payload.get("execution_id"),
        "authority_id": policy.get("authority_id"),
        "receipt_sha256": receipt.get("receipt_sha256"),
        "adapter_sha256": receipt.get("adapter_sha256"),
        "spec_sha256": receipt.get("spec_sha256"),
        "index_sha256": receipt.get("index_sha256"),
        "source_fingerprint_digest": receipt.get("source_fingerprint_digest"),
        "evidence_projection_sha256": capture_projection_digest(manifest),
        "issued_at": payload.get("issued_at"),
    }
    errors: list[str] = []
    if payload != expected:
        errors.append(
            "capture attestation payload is not exactly bound to the canonical receipt, source, and evidence projection"
        )
    if not isinstance(payload.get("issuer"), str) or len(payload.get("issuer", "")) < 3:
        errors.append("capture attestation issuer is missing")
    if (
        not isinstance(payload.get("execution_id"), str)
        or len(payload.get("execution_id", "")) < 6
    ):
        errors.append("capture attestation execution_id is missing")
    if (
        not isinstance(payload.get("issued_at"), str)
        or len(payload.get("issued_at", "")) < 10
    ):
        errors.append("capture attestation issued_at is missing")
    public_key = Path(str(policy.get("public_key", ""))).expanduser().resolve()
    if not public_key.is_file() or sha256_file(public_key) != policy.get(
        "public_key_sha256"
    ):
        errors.append(
            "configured capture authority public key is missing or hash-drifted"
        )
    else:
        errors.extend(
            verify_ed25519_signature(
                public_key, payload, str(attestation.get("signature", ""))
            )
        )
    return errors


def validate_run_shape(run: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = (
        "run_id",
        "project_root",
        "implementation_actor_id",
        "mode",
        "surface",
        "register",
        "platform",
        "design_read",
        "dials",
        "slop_risks",
        "design_read_fingerprint",
        "project_fingerprint",
        "capture_receipts",
        "capture_attestation",
        "capture_attestation_sha256",
        "trust_policy",
        "validation",
        "repair_policy",
        "repair_history",
        "status",
    )
    if run.get("schema") != SCHEMA_RUN:
        errors.append(f"unsupported run schema: {run.get('schema')}")
    for field in required:
        if field not in run:
            errors.append(f"missing run field: {field}")
    if len(str(run.get("design_read", ""))) < 20:
        errors.append("design_read must be at least 20 characters")
    dials = run.get("dials", {})
    for name in ("distinction", "motion", "density", "evidence", "systemness"):
        value = dials.get(name)
        if not isinstance(value, int) or not 1 <= value <= 10:
            errors.append(f"dial {name} must be an integer in range 1..10")
    policy = run.get("repair_policy", {})
    if policy.get("max_rounds", 99) > 2:
        errors.append("repair_policy.max_rounds may not exceed 2")
    if policy.get("critic_must_be_independent") is not True:
        errors.append("critic_must_be_independent must be true")
    fingerprint = run.get("project_fingerprint", {})
    if not fingerprint.get("files") or fingerprint.get("truncated") is not False:
        errors.append(
            "project fingerprint must contain the complete non-empty candidate set"
        )
    baseline = run.get("design_read_fingerprint", {})
    if not baseline.get("files") or baseline.get("truncated") is not False:
        errors.append(
            "design-read fingerprint must contain the complete non-empty candidate set"
        )
    for field in ("routes", "states", "viewports"):
        values = run.get(field)
        if not isinstance(values, list) or not values:
            errors.append(f"{field} must be a non-empty array")
    for viewport in run.get("viewports", []):
        if (
            not isinstance(viewport, dict)
            or not viewport.get("name")
            or not isinstance(viewport.get("width"), int)
            or not isinstance(viewport.get("height"), int)
        ):
            errors.append("each viewport must declare name and integer width/height")
    errors.extend(validate_capture_receipts(run))
    errors.extend(validate_trust_policy(run))
    if run.get("waivers"):
        errors.append(
            "waivers are diagnostic only and cannot be promoted by Design Runtime"
        )
    history = run.get("repair_history")
    if not isinstance(history, list) or len(history) > policy.get("max_rounds", 2):
        errors.append("repair_history must be an append-only list within max_rounds")
    else:
        previous = ""
        for index, record in enumerate(history, start=1):
            if not isinstance(record, dict) or record.get("round") != index:
                errors.append(f"repair_history[{index - 1}] has an invalid round")
                continue
            if record.get("previous_record_sha256", "") != previous:
                errors.append(f"repair_history[{index - 1}] hash chain is broken")
            canonical = {
                key: value for key, value in record.items() if key != "record_sha256"
            }
            actual = hashlib.sha256(
                json.dumps(canonical, sort_keys=True, separators=(",", ":")).encode()
            ).hexdigest()
            if record.get("record_sha256") != actual:
                errors.append(f"repair_history[{index - 1}] record hash is invalid")
            critic_path = (
                Path(str(record.get("critic_path", ""))).expanduser().resolve()
            )
            if not critic_path.is_file() or sha256_file(critic_path) != record.get(
                "critic_sha256"
            ):
                errors.append(
                    f"repair_history[{index - 1}] critic is missing or hash-drifted"
                )
            else:
                repair_critic = read_json(critic_path)
                if (
                    repair_critic.get("schema") != SCHEMA_CRITIC
                    or repair_critic.get("run_id") != run.get("run_id")
                    or repair_critic.get("round") != index - 1
                    or repair_critic.get("decision") != "repair"
                ):
                    errors.append(
                        f"repair_history[{index - 1}] critic does not prove that repair round"
                    )
            changed_files = record.get("changed_files")
            if not isinstance(changed_files, list) or not changed_files:
                errors.append(
                    f"repair_history[{index - 1}] has no changed-file evidence"
                )
            verifications = record.get("verification")
            if not isinstance(verifications, list) or not verifications:
                errors.append(
                    f"repair_history[{index - 1}] has no verification artifacts"
                )
            else:
                for verification in verifications:
                    if not isinstance(verification, dict):
                        errors.append(
                            f"repair_history[{index - 1}] verification is not an artifact record"
                        )
                        continue
                    path = (
                        Path(str(verification.get("path", ""))).expanduser().resolve()
                    )
                    if not path.is_file() or sha256_file(path) != verification.get(
                        "sha256"
                    ):
                        errors.append(
                            f"repair_history[{index - 1}] verification artifact is missing or hash-drifted"
                        )
            previous = str(record.get("record_sha256", ""))
    return errors


def waiver_exists(run: dict[str, Any], gate: str) -> bool:
    return any(
        waiver.get("gate") == gate
        and waiver.get("reason")
        and waiver.get("approved_by")
        for waiver in run.get("waivers", [])
    )


def validate_fingerprint(run: dict[str, Any]) -> list[str]:
    root = Path(run.get("project_root", ""))
    errors: list[str] = []
    if not root.is_dir():
        return [f"project_root missing: {root}"]
    stored = run.get("project_fingerprint", {})
    for entry in stored.get("files", []):
        path = root / entry.get("path", "")
        if not path.is_file():
            errors.append(f"fingerprint file missing: {path}")
        elif sha256_file(path) != entry.get("sha256"):
            errors.append(f"project changed after design read: {path}")
    current = build_fingerprint(root)
    if current.get("digest") != stored.get("digest") or current.get(
        "files"
    ) != stored.get("files"):
        errors.append(
            "project fingerprint candidate set or digest changed after design read"
        )
    return errors


def validate_evidence(
    run: dict[str, Any], manifest: dict[str, Any], *, require_evaluation: bool
) -> tuple[list[str], dict[str, bool]]:
    errors: list[str] = []
    checks = {
        "source_scan": False,
        "visual_evidence": False,
        "state_coverage": False,
        "accessibility": False,
        "independent_critic": False,
        "evaluation": False,
    }
    if manifest.get("schema") != SCHEMA_EVIDENCE:
        errors.append(f"unsupported evidence schema: {manifest.get('schema')}")
        return errors, checks
    if manifest.get("run_id") != run.get("run_id"):
        errors.append("run_id mismatch between run and evidence manifest")
    if (
        Path(str(manifest.get("project_root", ""))).expanduser().resolve()
        != Path(str(run.get("project_root", ""))).expanduser().resolve()
    ):
        errors.append("project_root mismatch between run and evidence manifest")
    if manifest.get("project_fingerprint_digest") != run.get(
        "project_fingerprint", {}
    ).get("digest"):
        errors.append("project fingerprint mismatch between run and evidence manifest")
    passed_kinds: set[str] = set()
    trusted_items: list[dict[str, Any]] = []
    for item in manifest.get("items", []):
        artifact = Path(item.get("path", ""))
        if not artifact.is_file():
            errors.append(f"evidence file missing: {artifact}")
            continue
        if sha256_file(artifact) != item.get("sha256"):
            errors.append(f"evidence hash drift: {artifact}")
            continue
        kind = item.get("kind", "")
        try:
            errors.extend(validate_artifact_content(kind, artifact))
        except ValueError as exc:
            errors.append(str(exc))
            continue
        provenance = item.get("provenance", {})
        producer = provenance.get("producer") if isinstance(provenance, dict) else None
        trusted = producer in TRUSTED_PRODUCERS and provenance.get("trust") in {
            "runtime",
            "runtime-adapter",
        }
        source_index = (
            provenance.get("source_index") if isinstance(provenance, dict) else None
        )
        if source_index:
            index_path = Path(str(source_index)).expanduser().resolve()
            if not index_path.is_file() or sha256_file(index_path) != provenance.get(
                "source_index_sha256"
            ):
                errors.append(f"capture index missing or hash-drifted: {index_path}")
                trusted = False
        if item.get("verdict") == "pass" and trusted:
            passed_kinds.add(kind)
            trusted_items.append(item)
        if item.get("kind") == "source-scan":
            hard_failures = item.get("finding_counts", {}).get("hard-fail", 0)
            payload = read_json(artifact)
            hard_failures = payload.get("counts", {}).get("hard-fail", hard_failures)
            if item.get("verdict") == "pass" and trusted and hard_failures == 0:
                checks["source_scan"] = True
            else:
                errors.append(f"source scan {item.get('id')} did not pass")
    platform = run.get("platform", {}).get("kind", "unknown")
    spec = load_platform_registry()["platforms"].get(
        platform, load_platform_registry()["platforms"]["unknown"]
    )
    for kind in spec["required_evidence"]:
        if kind not in passed_kinds:
            errors.append(f"required {platform} evidence missing: {kind}")
    checks["visual_evidence"] = "result-screenshot" in passed_kinds
    visual_modes = {
        "measure",
        "craft",
        "audit",
        "polish",
        "redesign",
        "typeset",
        "colorize",
        "animate",
        "harden",
    }
    if run.get("mode") in visual_modes and not (
        {"baseline-screenshot", "result-screenshot"} & passed_kinds
    ):
        errors.append(f"visual evidence missing for mode: {run.get('mode')}")
    if run.get("mode") == "redesign" and not {
        "baseline-screenshot",
        "result-screenshot",
    }.issubset(passed_kinds):
        errors.append(
            "redesign requires both trusted baseline-screenshot and result-screenshot evidence"
        )
    if platform == "web":
        checks["accessibility"] = "accessibility-tree" in passed_kinds
    else:
        checks["accessibility"] = any(
            item.get("verdict") == "pass"
            and "accessibility" in item.get("supports", [])
            for item in trusted_items
        )
    if platform in {"web", "flutter"} and not checks["accessibility"]:
        errors.append(f"required {platform} accessibility/semantics evidence missing")
    requested_tuples = {
        evidence_tuple(route, state, viewport.get("name"))
        for route in run.get("routes", [])
        for state in run.get("states", [])
        for viewport in run.get("viewports", [])
    }
    requested_tuples.discard(None)
    covered_tuples = {
        evidence_tuple(item.get("route"), item.get("state"), item.get("viewport"))
        for item in trusted_items
        if item.get("kind") == "result-screenshot"
    }
    covered_tuples.discard(None)
    assertion_tuples = {
        evidence_tuple(item.get("route"), item.get("state"), item.get("viewport"))
        for item in trusted_items
        if item.get("kind") == "state-assertion"
    }
    assertion_tuples.discard(None)
    accessibility_tuples = {
        evidence_tuple(item.get("route"), item.get("state"), item.get("viewport"))
        for item in trusted_items
        if item.get("kind") == "accessibility-tree"
    }
    accessibility_tuples.discard(None)
    required_assertion_tuples = {
        evidence_tuple(route, state, viewport.get("name"))
        for route in run.get("routes", [])
        for state in run.get("states", [])
        if state != "default"
        for viewport in run.get("viewports", [])
    }
    missing_assertions = sorted(required_assertion_tuples - assertion_tuples)
    if missing_assertions:
        errors.append(
            "missing passing state assertions: " + ", ".join(missing_assertions)
        )
    if platform == "web":
        missing_semantics = sorted(requested_tuples - accessibility_tuples)
        if missing_semantics:
            errors.append(
                "missing tuple-specific accessibility semantics: "
                + ", ".join(missing_semantics)
            )
    if run.get("mode") == "redesign":
        baseline_tuples = {
            evidence_tuple(item.get("route"), item.get("state"), item.get("viewport"))
            for item in trusted_items
            if item.get("kind") == "baseline-screenshot"
        }
        baseline_tuples.discard(None)
        missing_baselines = sorted(requested_tuples - baseline_tuples)
        if missing_baselines:
            errors.append(
                "missing comparable redesign baselines: " + ", ".join(missing_baselines)
            )
    missing_tuples = sorted(requested_tuples - covered_tuples)
    if missing_tuples:
        errors.append(
            "missing route/state/viewport tuples: " + ", ".join(missing_tuples)
        )
    checks["state_coverage"] = (
        not missing_tuples
        and not missing_assertions
        and (platform != "web" or not (requested_tuples - accessibility_tuples))
        and (run.get("mode") != "redesign" or not (requested_tuples - baseline_tuples))
        and bool(requested_tuples)
    )
    if require_evaluation:
        checks["evaluation"] = "evaluation-result" in passed_kinds
        if not checks["evaluation"]:
            errors.append("passing runtime-generated evaluation result missing")
    return errors, checks


def review_packet_for(
    run: dict[str, Any], manifest_path: Path, detector_path: Path
) -> dict[str, Any]:
    manifest = read_json(manifest_path)
    return {
        "schema": REVIEW_PACKET_SCHEMA,
        "run_id": run["run_id"],
        "implementation_actor_id": run["implementation_actor_id"],
        "source_fingerprint_digest": run["project_fingerprint"]["digest"],
        "evidence_manifest": str(manifest_path),
        "evidence_manifest_sha256": review_manifest_digest(manifest),
        "detector": str(detector_path),
        "detector_sha256": sha256_file(detector_path),
        "capture_receipt_sha256": [
            receipt["receipt_sha256"] for receipt in run.get("capture_receipts", [])
        ],
        "capture_attestation_sha256": run.get("capture_attestation_sha256", ""),
        "trusted_evidence_ids": [
            item["id"]
            for item in manifest.get("items", [])
            if item.get("verdict") == "pass"
            and item.get("provenance", {}).get("trust")
            in {"runtime", "runtime-adapter"}
        ],
        "public_key_sha256": run.get("trust_policy", {}).get("public_key_sha256", ""),
        "prepared_at": utc_now(),
    }


def validate_critic_attestation(
    run: dict[str, Any],
    manifest: dict[str, Any],
    critic_path: Path,
    attestation_path: Path | None,
) -> list[str]:
    if attestation_path is None:
        raw = run.get("critic_attestation")
        attestation_path = Path(raw).expanduser().resolve() if raw else None
    if attestation_path is None or not attestation_path.is_file():
        return ["signed orchestrator critic attestation missing"]
    attestation = read_json(attestation_path)
    if attestation.get("schema") != CRITIC_ATTESTATION_SCHEMA:
        return [f"unsupported critic attestation schema: {attestation.get('schema')}"]
    payload = attestation.get("payload")
    if not isinstance(payload, dict):
        return ["critic attestation payload is missing"]
    errors: list[str] = []
    packet_path = Path(str(run.get("review_packet", ""))).expanduser().resolve()
    if not packet_path.is_file() or sha256_file(packet_path) != run.get(
        "review_packet_sha256"
    ):
        errors.append("review packet is missing or hash-drifted")
        packet: dict[str, Any] = {}
    else:
        packet = read_json(packet_path)
    manifest_path = Path(str(run.get("evidence_manifest", ""))).expanduser().resolve()
    critic = read_json(critic_path)
    expected = {
        "schema": "design-critic-attestation-payload-v1",
        "run_id": run.get("run_id"),
        "issuer": payload.get("issuer"),
        "execution_id": payload.get("execution_id"),
        "critic_actor_id": critic.get("critic_id"),
        "implementation_actor_id": run.get("implementation_actor_id"),
        "review_packet_sha256": run.get("review_packet_sha256"),
        "critic_sha256": sha256_file(critic_path),
        "evidence_manifest_sha256": review_manifest_digest(manifest)
        if manifest_path.is_file()
        else "",
        "source_fingerprint_digest": run.get("project_fingerprint", {}).get("digest"),
        "issued_at": payload.get("issued_at"),
    }
    if payload != expected:
        errors.append(
            "critic attestation payload is not exactly bound to the current review packet, critic, evidence, and source"
        )
    if not isinstance(payload.get("issuer"), str) or len(payload.get("issuer", "")) < 3:
        errors.append("critic attestation issuer is missing")
    if (
        not isinstance(payload.get("execution_id"), str)
        or len(payload.get("execution_id", "")) < 6
    ):
        errors.append("critic attestation execution_id is missing")
    if packet.get("schema") != REVIEW_PACKET_SCHEMA:
        errors.append("review packet schema is invalid")
    elif packet.get("evidence_manifest_sha256") != expected["evidence_manifest_sha256"]:
        errors.append("evidence manifest changed after review packet preparation")
    policy = run.get("trust_policy", {})
    public_key = Path(str(policy.get("public_key", ""))).expanduser().resolve()
    if not public_key.is_file() or sha256_file(public_key) != policy.get(
        "public_key_sha256"
    ):
        errors.append("configured critic public key is missing or hash-drifted")
    else:
        errors.extend(
            verify_ed25519_signature(
                public_key, payload, str(attestation.get("signature", ""))
            )
        )
    return errors


def command_prepare_review(args: argparse.Namespace) -> int:
    run_path = Path(args.run).expanduser().resolve()
    run = read_json(run_path)
    manifest_path = (
        Path(args.evidence or run.get("evidence_manifest", "")).expanduser().resolve()
    )
    manifest = read_json(manifest_path)
    shape_errors = validate_run_shape(run)
    fingerprint_errors = validate_fingerprint(run)
    if not run.get("capture_receipts"):
        shape_errors.append(
            "runtime-owned capture receipt missing; diagnostic imports cannot be reviewed"
        )
    policy = run.get("trust_policy", {})
    public_key = Path(str(policy.get("public_key", ""))).expanduser().resolve()
    if not public_key.is_file() or sha256_file(public_key) != policy.get(
        "public_key_sha256"
    ):
        shape_errors.append(
            "an external critic Ed25519 public key is required before review"
        )
    capture_attestation_path = (
        Path(args.capture_attestation).expanduser().resolve()
        if args.capture_attestation
        else Path(str(run.get("capture_attestation", ""))).expanduser().resolve()
        if run.get("capture_attestation")
        else None
    )
    capture_attestation_errors = validate_capture_attestation(
        run, manifest, capture_attestation_path
    )
    if shape_errors or fingerprint_errors or capture_attestation_errors:
        raise ValueError(
            "review preparation failed: "
            + "; ".join(shape_errors + fingerprint_errors + capture_attestation_errors)
        )
    assert capture_attestation_path is not None
    run["capture_attestation"] = str(capture_attestation_path)
    run["capture_attestation_sha256"] = sha256_file(capture_attestation_path)
    detector_path = run_path.parent / "detector-result.json"
    detector = run_live_detector(run, detector_path)
    if detector.get("counts", {}).get("hard-fail", 0):
        raise ValueError("design-slop detector reported hard-fail findings")
    upsert_runtime_evidence(
        manifest,
        evidence_id="runtime-source-scan",
        kind="source-scan",
        path=detector_path,
        producer="design-runtime-detector@1",
        supports=["anti-slop", "source-scan"],
    )
    manifest["coverage"]["source_scan"] = True
    write_json(manifest_path, manifest)
    evidence_errors, checks = validate_evidence(run, manifest, require_evaluation=False)
    required_checks = (
        "source_scan",
        "visual_evidence",
        "state_coverage",
        "accessibility",
    )
    if evidence_errors or any(not checks[name] for name in required_checks):
        raise ValueError(
            "review evidence failed: "
            + "; ".join(
                evidence_errors or ["required mechanical checks are not all true"]
            )
        )
    packet_path = (
        Path(args.output).expanduser().resolve()
        if args.output
        else run_path.parent / "review-packet.json"
    )
    packet = review_packet_for(run, manifest_path, detector_path)
    write_json(packet_path, packet)
    run["review_packet"] = str(packet_path)
    run["review_packet_sha256"] = sha256_file(packet_path)
    run["critic_attestation"] = ""
    run["status"] = "needs_review"
    run["validation"] = checks
    write_json(run_path, run)
    print(
        json.dumps(
            {
                "status": "needs_review",
                "review_packet": str(packet_path),
                "review_packet_sha256": run["review_packet_sha256"],
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


def validate_critic(
    run: dict[str, Any],
    manifest: dict[str, Any],
    critic_path: Path | None,
    attestation_path: Path | None = None,
    *,
    require_attestation: bool = True,
) -> tuple[list[str], bool]:
    if critic_path is None:
        raw = run.get("critic_result")
        critic_path = Path(raw).expanduser().resolve() if raw else None
    if critic_path is None or not critic_path.is_file():
        return ["independent critic result missing"], False
    critic = read_json(critic_path)
    errors: list[str] = []
    if critic.get("schema") != SCHEMA_CRITIC:
        errors.append(f"unsupported critic schema: {critic.get('schema')}")
    if critic.get("run_id") != run.get("run_id"):
        errors.append("critic run_id mismatch")
    if critic.get("independent") is not True:
        errors.append("critic must be independent from the implementer")
    actor = critic.get("actor")
    if not isinstance(actor, dict):
        errors.append("critic actor provenance is missing")
        actor = {}
    implementation_actor_id = run.get("implementation_actor_id")
    if actor.get("role") != "independent_critic":
        errors.append("critic actor role must be independent_critic")
    if (
        actor.get("actor_id") != critic.get("critic_id")
        or actor.get("actor_id") == implementation_actor_id
    ):
        errors.append("critic actor must differ from the implementation actor")
    if actor.get("implementation_actor_id") != implementation_actor_id:
        errors.append("critic actor provenance does not name the implementation actor")
    context_path = Path(str(actor.get("context_manifest", ""))).expanduser().resolve()
    if not context_path.is_file() or sha256_file(context_path) != actor.get(
        "context_manifest_sha256"
    ):
        errors.append("critic context manifest is missing or hash-drifted")
    else:
        context = read_json(context_path)
        errors.extend(critic_context_errors(context))
    round_number = int(critic.get("round", -1))
    if round_number != len(run.get("repair_history", [])):
        errors.append("critic round is not backed by append-only repair_history")
    evidence_ids = {
        item.get("id")
        for item in manifest.get("items", [])
        if item.get("verdict") == "pass"
        and item.get("kind") != "evaluation-result"
        and item.get("provenance", {}).get("producer") in TRUSTED_PRODUCERS
        and item.get("provenance", {}).get("trust") in {"runtime", "runtime-adapter"}
    }
    missing = set(critic.get("evidence_ids", [])) - evidence_ids
    if missing:
        errors.append(
            f"critic references unknown evidence: {', '.join(sorted(missing))}"
        )
    if critic.get("decision") != "pass":
        errors.append(f"critic decision is {critic.get('decision')!r}, not pass")
    if set(critic.get("evidence_ids", [])) != evidence_ids:
        errors.append("critic must review the complete trusted evidence packet")
    rubric_scores = critic.get("rubric_scores")
    if not isinstance(rubric_scores, dict) or not rubric_scores:
        errors.append("critic rubric_scores are missing")
    if require_attestation:
        errors.extend(
            validate_critic_attestation(run, manifest, critic_path, attestation_path)
        )
    return errors, not errors


def run_validation(
    run_path: Path,
    manifest_path: Path,
    critic_path: Path | None,
    check_fingerprint: bool,
    *,
    require_evaluation: bool,
    attestation_path: Path | None = None,
) -> tuple[dict[str, Any], list[str]]:
    run = read_json(run_path)
    manifest = read_json(manifest_path)
    errors = validate_run_shape(run)
    if check_fingerprint:
        errors.extend(validate_fingerprint(run))
    evidence_errors, checks = validate_evidence(
        run, manifest, require_evaluation=require_evaluation
    )
    errors.extend(evidence_errors)
    errors.extend(validate_capture_attestation(run, manifest))
    critic_errors, critic_ok = validate_critic(
        run, manifest, critic_path, attestation_path, require_attestation=True
    )
    errors.extend(critic_errors)
    checks["independent_critic"] = critic_ok
    run["validation"] = checks
    return run, errors


def command_validate(args: argparse.Namespace) -> int:
    run_path = Path(args.run).expanduser().resolve()
    run_initial = read_json(run_path)
    manifest_path = (
        Path(args.evidence or run_initial.get("evidence_manifest", ""))
        .expanduser()
        .resolve()
    )
    critic_path = Path(args.critic).expanduser().resolve() if args.critic else None
    attestation_path = (
        Path(args.attestation).expanduser().resolve() if args.attestation else None
    )
    require_evaluation = run_initial.get("status") in {
        "passed",
        "ready_for_external_promotion",
    }
    run, errors = run_validation(
        run_path,
        manifest_path,
        critic_path,
        not args.allow_project_drift,
        require_evaluation=require_evaluation,
        attestation_path=attestation_path,
    )
    if args.allow_project_drift:
        errors.append("project drift check was bypassed; promotion is forbidden")
    if run_initial.get("status") == "passed":
        errors.append(
            "local Design Runtime may not assert passed; external provider/orchestrator promotion is required"
        )
    all_required_checks = (
        all(run["validation"].values())
        if require_evaluation
        else all(
            run["validation"][name]
            for name in (
                "source_scan",
                "visual_evidence",
                "state_coverage",
                "accessibility",
                "independent_critic",
            )
        )
    )
    if not all_required_checks:
        errors.append("required validation checks are not all true")
    status = (
        "ready_for_external_promotion"
        if not errors and require_evaluation
        else "ready_for_finalize"
        if not errors
        else "needs_evidence"
        if any("missing" in error for error in errors)
        else "failed"
    )
    result = {
        "schema": "design-runtime-validation-v1",
        "run_id": run.get("run_id"),
        "status": status,
        "checks": run["validation"],
        "errors": errors,
    }
    if args.write_status:
        run["status"] = status
        if critic_path:
            run["critic_result"] = str(critic_path)
        if attestation_path:
            run["critic_attestation"] = str(attestation_path)
        write_json(run_path, run)
    if args.output:
        write_json(Path(args.output).expanduser().resolve(), result)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if not errors else 2


def command_finalize(args: argparse.Namespace) -> int:
    run_path = Path(args.run).expanduser().resolve()
    run = read_json(run_path)
    manifest_path = (
        Path(args.evidence or run.get("evidence_manifest", "")).expanduser().resolve()
    )
    critic_path = Path(args.critic).expanduser().resolve()
    attestation_path = Path(args.attestation).expanduser().resolve()
    manifest = read_json(manifest_path)
    output_dir = run_path.parent
    packet_path = Path(str(run.get("review_packet", ""))).expanduser().resolve()
    if not packet_path.is_file() or sha256_file(packet_path) != run.get(
        "review_packet_sha256"
    ):
        raise ValueError(
            "prepare-review must create an unchanged review packet before finalization"
        )
    packet = read_json(packet_path)
    detector_path = Path(str(packet.get("detector", ""))).expanduser().resolve()
    if not detector_path.is_file() or sha256_file(detector_path) != packet.get(
        "detector_sha256"
    ):
        raise ValueError("prepared detector evidence is missing or hash-drifted")
    live_detector_path = output_dir / ".detector-finalize.json"
    live_detector = run_live_detector(run, live_detector_path)
    prepared_detector = read_json(detector_path)
    live_detector_path.unlink(missing_ok=True)
    if live_detector != prepared_detector:
        raise ValueError("live source detector result changed after independent review")

    preflight_run, errors = run_validation(
        run_path,
        manifest_path,
        critic_path,
        True,
        require_evaluation=False,
        attestation_path=attestation_path,
    )
    if errors:
        raise ValueError("finalization preflight failed: " + "; ".join(errors))

    evaluation_path = output_dir / "evaluation-result.json"
    process = subprocess.run(
        [
            sys.executable,
            str(GRADER),
            "grade",
            "--run",
            str(run_path),
            "--evidence",
            str(manifest_path),
            "--critic",
            str(critic_path),
            "--detector",
            str(detector_path),
            "--attestation",
            str(attestation_path),
            "--public-key",
            str(run.get("trust_policy", {}).get("public_key", "")),
            "--review-packet",
            str(packet_path),
            "--output",
            str(evaluation_path),
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    if process.returncode != 0:
        raise ValueError(
            process.stderr.strip()
            or process.stdout.strip()
            or "UI design grader failed"
        )

    manifest = read_json(manifest_path)
    upsert_runtime_evidence(
        manifest,
        evidence_id="runtime-evaluation",
        kind="evaluation-result",
        path=evaluation_path,
        producer="ui-design-grader@3",
        supports=["final-evaluation"],
    )
    write_json(manifest_path, manifest)
    final_run, final_errors = run_validation(
        run_path,
        manifest_path,
        critic_path,
        True,
        require_evaluation=True,
        attestation_path=attestation_path,
    )
    if final_errors or not all(final_run["validation"].values()):
        raise ValueError(
            "finalization integrity check failed: " + "; ".join(final_errors)
        )
    final_run["status"] = "ready_for_external_promotion"
    final_run["critic_result"] = str(critic_path)
    final_run["critic_attestation"] = str(attestation_path)
    final_run["final_evaluation"] = str(evaluation_path)
    final_run["finalized_at"] = utc_now()
    write_json(run_path, final_run)
    result = {
        "schema": "design-runtime-finalization-v1",
        "run_id": final_run["run_id"],
        "status": "ready_for_external_promotion",
        "checks": final_run["validation"],
        "detector": str(detector_path),
        "evaluation": str(evaluation_path),
    }
    if args.output:
        write_json(Path(args.output).expanduser().resolve(), result)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


def command_critic_template(args: argparse.Namespace) -> int:
    run = read_json(Path(args.run).expanduser().resolve())
    manifest = read_json(
        Path(args.evidence or run.get("evidence_manifest", "")).expanduser().resolve()
    )
    context_path = Path(args.context_manifest).expanduser().resolve()
    context = read_json(context_path)
    context_errors = critic_context_errors(context)
    if context_errors:
        raise ValueError(
            "critic context manifest invalid: " + "; ".join(context_errors)
        )
    if args.critic_id == run.get("implementation_actor_id"):
        raise ValueError("critic actor must differ from implementation_actor_id")
    packet_path = Path(str(run.get("review_packet", ""))).expanduser().resolve()
    if not packet_path.is_file() or sha256_file(packet_path) != run.get(
        "review_packet_sha256"
    ):
        raise ValueError(
            "prepare-review must create an immutable review packet before critic work"
        )
    if args.round != len(run.get("repair_history", [])):
        raise ValueError(
            "critic round must equal the append-only repair_history length"
        )
    trusted_evidence_ids = [
        item["id"]
        for item in manifest.get("items", [])
        if item.get("provenance", {}).get("producer") in TRUSTED_PRODUCERS
    ]
    if not trusted_evidence_ids:
        raise ValueError("critic template requires trusted capture evidence")
    payload = {
        "schema": SCHEMA_CRITIC,
        "run_id": run["run_id"],
        "critic_id": args.critic_id,
        "independent": True,
        "actor": {
            "actor_id": args.critic_id,
            "role": "independent_critic",
            "implementation_actor_id": run.get("implementation_actor_id"),
            "context_manifest": str(context_path),
            "context_manifest_sha256": sha256_file(context_path),
            "issued_at": utc_now(),
        },
        "round": args.round,
        "review_packet": str(packet_path),
        "review_packet_sha256": run.get("review_packet_sha256"),
        "evidence_ids": trusted_evidence_ids,
        "findings": [],
        "rubric_scores": {},
        "decision": "repair",
        "summary": "Replace with an evidence-backed independent review. Do not preserve implementer rationale as fact.",
    }
    output = Path(args.out).expanduser().resolve()
    write_json(output, payload)
    print(str(output))
    return 0


def command_record_repair(args: argparse.Namespace) -> int:
    run_path = Path(args.run).expanduser().resolve()
    critic_path = Path(args.critic).expanduser().resolve()
    run = read_json(run_path)
    critic = read_json(critic_path)
    attestation_path = Path(args.attestation).expanduser().resolve()
    history = list(run.get("repair_history", []))
    expected_critic_round = len(history)
    if critic.get("run_id") != run.get("run_id"):
        raise ValueError("repair critic run_id mismatch")
    if (
        critic.get("round") != expected_critic_round
        or critic.get("decision") != "repair"
    ):
        raise ValueError(
            "record-repair requires the current round critic decision=repair"
        )
    manifest_path = Path(run["evidence_manifest"]).expanduser().resolve()
    manifest = read_json(manifest_path)
    attestation_errors = validate_critic_attestation(
        run, manifest, critic_path, attestation_path
    )
    if attestation_errors:
        raise ValueError(
            "repair critic attestation failed: " + "; ".join(attestation_errors)
        )
    actor = critic.get("actor", {})
    if (
        critic.get("independent") is not True
        or actor.get("actor_id") == run.get("implementation_actor_id")
        or actor.get("role") != "independent_critic"
    ):
        raise ValueError("repair critic is not an attested independent actor")
    if len(history) >= run.get("repair_policy", {}).get("max_rounds", 2):
        raise ValueError("bounded repair limit reached")
    root = Path(run["project_root"]).expanduser().resolve()
    changed_files: list[dict[str, str]] = []
    for raw in args.changed_file:
        path = Path(raw).expanduser().resolve()
        try:
            relative = path.relative_to(root).as_posix()
        except ValueError as exc:
            raise ValueError(f"repair file escapes project root: {path}") from exc
        if not path.is_file():
            raise ValueError(f"repair file missing: {path}")
        changed_files.append({"path": relative, "sha256": sha256_file(path)})
    if not changed_files or not args.verification:
        raise ValueError(
            "record-repair requires changed files and verification evidence"
        )
    current_fingerprint = build_fingerprint(root)
    verification_artifacts: list[dict[str, str]] = []
    for raw in args.verification:
        path = Path(raw).expanduser().resolve()
        if not path.is_file():
            raise ValueError(f"repair verification artifact missing: {path}")
        verification_artifacts.append({"path": str(path), "sha256": sha256_file(path)})
    previous_hash = history[-1]["record_sha256"] if history else ""
    record: dict[str, Any] = {
        "round": len(history) + 1,
        "previous_record_sha256": previous_hash,
        "critic_path": str(critic_path),
        "critic_sha256": sha256_file(critic_path),
        "critic_attestation": str(attestation_path),
        "critic_attestation_sha256": sha256_file(attestation_path),
        "before_fingerprint": run.get("project_fingerprint", {}).get("digest"),
        "after_fingerprint": current_fingerprint["digest"],
        "changed_files": changed_files,
        "verification": verification_artifacts,
        "notes": args.notes or "",
        "recorded_at": utc_now(),
    }
    record["record_sha256"] = hashlib.sha256(
        json.dumps(record, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    history.append(record)
    run["repair_history"] = history
    run["project_fingerprint"] = current_fingerprint
    run["status"] = "running"
    run["review_packet"] = ""
    run["review_packet_sha256"] = ""
    run["critic_attestation"] = ""
    run["capture_receipts"] = []
    run["capture_attestation"] = ""
    run["capture_attestation_sha256"] = ""
    manifest["project_fingerprint_digest"] = current_fingerprint["digest"]
    manifest["items"] = [
        item
        for item in manifest.get("items", [])
        if item.get("provenance", {}).get("trust") == "manual"
    ]
    manifest["coverage"] = {
        "routes": [],
        "states": [],
        "viewports": [],
        "tuples": [],
        "source_scan": False,
        "accessibility": False,
        "critic": False,
    }
    write_json(manifest_path, manifest)
    write_json(run_path, run)
    print(json.dumps(record, ensure_ascii=False, indent=2))
    return 0


def command_plan(args: argparse.Namespace) -> int:
    root = Path(args.root).expanduser().resolve()
    platform, markers = detect_platform(root)
    spec = load_platform_registry()["platforms"].get(platform)
    print(
        json.dumps(
            {"platform": platform, "detected_from": markers, **spec},
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Evidence-backed Design Runtime v3")
    subparsers = parser.add_subparsers(dest="command", required=True)

    init = subparsers.add_parser(
        "init", help="create a design run and empty evidence manifest"
    )
    init.add_argument("--root", default=".")
    init.add_argument("--out")
    init.add_argument("--run-id")
    init.add_argument(
        "--mode",
        required=True,
        choices=(
            "shape",
            "reference",
            "measure",
            "craft",
            "audit",
            "polish",
            "redesign",
            "typeset",
            "colorize",
            "animate",
            "harden",
        ),
    )
    init.add_argument("--surface", required=True)
    init.add_argument("--implementation-actor-id")
    init.add_argument(
        "--critic-public-key",
        help="Ed25519 public key owned by the external critic/orchestrator trust boundary",
    )
    init.add_argument(
        "--register",
        required=True,
        choices=(
            "product",
            "brand",
            "operational",
            "editorial",
            "public-sector",
            "campaign",
            "design-system",
            "asset",
        ),
    )
    init.add_argument(
        "--platform",
        default="auto",
        choices=("auto", "web", "flutter", "native", "document", "unknown"),
    )
    init.add_argument("--design-read", required=True)
    init.add_argument("--audience")
    init.add_argument("--scene")
    init.add_argument("--visual-stance")
    init.add_argument("--anti-reference", action="append", default=[])
    init.add_argument(
        "--dials", required=True, help="DISTINCTION,MOTION,DENSITY,EVIDENCE,SYSTEMNESS"
    )
    init.add_argument("--slop-risk", action="append", required=True)
    init.add_argument("--route", action="append")
    init.add_argument("--state", action="append")
    init.add_argument(
        "--viewport", action="append", default=[], help="name:WIDTHxHEIGHT[@DSF]"
    )
    init.set_defaults(func=command_init)

    add = subparsers.add_parser(
        "add-evidence", help="hash and register an evidence artifact"
    )
    add.add_argument("--manifest", required=True)
    add.add_argument("--id")
    add.add_argument(
        "--kind",
        required=True,
        choices=(
            "baseline-screenshot",
            "result-screenshot",
            "interaction-recording",
            "accessibility-tree",
            "source-scan",
            "test-log",
            "design-token-snapshot",
            "critic-report",
            "evaluation-result",
        ),
    )
    add.add_argument("--path", required=True)
    add.add_argument("--supports", action="append", required=True)
    add.add_argument("--route")
    add.add_argument("--state")
    add.add_argument("--viewport")
    add.add_argument(
        "--platform", choices=("web", "flutter", "native", "document", "unknown")
    )
    add.add_argument("--command")
    add.add_argument(
        "--verdict",
        required=True,
        choices=("pass", "fail", "needs-review", "informational"),
    )
    add.add_argument("--finding-count", action="append")
    add.add_argument("--notes")
    add.set_defaults(func=command_add_evidence)

    import_index = subparsers.add_parser(
        "import-index", help="verify and import a platform capture index"
    )
    import_index.add_argument("--manifest", required=True)
    import_index.add_argument("--index", required=True)
    import_index.add_argument("--command")
    import_index.add_argument(
        "--allow-failed-index",
        action="store_true",
        help="diagnostic only; imported failed artifacts cannot satisfy final gates",
    )
    import_index.set_defaults(func=command_import_index)

    capture = subparsers.add_parser(
        "capture",
        help="run the canonical platform adapter and issue a runtime-owned capture receipt",
    )
    capture.add_argument("--run", required=True)
    capture.add_argument("--evidence")
    capture.add_argument("--spec", required=True)
    capture.add_argument("--out")
    capture.set_defaults(func=command_capture)

    prepare = subparsers.add_parser(
        "prepare-review",
        help="run live source gates and freeze the independent review packet",
    )
    prepare.add_argument("--run", required=True)
    prepare.add_argument("--evidence")
    prepare.add_argument(
        "--capture-attestation",
        help="external authority signature over the canonical capture receipt and evidence projection",
    )
    prepare.add_argument("--output")
    prepare.set_defaults(func=command_prepare_review)

    validate = subparsers.add_parser(
        "validate", help="validate gates and optionally persist status"
    )
    validate.add_argument("--run", required=True)
    validate.add_argument("--evidence")
    validate.add_argument("--critic")
    validate.add_argument("--attestation")
    validate.add_argument("--output")
    validate.add_argument("--write-status", action="store_true")
    validate.add_argument(
        "--allow-project-drift",
        action="store_true",
        help="skip fingerprint drift check for audit-only runs",
    )
    validate.set_defaults(func=command_validate)

    finalize = subparsers.add_parser(
        "finalize", help="run detector + grader and atomically promote a verified run"
    )
    finalize.add_argument("--run", required=True)
    finalize.add_argument("--evidence")
    finalize.add_argument("--critic", required=True)
    finalize.add_argument("--attestation", required=True)
    finalize.add_argument("--output")
    finalize.set_defaults(func=command_finalize)

    critic = subparsers.add_parser(
        "critic-template", help="create a bounded independent critic result template"
    )
    critic.add_argument("--run", required=True)
    critic.add_argument("--evidence")
    critic.add_argument("--critic-id", required=True)
    critic.add_argument("--context-manifest", required=True)
    critic.add_argument("--round", type=int, default=0, choices=(0, 1, 2))
    critic.add_argument("--out", required=True)
    critic.set_defaults(func=command_critic_template)

    repair = subparsers.add_parser(
        "record-repair", help="append one hash-chained bounded repair record"
    )
    repair.add_argument("--run", required=True)
    repair.add_argument("--critic", required=True)
    repair.add_argument("--attestation", required=True)
    repair.add_argument("--changed-file", action="append", required=True)
    repair.add_argument("--verification", action="append", required=True)
    repair.add_argument("--notes")
    repair.set_defaults(func=command_record_repair)

    plan = subparsers.add_parser(
        "plan", help="detect platform and print adapter evidence requirements"
    )
    plan.add_argument("--root", default=".")
    plan.set_defaults(func=command_plan)
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        return args.func(args)
    except (ValueError, OSError, KeyError) as exc:
        print(f"design-runtime: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
