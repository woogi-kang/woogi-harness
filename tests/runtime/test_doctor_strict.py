from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


class StrictDoctorTest(unittest.TestCase):
    def run_doctor(self, target: Path) -> tuple[subprocess.CompletedProcess[str], dict]:
        process = subprocess.run(
            [
                sys.executable,
                str(target / "scripts" / "harness-doctor.py"),
                "--root",
                str(target),
                "--strict",
                "--json",
            ],
            cwd=target,
            check=False,
            capture_output=True,
            text=True,
        )
        return process, json.loads(process.stdout)

    def test_strict_doctor_executes_verifiers_and_graders(self) -> None:
        with tempfile.TemporaryDirectory(
            prefix="harness-doctor-adversarial-"
        ) as temporary:
            target = Path(temporary) / "target"
            target.mkdir()
            subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "harness-sync.py"),
                    str(target),
                    "--apply",
                ],
                cwd=ROOT,
                check=True,
                capture_output=True,
                text=True,
            )

            verifier = target / "scripts" / "verify-stack-registry.py"
            verifier_source = verifier.read_text(encoding="utf-8")
            verifier.write_text("raise SystemExit(97)\n", encoding="utf-8")
            process, payload = self.run_doctor(target)
            self.assertNotEqual(process.returncode, 0)
            checks = {item["name"]: item for item in payload["checks"]}
            self.assertEqual(checks["tech-stack-registry"]["status"], "error")
            verifier.write_text(verifier_source, encoding="utf-8")

            ui_grader = target / ".claude" / "evals" / "ui-design" / "grader.py"
            ui_source = ui_grader.read_text(encoding="utf-8")
            ui_grader.write_text("raise SystemExit(98)\n", encoding="utf-8")
            process, payload = self.run_doctor(target)
            self.assertNotEqual(process.returncode, 0)
            checks = {item["name"]: item for item in payload["checks"]}
            self.assertEqual(checks["evals"]["status"], "error")
            ui_grader.write_text(ui_source, encoding="utf-8")

            korean_grader = (
                target / ".claude" / "evals" / "korean-typography" / "grader.sh"
            )
            original_mode = korean_grader.stat().st_mode
            korean_grader.chmod(0o644)
            process, payload = self.run_doctor(target)
            self.assertNotEqual(process.returncode, 0)
            checks = {item["name"]: item for item in payload["checks"]}
            self.assertEqual(checks["evals"]["status"], "error")
            korean_grader.chmod(original_mode)

    def test_strict_doctor_respects_profile_protected_agents_file(self) -> None:
        with tempfile.TemporaryDirectory(
            prefix="harness-doctor-protected-agents-"
        ) as temporary:
            target = Path(temporary) / "target"
            target.mkdir()
            subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "harness-sync.py"),
                    str(target),
                    "--apply",
                ],
                cwd=ROOT,
                check=True,
                capture_output=True,
                text=True,
            )
            agents = target / "AGENTS.md"
            agents.unlink()
            agents.write_text("# Workspace persona\n", encoding="utf-8")
            projects_path = (
                target / ".claude" / "registry" / "projects" / "projects.json"
            )
            projects = json.loads(projects_path.read_text(encoding="utf-8"))
            projects["projects"].append(
                {
                    "id": "protected-test",
                    "path": str(target),
                    "profile": ".claude/registry/projects/openclaw.json",
                    "enabled": True,
                }
            )
            projects_path.write_text(
                json.dumps(projects, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )

            process, payload = self.run_doctor(target)
            self.assertEqual(process.returncode, 0, process.stderr)
            checks = {item["name"]: item for item in payload["checks"]}
            self.assertEqual(checks["link:AGENTS.md"]["status"], "pass")
            self.assertEqual(
                checks["link:AGENTS.md"]["message"],
                "protected project file preserved",
            )


if __name__ == "__main__":
    unittest.main()
