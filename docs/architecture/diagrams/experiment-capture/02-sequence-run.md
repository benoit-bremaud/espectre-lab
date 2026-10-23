# Experiment capture — Sequence diagram (one run)

Actor-initiated goal: *"Measure how the module scores a scenario and compare it with
what really happened"*. One run = one capture + optional marks + one analysis.

```mermaid
sequenceDiagram
    actor Op as Operator
    participant CAP as capture.sh
    participant ESP as espectre-01<br/>web_server /events
    participant MARK as mark.sh
    participant FS as experiments/data/
    participant PY as analyze.py

    Op->>CAP: capture.sh HOST DURATION SLUG
    CAP->>ESP: GET /events (curl -N)
    activate ESP
    loop every ~1 s until DURATION
        ESP-->>CAP: event: state {id, value}
        CAP->>FS: append ts,entity,value
    end
    deactivate ESP
    CAP-->>Op: wrote <date>-<slug>.csv (N rows)

    opt scenario with ground truth
        Op->>MARK: mark.sh SLUG  (runs in parallel)
        loop operator keypress
            Op->>MARK: m / s
            MARK->>FS: append ts,label
        end
    end

    Op->>PY: analyze.py <csv> [--threshold 0.4]
    PY->>FS: read csv (+ marks.csv if present)
    PY-->>Op: markdown: score stats, episodes,<br/>precision/recall per threshold
    Op->>Op: paste into experiments/NNNN-*.md
```

## Notes

- `capture.sh` and `mark.sh` run in two terminals; they share only the run slug and the
  wall clock. Both hosts must be NTP-synced (the Pi and the laptop are).
- `analyze.py` never contacts the device: a journal entry can be recomputed later from the
  committed CSV, with another threshold.
