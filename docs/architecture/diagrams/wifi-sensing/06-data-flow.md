# Wi-Fi sensing — Data-flow diagram

UML data-flow of the ESPectre sensing pipeline, from radio waves to the two consumable
outputs (binary motion + 0-10 movement score). Home Assistant is optional (dashed).

```mermaid
flowchart LR
    AP([Wi-Fi access point<br/>box / router]) -->|RF frames| ANT

    subgraph ESP[ESP32-S3 / C6 / C3]
        ANT[Wi-Fi radio<br/>CSI extraction] -->|raw CSI<br/>per subcarrier| BASE[(Baseline<br/>captured at boot ~10s)]
        ANT -->|live CSI| DEV[Deviation<br/>vs baseline]
        BASE --> DEV
        DEV -->|mapped 0-10| SCORE[movement_sensor<br/>0-10 score]
        DEV --> CMP{> threshold?}
        CMP -->|yes| MOT[motion_sensor = ON]
        CMP -->|no| MOT2[motion_sensor = OFF]
    end

    SCORE --> WS[ESPHome web_server<br/>browser, standalone]
    MOT --> WS
    MOT2 --> WS
    SCORE -.native API.-> HA([Home Assistant<br/>optional, future])
    MOT -.native API.-> HA
    MOT2 -.native API.-> HA
    HA -.-> AUTO([Automations:<br/>lights, alerts, HVAC])
```

## Notes

- Moving bodies between the access point and the ESP32 perturb the RF path → CSI changes.
- The baseline is the "quiet room" fingerprint; a clean ~10 s calibration is required.
- Two outputs are produced: a binary `motion_sensor` and a 0-10 `movement_sensor` score
  (the deviation magnitude mapped to 0-10) — no images, no headcount.
- Standalone path (`web_server`) is enough to experiment; the Home Assistant path is an
  optional later addition for automations.
