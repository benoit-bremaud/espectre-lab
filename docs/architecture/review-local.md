# Local review — espectre-lab (branch feat/6-experiment-capture-tooling)

- Date: 2026-10-23
- Commit: 18a9bd0 (reviewed) → fixes applied in the follow-up commit on the same branch
- Scope: branch diff main...HEAD (19 files: experiments/tools, tests, CI, UML, docs)
- Checks run: design · docs · tests · security · correctness
- Verdict at review time: fix Must Have first · Must 3 · Should 6 · Nice 7
- **Resolution (same day): all 3 Must and 6 Should applied; 7 Nice filed as issue #8.**

## Pre-merge gate (after fixes)
| Step | Result |
|---|---|
| 1 Tests | ✅ 29 unit (pytest) · ✅ smoke: real 20 s capture via the Pi + 4 failure paths (rerun refused, ssh denied 255, unreachable host 7, bad slug 2) · no E2E suite in this repo |
| 2 Coverage | tests **94 %** stmts (floor 80) · docs: every public function/class in `experiments/tools/` now carries a contract docstring (floor 90) ✅ |
| 3 SonarQube | ⚠️ **waived for this PR** — no SonarQube project exists for the repo; owner decision 2026-10-23 (MCDA A 360 / B 360 tie, B chosen on one-task-per-chat): set up in its own brick, issue #7 |
| 4 Secrets | ✅ gitleaks clean (main..HEAD and full tree) · no tracked .env · diff read: no secrets; private LAN details only (see Nice / #8) |
| 5 QA pass | ✅ CLI product: `capture.sh` → CSV → `analyze.py` on the live module; transcript `docs/architecture/qa/2026-10-23-capture-smoke.txt` |
- Gate: **GREEN with SonarQube waiver (#7) — merge authorised**

Findings below are as reported at review time (commit 18a9bd0); Must and Should are resolved.

## 🔴 Must Have
- `experiments/tools/analyze.py:100,129,138,187` + `sse_to_csv.py:40` `[docs]` · doc coverage ≈40 % < 90 %: `score_stats`, `confusion`, `render_markdown`, both `main`, `read_marks` lack contract docstrings (ValueError on empty, positive = moving, `<stem>.marks.csv` auto-discovery, exit code 1) · add the five docstrings proposed by the doc audit.
- `experiments/0002-reconnect-baseline-3min.md:31-32,71-72,88` `[docs]` · journal says "ordinary daytime activity elsewhere in the home"; the owner confirmed the house was empty during the run (PROJECT_LOG is right) · fix the procedure, false-positive cause list and "Next" wording; the 0.406 spike becomes a confirmed noise-floor false positive.
- `docs/architecture/diagrams/experiment-capture/01-data-flow.md:28,41-42,50` + `02-sequence-run.md:16,35` `[docs][design]` · UML drift vs code: node says "pandas" (stdlib), filtering attributed to `capture.sh` (done by `sse_to_csv.py`, missing node), column `entity_id` (is `entity`), "precision/recall per threshold" (one threshold per run), SSH hop absent from the sequence · update both diagrams (UML is the contract).

## 🟡 Should Have
- `experiments/tools/sse_to_csv.py:29-35` `[correctness][security][design]` · fragile row emission: f-string instead of `csv.writer` (comma in a value corrupts the file), `KeyError` on missing `id`/`value`, crash on truncated JSON when `--max-time` cuts mid-line, `null` written as `None` then `_as_float` dies in `analyze.py`, `rstrip("\n")` breaks CRLF blank-line reset · use `csv.writer`, skip malformed/null payloads with a stderr warning, `rstrip("\r\n")`; add CRLF/truncated/null tests.
- `experiments/tools/capture.sh:28-45` `[correctness]` · silent failures: only `PIPESTATUS[0]` checked (a `sse_to_csv.py` crash passes), curl exit 28 also covers connect timeout so an unreachable host yields "Done: 0 rows" exit 0, HTTP errors pass without `-f`, same-day same-slug rerun overwrites the CSV · check `PIPESTATUS[1]`, add `-f --connect-timeout 5`, fail on 0 rows, refuse to overwrite.
- `experiments/tools/capture.sh:18-28` + `mark.sh:17` `[security][correctness]` · unvalidated arguments: HOST/DURATION are re-parsed by the remote shell via ssh (injection if the owner mistypes), SLUG goes into a path (`../`), SSH_HOST starting with `-` is read as an ssh option · regex-validate host/duration/slug, `ssh -- "$ssh_host"`.
- `tests/test_analyze.py:35` + gaps `[tests]` · p99 assertion `0.3 <= p99 <= 0.4` is too loose (exact 0.397); untested: single-sample p99, no-marks path, empty motion list, non-default `--threshold`, `_as_float` variants (`ON`, ` off `), mixed timezone offsets · tighten and add ~6 small tests.
- `experiments/tools/sse_to_csv.py:16` + `docs/privacy.md`, `01-data-flow.md:48`, `experiments/README.md:29` `[docs]` · `CSV_HEADER` is dead (header hardcoded in `capture.sh:30`); docs say CSV holds "only score and motion state" but every `state` event is recorded (threshold, calibrate rows present) · drop the constant or use it from the script; word the docs as "entities exposed by the web server, never raw CSI".
- `experiments/tools/analyze.py:131-134` `[design]` · `confusion` builds dict keys from string fragments (`"t"/"f" + "p"/"n"`): too clever, typo → runtime KeyError · four explicit counters.

## 🔵 Nice to Have
- `analyze.py:85-97` `[design][correctness]` · `label_samples` is O(samples × marks) and silently treats a mistyped label as still · `bisect` + warn on unknown labels.
- `analyze.py:148` `[design][docs]` · magic `>= 1` for device ON · `MOTION_ON = 1.0` constant with a one-line WHY.
- `analyze.py:234` `[correctness]` · `__doc__.splitlines()[0]` crashes under `python -OO` · `description=__doc__` with `RawDescriptionHelpFormatter`.
- `mark.sh:33` `[correctness]` · `date +%3N%:z` is GNU-only · comment it (Linux/Pi only) or use a python one-liner.
- `requirements-dev.txt`, `.github/workflows/python.yml` `[security][correctness]` · open `>=` pins drift; no `timeout-minutes`; local venv is 3.14 vs CI 3.12 · pin or add Dependabot `pip` + `github-actions`; add `timeout-minutes: 10`.
- `experiments/README.md:9-10,21-26`, `.claude/CLAUDE.md` § Architecture `[docs]` · example slug `0002-...` collides with the real 0002 (use 0003); paths in the README are relative to `experiments/` (say so); Architecture section does not list `experiments/tools/`, `experiments/data/`, `tests/`.
- `0002.md`, `experiments/README.md`, `PROJECT_LOG.md`, `.claude/CLAUDE.md`, `capture.sh:10` `[security]` · public repo exposes home-LAN recon details (`192.168.1.123`, subnets, `benoit@bb-homelab`) · optional: placeholders (`<module-ip>`, `user@homelab`). Owner's call; RFC 1918 addresses are not reachable from the internet.

## ⚪ Disagree / Intentional
- `analyze.py` stdlib `csv`/`statistics` instead of pandas `[design]` · deliberate (CLAUDE.md "stdlib only until a real need", PROJECT_LOG 2026-10-23).
- `tests/` at repo root with `pythonpath = ["experiments/tools"]`, no package `[design]` · scripts, not a library (`pyproject.toml` comment).
- Shell scripts without unit tests `[tests]` · shellcheck + live smoke run (QA transcript) are the proportionate check for ~80 lines of bash.
- Frozen dataclasses without docstrings `[docs]` · self-evident data carriers.

## Per-dimension summary
- Design: proportionate, no over-engineering; UML drift and one too-clever expression · Docs: 4 freshness defects + 6 missing contract docstrings (coverage ≈40 %) · Tests: healthy pyramid, no over-mocking; p99 assertion loose, ~6 edge cases missing · Security: nothing Must; argument validation and CSV-writer hardening; CI pinned and least-privilege · Correctness: no Must; `capture.sh` can report success on an unreachable host, `sse_to_csv.py` dies on truncated/null payloads.
