# Wi-Fi sensing — Use-case diagram

> **Frame:** `uc` — who interacts with the ESPectre sensing lab, and to do what.

UML use cases are **actor-initiated goals**, grouped by **domain** (Setup / Operate /
Experiment) — not by which component implements them. Home Assistant is a future,
optional secondary actor (dashed).

```mermaid
flowchart LR
    EXP(["Experimenter<br/>(la curieuse)"])
    HA(["Home Assistant<br/>(future)"])

    subgraph SYS["ESPectre Wi-Fi sensing"]
        direction TB
        subgraph SETUP["Setup"]
            UC1(["Flash & configure the sensor"])
            UC2(["Calibrate the baseline"])
        end
        subgraph OPERATE["Operate"]
            UC3(["Consult the motion state (web)"])
            UC4(["Adjust the detection threshold"])
        end
        subgraph EXPERIMENT["Experiment"]
            UC5(["Run a placement experiment"])
        end
    end

    EXP --- UC1
    EXP --- UC2
    EXP --- UC3
    EXP --- UC4
    EXP --- UC5
    HA -. future .-> UC3
```

## Notes

- Every use case is a **verb + observable outcome** the Experimenter initiates —
  *"Calibrate the baseline"*, not *"Baseline is captured"* (that is a system event).
- Grouping is by **domain**, never by backend: there is deliberately no Mobile / API /
  Backend split here — that structural view lives in
  [03-component.md](03-component.md), not in a use-case diagram.
- *"Consult the motion state"* is a **pull** (the Experimenter opens the web server),
  not *"Be notified of motion"* (a passive trigger, which is not a use case).
- Home Assistant is dashed: a later integration would let it consult the state for
  automations, but it is out of the current standalone scope.
