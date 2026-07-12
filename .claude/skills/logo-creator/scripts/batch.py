#!/usr/bin/env python3
"""Build a preview for files already generated through `image-prompt`.

This script is deliberately artifact-only: it does not author prompts, select
models, call an image API, or modify source rasters.
"""

from __future__ import annotations

import argparse
import html
import json
import re
from pathlib import Path


def discover_images(output_dir: Path, prefix: str, count: int | None) -> list[Path]:
    images = sorted(
        path
        for path in output_dir.iterdir()
        if path.is_file()
        and path.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp"}
        and path.name.startswith(prefix)
    )
    return images[:count] if count is not None else images


def build_preview(output_dir: Path, images: list[Path]) -> Path:
    template = Path(__file__).parent.parent / "templates" / "preview.html"
    if not template.is_file():
        raise SystemExit(f"preview template not found: {template}")

    document = template.read_text(encoding="utf-8")
    cards = []
    for index, image in enumerate(images, 1):
        name = html.escape(image.name, quote=True)
        cards.append(
            f'    <div class="logo-card" data-src="{name}" onclick="showModal(this)">\n'
            f'      <img src="{name}" alt="Logo option {index}">\n'
            f"      <p>#{index:02d}</p>\n"
            "    </div>"
        )

    document = document.replace("<!-- LOGO_CARDS_PLACEHOLDER -->", "\n".join(cards))
    document = re.sub(
        r'<!-- Example cards.*?(?=\s*</div>\s*\n\s*<div class="favorites-bar">)',
        "",
        document,
        flags=re.DOTALL,
    )
    preview = output_dir / "preview.html"
    preview.write_text(document, encoding="utf-8")
    return preview


def validate_manifest(path: Path, images: list[Path]) -> None:
    if not path.is_file():
        raise SystemExit(f"asset manifest not found: {path}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    records = payload if isinstance(payload, list) else payload.get("assets", [])
    source_names = {
        Path(record.get("source_raster", record.get("output_path", ""))).name
        for record in records
        if isinstance(record, dict)
    }
    missing = [image.name for image in images if image.name not in source_names]
    if missing:
        raise SystemExit(f"images missing from manifest: {', '.join(missing)}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build a preview for Gongnyang/Codex logo outputs"
    )
    parser.add_argument("--output-dir", "-d", type=Path, required=True)
    parser.add_argument("--prefix", default="logo-")
    parser.add_argument("--count", "-n", type=int)
    parser.add_argument("--manifest", type=Path)
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)
    images = discover_images(args.output_dir, args.prefix, args.count)
    if not images:
        raise SystemExit(
            "no generated logo files found; run image-prompt -> Codex $imagegen first"
        )
    if args.manifest:
        validate_manifest(args.manifest, images)
    preview = build_preview(args.output_dir, images)
    print(preview)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
