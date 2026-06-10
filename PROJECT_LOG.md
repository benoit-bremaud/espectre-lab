# Project Log — espectre-lab

Chronological operational logbook. Complements `git log`: records decisions, context,
and findings that the commit history alone does not capture. Newest entries on top.

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
