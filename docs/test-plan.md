# Test plan — catalogue of experiments

What we want to learn about Wi-Fi CSI sensing on this one module, in what order, and
with which configuration. Each row is one GitHub issue (kanban:
<https://github.com/users/benoit-bremaud/projects/74>), tracked in #33. A finished test
becomes a dated entry in [`experiments/`](../experiments/README.md).

## Common setup

- ESP32-C3 `espectre-01`, ESPectre 2.8.0, ESPHome defaults (auto threshold, see
  `experiments/0003-threshold-from-data.md`), current placement (shelf above the
  sofa-bed). Reach the module through the homelab Pi (`ssh <SSH_HOST>`).
- **One variable changes at a time** against the reference run
  [`0004`](../experiments/0004-baseline-empty-closed-nofan.md) (empty, windows closed,
  fan off: median 0.100, p99 0.163, max 0.211, 0 device episodes).
- Capture and analyse:

  ```bash
  experiments/tools/capture.sh <MODULE_IP> <seconds> <slug> <SSH_HOST>
  python3 experiments/tools/analyze.py experiments/data/<date>-<slug>.csv --threshold 0.4
  python3 experiments/tools/analyze.py experiments/data/<date>-<slug>.csv --threshold 0.5
  ```

- Ground-truth marks (`tools/mark.sh <slug>`) must be typed in a **system terminal**: the
  Claude app terminal pane cannot read single keys.
- Trust `Motion ON episodes (device)` over `Samples ≥ threshold` for the firmware's real
  false positives (the stream is ~1 Hz, the detector evaluates ~4× faster).

## A. Empty house (owner away)

| Id | Issue | Test | Configuration | Duration |
|---|---|---|---|---|
| A1 | #16 | Reference baseline | windows closed, fan off. **Done** (0004) | 30 min |
| A2 | #17 | Fan effect | windows closed, fan **on**, usual speed, slug `baseline-empty-closed-fan` | 15 min |
| A3 | #18 | Draught effect | windows **open**, fan off, slug `baseline-empty-open-nofan` | 15 min |
| A4 | #19 | Fan speed dose-response | windows closed, speeds 1 / 2 / 3, after A2 | 3 × 10 min |
| A5 | #20 | Wi-Fi traffic load | as A1, second device streaming or downloading | 15 min |
| A6 | #21 | Cold reboot calibration | reset the module in an empty room, repeat 3 times | 10 min each |

## B. Room occupied (owner at home)

| Id | Issue | Test | Configuration | Duration |
|---|---|---|---|---|
| B1 | #22 | Sensitivity ladder | fan off; marked 30 s phases: seated, lying, arm gesture, walking | 10 min |
| B2 | #23 | Presence vs movement | stay still seated then lying, watch the score decay | 2 × 5 min |
| B3 | #24 | Distance / position | same gesture at 1 / 3 / 5 m and behind the table | 4 × 3 min |
| B4 | #25 | Trapped calibration | reset the module while someone moves | 5 min |
| B5 | #26 | Bathroom, through-wall | walk with the door open, then closed | 2 × 3 min |
| B6 | #27 | Latency | 10 starts and 10 stops timed against marks | 10 min |

## C. Everyday perturbations

| Id | Issue | Test | Configuration |
|---|---|---|---|
| C1 | #28 | Door, blinds, washing machine, microwave | empty room, one event at a time, marked, 5 min each |
| C2 | #29 | Pets, robot vacuum | idea: needs borrowed equipment |
| C3 | #34 | Remote lights (string lights + 2 neons). **String lights done (0005): no effect; neons pending** | empty room, fan off; owner toggles remotely on the clock: all off / string / neons / all on, 5 min each. **Runnable while away** |

## D. Long run and robustness

| Id | Issue | Test | Configuration |
|---|---|---|---|
| D1 | #14 | Baseline 24 h to 7 d | Home Assistant recorder history (HA is back since 2026-10-26; unblocked) |
| D2 | #30 | Robustness | router reboot, Wi-Fi off/on 60 s, power cycle |

## E. Validate the final configuration

| Id | Issue | Test | Configuration |
|---|---|---|---|
| E1 | #12 | Durable threshold | `segmentation_threshold: 0.5` + debounce in the YAML, then rerun A1 and B1 |
| E2 | #31 | Alternative placement | move the module, rerun A1 and B1 |

## Suggested order

1. **Owner away:** C3 neon blocks (string lights done in 0005), D1 (HA history), A3, A6; A2 and A4 need the fan, so they wait until it can be driven (project `smart-ceiling-fan`) or the owner is home (A5 if time allows).
2. **Owner at home:** B1, B2, B6.
3. Then E1 (closes #12), B3, E2, B4, B5.
4. Later: C1, D2; C2 only if equipment turns up.
