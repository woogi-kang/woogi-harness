from __future__ import annotations

import hashlib
import json
import struct
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SMOKE_ROOT = ROOT / "docs" / "260713-harness-v3-image-smoke-test"


class ImageSmokeManifestTest(unittest.TestCase):
    def test_manifest_is_complete_hash_bound_and_honest(self) -> None:
        manifest = json.loads(
            (SMOKE_ROOT / "image-generation-manifest.json").read_text(encoding="utf-8")
        )
        prompts = SMOKE_ROOT / "prompts.jsonl"
        self.assertEqual(
            manifest["prompt_source"]["sha256"],
            hashlib.sha256(prompts.read_bytes()).hexdigest(),
        )
        contract = manifest["generation_contract"]
        self.assertEqual(contract["generator"], "image_gen__imagegen")
        self.assertEqual(contract["required_model"], "gpt-image-2")
        self.assertEqual(contract["fallback"], [])
        self.assertIsNone(contract["host_reported_model"])
        self.assertEqual(
            contract["generation_assurance"], "generated_under_trusted_host_contract"
        )

        artifacts = manifest["artifacts"]
        self.assertEqual(len(artifacts), 5)
        for artifact in artifacts:
            path = ROOT / artifact["path"]
            data = path.read_bytes()
            self.assertEqual(hashlib.sha256(data).hexdigest(), artifact["sha256"])
            self.assertEqual(len(data), artifact["bytes"])
            self.assertEqual(data[:8], b"\x89PNG\r\n\x1a\n")
            width, height = struct.unpack(">II", data[16:24])
            self.assertEqual({"width": width, "height": height}, artifact["dimensions"])

        approved = [item for item in artifacts if item["status"].startswith("approved")]
        rejected = [item for item in artifacts if item["status"] == "rejected"]
        self.assertEqual((len(approved), len(rejected)), (4, 1))
        self.assertEqual(rejected[0]["id"], "C11-HARNESS-SHADOW-001")
        self.assertIn("프롬프트에 없던", rejected[0]["review"])
        self.assertEqual(
            manifest["summary"],
            {
                "generated": 5,
                "approved": 4,
                "rejected": 1,
                "post_generation_text_overlay": False,
            },
        )


if __name__ == "__main__":
    unittest.main()
