from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from sse_to_csv import flatten

TZ = timezone(timedelta(hours=2))
FIXED_NOW = datetime(2026, 10, 23, 10, 46, 45, tzinfo=TZ)
STAMP = "2026-10-23T10:46:45.000+02:00"

SSE_STREAM = """event: ping

event: state
data: {"id":"sensor-movement_score","value":0.348981,"state":"0.35"}

event: log
data: [I] something

event: state
data: {"id":"binary_sensor-motion_detected","value":false,"state":"OFF"}

"""


def collect(text: str) -> tuple[list[tuple[str, str, str]], list[str]]:
    warnings: list[str] = []
    rows = list(
        flatten(
            text.splitlines(keepends=True), now=lambda: FIXED_NOW, warn=warnings.append
        )
    )
    return rows, warnings


def test_flatten_keeps_only_state_events_as_rows() -> None:
    rows, warnings = collect(SSE_STREAM)

    assert rows == [
        (STAMP, "sensor-movement_score", "0.348981"),
        (STAMP, "binary_sensor-motion_detected", "False"),
    ]
    assert warnings == []


def test_flatten_ignores_data_without_state_event() -> None:
    rows, _ = collect('data: {"id":"x","value":1}\n')

    assert rows == []


def test_flatten_resets_event_on_crlf_blank_line() -> None:
    stream = 'event: state\r\n\r\ndata: {"id":"x","value":1}\r\n'

    rows, _ = collect(stream)

    assert rows == []


@pytest.mark.parametrize(
    "payload",
    [
        '{"id":"sensor-movement_score","va',  # truncated by curl --max-time
        '{"id":"sensor-movement_score","state":"ON"}',  # no value
        '{"id":"sensor-movement_score","value":null}',  # null value
        '{"value":1}',  # no id
        "[1, 2]",  # not an object
    ],
)
def test_flatten_skips_unusable_payload_with_warning(payload: str) -> None:
    rows, warnings = collect(f"event: state\ndata: {payload}\n\n")

    assert rows == []
    assert len(warnings) == 1
