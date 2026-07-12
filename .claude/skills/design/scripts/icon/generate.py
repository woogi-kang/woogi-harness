#!/usr/bin/env python3
"""Normalize an existing deterministic SVG icon.

Raster icon generation is owned by `image-prompt` and Codex `$imagegen`.
This command never calls a model and never authors an image prompt.
"""

from __future__ import annotations

import argparse
import re
import xml.etree.ElementTree as ET
from pathlib import Path


SVG_NS = "http://www.w3.org/2000/svg"
ET.register_namespace("", SVG_NS)


def validate_tree(root: ET.Element) -> None:
    if root.tag not in {"svg", f"{{{SVG_NS}}}svg"}:
        raise SystemExit("input root is not <svg>")
    forbidden = {"script", "image", "foreignObject"}
    for element in root.iter():
        local = element.tag.rsplit("}", 1)[-1]
        if local in forbidden:
            raise SystemExit(f"forbidden SVG element: {local}")
        for attribute, value in element.attrib.items():
            name = attribute.rsplit("}", 1)[-1].lower()
            if name.startswith("on") or name in {"href", "src"}:
                raise SystemExit(f"forbidden SVG attribute: {name}")
            if re.search(r"(?:javascript:|data:|https?://)", value, re.IGNORECASE):
                raise SystemExit("external or executable SVG reference is forbidden")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Normalize and validate a deterministic SVG icon"
    )
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--size", type=int, default=24)
    parser.add_argument("--color")
    args = parser.parse_args()

    root = ET.fromstring(args.input.read_text(encoding="utf-8"))
    validate_tree(root)
    root.set("width", str(args.size))
    root.set("height", str(args.size))
    if "viewBox" not in root.attrib:
        root.set("viewBox", f"0 0 {args.size} {args.size}")
    if args.color:
        root.set("color", args.color)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    ET.ElementTree(root).write(args.output, encoding="unicode", xml_declaration=False)
    args.output.write_text(
        args.output.read_text(encoding="utf-8") + "\n", encoding="utf-8"
    )
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
