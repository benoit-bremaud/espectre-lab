# Project Log — espectre-lab

Chronological operational logbook. Complements `git log`: records decisions, context,
and findings that the commit history alone does not capture. Newest entries on top.

---

## 2026-10-26 — Experiment 0005: remote lights (test C3, partial, #34)

- Lights driven by a **temporary time-triggered Home Assistant automation** created from
  the owner's signed-in browser (no token, no webhook), deleted after the run.
- String lights on their Zigbee plug: no effect on the score (median 0.092 on vs 0.094
  off, 0 device episodes over 24 min). Inert-room floor reproduced (0.094 vs 0.100).
- The two Zigbee neons accepted `light.turn_on` but never changed state (unpowered or out
  of reach): neon blocks to rerun. Home Assistant is back up, so #14 is unblocked.

## 2026-10-26 — Experiment 0004: inert-room baseline + test plan (#16, #32)

**Context.** Owner away, windows closed, fan off: the first run where the two usual
perturbations of `0003` are both absent. Used the occasion to write down every test worth
running next.

**Findings.**

- 30 min, 1862 samples: median **0.100**, p99 0.163, max 0.211, **0 device episodes**
  (0003 run 2, fan on: median 0.229, max 0.435, 6 episodes). Stable per 5 min block, no
  burst, no SSE reset.
- The module idles about 2.3× lower without fan and draught: they, not the detector,
  drive the false positives. The windows-closed and fan-off effects are not separated
  yet (A2 #17 and A3 #18).

**Decisions.**

- Test plan catalogue in `docs/test-plan.md` (A empty house, B occupied, C perturbations,
  D long run, E validation), one issue per test (#16–#31), tracker #33, existing #12 and
  #14 reused for E1 and D1. New GitHub Project **espectre-lab** (#74, Todo / In Progress /
  Done) holds the backlog; labels `experiment` and `test-plan` added.
- Next brick: **A2** (#17), fan on / windows closed, 15 min, needs the fan switched on
  while the owner is away.

## 2026-10-24 — Experiment 0003: baseline + walk-through to pick a threshold (#10)

**Context.** `0002` left the default threshold 0.4 inside the idle noise. `0003` repeats
the baseline for 10 min with a documented placement (shelf above the sofa-bed, 1.8 m,
~10 m from the box, round table in between) in the owner's everyday conditions (ceiling
fan on, laundry drying), then a marked walk-through for precision/recall.

**Findings (baselines, house empty).**

- Run 2 (599 s): mean 0.232, p99 0.352, max 0.435 → 2 samples ≥ 0.4, 0 ≥ 0.5.
- Run 1 cut at 354 s (SSE connection reset) with a draught burst to 1.93 in its first
  minute, windows open: no threshold filters that, only the environment does.
- Device `Motion Detected` fires below the 0.4 entity value (0.379–0.397, and once with
  no published sample over 0.344): internal threshold ≈ 0.369 (`thr:0.3690`, #8) and the
  ~1 Hz SSE stream under-samples the score. Trust `Motion ON episodes (device)`, not
  `Samples ≥ threshold`, for the deployed firmware.
- Walk-through (2026-10-24, windows closed, owner + daughter in the room, marks on the
  clock): seated-still phases score 0.70–1.47, walking 0.94–1.12. The placement senses
  **presence, not movement**; "moving vs still" precision is 0.31 at any threshold.
- Empty vs occupied: at 0.5, 0 % of empty-house samples vs 79 % of occupied samples,
  every occupied minute detected.

**Decisions.**

- Everyday perturbations (fan, laundry) are kept during captures: the threshold must
  hold in real conditions, not in a sterile room.
- **Recommended threshold 0.5** (MCDA 435 vs 0.6 405 vs 0.4 275; no empty-house false
  alarm 40, presence detection 35, margin over idle max 25). 0.6 is the fallback if
  longer remote baselines show false alarms. Applied as `segmentation_threshold: 0.5`
  in #12 (separate PR); the slider is session-only.
- Regular remote empty-house baselines (owner away) to validate it over time.
- Two failed walk-through attempts discarded (marks lost in the app terminal pane;
  marks contradicting scores); only the clean run is committed.
- Multi-module localization idea filed as #11 (MCDA: refine threshold 415, multi-module
  heat map 325, ML classification on raw CSI 190 — not pursued).

## 2026-10-23 — Module back online + experiment capture tooling (#6)

**Context.** Board `espectre-01` (flashed 2026-06-17 on the homelab Pi, ESPHome 2026.5.3,
ESPectre 2.8.0) was re-plugged after ~4 months. It rejoined Wi-Fi at `<MODULE_IP>` on
the homelab LAN, reachable from the laptop only through the Pi (`<homelab>`, Tailscale).
First real measurement = experiment `0002`: 180 s unattended, house empty.

**Findings.**

- Cold restart needs nothing: mDNS, web server (80) and native API (6053) all answer.
- Idle score ≈ 0.23 (p99 0.349, max 0.406) against the default threshold 0.4: one 1 s
  false positive in 3 min with the house empty. Headroom is too thin by default.
- Device log prints `thr:0.3690` while the `Threshold` entity reads `0.4`: to explain
  from upstream before tuning.

**Decisions.**

- Experiment recorder = **SSE + Python** (MCDA 410/500) over MQTT + Python (350, design
  fallback if SSE proves unstable on long runs: swaps `capture.sh` only) and Home
  Assistant recorder (335). Criteria: fit to ground-truth stats 25, analysis freedom 20,
  effort 15, 24/7 recording 10, firmware change 10, KISS 10, learning value 10.
- Python profile added as **stdlib only** (no pandas yet): `csv` + `statistics` cover the
  stats/precision/recall needs; pandas can come with a notebook if ever needed.
- CSV data files contain score + motion state only (privacy doc updated); short runs
  referenced by a journal entry are committed.

**Done.**

- UML `docs/architecture/diagrams/experiment-capture/` (data-flow, sequence).
- `experiments/tools/`: `capture.sh` (SSE → CSV, optional ssh hop), `mark.sh` (manual
  ground truth), `sse_to_csv.py`, `analyze.py` (stats, episodes, precision/recall,
  markdown out). `tests/` with pytest (97 % coverage), ruff + mypy strict, CI `python.yml`.
- Experiment `0002` + its CSV; README / experiments README / privacy / CLAUDE.md updated.

**Next.** 10 min baseline with documented placement, then a marked walk-through to pick
the threshold on precision/recall; investigate `thr:0.3690`.

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

- `git init` on `main`, local git email set to `<personal email>`.
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
