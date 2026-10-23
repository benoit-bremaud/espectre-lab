# Experiment 0003 — Empty-house baseline + marked walk-through to pick a threshold

- **Date:** 2026-10-23
- **Board:** ESP32-C3 SuperMini (`esp32-c3-devkitm-1`), `espectre-01` at `192.168.1.123`
- **ESPHome version:** 2026.5.3 (firmware flashed 2026-06-17, no OTA since)
- **ESPectre version/commit:** `github://francescopace/espectre@2.8.0`

## Setup

- **Location:** studio flat: one large living room (bed + sofa, round table, kitchen
  corner) plus a small bathroom/WC next door.
- **Board placement:** on a small shelf recessed in the wall above the sofa-bed, ~1.8 m
  from the floor, at the far end of the room from the access point.
- **Access point:** ISP box next to the homelab Raspberry Pi, just under 10 m away in the
  same room. Line of sight crosses a round table (~1.5 m diameter) with 4 chairs.
- **Everyday perturbations (left as-is, on purpose):** a small ceiling fan right above
  the bed, i.e. close to the module, which the owner usually keeps running; laundry
  drying in the room (always the case). No pets, no robot vacuum.
- **Threshold / config changes:** defaults. `Threshold` entity reads **0.4**; the device
  log line prints `thr:0.3690` (see Findings).

## Goal

Experiment `0002` showed the idle score at ~0.23 with a p99 of 0.349 and one false
trigger at 0.406 in 3 min: the default threshold of 0.4 has almost no headroom. This
run answers, with data:

1. What is the idle noise floor over 10 min in the owner's **real everyday conditions**
   (fan on, laundry drying), with a documented placement?
2. What score does a person walking in the room produce, versus sitting still?
3. Which threshold (0.4 / 0.5 / 0.6) gives the best precision/recall trade-off?

## Procedure

1. Owner away all day (house genuinely empty). Baseline run from the laptop through the
   Pi: `tools/capture.sh 192.168.1.123 600 baseline-empty-house benoit@bb-homelab`.
2. The first run was cut after 354 s (curl exit 56, connection reset) and contained a
   large burst in its first minute; it was repeated in full as `baseline-empty-house-2`.
   Both CSVs are kept.
3. Evening, owner at home, **windows closed**, fan on: second capture
   (`walkthrough-marked`) while `tools/mark.sh walkthrough-marked` records ground truth
   (`m` when starting to walk, `s` when stopping, ~30 s cycles, ≥ 6 cycles, `q` to end).
4. `tools/analyze.py <csv> --threshold 0.4|0.5|0.6` on each run; the walk-through run
   with `--marks` for precision/recall.

## Scenarios & results

| Scenario | Expected | Detected? | Notes |
|---|---|---|---|
| Empty house, run 1 (354 s) | no motion | 11 false episodes | all in the first 55 s, max **1.93**; windows were open: a draught (laundry / curtain) is the probable cause |
| Empty house, run 2 (599 s) | no motion | 6 device episodes (2 samples ≥ 0.4) | max 0.435; quiet, no burst |
| Person walking (marked) | motion | _to fill this evening_ | |
| Person sitting still (marked) | no motion | _to fill this evening_ | |

### Baseline run 1 — `data/2026-10-23-baseline-empty-house.csv`

Window 12:23:08 → 12:29:03 (354 s), 381 samples: min 0.123, median 0.230, mean 0.257,
p99 0.951, max 1.929. 20 samples ≥ 0.4 in 11 episodes, 11 device motion episodes — every
one of them between 12:23:08 and 12:24:03. From 12:24:10 to the end (301 samples) the
room is quiet: mean 0.225, p99 0.336, max **0.377**, nothing over 0.4.

### Baseline run 2 — `data/2026-10-23-baseline-empty-house-2.csv`

Window 12:31:08 → 12:41:07 (599 s), 630 rows. `tools/analyze.py … --threshold 0.4`:

| Metric | Value |
|---|---|
| Samples | ~600 (~1 Hz) |
| Min | 0.126 |
| Median | 0.229 |
| Mean | 0.232 |
| p99 | 0.352 |
| Max | 0.435 |
| Samples ≥ 0.4 | 2 (0.435, 0.413) |
| Episodes ≥ 0.4 (from scores) | 2 |
| Motion ON episodes (device) | 6 (each ~1 s) |

False-positive count per candidate threshold over the same 10 min, from the published
scores: **0.4 → 2, 0.5 → 0, 0.6 → 0**.

### Walk-through — `data/2026-10-23-walkthrough-marked.csv`

_To fill this evening: analyze.py tables at 0.4 / 0.5 / 0.6 with `--marks`, precision,
recall, score range while walking vs still._

## False positives observed

- **Draught burst** (run 1, first minute): scores up to 1.93 with nobody home, windows
  open, fan on, laundry drying. No threshold filters a 1.9 spike; the only fix is the
  environment (close the windows) or accepting such events.
- **Idle noise just above 0.4** (run 2): two 1 s triggers at 0.435 and 0.413 in 10 min,
  in the owner's normal fan-on / laundry conditions.
- **Triggers below the exposed threshold**: the device switched `Motion Detected` ON at
  12:32:51 (score 0.397), 12:38:08 (0.379), 12:40:19 (0.390) and even 12:36:32 when the
  highest published score around it was 0.344. The published stream is ~1 Hz while the
  firmware evaluates the score faster, so some crossings never appear in the CSV; and the
  comparisons that do appear are consistent with an internal threshold of **0.369**, not
  0.4 (the `thr:0.3690` log value from `0002`, issue #8). The 0.352 sample at 12:34:28
  did not trigger, which fits 0.369 as well.

## Findings

- **Idle floor confirmed with a documented placement**: mean 0.23, p99 0.35, max 0.435
  over 10 min in everyday conditions (fan on, laundry). Same picture as `0002`: the
  default threshold sits inside the noise.
- The ceiling fan and the drying laundry **do not** push the idle score over 0.5 by
  themselves; an open window with a draught does (1.9).
- The device is **more sensitive than its `Threshold` entity says**: it fires around
  0.369 and on sub-second peaks the SSE stream does not publish. Counting
  `Samples ≥ threshold` in the CSV therefore under-estimates real false positives;
  `Motion ON episodes (device)` is the number to trust for the deployed firmware.
- _Threshold recommendation: to complete after the walk-through._

## Next

- Walk-through this evening, windows closed (step 3 of the procedure).
- Apply the chosen threshold in `esphome/espectre.yaml` in a separate PR.
- Issue #8: trace `thr:0.3690` in ESPectre 2.8.0 source (how the entity value maps to
  the internal threshold) before trusting any entity-based tuning.
- Optional `0004`: 10 min fan off + windows closed, to measure what the fan adds.
- Issue #11: multi-module room-level localization (heat map), long term.
