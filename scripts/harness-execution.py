#!/usr/bin/env python3
"""Create and transition typed, evidence-bearing harness execution records."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from harness_runtime_lib import (
    EXECUTION_ARTIFACT_ROOT,
    EXECUTION_STATES,
    HarnessError,
    load_data,
    new_execution_record,
    transition_execution,
    validate_execution_record,
    validate_process_outcome,
    write_json,
)


def parse_evidence(values: list[str]) -> list[dict[str, Any]]:
    evidence = []
    for value in values:
        if value.lstrip().startswith("{"):
            try:
                item = json.loads(value)
            except json.JSONDecodeError as exc:
                raise HarnessError(f"evidence JSON is invalid: {exc}") from exc
            if not isinstance(item, dict):
                raise HarnessError("evidence JSON must be an object")
            evidence.append(item)
            continue
        if ":" not in value:
            raise HarnessError("evidence must use TYPE:DESCRIPTION or a JSON object")
        evidence_type, description = value.split(":", 1)
        if not evidence_type.strip() or not description.strip():
            raise HarnessError("evidence requires non-empty type and description")
        evidence.append(
            {"type": evidence_type.strip(), "description": description.strip()}
        )
    return evidence


def parse_checks(values: list[str]) -> list[dict[str, str]]:
    checks = []
    for value in values:
        if "=" not in value:
            raise HarnessError("check must use CRITERION=passed|failed")
        criterion, status = value.rsplit("=", 1)
        if status not in {"passed", "failed"}:
            raise HarnessError("check status must be passed or failed")
        checks.append({"criterion": criterion.strip(), "status": status})
    return checks


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    init = subparsers.add_parser("init", help="Create a pending execution record")
    init.add_argument("--file", type=Path, required=True)
    init.add_argument("--id", required=True)
    init.add_argument("--objective", required=True)
    init.add_argument("--success-criterion", action="append", default=[])

    transition = subparsers.add_parser(
        "transition", help="Apply a validated state transition"
    )
    transition.add_argument("--file", type=Path, required=True)
    transition.add_argument("--to", required=True, choices=sorted(EXECUTION_STATES))
    transition.add_argument("--reason", default="")
    transition.add_argument("--stop-reason")
    transition.add_argument(
        "--evidence",
        action="append",
        default=[],
        help=(
            "Evidence JSON with type, description, path, sha256, and bytes. "
            "Succeeded evidence also requires producer, command, exit_code, and status. "
            "Paths are relative to the outcome-owned artifacts/ directory. "
            "TYPE:DESCRIPTION remains diagnostic-only and cannot support succeeded."
        ),
    )
    transition.add_argument("--check", action="append", default=[])

    validate = subparsers.add_parser("validate", help="Validate a record")
    validate.add_argument("--file", type=Path, required=True)
    validate.add_argument("--final", action="store_true")

    process = subparsers.add_parser(
        "from-exit", help="Resolve a process exit using an explicit outcome"
    )
    process.add_argument("--exit-code", type=int, required=True)
    process.add_argument("--outcome-file", type=Path)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        if args.command == "init":
            if not args.success_criterion:
                raise HarnessError("at least one --success-criterion is required")
            record = new_execution_record(
                args.id, args.objective, args.success_criterion
            )
            artifact_root = args.file.resolve().parent / EXECUTION_ARTIFACT_ROOT
            if artifact_root.is_symlink() or (
                artifact_root.exists() and not artifact_root.is_dir()
            ):
                raise HarnessError(
                    f"artifact root is symlinked or not a directory: {artifact_root}"
                )
            artifact_root.mkdir(parents=True, exist_ok=True)
            write_json(args.file, record)
            print(args.file)
            return 0

        if args.command == "transition":
            record = load_data(args.file)
            updated = transition_execution(
                record,
                args.to,
                reason=args.reason,
                stop_reason=args.stop_reason,
                evidence=parse_evidence(args.evidence),
                checks=parse_checks(args.check) if args.check else None,
            )
            if args.to == "succeeded":
                artifact_errors = validate_execution_record(
                    updated,
                    artifact_root=args.file.resolve().parent / EXECUTION_ARTIFACT_ROOT,
                )
                if artifact_errors:
                    raise HarnessError("; ".join(artifact_errors))
            write_json(args.file, updated)
            print(
                json.dumps({"state": updated["state"], "attempt": updated["attempt"]})
            )
            return 0

        if args.command == "validate":
            record = load_data(args.file)
            errors = validate_execution_record(
                record,
                final=args.final,
                artifact_root=args.file.resolve().parent / EXECUTION_ARTIFACT_ROOT,
            )
            if errors:
                for error in errors:
                    print(f"ERROR: {error}", file=sys.stderr)
                return 1
            print("PASS")
            return 0

        state, reason, _ = validate_process_outcome(args.exit_code, args.outcome_file)
        print(json.dumps({"state": state, "reason": reason}, ensure_ascii=False))
        return 0 if state == "succeeded" else 1
    except HarnessError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
