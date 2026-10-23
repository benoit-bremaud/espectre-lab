"""Summarise one capture CSV (and its optional marks file) as markdown tables.

Usage: analyze.py experiments/data/<date>-<slug>.csv [--threshold 0.4]

Ground truth, when present, is read from `<date>-<slug>.marks.csv` next to the CSV
(written by mark.sh). "Predicted moving" means score >= threshold. Pure file-in /
text-out: no network, so a journal entry can be recomputed later from the committed CSV
with another threshold.
"""

from __future__ import annotations

import argparse
import csv
import statistics
import sys
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

SCORE_ENTITY = "sensor-movement_score"
MOTION_ENTITY = "binary_sensor-motion_detected"
DEFAULT_THRESHOLD = 0.4
LABEL_MOVING = "moving"
LABEL_STILL = "still"


@dataclass(frozen=True)
class Sample:
    at: datetime
    value: float


@dataclass(frozen=True)
class Mark:
    at: datetime
    label: str


@dataclass(frozen=True)
class ScoreStats:
    count: int
    minimum: float
    median: float
    p99: float
    maximum: float
    mean: float


@dataclass(frozen=True)
class Confusion:
    true_positive: int
    false_positive: int
    false_negative: int
    true_negative: int

    @property
    def precision(self) -> float | None:
        """None (undefined, not 0) when nothing was predicted positive."""
        predicted_positive = self.true_positive + self.false_positive
        return self.true_positive / predicted_positive if predicted_positive else None

    @property
    def recall(self) -> float | None:
        """None (undefined, not 0) when the ground truth has no moving sample."""
        actual_positive = self.true_positive + self.false_negative
        return self.true_positive / actual_positive if actual_positive else None


def read_samples(csv_path: Path, entity: str) -> list[Sample]:
    """Read the rows of `entity` from a capture CSV, in file order."""
    with csv_path.open(newline="") as handle:
        return [
            Sample(datetime.fromisoformat(row["timestamp"]), _as_float(row["value"]))
            for row in csv.DictReader(handle)
            if row["entity"] == entity
        ]


def read_marks(marks_path: Path) -> list[Mark]:
    """Read the ground-truth marks written by mark.sh (`timestamp,label` CSV)."""
    with marks_path.open(newline="") as handle:
        return [
            Mark(datetime.fromisoformat(row["timestamp"]), row["label"])
            for row in csv.DictReader(handle)
        ]


def label_samples(samples: Sequence[Sample], marks: Sequence[Mark]) -> list[str]:
    """Label each sample with the latest mark at or before it (default: still)."""
    ordered_marks = sorted(marks, key=lambda mark: mark.at)
    labels: list[str] = []
    for sample in samples:
        label = LABEL_STILL
        for mark in ordered_marks:
            if mark.at <= sample.at:
                label = mark.label
            else:
                break
        labels.append(label)
    return labels


def score_stats(values: Sequence[float]) -> ScoreStats:
    """Min / median / mean / p99 / max of `values`.

    p99 uses the inclusive quantile method so it stays inside the observed range on
    short runs (a few hundred samples); a single sample is its own p99.

    Raises:
        ValueError: if `values` is empty.
    """
    if not values:
        raise ValueError("no score samples")
    p99 = (
        statistics.quantiles(values, n=100, method="inclusive")[98]
        if len(values) > 1
        else values[0]
    )
    return ScoreStats(
        count=len(values),
        minimum=min(values),
        median=statistics.median(values),
        p99=p99,
        maximum=max(values),
        mean=statistics.fmean(values),
    )


def count_episodes(active_flags: Sequence[bool]) -> int:
    """Number of OFF→ON transitions (an initial ON counts as one)."""
    episodes = 0
    previous = False
    for active in active_flags:
        if active and not previous:
            episodes += 1
        previous = active
    return episodes


def confusion(labels: Sequence[str], predicted_moving: Sequence[bool]) -> Confusion:
    """Confusion matrix of `predicted_moving` against ground truth (positive = moving).

    Raises:
        ValueError: if `labels` and `predicted_moving` differ in length.
    """
    pairs = [
        (predicted, label == LABEL_MOVING)
        for label, predicted in zip(labels, predicted_moving, strict=True)
    ]
    return Confusion(
        true_positive=sum(predicted and actual for predicted, actual in pairs),
        false_positive=sum(predicted and not actual for predicted, actual in pairs),
        false_negative=sum(not predicted and actual for predicted, actual in pairs),
        true_negative=sum(not predicted and not actual for predicted, actual in pairs),
    )


def render_markdown(
    scores: Sequence[Sample],
    motion: Sequence[Sample],
    marks: Sequence[Mark],
    threshold: float,
) -> str:
    """Markdown report for one run: score stats, then precision/recall if `marks` given.

    Predicted moving = score >= `threshold`. The device's own motion state is ON when
    the sample value is >= 1 (ESPHome booleans are coerced to 1.0 / 0.0 by `_as_float`).
    `scores` must be non-empty (`main` guards this).
    """
    values = [sample.value for sample in scores]
    stats = score_stats(values)
    predicted_moving = [value >= threshold for value in values]
    score_episodes = count_episodes(predicted_moving)
    device_on = [sample.value >= 1 for sample in motion]
    span = scores[-1].at - scores[0].at

    lines = [
        f"Window: {scores[0].at:%Y-%m-%d %H:%M:%S} → {scores[-1].at:%H:%M:%S}"
        f" ({int(span.total_seconds())} s), threshold {threshold}",
        "",
        "| Metric | Value |",
        "|---|---|",
        f"| Samples | {stats.count} |",
        f"| Min | {stats.minimum:.3f} |",
        f"| Median | {stats.median:.3f} |",
        f"| Mean | {stats.mean:.3f} |",
        f"| p99 | {stats.p99:.3f} |",
        f"| Max | {stats.maximum:.3f} |",
        f"| Samples ≥ {threshold} | {sum(predicted_moving)} |",
        f"| Episodes ≥ {threshold} (from scores) | {score_episodes} |",
        f"| Motion ON episodes (device) | {count_episodes(device_on)} |",
    ]
    if marks:
        labels = label_samples(scores, marks)
        result = confusion(labels, predicted_moving)
        lines += [
            "",
            f"Ground truth: {len(marks)} marks,"
            f" {labels.count(LABEL_MOVING)} samples labelled moving.",
            "",
            "| Metric | Value |",
            "|---|---|",
            f"| True positives | {result.true_positive} |",
            f"| False positives | {result.false_positive} |",
            f"| False negatives | {result.false_negative} |",
            f"| True negatives | {result.true_negative} |",
            f"| Precision | {_ratio(result.precision)} |",
            f"| Recall | {_ratio(result.recall)} |",
        ]
    return "\n".join(lines) + "\n"


def main(argv: Sequence[str] | None = None) -> int:
    """Print the report; return 0, or 1 when the CSV holds no movement-score rows."""
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("csv", type=Path, help="capture CSV written by capture.sh")
    parser.add_argument(
        "--threshold", type=float, default=DEFAULT_THRESHOLD, help="score threshold"
    )
    args = parser.parse_args(argv)

    scores = read_samples(args.csv, SCORE_ENTITY)
    if not scores:
        print(f"no {SCORE_ENTITY} rows in {args.csv}", file=sys.stderr)
        return 1
    motion = read_samples(args.csv, MOTION_ENTITY)
    marks_path = args.csv.with_suffix(".marks.csv")
    marks = read_marks(marks_path) if marks_path.exists() else []
    sys.stdout.write(render_markdown(scores, motion, marks, args.threshold))
    return 0


def _as_float(raw: str) -> float:
    lowered = raw.strip().lower()
    if lowered in {"true", "on"}:
        return 1.0
    if lowered in {"false", "off"}:
        return 0.0
    return float(lowered)


def _ratio(value: float | None) -> str:
    return "n/a" if value is None else f"{value:.2f}"


if __name__ == "__main__":
    sys.exit(main())
