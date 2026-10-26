# Local review — espectre-lab (branch docs/32-test-plan-and-docs)

- Date: 2026-10-26
- Commit: b4afd77 (reviewed) → Must + simple Should fixed in a6e7181 and e969d63
- Scope: branch diff origin/main...HEAD (experiments 0004/0005, test plan, LAN placeholders,
  pre-push secret gate: `.gitleaks.toml`, `scripts/hooks/pre-push`, `scripts/install-hooks.sh`,
  `scripts/test-secret-gate.sh`, `security.yml`)
- Checks run: design · docs · tests · security (Opus) · correctness · QA smoke
- Verdict: ship after the fixes (done) · Must 6 (fixed) · Should 9 (6 fixed) · Nice 7

The previous report (PR #15, 2026-10-24) is in git history.

## Pre-merge gate (head SHA e969d63)

| Step | Result |
|---|---|
| 1 Tests | ✅ 29 pytest · ✅ canary 26/26 · ruff, mypy strict, shellcheck clean · ESPHome config validated in CI only (esphome not installed locally) |
| 2 Coverage | tests 94 % (floor 80) · docs n/a (no Python API changed) |
| 3 SonarQube | ✅ PASSED (local instance, project `espectre-lab`) |
| 4 Secrets | ✅ gitleaks clean on origin/main..HEAD (5 commits) · no tracked .env · diff read: placeholders only |
| 5 QA pass | ✅ smoke (tooling/docs diff): capture + analyze, refuse-overwrite, canary, doc commands · report: docs/architecture/qa/2026-10-26-secret-gate-smoke.md |

- Gate: **GREEN — push authorised**

## 🔴 Must Have (all fixed)

- `scripts/hooks/pre-push:20-24` `[security]` · a remote sha unknown locally (not fetched, force-push elsewhere) made gitleaks scan nothing and exit 0: fail-open · `git cat-file -e` check, otherwise scan everything the remote lacks; canary `unknown-remote-sha`.
- `scripts/test-secret-gate.sh` missing-gitleaks `[tests, design]` · `PATH=/nonexistent` also removed git, so the case passed without reaching the gitleaks check · PATH holds only git, assert "gitleaks not found".
- `scripts/test-secret-gate.sh` block cases `[tests]` · any non-zero exit counted as "blocked" · assert the expected `RuleID` (needed `--verbose` in the hook, which also fixes its "see findings above" message that showed nothing).
- `scripts/test-secret-gate.sh` setup `[tests, correctness]` · user git config (signing, global hooksPath) could break or empty the throw-away repos · `GIT_CONFIG_GLOBAL=/dev/null`, setup failures exit 2.
- `.gitleaks.toml:7-11` `[security, design]` · global allowlist exempted the canary script (and the config) from every rule, defaults included · canary no longer exempt; config exempt from the custom rules only (`targetRules`).
- `docs/test-plan.md`, `experiments/README.md` `[docs]` · "HA broken" stale, suggested order stale, placeholders undefined · updated; placeholder glossary added.

## 🟡 Should Have

- ✅ `pre-push` `[correctness]` · gitleaks inherited the ref-list stdin (multi-ref push could skip refs) · `</dev/null`.
- ✅ `pre-push` `[security]` · `--not --remotes` skipped commits present on any remote · `--remotes=$1`.
- ✅ `.gitleaks.toml` `[security]` · gaps: uppercase e-mail/home, `/Users`, CGNAT/Tailscale, link-local, MAC, YAML `key:` · rules extended; canary near-miss cases (dotted versions, `github.com/users/…`, work e-mail) pass.
- ✅ `security.yml` `[security, design]` · tag-pinned third-party action with `GITHUB_TOKEN`, version drift between jobs · SHA pins, `persist-credentials: false`, timeouts, `GITLEAKS_VERSION: 8.30.1` (also required: `[[allowlists]]` needs ≥ 8.25), Dependabot github-actions.
- ✅ `.claude/CLAUDE.md`, `README.md` `[design, docs]` · nothing told a clone to run `install-hooks.sh`; HA "optional/future" stale · documented.
- ✅ `docs/setup-esphome.md`, `docs/how-it-works.md` `[docs]` · fan effect overclaimed · "fan and/or draught, not separated yet (A2/A3)".
- ⏳ `security.yml` `[correctness]` · a full-history scan would go red on the 33 pre-gate findings · only matters for a future scheduled/full scan; add a baseline then.
- ⏳ `scripts/test-secret-gate.sh` `[design]` · DRY · done partly (`new_repo`/`commit_file`/`expect` helpers).
- ⏳ CI Go toolchain for `go install` `[security]` · relies on the runner's Go; module checksum DB keeps the tag immutable · acceptable for now.

## 🔵 Nice to Have

- ✅ `pre-push` `gitleaks detect` deprecated → `gitleaks git`.
- ✅ `install-hooks.sh` dead `chmod`; mentions gitleaks requirement.
- ✅ `experiments/lab.env.example` placeholders quoted (sourceable).
- `install-hooks.sh` silently overwrites an existing `core.hooksPath`.
- `capture.sh` prints `tools/../data/` (normalise the path) · QA.
- Commit author e-mail is a personal address: switch to the GitHub noreply address.
- Bypasses by design: `--no-verify`, fresh clone without the hook; CI `gitleaks` job is the backstop.

## ⚪ Disagree / Intentional

- Public history keeps the pre-placeholder values (33 findings in a235990, 920e01c, 49f63ab, 4803ba5) · owner decision 2026-10-26 (option A): no rewrite, no force-push on main; low value outside the LAN.
- Gate scripts duplicated in `smart-ceiling-fan` · two copies, below the rule of three.
- The `<homelab>` hostname literal inside `.gitleaks.toml` · the rule needs it; already in public history.

## Per-dimension summary

- Design: flat, right-sized; one false-pass canary case. · Docs: HA status and placeholders stale, fixed. · Tests: canary gave false confidence (exit-code only, missing-gitleaks), now asserts rules. · Security: one fail-open (unknown remote sha), rule gaps, CI pinning, all fixed. · Correctness: experiment numbers match the CSVs; stdin and git-config isolation fixed.
