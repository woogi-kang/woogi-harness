#!/usr/bin/env python3
"""Sync Woogi Harness skills to Multica platform."""

import json
import re
import subprocess
import sys
from pathlib import Path

SKILLS_DIR = Path(__file__).parent.parent / ".claude" / "skills"
DRY_RUN = "--dry-run" in sys.argv
FILTER = ""
for i, arg in enumerate(sys.argv):
    if arg == "--filter" and i + 1 < len(sys.argv):
        FILTER = sys.argv[i + 1]

success = 0
failed = 0
skipped = 0

# Domain prefix mapping based on parent directory
DOMAIN_PREFIX_MAP = {
    "💻 개발": "",
    "🎯 기획": "plan",
    "🎨 디자인": "design",
    "📝 콘텐츠": "content",
    "📣 마케팅": "mkt",
    "⚖️ 법무": "legal",
    "💰 재무": "fin",
    "🔍 리뷰": "review",
    "🇰🇷 k-skill": "kr",
}

# Sub-domain prefix for dev skills
DEV_PREFIX_MAP = {
    "fastapi-agent-skills": "fastapi",
    "flutter-agent-skills": "flutter",
    "nextjs-agent-skills": "nextjs",
    "flutter-to-nextjs-skills": "f2n",
    "_shared": "shared",
}

# Sub-domain prefix for planning sub-skills
PLAN_SUB_PREFIX_MAP = {
    "planning-agent-skills": "plan",
}


def get_domain_prefix(rel_path: Path) -> str:
    """Derive domain prefix from directory structure to avoid name collisions."""
    parts = list(rel_path.parts)
    if len(parts) < 2:
        return ""

    # Check top-level domain
    top = parts[0]
    prefix = DOMAIN_PREFIX_MAP.get(top, "")

    # Check sub-domain (dev skills, planning skills, etc.)
    for part in parts:
        if part in DEV_PREFIX_MAP:
            return DEV_PREFIX_MAP[part]
        if part in PLAN_SUB_PREFIX_MAP:
            return PLAN_SUB_PREFIX_MAP[part]

    # For other domain sub-skills (e.g. 📝 콘텐츠/social-media-agent-skills/)
    # use the agent name as prefix
    for part in parts[1:]:
        if part.endswith("-skills") or part.endswith("-agent-skills"):
            short = part.replace("-agent-skills", "").replace("-skills", "")
            return short

    return prefix


def parse_frontmatter(content: str) -> dict:
    """Extract name and description from YAML frontmatter."""
    fm_match = re.match(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
    if not fm_match:
        return {}
    fm = fm_match.group(1)
    result = {}
    for key in ("name", "description"):
        m = re.search(rf'^{key}:\s*"?([^"\n]+)"?\s*$', fm, re.MULTILINE)
        if m:
            result[key] = m.group(1).strip().strip('"').strip("'")
    return result


def get_existing_skills() -> set:
    """Get names of already registered skills."""
    try:
        out = subprocess.check_output(
            ["multica", "skill", "list", "--output", "json"],
            text=True,
            stderr=subprocess.DEVNULL,
        )
        data = json.loads(out)
        return {s["name"] for s in data} if data else set()
    except Exception:
        return set()


def register_skill(name: str, description: str, content: str) -> bool:
    """Register a skill to Multica."""
    try:
        result = subprocess.run(
            [
                "multica", "skill", "create",
                "--name", name,
                "--description", description[:200],
                "--content", content,
                "--output", "json",
            ],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if '"id"' in result.stdout:
            return True
        print(f"    Error: {result.stderr or result.stdout}")
        return False
    except Exception as e:
        print(f"    Error: {e}")
        return False


def main():
    global success, failed, skipped

    print("=== Multica Skill Sync ===")
    print(f"Skills dir: {SKILLS_DIR}")
    print(f"Dry run: {DRY_RUN}")
    if FILTER:
        print(f"Filter: {FILTER}")
    print()

    existing = get_existing_skills()
    print(f"Existing skills in Multica: {len(existing)}")
    print()

    skill_files = sorted(SKILLS_DIR.rglob("SKILL.md"))
    print(f"Found {len(skill_files)} SKILL.md files")
    print()

    seen_names: set[str] = set()

    for skill_file in skill_files:
        rel = skill_file.relative_to(SKILLS_DIR)

        # Skip templates
        if "_template" in str(rel):
            skipped += 1
            continue

        # Apply filter
        if FILTER and FILTER not in str(rel):
            continue

        content = skill_file.read_text()
        meta = parse_frontmatter(content)

        name = meta.get("name", "")
        if not name:
            print(f"⚠ SKIP (no name): {rel}")
            skipped += 1
            continue

        # Clean prefix and add domain prefix for uniqueness
        clean_name = re.sub(r"^ckm:", "", name)
        domain_prefix = get_domain_prefix(rel)
        if domain_prefix and not clean_name.startswith(domain_prefix):
            clean_name = f"{domain_prefix}-{clean_name}"

        # If still duplicate, append parent dir number (e.g. 44-monetization → plan-pricing-strategy-44)
        if clean_name in seen_names:
            for part in rel.parts:
                m = re.match(r"^(\d+)-", part)
                if m:
                    clean_name = f"{clean_name}-{m.group(1)}"
                    break
            else:
                clean_name = f"{clean_name}-{len(seen_names)}"

        seen_names.add(clean_name)
        description = meta.get("description", "No description")

        # Check duplicate
        if clean_name in existing:
            print(f"⏭ EXISTS: {clean_name}")
            skipped += 1
            continue

        if DRY_RUN:
            print(f"🔍 DRY: {clean_name} — {description[:60]}")
            success += 1
        else:
            if register_skill(clean_name, description, content):
                print(f"✅ {clean_name}")
                existing.add(clean_name)
                success += 1
            else:
                print(f"❌ FAIL: {clean_name}")
                failed += 1

    print()
    print("=== Done ===")
    print(f"{'Would register' if DRY_RUN else 'Success'}: {success} | Skipped: {skipped} | Failed: {failed}")


if __name__ == "__main__":
    main()
