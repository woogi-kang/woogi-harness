#!/usr/bin/env python3
"""Validate a CIP image plan compiled by `image-prompt`.

Generation remains an agent action through Codex `$imagegen`. This command
owns output planning and provenance only.
"""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[5]
VALIDATOR = ROOT / ".claude/skills/image-prompt/scripts/check_prompt.mjs"


def load_jsonl(path: Path) -> list[dict]:
    records = []
    for line_number, line in enumerate(
        path.read_text(encoding="utf-8").splitlines(), 1
    ):
        if not line.strip():
            continue
        record = json.loads(line)
        if not isinstance(record, dict):
            raise SystemExit(f"record {line_number} is not an object")
        records.append(record)
    if not records:
        raise SystemExit("manifest has no records")
    return records


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate a Gongnyang CIP generation plan"
    )
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--brand-evidence", action="append", default=[])
    args = parser.parse_args()

    subprocess.run(
        ["node", str(VALIDATOR), "--jsonl", str(args.manifest)],
        check=True,
    )
    records = load_jsonl(args.manifest)
    args.output.mkdir(parents=True, exist_ok=True)
    plan = {
        "compiler": "image-prompt@2.3.0",
        "upstream_commit": "d1cd1dd3e77f7e12e2fed982fd738cc1ea880598",
        "generator": "image_gen__imagegen",
        "required_model": "gpt-image-2",
        "model_binding": "trusted-host-fixed",
        "local_model_verification": "unavailable",
        "host_reported_model": None,
        "generation_assurance": "pending_trusted_host_generation",
        "required_post_generation_assurance": "generated_under_trusted_host_contract",
        "status": "validated_awaiting_generation",
        "source_evidence": args.brand_evidence,
        "records": [
            {
                "id": record["id"],
                "prompt_record": f"{args.manifest}#{record['id']}",
                "output_path": record["output_path"],
            }
            for record in records
        ],
    }
    output = args.output / "cip-generation-plan.json"
    output.write_text(
        json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
