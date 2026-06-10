# Setup with ESPHome

## What ESPHome is

ESPHome turns a microcontroller (ESP32) into a configurable device from a single YAML
file: it compiles the YAML into firmware, flashes it, and handles Wi-Fi, OTA updates,
logging and a web server for you. ESPectre is added as an **external component** that
ESPHome pulls from GitHub and bakes into the firmware.

ESPHome does **not** require Home Assistant. With the `web_server` component you can read
the motion state straight from a browser. Home Assistant is optional and can be added
later for automations.

## Prerequisites

- One supported board (see [hardware.md](hardware.md)).
- ESPHome installed. Easiest: `pipx install esphome` (or the official Docker image / the
  Home Assistant ESPHome add-on if you already run HA).
- A USB cable for the first flash (afterwards you can use OTA).

## Steps

1. **Secrets.** Copy the example and fill in your Wi-Fi:

   ```bash
   cp esphome/secrets.yaml.example esphome/secrets.yaml
   # edit esphome/secrets.yaml  (gitignored — never committed)
   ```

2. **Validate** the configuration:

   ```bash
   esphome config esphome/espectre.yaml
   ```

3. **Flash** over USB (first time):

   ```bash
   esphome run esphome/espectre.yaml
   ```

4. **Calibrate.** Keep the room still for ~10 s after boot so the baseline is clean.

5. **Observe.** Watch logs and find the web server URL:

   ```bash
   esphome logs esphome/espectre.yaml
   ```

   Open the printed IP in a browser to see the motion binary sensor toggle.

## Standalone vs Home Assistant

- **Standalone (now):** the `web_server` component shows the sensor; good enough to learn
  and experiment.
- **Home Assistant (later):** with the native API enabled, the device auto-discovers in
  HA and the motion sensor becomes available for automations (lights, alerts, etc.).

## Tuning

- If you get too many false triggers, raise the detection threshold in the `espectre`
  config block (see the upstream README for the exact options) and re-flash via OTA.
- Re-calibrate (reboot with a still room) whenever you move the board or rearrange
  furniture significantly.
