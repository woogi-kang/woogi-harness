#!/usr/bin/env python3
"""Validate evidence contracts for a product UI promotion project."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "remotion.product-ui-promo.v1"
PRESETS = {
    "typing",
    "cursorClick",
    "imageDrag",
    "uiZoom",
    "cardStack",
    "brandTitle",
}
TRANSITIONS = {"cut", "fade", "slide", "wipe"}
CAPTURE_KINDS = {
    "playwright_live_app",
    "browser_product_fixture",
    "product_golden_renderer",
}
SHA256 = re.compile(r"^[0-9a-f]{64}$")


def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError(f"{path}: cannot read JSON: {error}") from error
    if not isinstance(value, dict):
        raise ValueError(f"{path}: root must be an object")
    return value


def require(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def is_number(value: Any) -> bool:
    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and math.isfinite(value)
    )


def is_positive_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value > 0


def is_nonnegative_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value >= 0


def is_nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def object_field(
    data: dict[str, Any],
    key: str,
    label: str,
    errors: list[str],
) -> dict[str, Any]:
    value = data.get(key)
    require(isinstance(value, dict), f"{label}: {key} must be an object", errors)
    return value if isinstance(value, dict) else {}


def validate_reference(data: dict[str, Any], errors: list[str]) -> None:
    require(
        data.get("schemaVersion") == SCHEMA_VERSION,
        "reference: bad schemaVersion",
        errors,
    )
    reference = object_field(data, "reference", "reference", errors)
    status = reference.get("status")
    require(
        status in {"analyzed", "not_provided"},
        "reference: status must be analyzed or not_provided",
        errors,
    )
    grammar = data.get("motionGrammar")
    require(
        isinstance(grammar, dict) and bool(grammar),
        "reference: motionGrammar is required",
        errors,
    )
    if status == "analyzed":
        shots = data.get("shots")
        require(
            isinstance(shots, list) and bool(shots),
            "reference: analyzed input needs shots",
            errors,
        )
        shot_items = shots if isinstance(shots, list) else []
        for index, shot in enumerate(shot_items):
            if not isinstance(shot, dict):
                errors.append(f"reference: shot {index} must be an object")
                continue
            require(
                all(
                    key in shot
                    for key in (
                        "startMs",
                        "endMs",
                        "durationMs",
                        "cameraEntry",
                        "transitionMs",
                        "revealOrder",
                    )
                ),
                f"reference: shot {index} is incomplete",
                errors,
            )
            start = shot.get("startMs")
            end = shot.get("endMs")
            duration = shot.get("durationMs")
            require(
                is_number(start) and start >= 0,
                f"reference: shot {index} startMs is invalid",
                errors,
            )
            require(
                is_number(end) and is_number(start) and end > start,
                f"reference: shot {index} endMs is invalid",
                errors,
            )
            require(
                is_number(duration) and duration > 0,
                f"reference: shot {index} durationMs is invalid",
                errors,
            )
            if is_number(start) and is_number(end) and is_number(duration):
                require(
                    abs((end - start) - duration) <= 1,
                    f"reference: shot {index} durationMs is inconsistent",
                    errors,
                )
            require(
                is_nonempty_string(shot.get("cameraEntry")),
                f"reference: shot {index} cameraEntry is invalid",
                errors,
            )
            require(
                is_number(shot.get("transitionMs"))
                and shot.get("transitionMs", -1) >= 0,
                f"reference: shot {index} transitionMs is invalid",
                errors,
            )
            reveal_order = shot.get("revealOrder")
            require(
                isinstance(reveal_order, list)
                and bool(reveal_order)
                and all(is_nonempty_string(item) for item in reveal_order),
                f"reference: shot {index} revealOrder is invalid",
                errors,
            )
    elif status == "not_provided":
        require(
            is_nonempty_string(reference.get("reason")),
            "reference: not_provided needs reason",
            errors,
        )


def validate_capture(
    data: dict[str, Any],
    errors: list[str],
    project_root: Path | None = None,
) -> None:
    require(
        data.get("schemaVersion") == SCHEMA_VERSION,
        "capture: bad schemaVersion",
        errors,
    )
    source = object_field(data, "source", "capture", errors)
    require(
        source.get("kind") in CAPTURE_KINDS,
        "capture: unsupported source kind",
        errors,
    )
    require(
        is_nonempty_string(source.get("repo")),
        "capture: source repo is required",
        errors,
    )
    require(
        is_nonempty_string(source.get("revision")),
        "capture: source revision is required",
        errors,
    )
    require(
        isinstance(source.get("dirtyWorktree"), bool),
        "capture: source dirtyWorktree must be boolean",
        errors,
    )
    runtime = object_field(data, "runtime", "capture", errors)
    viewport = runtime.get("viewport")
    require(
        isinstance(viewport, dict),
        "capture: runtime.viewport must be an object",
        errors,
    )
    if isinstance(viewport, dict):
        require(
            is_positive_int(viewport.get("width")),
            "capture: runtime.viewport.width is invalid",
            errors,
        )
        require(
            is_positive_int(viewport.get("height")),
            "capture: runtime.viewport.height is invalid",
            errors,
        )
    require(
        is_number(runtime.get("devicePixelRatio"))
        and runtime.get("devicePixelRatio", 0) > 0,
        "capture: runtime.devicePixelRatio is invalid",
        errors,
    )
    for key in ("locale", "timezone", "clock", "readiness"):
        require(
            is_nonempty_string(runtime.get(key)),
            f"capture: runtime.{key} is required",
            errors,
        )
    frames = data.get("frames")
    require(
        isinstance(frames, list) and bool(frames),
        "capture: at least one frame is required",
        errors,
    )
    frame_ids: set[str] = set()
    frame_paths: set[str] = set()
    resolved_root = project_root.resolve() if project_root is not None else None
    if resolved_root is not None:
        require(
            resolved_root.is_dir(),
            "capture: project root is missing or not a directory",
            errors,
        )
    frame_items = frames if isinstance(frames, list) else []
    for index, frame in enumerate(frame_items):
        if not isinstance(frame, dict):
            errors.append(f"capture: frame {index} must be an object")
            continue
        for key in ("id", "path", "state", "frame", "width", "height", "sha256"):
            require(key in frame, f"capture: frame {index}.{key} is required", errors)
        frame_id = frame.get("id")
        frame_path = frame.get("path")
        require(
            is_nonempty_string(frame_id),
            f"capture: frame {index} id is invalid",
            errors,
        )
        require(
            is_nonempty_string(frame_path),
            f"capture: frame {index} path is invalid",
            errors,
        )
        require(
            is_nonempty_string(frame.get("state")),
            f"capture: frame {index} state is invalid",
            errors,
        )
        require(
            is_nonnegative_int(frame.get("frame")),
            f"capture: frame {index} frame is invalid",
            errors,
        )
        require(
            is_positive_int(frame.get("width")),
            f"capture: frame {index} width is invalid",
            errors,
        )
        require(
            is_positive_int(frame.get("height")),
            f"capture: frame {index} height is invalid",
            errors,
        )
        require(
            bool(SHA256.fullmatch(str(frame.get("sha256", "")))),
            f"capture: frame {index} sha256 is invalid",
            errors,
        )
        if isinstance(frame_id, str):
            require(
                frame_id not in frame_ids,
                f"capture: frame {index} id is duplicated",
                errors,
            )
            frame_ids.add(frame_id)
        if isinstance(frame_path, str):
            require(
                frame_path not in frame_paths,
                f"capture: frame {index} path is duplicated",
                errors,
            )
            frame_paths.add(frame_path)
        if resolved_root is not None and isinstance(frame_path, str):
            raw_path = Path(frame_path)
            require(
                not raw_path.is_absolute(),
                f"capture: frame {index} path must be relative",
                errors,
            )
            capture_path = (resolved_root / raw_path).resolve()
            try:
                capture_path.relative_to(resolved_root)
                contained = True
            except ValueError:
                contained = False
            require(
                contained,
                f"capture: frame {index} path escapes project root",
                errors,
            )
            require(
                contained and capture_path.is_file(),
                f"capture: frame {index} file is missing",
                errors,
            )
            if contained and capture_path.is_file():
                actual_hash = hashlib.sha256(capture_path.read_bytes()).hexdigest()
                require(
                    actual_hash == frame.get("sha256"),
                    f"capture: frame {index} sha256 does not match its file",
                    errors,
                )


def validate_scenes(data: dict[str, Any], errors: list[str]) -> None:
    require(
        data.get("schemaVersion") == SCHEMA_VERSION,
        "scenes: bad schemaVersion",
        errors,
    )
    require(
        is_nonempty_string(data.get("composition")),
        "scenes: composition is required",
        errors,
    )
    for key in ("fps", "width", "height", "durationInFrames"):
        require(
            is_positive_int(data.get(key)),
            f"scenes: {key} must be a positive integer",
            errors,
        )
    scenes = data.get("scenes")
    require(
        isinstance(scenes, list) and bool(scenes),
        "scenes: at least one scene is required",
        errors,
    )
    total = 0
    scene_items = scenes if isinstance(scenes, list) else []
    for index, scene in enumerate(scene_items):
        if not isinstance(scene, dict):
            errors.append(f"scenes: scene {index} must be an object")
            continue
        expected = {"preset", "durationInFrames", "params", "transition", "camera"}
        require(
            expected.issubset(scene),
            f"scenes: scene {index} is missing the five-field contract",
            errors,
        )
        require(
            scene.get("preset") in PRESETS,
            f"scenes: scene {index} has unsupported preset",
            errors,
        )
        duration = scene.get("durationInFrames")
        require(
            is_positive_int(duration),
            f"scenes: scene {index} duration is invalid",
            errors,
        )
        if is_positive_int(duration):
            total += duration
        require(
            isinstance(scene.get("params"), dict),
            f"scenes: scene {index} params must be an object",
            errors,
        )
        transition = scene.get("transition")
        require(
            isinstance(transition, dict),
            f"scenes: scene {index} transition must be an object",
            errors,
        )
        transition = transition if isinstance(transition, dict) else {}
        require(
            transition.get("type") in TRANSITIONS,
            f"scenes: scene {index} transition type is invalid",
            errors,
        )
        transition_duration = transition.get("durationInFrames")
        require(
            is_nonnegative_int(transition_duration),
            f"scenes: scene {index} transition duration is invalid",
            errors,
        )
        if is_nonnegative_int(transition_duration) and is_positive_int(duration):
            require(
                transition_duration <= duration,
                f"scenes: scene {index} transition exceeds scene duration",
                errors,
            )
        camera = scene.get("camera")
        require(
            isinstance(camera, dict),
            f"scenes: scene {index} camera must be an object",
            errors,
        )
        camera = camera if isinstance(camera, dict) else {}
        require(
            all(
                is_number(camera.get(key))
                for key in ("x", "y", "scale", "rotateX", "rotateY")
            ),
            f"scenes: scene {index} camera is incomplete",
            errors,
        )
        require(
            is_number(camera.get("scale")) and camera.get("scale", 0) > 0,
            f"scenes: scene {index} camera scale is invalid",
            errors,
        )
    require(
        total == data.get("durationInFrames"),
        "scenes: durations do not sum to durationInFrames",
        errors,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--reference", type=Path, required=True)
    parser.add_argument("--capture", type=Path, required=True)
    parser.add_argument("--scenes", type=Path, required=True)
    parser.add_argument("--project-root", type=Path)
    args = parser.parse_args()

    errors: list[str] = []
    documents: dict[str, dict[str, Any]] = {}
    for label, path in (
        ("reference", args.reference),
        ("capture", args.capture),
        ("scenes", args.scenes),
    ):
        try:
            documents[label] = load_json(path)
        except ValueError as error:
            errors.append(str(error))

    if "reference" in documents:
        validate_reference(documents["reference"], errors)
    if "capture" in documents:
        validate_capture(documents["capture"], errors, args.project_root)
    if "scenes" in documents:
        validate_scenes(documents["scenes"], errors)

    if errors:
        for error in errors:
            print(f"FAIL: {error}")
        return 1
    print("PASS: product UI promotion contracts are valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
