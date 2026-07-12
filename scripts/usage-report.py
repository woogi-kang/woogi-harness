#!/usr/bin/env python3
"""
Claude Craft Usage Report

Reads .claude/logs/usage.jsonl and generates a summary:
  - Most used agents/skills
  - Usage by tool type
  - Usage over time (daily)

Current log format (written by .claude/hooks/usage-tracker.sh):
  {"schema_version":"harness.telemetry.v1", "subject_type":"agent|skill", ...}

The loader also accepts the legacy pretty-printed concatenated JSON format.

Requires no external dependencies (stdlib only).
"""

import sys
from collections import Counter, defaultdict
from pathlib import Path

from harness_runtime_lib import (
    HarnessError,
    normalize_telemetry_event,
    read_json_stream,
)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
LOG_FILE = PROJECT_ROOT / ".claude" / "logs" / "usage.jsonl"


def load_entries(path: Path = LOG_FILE) -> list[dict]:
    """Load v1 JSONL and the legacy concatenated pretty-JSON format."""
    return [normalize_telemetry_event(entry) for entry in read_json_stream(path)]


def generate_report(entries: list[dict]) -> None:
    """Print a formatted usage report."""
    if not entries:
        print("=== Claude Craft Usage Report ===")
        print()
        print("No usage data found.")
        print(f"Log file: {LOG_FILE}")
        print()
        print("Logging is automatic via PostToolUse hook (Agent|Skill).")
        print("Configured in: .claude/settings.json")
        return

    print("=== Claude Craft Usage Report ===")
    print(f"Total entries: {len(entries)}")

    # Date range
    timestamps = [e.get("timestamp", "")[:10] for e in entries if e.get("timestamp")]
    if timestamps:
        print(f"Period: {min(timestamps)} ~ {max(timestamps)}")
    print()

    # ---- Usage by tool type ----
    by_tool: Counter = Counter()
    by_name: Counter = Counter()
    by_date: Counter = Counter()
    tool_names: dict[str, Counter] = defaultdict(Counter)
    agent_types: Counter = Counter()

    for entry in entries:
        tool = entry.get("subject_type", entry.get("tool", "unknown"))
        name = entry.get("subject_id", entry.get("name", "unknown"))
        timestamp = entry.get("timestamp", "")

        by_tool[tool] += 1
        by_name[name] += 1
        tool_names[tool][name] += 1

        if tool == "agent":
            subtype = entry.get("metadata", {}).get(
                "subagent_type", entry.get("subagent_type", "general-purpose")
            )
            agent_types[subtype] += 1

        if timestamp:
            by_date[timestamp[:10]] += 1

    # ---- By Tool Type ----
    print("--- By Tool Type ---")
    print()
    for tool, count in by_tool.most_common():
        print(f"  {tool:20s}  {count:>5d}")
    print()

    # ---- Most Used (top 15) ----
    print("--- Most Used (Top 15) ---")
    print()
    for name, count in by_name.most_common(15):
        print(f"  {count:>5d}  {name}")
    print()

    # ---- Agent Types ----
    if agent_types:
        print("--- Agent Types ---")
        print()
        for subtype, count in agent_types.most_common():
            print(f"  {count:>5d}  {subtype}")
        print()

    # ---- Top per Tool Type ----
    for tool in sorted(tool_names.keys()):
        names = tool_names[tool]
        top = names.most_common(10)
        print(f"--- Top {tool}s ---")
        print()
        for name, count in top:
            print(f"  {count:>5d}  {name}")
        print()

    # ---- Least Used ----
    least = by_name.most_common()
    least.reverse()
    least_items = least[:10]
    if least_items:
        print("--- Least Used (Bottom 10) ---")
        print()
        for name, count in least_items:
            print(f"  {count:>5d}  {name}")
        print()

    # ---- Daily Usage ----
    if by_date:
        print("--- Daily Usage ---")
        print()
        for date_str in sorted(by_date.keys()):
            count = by_date[date_str]
            bar = "#" * min(count, 60)
            print(f"  {date_str}  {count:>4d}  {bar}")
        print()

    # ---- Sessions ----
    sessions = set(e.get("session_id") for e in entries if e.get("session_id"))
    if sessions:
        print(f"--- Sessions: {len(sessions)} unique ---")
        print()


def main() -> int:
    try:
        entries = load_entries()
    except HarnessError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    generate_report(entries)
    return 0


if __name__ == "__main__":
    sys.exit(main())
