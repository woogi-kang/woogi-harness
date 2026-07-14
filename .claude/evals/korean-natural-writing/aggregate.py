#!/usr/bin/env python3
"""Aggregate the 12-case blind Korean writing comparison."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
import sys
from pathlib import Path
from typing import Any


AXES_REQUIRED_AT_FOUR = (
    "naturalness",
    "genre_register_fit",
    "discourse_rhythm",
)
CRITIC_AXES = (
    "naturalness",
    "genre_register_fit",
    "voice_specificity",
    "discourse_rhythm",
    "editing_restraint",
)
COMPARISON_AXES = set(CRITIC_AXES) | {"meaning_preservation"}
VARIANTS = ("without_skill", "with_skill")
OVEREDIT_CASES = (
    "essay-underedit-good-draft",
    "work-negation-underedit",
)
REPO_ROOT = Path(__file__).resolve().parents[3]
AGGREGATE_PATH = Path(__file__).resolve()
GRADER_PATH = Path(__file__).with_name("grader.py")
CRITIC_INSTRUCTIONS_PATH = Path(__file__).with_name("critic-instructions.md")
EVAL_PROTOCOL_PATH = Path(__file__).with_name("eval.md")
SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$")
BASE_CHECK_KEYS = (
    "case_count_is_12",
    "skill_sha_matches_current",
    "evaluation_runtime_sha_matches_current",
    "with_skill_deterministic_12_of_12",
    "with_skill_critic_12_of_12",
    "with_skill_semantic_hard_gate_12_of_12",
    "quality_axes_at_least_10",
    "overedit_cases_preserve_invariants_and_restraint",
)


def load_grader():
    spec = importlib.util.spec_from_file_location(
        "korean_natural_writing_grader", GRADER_PATH
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load grader: {GRADER_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


GRADER = load_grader()


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


def load_case_ids(cases_dir: Path) -> list[str]:
    case_ids = [read_json(path).get("id") for path in sorted(cases_dir.glob("*.json"))]
    if not case_ids or any(not isinstance(case_id, str) for case_id in case_ids):
        raise ValueError(f"invalid or empty case set: {cases_dir}")
    if len(case_ids) != len(set(case_ids)):
        raise ValueError("duplicate case ids")
    return case_ids


def tree_sha256(root: Path, paths: list[Path]) -> str:
    digest = hashlib.sha256()
    for path in sorted(paths):
        digest.update(path.relative_to(root).as_posix().encode("utf-8"))
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def current_eval_provenance(cases_dir: Path) -> dict[str, str]:
    skill_paths = [
        path
        for path in (
            REPO_ROOT / ".claude" / "skills" / "korean-natural-writing"
        ).rglob("*")
        if path.is_file() and "__pycache__" not in path.parts
    ]
    return {
        "skill_sha256": tree_sha256(REPO_ROOT, skill_paths),
        "grader_sha256": file_sha256(GRADER_PATH),
        "analyzer_sha256": file_sha256(GRADER.ANALYZER_PATH),
        "critic_instructions_sha256": file_sha256(CRITIC_INSTRUCTIONS_PATH),
        "eval_protocol_sha256": file_sha256(EVAL_PROTOCOL_PATH),
        "aggregate_sha256": file_sha256(AGGREGATE_PATH),
        "case_set_sha256": tree_sha256(
            cases_dir,
            sorted(cases_dir.glob("*.json")),
        ),
    }


def validate_metadata(metadata: dict[str, Any]) -> None:
    for field in ("provider", "model", "created_at", "critic_protocol"):
        if not isinstance(metadata.get(field), str) or not metadata[field].strip():
            raise ValueError(f"metadata.{field} must be a non-empty string")
    iteration = metadata.get("iteration")
    if isinstance(iteration, bool) or not isinstance(iteration, int) or iteration < 1:
        raise ValueError("metadata.iteration must be a positive integer")
    for field in ("token_usage", "latency"):
        value = metadata.get(field)
        if not isinstance(value, dict) or value.get("status") not in {
            "observed",
            "unavailable",
        }:
            raise ValueError(
                f"metadata.{field}.status must be observed or unavailable"
            )
    for field in (
        "skill_sha256",
        "grader_sha256",
        "analyzer_sha256",
        "critic_instructions_sha256",
        "eval_protocol_sha256",
        "aggregate_sha256",
        "case_set_sha256",
    ):
        value = metadata.get(field)
        if not isinstance(value, str) or not SHA256_PATTERN.fullmatch(value):
            raise ValueError(f"metadata.{field} must be a lowercase SHA-256")


def evaluation_passed_deterministic(result: dict[str, Any]) -> bool:
    failures = result.get("adjustments", {}).get("hard_failures", [])
    invariants = result.get("deterministic", {}).get("invariants", {})
    return not failures and invariants.get("passed") is True


def evaluation_has_complete_critic(result: dict[str, Any]) -> bool:
    critic = result.get("independent_critic")
    scores = result.get("scores", {})
    if (
        not isinstance(critic, dict)
        or result.get("evidence_packet", {}).get("source_coverage") != "complete"
    ):
        return False
    gate_passed = critic.get("hard_gate", {}).get("passed") is True
    if not gate_passed:
        return result.get("result", {}).get("status") == "fail"
    return all(axis in scores for axis in CRITIC_AXES)


def evaluation_requires_human_review(result: dict[str, Any]) -> bool:
    return (
        result.get("independent_critic", {}).get("verdict")
        == "needs_human_review"
    )


def evaluation_meets_quality_axes(result: dict[str, Any]) -> bool:
    if (
        not evaluation_has_complete_critic(result)
        or result.get("result", {}).get("status") != "pass"
    ):
        return False
    scores = result["scores"]
    return all(float(scores[axis]["score"]) >= 4 for axis in AXES_REQUIRED_AT_FOUR)


def validate_evaluation_artifact(
    result: dict[str, Any],
    *,
    case: dict[str, Any],
    candidate_text: str,
    candidate_source: str,
    critic: dict[str, Any] | None,
) -> None:
    case_id = case["id"]
    if result.get("schema") != "evaluation-result-v1":
        raise ValueError(f"evaluation schema mismatch: {case_id}")
    if result.get("rubric") != "korean-natural-writing":
        raise ValueError(f"evaluation rubric mismatch: {case_id}")
    if result.get("case_id") != case_id:
        raise ValueError(f"evaluation case id mismatch: {case_id}")
    provenance = result.get("artifact_provenance")
    if not isinstance(provenance, dict):
        raise ValueError(f"evaluation artifact provenance missing: {case_id}")
    expected = {
        "case_sha256": canonical_json_sha256(case),
        "candidate_sha256": text_sha256(candidate_text),
        "critic_sha256": canonical_json_sha256(critic) if critic is not None else None,
    }
    if provenance != expected:
        raise ValueError(f"evaluation artifact provenance mismatch: {case_id}")
    if result.get("independent_critic") != critic:
        raise ValueError(f"embedded critic mismatch: {case_id}")
    included_signals = result.get("evidence_packet", {}).get("included_signals")
    if not isinstance(included_signals, list):
        raise ValueError(f"evaluation evidence packet missing: {case_id}")
    candidate_sources = [
        item.get("source")
        for item in included_signals
        if isinstance(item, dict) and item.get("id") == "E2"
    ]
    if len(candidate_sources) != 1 or not isinstance(candidate_sources[0], str):
        raise ValueError(f"evaluation candidate source missing: {case_id}")
    if candidate_sources[0] != candidate_source:
        raise ValueError(f"evaluation candidate source mismatch: {case_id}")
    recomputed = GRADER.grade(
        case,
        candidate_text,
        critic,
        candidate_source,
    )
    if result != recomputed:
        raise ValueError(f"evaluation artifact differs from grader output: {case_id}")


def validate_mapping(mapping: dict[str, Any], case_ids: list[str]) -> None:
    if set(mapping) != set(case_ids):
        raise ValueError("mapping case ids must exactly match the case set")
    for case_id in case_ids:
        assignment = mapping[case_id]
        if not isinstance(assignment, dict) or set(assignment) != {"A", "B"}:
            raise ValueError(f"invalid A/B mapping: {case_id}")
        if set(assignment.values()) != set(VARIANTS):
            raise ValueError(f"mapping must assign each variant once: {case_id}")


def validate_comparison(
    comparison: dict[str, Any],
    *,
    case: dict[str, Any],
    expected_left: str,
    expected_right: str,
    candidates: dict[str, str],
    critics: dict[str, dict[str, Any]],
    eligible_labels: set[str],
) -> str:
    case_id = case["id"]
    if comparison.get("case_id") != case_id:
        raise ValueError(f"comparison case id mismatch: {case_id}")
    if comparison.get("left") != expected_left or comparison.get("right") != expected_right:
        raise ValueError(f"comparison order mismatch: {case_id}")
    winner = comparison.get("winner")
    if winner not in {"A", "B", "Tie"}:
        raise ValueError(f"invalid comparison winner: {case_id}")
    confidence = comparison.get("confidence")
    if (
        isinstance(confidence, bool)
        or not isinstance(confidence, (int, float))
        or not 0 <= confidence <= 1
    ):
        raise ValueError(f"invalid comparison confidence: {case_id}")
    if not isinstance(comparison.get("rationale"), str) or not comparison["rationale"].strip():
        raise ValueError(f"comparison rationale is required: {case_id}")
    if comparison.get("case_sha256") != canonical_json_sha256(case):
        raise ValueError(f"comparison case hash mismatch: {case_id}")
    expected_candidate_hashes = {
        label: text_sha256(candidates[label]) for label in ("A", "B")
    }
    if comparison.get("candidate_sha256") != expected_candidate_hashes:
        raise ValueError(f"comparison candidate hashes mismatch: {case_id}")
    expected_critic_hashes = {
        label: canonical_json_sha256(critics[label]) for label in ("A", "B")
    }
    if comparison.get("pointwise_critic_sha256") != expected_critic_hashes:
        raise ValueError(f"comparison critic hashes mismatch: {case_id}")
    decisive_axes = comparison.get("decisive_axes")
    if (
        not isinstance(decisive_axes, list)
        or not decisive_axes
        or not all(axis in COMPARISON_AXES for axis in decisive_axes)
    ):
        raise ValueError(f"comparison decisive_axes are invalid: {case_id}")
    evidence = comparison.get("candidate_evidence")
    if not isinstance(evidence, dict) or set(evidence) != {"A", "B"}:
        raise ValueError(f"comparison candidate evidence is incomplete: {case_id}")
    for label in ("A", "B"):
        item = evidence[label]
        if not isinstance(item, dict):
            raise ValueError(f"comparison evidence {label} is invalid: {case_id}")
        excerpt = item.get("excerpt")
        effect = item.get("effect")
        if not isinstance(excerpt, str) or not excerpt.strip() or excerpt not in candidates[label]:
            raise ValueError(
                f"comparison evidence {label} must quote its candidate: {case_id}"
            )
        if not isinstance(effect, str) or not effect.strip():
            raise ValueError(f"comparison evidence {label}.effect is required: {case_id}")
    if winner in {"A", "B"} and winner not in eligible_labels:
        raise ValueError(f"comparison selected an ineligible candidate: {case_id}")
    if len(eligible_labels) == 1 and winner != next(iter(eligible_labels)):
        raise ValueError(f"comparison must select the only eligible candidate: {case_id}")
    if not eligible_labels and winner != "Tie":
        raise ValueError(f"comparison must tie when both candidates are ineligible: {case_id}")
    return winner


def validate_human_resolution(
    resolution: dict[str, Any],
    *,
    case: dict[str, Any],
    candidates: dict[str, str],
    critics: dict[str, dict[str, Any]],
    eligible_labels: set[str],
) -> str:
    case_id = case["id"]
    winner = resolution.get("winner")
    if winner not in {"A", "B", "Tie"}:
        raise ValueError(f"invalid human-review winner: {case_id}")
    if winner in {"A", "B"} and winner not in eligible_labels:
        raise ValueError(f"human review selected an ineligible candidate: {case_id}")
    if len(eligible_labels) == 1 and winner != next(iter(eligible_labels)):
        raise ValueError(f"human review must select the only eligible candidate: {case_id}")
    if not eligible_labels and winner != "Tie":
        raise ValueError(f"human review must tie when both candidates are ineligible: {case_id}")
    if resolution.get("candidate_sha256") != {
        label: text_sha256(candidates[label]) for label in ("A", "B")
    }:
        raise ValueError(f"human-review candidate hashes mismatch: {case_id}")
    if resolution.get("case_sha256") != canonical_json_sha256(case):
        raise ValueError(f"human-review case hash mismatch: {case_id}")
    if resolution.get("pointwise_critic_sha256") != {
        label: canonical_json_sha256(critics[label]) for label in ("A", "B")
    }:
        raise ValueError(f"human-review critic hashes mismatch: {case_id}")
    decisive_axes = resolution.get("decisive_axes")
    if (
        not isinstance(decisive_axes, list)
        or not decisive_axes
        or not all(axis in COMPARISON_AXES for axis in decisive_axes)
    ):
        raise ValueError(f"human-review decisive_axes are invalid: {case_id}")
    evidence = resolution.get("candidate_evidence")
    if not isinstance(evidence, dict) or set(evidence) != {"A", "B"}:
        raise ValueError(f"human-review candidate evidence is incomplete: {case_id}")
    for label in ("A", "B"):
        item = evidence[label]
        if not isinstance(item, dict):
            raise ValueError(f"human-review evidence {label} is invalid: {case_id}")
        excerpt = item.get("excerpt")
        effect = item.get("effect")
        if (
            not isinstance(excerpt, str)
            or not excerpt.strip()
            or excerpt not in candidates[label]
        ):
            raise ValueError(
                f"human-review evidence {label} must quote its candidate: {case_id}"
            )
        if not isinstance(effect, str) or not effect.strip():
            raise ValueError(
                f"human-review evidence {label}.effect is required: {case_id}"
            )
    if not isinstance(resolution.get("rationale"), str) or not resolution[
        "rationale"
    ].strip():
        raise ValueError(f"human-review rationale is required: {case_id}")
    return winner


def load_human_review(path: Path | None) -> dict[str, Any] | None:
    if path is None:
        return None
    review = read_json(path)
    if review.get("schema") != "korean-natural-writing.human-review.v2":
        raise ValueError("unsupported human-review schema")
    for field in ("reviewer", "created_at"):
        if not isinstance(review.get(field), str) or not review[field].strip():
            raise ValueError(f"human-review {field} is required")
    if review.get("reviewer_type") != "human":
        raise ValueError("human-review reviewer_type must be human")
    if review.get("attestation") != "human_direct_review":
        raise ValueError("human-review attestation must be human_direct_review")
    if not isinstance(review.get("cases"), dict):
        raise ValueError("human-review cases must be an object")
    return review


def score_at_least(result: dict[str, Any], axis: str, minimum: float) -> bool:
    score = result.get("scores", {}).get(axis, {}).get("score")
    return (
        not isinstance(score, bool)
        and isinstance(score, (int, float))
        and float(score) >= minimum
    )


def base_checks_pass(checks: dict[str, bool]) -> bool:
    return all(checks.get(key) is True for key in BASE_CHECK_KEYS)


def resolve_status(
    checks: dict[str, bool],
    *,
    human_review_could_still_pass: bool,
    reviewable_without_resolution: int,
) -> str:
    if all(checks.values()):
        return "pass"
    if human_review_could_still_pass and reviewable_without_resolution:
        return "needs_human_review"
    return "fail"


def aggregate(
    cases_dir: Path,
    run_dir: Path,
    mapping_path: Path,
    metadata_path: Path,
    human_review_path: Path | None = None,
) -> dict[str, Any]:
    case_ids = load_case_ids(cases_dir)
    mapping = read_json(mapping_path)
    metadata = read_json(metadata_path)
    human_review = load_human_review(human_review_path)
    human_cases = human_review["cases"] if human_review else {}
    validate_mapping(mapping, case_ids)
    validate_metadata(metadata)
    case_by_id: dict[str, dict[str, Any]] = {}
    for path in sorted(cases_dir.glob("*.json")):
        case = read_json(path)
        case_by_id[case["id"]] = case

    rows: list[dict[str, Any]] = []
    used_human_cases: set[str] = set()
    for case_id in case_ids:
        case = case_by_id[case_id]
        blind_dir = run_dir / "blind" / case_id
        evaluations: dict[str, dict[str, Any]] = {}
        deterministic: dict[str, dict[str, Any]] = {}
        candidate_completions: dict[str, str] = {}
        critics: dict[str, dict[str, Any]] = {}
        for variant in VARIANTS:
            candidate_path = run_dir / case_id / variant / "candidate.md"
            candidate_text = candidate_path.read_text(encoding="utf-8")
            candidate_completions[variant] = GRADER.extract_candidate(candidate_text)[0]
            deterministic[variant] = read_json(
                run_dir / case_id / variant / "evaluation-result-deterministic.json"
            )
            evaluations[variant] = read_json(
                run_dir / case_id / variant / "evaluation-result.json"
            )
            label = next(
                label
                for label, mapped_variant in mapping[case_id].items()
                if mapped_variant == variant
            )
            critic = read_json(blind_dir / f"critic-{label}.json")
            critics[label] = critic
            validate_evaluation_artifact(
                deterministic[variant],
                case=case,
                candidate_text=candidate_text,
                candidate_source=str(candidate_path),
                critic=None,
            )
            validate_evaluation_artifact(
                evaluations[variant],
                case=case,
                candidate_text=candidate_text,
                candidate_source=str(candidate_path),
                critic=critic,
            )

        blind_candidates = {
            label: (blind_dir / f"{label}.md").read_text(encoding="utf-8").strip()
            for label in ("A", "B")
        }
        for label, variant in mapping[case_id].items():
            if blind_candidates[label] != candidate_completions[variant]:
                raise ValueError(f"blind candidate does not match mapping: {case_id}/{label}")

        deterministic_pass = {
            variant: evaluation_passed_deterministic(deterministic[variant])
            for variant in VARIANTS
        }
        critic_complete = {
            variant: evaluation_has_complete_critic(evaluations[variant])
            for variant in VARIANTS
        }
        semantic_hard_gate = {
            variant: evaluations[variant]
            .get("independent_critic", {})
            .get("hard_gate", {})
            .get("passed")
            is True
            for variant in VARIANTS
        }
        eligible_labels = {
            label
            for label, variant in mapping[case_id].items()
            if deterministic_pass[variant]
            and critic_complete[variant]
            and semantic_hard_gate[variant]
        }
        first_winner = validate_comparison(
            read_json(blind_dir / "comparison-first.json"),
            case=case,
            expected_left="A",
            expected_right="B",
            candidates=blind_candidates,
            critics=critics,
            eligible_labels=eligible_labels,
        )
        swapped_winner = validate_comparison(
            read_json(blind_dir / "comparison-swapped.json"),
            case=case,
            expected_left="B",
            expected_right="A",
            candidates=blind_candidates,
            critics=critics,
            eligible_labels=eligible_labels,
        )
        consistent = first_winner == swapped_winner
        model_winner = first_winner if consistent else "needs_human_review"
        pointwise_human_review_required = any(
            evaluation_requires_human_review(evaluations[variant])
            for variant in VARIANTS
        )
        reviewable = (
            not consistent
            or model_winner == "Tie"
            or pointwise_human_review_required
        )
        resolved_winner = (
            "needs_human_review" if reviewable else model_winner
        )
        human_resolution = None
        if case_id in human_cases:
            if not reviewable:
                raise ValueError(f"human review cannot override a decisive model result: {case_id}")
            resolution = human_cases[case_id]
            if not isinstance(resolution, dict):
                raise ValueError(f"human-review case must be an object: {case_id}")
            resolved_winner = validate_human_resolution(
                resolution,
                case=case,
                candidates=blind_candidates,
                critics=critics,
                eligible_labels=eligible_labels,
            )
            human_resolution = resolution
            used_human_cases.add(case_id)
        variant_winner = (
            mapping[case_id][resolved_winner]
            if resolved_winner in {"A", "B"}
            else resolved_winner
        )
        rows.append(
            {
                "case_id": case_id,
                "deterministic_pass": deterministic_pass,
                "critic_complete": critic_complete,
                "semantic_hard_gate": semantic_hard_gate,
                "with_skill_quality_axes_pass": evaluation_meets_quality_axes(
                    evaluations["with_skill"]
                ),
                "with_skill_result_status": evaluations["with_skill"]
                .get("result", {})
                .get("status"),
                "with_skill_voice_specificity_at_least_4": score_at_least(
                    evaluations["with_skill"], "voice_specificity", 4
                ),
                "with_skill_editing_restraint_at_least_4": score_at_least(
                    evaluations["with_skill"], "editing_restraint", 4
                ),
                "eligible_labels": sorted(eligible_labels),
                "first_winner": first_winner,
                "swapped_winner": swapped_winner,
                "consistent": consistent,
                "model_winner": model_winner,
                "pointwise_human_review_required": pointwise_human_review_required,
                "human_resolution": human_resolution,
                "blind_winner": resolved_winner,
                "variant_winner": variant_winner,
                "unresolved_order_inconsistency": not consistent
                and human_resolution is None,
                "reviewable_without_resolution": reviewable
                and human_resolution is None,
            }
        )

    unused_human_cases = set(human_cases) - used_human_cases
    if unused_human_cases:
        raise ValueError(
            "human review contains non-reviewable or unknown cases: "
            + ", ".join(sorted(unused_human_cases))
        )

    with_skill_deterministic = sum(
        row["deterministic_pass"]["with_skill"] for row in rows
    )
    without_skill_deterministic = sum(
        row["deterministic_pass"]["without_skill"] for row in rows
    )
    with_skill_critic_complete = sum(
        row["critic_complete"]["with_skill"] for row in rows
    )
    with_skill_semantic = sum(
        row["semantic_hard_gate"]["with_skill"] for row in rows
    )
    quality_axes_pass = sum(row["with_skill_quality_axes_pass"] for row in rows)
    model_inconsistent = sum(not row["consistent"] for row in rows)
    unresolved_inconsistent = sum(
        row["unresolved_order_inconsistency"] for row in rows
    )
    human_resolutions = sum(row["human_resolution"] is not None for row in rows)
    pointwise_human_review_required = sum(
        row["pointwise_human_review_required"] for row in rows
    )
    reviewable_without_resolution = sum(
        row["reviewable_without_resolution"] for row in rows
    )
    ties = sum(row["variant_winner"] == "Tie" for row in rows)
    decisive = sum(row["variant_winner"] in VARIANTS for row in rows)
    with_skill_wins = sum(row["variant_winner"] == "with_skill" for row in rows)
    without_skill_wins = sum(
        row["variant_winner"] == "without_skill" for row in rows
    )
    win_rate = with_skill_wins / decisive if decisive else 0.0
    potential_decisive = decisive + reviewable_without_resolution
    optimistic_win_rate = (
        (with_skill_wins + reviewable_without_resolution) / potential_decisive
        if potential_decisive
        else 0.0
    )
    rows_by_id = {row["case_id"]: row for row in rows}
    overedit_pass = all(
        rows_by_id[case_id]["deterministic_pass"]["with_skill"]
        and rows_by_id[case_id]["semantic_hard_gate"]["with_skill"]
        and rows_by_id[case_id]["with_skill_result_status"] == "pass"
        and rows_by_id[case_id]["with_skill_voice_specificity_at_least_4"]
        and rows_by_id[case_id]["with_skill_editing_restraint_at_least_4"]
        for case_id in OVEREDIT_CASES
    )
    current_provenance = current_eval_provenance(cases_dir)
    skill_sha_matches_current = (
        metadata["skill_sha256"] == current_provenance["skill_sha256"]
    )
    runtime_sha_matches_current = all(
        metadata[field] == current_provenance[field]
        for field in (
            "grader_sha256",
            "analyzer_sha256",
            "critic_instructions_sha256",
            "eval_protocol_sha256",
            "aggregate_sha256",
            "case_set_sha256",
        )
    )

    checks = {
        "case_count_is_12": len(rows) == 12,
        "skill_sha_matches_current": skill_sha_matches_current,
        "evaluation_runtime_sha_matches_current": runtime_sha_matches_current,
        "with_skill_deterministic_12_of_12": with_skill_deterministic == 12,
        "with_skill_critic_12_of_12": with_skill_critic_complete == 12,
        "with_skill_semantic_hard_gate_12_of_12": with_skill_semantic == 12,
        "quality_axes_at_least_10": quality_axes_pass >= 10,
        "no_unresolved_order_inconsistency": unresolved_inconsistent == 0,
        "no_unresolved_human_review": reviewable_without_resolution == 0,
        "at_least_8_decisive_comparisons": decisive >= 8,
        "with_skill_win_rate_at_least_75_percent": decisive >= 8
        and win_rate >= 0.75,
        "overedit_cases_preserve_invariants_and_restraint": overedit_pass,
    }
    human_review_could_still_pass = (
        base_checks_pass(checks)
        and potential_decisive >= 8
        and optimistic_win_rate >= 0.75
    )
    status = resolve_status(
        checks,
        human_review_could_still_pass=human_review_could_still_pass,
        reviewable_without_resolution=reviewable_without_resolution,
    )

    return {
        "schema": "korean-natural-writing.aggregate.v1",
        "status": status,
        "case_count": len(rows),
        "provenance": {
            **metadata,
            "current": current_provenance,
            "skill_sha_matches_current": skill_sha_matches_current,
            "evaluation_runtime_sha_matches_current": runtime_sha_matches_current,
            "human_review": {
                "reviewer": human_review["reviewer"],
                "reviewer_type": human_review["reviewer_type"],
                "attestation": human_review["attestation"],
                "created_at": human_review["created_at"],
                "resolved_cases": sorted(used_human_cases),
            }
            if human_review
            else None,
        },
        "summary": {
            "with_skill_deterministic_pass": with_skill_deterministic,
            "without_skill_deterministic_pass": without_skill_deterministic,
            "with_skill_critic_complete": with_skill_critic_complete,
            "with_skill_semantic_hard_gate_pass": with_skill_semantic,
            "with_skill_quality_axes_pass": quality_axes_pass,
            "with_skill_wins": with_skill_wins,
            "without_skill_wins": without_skill_wins,
            "ties": ties,
            "model_order_inconsistencies": model_inconsistent,
            "unresolved_order_inconsistencies": unresolved_inconsistent,
            "human_resolutions": human_resolutions,
            "pointwise_human_review_required": pointwise_human_review_required,
            "reviewable_without_resolution": reviewable_without_resolution,
            "decisive_comparisons": decisive,
            "with_skill_win_rate": round(win_rate, 4),
            "potential_decisive_after_human_review": potential_decisive,
            "optimistic_with_skill_win_rate": round(optimistic_win_rate, 4),
            "human_review_could_still_pass": human_review_could_still_pass,
        },
        "checks": checks,
        "cases": rows,
    }


def self_test() -> int:
    mapping = {
        "case": {"A": "with_skill", "B": "without_skill"},
    }
    validate_mapping(mapping, ["case"])
    case = {"id": "case", "input": "원문입니다.", "required_meaning": [], "constraints": {}}
    candidates = {"A": "A 후보입니다.", "B": "B 후보입니다."}
    critics = {"A": {"critic": "a"}, "B": {"critic": "b"}}
    comparison = {
        "case_id": "case",
        "case_sha256": canonical_json_sha256(case),
        "left": "B",
        "right": "A",
        "winner": "A",
        "rationale": "A가 목적을 더 직접적으로 전달한다.",
        "confidence": 0.8,
        "candidate_sha256": {
            label: text_sha256(text) for label, text in candidates.items()
        },
        "pointwise_critic_sha256": {
            label: canonical_json_sha256(critic)
            for label, critic in critics.items()
        },
        "decisive_axes": ["naturalness"],
        "candidate_evidence": {
            "A": {"excerpt": "A 후보", "effect": "목적이 바로 드러난다."},
            "B": {"excerpt": "B 후보", "effect": "표현이 상대적으로 추상적이다."},
        },
    }
    winner = validate_comparison(
        comparison,
        case=case,
        expected_left="B",
        expected_right="A",
        candidates=candidates,
        critics=critics,
        eligible_labels={"A", "B"},
    )
    assert winner == "A"
    human_resolution = {
        "winner": "A",
        "rationale": "A가 목적을 더 직접적으로 전달한다.",
        "case_sha256": canonical_json_sha256(case),
        "candidate_sha256": {
            label: text_sha256(text) for label, text in candidates.items()
        },
        "pointwise_critic_sha256": {
            label: canonical_json_sha256(critic)
            for label, critic in critics.items()
        },
        "decisive_axes": ["naturalness"],
        "candidate_evidence": comparison["candidate_evidence"],
    }
    assert (
        validate_human_resolution(
            human_resolution,
            case=case,
            candidates=candidates,
            critics=critics,
            eligible_labels={"A", "B"},
        )
        == "A"
    )
    stale_human_resolution = json.loads(
        json.dumps(human_resolution, ensure_ascii=False)
    )
    stale_human_resolution["case_sha256"] = "0" * 64
    try:
        validate_human_resolution(
            stale_human_resolution,
            case=case,
            candidates=candidates,
            critics=critics,
            eligible_labels={"A", "B"},
        )
    except ValueError:
        pass
    else:
        raise AssertionError("stale human review must fail")
    assert evaluation_requires_human_review(
        {"independent_critic": {"verdict": "needs_human_review"}}
    )
    try:
        validate_comparison(
            {key: value for key, value in comparison.items() if key != "candidate_evidence"},
            case=case,
            expected_left="B",
            expected_right="A",
            candidates=candidates,
            critics=critics,
            eligible_labels={"A", "B"},
        )
    except ValueError:
        pass
    else:
        raise AssertionError("ungrounded comparison must fail")
    passing_checks = {"base": True, "comparison": True}
    assert (
        resolve_status(
            passing_checks,
            human_review_could_still_pass=True,
            reviewable_without_resolution=0,
        )
        == "pass"
    )
    review_checks = {"base": True, "comparison": False}
    assert (
        resolve_status(
            review_checks,
            human_review_could_still_pass=True,
            reviewable_without_resolution=2,
        )
        == "needs_human_review"
    )
    assert (
        resolve_status(
            review_checks,
            human_review_could_still_pass=False,
            reviewable_without_resolution=4,
        )
        == "fail"
    )
    semantic_checks = {key: True for key in BASE_CHECK_KEYS}
    semantic_checks["with_skill_semantic_hard_gate_12_of_12"] = False
    assert not base_checks_pass(semantic_checks)
    assert (
        resolve_status(
            semantic_checks,
            human_review_could_still_pass=False,
            reviewable_without_resolution=2,
        )
        == "fail"
    )
    candidate = "## 완성본\n후보입니다.\n\n## 다듬은 기준\n- 의미를 보존했다."
    completion, format_errors = GRADER.extract_candidate(candidate)
    assert not format_errors
    assert completion == "후보입니다."
    assert "의미를 보존" not in completion
    result = GRADER.grade(case, candidate, None, "self-test-candidate")
    validate_evaluation_artifact(
        result,
        case=case,
        candidate_text=candidate,
        candidate_source="self-test-candidate",
        critic=None,
    )
    replayed = json.loads(json.dumps(result, ensure_ascii=False))
    replayed["result"]["status"] = "pass"
    try:
        validate_evaluation_artifact(
            replayed,
            case=case,
            candidate_text=candidate,
            candidate_source="self-test-candidate",
            critic=None,
        )
    except ValueError:
        pass
    else:
        raise AssertionError("tampered evaluation must fail canonical recomputation")
    print("PASS")
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cases-dir", type=Path)
    parser.add_argument("--run-dir", type=Path)
    parser.add_argument("--mapping", type=Path)
    parser.add_argument("--metadata", type=Path)
    parser.add_argument("--human-review", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument(
        "--print-provenance",
        action="store_true",
        help="Print generation-time skill/evaluator/case hashes and exit",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.self_test:
        return self_test()
    if args.print_provenance:
        cases_dir = args.cases_dir or Path(__file__).with_name("cases")
        print(
            json.dumps(
                current_eval_provenance(cases_dir.resolve()),
                ensure_ascii=False,
                indent=2,
            )
        )
        return 0
    if not args.cases_dir or not args.run_dir or not args.mapping or not args.metadata:
        raise SystemExit(
            "--cases-dir, --run-dir, --mapping, and --metadata are required"
        )
    result = aggregate(
        args.cases_dir,
        args.run_dir,
        args.mapping,
        args.metadata,
        args.human_review,
    )
    payload = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload, encoding="utf-8")
    else:
        sys.stdout.write(payload)
    if result["status"] == "pass":
        return 0
    if result["status"] == "needs_human_review":
        return 2
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
