# Axonity Repo Refactor Guide

**How to use this file:** hand this file, plus `ENGINEERING_STANDARDS.md` and the rest of this `_project-template/` directory, to an AI coding agent along with a target repo. The agent should read both files, then execute the phases below in order against the target repo. `ENGINEERING_STANDARDS.md` explains *why* each item exists — read it first if a step below seems arbitrary. This file is the *what to do*, written to be followed exactly, safely, and idempotently (safe to re-run against a repo that's already partially or fully compliant — every step below checks before writing).

**Two ways this gets used:**
1. **Bootstrapping a brand-new project** — click "Use this template" on `Axonity-AI/project-template` on GitHub (or `gh repo create <new-name> --template Axonity-AI/project-template`), clone it, then run this guide. GitHub's template mechanism copies files as-is — it does **not** substitute placeholders — so the new repo will still have literal `{{PROJECT_NAME}}`/`{{PACKAGE_NAME}}`/`{{YEAR}}` tokens and a `src/__package_name__/` folder. Resolving those is the first thing Phase 0 covers below.
2. **Retrofitting an existing repo** to the standard — run this guide against a repo that already has real code and its own structure. Phase 0's "what already exists" check is what keeps this safe (never blindly overwrite real content).

---

## Hard-stop safety rules (read before doing anything)

These are non-negotiable, regardless of what phase you're in or how obviously "small" an action seems. If any of these come up, **stop and ask the human**, in plain language, before proceeding:

1. **Never commit a `.env` file or anything that looks like a real credential** (API key, password, token, private key). If you find one already committed in the target repo — in the current tree *or* in git history — stop immediately and report it; do not proceed with the rest of this guide until it's been triaged. See `docs/postmortems/0001-secret-leak-2026-08-06.md` for why this is rule #1.
2. **Never force-push or rewrite git history** (`git filter-repo`, `git rebase` on shared history, `git push --force`) without explicit human confirmation of exactly what will be rewritten and why.
3. **Never change a repository's visibility** (private → public or vice versa) without explicit human confirmation.
4. **Never merge a long-diverged branch by guessing at conflict resolutions.** If two branches have diverged enough that a merge produces real content conflicts (not just whitespace/line-ending noise), stop and report the conflicting files instead of resolving them unilaterally — especially for binary files or files neither side clearly "wins."
5. **Never delete files whose purpose is unclear** without flagging them first. If something looks like it might be intentional (a data file, a config override, an undocumented script), report it rather than silently removing it.
6. **Always end with a change report** (see Phase 5) — never leave the human to discover what changed by reading a diff cold.

If nothing above is triggered, proceed through the phases.

---

## Phase 0: Detect current state

Before writing anything, establish:

1. **Is this already a git repo?** (`git rev-parse --is-inside-work-tree`). If not, note this — some steps (git history checks) don't apply yet.
2. **Language/stack**: look for `requirements.txt`/`pyproject.toml`/`setup.py` (Python), `package.json` (Node/TypeScript), or both (a Python backend + JS frontend, like `axonity_chatbot`). Branch the rest of this guide accordingly — the governance files (CODEOWNERS, SECURITY.md, etc.) are language-agnostic and apply as-is; the lint/format/test tooling steps differ by language (see Phase 2, step 6).
3. **What already exists?** For every file this guide would create, check first — never blindly overwrite. Rule of thumb: if it exists and looks intentional (non-empty, plausible content), leave it and note the conflict in the final report instead of overwriting. If it exists but is clearly a stub/placeholder, it's safe to replace.
4. **Existing package/project name**: if `src/<something>/` or a `package.json` `"name"` field already exists, use that as `{{PACKAGE_NAME}}` instead of asking — don't rename an established package.
5. **Fresh-from-template check**: if `src/__package_name__/` still exists literally, or any file still contains `{{PROJECT_NAME}}`/`{{PACKAGE_NAME}}`/`{{YEAR}}`, this is an unbootstrapped template copy (see "Two ways this gets used" above). Ask the human for the project name if it's not obvious from context, derive `package_name` as its snake_case form, then: rename `src/__package_name__/` to `src/<package_name>/`, and find-and-replace every `{{PROJECT_NAME}}` / `{{PACKAGE_NAME}}` / `{{YEAR}}` token across every file that still has one — check `docker/compose.yml`, `README.md`, `pyproject.toml`, and `LICENSE` at minimum (`.github/workflows/ci.yml` and `.github/branch-protection-ruleset.json` deliberately don't use tokens — see the comment in `ci.yml`'s `docker` job for why). Do this before anything else in Phase 2. **If adding a new placeholder token to any `.yml`/`.yaml`/`.json` file, always quote it** (`"{{TOKEN}}"`) — an unquoted `{{...}}` at the start of a YAML value is parsed as a flow-mapping, not a literal string, and breaks the whole file (this exact bug shipped once and broke the template's own CI — see the git history of `ci.yml` and `docker/compose.yml`).

---

## Phase 1: Target layout

```
README.md
LICENSE
CODEOWNERS
SECURITY.md
CONTRIBUTING.md
.gitignore
.editorconfig
.pre-commit-config.yaml
pyproject.toml                 # Python projects — consolidates ruff/pytest config
requirements.txt                # or package.json for Node projects
src/<package_name>/...          # production code
tests/...                       # pytest discovery, or the JS equivalent
docs/
  architecture.md
  run_instructions.md
  adr/0000-template.md
  postmortems/                  # created empty; populated only when there's an actual incident
frontend/                       # if a frontend exists, keep it as its own top-level dir, unchanged in place
scripts/setup.sh                # one-time onboarding: installs deps + activates pre-commit hooks
scripts/run_local.sh
docker/Dockerfile
docker/compose.yml
.github/
  workflows/ci.yml
  ISSUE_TEMPLATE/bug_report.md
  ISSUE_TEMPLATE/feature_request.md
  PULL_REQUEST_TEMPLATE.md
  dependabot.yml
  branch-protection-ruleset.json
```

## Phase 2: File-by-file instructions

Work through these in order. For every file, the rule is the same: **if it already exists and has real content, don't overwrite — note it in the final report as "already present, left as-is" or "already present, content differs from template — flagged for human review" if the existing version looks meaningfully different from what's described here.**

1. **`LICENSE`** — if absent, copy from this template (`{{PACKAGE_NAME}}` → repo name in snake_case, `{{YEAR}}` → current year). Default is proprietary/all-rights-reserved (`Axonity Solutions Inc.`) — this is a closed-source company repo unless a human explicitly says otherwise.
2. **`CODEOWNERS`** — if absent, copy from this template. If the target repo already has committers other than the default owner, ask who should own what before defaulting everything to one person.
3. **`SECURITY.md`, `CONTRIBUTING.md`** — if absent, copy from this template, substituting `{{PROJECT_NAME}}`. If the repo already has good versions of these (as `axonity_chatbot` does), leave them — don't replace a specific, real policy with a generic template.
4. **`.github/ISSUE_TEMPLATE/*.md`, `.github/PULL_REQUEST_TEMPLATE.md`** — copy if absent.
5. **`.github/dependabot.yml`** — copy if absent. Drop any `package-ecosystem` blocks for ecosystems that plainly don't apply (e.g. remove the `npm` block if there's no `package.json` anywhere and never will be) — don't leave dead config, but don't guess either; a Python-only repo still might grow a frontend later, so when in doubt, leave the block (Dependabot silently finds nothing rather than erroring).
6. **Lint/format/type-check tooling** — this is the one place the guide branches by language:
   - **Python**: copy `pyproject.toml` (ruff + pytest config) if no equivalent config exists. If the repo currently uses flake8+black+isort with its own config, **do not silently replace it** — that's a tool migration, not a scaffolding gap, and deserves its own reviewed PR. Note it in the final report as a recommended follow-up instead.
   - **Node/TypeScript**: ensure `eslint` and `typescript` are actual installed devDependencies (not just an npm script referencing a binary that isn't installed — check `package.json`'s `devDependencies`, don't just check that a `"lint"` script string exists). If eslint config is missing or based on a stale preset (e.g. `react-app` after a Vite migration), flag it for follow-up rather than inventing a new config blind — a wrong eslint config generates false-positive noise that trains people to ignore lint output entirely, which is worse than no linter.
7. **`.editorconfig`** — copy if absent.
8. **`.pre-commit-config.yaml`** — copy if absent, adjusted for the detected language (drop the `ruff` hook block for a pure-Node repo; add an eslint/prettier pre-commit mirror hook instead if appropriate). **Add the config file only — do not run `pre-commit install` or `pre-commit run --all-files` against existing code without asking first.** A first-run formatting pass across a real codebase produces a large diff that deserves a dedicated, reviewed commit, not something bundled silently into a scaffolding pass. Also add `scripts/setup.sh` if absent — pre-commit only runs for people who've locally opted in (`.git/hooks/` isn't part of what git clones, by design), so folding hook installation into the one setup command everyone already runs is what makes adoption actually happen instead of relying on people remembering a separate step. The CI `secrets` job (next step) is the real, non-bypassable backstop for whoever skips this anyway.
9. **`docs/`** — ensure `architecture.md`, `run_instructions.md`, `adr/0000-template.md` exist (copy template versions if absent; don't overwrite real content). Create `docs/postmortems/` as an empty directory (with a `.gitkeep`) if it doesn't exist — don't fabricate a postmortem for an incident that didn't happen in this repo.
10. **`.github/workflows/ci.yml`** — if absent, copy the template version, adjusted for the detected language/stack (see `axonity_chatbot`'s CI for the pattern of separate jobs per concern, real service containers for integration tests, honest comments for anything deliberately out of scope). Make sure a `secrets` job running gitleaks exists even if the rest of the workflow is left alone — it's the CI-side backstop for anyone who skipped `scripts/setup.sh`'s pre-commit install, and it's cheap/low-risk to add on its own even to an existing workflow you're otherwise not touching. Use the raw `gitleaks detect` CLI (downloaded directly), not the `gitleaks/gitleaks-action` marketplace Action — it now requires a paid license for organization repos. If a CI workflow already exists, **do not replace it wholesale** — instead, diff it against the standard (see checklist below) and report gaps: is `lint`/`test` actually gating merges, or does something have `continue-on-error: true` on a check that's supposed to mean something?

    **Important:** `gitleaks detect` scans the repo's *entire* git history by default, unlike the pre-commit hook (`gitleaks protect --staged`, which only checks what's being committed right now). The first time this runs against a repo with real history, it commonly surfaces old false positives (doc examples, test fixtures) alongside anything real — triage every finding individually, don't assume they're all noise and don't assume they're all real. For confirmed-safe ones, record them with `gitleaks detect --report-path .gitleaks-baseline.json` and pass `--baseline-path .gitleaks-baseline.json` in CI so they stop being re-flagged while anything new still fails the build. Never baseline something without actually confirming it's safe first — see `axonity_chatbot`'s `.gitleaks-baseline.json` and its commit message for a worked example of what reviewed triage looks like.
11. **`.github/branch-protection-ruleset.json`** — copy if absent. This is prepared, not applied — applying it (`gh api --method POST repos/{owner}/{repo}/rulesets --input .github/branch-protection-ruleset.json`) requires the repo to support branch protection (public repos: yes today; private repos: requires GitHub Team or higher — check via `gh api repos/{owner}/{repo}/rulesets` first; a 403 mentioning "Upgrade to GitHub Pro" means it's plan-gated, not a bug in this guide). Applying it is a repo-configuration change — confirm with the human before running the apply command, even though the JSON itself is safe to add to the repo.
12. **GitHub repo security settings** (`secret_scanning`, `secret_scanning_push_protection`, `dependabot_security_updates`, vulnerability alerts) — these are GitHub API/Settings changes, not files. Check current state via `gh api repos/{owner}/{repo} --jq .security_and_analysis` and `gh api repos/{owner}/{repo}/vulnerability-alerts`. Enabling secret scanning + push protection is free on public repos and safe to just do; on private repos it may 404/422 if plan-gated — report rather than treating as an error. Enabling vulnerability alerts is free on any visibility — attempt it (`gh api --method PUT repos/{owner}/{repo}/vulnerability-alerts`) and report the result either way.

## Phase 3: Verify

1. Run the test suite. It should pass (or fail for pre-existing reasons unrelated to this guide's changes — don't mask an existing failure, but don't block on fixing unrelated pre-existing bugs either; report them).
2. Run the lint/format check the same way CI would. Report pass/fail — don't silently fix real lint errors in unrelated code as a side effect of this pass; that's scope creep into someone else's diff.
3. Confirm `git status` shows only the files this guide actually intended to add/change — nothing unexpected got swept in (e.g. don't accidentally stage a `.env` that was untracked for a reason).

## Phase 4: Commit

- Conventional Commits format: `chore(structure): apply Axonity standard repo layout` as the primary commit (split into more if the changes are large enough that one atomic commit would be hard to review — use judgment).
- Do not push without the human's go-ahead if this is the first time this guide has run against a repo they haven't seen the diff for yet.

## Phase 5: Report

Always end with a compact report, formatted as a checklist — present/absent/flagged, one line per item, not prose:

```
LICENSE               [added | already present | flagged: <reason>]
CODEOWNERS             [added | already present]
SECURITY.md            [added | already present, left as-is | flagged: <reason>]
CONTRIBUTING.md        [added | already present, left as-is | flagged: <reason>]
Issue/PR templates     [added | already present]
dependabot.yml         [added | already present]
.editorconfig          [added | already present]
scripts/setup.sh       [added | already present]
.pre-commit-config.yaml[added (not installed/run) | already present]
Lint/format config     [added | already present | flagged: migration recommended]
docs/ (architecture, run_instructions, adr, postmortems/) [added | already present]
CI workflow            [added | already present | flagged: non-blocking checks found]
branch-protection-ruleset.json [added | already present | applied | blocked: <reason>]
Repo security settings [checked — secret_scanning: X, push_protection: X, vuln_alerts: X]
```

Plus a short freeform section: any files moved, any conflicts flagged, any TODOs left for the human, and any of the hard-stop safety rules that were triggered during the run.
