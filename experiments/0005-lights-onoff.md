# Experiment 0005 — Remote lights as a controlled perturbation (test C3, partial)

- **Date:** 2026-10-26
- **Board / versions / placement:** unchanged from `0004` (ESP32-C3 `espectre-01`, ESPectre
  2.8.0, ESPHome 2026.5.3, shelf above the sofa-bed).
- **Conditions:** owner away, house empty, windows closed, ceiling fan off.
- **Threshold / config changes:** none.

## Goal

Do the remotely switchable lights around the bed (a string of lights on the Zigbee plug
`switch.prise_salon`, two Zigbee neon tubes `light.neon_gauche` / `light.neon_droit`)
change the idle score? Issue #34.

## Procedure

1. Light control without any new credential: a **temporary Home Assistant automation**
   created from the owner's already-signed-in browser, with time triggers (no webhook,
   no token): 16:01 all off, 16:06 string lights, 16:11 neons, 16:16 all on, 16:21 all off.
   Deleted right after the run (HA returns 404 for it).
2. `tools/capture.sh <MODULE_IP> 1440 lights-onoff <SSH_HOST>` from 15:58:26 to 16:22:26.
3. Light states checked afterwards in the HA history.

## Scenarios & results

HA history: the plug switched exactly at 16:06 (on), 16:11 (off), 16:16 (on), 16:21 (off).
**The neons never changed state**: `light.turn_on` is accepted without error but the
lamps stay `off` (last change 14:58, before the run; a 5 s manual probe after the run
gives the same). Probably unpowered at the wall switch or out of Zigbee reach. So the
"neons" block is really all off and the "all" block is string lights only.

| Block (actual state) | Samples | Median | p99 | Max | ≥ 0.4 |
|---|---|---|---|---|---|
| 15:58–16:01 all off | 159 | 0.099 | 0.145 | 0.183 | 0 |
| 16:01–16:06 all off | 311 | 0.094 | 0.144 | 0.334 | 0 |
| 16:06–16:11 string lights on | 310 | 0.092 | 0.140 | 0.153 | 0 |
| 16:11–16:16 all off (neons failed) | 310 | 0.097 | 0.169 | 0.201 | 0 |
| 16:16–16:21 string lights on | 309 | 0.092 | 0.145 | 0.155 | 0 |
| 16:21–16:22 all off | 90 | 0.094 | 0.148 | 0.177 | 0 |

Whole run (1439 s, 1489 samples): median 0.094, p99 0.153, max 0.334, **0 device
episodes**.

## False positives observed

None. The single 0.334 peak (all-off block) is isolated and below every candidate
threshold.

## Findings

- **The string lights and their Zigbee plug do not perturb the CSI score**: the "on"
  blocks (median 0.092) match the "off" blocks (0.094–0.099) and the `0004` reference
  (0.100). The switching moments themselves leave no peak.
- Second inert-room run of the day: median 0.094 vs 0.100 in `0004`, so the floor of
  ~0.10 is reproducible.
- **Neons not tested**: rerun the neon blocks once they respond to Home Assistant
  (check the wall switch / Zigbee link from the `home-assistant` project).
