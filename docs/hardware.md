# Hardware

## Supported boards

CSI extraction requires an ESP32 variant whose Wi-Fi stack exposes CSI through the
ESP-IDF framework. ESPectre supports:

- **ESP32-S3**
- **ESP32-C6**
- **ESP32-C3**

## Not supported

- **ESP8266** — no CSI capability at all.
- The **classic ESP32** (original) is generally not targeted by ESPectre; stick to the
  S3 / C6 / C3 listed above to avoid surprises.

## What to buy

- A dev board with USB (USB-C preferred) for easy first flashing over serial.
- Any of the three supported variants works; pick by availability/price (~10 €).
- A stable USB power supply — the board must stay powered and connected to Wi-Fi 24/7
  to act as a sensor.

## Placement notes (to validate by experiment)

- Mount it a few meters from the access point with the monitored area roughly between
  the two (motion in the "Wi-Fi path" disturbs CSI the most).
- Avoid placing it right next to large metal objects or appliances that move.
- 2.4 GHz is the relevant band; a congested channel (many neighbours) increases noise.

Record real placement results in [../experiments/](../experiments/).
