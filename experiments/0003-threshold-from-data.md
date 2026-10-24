# Experiment 0003 — Empty-house baseline + marked walk-through to pick a threshold

- **Date:** 2026-10-23 (baselines) and 2026-10-24 (walk-through)
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

(Answered differently than planned: see Findings, the trade-off that matters here is
empty vs occupied.)

## Procedure

1. Owner away all day (house genuinely empty). Baseline run from the laptop through the
   Pi: `tools/capture.sh 192.168.1.123 600 baseline-empty-house benoit@bb-homelab`.
2. The first run was cut after 354 s (curl exit 56, connection reset) and contained a
   large burst in its first minute; it was repeated in full as `baseline-empty-house-2`.
   Both CSVs are kept.
3. Next morning (2026-10-24), owner at home, **windows closed**, fan on, the owner's
   daughter also in the room (she woke up during the test): marked walk-through.
   `m` = *someone* moves in the room (owner or daughter), `s` = nobody moves. Phases
   switch on the wall clock at :00 / :30, still = seated, arms resting.
4. Two earlier walk-through attempts were discarded and not committed: the first lost
   its marks (`mark.sh` started from the Claude desktop app's terminal pane exits after
   the first key: single-key reads do not work there, use a system terminal), the
   second had marks that contradict the scores (owner moving during "still" phases).
5. `tools/analyze.py <csv> --threshold 0.369|0.4|0.5|0.6|0.8` on every run (the marks
   file next to the CSV is picked up automatically).

## Scenarios & results

| Scenario | Expected | Detected? | Notes |
|---|---|---|---|
| Empty house, run 1 (354 s) | no motion | 11 false episodes | all in the first 55 s, max **1.93**; windows were open: a draught (laundry / curtain) is the probable cause |
| Empty house, run 2 (599 s) | no motion | 6 device episodes (2 samples ≥ 0.4) | max 0.435; quiet, no burst |
| Person walking (marked, 4 × 30 s) | motion | yes, every phase | mean 0.94–1.12, peaks ~3.0 |
| Person sitting still (marked, 5 phases) | no motion | **yes, every phase** | mean 0.70–1.47: presence alone triples the empty-room score |

### Baseline run 1 — `data/2026-10-23-baseline-empty-house.csv`

Window 12:23:08 → 12:29:03 (354 s), 381 samples: min 0.123, median 0.230, mean 0.257,
p99 0.951, max 1.929. 20 samples ≥ 0.4 in 11 episodes, 11 device motion episodes — every
one of them between 12:23:08 and 12:24:03. From 12:24:10 to the end (301 samples) the
room is quiet: mean 0.225, p99 0.336, max **0.377**, nothing over 0.4.

### Baseline run 2 — `data/2026-10-23-baseline-empty-house-2.csv`

Window 12:31:08 → 12:41:07 (599 s), 630 rows. `tools/analyze.py … --threshold 0.4`:

| Metric | Value |
|---|---|
| Samples | 615 (~1 Hz) |
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

### Walk-through — `data/2026-10-24-walkthrough-marked-2.csv` (+ `.marks.csv`)

Window 11:27:06 → 11:32:36 (329 s), 10 marks, phases on the clock from 11:28:03.
Score per marked phase:

| Phase | Samples | Mean | Max |
|---|---|---|---|
| still (11:28:03, 90 s) | 90 | 0.83 | 1.88 |
| moving (11:29:30) | 34 | 0.94 | 3.03 |
| still (11:30:01) | 30 | 0.94 | 1.96 |
| moving (11:30:30) | 33 | 1.07 | 2.96 |
| still (11:31:00) | 31 | 0.70 | 1.36 |
| moving (11:31:30) | 34 | 1.12 | 3.10 |
| still (11:32:01) | 30 | 1.47 | 3.88 |

Moving and still phases overlap completely, so precision for "someone is moving" is
poor at any threshold (`analyze.py --threshold 0.5`: TP 89, FP 197, FN 19, TN 44 →
precision 0.31, recall 0.82). The "false positives" are seated people, not noise.

The question this placement can answer is **empty vs occupied**. Share of score samples
at or above each threshold, empty house (baseline run 2, 10 min) vs occupied
(walk-through from 11:28:03, both phases):

| Threshold | Empty house ≥ thr | Occupied ≥ thr | Occupied minutes with a detection |
|---|---|---|---|
| 0.369 (current, auto) | 0.8 % (6 device episodes) | 92.4 % | 5 / 5 |
| 0.4 | 0.3 % (2 samples) | 89.7 % | 5 / 5 |
| **0.5** | **0 %** | **79.3 %** | **5 / 5** |
| 0.6 | 0 % | 71.4 % | 5 / 5 |
| 0.8 | 0 % | 54.5 % | 5 / 5 |

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

- **A seated, still person** (and the daughter in the room) keeps the score at 0.7–1.5:
  not a false positive for presence, but it makes "motion vs still" unanswerable here.

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
### Why the device fires at 0.369 while the entity shows 0.4 (ESPectre 2.8.0 source)

Read from the upstream tag `2.8.0` (`components/espectre/`), closes the `0002` side
observation and the matching item of issue #8:

- **The threshold is adaptive, recomputed at every boot and every `Calibrate`.** With the
  default `segmentation_threshold: auto`, after the ~10 s baseline calibration the
  firmware takes the moving-variance values of that window and sets
  `threshold = P95 × 1.1` (`threshold.h`, `espectre.cpp` calibration callback). On
  `espectre-01` that gave **0.3690**: the log value is the real detector threshold.
  It is consistent with our 10 min p99 of 0.35: 10 s of calibration under-estimates the
  tail, so the auto threshold ends up inside the idle noise.
- **0.4 is a display rounding.** The `Threshold` number entity is declared with
  `step=0.1` (`__init__.py`); the web server and Home Assistant show 0.369 as 0.4.
  Nothing is wrong with the entity, it just cannot display the third decimal.
- **A slider change is session-only.** `set_threshold_runtime()` logs "session-only,
  recalculated at boot": any value set from the web UI or HA is lost at the next reboot
  or recalibration. A durable threshold needs `segmentation_threshold: <number>` in the
  YAML (MANUAL mode, adaptive calculation skipped, the log then prints both).
- **No hysteresis, but a 3-hit debounce.** `MVSDetector` compares the moving variance
  strictly `>` / `<` the same threshold; the effective state only flips after
  `motion_on_hits` / `motion_off_hits` = 3 consecutive evaluations.
- **Evaluation is 4× faster than publication.** The detector is evaluated every
  `evaluation_interval` = 25 packets and the score is published every
  `publish_interval` = 100 packets (= the 100 pkt/s traffic generator), i.e. ~250 ms vs
  ~1 s. A motion episode therefore needs only ~750 ms over the threshold, and the 1 Hz
  SSE stream can miss the whole crossing — exactly the 12:36:32 trigger with no
  published sample over 0.344.

Consequences for this experiment: compare the CSV scores against **0.369**, not 0.4,
when explaining device episodes; and the chosen threshold must go into the YAML as
`segmentation_threshold`, not into the slider.

- **This placement senses presence, not movement.** A person sitting still with arms
  resting scores 0.7–1.5 against 0.23 for the empty room; walking adds little (~1.0).
  The useful binary output is "someone is in the room".
- **Recommended threshold: 0.5** (MCDA, owner-validated: 0.5 → 435/500, 0.6 → 405,
  0.4 → 275; criteria: no false alarm in the empty house 40, presence detection 35,
  margin above the idle max 25). Zero empty-house samples over 0.5 in 10 min, presence
  seen 79 % of the time and in every occupied minute. Margin over the idle max (0.435)
  is only +0.065: if false alarms come back over longer runs, 0.6 is the fallback
  (sensitivity check: weighting the margin 45 makes 0.6 win). No threshold filters a
  draught burst (1.93 with windows open).
- **Tooling:** the SSE capture was cut twice (curl exit 56 after ~6 and ~8 min) and ran
  fine twice; long runs need a retry/reconnect or HA history (#14). `mark.sh` needs a
  real terminal (single-key reads).

## Next

- Apply `segmentation_threshold: 0.5` in
  `esphome/espectre.yaml` (separate PR); the slider would not survive a reboot.
- Regular remote empty-house baselines (owner away, run from anywhere through the Pi)
  to check that 0.5 holds over days, weather and seasons; then HA history (#14) for
  overnight runs once Home Assistant is back.
- Optional `0004`: 10 min fan off + windows closed, to measure what the fan adds.
- Issue #11: multi-module room-level localization (heat map), long term.
