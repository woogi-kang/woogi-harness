#!/usr/bin/env python3
"""
Woogi Harness Integrity Check

Verifies the entire agent -> skill -> references chain:
  1. Agent -> Skill references
  2. Skill -> Reference file integrity
  3. Command -> Skill references
  4. Symlink health
  5. Orphan / unreferenced detection

Exit codes: 0 = all pass, 1 = warnings only, 2 = errors found
"""

import json
import os
import re
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CLAUDE_DIR = PROJECT_ROOT / ".claude"
AGENTS_DIR = CLAUDE_DIR / "agents"
SKILLS_DIR = CLAUDE_DIR / "skills"
COMMANDS_DIR = CLAUDE_DIR / "commands"

EXPECTED_SYMLINKS = [
    # (symlink_path, expected_target)
    (PROJECT_ROOT / ".agents" / "skills", Path("../.claude/skills")),
    (PROJECT_ROOT / "GEMINI.md", Path("CLAUDE.md")),
    (PROJECT_ROOT / "AGENTS.md", Path("CLAUDE.md")),
]

# Regex patterns to find file references inside markdown files
# Matches: `references/something.md`, `./references/something.md`, etc.
REF_PATTERNS = [
    re.compile(r'`(references/[^`]+)`'),
    re.compile(r'`(\./references/[^`]+)`'),
    re.compile(r'\(references/([^)]+)\)'),
    re.compile(r'\(\./references/([^)]+)\)'),
]

# Pattern to find skill name references in agent/command files
# Matches things like: skills/, .claude/skills/, /skills/ paths
SKILL_PATH_PATTERNS = [
    re.compile(r'(?:\.claude/skills|skills)/([^\s`"\')\]]+)'),
]

# Pattern to find skill names in YAML frontmatter (skills: list)
SKILL_NAME_PATTERN = re.compile(r'^\s*-\s+([\w-]+)\s*$', re.MULTILINE)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

class CheckResult:
    """Collects results for a single check category."""

    def __init__(self, name: str):
        self.name = name
        self.passed: list[str] = []
        self.warnings: list[str] = []
        self.errors: list[str] = []
        self.info: list[str] = []

    @property
    def ok(self) -> bool:
        return len(self.errors) == 0

    def summary_icon(self) -> str:
        if self.errors:
            return "[!]"
        if self.warnings:
            return "[~]"
        return "[✓]"


def read_text(path: Path) -> str:
    """Read a file with UTF-8 encoding, return empty string on failure."""
    try:
        return path.read_text(encoding="utf-8")
    except Exception:
        return ""


def find_md_files(directory: Path) -> list[Path]:
    """Recursively find all .md files under a directory."""
    if not directory.exists():
        return []
    return sorted(directory.rglob("*.md"))


def relative(path: Path) -> str:
    """Return path relative to PROJECT_ROOT for display."""
    try:
        return str(path.relative_to(PROJECT_ROOT))
    except ValueError:
        return str(path)


def extract_references_from_skill(skill_md_path: Path) -> list[tuple[str, int]]:
    """Extract reference file paths mentioned in a SKILL.md.

    Returns list of (ref_relative_path, line_number).
    The ref_relative_path is relative to the skill directory (parent of SKILL.md).
    """
    text = read_text(skill_md_path)
    results = []
    for line_no, line in enumerate(text.splitlines(), start=1):
        for pat in REF_PATTERNS:
            for match in pat.finditer(line):
                ref_path = match.group(1) if pat.groups else match.group(0)
                # Normalize leading ./
                ref_path = ref_path.lstrip("./")
                # Only care about references/ paths
                if ref_path.startswith("references/"):
                    # Skip template patterns like {subcommand}.md
                    if "{" in ref_path and "}" in ref_path:
                        continue
                    results.append((ref_path, line_no))
    return results


def collect_all_skill_dirs() -> list[Path]:
    """Collect all skill directories (directories that contain SKILL.md)."""
    result = []
    for skill_md in SKILLS_DIR.rglob("SKILL.md"):
        result.append(skill_md.parent)
    return sorted(set(result))


def extract_skill_refs_from_agent(agent_md_path: Path) -> list[str]:
    """Extract skill references from an agent .md file.

    Looks for:
    - YAML frontmatter `skills:` lists
    - Inline skill path references like `.claude/skills/foo` or `skills/foo`
    - Skill name references like `/ck:brand`, `/ckm:design`
    """
    text = read_text(agent_md_path)
    refs = set()

    # 1. YAML frontmatter skills list
    in_frontmatter = False
    in_skills_block = False
    for line in text.splitlines():
        if line.strip() == "---":
            if not in_frontmatter:
                in_frontmatter = True
                continue
            else:
                break  # end of frontmatter
        if in_frontmatter:
            if line.startswith("skills:"):
                in_skills_block = True
                continue
            if in_skills_block:
                m = SKILL_NAME_PATTERN.match(line)
                if m:
                    refs.add(m.group(1))
                elif not line.startswith(" ") and not line.startswith("\t"):
                    in_skills_block = False

    # 2. Path-based references to skills/
    for pat in SKILL_PATH_PATTERNS:
        for m in pat.finditer(text):
            skill_ref = m.group(1).rstrip("/").split("/")[0]
            if skill_ref and not skill_ref.startswith("_"):
                refs.add(skill_ref)

    # 3. Slash-command style: /ck:name, /ckm:name
    for m in re.finditer(r'/ck[m]?:([a-zA-Z0-9_-]+)', text):
        refs.add(m.group(1))

    return sorted(refs)


# ---------------------------------------------------------------------------
# Checks
# ---------------------------------------------------------------------------

def check_symlinks() -> CheckResult:
    """Check 4: Verify all expected symlinks are valid."""
    result = CheckResult("Symlinks")

    for symlink_path, expected_target in EXPECTED_SYMLINKS:
        display = relative(symlink_path)
        if not symlink_path.exists() and not symlink_path.is_symlink():
            result.errors.append(f"{display} does not exist")
            continue

        if not symlink_path.is_symlink():
            result.errors.append(f"{display} is not a symlink")
            continue

        actual_target = Path(os.readlink(symlink_path))
        # Resolve to check if valid
        try:
            resolved = symlink_path.resolve(strict=True)
            # Symlink is valid (resolves to existing target)
            if actual_target == expected_target:
                result.passed.append(f"{display} -> {expected_target}")
            else:
                # Target is different but still valid
                result.warnings.append(
                    f"{display} -> {actual_target} (expected {expected_target})"
                )
        except OSError:
            result.errors.append(f"{display} -> {actual_target} (broken symlink)")

    return result


def check_agent_skill_refs() -> CheckResult:
    """Check 1: Verify that agent files reference skills that exist."""
    result = CheckResult("Agent→Skill references")

    agent_files = find_md_files(AGENTS_DIR)
    all_skill_names = set()
    for d in collect_all_skill_dirs():
        # Build various name forms that might be referenced
        try:
            rel = d.relative_to(SKILLS_DIR)
            parts = list(rel.parts)
            # Add the full path name
            all_skill_names.add(str(rel))
            # Add just the leaf directory name
            all_skill_names.add(parts[-1])
            # Add the first part (category)
            all_skill_names.add(parts[0])
        except ValueError:
            pass

    # Also add top-level skill directories
    if SKILLS_DIR.exists():
        for item in SKILLS_DIR.iterdir():
            if item.is_dir():
                all_skill_names.add(item.name)

    valid_count = 0
    for agent_file in agent_files:
        skill_refs = extract_skill_refs_from_agent(agent_file)
        for ref in skill_refs:
            # Check if this ref matches any known skill name
            matched = False
            for name in all_skill_names:
                if ref == name or ref in name or name.endswith(ref):
                    matched = True
                    break
            # Also check if a directory with this name exists under skills/
            if not matched:
                # Direct path check
                for candidate in SKILLS_DIR.rglob("*"):
                    if candidate.is_dir() and candidate.name == ref:
                        matched = True
                        break

            if matched:
                valid_count += 1
                result.passed.append(
                    f"{relative(agent_file)} -> {ref}"
                )
            else:
                result.warnings.append(
                    f"{relative(agent_file)} references skill '{ref}' (not found in skills/)"
                )

    return result


def check_skill_references() -> CheckResult:
    """Check 2: Verify skill -> reference file integrity."""
    result = CheckResult("Skill→Reference files")

    skill_dirs = collect_all_skill_dirs()

    referenced_files: set[Path] = set()
    all_reference_files: set[Path] = set()

    for skill_dir in skill_dirs:
        skill_md = skill_dir / "SKILL.md"
        if not skill_md.exists():
            continue

        # Collect all files that exist in references/ subdirectory
        refs_dir = skill_dir / "references"
        if refs_dir.exists():
            for f in refs_dir.rglob("*"):
                if f.is_file():
                    all_reference_files.add(f)

        # Extract references from SKILL.md
        refs = extract_references_from_skill(skill_md)
        for ref_path, line_no in refs:
            full_path = (skill_dir / ref_path).resolve()
            referenced_files.add(full_path)

            if full_path.exists():
                result.passed.append(
                    f"{relative(skill_md)}: {ref_path}"
                )
            else:
                result.errors.append(
                    f"{relative(full_path)} (referenced in {relative(skill_md)} line {line_no})"
                )

    # Find orphan reference files (exist but never referenced)
    orphan_refs = all_reference_files - referenced_files
    # Filter: only flag .md files as orphans (ignore data files, scripts, etc.)
    for orphan in sorted(orphan_refs):
        if orphan.suffix == ".md":
            result.info.append(f"{relative(orphan)}")

    return result


def check_command_skill_refs() -> CheckResult:
    """Check 3: Verify command -> skill references."""
    result = CheckResult("Command→Skill references")

    if not COMMANDS_DIR.exists():
        result.info.append("No commands directory found")
        return result

    command_files = find_md_files(COMMANDS_DIR)
    all_skill_names = set()
    for d in collect_all_skill_dirs():
        try:
            rel = d.relative_to(SKILLS_DIR)
            all_skill_names.add(str(rel))
            all_skill_names.add(rel.parts[-1])
        except ValueError:
            pass
    if SKILLS_DIR.exists():
        for item in SKILLS_DIR.iterdir():
            if item.is_dir():
                all_skill_names.add(item.name)

    for cmd_file in command_files:
        text = read_text(cmd_file)
        # Look for skill references
        skill_refs = set()
        for m in re.finditer(r'/ck[m]?:([a-zA-Z0-9_-]+)', text):
            skill_refs.add(m.group(1))
        for pat in SKILL_PATH_PATTERNS:
            for m in pat.finditer(text):
                skill_ref = m.group(1).rstrip("/").split("/")[0]
                if skill_ref and not skill_ref.startswith("_"):
                    skill_refs.add(skill_ref)

        for ref in sorted(skill_refs):
            matched = any(
                ref == name or ref in name or name.endswith(ref)
                for name in all_skill_names
            )
            if not matched:
                for candidate in SKILLS_DIR.rglob("*"):
                    if candidate.is_dir() and candidate.name == ref:
                        matched = True
                        break

            if matched:
                result.passed.append(f"{relative(cmd_file)} -> {ref}")
            else:
                result.warnings.append(
                    f"{relative(cmd_file)} references skill '{ref}' (not found)"
                )

    if not result.passed and not result.warnings and not result.errors:
        result.info.append("No skill references found in commands")

    return result


def check_unreferenced_skills() -> CheckResult:
    """Check 5: Find skills not referenced by any agent or command."""
    result = CheckResult("Unreferenced skills")

    # Collect all skill directory names
    skill_dirs = collect_all_skill_dirs()

    # Collect all text from agents and commands
    all_text = ""
    for md in find_md_files(AGENTS_DIR):
        all_text += read_text(md) + "\n"
    if COMMANDS_DIR.exists():
        for md in find_md_files(COMMANDS_DIR):
            all_text += read_text(md) + "\n"
    # Also check SKILL.md files themselves (skills can reference other skills)
    for sd in skill_dirs:
        skill_md = sd / "SKILL.md"
        if skill_md.exists():
            all_text += read_text(skill_md) + "\n"

    all_text_lower = all_text.lower()

    for skill_dir in skill_dirs:
        try:
            rel = skill_dir.relative_to(SKILLS_DIR)
        except ValueError:
            continue

        skill_name = skill_dir.name
        # Check if skill name appears anywhere in agents/commands/other skills
        # Use case-insensitive search on the leaf name
        if skill_name.lower() in all_text_lower:
            result.passed.append(f"{relative(skill_dir)}")
        else:
            # Also try partial matches for hyphenated names
            parts = skill_name.split("-")
            found = False
            if len(parts) > 1:
                # Check if the joined form appears
                joined = "".join(parts)
                if joined.lower() in all_text_lower:
                    found = True
            if not found:
                result.info.append(f"{relative(skill_dir)}")

    return result


# ---------------------------------------------------------------------------
# Report
# ---------------------------------------------------------------------------

def print_report(checks: list[CheckResult]) -> int:
    """Print the report and return exit code."""
    print("=== Woogi Harness Integrity Check ===")
    print()

    total_checks = len(checks)
    passed_checks = 0
    total_warnings = 0
    total_errors = 0

    for check in checks:
        icon = check.summary_icon()
        n_passed = len(check.passed)
        n_total = n_passed + len(check.errors)

        # Header line
        if check.errors:
            if n_total > 0:
                print(f"{icon} {check.name}: {len(check.errors)} broken references")
            else:
                print(f"{icon} {check.name}: {len(check.errors)} errors")
        elif check.warnings:
            print(f"{icon} {check.name}: {n_passed} valid, {len(check.warnings)} warnings")
        else:
            if n_total > 0:
                print(f"{icon} {check.name}: {n_passed}/{n_total} valid")
            else:
                print(f"{icon} {check.name}: OK")

        # Detail lines
        for err in check.errors:
            print(f"    - {err}")
            total_errors += 1

        for warn in check.warnings:
            print(f"    ~ {warn}")
            total_warnings += 1

        if check.info:
            if check.name == "Unreferenced skills":
                print(f"[i] {check.name}: {len(check.info)} skills not referenced by any agent or command")
            elif "Orphan" in check.name or check.info:
                if any("orphan" in i.lower() or "references/" in i for i in check.info):
                    pass  # handled below
            for item in check.info:
                print(f"    - {item}")

        if check.ok and not check.warnings:
            passed_checks += 1

        print()

    # If there are orphan reference files from the skill check, print them separately
    for check in checks:
        if check.name == "Skill→Reference files" and check.info:
            print(f"[i] Orphan references: {len(check.info)} files not referenced by any SKILL.md")
            for item in check.info:
                print(f"    - {item}")
            print()

    # Summary
    print("=== Summary ===")
    print(f"Checks passed: {passed_checks}/{total_checks}")
    if total_warnings:
        print(f"Warnings: {total_warnings}")
    if total_errors:
        print(f"Errors: {total_errors}")

    if not total_warnings and not total_errors:
        print("All checks passed!")

    if total_errors:
        return 2
    elif total_warnings:
        return 1
    return 0


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    checks = [
        check_symlinks(),
        check_agent_skill_refs(),
        check_skill_references(),
        check_command_skill_refs(),
        check_unreferenced_skills(),
    ]
    return print_report(checks)


if __name__ == "__main__":
    sys.exit(main())
