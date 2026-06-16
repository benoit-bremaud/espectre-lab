# Wi-Fi sensing — Data-flow diagram

UML data-flow of the ESPectre sensing pipeline, from radio waves to a consumable motion
state. Home Assistant is optional (dashed).

```mermaid
flowchart LR
    AP([Wi-Fi access point<br/>box / router]) -->|RF frames| ANT

    subgraph ESP[ESP32-S3 / C6 / C3]
        ANT[Wi-Fi radio<br/>CSI extraction] -->|raw CSI<br/>per subcarrier| BASE[(Baseline<br/>captured at boot ~10s)]
        ANT -->|live CSI| CMP{Deviation<br/>> threshold?}
        BASE --> CMP
        CMP -->|yes| MOT[Motion state = ON]
        CMP -->|no| MOT2[Motion state = OFF]
    end

    MOT --> WS[ESPHome web_server<br/>browser, standalone]
    MOT2 --> WS
    MOT -.native API.-> HA([Home Assistant<br/>optional, future])
    MOT2 -.native API.-> HA
    HA -.-> AUTO([Automations:<br/>lights, alerts, HVAC])
```

## Notes

- Moving bodies between the access point and the ESP32 perturb the RF path → CSI changes.
- The baseline is the "quiet room" fingerprint; a clean ~10 s calibration is required.
- The binary motion state is the only data produced — no images, no headcount.
- Standalone path (`web_server`) is enough to experiment; the Home Assistant path is an
  optional later addition for automations.
