"""Flatten an ESPHome web_server SSE stream (stdin) into CSV rows (stdout).

Only `event: state` payloads are kept; `ping` and `log` events are dropped.
Each row is `timestamp,entity,value` where timestamp is the local receive time (ISO 8601
with offset), entity the ESPHome entity id (e.g. `sensor-movement_score`) and value the
raw `value` field of the JSON payload.
"""

from __future__ import annotations

import json
import sys
from collections.abc import Callable, Iterable, Iterator
from datetime import datetime

CSV_HEADER = "timestamp,entity,value"


def _local_now() -> datetime:
    return datetime.now().astimezone()


def flatten(
    sse_lines: Iterable[str], now: Callable[[], datetime] = _local_now
) -> Iterator[str]:
    """Yield one CSV row per `state` event found in the SSE `sse_lines`."""
    event_name = ""
    for raw_line in sse_lines:
        line = raw_line.rstrip("\n")
        if line.startswith("event:"):
            event_name = line[len("event:") :].strip()
        elif line.startswith("data:") and event_name == "state":
            payload = json.loads(line[len("data:") :])
            stamp = now().isoformat(timespec="milliseconds")
            yield f"{stamp},{payload['id']},{payload['value']}"
        elif line == "":
            event_name = ""


def main() -> None:
    for row in flatten(sys.stdin):
        print(row, flush=True)


if __name__ == "__main__":
    main()
