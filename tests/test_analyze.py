from __future__ import annotations

from datetime import UTC, datetime, timedelta, timezone
from pathlib import Path

import pytest

from analyze import (
    Mark,
    Sample,
    _as_float,
    confusion,
    count_episodes,
    label_samples,
    main,
    read_samples,
    score_stats,
)

TZ = timezone(timedelta(hours=2))
T0 = datetime(2026, 10, 23, 10, 0, 0, tzinfo=TZ)


def at(seconds: int) -> datetime:
    return T0 + timedelta(seconds=seconds)


def test_score_stats_four_samples_computes_all_fields() -> None:
    stats = score_stats([0.1, 0.2, 0.3, 0.4])

    assert stats.count == 4
    assert stats.minimum == 0.1
    assert stats.maximum == 0.4
    assert stats.median == pytest.approx(0.25)
    assert stats.mean == pytest.approx(0.25)
    assert stats.p99 == pytest.approx(0.397)  # inclusive method: 0.1 + 0.99 * 0.3


def test_score_stats_single_sample_is_its_own_p99() -> None:
    stats = score_stats([0.7])

    assert stats.p99 == stats.median == stats.maximum == 0.7


def test_score_stats_rejects_empty() -> None:
    with pytest.raises(ValueError):
        score_stats([])


@pytest.mark.parametrize(
    ("raw", "expected"),
    [("ON", 1.0), (" off ", 0.0), ("True", 1.0), ("0.348981", 0.348981)],
)
def test_as_float_accepts_booleans_and_numbers(raw: str, expected: float) -> None:
    assert _as_float(raw) == expected


def test_as_float_rejects_garbage() -> None:
    with pytest.raises(ValueError):
        _as_float("None")


@pytest.mark.parametrize(
    ("flags", "expected"),
    [
        ([], 0),
        ([False, False], 0),
        ([True, True, False, True], 2),
        ([False, True, False, True, True], 2),
    ],
)
def test_count_episodes_counts_off_to_on_transitions(
    flags: list[bool], expected: int
) -> None:
    assert count_episodes(flags) == expected


def test_label_samples_uses_latest_preceding_mark_default_still() -> None:
    samples = [Sample(at(s), 0.0) for s in (0, 10, 20, 30)]
    marks = [Mark(at(25), "still"), Mark(at(10), "moving"), Mark(at(99), "moving")]

    assert label_samples(samples, marks) == ["still", "moving", "moving", "still"]


def test_label_samples_without_marks_is_all_still() -> None:
    samples = [Sample(at(s), 0.0) for s in (0, 10)]

    assert label_samples(samples, []) == ["still", "still"]


def test_label_samples_compares_across_utc_offsets() -> None:
    utc_mark = Mark(datetime(2026, 10, 23, 8, 0, 10, tzinfo=UTC), "moving")
    samples = [Sample(at(5), 0.0), Sample(at(15), 0.0)]  # at() is +02:00

    assert label_samples(samples, [utc_mark]) == ["still", "moving"]


def test_confusion_precision_recall() -> None:
    labels = ["moving", "moving", "still", "still", "still"]
    predicted = [True, False, True, False, False]

    result = confusion(labels, predicted)

    assert (result.true_positive, result.false_positive) == (1, 1)
    assert (result.false_negative, result.true_negative) == (1, 2)
    assert result.precision == pytest.approx(0.5)
    assert result.recall == pytest.approx(0.5)


def test_confusion_without_positives_reports_none() -> None:
    result = confusion(["still"], [False])

    assert result.precision is None
    assert result.recall is None


@pytest.fixture
def capture_csv(tmp_path: Path) -> Path:
    rows = [
        "timestamp,entity,value",
        f"{at(0).isoformat()},binary_sensor-motion_detected,False",
        f"{at(0).isoformat()},sensor-movement_score,0.2",
        f"{at(1).isoformat()},sensor-movement_score,0.5",
        f"{at(1).isoformat()},binary_sensor-motion_detected,True",
        f"{at(2).isoformat()},sensor-movement_score,0.3",
        f"{at(2).isoformat()},binary_sensor-motion_detected,False",
    ]
    path = tmp_path / "2026-10-23-test.csv"
    path.write_text("\n".join(rows) + "\n")
    return path


def test_read_samples_filters_entity_and_parses_booleans(capture_csv: Path) -> None:
    motion = read_samples(capture_csv, "binary_sensor-motion_detected")

    assert [sample.value for sample in motion] == [0.0, 1.0, 0.0]


def test_main_renders_stats_and_ground_truth(
    capture_csv: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    marks = capture_csv.with_suffix(".marks.csv")
    marks.write_text(f"timestamp,label\n{at(1).isoformat()},moving\n")

    assert main([str(capture_csv), "--threshold", "0.4"]) == 0

    out = capsys.readouterr().out
    assert "Window: 2026-10-23 10:00:00 → 10:00:02 (2 s), threshold 0.4" in out
    assert "| Samples | 3 |" in out
    assert "| Samples ≥ 0.4 | 1 |" in out
    assert "| Episodes ≥ 0.4 (from scores) | 1 |" in out
    assert "| Motion ON episodes (device) | 1 |" in out
    assert "| True positives | 1 |" in out
    assert "| False negatives | 1 |" in out
    assert "| Precision | 1.00 |" in out
    assert "| Recall | 0.50 |" in out


def test_main_without_marks_or_motion_rows_uses_given_threshold(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    path = tmp_path / "2026-10-23-scores-only.csv"
    path.write_text(
        "timestamp,entity,value\n"
        f"{at(0).isoformat()},sensor-movement_score,0.2\n"
        f"{at(1).isoformat()},sensor-movement_score,0.3\n"
    )

    assert main([str(path), "--threshold", "0.25"]) == 0

    out = capsys.readouterr().out
    assert "| Samples ≥ 0.25 | 1 |" in out
    assert "| Motion ON episodes (device) | 0 |" in out
    assert "Ground truth" not in out


def test_main_fails_without_score_rows(tmp_path: Path) -> None:
    empty = tmp_path / "empty.csv"
    empty.write_text("timestamp,entity,value\n")

    assert main([str(empty)]) == 1
