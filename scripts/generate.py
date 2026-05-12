#!/usr/bin/env python3
"""
generate.py — Daily content generator for auto-streak.
Runs inside GitHub Actions. Updates activity-log.json, stats.json,
and rewrites README.md with live stats + ASCII graph.
"""

import json
import os
import random
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

# ─── CONFIG ───────────────────────────────────────────────────────────────────

ROOT = Path(__file__).parent.parent
ACTIVITY_LOG = ROOT / "activity-log.json"
STATS_FILE = ROOT / "stats.json"
README_FILE = ROOT / "README.md"
COMMIT_MSG_FILE = Path("/tmp/commit_msg.txt")

COMMIT_COUNT = int(os.environ.get("COMMIT_COUNT", "1"))

# ─── DATA POOLS ───────────────────────────────────────────────────────────────

COMMIT_MESSAGES = [
    "chore: update daily activity log",
    "docs: refresh contribution stats",
    "chore: automated daily sync",
    "refactor: minor data cleanup",
    "docs: update streak metrics",
    "chore: daily health check passed",
    "perf: incremental log optimization",
    "chore: bump activity timestamp",
    "docs: daily report generated",
    "chore: streak engine heartbeat",
    "fix: resolve stale activity data",
    "chore: sync contribution graph",
    "build: daily artifact generation",
    "ci: scheduled maintenance pass",
    "docs: log rotation complete",
]

QUOTES = [
    "Code is like humor. When you have to explain it, it's bad. — Cory House",
    "First, solve the problem. Then, write the code. — John Johnson",
    "Any fool can write code that a computer can understand. Good programmers write code that humans can understand. — Martin Fowler",
    "Experience is the name everyone gives to their mistakes. — Oscar Wilde",
    "In order to be irreplaceable, one must always be different. — Coco Chanel",
    "The best time to plant a tree was 20 years ago. The second best time is now. — Chinese Proverb",
    "It always seems impossible until it's done. — Nelson Mandela",
    "The only way to do great work is to love what you do. — Steve Jobs",
    "Simplicity is the soul of efficiency. — Austin Freeman",
    "Make it work, make it right, make it fast. — Kent Beck",
    "Programs must be written for people to read, and only incidentally for machines to execute. — Abelson & Sussman",
    "The most dangerous phrase in the language is 'we've always done it this way'. — Grace Hopper",
    "Talk is cheap. Show me the code. — Linus Torvalds",
    "Perfection is achieved not when there is nothing more to add, but when there is nothing left to take away. — Antoine de Saint-Exupéry",
    "Every great developer you know got there by solving problems they were unqualified to solve until they did it. — Patrick McKenzie",
    "The function of good software is to make the complex appear to be simple. — Grady Booch",
    "One of the best programming skills you can have is knowing when to walk away for a while. — Oscar Godson",
    "Software is a great combination between artistry and engineering. — Bill Gates",
    "Clean code always looks like it was written by someone who cares. — Robert C. Martin",
    "A good programmer is someone who always looks both ways before crossing a one-way street. — Doug Linder",
]

MOODS = ["🚀 shipping", "☕ caffeinated", "🎯 focused", "⚡ in flow", "🔥 grinding", "🧠 thinking", "🌙 late-night", "🌅 early bird", "💡 inspired", "🎧 locked in"]

FAKE_METRICS = [
    ("lines_reviewed", lambda: random.randint(50, 400)),
    ("bugs_squashed", lambda: random.randint(0, 5)),
    ("prs_skimmed", lambda: random.randint(1, 8)),
    ("stack_overflow_tabs", lambda: random.randint(3, 20)),
    ("coffee_consumed_ml", lambda: random.randint(200, 600)),
    ("commits_pondered", lambda: random.randint(1, 10)),
    ("docs_written_lines", lambda: random.randint(10, 150)),
    ("tests_written", lambda: random.randint(0, 12)),
]

# ─── HELPERS ──────────────────────────────────────────────────────────────────

def now_utc() -> datetime:
    override = os.environ.get("OVERRIDE_DATE")
    if override:
        try:
            base_dt = datetime.strptime(override.strip(), "%Y-%m-%d").replace(tzinfo=timezone.utc)
            now = datetime.now(timezone.utc)
            return base_dt.replace(hour=now.hour, minute=now.minute, second=now.second, microsecond=now.microsecond)
        except ValueError:
            pass
    return datetime.now(timezone.utc)

def today_str() -> str:
    return now_utc().strftime("%Y-%m-%d")

def load_json(path: Path, default):
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            pass
    return default

def save_json(path: Path, data):
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

# ─── STATS ENGINE ─────────────────────────────────────────────────────────────

def update_stats(stats: dict) -> dict:
    today = today_str()
    last_date = stats.get("last_commit_date", "")

    if last_date == today:
        # Already ran today — just increment daily count
        stats["daily_commits"] = stats.get("daily_commits", 1) + 1
        return stats

    # Check if streak is still alive (last commit was yesterday)
    try:
        last_dt = datetime.strptime(last_date, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        yesterday = now_utc().replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=1)
        if last_dt.date() >= yesterday.date():
            stats["current_streak"] = stats.get("current_streak", 0) + 1
        else:
            stats["current_streak"] = 1  # streak broke, reset
    except (ValueError, TypeError):
        stats["current_streak"] = 1

    stats["total_commits"] = stats.get("total_commits", 0) + COMMIT_COUNT
    stats["total_days"] = stats.get("total_days", 0) + 1
    stats["longest_streak"] = max(stats.get("longest_streak", 0), stats["current_streak"])
    stats["last_commit_date"] = today
    stats["daily_commits"] = COMMIT_COUNT
    stats["last_mood"] = random.choice(MOODS)
    stats["started_at"] = stats.get("started_at", today)

    return stats

# ─── ACTIVITY LOG ─────────────────────────────────────────────────────────────

def update_activity_log(log: list, stats: dict) -> list:
    today = today_str()
    entry = {
        "date": today,
        "timestamp": now_utc().isoformat(),
        "commits": COMMIT_COUNT,
        "streak_day": stats["current_streak"],
        "mood": stats["last_mood"],
        "quote": random.choice(QUOTES),
        "metrics": {k: fn() for k, fn in random.sample(FAKE_METRICS, k=4)},
    }

    # Remove any existing entry for today (idempotent re-runs)
    log = [e for e in log if e.get("date") != today]
    log.append(entry)

    # Keep last 90 days only
    log = sorted(log, key=lambda e: e["date"])[-90:]
    return log

# ─── ASCII GRAPH ──────────────────────────────────────────────────────────────

def build_ascii_graph(log: list) -> str:
    """Build a 4-week ASCII contribution heatmap."""
    today = now_utc().date()
    # Build a dict of date -> commit count
    commit_map = {e["date"]: e["commits"] for e in log}

    # 28 days grid
    lines = []
    days_label = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
    shade = [" ", "░", "▒", "▓", "█"]  # 0, 1, 2, 3 commits

    # Header: week columns
    header = "     " + "  ".join([f"W{i+1}" for i in range(4)])
    lines.append(header)

    for dow in range(7):  # Sunday=0 ... Saturday=6
        row = f"{days_label[dow]}  "
        for week in range(4):
            days_ago = (3 - week) * 7 + (today.weekday() + 1 - dow) % 7
            target = today - timedelta(days=days_ago)
            count = commit_map.get(str(target), 0)
            idx = min(count, len(shade) - 1)
            row += shade[idx] + "  "
        lines.append(row)

    return "\n".join(lines)

# ─── README GENERATOR ─────────────────────────────────────────────────────────

def build_readme(stats: dict, log: list) -> str:
    today = today_str()
    streak = stats.get("current_streak", 1)
    longest = stats.get("longest_streak", streak)
    total_commits = stats.get("total_commits", COMMIT_COUNT)
    total_days = stats.get("total_days", 1)
    started = stats.get("started_at", today)
    mood = stats.get("last_mood", "🚀 shipping")

    # Last quote
    last_entry = log[-1] if log else {}
    quote = last_entry.get("quote", random.choice(QUOTES))

    # Streak fire emoji scale
    if streak >= 30:
        fire = "🔥🔥🔥"
    elif streak >= 14:
        fire = "🔥🔥"
    elif streak >= 7:
        fire = "🔥"
    else:
        fire = "✨"

    graph = build_ascii_graph(log)

    # Last 7 days activity table
    recent = sorted(log, key=lambda e: e["date"])[-7:]
    table_rows = ""
    for e in reversed(recent):
        bar = "█" * e["commits"] + "░" * (3 - e["commits"])
        table_rows += f"| {e['date']} | {e['commits']} | {bar} | {e['mood']} |\n"

    readme = f"""# 🔥 Auto Streak Engine

> *Keeping the graph green, one commit at a time.*

<!-- AUTO-GENERATED — DO NOT EDIT MANUALLY -->
<!-- Last updated: {now_utc().isoformat()} -->

---

## {fire} Current Status

| Metric | Value |
|--------|-------|
| 🗓️ Today | `{today}` |
| 🔥 Current Streak | **{streak} day{"s" if streak != 1 else ""}** |
| 🏆 Longest Streak | `{longest} days` |
| 📦 Total Commits | `{total_commits}` |
| 📅 Active Days | `{total_days}` |
| 🚀 Started | `{started}` |
| 🎭 Current Mood | {mood} |

---

## 📊 28-Day Contribution Map

```
{graph}

Legend: (space)=0  ░=1  ▒=2  ▓=3+
```

---

## 📅 Last 7 Days

| Date | Commits | Graph | Mood |
|------|---------|-------|------|
{table_rows}
---

## 💬 Today's Quote

> *{quote}*

---

## ⚙️ How This Works

This repo uses **GitHub Actions** with a daily `cron` schedule to automatically:

1. Run `scripts/generate.py` — generates new content, updates stats
2. Append a new entry to `activity-log.json`
3. Rewrite this README with fresh stats
4. Commit & push — keeping the contribution graph active

**Zero manual interaction required after initial setup.**

```
.
├── .github/
│   └── workflows/
│       └── auto-streak.yml   ← The scheduler
├── scripts/
│   └── generate.py           ← Content engine
├── activity-log.json         ← Append-only activity log
├── stats.json                ← Streak counter & metrics
└── README.md                 ← Auto-generated (this file)
```

---

## 🚀 Setup

See [SETUP.md](./SETUP.md) for full instructions.

---

*Auto-generated by streak-bot · {now_utc().strftime("%Y-%m-%d %H:%M")} UTC*
"""
    return readme.strip() + "\n"

# ─── LARGE COMMIT GENERATOR ───────────────────────────────────────────────────

def generate_large_commit_data():
    """Generates a large chunk of mock data to make the commit size huge so GitHub thinks it's real work."""
    import string
    
    mock_dir = ROOT / "mock_data"
    mock_dir.mkdir(exist_ok=True)
    
    # We write to a rotating file so the repo doesn't grow infinitely large.
    file_idx = random.randint(0, 5)
    mock_file = mock_dir / f"system_logs_{file_idx}.json"
    
    data = []
    lines_to_generate = random.randint(1500, 5000)
    for _ in range(lines_to_generate):
        data.append({
            "timestamp": now_utc().isoformat(),
            "level": random.choice(["INFO", "DEBUG", "WARN", "ERROR", "TRACE", "FATAL"]),
            "module": random.choice(["auth", "db", "api", "worker", "cache", "scheduler", "payment"]),
            "message": "".join(random.choices(string.ascii_letters + string.digits + " ", k=random.randint(20, 150))),
            "metrics": {
                "cpu_usage": random.uniform(0.1, 99.9),
                "mem_usage_mb": random.randint(100, 8000),
                "latency_ms": random.randint(1, 2500)
            }
        })
    
    save_json(mock_file, data)
    print(f"[generate.py] Generated large commit data: {len(data)} log entries in {mock_file.relative_to(ROOT)}")

# ─── ORGANIC RANDOMIZER ───────────────────────────────────────────────────────

def should_run(stats: dict) -> bool:
    """Decides if the script should actually commit right now."""
    today = today_str()
    last_date = stats.get("last_commit_date", "")
    daily_commits = stats.get("daily_commits", 0) if last_date == today else 0

    if daily_commits >= 3:
        # Cap at ~3 commits a day
        return False

    current_hour = now_utc().hour

    if daily_commits == 0:
        # We MUST commit today to keep the streak alive.
        # If it's getting late (after 20:00 UTC), force a commit.
        if current_hour >= 20:
            print("[generate.py] Getting late! Forcing a commit to save the streak.")
            return True
        
        # Otherwise, 1 in 10 chance per run. 
        # (If cron runs every 10 mins, it's 6 times an hour. Usually commits within 2-3 hours).
        return random.randint(1, 10) == 1
    else:
        # We already have at least 1 commit. We want maybe 1 or 2 more.
        # 1 in 25 chance to do additional commits.
        return random.randint(1, 25) == 1

# ─── MAIN ─────────────────────────────────────────────────────────────────────

def main():
    print(f"[generate.py] Running — {now_utc().isoformat()}")

    # Load existing data
    stats = load_json(STATS_FILE, {})
    
    # Decide organically whether to proceed
    force = "--force" in sys.argv
    if not force and not should_run(stats):
        print("[generate.py] Organic randomizer skipped this run. Staying stealthy.")
        return

    print(f"[generate.py] Commit count this run: {COMMIT_COUNT}")

    log = load_json(ACTIVITY_LOG, [])

    # Update stats
    stats = update_stats(stats)

    # Generate huge commit payload
    generate_large_commit_data()

    # Update activity log
    log = update_activity_log(log, stats)

    # Build README
    readme = build_readme(stats, log)

    # Save everything
    save_json(STATS_FILE, stats)
    save_json(ACTIVITY_LOG, log)
    README_FILE.write_text(readme, encoding="utf-8")

    # Pick a commit message and write to /tmp for the workflow to read
    msg = random.choice(COMMIT_MESSAGES)
    # Append streak day for extra uniqueness
    msg += f" [day {stats['current_streak']}]"
    try:
        COMMIT_MSG_FILE.parent.mkdir(parents=True, exist_ok=True)
        COMMIT_MSG_FILE.write_text(msg, encoding="utf-8")
    except Exception as e:
        print(f"[generate.py] Warning: Could not write commit msg to {COMMIT_MSG_FILE}: {e}")

    print(f"[generate.py] Streak day: {stats['current_streak']}")
    print(f"[generate.py] Commit message: {msg}")
    print("[generate.py] Done ✅")

if __name__ == "__main__":
    main()
