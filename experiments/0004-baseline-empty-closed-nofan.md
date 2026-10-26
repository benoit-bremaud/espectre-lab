# Experiment 0004 — Empty-house baseline, windows closed, fan off (test A1)

- **Date:** 2026-10-26
- **Board:** ESP32-C3 SuperMini (`esp32-c3-devkitm-1`), `espectre-01` at `<MODULE_IP>`
- **ESPHome version:** 2026.5.3 (firmware unchanged since 2026-06-17)
- **ESPectre version/commit:** `github://francescopace/espectre@2.8.0`

## Setup

- **Location / placement / access point:** unchanged from `0003` (studio flat, shelf above
  the sofa-bed at 1.8 m, ISP box just under 10 m away, round table in the line of sight).
- **Conditions:** owner away all day, house genuinely empty (no pets, no robot vacuum),
  **windows closed, ceiling fan off**, laundry left drying as usual.
- **Threshold / config changes:** none (defaults, auto threshold).

## Goal

`0003` measured the idle noise with the fan on and, in one run, windows open. It could not
tell which of the fan and the draught drives the false positives. This run is the
reference "inert room" (test **A1** of `docs/test-plan.md`, issue #16): the lowest noise
floor the placement can show.

## Procedure

1. `tools/capture.sh <MODULE_IP> 1800 baseline-empty-closed-nofan <SSH_HOST>`
   (started from the system terminal at 11:15, ran to completion in one piece, no SSE
   reset this time).
2. `tools/analyze.py data/2026-10-26-baseline-empty-closed-nofan.csv --threshold 0.4`
   and `--threshold 0.5`.

## Scenarios & results

| Scenario | Expected | Detected? | Notes |
|---|---|---|---|
| Empty house, windows closed, fan off (1799 s) | no motion | **no** | 0 device episodes, 0 samples ≥ 0.4 |

Window 11:15:13 → 11:45:12 (1799 s), 1862 samples (~1 Hz):

| Metric | Value | `0003` run 2 (fan on) |
|---|---|---|
| Min | 0.058 | 0.126 |
| Median | **0.100** | 0.229 |
| Mean | 0.102 | 0.232 |
| p99 | **0.163** | 0.352 |
| Max | **0.211** | 0.435 |
| Samples ≥ 0.4 | 0 | 2 |
| Samples ≥ 0.5 | 0 | 0 |
| Motion ON episodes (device) | **0** | 6 |

Stable over time: median per 5 min block 0.098–0.102, block max 0.169–0.211, no drift and
no burst.

## False positives observed

None. In particular no first-minute burst like `0003` run 1 (windows open).

## Findings

- **An inert room idles at about 0.10**, 2.3× lower than with the fan on (0.23). The p99
  (0.163) and the max (0.211) sit far below 0.369 (current auto threshold), 0.4 and 0.5.
- The fan and/or the draught are therefore the **dominant source of the false positives**
  seen in `0002` and `0003`; the module itself is quiet.
- The recommended threshold **0.5** (see `0003`) keeps more than 2× margin over the
  quietest-room maximum; even the 0.4 default would not have fired here.
- **Limits:** this run changes two things at once (windows closed *and* fan off) against
  `0003`, so it does not separate them; the next runs do (A2 fan only `#17`, A3 windows
  only `#18`). One 30 min run on one day: no claim about long-term stability (D1, `#14`).

## Follow-ups

- A2 (#17) and A3 (#18) to split the fan and draught contributions.
- A6 (#21): is the ~10 s calibration as quiet after a cold reboot?
- #12 still applies: make 0.5 durable in the YAML.
