#!/usr/bin/env python3
"""Executable Design Runtime v3 regression and evidence grader."""

from __future__ import annotations

import argparse
import base64
import binascii
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from functools import lru_cache
from pathlib import Path
from typing import Any


EVAL_DIR = Path(__file__).resolve().parent
CLAUDE_DIR = EVAL_DIR.parents[1]
DETECTOR = (
    CLAUDE_DIR / "skills" / "design-harness" / "scripts" / "detect-design-slop.mjs"
)
DEFAULT_CASES = EVAL_DIR / "cases" / "detector-regression.json"

WEIGHTS: dict[str, dict[str, float]] = {
    "product": {
        "usability": 0.25,
        "state_completeness": 0.20,
        "craft": 0.20,
        "accessibility": 0.15,
        "evidence_truth": 0.10,
        "distinction": 0.10,
    },
    "operational": {
        "task_efficiency": 0.25,
        "density_readability": 0.20,
        "state_completeness": 0.20,
        "craft": 0.15,
        "accessibility": 0.10,
        "evidence_truth": 0.10,
    },
    "brand": {
        "register_fit": 0.15,
        "distinction": 0.25,
        "evidence_truth": 0.20,
        "craft": 0.20,
        "accessibility": 0.10,
        "narrative": 0.10,
    },
    "campaign": {
        "register_fit": 0.15,
        "distinction": 0.20,
        "evidence_truth": 0.20,
        "craft": 0.20,
        "accessibility": 0.10,
        "message_clarity": 0.15,
    },
    "public-sector": {
        "usability": 0.25,
        "accessibility": 0.25,
        "system_fidelity": 0.20,
        "state_completeness": 0.15,
        "evidence_truth": 0.15,
    },
    "editorial": {
        "register_fit": 0.20,
        "typography": 0.25,
        "distinction": 0.20,
        "craft": 0.15,
        "accessibility": 0.10,
        "evidence_truth": 0.10,
    },
    "design-system": {
        "system_fidelity": 0.25,
        "state_completeness": 0.20,
        "accessibility": 0.20,
        "craft": 0.15,
        "evidence_truth": 0.15,
        "adoption_safety": 0.05,
    },
    "asset": {
        "brief_fidelity": 0.25,
        "craft": 0.25,
        "distinctiveness": 0.20,
        "technical_fitness": 0.15,
        "evidence_truth": 0.15,
    },
}

TRUSTED_PRODUCERS = {
    "capture-web-evidence@1",
    "capture-flutter-evidence@1",
    "design-runtime-detector@1",
}


@lru_cache(maxsize=1)
def resolve_openssl_ed25519() -> str | None:
    candidates = (
        shutil.which("openssl"),
        shutil.which("openssl3"),
        "/opt/homebrew/opt/openssl@3/bin/openssl",
        "/usr/local/opt/openssl@3/bin/openssl",
        "/opt/homebrew/bin/openssl",
        "/usr/local/bin/openssl",
    )
    seen: set[str] = set()
    for candidate in candidates:
        if not candidate or candidate in seen:
            continue
        seen.add(candidate)
        try:
            with tempfile.TemporaryDirectory(prefix="design-grader-openssl-") as temp:
                root = Path(temp)
                private = root / "private.pem"
                public = root / "public.pem"
                payload = root / "payload.bin"
                signature = root / "signature.bin"
                payload.write_bytes(b"design-grader-ed25519-probe")
                commands = (
                    [
                        candidate,
                        "genpkey",
                        "-algorithm",
                        "ED25519",
                        "-out",
                        str(private),
                    ],
                    [
                        candidate,
                        "pkey",
                        "-in",
                        str(private),
                        "-pubout",
                        "-out",
                        str(public),
                    ],
                    [
                        candidate,
                        "pkeyutl",
                        "-sign",
                        "-inkey",
                        str(private),
                        "-rawin",
                        "-in",
                        str(payload),
                        "-out",
                        str(signature),
                    ],
                    [
                        candidate,
                        "pkeyutl",
                        "-verify",
                        "-pubin",
                        "-inkey",
                        str(public),
                        "-rawin",
                        "-in",
                        str(payload),
                        "-sigfile",
                        str(signature),
                    ],
                )
                supported = all(
                    subprocess.run(
                        command,
                        check=False,
                        capture_output=True,
                        timeout=5,
                    ).returncode
                    == 0
                    for command in commands
                )
        except (OSError, subprocess.TimeoutExpired):
            continue
        if supported:
            return candidate
    return None


def load_object(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"expected JSON object: {path}")
    return payload


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_bytes(payload: dict[str, Any]) -> bytes:
    return json.dumps(
        payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


def review_manifest_digest(manifest: dict[str, Any]) -> str:
    review_view = dict(manifest)
    review_view.pop("generated_at", None)
    review_view["items"] = [
        item
        for item in manifest.get("items", [])
        if item.get("kind") != "evaluation-result"
    ]
    return hashlib.sha256(canonical_bytes(review_view)).hexdigest()


def verify_signature(
    public_key: Path, payload: dict[str, Any], signature_b64: str
) -> bool:
    try:
        signature = base64.b64decode(signature_b64, validate=True)
    except (ValueError, binascii.Error):
        return False
    openssl = resolve_openssl_ed25519()
    if openssl is None:
        return False
    with tempfile.TemporaryDirectory(prefix="ui-design-grader-signature-") as temporary:
        root = Path(temporary)
        payload_path = root / "payload.json"
        signature_path = root / "signature.bin"
        payload_path.write_bytes(canonical_bytes(payload))
        signature_path.write_bytes(signature)
        try:
            process = subprocess.run(
                [
                    openssl,
                    "pkeyutl",
                    "-verify",
                    "-pubin",
                    "-inkey",
                    str(public_key),
                    "-rawin",
                    "-in",
                    str(payload_path),
                    "-sigfile",
                    str(signature_path),
                ],
                check=False,
                capture_output=True,
                text=True,
                timeout=10,
            )
        except (OSError, subprocess.TimeoutExpired):
            return False
    return process.returncode == 0


def write_result(path: Path | None, payload: dict[str, Any]) -> None:
    rendered = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    if path:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(rendered, encoding="utf-8")
    print(rendered, end="")


def self_test(args: argparse.Namespace) -> int:
    cases_payload = load_object(Path(args.cases).resolve())
    failures: list[dict[str, Any]] = []
    results: list[dict[str, Any]] = []
    with tempfile.TemporaryDirectory(prefix="design-eval-") as temporary:
        root = Path(temporary)
        for case in cases_payload.get("cases", []):
            source = root / f"{case['id']}{case['extension']}"
            source.write_text(case["source"], encoding="utf-8")
            process = subprocess.run(
                [
                    "node",
                    str(DETECTOR),
                    "--format",
                    "json",
                    "--fail-on",
                    "none",
                    str(source),
                ],
                cwd=root,
                check=False,
                capture_output=True,
                text=True,
            )
            if process.returncode != 0:
                actual: set[str] = set()
                error = (
                    process.stderr.strip() or f"detector exited {process.returncode}"
                )
            else:
                scan = json.loads(process.stdout)
                actual = {finding["id"] for finding in scan.get("findings", [])}
                error = ""
            expected = set(case.get("expected_ids", []))
            missing = sorted(expected - actual)
            unexpected = sorted(actual - expected) if case.get("exact") else []
            passed = not error and not missing and not unexpected
            row = {
                "id": case["id"],
                "passed": passed,
                "expected": sorted(expected),
                "actual": sorted(actual),
                "missing": missing,
                "unexpected": unexpected,
                "error": error,
            }
            results.append(row)
            if not passed:
                failures.append(row)
    payload = {
        "schema": "ui-design-eval-self-test-v1",
        "status": "pass" if not failures else "fail",
        "summary": {
            "passed": len(results) - len(failures),
            "failed": len(failures),
            "total": len(results),
        },
        "failures": failures,
    }
    write_result(Path(args.output).resolve() if args.output else None, payload)
    return 0 if not failures else 2


def evidence_ids(manifest: dict[str, Any]) -> set[str]:
    return {str(item.get("id")) for item in manifest.get("items", [])}


def grade(args: argparse.Namespace) -> int:
    run_path = Path(args.run).resolve()
    evidence_path = Path(args.evidence).resolve()
    critic_path = Path(args.critic).resolve()
    run = load_object(run_path)
    evidence = load_object(evidence_path)
    critic = load_object(critic_path)
    scores_input = {
        "scores": critic.get("rubric_scores", {}),
        "excluded_signals": critic.get("excluded_signals", []),
    }
    detector_path = Path(args.detector).resolve()
    detector = load_object(detector_path)
    attestation = load_object(Path(args.attestation).resolve())
    review_packet_path = Path(args.review_packet).resolve()
    review_packet = load_object(review_packet_path)
    public_key = Path(args.public_key).resolve()
    register = run.get("register")
    if register not in WEIGHTS:
        raise ValueError(f"unsupported design register: {register}")
    weights = WEIGHTS[register]
    integrity_errors: list[str] = []
    if evidence.get("run_id") != run.get("run_id") or critic.get("run_id") != run.get(
        "run_id"
    ):
        integrity_errors.append("run_id mismatch across grader inputs")
    if run.get("waivers"):
        integrity_errors.append("waived runs cannot receive a passing final evaluation")
    if detector.get("schema") != "design-slop-scan-v2" or not detector.get(
        "files_scanned"
    ):
        integrity_errors.append(
            "detector input is missing, empty, or has the wrong schema"
        )
    if review_packet.get("schema") != "design-review-packet-v1" or sha256(
        review_packet_path
    ) != run.get("review_packet_sha256"):
        integrity_errors.append(
            "review packet is missing, hash-drifted, or has the wrong schema"
        )
    if review_packet.get("evidence_manifest_sha256") != review_manifest_digest(
        evidence
    ):
        integrity_errors.append(
            "evidence manifest differs from the independently reviewed packet"
        )
    if review_packet.get("detector_sha256") != sha256(detector_path):
        integrity_errors.append(
            "detector result differs from the independently reviewed packet"
        )
    payload = attestation.get("payload")
    if attestation.get("schema") != "design-critic-attestation-v1" or not isinstance(
        payload, dict
    ):
        integrity_errors.append("signed critic attestation is missing or malformed")
        payload = {}
    expected_attestation = {
        "schema": "design-critic-attestation-payload-v1",
        "run_id": run.get("run_id"),
        "issuer": payload.get("issuer"),
        "execution_id": payload.get("execution_id"),
        "critic_actor_id": critic.get("critic_id"),
        "implementation_actor_id": run.get("implementation_actor_id"),
        "review_packet_sha256": run.get("review_packet_sha256"),
        "critic_sha256": sha256(critic_path),
        "evidence_manifest_sha256": review_manifest_digest(evidence),
        "source_fingerprint_digest": run.get("project_fingerprint", {}).get("digest"),
        "issued_at": payload.get("issued_at"),
    }
    if payload != expected_attestation:
        integrity_errors.append("critic attestation is not bound to the current inputs")
    if not public_key.is_file() or sha256(public_key) != run.get(
        "trust_policy", {}
    ).get("public_key_sha256"):
        integrity_errors.append(
            "critic public key is missing or differs from the run trust policy"
        )
    elif resolve_openssl_ed25519() is None:
        integrity_errors.append(
            "OpenSSL with Ed25519 pkeyutl -rawin support is required"
        )
    elif not verify_signature(
        public_key, payload, str(attestation.get("signature", ""))
    ):
        integrity_errors.append("critic attestation signature verification failed")
    trusted_items: list[dict[str, Any]] = []
    for item in evidence.get("items", []):
        path = Path(str(item.get("path", ""))).expanduser().resolve()
        if not path.is_file() or sha256(path) != item.get("sha256"):
            integrity_errors.append(f"evidence path/hash invalid: {item.get('id')}")
            continue
        provenance = item.get("provenance", {})
        if (
            provenance.get("producer") in TRUSTED_PRODUCERS
            and provenance.get("trust") in {"runtime", "runtime-adapter"}
            and item.get("verdict") == "pass"
        ):
            trusted_items.append(item)
    detector_items = [
        item for item in trusted_items if item.get("kind") == "source-scan"
    ]
    if (
        not detector_items
        or Path(detector_items[-1]["path"]).resolve() != detector_path
    ):
        integrity_errors.append(
            "detector is not the runtime-generated source-scan evidence"
        )
    included_signals = [
        {
            "id": item["id"],
            "source": item["path"],
            "summary": f"{item['kind']} for route={item.get('route', 'n/a')} state={item.get('state', 'n/a')} viewport={item.get('viewport', 'n/a')}",
            "supports": item.get("supports", []),
        }
        for item in trusted_items
    ]
    known_evidence = {str(item.get("id")) for item in trusted_items}
    missing_evidence: list[str] = list(integrity_errors)
    kinds = {item.get("kind") for item in trusted_items}
    for kind in ("source-scan", "result-screenshot"):
        if kind not in kinds:
            missing_evidence.append(f"required evidence kind missing: {kind}")
    if (
        run.get("platform", {}).get("kind") == "web"
        and "accessibility-tree" not in kinds
    ):
        missing_evidence.append("web accessibility tree missing")
    actor = critic.get("actor", {})
    if (
        critic.get("independent") is not True
        or actor.get("role") != "independent_critic"
        or actor.get("actor_id") == run.get("implementation_actor_id")
    ):
        missing_evidence.append("critic independence not established")
    unknown_critic_evidence = set(critic.get("evidence_ids", [])) - known_evidence
    if unknown_critic_evidence:
        missing_evidence.append(
            f"critic references unknown evidence IDs: {', '.join(sorted(unknown_critic_evidence))}"
        )

    score_rows: dict[str, Any] = {}
    weighted_score = 0.0
    score_errors: list[str] = []
    for axis, weight in weights.items():
        row = scores_input.get("scores", {}).get(axis)
        if not isinstance(row, dict):
            score_errors.append(f"missing score axis: {axis}")
            continue
        score = row.get("score")
        if not isinstance(score, (int, float)) or not 0 <= score <= 10:
            score_errors.append(f"invalid score for {axis}")
            continue
        references = row.get("evidence", [])
        unknown = set(references) - known_evidence
        if not references or unknown:
            score_errors.append(f"axis {axis} lacks valid evidence references")
        weighted_score += float(score) * weight
        score_rows[axis] = {
            "score": score,
            "max": 10,
            "weight": weight,
            "evidence": references,
            "rationale": row.get("rationale", ""),
        }

    hard_failures: list[dict[str, Any]] = []
    if detector.get("counts", {}).get("hard-fail", 0):
        hard_failures.append(
            {
                "reason": "unwaived design-slop detector hard failure",
                "evidence": ["source-scan"],
            }
        )
    if critic.get("decision") in {"fail", "blocked"}:
        hard_failures.append(
            {
                "reason": f"independent critic decision: {critic.get('decision')}",
                "evidence": critic.get("evidence_ids", []),
            }
        )
    if int(critic.get("round", 99)) > int(
        run.get("repair_policy", {}).get("max_rounds", 2)
    ):
        hard_failures.append(
            {
                "reason": "repair round exceeded the bounded repair policy",
                "evidence": critic.get("evidence_ids", []),
            }
        )

    below_floor = [axis for axis, row in score_rows.items() if row["score"] < 5]
    adjusted = round(weighted_score, 2)
    if hard_failures or below_floor or adjusted < 7.0:
        status = "fail"
    elif missing_evidence or score_errors or critic.get("decision") != "pass":
        status = "needs_review"
    else:
        status = "pass"
    confidence = min(
        1.0,
        len(included_signals)
        / max(4, len(run.get("routes", [])) + len(run.get("viewports", [])) + 2),
    )
    if missing_evidence or score_errors:
        confidence = min(confidence, 0.69)
    payload = {
        "schema": "evaluation-result-v1",
        "rubric": f"ui-design-v3:{register}",
        "evidence_packet": {
            "source_coverage": "complete" if not missing_evidence else "partial",
            "included_signals": included_signals,
            "excluded_signals": critic.get("excluded_signals", []),
            "missing_evidence": missing_evidence + score_errors,
        },
        "scores": score_rows,
        "adjustments": {
            "bonus": [],
            "deductions": [
                {
                    "points": 0,
                    "reason": f"axis below minimum floor: {axis}",
                    "evidence": score_rows[axis]["evidence"],
                }
                for axis in below_floor
            ],
            "hard_failures": hard_failures,
        },
        "result": {
            "weighted_score": round(weighted_score, 2),
            "adjusted_score": adjusted,
            "status": status,
            "confidence": round(confidence, 2),
            "summary": f"{register} register evaluation: {status}; evidence and critic gates are evaluated separately from taste scores.",
        },
    }
    write_result(Path(args.output).resolve() if args.output else None, payload)
    return 0 if status == "pass" else 2


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Design Runtime v3 eval runner")
    subparsers = parser.add_subparsers(dest="command", required=True)
    self_test_parser = subparsers.add_parser("self-test")
    self_test_parser.add_argument("--cases", default=str(DEFAULT_CASES))
    self_test_parser.add_argument("--output")
    self_test_parser.set_defaults(func=self_test)
    grade_parser = subparsers.add_parser("grade")
    grade_parser.add_argument("--run", required=True)
    grade_parser.add_argument("--evidence", required=True)
    grade_parser.add_argument("--critic", required=True)
    grade_parser.add_argument("--detector", required=True)
    grade_parser.add_argument("--attestation", required=True)
    grade_parser.add_argument("--public-key", required=True)
    grade_parser.add_argument("--review-packet", required=True)
    grade_parser.add_argument("--output")
    grade_parser.set_defaults(func=grade)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        return args.func(args)
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        print(f"ui-design-grader: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
