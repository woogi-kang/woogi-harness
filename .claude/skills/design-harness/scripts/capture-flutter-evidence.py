#!/usr/bin/env python3
"""Run Flutter verification and index declared golden/integration evidence."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Any


def load_object(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"expected JSON object: {path}")
    return payload


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_spec(spec: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if spec.get("schema") != "design-flutter-capture-v1":
        errors.append("schema must be design-flutter-capture-v1")
    targets = spec.get("test_targets", [])
    if not isinstance(targets, list) or any(
        not isinstance(value, str) or not value for value in targets
    ):
        errors.append("test_targets must be a list of paths")
    generated_root = spec.get("generated_artifact_root")
    if not isinstance(generated_root, str) or not generated_root:
        errors.append(
            "generated_artifact_root must be a non-empty project-relative path"
        )
    artifacts = spec.get("artifacts", [])
    if not isinstance(artifacts, list) or not artifacts:
        errors.append("artifacts must be a non-empty array")
    seen: set[str] = set()
    for index, artifact in enumerate(artifacts if isinstance(artifacts, list) else []):
        where = f"artifacts[{index}]"
        if not isinstance(artifact, dict):
            errors.append(f"{where} must be an object")
            continue
        artifact_id = artifact.get("id")
        if not isinstance(artifact_id, str) or not artifact_id:
            errors.append(f"{where}.id is required")
        elif artifact_id in seen:
            errors.append(f"{where}.id is duplicated")
        else:
            seen.add(artifact_id)
        if artifact.get("kind") not in {
            "result-screenshot",
            "baseline-screenshot",
            "accessibility-tree",
        }:
            errors.append(f"{where}.kind is unsupported")
        for field in ("path", "screen", "state", "viewport"):
            if not isinstance(artifact.get(field), str) or not artifact[field]:
                errors.append(f"{where}.{field} is required")
        if not isinstance(artifact.get("supports"), list) or not artifact["supports"]:
            errors.append(f"{where}.supports must be a non-empty list")
    return errors


def validate_project_paths(root: Path, spec: dict[str, Any]) -> list[str]:
    errors: list[str] = []

    def confined(raw: str, where: str) -> Path | None:
        relative = Path(raw)
        if relative.is_absolute() or ".." in relative.parts:
            errors.append(f"{where} must be project-relative: {raw}")
            return None
        candidate = (root / relative).resolve(strict=False)
        try:
            candidate.relative_to(root)
        except ValueError:
            errors.append(f"{where} escapes project root: {raw}")
            return None
        return candidate

    generated_root = confined(
        str(spec.get("generated_artifact_root", "")), "generated_artifact_root"
    )
    if generated_root is None or generated_root == root:
        errors.append("generated_artifact_root must be a confined subdirectory")
        return errors

    for index, target in enumerate(spec.get("test_targets", [])):
        target_path = confined(str(target), f"test_targets[{index}]")
        if target_path is not None and not any(
            target_path.is_relative_to(root / prefix)
            for prefix in ("test", "integration_test")
        ):
            errors.append(
                f"test_targets[{index}] must stay under test/ or integration_test/"
            )

    for index, artifact in enumerate(spec.get("artifacts", [])):
        if not isinstance(artifact, dict):
            continue
        artifact_path = confined(
            str(artifact.get("path", "")), f"artifacts[{index}].path"
        )
        if artifact_path is None:
            continue
        if artifact.get(
            "kind"
        ) != "baseline-screenshot" and not artifact_path.is_relative_to(generated_root):
            errors.append(
                f"artifacts[{index}].path must stay under generated_artifact_root: "
                f"{artifact.get('path')}"
            )
    return errors


def run_command(command: list[str], root: Path, log_path: Path) -> int:
    process = subprocess.run(
        command, cwd=root, check=False, capture_output=True, text=True
    )
    log_path.write_text(
        f"$ {' '.join(command)}\n\nSTDOUT\n{process.stdout}\nSTDERR\n{process.stderr}\nEXIT {process.returncode}\n",
        encoding="utf-8",
    )
    return process.returncode


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--spec", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--validate-only", action="store_true")
    parser.add_argument("--run-id", default="")
    parser.add_argument("--nonce", default="")
    parser.add_argument("--source-fingerprint", default="")
    args = parser.parse_args()
    root = args.root.expanduser().resolve()
    spec_path = args.spec.expanduser().resolve()
    out = args.out.expanduser().resolve()
    try:
        spec = load_object(spec_path)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"capture-flutter-evidence: {exc}", file=sys.stderr)
        return 2
    errors = validate_spec(spec)
    errors.extend(validate_project_paths(root, spec))
    if errors:
        print(
            json.dumps(
                {"status": "invalid", "errors": errors}, ensure_ascii=False, indent=2
            )
        )
        return 2
    if args.validate_only:
        print(json.dumps({"status": "valid", "artifacts": len(spec["artifacts"])}))
        return 0
    if (
        not args.run_id
        or not re.fullmatch(r"[a-f0-9]{48}", args.nonce)
        or not re.fullmatch(r"[a-f0-9]{64}", args.source_fingerprint)
    ):
        print(
            "capture-flutter-evidence: trusted capture requires run-id, nonce, and source fingerprint",
            file=sys.stderr,
        )
        return 2
    if not (root / "pubspec.yaml").is_file():
        print(
            f"capture-flutter-evidence: pubspec.yaml missing: {root}", file=sys.stderr
        )
        return 2
    if shutil.which("flutter") is None:
        print(
            "capture-flutter-evidence: flutter executable is unavailable; no fallback is permitted",
            file=sys.stderr,
        )
        return 2
    out.mkdir(parents=True, exist_ok=True)
    capture_started_ns = time.time_ns()
    results: list[dict[str, Any]] = []
    analyze_log = out / "flutter-analyze.log"
    analyze_code = run_command(["flutter", "analyze"], root, analyze_log)
    results.append(
        {
            "id": "flutter-analyze",
            "status": "passed" if analyze_code == 0 else "failed",
            "artifacts": [
                {
                    "kind": "test-log",
                    "path": str(analyze_log),
                    "sha256": sha256(analyze_log),
                    "platform": "flutter",
                    "supports": ["static-analysis"],
                }
            ],
        }
    )
    targets = [str(value) for value in spec.get("test_targets", [])]
    test_log = out / "flutter-test.log"
    test_code = run_command(["flutter", "test", *targets], root, test_log)
    results.append(
        {
            "id": "flutter-test",
            "status": "passed" if test_code == 0 else "failed",
            "artifacts": [
                {
                    "kind": "test-log",
                    "path": str(test_log),
                    "sha256": sha256(test_log),
                    "platform": "flutter",
                    "supports": ["tests"],
                }
            ],
        }
    )
    for item in spec["artifacts"]:
        source = (root / Path(item["path"])).resolve()
        if not source.is_file():
            results.append(
                {
                    "id": item["id"],
                    "status": "failed",
                    "errors": [f"artifact missing: {source}"],
                    "artifacts": [],
                }
            )
            continue
        if (
            item["kind"] != "baseline-screenshot"
            and source.stat().st_mtime_ns < capture_started_ns
        ):
            results.append(
                {
                    "id": item["id"],
                    "status": "failed",
                    "errors": [
                        f"artifact was not regenerated by this test run: {source}"
                    ],
                    "artifacts": [],
                }
            )
            continue
        suffix = source.suffix or ".artifact"
        destination = out / f"{item['id']}{suffix}"
        shutil.copy2(source, destination)
        results.append(
            {
                "id": item["id"],
                "status": "passed",
                "artifacts": [
                    {
                        "kind": item["kind"],
                        "path": str(destination),
                        "sha256": sha256(destination),
                        "route": item["screen"],
                        "state": item["state"],
                        "viewport": item["viewport"],
                        "platform": "flutter",
                        "supports": item["supports"],
                    }
                ],
            }
        )
    payload = {
        "schema": "design-capture-index-v1",
        "producer": "capture-flutter-evidence@1",
        "generated_at": dt.datetime.now(dt.timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z"),
        "platform": "flutter",
        "project_root": str(root),
        "spec": str(spec_path),
        "spec_sha256": sha256(spec_path),
        "run_id": args.run_id,
        "nonce": args.nonce,
        "adapter_sha256": sha256(Path(__file__).resolve()),
        "source_fingerprint_digest": args.source_fingerprint,
        "status": "passed"
        if all(result["status"] == "passed" for result in results)
        else "failed",
        "results": results,
    }
    index = out / "capture-index.json"
    index.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(index)
    return 0 if payload["status"] == "passed" else 2


if __name__ == "__main__":
    raise SystemExit(main())
