# Privacy & RGPD

## Local-first by design

ESPectre processes CSI on the ESP32 itself and exposes a binary motion state **and** a
0–10 movement-intensity score (the `movement_sensor`). There is no image, no audio, and no
raw data leaving the device unless you explicitly forward it (e.g. to Home Assistant on
your own LAN). Keeping everything local is the privacy advantage of this approach over
cameras.

Note that the continuous 0–10 score is **more revealing than the binary state**: logged
over time it can hint at activity patterns (when a room is busy or quiet). Treat it as the
more sensitive of the two outputs.

## Where RGPD still applies

The same technology can track the movements of identifiable people. Under the GDPR
(RGPD), monitoring people's presence/movements can be personal-data processing. Even for
a home lab, apply these principles:

- **Consent / transparency.** Do not monitor people (guests, flatmates, family in private
  spaces) without informing them. Covertly tracking someone via a tampered router is both
  unethical and unlawful.
- **Purpose limitation.** Use it for the stated purpose (e.g. turn on a light), not for
  silently profiling someone's daily routine.
- **Data minimisation.** Keep only what you need. If the binary state is enough, set
  `internal: true` on `movement_sensor` so the 0–10 score is computed but not exposed;
  do not log long-term movement histories of identifiable people without a clear, lawful
  reason.
- **Scope.** Monitor your own space. Do not point it at, or infer activity in, a
  neighbour's home.

## This repo

This is a personal learning lab on the author's own hardware and space. No third-party
personal data is collected, stored, or published. If that ever changes, revisit this
document and the lawful basis first.
