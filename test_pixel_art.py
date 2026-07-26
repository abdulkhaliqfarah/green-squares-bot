"""Tests for pixel_art.py -- pure date/pattern logic (no real git operations)."""

from __future__ import annotations

import datetime

import pytest

import pixel_art


def test_builtin_patterns_are_seven_rows_and_rectangular() -> None:
    for name, pattern in pixel_art.BUILTIN_PATTERNS.items():
        assert len(pattern) == pixel_art.GRAPH_ROWS, name
        width = len(pattern[0])
        assert all(len(row) == width for row in pattern), name


@pytest.mark.parametrize("name", ["heart", "diamond"])
def test_symmetric_builtin_patterns_are_horizontal_palindromes(name: str) -> None:
    for row in pixel_art.BUILTIN_PATTERNS[name]:
        assert row == row[::-1], f"{name} row {row!r} is not symmetric"


def test_next_sunday_on_or_after_keeps_a_sunday() -> None:
    sunday = datetime.date(2026, 8, 2)
    assert sunday.isoweekday() == 7
    assert pixel_art.next_sunday_on_or_after(sunday) == sunday


def test_next_sunday_on_or_after_advances_to_next_sunday() -> None:
    wednesday = datetime.date(2026, 8, 5)
    assert wednesday.isoweekday() == 3
    result = pixel_art.next_sunday_on_or_after(wednesday)
    assert result.isoweekday() == 7
    assert result > wednesday
    assert (result - wednesday).days < 7


def test_validate_pattern_rejects_wrong_row_count() -> None:
    with pytest.raises(pixel_art.PatternError):
        pixel_art.validate_pattern(["###", "###"])


def test_validate_pattern_rejects_ragged_rows() -> None:
    rows = ["###", "##", "###", "###", "###", "###", "###"]
    with pytest.raises(pixel_art.PatternError):
        pixel_art.validate_pattern(rows)


def test_pattern_to_dates_maps_single_pixel_to_correct_weekday_and_week() -> None:
    start_sunday = datetime.date(2026, 8, 2)
    pattern = [
        "#......",
        ".......",
        ".......",
        ".......",
        ".......",
        ".......",
        "......#",
    ]
    dates = pixel_art.pattern_to_dates(pattern, start_sunday)
    # Row 0 (Sunday) col 0 -> start_sunday itself.
    assert dates[0] == start_sunday
    assert dates[0].isoweekday() == 7
    # Row 6 (Saturday) col 6 -> 6 weeks later, on a Saturday.
    assert dates[1] == start_sunday + datetime.timedelta(weeks=6, days=6)
    assert dates[1].isoweekday() == 6


def test_pattern_to_dates_rejects_non_sunday_start() -> None:
    not_sunday = datetime.date(2026, 8, 3)
    with pytest.raises(pixel_art.PatternError):
        pixel_art.pattern_to_dates(pixel_art.BUILTIN_PATTERNS["diamond"], not_sunday)


def test_build_plan_uses_requested_intensity_for_every_cell() -> None:
    start_sunday = datetime.date(2026, 8, 2)
    plan = pixel_art.build_plan(pixel_art.BUILTIN_PATTERNS["diamond"], start_sunday, commits_per_cell=5)
    assert plan  # non-empty
    assert all(count == 5 for _, count in plan)


def test_render_preview_uses_block_for_on_pixels() -> None:
    rendered = pixel_art.render_preview(["#.", ".#"])
    assert rendered == "█·\n·█"


def test_load_pattern_resolves_builtin_by_name() -> None:
    assert pixel_art.load_pattern("heart") == pixel_art.BUILTIN_PATTERNS["heart"]


def test_load_pattern_raises_for_unknown_name_or_missing_file() -> None:
    with pytest.raises(pixel_art.PatternError):
        pixel_art.load_pattern("not-a-real-pattern-or-file")


def test_load_pattern_reads_a_custom_pattern_file(tmp_path) -> None:
    custom = tmp_path / "custom.txt"
    custom.write_text("\n".join(["#######"] * 7) + "\n")
    assert pixel_art.load_pattern(str(custom)) == ["#######"] * 7


def test_parse_args_push_implies_commit() -> None:
    args = pixel_art.parse_args(["--pattern", "heart", "--push"])
    assert args.commit is True
    assert args.push is True


def test_parse_args_defaults_to_no_commit() -> None:
    args = pixel_art.parse_args(["--pattern", "heart"])
    assert args.commit is False
    assert args.push is False
