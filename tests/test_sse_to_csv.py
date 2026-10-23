from __future__ import annotations

from datetime import datetime, timedelta, timezone

from sse_to_csv import flatten

TZ = timezone(timedelta(hours=2))
FIXED_NOW = datetime(2026, 10, 23, 10, 46, 45, tzinfo=TZ)

SSE_STREAM = """event: ping

event: state
data: {"id":"sensor-movement_score","value":0.348981,"state":"0.35"}

event: log
data: [I] something

event: state
data: {"id":"binary_sensor-motion_detected","value":false,"state":"OFF"}

"""


def test_flatten_keeps_only_state_events_as_csv_rows() -> None:
    rows = list(flatten(SSE_STREAM.splitlines(keepends=True), now=lambda: FIXED_NOW))

    assert rows == [
        "2026-10-23T10:46:45.000+02:00,sensor-movement_score,0.348981",
        "2026-10-23T10:46:45.000+02:00,binary_sensor-motion_detected,False",
    ]


def test_flatten_ignores_data_without_state_event() -> None:
    orphan = ['data: {"id":"x","value":1}\n']

    assert list(flatten(orphan, now=lambda: FIXED_NOW)) == []
