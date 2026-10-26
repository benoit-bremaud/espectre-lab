# Experiments journal

Dated notes on real ESPectre runs: hardware, placement, scenarios, and what actually
happened (especially false positives). The point is to learn empirically how usable
Wi-Fi CSI sensing is in a real home.

## How to log an experiment

1. Copy `0001-template.md` to the next number + a short slug,
   e.g. `0003-living-room-walkthrough.md`.
2. Fill every section honestly — negative results are the valuable ones here.
3. Reference the experiment in `../PROJECT_LOG.md` if it drives a decision.

## Local lab values

Docs and commands use placeholders because this repository is public: `<MODULE_IP>` (the
module), `<SSH_HOST>` (`user@host` of the homelab jump host), `<homelab>` (its hostname),
`<other-user>` (another account on it), `<UNREACHABLE_IP>` (a deliberately dead address in
the smoke tests), `<LAN_CIDR>` / `<LAPTOP_CIDR>` (the homelab and laptop subnets), `<repo>`
(the local checkout path) and `<personal email>`. Copy `lab.env.example` to `lab.env` (gitignored), fill in the real
values and `source experiments/lab.env`, then call the tools with `"$MODULE_IP"` and
`"$SSH_HOST"`. The pre-push gate (`scripts/hooks/pre-push`) refuses private IPs, the
homelab hostname, personal e-mails, home paths and MAC addresses; enable it once per clone with
`scripts/install-hooks.sh` (needs `gitleaks` on PATH).

## Tools (`tools/`)

Reproducible capture + analysis, stdlib Python only (decision: SSE + Python, see
`docs/architecture/diagrams/experiment-capture/`). The firmware is untouched: the source is
the ESPHome web server's `/events` stream.

```bash
# paths below are relative to experiments/
# 1. record N seconds into data/<date>-<slug>.csv (4th arg: ssh host when the module is on another LAN)
tools/capture.sh <MODULE_IP> 600 baseline-empty-house <SSH_HOST>
# 2. (optional, second terminal) ground-truth marks: m = moving, s = still, q = quit
tools/mark.sh baseline-empty-house
# 3. stats + precision/recall as markdown, paste into the journal
python3 tools/analyze.py data/2026-10-23-baseline-empty-house.csv --threshold 0.4
```

Data files hold the entities the web server exposes (movement score, motion state,
threshold, calibrate switch), never raw CSI. Commit the
small CSVs referenced by a journal entry; keep long runs out of git.

Dev checks: `pip install -r requirements-dev.txt`, then `ruff format . && ruff check .`,
`mypy`, `pytest --cov` (CI runs the same).

Planned runs and their configuration: [`../docs/test-plan.md`](../docs/test-plan.md).

## Index

- `0001-template.md` — template (not a real experiment).
- `0002-reconnect-baseline-3min.md` — 2026-10-23: cold restart after months unplugged
  (OK) + 180 s unattended baseline; idle score ~0.23, one false trigger at 0.406 vs
  default threshold 0.4.
- `0003-threshold-from-data.md` — 2026-10-23: documented placement, two 10 min
  empty-house baselines in everyday conditions (fan on, laundry; one draught burst to
  1.93 with windows open) + marked walk-through to pick a threshold from
  precision/recall. Device fires at ~0.369 (auto threshold), not at the 0.4 the
  entity shows. Finding: the placement senses **presence**, not movement (a seated
  person scores 0.7–1.5 vs 0.23 empty); recommended threshold **0.5**.
- `0004-baseline-empty-closed-nofan.md` — 2026-10-26: 30 min empty-house baseline,
  windows closed, **fan off**: median 0.100, p99 0.163, max 0.211, 0 device episodes —
  2.3× quieter than with the fan on (0.23). Fan and draught, not the module, drive the
  false positives. Reference run of the [test plan](../docs/test-plan.md).
- `0005-lights-onoff.md` — 2026-10-26: test C3, lights switched by a temporary timed Home
  Assistant automation during a 24 min empty-house capture. String lights on/off: no
  effect (median 0.092 vs 0.094 off). Neons did not respond (not tested). Floor 0.094
  reproduces `0004`.
