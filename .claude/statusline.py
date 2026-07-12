#!/usr/bin/env python3
"""
Claude Code Status Line - Cost Tracking Script
Displays session cost, daily cost, context usage, and hourly rate in the status line.

The script consumes Claude Code's official ``model.display_name``,
``cost.total_cost_usd``, ``cost.total_duration_ms``, and
``context_window.used_percentage`` fields. It never guesses model names or
pricing for unknown models.
"""

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# Cost tracking file location
TRACKING_FILE = Path.home() / ".claude" / "cost_tracking.json"


def load_tracking_data() -> dict:
    """Load cost tracking data from file."""
    default_data = {"sessions": {}, "daily": {}, "current_block": None}

    if not TRACKING_FILE.exists():
        return default_data

    try:
        with open(TRACKING_FILE, "r") as f:
            data = json.load(f)

        # Migrate old format (list -> dict for sessions)
        for date_key, daily_entry in data.get("daily", {}).items():
            sessions = daily_entry.get("sessions", {})
            if isinstance(sessions, list):
                new_sessions = {}
                for sid in sessions:
                    if sid in data.get("sessions", {}):
                        new_sessions[sid] = data["sessions"][sid].get("total_cost", 0.0)
                daily_entry["sessions"] = new_sessions

        return data
    except (json.JSONDecodeError, IOError):
        return default_data


def save_tracking_data(data: dict):
    """Save cost tracking data to file."""
    try:
        with open(TRACKING_FILE, "w") as f:
            json.dump(data, f, indent=2, default=str)
    except IOError:
        pass


def get_model_display(model) -> str:
    """Use the provider-supplied display name without family/version guessing."""
    if not isinstance(model, dict):
        return "Claude"

    display_name = model.get("display_name")
    model_id = model.get("id")
    if isinstance(display_name, str) and display_name.strip():
        return display_name.strip()
    if isinstance(model_id, str) and model_id.strip():
        return model_id.strip()
    return "Unknown model"


def get_git_branch() -> str | None:
    """Get current git branch name."""
    try:
        result = subprocess.run(
            ["git", "branch", "--show-current"],
            capture_output=True,
            text=True,
            timeout=2,
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        pass
    return None


def get_context_progress(context_window: dict, max_context: int = 200_000) -> str:
    """Generate context usage progress bar."""
    if not isinstance(context_window, dict):
        return "📊 [░░░░░░░░░░] 0%"

    official_percent = context_window.get("used_percentage")
    if isinstance(official_percent, (int, float)):
        percent = min(100, max(0, float(official_percent)))
    else:
        current_usage = context_window.get("current_usage") or {}
        input_used = sum(
            current_usage.get(key, 0) or 0
            for key in (
                "input_tokens",
                "cache_creation_input_tokens",
                "cache_read_input_tokens",
            )
        )
        max_ctx = context_window.get("context_window_size", max_context) or max_context
        percent = min(100, (input_used / max_ctx) * 100)

    # Generate progress bar (10 chars)
    filled = int(percent / 10)
    bar = "█" * filled + "░" * (10 - filled)

    # Color indicator based on usage
    if percent >= 80:
        icon = "🔴"
    elif percent >= 60:
        icon = "🟡"
    else:
        icon = "🟢"

    return f"{icon} [{bar}] {percent:.0f}%"


def main():
    try:
        # 1. Read JSON from stdin
        input_data = json.load(sys.stdin)

        # 2. Extract basic info (with None checks)
        model = input_data.get("model") or {}
        session_id = input_data.get("session_id") or "default"
        context_window = input_data.get("context_window") or {}

        model_display = get_model_display(model)
        cost = input_data.get("cost") or {}

        # 3. Load tracking data
        tracking_data = load_tracking_data()
        now = datetime.now()
        today_str = now.strftime("%Y-%m-%d")

        # 4. Calculate session cost
        session_cost = float(cost.get("total_cost_usd") or 0.0)

        # 5. Update session data
        if session_id not in tracking_data["sessions"]:
            tracking_data["sessions"][session_id] = {
                "start_time": now.isoformat(),
                "date": today_str,
                "total_cost": 0.0,
                "last_update": now.isoformat(),
            }

        session_data = tracking_data["sessions"][session_id]
        session_data["total_cost"] = session_cost
        session_data["last_update"] = now.isoformat()

        # 6. Update daily data
        if today_str not in tracking_data["daily"]:
            tracking_data["daily"][today_str] = {"sessions": {}, "total": 0.0}

        daily_data = tracking_data["daily"][today_str]
        daily_data["sessions"][session_id] = session_cost
        today_cost = sum(daily_data["sessions"].values())
        daily_data["total"] = today_cost

        # 7. Calculate session elapsed time for hourly rate
        session_start_str = session_data.get("start_time", now.isoformat())
        try:
            session_start = datetime.fromisoformat(session_start_str)
        except (ValueError, TypeError):
            session_start = now

        official_duration_ms = cost.get("total_duration_ms")
        if isinstance(official_duration_ms, (int, float)) and official_duration_ms >= 0:
            elapsed_seconds = float(official_duration_ms) / 1000
        else:
            elapsed_seconds = (now - session_start).total_seconds()
        elapsed_minutes = elapsed_seconds / 60
        elapsed_hours = elapsed_seconds / 3600

        # 8. Calculate hourly rate (only if 5+ minutes elapsed)
        if elapsed_minutes >= 5 and elapsed_hours > 0:
            hourly_rate = session_cost / elapsed_hours
            rate_str = f"🔥 ${hourly_rate:.2f}/hr"
        else:
            rate_str = f"⏱️ ~{int(elapsed_minutes)}m"

        # 9. Save data
        save_tracking_data(tracking_data)

        # 10. Get git branch
        git_branch = get_git_branch()
        branch_str = f" | 🌿 {git_branch}" if git_branch else ""

        # 11. Get context usage progress
        context_str = get_context_progress(context_window)

        # 12. Output status line
        status = f"🤖 {model_display}{branch_str} | {context_str} | {rate_str} | 💰 ${today_cost:.2f} today"
        print(status)

    except Exception as e:
        # Fallback output on error
        print(f"🤖 Claude | ⚠️ Error: {str(e)[:30]}")


if __name__ == "__main__":
    main()
