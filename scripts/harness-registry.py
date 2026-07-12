#!/usr/bin/env python3
"""Inspect and validate the canonical Claude Craft capability registry."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from harness_runtime_lib import (
    HarnessError,
    build_asset_inventory,
    capability_index,
    merge_effective_capabilities,
    project_root_from,
    validate_registry,
    write_json,
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "command",
        choices=("validate", "list", "resolve", "inventory", "build"),
        nargs="?",
        default="validate",
    )
    parser.add_argument(
        "names", nargs="*", help="Capability ids or aliases for resolve"
    )
    parser.add_argument("--root", type=Path, help="Repository root")
    parser.add_argument(
        "--strict-legacy",
        action="store_true",
        help="Treat duplicate names in the legacy catalog as errors",
    )
    parser.add_argument(
        "--json", action="store_true", help="Emit machine-readable JSON"
    )
    parser.add_argument("--output", type=Path, help="Inventory output path for build")
    args = parser.parse_args()

    root = (args.root or project_root_from(Path(__file__))).resolve()
    registry_root = root / ".claude" / "registry"
    try:
        capabilities, issues = validate_registry(
            root, registry_root, strict_legacy=args.strict_legacy
        )
        inventory = build_asset_inventory(root)
        effective = merge_effective_capabilities(capabilities, inventory)
    except HarnessError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    errors = [issue for issue in issues if issue.severity == "error"]
    if args.command == "inventory":
        if args.json:
            print(json.dumps(inventory, ensure_ascii=False, indent=2))
        else:
            print(
                f"Inventory: {inventory['asset_count']} assets, "
                f"{len(inventory['duplicate_groups'])} duplicate name groups"
            )
            for name, count in inventory["duplicate_groups"].items():
                print(f"DUPLICATE {name}: {count}")
        return 1 if errors else 0

    if args.command == "build":
        output = args.output or registry_root / "generated" / "inventory.json"
        if not output.is_absolute():
            output = root / output
        write_json(output, inventory)
        result = {
            "output": str(output),
            "asset_count": inventory["asset_count"],
            "inventory_hash": inventory["inventory_hash"],
        }
        print(json.dumps(result, ensure_ascii=False, indent=2) if args.json else output)
        return 1 if errors else 0

    if args.command == "list":
        payload = [
            {
                "id": item["id"],
                "kind": item.get("kind"),
                "aliases": item.get("aliases", []),
                "status": item.get("status"),
            }
            for item in effective
        ]
        if args.json:
            print(json.dumps(payload, ensure_ascii=False, indent=2))
        else:
            for item in payload:
                aliases = ", ".join(item["aliases"]) or "-"
                print(f"{item['id']:<32} {item['kind']:<10} aliases={aliases}")
        return 1 if errors else 0

    if args.command == "resolve":
        index = capability_index(effective)
        resolved = []
        missing = []
        for name in args.names:
            item = index.get(name)
            if item is None:
                missing.append(name)
            else:
                resolved.append(
                    {"requested": name, "id": item["id"], "source": item.get("source")}
                )
        if args.json:
            print(
                json.dumps(
                    {"resolved": resolved, "missing": missing},
                    ensure_ascii=False,
                    indent=2,
                )
            )
        else:
            for item in resolved:
                print(f"{item['requested']} -> {item['id']} ({item['source']})")
            for name in missing:
                print(f"UNKNOWN: {name}", file=sys.stderr)
        return 1 if errors or missing else 0

    payload = {
        "ok": not errors,
        "static_count": len(capabilities),
        "inventory_count": inventory["asset_count"],
        "resolvable_count": len(effective),
        "capability_count": len(effective),
        "inventory_hash": inventory["inventory_hash"],
        "issues": [issue.as_dict() for issue in issues],
    }
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(
            f"Registry: {len(capabilities)} static + {inventory['asset_count']} inventoried "
            f"= {len(effective)} resolvable entries"
        )
        for issue in issues:
            paths = f" ({', '.join(issue.paths)})" if issue.paths else ""
            print(f"{issue.severity.upper()}: [{issue.code}] {issue.message}{paths}")
        print("PASS" if not errors else "FAIL")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
