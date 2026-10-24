# Local review — espectre-lab (branch feat/experiment-0003-threshold)

- Date: 2026-10-24
- Commit: 749aa64 (reviewed) → Should fixed in the follow-up commit on the same branch
- Scope: branch diff main...HEAD (7 files: experiment 0003 journal, experiments README,
  PROJECT_LOG, 4 data CSVs). Docs + data only, no code.
- Checks run: docs · correctness (journal numbers cross-checked against the CSVs with
  `tools/analyze.py`). Design, tests and security agents not run: no code in the diff.
- Verdict: ship as-is after the Should fix · Must 0 · Should 1 · Nice 2

The previous report (PR #9, 2026-10-23) is in git history.

## Pre-merge gate (head SHA 749aa64)

| Step | Result |
|---|---|
| 1 Tests | ✅ 29 pytest passed · ruff format/check clean · mypy strict clean |
| 2 Coverage | tests 94 % (floor 80) · docs n/a (no code changed) |
| 3 SonarQube | ✅ PASSED (local instance, project `espectre-lab`) |
| 4 Secrets | ✅ gitleaks clean on main..HEAD (3 commits) · no tracked .env · diff read: nothing new sensitive |
| 5 QA pass | n/a for a docs/data diff; the real artefact (`capture.sh` + `mark.sh` + `analyze.py`) ran 4 times on 2026-10-23/24 against the device |

- Gate: **GREEN — push authorised**

## 🔴 Must Have

_None._

## 🟡 Should Have

- `experiments/0003-threshold-from-data.md` `[docs][correctness]` · baseline run 2 sample
  count written "~600" (actual 615) and walk-through window "330 s" (actual 329 s) ·
  fixed in the follow-up commit.

## 🔵 Nice to Have

- `experiments/0003-threshold-from-data.md` `[security]` · home-LAN details (module IP,
  ssh host) in a public repo · already tracked in #8, no new exposure.
- `experiments/tools/mark.sh` `[correctness]` · single-key reads fail in the Claude desktop
  app's terminal pane (script exits after the first key) · documented in the journal; add
  to #8 (detect a non-interactive stdin and warn).

## ⚪ Disagree / Intentional

- Two failed walk-through runs not committed · their labels were lost or wrong, so they
  carry no ground truth; the journal explains why.

## Per-dimension summary

- Docs: journal complete, numbers match the CSVs after the fix · Correctness: precision/
  recall reframed as empty vs occupied, consistent with the data · Design / Tests /
  Security: no code changed.
