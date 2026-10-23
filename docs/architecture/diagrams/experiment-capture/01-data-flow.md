# Experiment capture — Data-flow diagram

UML data-flow of the experiment tooling (issue #6): how a run's movement scores and the
manual ground truth travel from the module to the markdown table pasted into the
experiment journal. The firmware is untouched: the only source is the ESPHome
`web_server` Server-Sent-Events stream.

Decision record: MCDA 2026-10-23 — SSE + Python (410/500) chosen over MQTT + Python (350,
design fallback) and Home Assistant recorder (335). See `PROJECT_LOG.md`.

```mermaid
flowchart LR
    subgraph ESP[ESP32-C3 — espectre-01]
        WS[ESPHome web_server<br/>GET /events<br/>text/event-stream]
    end

    subgraph RUN[Operator shell — laptop or Pi]
        CAP[capture.sh<br/>host, duration, slug]
        MARK[mark.sh<br/>moving / still]
    end

    subgraph DATA[experiments/data/]
        CSV[(&lt;date&gt;-&lt;slug&gt;.csv<br/>ts, entity, value)]
        MARKS[(&lt;date&gt;-&lt;slug&gt;.marks.csv<br/>ts, label)]
    end

    subgraph ANA[Analysis — Python]
        PY[analyze.py<br/>pandas]
    end

    WS -->|SSE 'state' events<br/>~1 Hz JSON| CAP
    CAP -->|one row per<br/>state event| CSV
    MARK -->|one row per<br/>operator keypress| MARKS
    CSV --> PY
    MARKS --> PY
    PY -->|markdown tables:<br/>score stats + precision/recall| JOURNAL[experiments/NNNN-*.md]
```

## Notes

- `capture.sh` keeps only `event: state` payloads and flattens them to
  `timestamp,entity_id,value` (the SSE `ping` and `log` events are dropped).
- Ground truth is manual: during a run the operator presses a key in `mark.sh` each time
  the real situation changes (`moving` ↔ `still`). A mark holds until the next one;
  a run with no mark is treated as `still` end to end (baseline run).
- `analyze.py` is pure: files in, markdown out, no network. Threshold is an argument
  (defaults to the device's 0.4) so several thresholds can be evaluated on the same CSV.
- Data files contain only the movement score and the motion state, never raw CSI
  (see `docs/privacy.md`).
- 24/7 continuous recording is out of scope: SSE is single-client and not reconnected.
  The MQTT fallback (option B) would replace `capture.sh` only; `analyze.py` is reused.
