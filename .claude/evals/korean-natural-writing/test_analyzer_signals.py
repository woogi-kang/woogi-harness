#!/usr/bin/env python3
"""Run deterministic advisory-signal regression fixtures."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
ANALYZER_PATH = (
    ROOT
    / ".claude"
    / "skills"
    / "korean-natural-writing"
    / "scripts"
    / "analyze_korean_style.py"
)
FIXTURE_PATH = Path(__file__).with_name("fixtures") / "analyzer-signals.json"


def load_analyzer():
    spec = importlib.util.spec_from_file_location(
        "korean_style_analyzer_fixture_test",
        ANALYZER_PATH,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load analyzer: {ANALYZER_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def main() -> int:
    analyzer = load_analyzer()
    fixture = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    assert fixture["schema"] == "korean-natural-writing.analyzer-fixtures.v1"

    for case in fixture["cases"]:
        report = analyzer.build_report(
            case["text"],
            source=case["id"],
            genre=case["genre"],
        )
        assert report["schema_version"] == "korean-natural-writing.style-report.v2"
        assert report["authorship_inference_supported"] is False
        assert report["status"] == case.get(
            "expected_status", "review" if case["required_flags"] else "pass"
        )
        flags = {item["id"]: item for item in report["style_flags"]}
        for flag in flags.values():
            assert flag["advisory"] is True
            assert flag["signal_strength"] in {"high", "medium", "low"}
            assert flag["confidence"] in {"high", "medium", "low"}
            assert isinstance(flag["reader_harm"], str) and flag["reader_harm"]
            for example in flag["examples"]:
                assert 0 <= example["start"] < example["end"] <= len(case["text"])

        for marker_id in case["required_flags"]:
            assert marker_id in flags, f"{case['id']}: missing {marker_id}"
        for marker_id in case["forbidden_flags"]:
            assert marker_id not in flags, f"{case['id']}: unexpected {marker_id}"
        for marker_id, expected in case.get("expected_applicability", {}).items():
            assert (
                flags[marker_id]["applicable_to_requested_genre"] is expected
            ), f"{case['id']}: unexpected applicability for {marker_id}"

    print(f"PASS {len(fixture['cases'])} analyzer fixtures")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
