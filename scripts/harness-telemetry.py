#!/usr/bin/env python3
"""Normalize, validate, and append Claude Craft telemetry JSONL."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from pathlib import Path

from harness_runtime_lib import (
    HarnessError,
    normalize_telemetry_event,
    read_json_stream,
)


REQUIRED = {
    "schema_version",
    "timestamp",
    "session_id",
    "provider",
    "event_type",
    "subject_type",
    "subject_id",
    "status",
    "metadata",
}


def event_errors(event: dict) -> list[str]:
    errors = []
    missing = sorted(REQUIRED - set(event))
    if missing:
        errors.append("missing fields: " + ", ".join(missing))
    if event.get("schema_version") != "harness.telemetry.v1":
        errors.append("schema_version must be harness.telemetry.v1")
    timestamp = event.get("timestamp")
    if not isinstance(timestamp, str) or not timestamp.strip():
        errors.append("timestamp must be a non-empty RFC 3339 string")
    else:
        try:
            parsed = dt.datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        except ValueError:
            errors.append("timestamp must be a valid RFC 3339 date-time")
        else:
            if parsed.tzinfo is None:
                errors.append("timestamp must include a timezone")
    for field in (
        "session_id",
        "provider",
        "event_type",
        "subject_type",
        "subject_id",
        "status",
    ):
        value = event.get(field)
        if not isinstance(value, str) or not value.strip():
            errors.append(f"{field} must be a non-empty string")
    for field in ("duration_ms", "context_bytes"):
        value = event.get(field)
        if value is not None and (
            not isinstance(value, int) or isinstance(value, bool) or value < 0
        ):
            errors.append(f"{field} must be null or a non-negative integer")
    if not isinstance(event.get("metadata"), dict):
        errors.append("metadata must be an object")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    normalize = subparsers.add_parser(
        "normalize", help="Convert legacy/pretty logs to one-object-per-line v1 JSONL"
    )
    normalize.add_argument("input", type=Path)
    normalize.add_argument("--output", type=Path)
    validate = subparsers.add_parser("validate", help="Validate all events in a log")
    validate.add_argument("input", type=Path)
    append = subparsers.add_parser("append", help="Append one event read from stdin")
    append.add_argument("output", type=Path)
    args = parser.parse_args()

    if args.command in {"normalize", "validate"}:
        try:
            entries = [
                normalize_telemetry_event(item) for item in read_json_stream(args.input)
            ]
        except HarnessError as exc:
            print(f"ERROR: {exc}", file=sys.stderr)
            return 2
        invalid = [
            (index, event_errors(item))
            for index, item in enumerate(entries)
            if event_errors(item)
        ]
        if invalid:
            for index, errors in invalid:
                print(f"ERROR event[{index}]: {'; '.join(errors)}", file=sys.stderr)
            return 1
        if args.command == "validate":
            print(f"PASS: {len(entries)} events")
            return 0
        output_lines = "".join(
            json.dumps(item, ensure_ascii=False, separators=(",", ":")) + "\n"
            for item in entries
        )
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(output_lines, encoding="utf-8")
            print(args.output)
        else:
            sys.stdout.write(output_lines)
        return 0

    try:
        event = normalize_telemetry_event(json.load(sys.stdin))
    except json.JSONDecodeError as exc:
        print(f"ERROR: invalid stdin JSON: {exc}", file=sys.stderr)
        return 2
    errors = event_errors(event)
    if errors:
        print("ERROR: " + "; ".join(errors), file=sys.stderr)
        return 1
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("a", encoding="utf-8") as handle:
        handle.write(
            json.dumps(event, ensure_ascii=False, separators=(",", ":")) + "\n"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
