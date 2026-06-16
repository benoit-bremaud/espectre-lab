# Project Log — espectre-lab

Chronological operational logbook. Complements `git log`: records decisions, context,
and findings that the commit history alone does not capture. Newest entries on top.

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

**Context.** Board (ESP32-S3/C6/C3) now in hand; first real flash imminent. Per the
UML-first rule, the sensing feature must be modelled before the build. Only the
data-flow diagram existed, and it was mis-numbered vs the convention (use-case first →
data-flow last).

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
