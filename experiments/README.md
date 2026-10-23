# Experiments journal

Dated notes on real ESPectre runs: hardware, placement, scenarios, and what actually
happened (especially false positives). The point is to learn empirically how usable
Wi-Fi CSI sensing is in a real home.

## How to log an experiment

1. Copy `0001-template.md` to the next number + a short slug,
   e.g. `0003-living-room-walkthrough.md`.
2. Fill every section honestly — negative results are the valuable ones here.
3. Reference the experiment in `../PROJECT_LOG.md` if it drives a decision.

## Tools (`tools/`)

Reproducible capture + analysis, stdlib Python only (decision: SSE + Python, see
`docs/architecture/diagrams/experiment-capture/`). The firmware is untouched: the source is
the ESPHome web server's `/events` stream.

```bash
# paths below are relative to experiments/
# 1. record N seconds into data/<date>-<slug>.csv (4th arg: ssh host when the module is on another LAN)
tools/capture.sh 192.168.1.123 600 baseline-empty-house benoit@bb-homelab
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

## Index

- `0001-template.md` — template (not a real experiment).
- `0002-reconnect-baseline-3min.md` — 2026-10-23: cold restart after months unplugged
  (OK) + 180 s unattended baseline; idle score ~0.23, one false trigger at 0.406 vs
  default threshold 0.4.
- `0003-threshold-from-data.md` — 2026-10-23: documented placement, two 10 min
  empty-house baselines in everyday conditions (fan on, laundry; one draught burst to
  1.93 with windows open) + marked walk-through to pick a threshold from
  precision/recall. Device fires at ~0.369, not at the 0.4 the entity shows.
