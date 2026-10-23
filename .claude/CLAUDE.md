# Project conventions — espectre-lab

## What this is

Personal exploration lab around **ESPectre** (Wi-Fi CSI motion detection, ESPHome
external component by Francesco Pace). NOT a reimplementation: this repo *consumes*
the upstream component and documents experiments. Curiosity-driven, no production goal.

## Stack

- **ESPHome** (YAML) compiled to ESP32 firmware — ESP-IDF framework (required for CSI).
- Markdown for docs and the experiment journal.
- Python ≥ 3.11, **stdlib only**, for the experiment capture/analysis scripts in
  `experiments/tools/` (no pandas until a real need; dev tools in `requirements-dev.txt`).

## Commands

- Validate config : `esphome config esphome/espectre.yaml`
- Compile firmware : `esphome compile esphome/espectre.yaml`
- Flash (USB, first time) : `esphome run esphome/espectre.yaml`
- Live logs : `esphome logs esphome/espectre.yaml`
- Secrets live in `esphome/secrets.yaml` (gitignored; copy from `secrets.yaml.example`).
- Experiment run : `experiments/tools/capture.sh HOST SECONDS SLUG [SSH_HOST]`, then
  `python3 experiments/tools/analyze.py experiments/data/<date>-<slug>.csv`.
- Python checks : `ruff format . && ruff check . && mypy && pytest --cov` (CI `python.yml`).
- The module lives on the homelab LAN (`192.168.1.x`), not the laptop LAN: reach it via
  `ssh benoit@bb-homelab` (4th arg of `capture.sh`).

## Architecture

- `esphome/` : ESPHome YAML config flashed to the ESP32 (+ secrets example).
- `docs/` : how Wi-Fi CSI sensing works, hardware notes, setup guide, privacy/RGPD.
- `docs/architecture/diagrams/` : Mermaid UML (data-flow of the sensing pipeline).
- `experiments/` : dated experiment journal (placement, false positives, findings).

## Project-specific conventions

- Hardware constraint: only **ESP32-S3 / C6 / C3** extract CSI. ESP8266 and classic
  ESP32 are out of scope — never document them as supported.
- Runs **standalone** (ESPHome `web_server`) — Home Assistant is optional/future.
- Wi-Fi credentials NEVER committed: always via `!secret` + gitignored `secrets.yaml`.

## Known gotchas

- CSI needs `CONFIG_ESP_WIFI_CSI_ENABLED: y` AND power management disabled
  (`CONFIG_PM_ENABLE: n`) in `sdkconfig_options`, else no CSI frames.
- ~10 s post-boot calibration: the room must stay still or the baseline is wrong.
- Many false positives by design (pets, robot vacuum, blinds, neighbour 2.4GHz, weather);
  it reports motion / no-motion only — it cannot count people.
