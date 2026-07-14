#!/usr/bin/env python3
"""Grade Korean natural-writing outputs with deterministic and critic gates."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import re
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
ANALYZER_PATH = (
    ROOT
    / ".claude"
    / "skills"
    / "korean-natural-writing"
    / "scripts"
    / "analyze_korean_style.py"
)


def load_analyzer():
    spec = importlib.util.spec_from_file_location("korean_style_analyzer", ANALYZER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load analyzer: {ANALYZER_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ANALYZER = load_analyzer()
AXES = (
    "naturalness",
    "genre_register_fit",
    "voice_specificity",
    "discourse_rhythm",
    "editing_restraint",
)
WEIGHTS = {
    "naturalness": 0.25,
    "genre_register_fit": 0.20,
    "voice_specificity": 0.20,
    "discourse_rhythm": 0.20,
    "editing_restraint": 0.15,
}
SEMANTIC_AXIS_PATTERN = re.compile(r"^[a-z][a-z0-9_]{1,63}$")


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def canonical_json_sha256(value: Any) -> str:
    payload = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def text_sha256(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def extract_candidate(text: str) -> tuple[str, list[str]]:
    errors: list[str] = []
    start = re.search(r"(?m)^## 완성본[ \t]*$", text)
    if not start:
        return "", ["required output heading missing: ## 완성본"]
    body = text[start.end() :]
    notes = re.search(r"(?m)^## 다듬은 기준[ \t]*$", body)
    if not notes:
        next_heading = re.search(r"(?m)^##\s+", body)
        completion = body[: next_heading.start()].strip() if next_heading else body.strip()
        return completion, ["required output heading missing: ## 다듬은 기준"]

    completion = body[: notes.start()].strip()
    notes_body = body[notes.end() :]
    optional_section = re.search(r"(?m)^## 확인이 필요한 부분[ \t]*$", notes_body)
    if optional_section:
        notes_body = notes_body[: optional_section.start()]
    bullets = re.findall(r"(?m)^[ \t]*[-*][ \t]+\S.*$", notes_body)
    if not bullets:
        errors.append("## 다듬은 기준 must contain at least one bullet")
    if len(bullets) > 3:
        errors.append("## 다듬은 기준 must contain at most three bullets")
    return completion, errors


def hard_failure(reason: str, evidence: str = "E3") -> dict[str, Any]:
    return {"reason": reason, "evidence": [evidence]}


def validate_critic(critic: dict[str, Any], case: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    gate = critic.get("hard_gate")
    if not isinstance(gate, dict) or not isinstance(gate.get("passed"), bool):
        errors.append("critic hard_gate.passed must be boolean")
    else:
        failures = gate.get("failures")
        if not isinstance(failures, list) or not all(
            isinstance(item, str) and item.strip() for item in failures
        ):
            errors.append("critic hard_gate.failures must be a list of non-empty strings")
        elif gate["passed"] and failures:
            errors.append("critic hard_gate cannot pass with listed failures")
        elif not gate["passed"] and not failures:
            errors.append("critic failed hard gate must list at least one failure")
    gate_passed = isinstance(gate, dict) and gate.get("passed") is True
    scores = critic.get("scores")
    if gate_passed and not isinstance(scores, dict):
        errors.append("critic scores must be an object after the hard gate passes")
    elif scores is not None and not isinstance(scores, dict):
        errors.append("critic scores must be an object when provided")
    elif isinstance(scores, dict) and (gate_passed or scores):
        for axis in AXES:
            score = scores.get(axis)
            if (
                isinstance(score, bool)
                or not isinstance(score, (int, float))
                or not math.isfinite(float(score))
                or not 1 <= score <= 5
            ):
                errors.append(f"critic score {axis} must be between 1 and 5")
    findings = critic.get("findings")
    if not isinstance(findings, list) or not findings:
        errors.append("critic findings must contain at least one cited observation")
    else:
        allowed_axes = set(AXES) | {"meaning_preservation"}
        for index, finding in enumerate(findings):
            if not isinstance(finding, dict):
                errors.append(f"critic finding {index} must be an object")
                continue
            for field in ("excerpt", "axis", "impact", "edit_intent"):
                if not isinstance(finding.get(field), str) or not finding[field].strip():
                    errors.append(f"critic finding {index}.{field} must be a non-empty string")
            if finding.get("axis") not in allowed_axes:
                errors.append(f"critic finding {index}.axis is not recognized")
        cited_axes = {
            finding.get("axis")
            for finding in findings
            if isinstance(finding, dict)
        }
        if gate_passed:
            for axis in AXES:
                if axis not in cited_axes:
                    errors.append(f"critic findings must cite the {axis} score")
        elif "meaning_preservation" not in cited_axes:
            errors.append(
                "critic findings must cite meaning_preservation when the hard gate fails"
            )

    required_meaning = case.get("required_meaning", [])
    coverage = critic.get("required_meaning_coverage")
    unfulfilled_contract_items = 0
    if not isinstance(coverage, list):
        errors.append("critic required_meaning_coverage must be a list")
    elif not isinstance(required_meaning, list) or not all(
        isinstance(item, str) and item.strip() for item in required_meaning
    ):
        errors.append("case required_meaning must be a list of non-empty strings")
    else:
        if len(coverage) != len(required_meaning):
            errors.append(
                "critic required_meaning_coverage must contain one item per case requirement"
            )
        for index, expected in enumerate(required_meaning):
            if index >= len(coverage) or not isinstance(coverage[index], dict):
                continue
            item = coverage[index]
            if item.get("requirement") != expected:
                errors.append(
                    f"critic required_meaning_coverage {index}.requirement must exactly match the case"
                )
            if not isinstance(item.get("passed"), bool):
                errors.append(
                    f"critic required_meaning_coverage {index}.passed must be boolean"
                )
            elif not item["passed"]:
                unfulfilled_contract_items += 1
            if not isinstance(item.get("evidence"), str) or not item["evidence"].strip():
                errors.append(
                    f"critic required_meaning_coverage {index}.evidence must be a non-empty string"
                )

    expected_contract_checks = {
        "task": case.get("task"),
        "genre": case.get("genre"),
        "register": case.get("constraints", {}).get("register"),
    }
    relevant_contract_checks = {
        key: value
        for key, value in expected_contract_checks.items()
        if isinstance(value, str) and value.strip()
    }
    contract_checks = critic.get("contract_checks")
    if relevant_contract_checks and not isinstance(contract_checks, dict):
        errors.append("critic contract_checks must be an object")
    elif isinstance(contract_checks, dict):
        for key in relevant_contract_checks:
            item = contract_checks.get(key)
            if not isinstance(item, dict):
                errors.append(f"critic contract_checks.{key} must be an object")
                continue
            if not isinstance(item.get("passed"), bool):
                errors.append(f"critic contract_checks.{key}.passed must be boolean")
            elif not item["passed"]:
                unfulfilled_contract_items += 1
            if not isinstance(item.get("evidence"), str) or not item["evidence"].strip():
                errors.append(
                    f"critic contract_checks.{key}.evidence must be a non-empty string"
                )
    semantic_deltas = critic.get("semantic_deltas")
    if not isinstance(semantic_deltas, list):
        errors.append("critic semantic_deltas must be a list")
    else:
        unlicensed_count = 0
        for index, delta in enumerate(semantic_deltas):
            if not isinstance(delta, dict):
                errors.append(f"critic semantic_delta {index} must be an object")
                continue
            for field in ("source_excerpt", "candidate_excerpt", "axis", "reason"):
                if not isinstance(delta.get(field), str) or not delta[field].strip():
                    errors.append(
                        f"critic semantic_delta {index}.{field} must be a non-empty string"
                    )
            delta_axis = delta.get("axis")
            if (
                not isinstance(delta_axis, str)
                or not SEMANTIC_AXIS_PATTERN.fullmatch(delta_axis)
                or delta_axis in AXES
            ):
                errors.append(
                    f"critic semantic_delta {index}.axis must be a snake_case semantic dimension, not a quality score axis"
                )
            if not isinstance(delta.get("licensed"), bool):
                errors.append(f"critic semantic_delta {index}.licensed must be boolean")
            elif not delta["licensed"]:
                unlicensed_count += 1
        if isinstance(gate, dict) and isinstance(gate.get("passed"), bool):
            if gate["passed"] and unlicensed_count:
                errors.append("critic hard gate cannot pass with an unlicensed semantic delta")
            if gate["passed"] and unfulfilled_contract_items:
                errors.append(
                    "critic hard gate cannot pass with an unfulfilled meaning or contract check"
                )
    verdict = critic.get("verdict")
    if verdict not in {"pass", "fail", "needs_human_review"}:
        errors.append("critic verdict must be pass, fail, or needs_human_review")
    confidence = critic.get("confidence")
    if (
        isinstance(confidence, bool)
        or not isinstance(confidence, (int, float))
        or not math.isfinite(float(confidence))
        or not 0 <= confidence <= 1
    ):
        errors.append("critic confidence must be a number between 0 and 1")
    return errors


def grade(case: dict[str, Any], candidate_text: str, critic: dict[str, Any] | None, candidate_source: str) -> dict[str, Any]:
    completion, format_errors = extract_candidate(candidate_text)
    constraints = case.get("constraints", {})
    required_tokens = constraints.get("required_tokens", [])
    exact_tokens = constraints.get("exact_tokens", [])
    ignored_categories = constraints.get("mutable_fixed_categories", [])
    forbidden_tokens = constraints.get("forbidden_tokens", [])
    hard_failures: list[dict[str, Any]] = []
    hard_failures.extend(hard_failure(error, "E2") for error in format_errors)

    for token in required_tokens:
        if ANALYZER.literal_occurrence_count(completion, token) == 0:
            hard_failures.append(hard_failure(f"required token missing: {token}"))
    for token in forbidden_tokens:
        if ANALYZER.literal_occurrence_count(completion, token) > 0:
            hard_failures.append(hard_failure(f"forbidden unsupported token present: {token}"))

    length = len(re.sub(r"\s+", "", completion))
    minimum = constraints.get("min_chars")
    maximum = constraints.get("max_chars")
    if isinstance(minimum, int) and length < minimum:
        hard_failures.append(hard_failure(f"completion too short: {length} < {minimum}"))
    if isinstance(maximum, int) and length > maximum:
        hard_failures.append(hard_failure(f"completion too long: {length} > {maximum}"))

    style_report = ANALYZER.build_report(
        completion,
        source=candidate_source,
        original=case["input"],
        protected=exact_tokens,
        ignored_categories=ignored_categories,
    )
    invariant = style_report["invariant_comparison"]
    if not invariant["passed"]:
        hard_failures.append(
            hard_failure(
                "fixed-token invariant drift: "
                + json.dumps(
                    {
                        "missing": invariant["missing"],
                        "added": invariant["added"],
                    },
                    ensure_ascii=False,
                )
            )
        )

    critic_errors: list[str] = []
    if critic is not None:
        critic_errors = validate_critic(critic, case)
        if not critic_errors:
            for index, finding in enumerate(critic["findings"]):
                if finding["excerpt"] not in completion:
                    critic_errors.append(
                        f"critic finding {index}.excerpt must appear verbatim in the candidate completion"
                    )
            for index, delta in enumerate(critic["semantic_deltas"]):
                if delta["source_excerpt"] not in case["input"]:
                    critic_errors.append(
                        f"critic semantic_delta {index}.source_excerpt must appear verbatim in the source"
                    )
                if delta["candidate_excerpt"] not in completion:
                    critic_errors.append(
                        f"critic semantic_delta {index}.candidate_excerpt must appear verbatim in the candidate completion"
                    )
            for index, item in enumerate(critic["required_meaning_coverage"]):
                if item["passed"] and item["evidence"] not in completion:
                    critic_errors.append(
                        f"critic required_meaning_coverage {index}.evidence must appear verbatim in the candidate completion"
                    )
            for key, item in critic.get("contract_checks", {}).items():
                if item["passed"] and item["evidence"] not in completion:
                    critic_errors.append(
                        f"critic contract_checks.{key}.evidence must appear verbatim in the candidate completion"
                    )
        for error in critic_errors:
            hard_failures.append(hard_failure(error, "E4"))
        if not critic_errors and not critic["hard_gate"]["passed"]:
            critic_failures = critic["hard_gate"].get("failures") or ["critic semantic hard gate failed"]
            for failure in critic_failures:
                hard_failures.append(hard_failure(str(failure), "E4"))

    score_payload: dict[str, Any] = {}
    weighted_score = 0.0
    if critic is not None and not critic_errors and critic["hard_gate"]["passed"]:
        for axis in AXES:
            score = float(critic["scores"][axis])
            weighted_score += score * WEIGHTS[axis]
            score_payload[axis] = {
                "score": score,
                "max": 5,
                "weight": WEIGHTS[axis],
                "evidence": ["E4"],
                "rationale": "See independent critic findings for cited excerpts.",
            }

    missing_evidence: list[str] = []
    if critic is None:
        missing_evidence.append("independent Korean naturalness and genre-register critique")
    elif critic_errors:
        missing_evidence.append("valid independent critic evidence")

    if hard_failures:
        status = "fail"
    elif critic is None:
        status = "needs_review"
    elif critic["verdict"] == "needs_human_review":
        status = "needs_review"
    else:
        scores = critic["scores"]
        passed_axes = (
            scores["naturalness"] >= 4
            and scores["genre_register_fit"] >= 4
            and scores["discourse_rhythm"] >= 4
            and scores["voice_specificity"] >= 3
            and scores["editing_restraint"] >= 3
        )
        status = "pass" if critic["verdict"] == "pass" and passed_axes else "fail"

    confidence = (
        0.45
        if critic is None
        else float(critic["confidence"])
        if not critic_errors
        else 0.0
    )
    summary = (
        "Deterministic meaning-preservation gate failed."
        if hard_failures
        else "Deterministic gate passed; independent language review is still required."
        if critic is None
        else f"Deterministic and independent critic result: {status}."
    )
    return {
        "schema": "evaluation-result-v1",
        "rubric": "korean-natural-writing",
        "case_id": case["id"],
        "artifact_provenance": {
            "case_sha256": canonical_json_sha256(case),
            "candidate_sha256": text_sha256(candidate_text),
            "critic_sha256": canonical_json_sha256(critic) if critic is not None else None,
        },
        "evidence_packet": {
            "source_coverage": "complete" if critic is not None and not critic_errors else "partial",
            "included_signals": [
                {
                    "id": "E1",
                    "source": "case JSON",
                    "summary": "Original text, genre, reader, task, and protected constraints.",
                    "supports": ["meaning_preservation", "genre_register_fit"],
                },
                {
                    "id": "E2",
                    "source": candidate_source,
                    "summary": "Candidate completion after excluding edit notes.",
                    "supports": list(AXES),
                },
                {
                    "id": "E3",
                    "source": str(ANALYZER_PATH.relative_to(ROOT)),
                    "summary": f"Fixed-token comparison and {len(style_report['style_flags'])} advisory style signals.",
                    "supports": ["meaning_preservation", "mechanical_style_review"],
                },
            ]
            + (
                [
                    {
                        "id": "E4",
                        "source": "independent critic JSON",
                        "summary": "Pointwise Korean writing scores and cited findings.",
                        "supports": list(AXES),
                    }
                ]
                if critic is not None and not critic_errors
                else []
            ),
            "excluded_signals": [
                {"signal": "model or skill identity", "reason": "prestige"},
                {"signal": "AI detector score", "reason": "unsupported"},
                {"signal": "verbosity by itself", "reason": "out_of_scope"},
            ],
            "missing_evidence": missing_evidence,
        },
        "scores": score_payload,
        "adjustments": {"bonus": [], "deductions": [], "hard_failures": hard_failures},
        "deterministic": {
            "completion_characters_without_space": length,
            "invariants": invariant,
            "style_flags": style_report["style_flags"],
        },
        "independent_critic": critic,
        "result": {
            "weighted_score": round(weighted_score, 3),
            "adjusted_score": round(weighted_score, 3),
            "status": status,
            "confidence": confidence,
            "summary": summary,
        },
    }


def self_test() -> int:
    case = {
        "id": "self-test",
        "input": "7월 31일까지 `plan_id`는 변경되지 않습니다. https://example.com",
        "task": "날짜와 식별자를 보존해 안내문을 다듬어라.",
        "genre": "work-technical",
        "required_meaning": ["7월 31일까지 plan_id가 바뀌지 않는다"],
        "constraints": {
            "register": "hamnida",
            "required_tokens": ["plan_id"],
            "min_chars": 10,
            "max_chars": 120,
        },
    }
    passing = grade(
        case,
        "## 완성본\n7월 31일까지 `plan_id`는 바뀌지 않습니다. https://example.com\n\n## 다듬은 기준\n- 호흡 조정",
        None,
        "self-test-pass",
    )
    assert passing["result"]["status"] == "needs_review"
    failing = grade(case, "8월 1일부터 plan은 바뀝니다.", None, "self-test-fail")
    assert failing["result"]["status"] == "fail"
    critic = {
        "hard_gate": {"passed": True, "failures": []},
        "scores": {axis: 5 for axis in AXES},
        "findings": [
            {
                "excerpt": "7월 31일까지",
                "axis": axis,
                "impact": f"{axis} 점수의 실제 후보 근거",
                "edit_intent": "현재 표현 유지",
            }
            for axis in AXES
        ],
        "required_meaning_coverage": [
            {
                "requirement": "7월 31일까지 plan_id가 바뀌지 않는다",
                "passed": True,
                "evidence": "7월 31일까지 `plan_id`는 바뀌지 않습니다",
            }
        ],
        "contract_checks": {
            key: {
                "passed": True,
                "evidence": "7월 31일까지 `plan_id`는 바뀌지 않습니다",
            }
            for key in ("task", "genre", "register")
        },
        "semantic_deltas": [],
        "verdict": "pass",
        "confidence": 0.9,
    }
    valid_critic = grade(
        case,
        "## 완성본\n7월 31일까지 `plan_id`는 바뀌지 않습니다. https://example.com\n\n## 다듬은 기준\n- 의미 보존",
        critic,
        "self-test-valid-critic",
    )
    assert valid_critic["result"]["status"] == "pass", json.dumps(
        valid_critic["adjustments"], ensure_ascii=False
    )
    assert valid_critic["artifact_provenance"]["critic_sha256"] == canonical_json_sha256(
        critic
    )
    substring_token = grade(
        {
            "id": "self-test-token-boundary",
            "input": "AI를 사용합니다.",
            "constraints": {"required_tokens": ["AI"]},
        },
        "## 완성본\nKAIST를 사용합니다.\n\n## 다듬은 기준\n- 표현 유지",
        None,
        "self-test-token-boundary",
    )
    assert substring_token["result"]["status"] == "fail"
    assert any(
        "required token missing: AI" in item["reason"]
        for item in substring_token["adjustments"]["hard_failures"]
    )
    failed_critic = {
        "hard_gate": {"passed": False, "failures": ["필수 의미가 빠졌다."]},
        "scores": {},
        "findings": [
            {
                "excerpt": "바뀌지 않습니다",
                "axis": "meaning_preservation",
                "impact": "필수 의미 검토가 필요하다.",
                "edit_intent": "원문의 조건을 복원한다.",
            }
        ],
        "required_meaning_coverage": [
            {
                "requirement": "7월 31일까지 plan_id가 바뀌지 않는다",
                "passed": False,
                "evidence": "바뀌지 않습니다",
            }
        ],
        "contract_checks": {
            "task": {"passed": False, "evidence": "바뀌지 않습니다"},
            "genre": {"passed": True, "evidence": "바뀌지 않습니다"},
            "register": {"passed": True, "evidence": "바뀌지 않습니다"},
        },
        "semantic_deltas": [],
        "verdict": "fail",
        "confidence": 0.9,
    }
    valid_gate_failure = grade(
        case,
        "## 완성본\n7월 31일까지 `plan_id`는 바뀌지 않습니다. https://example.com\n\n## 다듬은 기준\n- 의미 검토",
        failed_critic,
        "self-test-valid-gate-failure",
    )
    assert valid_gate_failure["result"]["status"] == "fail"
    assert valid_gate_failure["scores"] == {}
    assert valid_gate_failure["evidence_packet"]["source_coverage"] == "complete"
    critic["hard_gate"] = {"passed": False, "failures": []}
    critic_gate_failure = grade(
        case,
        "7월 31일까지 `plan_id`는 바뀌지 않습니다. https://example.com",
        critic,
        "self-test-critic-gate",
    )
    assert critic_gate_failure["result"]["status"] == "fail"
    assert any(
        "failed hard gate must list" in item["reason"]
        for item in critic_gate_failure["adjustments"]["hard_failures"]
    )
    critic["hard_gate"] = {"passed": True, "failures": []}
    critic["findings"][0]["excerpt"] = "후보에 없는 인용"
    fabricated_excerpt = grade(
        case,
        "7월 31일까지 `plan_id`는 바뀌지 않습니다. https://example.com",
        critic,
        "self-test-fabricated-excerpt",
    )
    assert fabricated_excerpt["result"]["status"] == "fail"
    assert any(
        "must appear verbatim" in item["reason"]
        for item in fabricated_excerpt["adjustments"]["hard_failures"]
    )
    critic["findings"][0]["excerpt"] = "7월 31일까지"
    critic["semantic_deltas"] = [
        {
            "source_excerpt": "변경되지 않습니다",
            "candidate_excerpt": "바뀌지 않습니다",
            "axis": "modality",
            "licensed": False,
            "reason": "검토용 미허용 변화",
        }
    ]
    unlicensed_delta = grade(
        case,
        "7월 31일까지 `plan_id`는 바뀌지 않습니다. https://example.com",
        critic,
        "self-test-unlicensed-delta",
    )
    assert unlicensed_delta["result"]["status"] == "fail"
    assert any(
        "cannot pass with an unlicensed" in item["reason"]
        for item in unlicensed_delta["adjustments"]["hard_failures"]
    )
    critic["semantic_deltas"] = []
    critic["confidence"] = "medium"
    invalid_confidence = grade(
        case,
        "7월 31일까지 `plan_id`는 바뀌지 않습니다. https://example.com",
        critic,
        "self-test-invalid-confidence",
    )
    assert invalid_confidence["result"]["status"] == "fail"
    assert invalid_confidence["result"]["confidence"] == 0.0
    critic["confidence"] = 0.9
    critic["semantic_deltas"] = [
        {
            "source_excerpt": "변경되지 않습니다",
            "candidate_excerpt": "바뀌지 않습니다",
            "axis": "naturalness",
            "licensed": True,
            "reason": "품질 축을 의미 변화 축으로 잘못 사용한 검토용 입력",
        }
    ]
    invalid_semantic_axis = grade(
        case,
        "7월 31일까지 `plan_id`는 바뀌지 않습니다. https://example.com",
        critic,
        "self-test-invalid-semantic-axis",
    )
    assert invalid_semantic_axis["result"]["status"] == "fail"
    assert any(
        "snake_case semantic dimension" in item["reason"]
        for item in invalid_semantic_axis["adjustments"]["hard_failures"]
    )
    leaked_notes = grade(
        {
            "id": "self-test-heading",
            "input": "모아는 AI 일정 관리 서비스입니다.",
            "constraints": {"required_tokens": ["모아", "AI"]},
        },
        "일정을 관리합니다.\n\n## 다듬은 기준\n- 모아와 AI를 보존",
        None,
        "self-test-heading",
    )
    assert leaked_notes["result"]["status"] == "fail"
    print("PASS")
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case", type=Path)
    parser.add_argument("--candidate", type=Path)
    parser.add_argument("--critic", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--self-test", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.self_test:
        return self_test()
    if not args.case or not args.candidate:
        raise SystemExit("--case and --candidate are required")
    case = read_json(args.case)
    candidate = args.candidate.read_text(encoding="utf-8")
    critic = read_json(args.critic) if args.critic else None
    result = grade(case, candidate, critic, str(args.candidate))
    payload = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload, encoding="utf-8")
    else:
        sys.stdout.write(payload)
    if result["result"]["status"] == "pass":
        return 0
    if result["result"]["status"] == "needs_review":
        return 2
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
