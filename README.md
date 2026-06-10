# espectre-lab

Personal exploration lab around **Wi-Fi CSI motion detection** using
[ESPectre](https://github.com/francescopace/espectre) — an ESPHome external
component that turns a cheap ESP32 into a presence/motion sensor **without a camera**,
by analysing how moving bodies disturb Wi-Fi Channel State Information (CSI).

> Status: **discovery / learning**. This repo does not reimplement ESPectre — it
> consumes the upstream component, documents how it works, and journals experiments.

## Why this repo

Curiosity: understand how Wi-Fi sensing actually works, get it running on a single
ESP32, and find out whether it is usable in practice (accuracy, false positives,
placement). Home Assistant is **not required** to start — ESPHome runs standalone and
exposes motion state through its built-in web server.

## Hardware

CSI extraction only works on **ESP32-S3 / ESP32-C6 / ESP32-C3**. The classic ESP32
and the ESP8266 are **not** supported. See [docs/hardware.md](docs/hardware.md).

## Quick start

1. Copy `esphome/secrets.yaml.example` to `esphome/secrets.yaml` and fill in your Wi-Fi.
2. `esphome run esphome/espectre.yaml` (USB) to flash the board.
3. Keep the room still for ~10 s after boot (calibration).
4. Open the board's web server (printed in `esphome logs`) to watch the motion state.

Full guide: [docs/setup-esphome.md](docs/setup-esphome.md).

## Docs

- [How it works](docs/how-it-works.md) — Wi-Fi CSI sensing explained simply.
- [Hardware](docs/hardware.md) — supported boards, what to buy, why not ESP8266.
- [Setup with ESPHome](docs/setup-esphome.md) — flash, calibrate, standalone vs Home Assistant.
- [Privacy & RGPD](docs/privacy.md) — local-only data and consent considerations.
- [Data-flow diagram](docs/architecture/diagrams/wifi-sensing/01-data-flow.md).
- [Experiments journal](experiments/) — dated notes on placement, false positives, findings.

## Credits & references

- Upstream component: [francescopace/espectre](https://github.com/francescopace/espectre)
- Korben article: <https://korben.info/espectre-detection-mouvement-wifi-esp32.html>
- Home Assistant thread: <https://community.home-assistant.io/t/espectre-wi-fi-motion-detection-for-home-assistant/961251>
- ESPHome: <https://esphome.io>
