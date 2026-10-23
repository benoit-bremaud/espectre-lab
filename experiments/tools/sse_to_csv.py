"""Flatten an ESPHome web_server SSE stream (stdin) into CSV rows (stdout).

Only `event: state` payloads are kept; `ping` and `log` events are dropped. Every
entity the web server exposes is recorded (score, motion state, threshold, calibrate
switch), never raw CSI. Each row is `timestamp,entity,value`: local receive time
(ISO 8601 with offset), the ESPHome entity id (e.g. `sensor-movement_score`) and the
raw `value` field of the JSON payload.
"""

from __future__ import annotations

import csv
import json
import sys
from collections.abc import Callable, Iterable, Iterator
from datetime import datetime

CSV_HEADER = ("timestamp", "entity", "value")

Row = tuple[str, str, str]


def _local_now() -> datetime:
    return datetime.now().astimezone()


def flatten(
    sse_lines: Iterable[str],
    now: Callable[[], datetime] = _local_now,
    warn: Callable[[str], None] = lambda message: print(message, file=sys.stderr),
) -> Iterator[Row]:
    """Yield one `(timestamp, entity, value)` row per usable `state` event.

    A capture is cut by `curl --max-time`, so the last `data:` line may be truncated;
    such lines, and payloads without `id`/`value` or with a null value, are reported
    through `warn` and skipped instead of aborting the whole run.
    """
    event_name = ""
    for raw_line in sse_lines:
        line = raw_line.rstrip("\r\n")
        if line.startswith("event:"):
            event_name = line[len("event:") :].strip()
        elif line.startswith("data:") and event_name == "state":
            row = _parse_state(line[len("data:") :], now(), warn)
            if row is not None:
                yield row
        elif line == "":
            event_name = ""


def _parse_state(
    payload_text: str, received_at: datetime, warn: Callable[[str], None]
) -> Row | None:
    try:
        payload = json.loads(payload_text)
    except json.JSONDecodeError:
        warn(f"skipped unparsable state payload: {payload_text[:60]!r}")
        return None
    entity = payload.get("id") if isinstance(payload, dict) else None
    value = payload.get("value") if isinstance(payload, dict) else None
    if not isinstance(entity, str) or value is None:
        warn(f"skipped state payload without id/value: {payload_text[:60]!r}")
        return None
    return received_at.isoformat(timespec="milliseconds"), entity, str(value)


def main() -> None:
    """Stream stdin SSE to stdout CSV, header first, flushing each row (live tail)."""
    writer = csv.writer(sys.stdout, lineterminator="\n")
    writer.writerow(CSV_HEADER)
    sys.stdout.flush()
    for row in flatten(sys.stdin):
        writer.writerow(row)
        sys.stdout.flush()


if __name__ == "__main__":
    main()
