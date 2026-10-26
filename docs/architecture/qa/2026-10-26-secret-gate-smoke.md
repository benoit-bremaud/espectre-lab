# QA smoke - secret gate, capture tooling and test-plan docs (2026-10-26)

| Level | Head SHA | Environment | Targets | Agent / model |
|---|---|---|---|---|
| smoke | b4afd77 (branch `docs/32-test-plan-and-docs`) | local laptop + ESP32-C3 module reached through the homelab Pi (`<MODULE_IP>` via `<SSH_HOST>`) | L (CLI tooling), F (running firmware, read-only) | qa-tester, Sonnet (product part; security part not run) |

Plan: diff is docs and tooling only, so level `smoke`. Real addresses come from the
gitignored `experiments/lab.env`; this report uses placeholders only. The device is only
read (SSE stream), nothing is written to it.

## Results

| ID | Check | Verdict | Evidence |
|---|---|---|---|
| SM-1 | `capture.sh "$MODULE_IP" 20 qa-smoke-1627 "$SSH_HOST"` records rows | PASS | `Done: 25 rows` ; CSV has header `timestamp,entity,value`, motion and score rows, 25 data lines |
| SM-2 | `analyze.py <csv>` prints the stats table | PASS | window 19 s, 22 samples, min 0.062, median 0.091, max 0.121, 0 device episodes (consistent with reference run 0004, floor about 0.09-0.10) |
| SM-3 | `analyze.py <csv> --threshold 0.5` | PASS | table printed, threshold 0.5 |
| SM-4 | `capture.sh` refuses an existing slug | PASS | rerun with the same slug: message "already exists: pick another SLUG", exit 1, file untouched |
| SM-5 | `capture.sh` with no argument prints usage | PASS | usage header printed |
| SM-6 | `scripts/test-secret-gate.sh` | PASS | exit 0, 13 cases, none not `ok` (clean-doc, wifi-secret and new-branch cases included) |
| SM-7 | `pre-push` hook on this branch (new-branch push simulation) | PASS | exit 0; gitleaks: 3 commits scanned, no leaks found |
| SM-8 | Docs commands runnable (experiments/README.md, docs/test-plan.md) | PASS | see below |
| UI-02 | Console / network | N/A | no UI |
| SEC-* , ROB-11 | Security probes | NOT TESTED | security part not run |

SM-8 detail: with `lab.env` sourced, `experiments/tools/capture.sh <MODULE_IP> <seconds> <slug> <SSH_HOST>`
(test-plan, from repo root) works as written with `"$MODULE_IP"` / `"$SSH_HOST"`. README commands
(paths relative to `experiments/`) run as written: `tools/capture.sh` usage, `tools/mark.sh` present,
`python3 tools/analyze.py data/2026-10-23-baseline-empty-house.csv --threshold 0.4` prints a table.
`analyze.py` with `--threshold 0.4` and `0.5` on the smoke CSV works. Files referenced by the docs exist
(`0003`, `0004`, `requirements-dev.txt`, `lab.env.example`, `docs/architecture/diagrams/experiment-capture`).
`mark.sh` is interactive and was not exercised (needs a system terminal, as the docs say).

## Not covered

- `mark.sh` interactive keys; `mypy` and `pytest --cov` (not in the smoke scope; `mypy` is not on PATH in this
  environment, `pip install -r requirements-dev.txt` would provide it).
- Gate cases beyond the 13 shipped; a push of a branch with an existing remote SHA (only the new-branch path run).
- SEC and ROB-11 (security part).

## Findings

1. Nice - `capture.sh` prints its output path with a `tools/../data/` segment
   (`Recording ... -> <repo>/experiments/tools/../data/<date>-<slug>.csv`). Cosmetic; normalising
   `data_dir` (e.g. `cd ... && pwd`) would print a clean path. Not filed (per instruction).
2. Nice - the smoke CSV lands in `experiments/data/`, which is not gitignored, so a careless
   `git add experiments/data` would commit it. Left untracked on purpose:
   `experiments/data/2026-10-26-qa-smoke-1627.csv`. Not filed (per instruction).

No Must or Should finding.

## Delta vs previous report

Previous: `docs/architecture/qa/2026-10-23-capture-smoke.txt` (same smoke, same 25 rows, floor 0.13 then vs 0.09 now,
the lower value matches the quieter conditions documented in `0004`). Fixed 0, still failing 0, new 2 (Nice).
