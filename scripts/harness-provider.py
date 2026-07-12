#!/usr/bin/env python3
"""Resolve and enforce a provider-native Claude Craft quality-class binding."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from harness_runtime_lib import (
    HarnessError,
    load_data,
    project_root_from,
    resolve_provider_quality,
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, help="Repository root")
    parser.add_argument(
        "--provider", required=True, help="claude, codex, gemini, or opencode"
    )
    parser.add_argument(
        "--quality-tier",
        required=True,
        help="reasoning_high, implementation, fast_scan, or independent_critic",
    )
    parser.add_argument("--output", type=Path, help="Optional JSON output path")
    args = parser.parse_args()

    root = (args.root or project_root_from(Path(__file__))).resolve()
    try:
        registry = load_data(root / ".claude" / "registry" / "providers" / "core.yaml")
        binding = resolve_provider_quality(registry, args.provider, args.quality_tier)
    except HarnessError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    payload = json.dumps(binding, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        output = args.output if args.output.is_absolute() else root / args.output
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(payload, encoding="utf-8")
        print(output)
    else:
        sys.stdout.write(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
