#!/usr/bin/env python3
from __future__ import annotations

import base64
import datetime as dt
import hashlib
import json
import os
import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path
from urllib.parse import urlparse


EVAL_DIR = Path(__file__).resolve().parent
CLAUDE_DIR = EVAL_DIR.parents[1]
HARNESS_ROOT = EVAL_DIR.parents[2]
RUNTIME = CLAUDE_DIR / "skills" / "design-harness" / "scripts" / "design-runtime.py"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_bytes(payload: dict) -> bytes:
    return json.dumps(
        payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode()


def review_manifest_digest(manifest: dict) -> str:
    view = dict(manifest)
    view.pop("generated_at", None)
    view["items"] = [
        item
        for item in manifest.get("items", [])
        if item.get("kind") != "evaluation-result"
    ]
    return hashlib.sha256(canonical_bytes(view)).hexdigest()


def capture_projection_digest(manifest: dict) -> str:
    keys = (
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
    items = [
        {key: item.get(key) for key in keys if key in item}
        for item in manifest.get("items", [])
        if item.get("provenance", {}).get("trust") == "runtime-adapter"
    ]
    items.sort(key=lambda item: (str(item.get("path")), str(item.get("kind"))))
    return hashlib.sha256(
        canonical_bytes({"schema": "design-capture-projection-v1", "items": items})
    ).hexdigest()


def schema_errors(
    value: object,
    schema: dict,
    *,
    root_schema: dict | None = None,
    path: str = "$",
) -> list[str]:
    root_schema = root_schema or schema
    if "$ref" in schema:
        reference = str(schema["$ref"])
        if not reference.startswith("#/"):
            return [f"{path}: unsupported external schema reference {reference}"]
        resolved: object = root_schema
        for part in reference[2:].split("/"):
            resolved = resolved[part]  # type: ignore[index]
        referenced_errors = schema_errors(
            value,
            resolved,  # type: ignore[arg-type]
            root_schema=root_schema,
            path=path,
        )
        siblings = {key: item for key, item in schema.items() if key != "$ref"}
        return referenced_errors + (
            schema_errors(value, siblings, root_schema=root_schema, path=path)
            if siblings
            else []
        )
    errors: list[str] = []

    expected_type = schema.get("type")
    type_map = {
        "object": lambda item: isinstance(item, dict),
        "array": lambda item: isinstance(item, list),
        "string": lambda item: isinstance(item, str),
        "integer": lambda item: isinstance(item, int) and not isinstance(item, bool),
        "number": lambda item: (
            isinstance(item, (int, float)) and not isinstance(item, bool)
        ),
        "boolean": lambda item: isinstance(item, bool),
        "null": lambda item: item is None,
    }
    if isinstance(expected_type, str) and expected_type in type_map:
        if not type_map[expected_type](value):
            return [f"{path}: expected {expected_type}"]
    elif isinstance(expected_type, list):
        if not any(
            type_map.get(name, lambda _: False)(value) for name in expected_type
        ):
            return [f"{path}: expected one of {expected_type}"]

    if "const" in schema and value != schema["const"]:
        errors.append(f"{path}: value differs from const")
    if "enum" in schema and value not in schema["enum"]:
        errors.append(f"{path}: value is outside enum")

    for branch in schema.get("allOf", []):
        errors.extend(schema_errors(value, branch, root_schema=root_schema, path=path))
    if "anyOf" in schema and not any(
        not schema_errors(value, branch, root_schema=root_schema, path=path)
        for branch in schema["anyOf"]
    ):
        errors.append(f"{path}: no anyOf branch matched")
    if "oneOf" in schema:
        matches = sum(
            not schema_errors(value, branch, root_schema=root_schema, path=path)
            for branch in schema["oneOf"]
        )
        if matches != 1:
            errors.append(f"{path}: expected exactly one oneOf match, got {matches}")
    if "not" in schema and not schema_errors(
        value, schema["not"], root_schema=root_schema, path=path
    ):
        errors.append(f"{path}: prohibited not schema matched")
    if "if" in schema:
        condition_matches = not schema_errors(
            value, schema["if"], root_schema=root_schema, path=path
        )
        selected = schema.get("then") if condition_matches else schema.get("else")
        if isinstance(selected, dict):
            errors.extend(
                schema_errors(value, selected, root_schema=root_schema, path=path)
            )

    if isinstance(value, dict):
        required = set(schema.get("required", []))
        missing = sorted(required - set(value))
        if missing:
            errors.append(f"{path}: missing {', '.join(missing)}")
        properties = schema.get("properties", {})
        if schema.get("additionalProperties") is False:
            extra = sorted(set(value) - set(properties))
            if extra:
                errors.append(f"{path}: undeclared {', '.join(extra)}")
        elif isinstance(schema.get("additionalProperties"), dict):
            for key in set(value) - set(properties):
                errors.extend(
                    schema_errors(
                        value[key],
                        schema["additionalProperties"],
                        root_schema=root_schema,
                        path=f"{path}.{key}",
                    )
                )
        for key, child in value.items():
            child_schema = properties.get(key)
            if isinstance(child_schema, dict):
                errors.extend(
                    schema_errors(
                        child,
                        child_schema,
                        root_schema=root_schema,
                        path=f"{path}.{key}",
                    )
                )
    elif isinstance(value, list):
        if len(value) < int(schema.get("minItems", 0)):
            errors.append(f"{path}: fewer than minItems")
        if "maxItems" in schema and len(value) > int(schema["maxItems"]):
            errors.append(f"{path}: more than maxItems")
        if schema.get("uniqueItems"):
            encoded = [
                json.dumps(
                    item, ensure_ascii=False, sort_keys=True, separators=(",", ":")
                )
                for item in value
            ]
            if len(encoded) != len(set(encoded)):
                errors.append(f"{path}: duplicate array items")
        if isinstance(schema.get("items"), dict):
            for index, child in enumerate(value):
                errors.extend(
                    schema_errors(
                        child,
                        schema["items"],
                        root_schema=root_schema,
                        path=f"{path}[{index}]",
                    )
                )
    elif isinstance(value, str):
        if len(value) < int(schema.get("minLength", 0)):
            errors.append(f"{path}: shorter than minLength")
        if "maxLength" in schema and len(value) > int(schema["maxLength"]):
            errors.append(f"{path}: longer than maxLength")
        if "pattern" in schema and re.search(str(schema["pattern"]), value) is None:
            errors.append(f"{path}: pattern mismatch")
        if schema.get("format") == "date-time":
            try:
                parsed_datetime = dt.datetime.fromisoformat(
                    value.replace("Z", "+00:00")
                )
            except ValueError:
                errors.append(f"{path}: invalid date-time")
            else:
                if "T" not in value or parsed_datetime.tzinfo is None:
                    errors.append(f"{path}: date-time must include time and timezone")
        elif schema.get("format") == "uri":
            parsed = urlparse(value)
            if not parsed.scheme:
                errors.append(f"{path}: invalid URI")
    elif isinstance(value, (int, float)) and not isinstance(value, bool):
        if "minimum" in schema and value < schema["minimum"]:
            errors.append(f"{path}: below minimum")
        if "maximum" in schema and value > schema["maximum"]:
            errors.append(f"{path}: above maximum")
        if "exclusiveMinimum" in schema and value <= schema["exclusiveMinimum"]:
            errors.append(f"{path}: below exclusiveMinimum")
        if "exclusiveMaximum" in schema and value >= schema["exclusiveMaximum"]:
            errors.append(f"{path}: above exclusiveMaximum")
    return errors


MOCK_PLAYWRIGHT = r"""
const fs = require('fs');
const zlib = require('zlib');
function crc32(buffer) {
  let crc = 0xffffffff;
  for (const byte of buffer) {
    crc ^= byte;
    for (let i = 0; i < 8; i += 1) crc = (crc >>> 1) ^ (0xedb88320 & -(crc & 1));
  }
  return (crc ^ 0xffffffff) >>> 0;
}
function chunk(type, payload) {
  const name = Buffer.from(type); const size = Buffer.alloc(4); size.writeUInt32BE(payload.length);
  const crc = Buffer.alloc(4); crc.writeUInt32BE(crc32(Buffer.concat([name, payload])));
  return Buffer.concat([size, name, payload, crc]);
}
function png(fill) {
  const width = 390, height = 844; const ihdr = Buffer.alloc(13);
  ihdr.writeUInt32BE(width, 0); ihdr.writeUInt32BE(height, 4); ihdr[8] = 8; ihdr[9] = 6;
  const rows = []; for (let y = 0; y < height; y += 1) rows.push(Buffer.concat([Buffer.from([0]), Buffer.alloc(width * 4, fill)]));
  return Buffer.concat([Buffer.from([137,80,78,71,13,10,26,10]), chunk('IHDR', ihdr), chunk('IDAT', zlib.deflateSync(Buffer.concat(rows))), chunk('IEND', Buffer.alloc(0))]);
}
let screenshotCount = 0;
function page() {
  return { on(){}, async goto(){}, locator(){ return { async waitFor(){}, async click(){}, async fill(){}, async press(){}, async isVisible(){ return true; }, async textContent(){ return 'Error state'; }, async ariaSnapshot(){ return '- main\n  - heading Review queue\n  - table'; } }; }, async screenshot({path}){ screenshotCount += 1; fs.writeFileSync(path, png(31 + screenshotCount)); } };
}
exports.chromium = { async launch(){ return { async newContext(){ return { async newPage(){ return page(); }, async close(){} }; }, async close(){} }; } };
"""


class DesignRuntimeTest(unittest.TestCase):
    def run_runtime(
        self, *arguments: str, expected: int = 0
    ) -> subprocess.CompletedProcess[str]:
        process = subprocess.run(
            [
                "python3",
                str(getattr(self, "runtime_executable", RUNTIME)),
                *arguments,
            ],
            check=False,
            capture_output=True,
            text=True,
            env=os.environ.copy(),
        )
        self.assertEqual(process.returncode, expected, process.stderr or process.stdout)
        return process

    def make_keys(self, root: Path) -> tuple[Path, Path]:
        private = root / "critic-private.pem"
        public = root / "critic-public.pem"
        subprocess.run(
            ["openssl", "genpkey", "-algorithm", "ED25519", "-out", str(private)],
            check=True,
            capture_output=True,
        )
        subprocess.run(
            ["openssl", "pkey", "-in", str(private), "-pubout", "-out", str(public)],
            check=True,
            capture_output=True,
        )
        runtime_root = root / "trusted-runtime" / ".claude"
        shutil.copytree(
            CLAUDE_DIR / "skills" / "design-harness",
            runtime_root / "skills" / "design-harness",
        )
        shutil.copytree(
            CLAUDE_DIR / "registry",
            runtime_root / "registry",
        )
        shutil.copytree(
            CLAUDE_DIR / "evals" / "ui-design",
            runtime_root / "evals" / "ui-design",
        )
        trust_store = runtime_root / "registry" / "design" / "trusted-authorities.json"
        trust_store.write_text(
            json.dumps(
                {
                    "$schema": "critic-trust-store.schema.json",
                    "schema": "design-critic-trust-store-v1",
                    "authorities": [
                        {
                            "id": "test-external-orchestrator",
                            "status": "active",
                            "purposes": ["capture", "critic"],
                            "public_key_sha256": sha256(public),
                        }
                    ],
                }
            )
            + "\n",
            encoding="utf-8",
        )
        self.runtime_executable = (
            runtime_root / "skills" / "design-harness" / "scripts" / "design-runtime.py"
        )
        self.external_private_key = private
        return private, public

    def init_web_run(
        self,
        project: Path,
        output: Path,
        public_key: Path,
        *,
        run_id: str = "web-runtime-test",
        states: tuple[str, ...] = ("default",),
    ) -> None:
        (project / "src").mkdir(parents=True)
        (project / "node_modules" / "playwright").mkdir(parents=True)
        (project / "node_modules" / "playwright" / "index.js").write_text(
            MOCK_PLAYWRIGHT, encoding="utf-8"
        )
        (project / "package.json").write_text(
            '{"dependencies":{"next":"16.2.10","react":"19.2.7","playwright":"1.61.1"}}\n',
            encoding="utf-8",
        )
        (project / "src" / "page.tsx").write_text(
            "export function ReviewQueue(){return <main><h1>Review queue</h1><table><tbody /></table></main>}\n",
            encoding="utf-8",
        )
        arguments = [
            "init",
            "--root",
            str(project),
            "--out",
            str(output),
            "--run-id",
            run_id,
            "--implementation-actor-id",
            "implementer:test",
            "--critic-public-key",
            str(public_key),
            "--mode",
            "craft",
            "--surface",
            "review-queue",
            "--register",
            "operational",
            "--design-read",
            "Reading this as an operator review queue with dense evidence and no decorative card rows.",
            "--dials",
            "3,1,9,9,9",
            "--slop-risk",
            "decorative card rows",
            "--route",
            "/reviews",
            "--viewport",
            "mobile:390x844",
        ]
        for state in states:
            arguments += ["--state", state]
        self.run_runtime(*arguments)

    def write_capture_spec(
        self, output: Path, states: tuple[str, ...] = ("default",)
    ) -> Path:
        spec = output / "capture-spec.json"
        cases = [
            {
                "id": f"review-{state}-mobile",
                "path": "/reviews",
                "state": state,
                "viewport": {
                    "name": "mobile",
                    "width": 390,
                    "height": 844,
                    "device_scale_factor": 1,
                },
                "wait_for_selector": "main",
                "actions": [],
                "supports": ["visual-qa", "state-coverage"],
                "capture_aria": True,
                **(
                    {"assertions": [{"type": "visible", "selector": "#error-state"}]}
                    if state != "default"
                    else {}
                ),
            }
            for state in states
        ]
        spec.write_text(
            json.dumps(
                {
                    "schema": "design-web-capture-v1",
                    "base_url": "http://127.0.0.1:3000",
                    "cases": cases,
                }
            )
            + "\n",
            encoding="utf-8",
        )
        return spec

    def capture_and_prepare(
        self, output: Path, states: tuple[str, ...] = ("default",)
    ) -> None:
        spec = self.write_capture_spec(output, states)
        self.run_runtime(
            "capture", "--run", str(output / "design-run.json"), "--spec", str(spec)
        )
        attestation = self.create_capture_attestation(output, self.external_private_key)
        self.run_runtime(
            "prepare-review",
            "--run",
            str(output / "design-run.json"),
            "--capture-attestation",
            str(attestation),
        )

    def create_capture_attestation(self, output: Path, private_key: Path) -> Path:
        run = json.loads((output / "design-run.json").read_text(encoding="utf-8"))
        manifest = json.loads(
            (output / "evidence-manifest.json").read_text(encoding="utf-8")
        )
        receipt = run["capture_receipts"][0]
        payload = {
            "schema": "design-capture-attestation-payload-v1",
            "run_id": run["run_id"],
            "issuer": "test-orchestrator",
            "execution_id": "capture-task-1",
            "authority_id": run["trust_policy"]["authority_id"],
            "receipt_sha256": receipt["receipt_sha256"],
            "adapter_sha256": receipt["adapter_sha256"],
            "spec_sha256": receipt["spec_sha256"],
            "index_sha256": receipt["index_sha256"],
            "source_fingerprint_digest": receipt["source_fingerprint_digest"],
            "evidence_projection_sha256": capture_projection_digest(manifest),
            "issued_at": "2026-07-13T00:00:00Z",
        }
        canonical = output / "capture-attestation-payload.json"
        signature = output / "capture-attestation.sig"
        canonical.write_bytes(canonical_bytes(payload))
        subprocess.run(
            [
                "openssl",
                "pkeyutl",
                "-sign",
                "-inkey",
                str(private_key),
                "-rawin",
                "-in",
                str(canonical),
                "-out",
                str(signature),
            ],
            check=True,
            capture_output=True,
        )
        attestation = output / "capture-attestation.json"
        attestation.write_text(
            json.dumps(
                {
                    "schema": "design-capture-attestation-v1",
                    "payload": payload,
                    "signature": base64.b64encode(signature.read_bytes()).decode(),
                },
                ensure_ascii=False,
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        return attestation

    def write_critic_context(
        self, output: Path, name: str = "critic-context.json"
    ) -> Path:
        selected_artifact = output / "review-packet.json"
        provider = subprocess.run(
            [
                "python3",
                str(HARNESS_ROOT / "scripts" / "harness-provider.py"),
                "--provider",
                "claude",
                "--quality-tier",
                "independent_critic",
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        binding = json.loads(provider.stdout)
        context = output / name
        context.write_text(
            json.dumps(
                {
                    "schema_version": "harness.context-manifest.v1",
                    "generated_at": "2026-07-13T00:00:00Z",
                    "repository": str(output),
                    "profile": "critic",
                    "profile_path": ".claude/registry/projects/critic.json",
                    "provider_binding": binding,
                    "capabilities": ["design-harness"],
                    "inventory_hash": hashlib.sha256(b"test-inventory").hexdigest(),
                    "budget_bytes": 1_000_000,
                    "total_bytes": selected_artifact.stat().st_size,
                    "selected": [
                        {
                            "path": selected_artifact.relative_to(output).as_posix(),
                            "capability": "design-harness",
                            "bytes": selected_artifact.stat().st_size,
                            "sha256": sha256(selected_artifact),
                            "required": True,
                        }
                    ],
                    "skipped": [],
                },
                ensure_ascii=False,
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        return context

    def create_critic_and_attestation(
        self, output: Path, private_key: Path
    ) -> tuple[Path, Path]:
        run_path = output / "design-run.json"
        manifest_path = output / "evidence-manifest.json"
        run = json.loads(run_path.read_text())
        context = self.write_critic_context(output)
        critic = output / "critic-result.json"
        self.run_runtime(
            "critic-template",
            "--run",
            str(run_path),
            "--critic-id",
            "critic:external-task-1",
            "--context-manifest",
            str(context),
            "--out",
            str(critic),
        )
        payload = json.loads(critic.read_text())
        axes = (
            "task_efficiency",
            "density_readability",
            "state_completeness",
            "craft",
            "accessibility",
            "evidence_truth",
        )
        payload["decision"] = "pass"
        payload["summary"] = (
            "A separate attested reviewer checked every captured state, source gate, and accessibility artifact."
        )
        payload["rubric_scores"] = {
            axis: {
                "score": 8,
                "evidence": payload["evidence_ids"],
                "rationale": "The frozen review packet provides direct evidence for this rubric axis.",
            }
            for axis in axes
        }
        critic.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        manifest = json.loads(manifest_path.read_text())
        attestation_payload = {
            "schema": "design-critic-attestation-payload-v1",
            "run_id": run["run_id"],
            "issuer": "test-orchestrator",
            "execution_id": "external-task-1",
            "critic_actor_id": payload["critic_id"],
            "implementation_actor_id": run["implementation_actor_id"],
            "review_packet_sha256": run["review_packet_sha256"],
            "critic_sha256": sha256(critic),
            "evidence_manifest_sha256": review_manifest_digest(manifest),
            "source_fingerprint_digest": run["project_fingerprint"]["digest"],
            "issued_at": "2026-07-13T00:00:00Z",
        }
        canonical = output / "attestation-payload.json"
        signature = output / "attestation.sig"
        canonical.write_bytes(canonical_bytes(attestation_payload))
        subprocess.run(
            [
                "openssl",
                "pkeyutl",
                "-sign",
                "-inkey",
                str(private_key),
                "-rawin",
                "-in",
                str(canonical),
                "-out",
                str(signature),
            ],
            check=True,
            capture_output=True,
        )
        attestation = output / "critic-attestation.json"
        attestation.write_text(
            json.dumps(
                {
                    "schema": "design-critic-attestation-v1",
                    "payload": attestation_payload,
                    "signature": base64.b64encode(signature.read_bytes()).decode(),
                },
                ensure_ascii=False,
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        return critic, attestation

    def test_attested_direct_capture_stops_at_external_promotion_boundary(self) -> None:
        with tempfile.TemporaryDirectory(
            prefix="design-runtime-finalize-"
        ) as temporary:
            root = Path(temporary)
            project = root / "project"
            output = root / "run"
            project.mkdir()
            private, public = self.make_keys(root)
            self.init_web_run(project, output, public)
            self.capture_and_prepare(output)
            critic, attestation = self.create_critic_and_attestation(output, private)
            finalized = self.run_runtime(
                "finalize",
                "--run",
                str(output / "design-run.json"),
                "--critic",
                str(critic),
                "--attestation",
                str(attestation),
            )
            self.assertEqual(
                json.loads(finalized.stdout)["status"], "ready_for_external_promotion"
            )
            schema_pairs = (
                (
                    output / "design-run.json",
                    CLAUDE_DIR / "registry/design/design-run.schema.json",
                ),
                (
                    output / "evidence-manifest.json",
                    CLAUDE_DIR / "registry/design/evidence-manifest.schema.json",
                ),
                (
                    output / "review-packet.json",
                    CLAUDE_DIR / "registry/design/review-packet.schema.json",
                ),
                (
                    output / "capture-attestation.json",
                    CLAUDE_DIR / "registry/design/capture-attestation.schema.json",
                ),
            )
            for artifact_path, schema_path in schema_pairs:
                artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
                schema = json.loads(schema_path.read_text(encoding="utf-8"))
                self.assertEqual(
                    schema_errors(artifact, schema),
                    [],
                    f"{artifact_path.name} differs from {schema_path.name}",
                )
            run_schema = json.loads(
                (CLAUDE_DIR / "registry/design/design-run.schema.json").read_text(
                    encoding="utf-8"
                )
            )
            invalid_run = json.loads((output / "design-run.json").read_text())
            invalid_run["schema"] = "forged-design-run"
            invalid_run["dials"]["motion"] = 11
            constraint_errors = schema_errors(invalid_run, run_schema)
            self.assertTrue(
                any("const" in error for error in constraint_errors), constraint_errors
            )
            self.assertTrue(
                any("above maximum" in error for error in constraint_errors),
                constraint_errors,
            )
            revalidated = self.run_runtime(
                "validate", "--run", str(output / "design-run.json")
            )
            self.assertEqual(
                json.loads(revalidated.stdout)["status"], "ready_for_external_promotion"
            )
            run_path = output / "design-run.json"
            forged = json.loads(run_path.read_text())
            forged["status"] = "passed"
            run_path.write_text(json.dumps(forged) + "\n")
            rejected = self.run_runtime("validate", "--run", str(run_path), expected=2)
            self.assertIn("may not assert passed", rejected.stdout)

    def test_handmade_capture_index_is_diagnostic_only(self) -> None:
        with tempfile.TemporaryDirectory(
            prefix="design-runtime-manual-index-"
        ) as temporary:
            root = Path(temporary)
            project = root / "project"
            output = root / "run"
            project.mkdir()
            _, public = self.make_keys(root)
            self.init_web_run(project, output, public)
            spec = self.write_capture_spec(output)
            artifact_dir = output / "manual"
            artifact_dir.mkdir()
            screenshot = artifact_dir / "fake.png"
            screenshot.write_bytes(b"not a png")
            index = artifact_dir / "capture-index.json"
            index.write_text(
                json.dumps(
                    {
                        "schema": "design-capture-index-v1",
                        "producer": "capture-web-evidence@1",
                        "generated_at": "2026-07-13T00:00:00Z",
                        "platform": "web",
                        "project_root": str(project),
                        "spec": str(spec),
                        "spec_sha256": sha256(spec),
                        "status": "passed",
                        "results": [
                            {
                                "id": "manual",
                                "status": "passed",
                                "artifacts": [
                                    {
                                        "kind": "test-log",
                                        "path": str(screenshot),
                                        "sha256": sha256(screenshot),
                                        "platform": "web",
                                        "supports": ["diagnostic"],
                                    }
                                ],
                            }
                        ],
                    }
                )
                + "\n",
                encoding="utf-8",
            )
            self.run_runtime(
                "import-index",
                "--manifest",
                str(output / "evidence-manifest.json"),
                "--index",
                str(index),
            )
            prepared = self.run_runtime(
                "prepare-review", "--run", str(output / "design-run.json"), expected=2
            )
            self.assertIn("runtime-owned capture receipt missing", prepared.stderr)

    def test_source_drift_after_capture_fails(self) -> None:
        with tempfile.TemporaryDirectory(prefix="design-runtime-drift-") as temporary:
            root = Path(temporary)
            project = root / "project"
            output = root / "run"
            project.mkdir()
            _, public = self.make_keys(root)
            self.init_web_run(project, output, public)
            spec = self.write_capture_spec(output)
            self.run_runtime(
                "capture", "--run", str(output / "design-run.json"), "--spec", str(spec)
            )
            capture_attestation = self.create_capture_attestation(
                output, self.external_private_key
            )
            (project / "src" / "live-page.mdx").write_text(
                '# Changed after capture\n\n<div className="rounded-3xl">drift</div>\n'
            )
            prepared = self.run_runtime(
                "prepare-review",
                "--run",
                str(output / "design-run.json"),
                "--capture-attestation",
                str(capture_attestation),
                expected=2,
            )
            self.assertIn(
                "project fingerprint candidate set or digest changed", prepared.stderr
            )

    def test_visual_noise_cannot_fake_a_distinct_semantic_state(self) -> None:
        with tempfile.TemporaryDirectory(
            prefix="design-runtime-projection-"
        ) as temporary:
            root = Path(temporary)
            project = root / "project"
            output = root / "run"
            project.mkdir()
            _, public = self.make_keys(root)
            states = ("default", "error")
            self.init_web_run(project, output, public, states=states)
            spec = self.write_capture_spec(output, states)
            captured = self.run_runtime(
                "capture",
                "--run",
                str(output / "design-run.json"),
                "--spec",
                str(spec),
                expected=2,
            )
            self.assertIn("identical accessibility semantics", captured.stderr)

    def test_init_supplied_critic_key_is_not_a_trust_root(self) -> None:
        with tempfile.TemporaryDirectory(
            prefix="design-runtime-untrusted-key-"
        ) as temporary:
            root = Path(temporary)
            project = root / "project"
            project.mkdir()
            (project / "package.json").write_text(
                '{"dependencies":{"next":"16.2.10"}}\n'
            )
            self.make_keys(root)
            rogue_private = root / "rogue-private.pem"
            public = root / "rogue-public.pem"
            subprocess.run(
                [
                    "openssl",
                    "genpkey",
                    "-algorithm",
                    "ED25519",
                    "-out",
                    str(rogue_private),
                ],
                check=True,
                capture_output=True,
            )
            subprocess.run(
                [
                    "openssl",
                    "pkey",
                    "-in",
                    str(rogue_private),
                    "-pubout",
                    "-out",
                    str(public),
                ],
                check=True,
                capture_output=True,
            )
            rejected = self.run_runtime(
                "init",
                "--root",
                str(project),
                "--out",
                str(root / "run"),
                "--mode",
                "craft",
                "--surface",
                "queue",
                "--register",
                "operational",
                "--critic-public-key",
                str(public),
                "--design-read",
                "Reading this as a high-trust operational queue with dense evidence.",
                "--dials",
                "3,1,9,9,9",
                "--slop-risk",
                "decorative cards",
                expected=2,
            )
            self.assertIn("is not a trust root", rejected.stderr)

    def test_caller_selected_trust_store_environment_is_ignored(self) -> None:
        with tempfile.TemporaryDirectory(
            prefix="design-runtime-caller-trust-store-"
        ) as temporary:
            root = Path(temporary)
            project = root / "project"
            project.mkdir()
            (project / "package.json").write_text(
                '{"dependencies":{"next":"16.2.10"}}\n', encoding="utf-8"
            )
            private = root / "self-private.pem"
            public = root / "self-public.pem"
            subprocess.run(
                ["openssl", "genpkey", "-algorithm", "ED25519", "-out", str(private)],
                check=True,
                capture_output=True,
            )
            subprocess.run(
                [
                    "openssl",
                    "pkey",
                    "-in",
                    str(private),
                    "-pubout",
                    "-out",
                    str(public),
                ],
                check=True,
                capture_output=True,
            )
            caller_store = root / "caller-selected-store.json"
            caller_store.write_text(
                json.dumps(
                    {
                        "schema": "design-critic-trust-store-v1",
                        "authorities": [
                            {
                                "id": "self-authority",
                                "status": "active",
                                "purposes": ["capture", "critic"],
                                "public_key_sha256": sha256(public),
                            }
                        ],
                    }
                )
                + "\n",
                encoding="utf-8",
            )
            environment = os.environ.copy()
            environment["CLAUDE_CRAFT_DESIGN_TRUST_STORE"] = str(caller_store)
            rejected = subprocess.run(
                [
                    "python3",
                    str(RUNTIME),
                    "init",
                    "--root",
                    str(project),
                    "--out",
                    str(root / "run"),
                    "--mode",
                    "craft",
                    "--surface",
                    "queue",
                    "--register",
                    "operational",
                    "--critic-public-key",
                    str(public),
                    "--design-read",
                    "Reading this as a high-trust operational queue with dense evidence.",
                    "--dials",
                    "3,1,9,9,9",
                    "--slop-risk",
                    "decorative cards",
                ],
                check=False,
                capture_output=True,
                text=True,
                env=environment,
            )
            self.assertEqual(rejected.returncode, 2, rejected.stderr or rejected.stdout)
            self.assertIn("caller-selected store is not a trust root", rejected.stderr)

    def test_capture_receipt_must_rebind_to_the_canonical_adapter(self) -> None:
        with tempfile.TemporaryDirectory(
            prefix="design-runtime-receipt-binding-"
        ) as temporary:
            root = Path(temporary)
            project = root / "project"
            output = root / "run"
            project.mkdir()
            _, public = self.make_keys(root)
            self.init_web_run(project, output, public)
            spec = self.write_capture_spec(output)
            self.run_runtime(
                "capture", "--run", str(output / "design-run.json"), "--spec", str(spec)
            )
            run_path = output / "design-run.json"
            run = json.loads(run_path.read_text())
            receipt = run["capture_receipts"][0]
            forged_adapter = Path(receipt["index"]).parent / "forged-adapter.mjs"
            forged_adapter.write_text("// self-authored adapter alias\n")
            receipt["adapter"] = str(forged_adapter)
            receipt["adapter_sha256"] = sha256(forged_adapter)
            unsigned = {
                key: value for key, value in receipt.items() if key != "receipt_sha256"
            }
            receipt["receipt_sha256"] = hashlib.sha256(
                canonical_bytes(unsigned)
            ).hexdigest()
            run_path.write_text(json.dumps(run) + "\n")
            rejected = self.run_runtime(
                "prepare-review", "--run", str(run_path), expected=2
            )
            self.assertIn("not the canonical runtime adapter", rejected.stderr)

    def test_rehashed_capture_projection_cannot_reuse_external_attestation(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory(
            prefix="design-runtime-signed-capture-drift-"
        ) as temporary:
            root = Path(temporary)
            project = root / "project"
            output = root / "run"
            project.mkdir()
            _, public = self.make_keys(root)
            self.init_web_run(project, output, public)
            spec = self.write_capture_spec(output)
            self.run_runtime(
                "capture", "--run", str(output / "design-run.json"), "--spec", str(spec)
            )
            attestation = self.create_capture_attestation(
                output, self.external_private_key
            )
            run_path = output / "design-run.json"
            run = json.loads(run_path.read_text(encoding="utf-8"))
            receipt = run["capture_receipts"][0]
            index_path = Path(receipt["index"])
            index = json.loads(index_path.read_text(encoding="utf-8"))
            index["generated_at"] = "2026-07-13T00:01:00Z"
            index_path.write_text(json.dumps(index) + "\n", encoding="utf-8")
            receipt["index_sha256"] = sha256(index_path)
            unsigned = {
                key: value for key, value in receipt.items() if key != "receipt_sha256"
            }
            receipt["receipt_sha256"] = hashlib.sha256(
                canonical_bytes(unsigned)
            ).hexdigest()
            run_path.write_text(json.dumps(run) + "\n", encoding="utf-8")
            rejected = self.run_runtime(
                "prepare-review",
                "--run",
                str(run_path),
                "--capture-attestation",
                str(attestation),
                expected=2,
            )
            self.assertIn(
                "capture attestation payload is not exactly bound", rejected.stderr
            )

    def test_non_default_state_requires_a_typed_assertion(self) -> None:
        with tempfile.TemporaryDirectory(
            prefix="design-runtime-state-assertion-"
        ) as temporary:
            root = Path(temporary)
            project = root / "project"
            output = root / "run"
            project.mkdir()
            _, public = self.make_keys(root)
            states = ("default", "error")
            self.init_web_run(project, output, public, states=states)
            spec = self.write_capture_spec(output, states)
            payload = json.loads(spec.read_text())
            payload["cases"][1].pop("assertions")
            spec.write_text(json.dumps(payload) + "\n")
            rejected = self.run_runtime(
                "capture",
                "--run",
                str(output / "design-run.json"),
                "--spec",
                str(spec),
                expected=2,
            )
            self.assertIn("requires typed state assertions", rejected.stderr)

    def test_browser_normalized_backslash_path_cannot_escape_loopback(self) -> None:
        with tempfile.TemporaryDirectory(
            prefix="design-runtime-same-origin-path-"
        ) as temporary:
            root = Path(temporary)
            project = root / "project"
            output = root / "run"
            project.mkdir()
            _, public = self.make_keys(root)
            self.init_web_run(project, output, public)
            spec = self.write_capture_spec(output)
            payload = json.loads(spec.read_text(encoding="utf-8"))
            payload["cases"][0]["path"] = "/\\evil.example/x"
            spec.write_text(json.dumps(payload) + "\n", encoding="utf-8")
            rejected = self.run_runtime(
                "capture",
                "--run",
                str(output / "design-run.json"),
                "--spec",
                str(spec),
                expected=2,
            )
            self.assertIn("same-origin relative paths", rejected.stderr)
            adapter = (
                CLAUDE_DIR
                / "skills"
                / "design-harness"
                / "scripts"
                / "capture-web-evidence.mjs"
            )
            adapter_rejected = subprocess.run(
                [
                    "node",
                    str(adapter),
                    "--root",
                    str(project),
                    "--spec",
                    str(spec),
                    "--out",
                    str(root / "adapter-out"),
                    "--validate-only",
                ],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(adapter_rejected.returncode, 2)
            self.assertIn("same-origin relative path", adapter_rejected.stderr)

    def test_redesign_result_only_capture_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory(
            prefix="design-runtime-redesign-baseline-"
        ) as temporary:
            root = Path(temporary)
            project = root / "project"
            output = root / "run"
            project.mkdir()
            _, public = self.make_keys(root)
            self.init_web_run(project, output, public)
            run_path = output / "design-run.json"
            run = json.loads(run_path.read_text())
            run["mode"] = "redesign"
            run_path.write_text(json.dumps(run) + "\n")
            spec = self.write_capture_spec(output)
            rejected = self.run_runtime(
                "capture", "--run", str(run_path), "--spec", str(spec), expected=2
            )
            self.assertIn("baseline and result", rejected.stderr)

    def test_self_authored_critic_alias_and_scores_cannot_pass(self) -> None:
        with tempfile.TemporaryDirectory(
            prefix="design-runtime-self-critic-"
        ) as temporary:
            root = Path(temporary)
            project = root / "project"
            output = root / "run"
            project.mkdir()
            _, public = self.make_keys(root)
            self.init_web_run(project, output, public)
            self.capture_and_prepare(output)
            incomplete_context = output / "incomplete-context.json"
            incomplete_context.write_text(
                '{"schema_version":"harness.context-manifest.v1"}\n'
            )
            critic = output / "self-critic.json"
            rejected_context = self.run_runtime(
                "critic-template",
                "--run",
                str(output / "design-run.json"),
                "--critic-id",
                "critic:self-alias",
                "--context-manifest",
                str(incomplete_context),
                "--out",
                str(critic),
                expected=2,
            )
            self.assertIn(
                "critic context manifest missing fields", rejected_context.stderr
            )
            forged_context = self.write_critic_context(output, "forged-context.json")
            forged_payload = json.loads(forged_context.read_text(encoding="utf-8"))
            forged_binding = forged_payload["provider_binding"]
            forged_binding["execution_profile"] = {
                "kind": "cli-args",
                "args": ["--effort", "low"],
            }
            unsigned = {
                key: value
                for key, value in forged_binding.items()
                if key != "binding_hash"
            }
            forged_binding["binding_hash"] = hashlib.sha256(
                canonical_bytes(unsigned)
            ).hexdigest()
            forged_context.write_text(
                json.dumps(forged_payload) + "\n", encoding="utf-8"
            )
            rejected_binding = self.run_runtime(
                "critic-template",
                "--run",
                str(output / "design-run.json"),
                "--critic-id",
                "critic:forged-profile",
                "--context-manifest",
                str(forged_context),
                "--out",
                str(critic),
                expected=2,
            )
            self.assertIn(
                "differs from the canonical provider registry", rejected_binding.stderr
            )
            context = self.write_critic_context(output, "self-context.json")
            self.run_runtime(
                "critic-template",
                "--run",
                str(output / "design-run.json"),
                "--critic-id",
                "critic:self-alias",
                "--context-manifest",
                str(context),
                "--out",
                str(critic),
            )
            critic_payload = json.loads(critic.read_text())
            critic_payload["decision"] = "pass"
            critic_payload["rubric_scores"] = {
                "task_efficiency": {
                    "score": 10,
                    "evidence": critic_payload["evidence_ids"],
                    "rationale": "Self-authored score must not be enough to pass the independent boundary.",
                }
            }
            critic.write_text(json.dumps(critic_payload) + "\n")
            fake = output / "fake-attestation.json"
            fake.write_text(
                json.dumps(
                    {
                        "schema": "design-critic-attestation-v1",
                        "payload": {},
                        "signature": "ZmFrZQ==",
                    }
                )
                + "\n"
            )
            result = self.run_runtime(
                "finalize",
                "--run",
                str(output / "design-run.json"),
                "--critic",
                str(critic),
                "--attestation",
                str(fake),
                expected=2,
            )
            self.assertIn("attestation", result.stderr)
            legacy_scores = self.run_runtime(
                "finalize",
                "--run",
                str(output / "design-run.json"),
                "--critic",
                str(critic),
                "--attestation",
                str(fake),
                "--scores",
                str(fake),
                expected=2,
            )
            self.assertIn("unrecognized arguments: --scores", legacy_scores.stderr)

    def test_forged_repair_and_empty_coverage_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory(prefix="design-runtime-forged-") as temporary:
            root = Path(temporary)
            project = root / "project"
            output = root / "run"
            project.mkdir()
            _, public = self.make_keys(root)
            self.init_web_run(project, output, public)
            run_path = output / "design-run.json"
            run = json.loads(run_path.read_text())
            record = {
                "round": 1,
                "previous_record_sha256": "",
                "critic_path": str(output / "missing-critic.json"),
                "critic_sha256": "0" * 64,
                "before_fingerprint": "0" * 64,
                "after_fingerprint": "1" * 64,
                "changed_files": [{"path": "src/page.tsx", "sha256": "2" * 64}],
                "verification": [
                    {"path": str(output / "missing.log"), "sha256": "3" * 64}
                ],
            }
            record["record_sha256"] = hashlib.sha256(
                json.dumps(record, sort_keys=True, separators=(",", ":")).encode()
            ).hexdigest()
            run["repair_history"] = [record]
            run["routes"] = []
            run["states"] = []
            run["viewports"] = []
            run_path.write_text(json.dumps(run) + "\n")
            validation = self.run_runtime(
                "validate", "--run", str(run_path), expected=2
            )
            self.assertIn("routes must be a non-empty array", validation.stdout)
            self.assertIn("critic is missing or hash-drifted", validation.stdout)

    def test_missing_detector_target_and_required_grader_inputs_fail(self) -> None:
        missing = subprocess.run(
            [
                "node",
                str(
                    CLAUDE_DIR / "skills/design-harness/scripts/detect-design-slop.mjs"
                ),
                "--format",
                "json",
                "--fail-on",
                "none",
                str(HARNESS_ROOT / ".definitely-missing-design-target"),
            ],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(missing.returncode, 2)
        self.assertIn("target does not exist", missing.stdout)
        grader = subprocess.run(
            ["python3", str(EVAL_DIR / "grader.py"), "grade"],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(grader.returncode, 2)
        self.assertIn("--detector", grader.stderr)

    def test_flutter_capture_rejects_source_paths_without_deleting_them(self) -> None:
        with tempfile.TemporaryDirectory(prefix="flutter-capture-path-") as temporary:
            root = Path(temporary)
            project = root / "project"
            project.mkdir()
            (project / "pubspec.yaml").write_text("name: fixture\n", encoding="utf-8")
            (project / "lib").mkdir()
            source = project / "lib" / "main.dart"
            source.write_text("void main() {}\n", encoding="utf-8")
            spec = root / "capture.json"
            spec.write_text(
                json.dumps(
                    {
                        "schema": "design-flutter-capture-v1",
                        "test_targets": ["test/widget_test.dart"],
                        "generated_artifact_root": "build/design-evidence",
                        "artifacts": [
                            {
                                "id": "forged-source",
                                "kind": "result-screenshot",
                                "path": "lib/main.dart",
                                "screen": "home",
                                "state": "default",
                                "viewport": "phone",
                                "supports": ["visual-qa"],
                            }
                        ],
                    }
                )
                + "\n",
                encoding="utf-8",
            )
            adapter = (
                CLAUDE_DIR / "skills/design-harness/scripts/capture-flutter-evidence.py"
            )
            result = subprocess.run(
                [
                    "python3",
                    str(adapter),
                    "--root",
                    str(project),
                    "--spec",
                    str(spec),
                    "--out",
                    str(root / "out"),
                    "--run-id",
                    "fixture",
                    "--nonce",
                    "a" * 48,
                    "--source-fingerprint",
                    "b" * 64,
                ],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 2)
            self.assertIn("must stay under generated_artifact_root", result.stdout)
            self.assertEqual(source.read_text(encoding="utf-8"), "void main() {}\n")


if __name__ == "__main__":
    unittest.main()
