#!/usr/bin/env python3
"""Report Korean writing-pattern signals and preserved-token drift.

The style signals are advisory. Only invariant drift can fail the command when
--strict-invariants is set.
"""

from __future__ import annotations

import argparse
import json
import re
import statistics
import sys
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


SCHEMA_VERSION = "korean-natural-writing.style-report.v1"


@dataclass(frozen=True)
class Marker:
    marker_id: str
    category: str
    pattern: re.Pattern[str]
    min_count: int = 1


MARKERS = (
    Marker(
        "generic_opening",
        "discourse",
        re.compile(r"오늘날|현대\s*사회(?:에서|는)?|빠르게\s*변화하는|디지털\s*시대|이\s*여정에서"),
    ),
    Marker(
        "inflated_abstraction",
        "abstraction",
        re.compile(
            r"새로운\s*가능성|중요한\s*역할|깊은\s*(?:의미|울림)|진정한\s*가치|"
            r"특별한\s*경험|완벽한\s*솔루션|혁신적인\s*접근|따뜻한\s*여운|한\s*단계\s*더\s*성장"
        ),
    ),
    Marker(
        "formulaic_contrast",
        "abstraction",
        re.compile(r"단순히.{0,40}(?:넘어|그치지\s*않고)|.{0,30}에\s*그치지\s*않고"),
    ),
    Marker(
        "unearned_certainty",
        "evidence",
        re.compile(r"주목할\s*필요가\s*있다|중요하다고\s*할\s*수\s*있다|필수적이다|분명하다"),
    ),
    Marker(
        "preposition_calque",
        "translationese",
        re.compile(
            r"에\s*대(?:한|하여)|에\s*관하여|에\s*있어(?:서)?|의\s*측면에서|"
            r"[을를]\s*통해|로부터|에\s*의해"
        ),
        min_count=2,
    ),
    Marker(
        "opaque_passive",
        "translationese",
        re.compile(r"되어지|하게\s*되(?:었|었다|었습니다|어)|(?:진행|결정|고려)되(?:었|었다|었습니다)"),
        min_count=2,
    ),
    Marker(
        "explicit_pronoun",
        "translationese",
        re.compile(r"(?:그것|그들|이것은|저것은)(?:이|은|는|을|를|의|도|과|와)?"),
        min_count=3,
    ),
    Marker(
        "empty_nominal_verb",
        "translationese",
        re.compile(r"(?:진행|수행|제공|활용|강화|제고)(?:을|를)?\s*(?:하|했|한다|합니다|하였다)"),
        min_count=3,
    ),
    Marker(
        "delayed_assertion",
        "translationese",
        re.compile(r"(?:하는|인)\s*것이다|라고\s*할\s*수\s*있다"),
        min_count=3,
    ),
    Marker(
        "connector_scaffold",
        "rhythm",
        re.compile(r"이를\s*통해|그\s*결과|궁극적으로|또한|특히|이러한"),
        min_count=4,
    ),
    Marker(
        "generic_cta",
        "copy",
        re.compile(r"지금\s*바로|놓치지\s*마세요|놀라운|혁신적인|완벽한"),
        min_count=2,
    ),
    Marker(
        "forced_emotion",
        "story",
        re.compile(r"깊은\s*울림|따뜻한\s*여운|진정한\s*의미|가슴\s*깊이|잊지\s*못할"),
        min_count=2,
    ),
)


REGISTER_PATTERNS = {
    "hamnida": re.compile(r"(?:습니다|니다)$"),
    "haeyo": re.compile(r"[가-힣]+요$"),
    "handa": re.compile(r"[가-힣]+다$"),
    "nominal": re.compile(r"(?:함|임|됨|완료|필요)$"),
}


FIXED_TOKEN_PATTERNS = {
    "code_block": re.compile(r"```[^\n]*\n.*?```", re.DOTALL),
    "inline_code": re.compile(r"`([^`\n]+)`"),
    # Capture Unicode IRI paths as well as ASCII URLs. normalize_url separates
    # a bare-domain Korean particle such as ``https://example.com에서``.
    "url": re.compile(r"https?://[^\s<>{}\"'`]+"),
    "email": re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"),
    "version": re.compile(
        r"(?<![A-Za-z0-9_])v\d+(?:\.\d+)+(?:[-+][A-Za-z0-9.-]+)?"
        r"(?![A-Za-z0-9._+-])",
        re.IGNORECASE,
    ),
    "currency": re.compile(
        r"(?<![\w])(?:[$€£¥₩]\s*\d[\d,]*(?:\.\d+)?|"
        r"\d[\d,]*(?:\.\d+)?\s*(?:USD|KRW|EUR|JPY|CNY|GBP)(?![A-Za-z]))",
        re.IGNORECASE,
    ),
    "number": re.compile(
        r"(?<![\w])[-+]?\d[\d,]*(?:\.\d+)?"
        r"(?:\s*(?:%|퍼센트|배|만원|억원|개월|시간|원|개|명|건|회|일|주|년|월|시|초|분|"
        r"°C|°F|KiB|MiB|GiB|TiB|KB|MB|GB|TB|ms|kg|km|cm|mm|px|fps|kHz|MHz|GHz|Hz|s|g|m)"
        r")?"
    ),
    "quotation": re.compile(
        r'"([^"\n]{1,})"|“([^”\n]{1,})”|‘([^’\n]{1,})’|\'([^\'\n]{1,})\''
    ),
}


NEGATION_PATTERN = re.compile(r"않(?:다|는다|았다|았다|습니다)?|아니(?:다|며|고)?|없(?:다|는|었다|습니다)?|못\s*\w+|불가|금지")
KOREAN_URL_PARTICLES = (
    "으로부터",
    "에게서",
    "에서는",
    "으로",
    "에게",
    "부터",
    "까지",
    "에서",
    "로",
    "은",
    "는",
    "이",
    "가",
    "을",
    "를",
    "와",
    "과",
    "에",
    "도",
    "의",
)


def read_text(path_value: str) -> str:
    if path_value == "-":
        return sys.stdin.read()
    return Path(path_value).read_text(encoding="utf-8")


def line_number(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


def compact_excerpt(text: str, start: int, end: int, radius: int = 42) -> str:
    left = max(0, start - radius)
    right = min(len(text), end + radius)
    excerpt = re.sub(r"\s+", " ", text[left:right]).strip()
    return excerpt[:120]


def sentences(text: str) -> list[str]:
    without_code = FIXED_TOKEN_PATTERNS["code_block"].sub(" ", text)
    parts = re.split(r"(?<=[.!?。！？])\s+|\n+", without_code)
    return [part.strip() for part in parts if re.search(r"[가-힣A-Za-z0-9]", part)]


def eojeol_count(text: str) -> int:
    return len(re.findall(r"[가-힣A-Za-z0-9_./%+-]+", text))


def sentence_metrics(items: list[str]) -> dict[str, object]:
    lengths = [eojeol_count(item) for item in items]
    mean = statistics.fmean(lengths) if lengths else 0.0
    stdev = statistics.pstdev(lengths) if len(lengths) > 1 else 0.0
    return {
        "sentence_count": len(items),
        "average_eojeol": round(mean, 2),
        "sentence_eojeol_stdev": round(stdev, 2),
        "length_coefficient_of_variation": round(stdev / mean, 3) if mean else 0.0,
        "shortest_eojeol": min(lengths, default=0),
        "longest_eojeol": max(lengths, default=0),
    }


def ending_register(sentence: str) -> str | None:
    cleaned = re.sub(r"[\s.!?。！？”’\")\]]+$", "", sentence)
    last = cleaned.split()[-1] if cleaned.split() else ""
    for name, pattern in REGISTER_PATTERNS.items():
        if pattern.search(last):
            return name
    return None


def register_metrics(items: list[str]) -> dict[str, object]:
    counts = Counter(filter(None, (ending_register(item) for item in items)))
    classified = sum(counts.values())
    dominant = counts.most_common(1)[0] if counts else (None, 0)
    mixed = len([count for count in counts.values() if count >= 2]) >= 2
    return {
        "counts": dict(sorted(counts.items())),
        "classified_sentences": classified,
        "dominant": dominant[0],
        "dominant_ratio": round(dominant[1] / classified, 3) if classified else 0.0,
        "mixed_register_review": mixed,
    }


def repeated_openers(items: list[str]) -> list[dict[str, object]]:
    openers: Counter[str] = Counter()
    for item in items:
        tokens = re.findall(r"[가-힣A-Za-z0-9]+", item)
        if tokens:
            openers[tokens[0]] += 1
    return [
        {"opener": opener, "count": count}
        for opener, count in openers.most_common()
        if count >= 3
    ]


def style_flags(text: str, items: list[str]) -> list[dict[str, object]]:
    flags: list[dict[str, object]] = []
    for marker in MARKERS:
        matches = list(marker.pattern.finditer(text))
        if len(matches) < marker.min_count:
            continue
        flags.append(
            {
                "id": marker.marker_id,
                "category": marker.category,
                "count": len(matches),
                "examples": [
                    {
                        "line": line_number(text, match.start()),
                        "match": match.group(0),
                        "excerpt": compact_excerpt(text, match.start(), match.end()),
                    }
                    for match in matches[:3]
                ],
                "advisory": True,
            }
        )

    registers = register_metrics(items)
    if registers["mixed_register_review"]:
        flags.append(
            {
                "id": "mixed_register",
                "category": "register",
                "count": sum(registers["counts"].values()),
                "examples": [],
                "advisory": True,
            }
        )

    metrics = sentence_metrics(items)
    if metrics["sentence_count"] >= 5 and metrics["length_coefficient_of_variation"] < 0.18:
        flags.append(
            {
                "id": "uniform_sentence_length",
                "category": "rhythm",
                "count": metrics["sentence_count"],
                "examples": [],
                "advisory": True,
            }
        )
    return flags


def normalize_url(value: str) -> str:
    normalized = value.rstrip(".,!?;:。！？…\"'”’")
    pairs = (("(", ")"), ("[", "]"), ("{", "}"))
    for opening, closing in pairs:
        while normalized.endswith(closing) and normalized.count(closing) > normalized.count(opening):
            normalized = normalized[:-1]
    # Korean particles are commonly attached to an IRI without whitespace.
    # Treat a terminal particle as surrounding prose for both Unicode hosts and
    # paths. This is a preservation policy, not a URL-validity parser.
    for particle in KOREAN_URL_PARTICLES:
        if not normalized.endswith(particle):
            continue
        candidate = normalized[: -len(particle)]
        if re.fullmatch(r"https?://[^\s<>{}\"'`]+", candidate):
            normalized = candidate
            break
    return normalized


def normalize_fixed(value: str, category: str) -> str:
    if category in {"code_block", "inline_code"}:
        return value.replace("\r\n", "\n").strip("\n")
    if category == "url":
        return normalize_url(value)
    if category in {"currency", "number"}:
        return re.sub(r"\s+", "", value)
    return re.sub(r"\s+", " ", value).strip()


def literal_occurrence_count(text: str, value: str) -> int:
    """Count protected ASCII identifiers without accepting substrings."""
    if re.fullmatch(r"[A-Za-z0-9_./:+-]+", value) and re.search(
        r"[A-Za-z0-9_]", value
    ):
        return len(re.findall(rf"(?<![A-Za-z0-9_]){re.escape(value)}(?![A-Za-z0-9_])", text))
    return text.count(value)


def extract_fixed_tokens(text: str, protected: Iterable[str] = ()) -> dict[str, Counter[str]]:
    result: dict[str, Counter[str]] = {}
    for name, pattern in FIXED_TOKEN_PATTERNS.items():
        values = [
            normalize_fixed(
                next((group for group in match.groups() if group is not None), match.group(0)),
                name,
            )
            for match in pattern.finditer(text)
        ]
        result[name] = Counter(value for value in values if value)
    result["manual"] = Counter(
        {
            value: literal_occurrence_count(text, value)
            for value in protected
            if value and literal_occurrence_count(text, value) > 0
        }
    )
    return result


def counter_items(counter: Counter[str]) -> list[dict[str, object]]:
    return [
        {"value": value, "count": count}
        for value, count in sorted(counter.items())
        if count > 0
    ]


def compare_invariants(
    original: str,
    revised: str,
    protected: Iterable[str],
    ignored_categories: Iterable[str] = (),
) -> dict[str, object]:
    before = extract_fixed_tokens(original, protected)
    after = extract_fixed_tokens(revised, protected)
    ignored = set(ignored_categories)
    missing: dict[str, list[dict[str, object]]] = {}
    added: dict[str, list[dict[str, object]]] = {}
    for category in before:
        if category in ignored:
            continue
        missing_values = before[category] - after.get(category, Counter())
        added_values = after.get(category, Counter()) - before[category]
        if missing_values:
            missing[category] = counter_items(missing_values)
        if added_values:
            added[category] = counter_items(added_values)

    original_negations = len(NEGATION_PATTERN.findall(original))
    revised_negations = len(NEGATION_PATTERN.findall(revised))
    warnings: list[dict[str, object]] = []
    if original_negations != revised_negations:
        warnings.append(
            {
                "id": "negation_count_changed",
                "original": original_negations,
                "revised": revised_negations,
                "note": "Review negation and modality manually; equivalent rewrites can change this count.",
            }
        )

    return {
        "passed": not missing and not added,
        "strict_passed": not missing and not added and not warnings,
        "missing": missing,
        "added": added,
        "warnings": warnings,
        "manual_semantic_review_required": True,
    }


def strict_exit_code(comparison: dict[str, object]) -> int:
    if not comparison["passed"]:
        return 1
    if comparison["warnings"]:
        return 2
    return 0


def build_report(
    text: str,
    *,
    source: str,
    original: str | None = None,
    protected: Iterable[str] = (),
    ignored_categories: Iterable[str] = (),
) -> dict[str, object]:
    sentence_items = sentences(text)
    metrics = {
        "characters": len(text),
        "eojeol": eojeol_count(text),
        **sentence_metrics(sentence_items),
        "register": register_metrics(sentence_items),
        "repeated_openers": repeated_openers(sentence_items),
    }
    flags = style_flags(text, sentence_items)
    comparison = (
        compare_invariants(original, text, protected, ignored_categories)
        if original is not None
        else None
    )
    status = "fail" if comparison and not comparison["passed"] else "review" if flags or (comparison and comparison["warnings"]) else "pass"
    return {
        "schema_version": SCHEMA_VERSION,
        "source": source,
        "status": status,
        "metrics": metrics,
        "style_flags": flags,
        "style_flags_are_advisory": True,
        "invariant_comparison": comparison,
    }


def markdown_report(report: dict[str, object]) -> str:
    metrics = report["metrics"]
    lines = [
        "# Korean Style Report",
        "",
        f"- Status: `{report['status']}`",
        f"- Sentences: {metrics['sentence_count']}",
        f"- Average eojeol: {metrics['average_eojeol']}",
        f"- Advisory flags: {len(report['style_flags'])}",
        "",
        "## Style signals",
        "",
    ]
    if report["style_flags"]:
        for flag in report["style_flags"]:
            lines.append(f"- `{flag['id']}` ({flag['category']}): {flag['count']}")
    else:
        lines.append("- None")
    comparison = report.get("invariant_comparison")
    if comparison is not None:
        lines.extend(
            [
                "",
                "## Invariant comparison",
                "",
                f"- Fixed tokens passed: `{str(comparison['passed']).lower()}`",
                f"- Strict pass: `{str(comparison['strict_passed']).lower()}`",
            ]
        )
        for key in ("missing", "added"):
            if comparison[key]:
                lines.append(f"- {key.title()}: `{json.dumps(comparison[key], ensure_ascii=False)}`")
        for warning in comparison["warnings"]:
            lines.append(f"- Warning `{warning['id']}`: {warning['note']}")
    return "\n".join(lines) + "\n"


def run_self_test() -> int:
    original = "Memoriz는 2026년 7월 14일 `deep_mode`를 공개하지 않습니다. https://example.com"
    preserved = "Memoriz는 2026년 7월 14일에도 `deep_mode`를 공개하지 않습니다. https://example.com"
    drifted = "Memoriz는 2026년 7월 15일 deep mode를 공개합니다."
    assert compare_invariants(original, preserved, ["Memoriz"])["passed"]
    particle_attached = preserved.replace("https://example.com", "https://example.com에서")
    assert compare_invariants(original, particle_attached, ["Memoriz"])["passed"]
    assert not compare_invariants(original, drifted, ["Memoriz"])["passed"]
    assert not compare_invariants(original, preserved.replace("Memoriz", "서비스"), ["Memoriz"])["passed"]
    quote_added = compare_invariants("분석 시작 버튼을 누릅니다.", '"분석 시작" 버튼을 누릅니다.', [])
    assert not quote_added["passed"]
    assert compare_invariants(
        "분석 시작 버튼을 누릅니다.",
        '"분석 시작" 버튼을 누릅니다.',
        [],
        ["quotation"],
    )["passed"]
    assert not compare_invariants("버튼을 누릅니다.", '"분석 시작"을 누릅니다.', [])["passed"]
    assert not compare_invariants('"분석 시작"을 누릅니다.', "버튼을 누릅니다.", [])["passed"]
    assert not compare_invariants("“예”라고 답했다.", "“아”라고 답했다.", [])["passed"]
    assert not compare_invariants("'예'라고 답했다.", "'아'라고 답했다.", [])["passed"]
    assert not compare_invariants("파일은 5GB입니다.", "파일은 5MB입니다.", [])["passed"]
    assert not compare_invariants("온도는 10°C입니다.", "온도는 10°F입니다.", [])["passed"]
    assert not compare_invariants("가격은 $10입니다.", "가격은 ₩10입니다.", [])["passed"]
    assert not compare_invariants("버전은 v1.2입니다.", "버전은 v2.2입니다.", [])["passed"]
    assert compare_invariants("주소는 https://example.com.", "주소는 https://example.com", [])["passed"]
    assert compare_invariants("[문서](https://example.com)", "문서: https://example.com", [])["passed"]
    assert compare_invariants(
        "문서는 https://예시.한국에 있습니다.",
        "문서는 https://예시.한국에서 확인합니다.",
        [],
    )["passed"]
    assert compare_invariants(
        "문서는 https://example.com/가이드에 있습니다.",
        "문서는 https://example.com/가이드에서 확인합니다.",
        [],
    )["passed"]
    assert not compare_invariants(
        "문서는 https://example.com/가이드에 있습니다.",
        "문서는 https://example.com/가격에 있습니다.",
        [],
    )["passed"]
    assert compare_invariants("가격은 $ 10입니다.", "가격은 $10입니다.", [])["passed"]
    assert compare_invariants("할인은 10 %입니다.", "할인은 10%입니다.", [])["passed"]
    assert compare_invariants("가격은 10 USD입니다.", "가격은 10USD입니다.", [])["passed"]
    assert not compare_invariants("AI를 사용합니다.", "KAIST를 사용합니다.", ["AI"])["passed"]
    assert not compare_invariants(
        "AI-plan을 사용합니다.",
        "XAI-planY를 사용합니다.",
        ["AI-plan"],
    )["passed"]
    code_before = "```python\nif ready:\n    run()\n```"
    code_after = "```python\nif ready:\nrun()\n```"
    assert not compare_invariants(code_before, code_after, [])["passed"]
    negation_drift = compare_invariants(
        "이 기능은 자동으로 실행되지 않습니다.",
        "이 기능은 자동으로 실행됩니다.",
        [],
    )
    assert negation_drift["passed"]
    assert not negation_drift["strict_passed"]
    assert strict_exit_code(negation_drift) == 2
    assert strict_exit_code(compare_invariants(original, drifted, ["Memoriz"])) == 1
    assert strict_exit_code(compare_invariants(original, preserved, ["Memoriz"])) == 0
    flagged = build_report(
        "오늘날 빠르게 변화하는 시대에 혁신적인 접근은 새로운 가능성을 엽니다. "
        "지금 바로 놀라운 경험을 놓치지 마세요.",
        source="self-test",
    )
    assert any(flag["id"] == "generic_opening" for flag in flagged["style_flags"])
    assert any(flag["id"] == "inflated_abstraction" for flag in flagged["style_flags"])
    print("PASS")
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", nargs="?", help="UTF-8 text file, or - for stdin")
    parser.add_argument("--original", help="Original file for invariant comparison")
    parser.add_argument("--protect", action="append", default=[], help="Exact token that must be preserved; repeatable")
    parser.add_argument(
        "--ignore-category",
        action="append",
        default=[],
        choices=tuple(FIXED_TOKEN_PATTERNS),
        help="Fixed-token category that may change; repeatable (for example, authored dialogue quotations)",
    )
    parser.add_argument("--strict-invariants", action="store_true", help="Exit 1 when fixed tokens are missing or added")
    parser.add_argument("--format", choices=("json", "markdown"), default="json")
    parser.add_argument("--self-test", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.self_test:
        return run_self_test()
    if not args.input:
        raise SystemExit("input is required unless --self-test is used")
    if args.strict_invariants and not args.original:
        raise SystemExit("--strict-invariants requires --original")
    text = read_text(args.input)
    original = read_text(args.original) if args.original else None
    report = build_report(
        text,
        source=args.input,
        original=original,
        protected=args.protect,
        ignored_categories=args.ignore_category,
    )
    if args.format == "markdown":
        sys.stdout.write(markdown_report(report))
    else:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    if args.strict_invariants and report["invariant_comparison"]:
        return strict_exit_code(report["invariant_comparison"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
