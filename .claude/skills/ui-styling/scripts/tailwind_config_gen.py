#!/usr/bin/env python3
"""Generate a Tailwind CSS 4 CSS-first theme file.

The filename is kept for compatibility with existing skill callers. It no longer
generates a Tailwind 3 JavaScript configuration.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path


TOKEN_NAME = re.compile(r"^[a-z0-9][a-z0-9-]*$")


class TailwindConfigGenerator:
    """Build Tailwind 4 ``@theme`` and ``@plugin`` CSS."""

    def __init__(
        self,
        typescript: bool | None = None,
        framework: str = "react",
        output_path: Path | None = None,
    ) -> None:
        self.typescript = typescript
        self.framework = framework
        self.output_path = output_path or Path.cwd() / "tailwind-theme.css"
        self.tokens: dict[str, str] = {}
        self.plugins: list[str] = []

    @staticmethod
    def _name(value: str) -> str:
        normalized = value.strip().lower().replace("_", "-")
        if not TOKEN_NAME.fullmatch(normalized):
            raise ValueError(f"invalid Tailwind token name: {value!r}")
        return normalized

    def add_colors(self, colors: dict[str, str]) -> None:
        for name, value in colors.items():
            self.tokens[f"--color-{self._name(name)}"] = value.strip()

    def add_color_palette(self, name: str, base_color: str) -> None:
        """Add the supplied color as shade 500 without fabricating a palette."""
        self.tokens[f"--color-{self._name(name)}-500"] = base_color.strip()

    def add_fonts(self, fonts: dict[str, list[str]]) -> None:
        for role, families in fonts.items():
            if not families:
                raise ValueError(f"font family list is empty: {role}")
            rendered = ", ".join(
                family
                if family in {"serif", "sans-serif", "monospace", "system-ui"}
                else f'"{family}"'
                for family in families
            )
            self.tokens[f"--font-{self._name(role)}"] = rendered

    def add_spacing(self, spacing: dict[str, str]) -> None:
        for name, value in spacing.items():
            self.tokens[f"--spacing-{self._name(name)}"] = value.strip()

    def add_breakpoints(self, breakpoints: dict[str, str]) -> None:
        for name, value in breakpoints.items():
            self.tokens[f"--breakpoint-{self._name(name)}"] = value.strip()

    def add_plugins(self, plugins: list[str]) -> None:
        for plugin in plugins:
            value = plugin.strip()
            if not value or any(
                character in value for character in {'"', "'", "\n", "\r"}
            ):
                raise ValueError(f"invalid plugin package: {plugin!r}")
            if value not in self.plugins:
                self.plugins.append(value)

    def recommend_plugins(self) -> list[str]:
        """Return no automatic plugins; project requirements decide."""
        return []

    def generate_config_string(self) -> str:
        lines = [
            "/* Tailwind CSS 4 theme — generated; edit the source contract, not this file. */",
            '@import "tailwindcss";',
            "",
            "@custom-variant dark (&:where(.dark, .dark *));",
        ]
        for plugin in self.plugins:
            lines.append(f'@plugin "{plugin}";')
        if self.plugins:
            lines.append("")
        lines.append("@theme {")
        for name, value in sorted(self.tokens.items()):
            lines.append(f"  {name}: {value};")
        lines.append("}")
        lines.append("")
        return "\n".join(lines)

    def write_config(self) -> tuple[bool, str]:
        valid, message = self.validate_config()
        if not valid:
            return False, message
        try:
            self.output_path.parent.mkdir(parents=True, exist_ok=True)
            self.output_path.write_text(self.generate_config_string(), encoding="utf-8")
        except OSError as exc:
            return False, f"Failed to write theme: {exc}"
        return True, f"Tailwind 4 theme written to {self.output_path}"

    def validate_config(self) -> tuple[bool, str]:
        for name, value in self.tokens.items():
            if not name.startswith(
                ("--color-", "--font-", "--spacing-", "--breakpoint-")
            ):
                return False, f"Unsupported token namespace: {name}"
            if not value:
                return False, f"Empty token value: {name}"
        return True, "Tailwind 4 CSS-first theme valid"


def parse_pairs(values: list[str] | None, label: str) -> dict[str, str]:
    result: dict[str, str] = {}
    for value in values or []:
        name, separator, item = value.partition(":")
        if not separator or not name or not item:
            raise ValueError(f"{label} must use NAME:VALUE: {value!r}")
        result[name] = item
    return result


def parse_fonts(values: list[str] | None) -> dict[str, list[str]]:
    return {
        role: [family.strip() for family in value.split(",") if family.strip()]
        for role, value in parse_pairs(values, "font").items()
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate Tailwind CSS 4 @theme CSS")
    parser.add_argument(
        "--framework", choices=["react", "vue", "svelte", "nextjs"], default="react"
    )
    parser.add_argument("--output", type=Path)
    parser.add_argument("--colors", nargs="*", metavar="NAME:VALUE")
    parser.add_argument("--fonts", nargs="*", metavar="ROLE:FAMILY1,FAMILY2")
    parser.add_argument("--spacing", nargs="*", metavar="NAME:VALUE")
    parser.add_argument("--breakpoints", nargs="*", metavar="NAME:WIDTH")
    parser.add_argument("--plugin", action="append", default=[])
    parser.add_argument("--js", action="store_true", help=argparse.SUPPRESS)
    args = parser.parse_args()
    if args.js:
        parser.error(
            "Tailwind 4 generated defaults are CSS-first; use an explicit legacy @config migration lane if required"
        )
    try:
        generator = TailwindConfigGenerator(
            framework=args.framework, output_path=args.output
        )
        generator.add_colors(parse_pairs(args.colors, "color"))
        generator.add_fonts(parse_fonts(args.fonts))
        generator.add_spacing(parse_pairs(args.spacing, "spacing"))
        generator.add_breakpoints(parse_pairs(args.breakpoints, "breakpoint"))
        generator.add_plugins(args.plugin)
        success, message = generator.write_config()
    except ValueError as exc:
        parser.error(str(exc))
    print(message)
    return 0 if success else 1


if __name__ == "__main__":
    raise SystemExit(main())
