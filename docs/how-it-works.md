# How it works — Wi-Fi CSI motion sensing

## The core idea

A Wi-Fi radio constantly measures the quality of the signal it receives, across many
sub-frequencies (subcarriers), as **Channel State Information (CSI)**. CSI describes how
the radio wave was attenuated and phase-shifted on its way from the transmitter to the
receiver.

When a person moves in the room, their body reflects, absorbs and scatters those radio
waves. The reflections change, so the CSI changes. **Motion = a change in the CSI
pattern over time.** No camera, no PIR sensor — just the Wi-Fi that is already there.

> Analogy: think of your hand passing in front of a lamp. You never look at the hand
> directly — you just see the shadow move on the wall. CSI is the "shadow" the moving
> body casts on the Wi-Fi signal.

## The pipeline

1. The ESP32 stays connected to your Wi-Fi access point (your box/router).
2. For each received frame, the ESP32 firmware extracts the raw CSI (per-subcarrier
   amplitude/phase).
3. ESPectre computes how much the CSI deviates from a learned **baseline** (the "quiet
   room" fingerprint captured at boot).
4. Deviation above a threshold → **motion detected**; back to baseline → no motion.
5. Adding `espectre:` auto-creates **two** sensors (plus controls):
   - `motion_sensor` — **binary** (motion / no motion), the thresholded state from step 4.
   - `movement_sensor` — a **0–10 movement-intensity score** (a moving-variance metric in
     MVS mode, or a 0–10 confidence-like score in ML mode).
   - a `threshold` number and a `calibrate` switch to tune/recalibrate at runtime.

The score is the more useful signal while experimenting: you watch it rise and fall to
tune the threshold, rather than seeing only the ON/OFF flip.

## Calibration

At boot the component needs a stable reference. For ~10 seconds after power-on, **keep
the room still** so the baseline represents an empty/quiet space. A bad baseline (someone
walking during calibration) makes detection unreliable until you recalibrate — either by
toggling the `calibrate` switch at runtime (no reboot) or by rebooting with a still room.

## What it can and cannot do

It can:

- Detect that *something* moved in the monitored space, in real time.
- Work through some obstacles where line-of-sight cameras/PIR fail.
- Keep all processing on-device (no cloud, no images).

It cannot:

- **Count people** — neither the binary state nor the 0–10 score is a headcount; the
  score reflects movement *intensity*, not how many bodies moved.
- **Identify** who moved.
- Avoid false positives from non-human movement.

## Why false positives are unavoidable

The radio environment changes for many reasons beyond a human walking:

- Pets, a robot vacuum, blinds/curtains moving.
- A neighbour's network saturating the 2.4 GHz band.
- Furniture moved, doors opened, even weather/humidity shifts over long periods.

Expect to tune the threshold and accept that this is a *presence hint*, not a precise
occupancy sensor.
