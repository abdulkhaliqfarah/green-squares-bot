"""🎨 pixel_art.py — draw a shape or spell out a short pattern on your GitHub
contribution graph, the classic "gitfiti" trick.

GitHub's contribution graph is a 7-row (Sun..Sat, top to bottom) grid where
each column is one week. To "light up" a cell you just need a commit whose
author/committer date falls on that exact day — GitHub doesn't care when the
commit was actually pushed, only what date is recorded in it.

This script:
  1. Takes a starting Sunday and a pattern (a built-in shape, or your own
     pattern file).
  2. For every "on" pixel, makes a small number of backdated commits on the
     matching date (more commits = a darker green cell).
  3. Defaults to --dry-run, which prints the exact plan (dates + commit
     counts) without touching git at all.

This never rewrites or deletes existing commits — it only ever appends new
ones with an explicit historical --date, same as any other backfill.

Usage:
    python pixel_art.py --preview heart
    python pixel_art.py --pattern heart --start-date 2026-08-02 --dry-run
    python pixel_art.py --pattern heart --start-date 2026-08-02 --commit --push
"""

from __future__ import annotations

import argparse
import datetime
import os
import subprocess
import sys
from pathlib import Path

GRAPH_ROWS = 7  # one row per weekday, Sunday=0 .. Saturday=6
DEFAULT_TARGET_FILE = "pixel_art_log.txt"

# A handful of small, hand-verified shapes. Each is exactly 7 rows tall (one
# row per weekday) and every row is a palindrome, so each shape is guaranteed
# horizontally symmetric — easy to sanity-check just by reading it.
BUILTIN_PATTERNS: dict[str, list[str]] = {
    "heart": [
        ".##.##.",
        "#######",
        "#######",
        "#######",
        ".#####.",
        "..###..",
        "...#...",
    ],
    "diamond": [
        "...#...",
        "..###..",
        ".#####.",
        "#######",
        ".#####.",
        "..###..",
        "...#...",
    ],
    "square": [
        "#######",
        "#######",
        "#######",
        "#######",
        "#######",
        "#######",
        "#######",
    ],
    "frame": [
        "#######",
        "#.....#",
        "#.....#",
        "#.....#",
        "#.....#",
        "#.....#",
        "#######",
    ],
}

# Roughly-observed GitHub contribution-graph shading tiers. GitHub doesn't
# publish exact thresholds and they can change, so treat these as "probably
# looks lighter/darker", not a precise guarantee.
INTENSITY_TO_COMMIT_COUNT = {1: 2, 2: 5, 3: 8, 4: 12}


class PatternError(ValueError):
    """Raised when a pattern is malformed or a name/file can't be resolved."""


def load_pattern(name_or_path: str) -> list[str]:
    """Resolve a built-in pattern name or a custom pattern file into row strings."""
    if name_or_path in BUILTIN_PATTERNS:
        return BUILTIN_PATTERNS[name_or_path]

    path = Path(name_or_path)
    if not path.exists():
        available = ", ".join(sorted(BUILTIN_PATTERNS))
        raise PatternError(
            f"{name_or_path!r} is not a built-in pattern ({available}) and no such file exists."
        )
    rows = [line.rstrip("\n") for line in path.read_text().splitlines() if line.strip("\n") != ""]
    return validate_pattern(rows)


def validate_pattern(rows: list[str]) -> list[str]:
    """Ensure a pattern is exactly GRAPH_ROWS tall and rectangular."""
    if len(rows) != GRAPH_ROWS:
        raise PatternError(
            f"Pattern must have exactly {GRAPH_ROWS} rows (one per weekday), got {len(rows)}."
        )
    width = len(rows[0])
    if any(len(row) != width for row in rows):
        raise PatternError("All pattern rows must be the same width.")
    return rows


def next_sunday_on_or_after(date: datetime.date) -> datetime.date:
    """Return `date` itself if it's a Sunday, otherwise the next Sunday."""
    sunday_based_weekday = date.isoweekday() % 7  # isoweekday: Mon=1..Sun=7 -> Sun=0..Sat=6
    days_until_sunday = (7 - sunday_based_weekday) % 7
    return date + datetime.timedelta(days=days_until_sunday)


def pattern_to_dates(pattern: list[str], start_sunday: datetime.date) -> list[datetime.date]:
    """Map every "on" pixel in `pattern` to the calendar date of its graph cell."""
    if start_sunday.isoweekday() != 7:
        raise PatternError(f"{start_sunday} is not a Sunday.")

    width = len(pattern[0])
    dates: list[datetime.date] = []
    for col in range(width):
        for row in range(GRAPH_ROWS):
            if pattern[row][col] not in (" ", ".", "·"):
                dates.append(start_sunday + datetime.timedelta(weeks=col, days=row))
    return sorted(dates)


def render_preview(pattern: list[str]) -> str:
    """Render a pattern as readable ASCII (on -> '█', off -> '·')."""
    lines = []
    for row in pattern:
        lines.append("".join("█" if ch not in (" ", ".", "·") else "·" for ch in row))
    return "\n".join(lines)


def build_plan(
    pattern: list[str], start_sunday: datetime.date, commits_per_cell: int
) -> list[tuple[datetime.date, int]]:
    """Return [(date, commit_count), ...] for every lit cell, oldest date first."""
    return [(date, commits_per_cell) for date in pattern_to_dates(pattern, start_sunday)]


def make_backdated_commit(
    date: datetime.date, index: int, target_file: str, repo_dir: Path
) -> None:
    """Append a line to `target_file` and commit it with an explicit historical date."""
    commit_time = datetime.datetime.combine(date, datetime.time(12, 0, 0))
    date_str = commit_time.strftime("%Y-%m-%dT%H:%M:%S")

    with open(repo_dir / target_file, "a") as f:
        f.write(f"[{date_str}] pixel art commit #{index}\n")

    env = os.environ.copy()
    env["GIT_AUTHOR_DATE"] = date_str
    env["GIT_COMMITTER_DATE"] = date_str

    subprocess.run(["git", "add", target_file], cwd=repo_dir, check=True)
    subprocess.run(
        ["git", "commit", "-m", f"🎨 pixel art ({date.isoformat()})"],
        cwd=repo_dir,
        env=env,
        check=True,
    )


def run(args: argparse.Namespace) -> int:
    if args.preview:
        try:
            pattern = load_pattern(args.preview)
        except PatternError as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 1
        print(render_preview(pattern))
        return 0

    if not args.pattern:
        print("error: --pattern (or --preview) is required", file=sys.stderr)
        return 1

    try:
        pattern = load_pattern(args.pattern)
    except PatternError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    start = args.start_date or datetime.date.today()
    start_sunday = next_sunday_on_or_after(start)
    if start_sunday != start:
        print(f"note: {start} isn't a Sunday, using {start_sunday} instead.")

    commits_per_cell = INTENSITY_TO_COMMIT_COUNT[args.intensity]
    plan = build_plan(pattern, start_sunday, commits_per_cell)
    total_commits = sum(count for _, count in plan)

    print(f"Pattern: {args.pattern}  ({len(plan)} cells, {total_commits} commits total)")
    print(f"Start (Sunday): {start_sunday}  End: {plan[-1][0] if plan else start_sunday}")
    print()
    print(render_preview(pattern))
    print()
    for date, count in plan:
        print(f"  {date} ({date.strftime('%A'):9s}) -> {count} commit(s)")

    if not args.commit:
        print("\nDry run only — no commits were made. Pass --commit to actually create them.")
        return 0

    repo_dir = Path(args.repo_dir).resolve()
    index = 0
    for date, count in plan:
        for _ in range(count):
            index += 1
            make_backdated_commit(date, index, args.target_file, repo_dir)
    print(f"\n✅ Made {index} backdated commit(s).")

    if args.push:
        subprocess.run(["git", "push", "origin", "HEAD"], cwd=repo_dir, check=True)
        print("✅ Pushed.")
    else:
        print("Not pushed — pass --push once you're happy with `git log`.")

    return 0


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(
        "--pattern", help=f"Built-in pattern ({', '.join(sorted(BUILTIN_PATTERNS))}) or a path to a pattern file."
    )
    parser.add_argument("--preview", help="Print a pattern as ASCII and exit (no dates, no git).")
    parser.add_argument(
        "--start-date",
        type=lambda s: datetime.date.fromisoformat(s),
        default=None,
        help="First Sunday of the drawing window (YYYY-MM-DD). Defaults to today, snapped to the next Sunday.",
    )
    parser.add_argument(
        "--intensity", type=int, choices=sorted(INTENSITY_TO_COMMIT_COUNT), default=3,
        help="1 (lightest) .. 4 (darkest) commits per lit cell.",
    )
    parser.add_argument("--target-file", default=DEFAULT_TARGET_FILE, help="File to append commit content to.")
    parser.add_argument("--repo-dir", default=".", help="Path to the git repository to commit into.")
    parser.add_argument("--commit", action="store_true", help="Actually create the backdated commits.")
    parser.add_argument("--push", action="store_true", help="Push after committing (implies --commit).")
    args = parser.parse_args(argv)
    if args.push:
        args.commit = True
    return args


def main() -> None:
    sys.exit(run(parse_args()))


if __name__ == "__main__":
    main()
