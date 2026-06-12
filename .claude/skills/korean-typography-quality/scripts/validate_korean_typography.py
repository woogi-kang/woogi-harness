#!/usr/bin/env python3
"""Static Korean typography guard for generated artifacts.

Usage:
  python validate_korean_typography.py artifact.html [artifact.css ...]
  cat artifact.html | python validate_korean_typography.py -
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

HANGUL_RE = re.compile(r"[가-힣]")
FONT_RE = re.compile(r"font-family\\s*:\\s*([^;}{]+)", re.I)
KOREAN_FONT_MARKERS = [
    "Pretendard", "Nanum", "Noto Sans KR", "Noto Serif KR", "Apple SD Gothic Neo",
    "Malgun Gothic", "Spoqa", "Goorm", "Gmarket", "MaruBuri", "Hahmlet", "Gowun",
    "IBM Plex Sans KR",
]


def read_inputs(paths: list[str]) -> dict[str, str]:
    if not paths:
        data = sys.stdin.read()
        return {"<stdin>": data}
    out: dict[str, str] = {}
    for raw in paths:
        if raw == "-":
            out["<stdin>"] = sys.stdin.read()
            continue
        p = Path(raw)
        if p.is_dir():
            for child in p.rglob("*"):
                if child.suffix.lower() in {".html", ".css", ".tsx", ".jsx", ".ts", ".js", ".md", ".mdx"}:
                    out[str(child)] = child.read_text(encoding="utf-8", errors="ignore")
        else:
            out[str(p)] = p.read_text(encoding="utf-8", errors="ignore")
    return out


def has_any(text: str, needles: list[str]) -> bool:
    lower = text.lower()
    return any(n.lower() in lower for n in needles)


def normalized_font_families(text: str) -> set[str]:
    families: set[str] = set()
    for match in FONT_RE.finditer(text):
        value = match.group(1)
        # Keep CSS variable font roles as one family each.
        if "var(" in value:
            families.add(value.strip())
            continue
        first = value.split(",")[0].strip().strip('"\'')
        if first:
            families.add(first)
    return families


def evaluate(text: str) -> tuple[list[str], list[str]]:
    failures: list[str] = []
    warnings: list[str] = []
    has_korean = bool(HANGUL_RE.search(text))
    css_like = any(token in text for token in ["font-family", "word-break", "line-height", "<style", "className=", "class="])

    if not has_korean:
        warnings.append("No Hangul text detected; Korean typography checks are advisory only.")
        return failures, warnings

    if not css_like:
        failures.append("Korean content found but no detectable CSS/typography rules were present.")
        return failures, warnings

    if "word-break: keep-all" not in text and "wordBreak: 'keep-all'" not in text and 'wordBreak: "keep-all"' not in text:
        failures.append("Missing Korean-safe `word-break: keep-all`.")
    if "overflow-wrap" not in text and "overflowWrap" not in text:
        failures.append("Missing `overflow-wrap` fallback to avoid long-token overflow.")
    if not has_any(text, KOREAN_FONT_MARKERS):
        failures.append("No known Korean-capable font marker found in font stack.")
    if re.search(r"code|pre|kbd|samp|terminal|cli", text, re.I):
        if not has_any(text, ["NanumGothicCoding", "ui-monospace", "SFMono", "Consolas", "monospace"]):
            failures.append("Code/terminal context detected but no code font fallback was found.")
        if "overflow-wrap: anywhere" not in text and "overflowWrap: 'anywhere'" not in text and 'overflowWrap: "anywhere"' not in text:
            warnings.append("Code/terminal context should usually use `overflow-wrap: anywhere`.")
    families = normalized_font_families(text)
    non_system = {f for f in families if not any(s in f.lower() for s in ["var(", "system-ui", "sans-serif", "serif", "monospace"])}
    if len(non_system) > 4:
        warnings.append(f"Many distinct font-family declarations detected ({len(non_system)}): {sorted(non_system)}")
    if re.search(r"letter-spacing\\s*:\\s*-?0\\.0[4-9]em", text):
        warnings.append("Aggressive negative letter-spacing detected; Hangul body text may look cramped.")
    return failures, warnings


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate Korean typography CSS hygiene.")
    parser.add_argument("paths", nargs="*", help="Files or directories to scan; use - for stdin")
    parser.add_argument("--json", action="store_true", help="Emit JSON")
    args = parser.parse_args()

    inputs = read_inputs(args.paths)
    results = []
    total_failures: list[str] = []
    for name, text in inputs.items():
        failures, warnings = evaluate(text)
        total_failures.extend(f"{name}: {f}" for f in failures)
        results.append({"path": name, "passed": not failures, "failures": failures, "warnings": warnings})

    payload = {"passed": not total_failures, "results": results}
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print("PASS" if payload["passed"] else "FAIL")
        for item in results:
            print(f"\
## {item['path']}")
            for failure in item["failures"]:
                print(f"FAIL: {failure}")
            for warning in item["warnings"]:
                print(f"WARN: {warning}")
    return 0 if payload["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
