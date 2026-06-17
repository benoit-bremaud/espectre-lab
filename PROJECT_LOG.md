# Project Log — espectre-lab

Chronological operational logbook. Complements `git log`: records decisions, context,
and findings that the commit history alone does not capture. Newest entries on top.

---

## 2026-06-16 — Target the ESP32-C3 SuperMini for the first flash

**Context.** Three ESP32-C3 SuperMini boards are now in hand; bringing up the first one.
The config still targeted `esp32-s3-devkitc-1` and had a bare `logger:`.

**Decisions.**

- Set `board: esp32-c3-devkitm-1` (standard generic C3 id, valid for the SuperMini).
- Route the logger to the C3's native USB: `logger: hardware_uart: USB_SERIAL_JTAG`.
  On the SuperMini, UART0 is not wired to the USB port, so without this `esphome logs`
  over USB stays silent.
- Rename the device `espectre-lab` → `espectre-01` (unique mDNS/OTA hostname; sets up an
  -01/-02/-03 scheme for the three boards).

**Next.** Flash board 1 over USB, ~10 s calibration, verify the web UI sensors; then
commit/PR this config (CI re-validates `esphome config` on C3) and replicate to 02/03.

---

## 2026-06-16 — Document the movement_sensor 0-10 score (closes #2)

**Context.** Review of #1 (and verification against upstream SETUP.md) showed `espectre:`
auto-creates more than the binary `motion_sensor`: also a `movement_sensor` 0-10 score,
a threshold `number`, and a `calibrate` switch. The conception framed the output as
"binary only", which was inaccurate.

**Decisions.**

- **Keep the score exposed** (not `internal: true`): the continuous 0-10 value is the
  signal we want to watch when tuning the threshold during experiments.
- Make the whole conception consistent with the real sensor set.

**Done.**

- Diagrams: `02-sequence-detection` (publishes the score per frame), `06-data-flow` (added
  the `movement_sensor` output path), `03-component` (edge labels).
- Docs: `how-it-works.md`, `privacy.md` (continuous score is more revealing; `internal:
  true` option for minimisation), `setup-esphome.md`, and a clarifying comment in
  `espectre.yaml`.

**Next.**

- First flash once a board is available; confirm the exposed sensors match the docs.

---

## 2026-06-16 — Pin upstream component + ESPHome config CI

**Context.** No board in hand yet; goal is to make everything flash-ready so the first
flash is a one-command step when hardware arrives. Review of #1 also flagged an unpinned
`external_components` pull (non-reproducible builds).

**Decisions.**

- Pin `external_components` to upstream release **`2.8.0`** (latest stable) via `ref:`.
  Bumps are deliberate from now on.
- Add a CI job that validates `esphome config` on every push/PR, using a placeholder
  `secrets.yaml` copied from the example (no real credentials needed to validate).

**Done.**

- `esphome/espectre.yaml`: `ref: "2.8.0"` on the ESPectre source.
- New workflow `.github/workflows/esphome.yml` (Python + `pip install esphome` +
  `esphome config`).

**Next.**

- Resolve #2 (document the `movement_sensor` 0-10 score) on its own branch.
- First flash + calibration once a board is available.

---

## 2026-06-15 — UML conception set for `wifi-sensing`

**Context.** Modelling the sensing feature ahead of the planned first flash. Per the
UML-first rule, the feature must be modelled before the build. Only the data-flow diagram
existed, and it was mis-numbered vs the convention (use-case first → data-flow last).

> **Correction (2026-06-16):** an earlier draft of this entry stated a board was already
> in hand. That was inaccurate — no compatible ESP32 is available yet; the first flash is
> deferred until hardware arrives (see the 2026-06-16 entry).

**Decisions.**

- Complete the `wifi-sensing` conception with four diagrams (use-case, sequence,
  component, state) — Mermaid, matching the existing style (no PlantUML for this lab).
- **Skip `class`** (n° 04 left intentionally empty): the repo consumes an upstream
  `external_component` (YAML), there is no first-party class model to own.
- Renumber data-flow to last (`06-data-flow.md`) for convention conformance.

**Done.**

- New diagrams: `01-use-case.md`, `02-sequence-detection.md`, `03-component.md`,
  `05-state-motion.md` under `docs/architecture/diagrams/wifi-sensing/`.
- Renamed `01-data-flow.md` → `06-data-flow.md`; updated the README docs section to
  list the full diagram set.

**Next.**

- First USB flash + ~10 s calibration, then fill experiment `0001` (placement, false
  positives) against the modelled behaviour.

---

## 2026-06-10 — Repository scaffold

**Context.** Discovered ESPectre via Korben's article on Wi-Fi CSI motion detection.
Created this repo as a personal exploration lab (curiosity-driven) to understand the
technology and test it on a single ESP32. No production or commercial goal.

**Decisions.**

- Scope = exploration/docs lab consuming upstream `francescopace/espectre`; **not** a
  reimplementation.
- Run **standalone** via ESPHome `web_server`; Home Assistant integration deferred
  (not installed yet) — documented as a future step.
- Stack profile = `base` (no Node/Python yet); core artifacts are ESPHome YAML + docs.
- Repository **private** by default (private-first policy).

**Done.**

- `git init` on `main`, local git email set to `bbd.concept@gmail.com`.
- `.claude/` scaffolded (base profile) and `CLAUDE.md` filled with real project specifics.
- Root files: `README.md`, `.gitignore` (ESPHome secrets/builds + Claude overrides).
- Docs: how-it-works, hardware, setup-esphome, privacy.
- UML data-flow diagram under `docs/architecture/diagrams/wifi-sensing/`.
- ESPHome config `esphome/espectre.yaml` + `secrets.yaml.example`.
- Experiment journal template under `experiments/`.
- Gitleaks secret-scan CI workflow.

**Next.**

- Acquire/confirm an ESP32-S3/C6/C3 and run a first real flash + calibration experiment.
- Decide on Home Assistant integration once HA is set up.
