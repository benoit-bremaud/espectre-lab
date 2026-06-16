# Wi-Fi sensing — Sequence diagram (detection scenario)

> **Frame:** `sd` — what happens *in time* from power-on to a consumable motion state.

The critical runtime scenario: boot, the ~10 s calibration window, then the steady-state
detection loop. This is the **per-frame loop** that the structural data-flow view
([06-data-flow.md](06-data-flow.md)) cannot show in time.

```mermaid
sequenceDiagram
    participant AP as Wi-Fi AP (box/router)
    participant ESP as ESP32 (radio + espectre)
    participant WS as web_server
    participant BR as Browser
    participant HA as Home Assistant (optional)

    Note over ESP: Power-on
    ESP->>AP: Associate / connect (2.4 GHz)
    AP-->>ESP: Connected

    rect rgb(245,245,245)
    Note over ESP: Calibration ~10 s — room must stay still
    loop until baseline stable (~10 s)
        AP-->>ESP: Wi-Fi frame
        ESP->>ESP: Extract CSI, aggregate baseline
    end
    end

    rect rgb(235,245,255)
    Note over ESP: Steady-state monitoring
    loop per received frame
        AP-->>ESP: Wi-Fi frame
        ESP->>ESP: Extract CSI, compare to baseline
        alt deviation > threshold
            ESP->>WS: motion = ON
        else deviation ≤ threshold
            ESP->>WS: motion = OFF
        end
        opt Home Assistant configured
            ESP-->>HA: state via native API
        end
    end
    end

    BR->>WS: GET / (poll motion state)
    WS-->>BR: current motion state
```

## Notes

- A bad calibration (movement during the first ~10 s) poisons the baseline for the whole
  session — the only recovery is a reboot (see [05-state-motion.md](05-state-motion.md)).
- The output written to `web_server` is strictly **binary** (ON/OFF) — no headcount,
  no identity, consistent with [how-it-works.md](../../../how-it-works.md).
- The Home Assistant leg is an `opt` block: nothing is sent unless the native API is
  actually wired to an HA instance (future).
