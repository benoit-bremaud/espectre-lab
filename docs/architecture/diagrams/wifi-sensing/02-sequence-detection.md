# Wi-Fi sensing — Sequence diagram (detection scenario)

> **Frame:** `sd` — what happens *in time* from power-on to a consumable motion state.

The critical runtime scenario: boot, the ~10 s calibration window, then the steady-state
detection loop. This is the runtime view that the structural data-flow
([06-data-flow.md](06-data-flow.md)) cannot show in time — including the two outputs'
distinct cadences.

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
    loop continuously
        AP-->>ESP: Wi-Fi frames (CSI)
        ESP->>ESP: Update deviation vs baseline
        ESP->>WS: movement_sensor = score (0-10) — every publish_interval
        opt motion state changes (evaluation_interval + N consecutive hits)
            ESP->>WS: motion_sensor = ON / OFF
        end
        opt Home Assistant configured
            ESP-->>HA: sensors via native API
        end
    end
    end

    BR->>WS: GET / (poll sensor states)
    WS-->>BR: motion state + movement score
```

## Notes

- A bad calibration (movement during the first ~10 s) poisons the baseline — recover by
  toggling the `calibrate` switch (runtime recalibration) or rebooting (see
  [05-state-motion.md](05-state-motion.md)).
- The two outputs have **different cadences**: the `movement_sensor` 0-10 score publishes
  every `publish_interval`, while the binary `motion_sensor` flips on `evaluation_interval`
  after N consecutive hits (`motion_on_hits` / `motion_off_hits`, anti-flicker). Neither is
  a headcount or identity, consistent with [how-it-works.md](../../../how-it-works.md).
- The Home Assistant leg is an `opt` block: nothing is sent unless the native API is
  actually wired to an HA instance (future).
