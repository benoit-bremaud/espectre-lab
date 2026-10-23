# Experiment 0002 — Reconnect check + 3-minute unattended baseline

- **Date:** 2026-10-23
- **Board:** ESP32-C3 SuperMini (`esp32-c3-devkitm-1`)
- **ESPHome version:** 2026.5.3 (build on the homelab Pi, 2026-06-17)
- **ESPectre version/commit:** `github://francescopace/espectre@2.8.0`

## Setup

- **Location:** home, room not recorded (module re-plugged after ~4 months unpowered).
- **Board placement:** on a USB charger; exact spot / height not recorded.
- **Access point:** home Wi-Fi, homelab LAN `192.168.1.0/24`; module at `192.168.1.123`
  (`espectre-01.local`). Note: the laptop sits on `192.168.0.0/24`, so the module is
  only reachable through the Pi (`bb-homelab` over Tailscale), not from the laptop LAN.
- **Threshold / config changes:** defaults. Threshold read back from the device: **0.4**.
  Firmware is the one flashed on 2026-06-17 (commit `fe55677`), no OTA since.

## Goal

1. Confirm the module survives a cold restart after months unplugged: joins Wi-Fi, keeps
   its name, web server and native API answer.
2. Capture a short unattended baseline of the movement score to see how much headroom
   there is under the default threshold at rest.

## Procedure

1. Plug the module on a USB charger, wait for the LED.
2. From the Pi: `getent hosts espectre-01.local`, ping, check TCP 80 and 6053.
3. From the Pi, record the web-server event stream for 180 s:
   `curl -N http://192.168.1.123/events`, timestamping every `data:` line.
4. Nobody deliberately moved near the module; the household was not frozen either
   (ordinary daytime activity elsewhere in the home).
5. Aggregate the `Movement Score` samples and the `Motion Detected` transitions.

## Scenarios & results

| Scenario | Expected | Detected? | Notes |
|---|---|---|---|
| Cold restart after ~4 months | boots, rejoins Wi-Fi | yes | mDNS OK, ping ~5 ms, ports 80 + 6053 open, entities present |
| Unattended room, 180 s | no motion | 1 false trigger | 185 score samples; motion ON for 1 s at 10:48:51 |

Data: `data/2026-10-23-reconnect-baseline.csv` (converted from the raw capture; later
runs are written directly by `tools/capture.sh`). Table produced by
`tools/analyze.py data/2026-10-23-reconnect-baseline.csv`:

| Metric | Value |
|---|---|
| Samples | 185 (~1 Hz over 179 s) |
| Min | 0.116 |
| Median | 0.227 |
| Mean | 0.229 |
| p99 | 0.349 |
| Max | 0.406 |
| Samples ≥ 0.4 | 1 |
| Episodes ≥ 0.4 (from scores) | 1 |
| Motion ON episodes (device) | 1 (1 s) |

Top five samples: 0.406, 0.359, 0.347, 0.312, 0.309. The baseline hovers around 0.2–0.3
with sporadic spikes; the single 0.406 spike is the one that crossed the threshold. With
`--threshold 0.5` the same CSV yields zero samples over and zero episodes.

Side observation from the device log lines mixed into the stream: ESPectre prints
`thr:0.3690` on every line, while the `Threshold` number entity reads `0.4`. The internal
threshold is therefore not exactly the exposed value (adaptive or hysteresis?); to check
against upstream code before tuning. The log also showed `uptime:418` at capture start,
i.e. the module had been powered for ~7 min, well past the ~10 s calibration.

## False positives observed

- One 1-second `Motion Detected = ON` on a 0.406 spike while nobody was near the module.
  Cause unknown (nothing was watched): candidates are ordinary activity elsewhere in the
  home, neighbour 2.4 GHz traffic, or simply the idle noise floor sitting too close to the
  default threshold.

## Findings

- The module is robust to a long power-off: no reflash, no reconfiguration needed.
- At rest the score sits at ~0.23 ± spikes up to ~0.35, i.e. the default threshold of 0.4
  leaves only ~0.05 of headroom above the observed idle peaks. Expect occasional spurious
  triggers with defaults in this placement.
- The web server's `/events` SSE stream is a good enough data source for experiments
  (JSON per entity, ~1 Hz); no Home Assistant needed.
- Procedure gap: placement and room were not written down before recording, which makes
  the numbers hard to compare later. Fix that in the next run.

## Next

- Repeat with a documented placement and a genuinely still room (nobody home or
  everybody seated), for 10 minutes, to get a clean noise floor:
  `tools/capture.sh 192.168.1.123 600 baseline-empty-house benoit@bb-homelab`.
- Then a controlled walk-through with `tools/mark.sh` running, to measure the score a
  real person produces and pick a threshold with real margin (likely 0.5–0.6 rather
  than 0.4) from precision/recall.
- Explain the `thr:0.3690` vs `0.4` discrepancy from the upstream source.
