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
- Pre-push secret gate (once per clone) : `scripts/install-hooks.sh`; canary :
  `scripts/test-secret-gate.sh` (needs `gitleaks` on PATH, the hook refuses the push without it).
- SonarQube (local instance, pre-push/pre-merge gate) : `pytest --cov --cov-report=xml`
  then `SONAR_TOKEN="$(cat ~/.config/sonarqube/analysis-token)" sonar-scanner`
  (config in `sonar-project.properties`, project `espectre-lab`, waits for the gate).
- The module lives on the homelab LAN (`<LAN_CIDR>`), not the laptop LAN: reach it via
  `ssh <SSH_HOST>` (4th arg of `capture.sh`).

## Architecture

- `esphome/` : ESPHome YAML config flashed to the ESP32 (+ secrets example).
- `docs/` : how Wi-Fi CSI sensing works, hardware notes, setup guide, privacy/RGPD.
- `docs/architecture/diagrams/` : Mermaid UML (data-flow of the sensing pipeline).
- `experiments/` : dated experiment journal (placement, false positives, findings).
- `experiments/tools/` : stdlib-Python capture/analysis (`capture.sh`, `mark.sh`,
  `analyze.py`, `sse_to_csv.py`); `experiments/data/` : committed CSVs; `tests/` : pytest.
- `docs/test-plan.md` : catalogue of planned experiments; backlog on the GitHub Project
  espectre-lab (#74), tracker issue #33.

## Project-specific conventions

- Hardware constraint: only **ESP32-S3 / C6 / C3** extract CSI. ESP8266 and classic
  ESP32 are out of scope — never document them as supported.
- Runs **standalone** (ESPHome `web_server`) — Home Assistant (on the homelab) also records the entities; still optional for the module itself.
- Wi-Fi credentials NEVER committed: always via `!secret` + gitignored `secrets.yaml`.

## Known gotchas

- CSI needs `CONFIG_ESP_WIFI_CSI_ENABLED: y` AND power management disabled
  (`CONFIG_PM_ENABLE: n`) in `sdkconfig_options`, else no CSI frames.
- ~10 s post-boot calibration: the room must stay still or the baseline is wrong.
- Measured idle score: ~0.10 inert room, ~0.23 with the ceiling fan on, bursts to ~1.9
  with a draught (windows open). Recommended threshold 0.5 (`experiments/0003`).
- Many false positives by design (pets, robot vacuum, blinds, neighbour 2.4GHz, weather);
  it reports motion / no-motion only — it cannot count people.
