# Axonity Engineering Standards

What this is: the reference for how Axonity builds and ships software, written for a company going from solo-founder to a real team. Each section says what the practice is, why large, well-run engineering orgs (Google, Meta, Amazon, Netflix, and the mature-OSS world generally) rely on it, what mechanism implements it at Axonity, and how it's sized for where the company is today vs. after hiring.

The companion file, `REFACTOR_GUIDE.md`, is the executable checklist — hand that to an AI coding agent to bring a specific repo up to this bar. This file is the *why*, so decisions don't have to be re-litigated every time, and so a new hire can read one document and understand the engineering culture instead of reverse-engineering it from tribal knowledge.

**Sizing principle:** copying a big company's practices at the wrong scale is itself a mistake — nobody at 1-3 engineers needs Bazel, a monorepo, or a dedicated release-engineering team. What actually transfers regardless of headcount: the trunk stays releasable, nothing merges without CI passing, nothing ships without review (even self-review via PR), secrets never touch git, dependencies update themselves, and a new engineer is productive from the README alone. Everything below is filtered through that lens — each section says explicitly what's worth doing solo vs. what only starts paying off once there's a team.

---

## 1. Repo structure & polyrepo vs. monorepo

**Practice:** one GitHub repo per deployable project (`axonity_chatbot`, `visual_search_ranking`, each future project), plus one lightweight org-index repo (`Axonity-AI/.github`) that's just a README pointing at the others. Every project repo follows the same internal layout: `src/<package_name>/`, `tests/`, `docs/`, `scripts/`, `docker/`, `.github/`.

**Why FANG-adjacent:** Google/Meta use monorepos because they have custom build systems (Bazel/Buck) and thousands of engineers who need atomic cross-project commits. That trade-off doesn't exist at Axonity's scale — a monorepo here would mean paying the coordination cost (shared CI triggers, shared versioning, harder to give a contractor scoped access to one project) without the benefit (nobody's making atomic cross-repo commits yet). Polyrepo is standard for startups and small-to-mid engineering orgs for exactly this reason.

**Right-sized:** keep polyrepo. Revisit only if the company reaches a point where genuinely shared library code needs to be versioned and consumed by multiple projects simultaneously — at that point, a private package registry (PyPI-compatible or npm-compatible) for the shared library is the right next step, not a monorepo.

---

## 2. Branching strategy

**Practice:** trunk-based development. `main` is always releasable. Work happens on short-lived branches (`feat/<slug>`, `fix/<slug>`) branched from `main`, merged back via PR within days, not months. No long-lived parallel branches (`phase_2`, `phase_3`-style) that drift until merging them means resolving dozens of conflicts and rediscovering binary-file mistakes baked into history — exactly what happened in this org's `axonity_chatbot` history and cost real time to untangle.

**Why FANG-adjacent:** every major tech company converged on trunk-based development because long-lived branches are where integration pain compounds silently — the cost of merging is roughly quadratic in how long branches diverge. Feature flags (a boolean config check, not a branch) are the standard way to ship incomplete work to `main` safely.

**Right-sized:** even solo, name branches by intent and merge them within days. The discipline costs nothing extra and prevents exactly the divergence/large-file/history-rewrite mess this org already lived through once.

---

## 3. Code review & CODEOWNERS

**Practice:** nothing merges to `main` without going through a PR, even solo (self-review still forces you to read your own diff as a reviewer would, and creates a paper trail of what shipped and why). `CODEOWNERS` maps paths to the person responsible for reviewing changes there.

**Why FANG-adjacent:** review is the highest-leverage bug-catching mechanism that exists — cheaper than any test suite per bug caught, and it's how tacit knowledge about a codebase spreads instead of staying locked in one person's head. `CODEOWNERS` is what makes review *scale*: once there's a team, PRs touching `backend/auth/` auto-request the person who actually owns auth, instead of review becoming a bottleneck on whoever happens to be free.

**Right-sized:** solo, `CODEOWNERS` is just `* @your-username` — it costs nothing to add now and it's already correct once the first hire joins (add their username to the paths they own). Actually *requiring* review (branch protection) needs GitHub Team on private repos — see §11.

---

## 4. CI gating

**Practice:** every PR runs, at minimum: lint, type-check, tests (with an enforced coverage floor, not just a reported number), and a build/docker-build check. All of these **block merge on failure** — no `continue-on-error: true` on anything that's supposed to mean something. A check that can't fail the build isn't a check, it's decoration.

**Why FANG-adjacent:** CI-as-gate is how large orgs keep `main` shippable at every commit without relying on individual discipline. The moment a "required" check is allowed to fail silently, it stops being enforced within a release or two — this org's own audit found exactly that pattern (`visual_search_ranking`'s formatting/import-order checks both set to `continue-on-error: true`, so they've never actually blocked anything).

**Right-sized:** the CI structure here (`_project-template/.github/workflows/ci.yml`) mirrors `axonity_chatbot`'s real pattern — separate jobs per concern (don't make the frontend wait on backend test setup), real service containers for integration tests (Postgres/Redis via GitHub Actions `services:`, not mocks-only), and honest comments when something is deliberately out of scope for CI rather than silently skipped.

---

## 5. Secret management

**Practice:** secrets never touch git, full stop. `.env` is gitignored everywhere; `.env.example` (no real values) is the only committed variant. A pre-commit hook runs secret detection (gitleaks/detect-secrets) *before* a commit can be made — the earliest possible point to catch a mistake. This only works for people who've locally run `scripts/setup.sh` (git hooks aren't part of what gets cloned, by design — there's no way to force a local hook to run on someone's machine without them opting in once), so it's a convenience layer, not the enforcement boundary. The actual, non-bypassable enforcement is CI: a `secrets` job (gitleaks) running on GitHub's servers on every push/PR, plus GitHub secret scanning + push protection at the platform level — both run regardless of what's installed on any individual's laptop. **If a secret is ever committed, treat it as compromised the moment it's pushed — rotate it — even if removed in a later commit or the repo was private.** History retains everything until deliberately scrubbed, and scrubbing doesn't undo exposure that already happened.

**Why this is here at all:** this is not theoretical. On 2026-08-06, a real Anthropic API key and OpenAI API key (committed in `portfolio_projects`' very first commit, years earlier) were exposed for a period when that repo was made public, because none of the mechanisms in this section existed yet. See `docs/postmortems/0001-secret-leak-2026-08-06.md` for the full incident writeup — corrective actions from that incident are what populated this section.

**Right-sized:** this one has no "right-sized down" — a leaked production API key costs the same real money and the same real risk whether the company has 1 employee or 1,000. Adopt the pre-commit hook and push protection on every repo immediately, no exceptions.

**Two implementation gotchas worth knowing up front** (both hit while rolling this out across Axonity's repos):
- Use the raw `gitleaks` CLI in CI (`gitleaks detect`, downloaded directly), not the `gitleaks/gitleaks-action` marketplace Action — it now requires a paid license for organization-owned repos, a maintainer-side change unrelated to anything in this repo.
- `gitleaks detect` scans the repo's *entire* git history by default, unlike the pre-commit hook (`gitleaks protect --staged`, which only checks what's being committed right now). The first time CI-side scanning runs against a repo with real history, it commonly surfaces old false positives (doc examples, test fixtures) — and occasionally something real-but-dead (`axonity_chatbot`'s CI turn-on found an expired JWT from a `Bash(TOKEN="...")` command that Claude Code had auto-saved into `.claude/settings.local.json`, months earlier — harmless since already expired, but still shouldn't have been tracked). Triage every finding individually, then record confirmed-safe ones in a `.gitleaks-baseline.json` (`gitleaks detect --report-path .gitleaks-baseline.json`) so CI stops re-flagging them via `--baseline-path` while anything new still fails the build. Never baseline something without actually confirming it's safe first.

---

## 6. Dependency management

**Practice:** Dependabot (`.github/dependabot.yml`) opens automated PRs for version bumps and security patches on a weekly cadence, per ecosystem (pip, npm, docker, github-actions). Dependency versions are pinned in a lockfile (`requirements.txt` with exact pins, or `package-lock.json`/`poetry.lock`), not loose ranges — a build should be reproducible byte-for-byte from the lockfile, not "whatever the latest compatible version happened to be today." Vulnerability alerts are enabled on every repo regardless of visibility (this is a free GitHub feature, not gated behind a paid plan).

**Why FANG-adjacent:** unpatched dependencies are one of the most common real-world breach vectors (see: Log4Shell, every major supply-chain CVE of the last five years). Automating the update PR removes the excuse of "nobody had time to check" — a human still reviews and merges, but the discovery and PR-drafting work is free.

**Right-sized:** turn this on everywhere now — it's zero-maintenance once configured and the earlier it's on, the smaller each individual update PR stays (dependencies that drift for a year produce one enormous, risky update instead of fifty small, safe ones).

---

## 7. Commit conventions

**Practice:** [Conventional Commits](https://www.conventionalcommits.org/) — `feat:`, `fix:`, `chore:`, `docs:`, `refactor:`, `test:`, `ci:`, with an optional scope (`feat(frontend): ...`). Enforced via a commit-msg pre-commit hook, not just convention-by-memory.

**Why FANG-adjacent:** the payoff isn't the format itself, it's what it *unlocks*: a `CHANGELOG.md` and a semantic version bump (`fix:` → patch, `feat:` → minor, `BREAKING CHANGE:` footer → major) can both be generated automatically from commit history (via `release-please` or `semantic-release`), instead of someone manually reconstructing "what shipped since last release" from memory.

**Right-sized:** adopt now, before habits set and before there's a second contributor to onboard onto a convention retroactively. `axonity_chatbot`'s `phase_3` history already shows partial, inconsistent adoption (`feat(frontend): ...` mixed with freeform messages) — the hook is what makes it consistent instead of best-effort.

---

## 8. Testing

**Practice:** unit tests are the base of the pyramid (fast, most numerous), integration tests next (real service containers, fewer), e2e/performance tests at the top (slowest, fewest, often excluded from per-commit CI and run on a schedule instead). Coverage is *measured and gated* — a declared threshold (e.g. `--cov-fail-under=85`) that actually fails the build if unmet, not a number reported to a dashboard nobody looks at.

**Why FANG-adjacent:** the shape matters more than the total count — a codebase with 1000 slow e2e tests and no unit tests is slower to develop against and just as prone to gaps as one with no tests at all. `axonity_chatbot`'s `pytest.ini` already declares the right shape (unit/integration/api/security/performance markers, `--cov-fail-under=85`) — the gap the audit found is that nothing in CI was actually running it, so the gate existed on paper only.

**Right-sized:** the marker taxonomy and coverage-gate pattern from `axonity_chatbot` is the template default. Don't chase 100% coverage — target it on critical paths (auth, payments, data mutation) and accept lower coverage on glue code.

---

## 9. Documentation as code

**Practice:** `README.md` is the front door (Overview, Quickstart, Run tests, Deploy notes, Contacts — sections a stranger needs in the first five minutes). `docs/` holds anything longer-lived: architecture, deployment, development workflow, testing strategy. `docs/adr/` holds Architecture Decision Records — one short markdown file per significant technical decision (what was decided, what alternatives were considered, why this one), so six months later nobody has to reverse-engineer *why* the RAG store is pgvector instead of Pinecone. Docs live in the same repo and the same PR as the code they describe, reviewed the same way.

**Why FANG-adjacent:** documentation that lives outside the repo (a wiki, a Google Doc) reliably rots because it's not in the path of the PR that invalidates it. ADRs specifically are a lightweight practice borrowed from the OSS/big-company world precisely because "why did we do it this way" is the question new hires ask most and existing engineers answer worst from memory.

**Right-sized:** `axonity_chatbot`'s `docs/` structure (`ARCHITECTURE.md`, `DEVELOPMENT.md`, `TESTING_GUIDE.md`, `DEPLOYMENT_GUIDE.md`, a `project-management/` subfolder for task tracking) is a good template-sized version of this — comprehensive without needing a dedicated docs team.

---

## 10. Release process & versioning

**Practice:** [Semantic Versioning](https://semver.org/) (`MAJOR.MINOR.PATCH`), an actual `CHANGELOG.md` (Keep a Changelog format), and GitHub Releases cut from tags — not "just push to `main` and call it deployed." Once Conventional Commits (§7) is adopted, this can be substantially automated via `release-please` or `semantic-release`.

**Why FANG-adjacent:** without versioning, "what changed between what's in production and what's in `main`" is an unanswerable question except by reading raw commit history. A tagged release is a fixed, citable point — essential the moment there's more than one deployment target (staging vs. prod) or more than one person who needs to know what shipped.

**Right-sized:** none of Axonity's repos have ever cut a release or tag (confirmed via audit). Worth starting even solo — the first tag is free, and it establishes the habit before it's needed for an actual production incident rollback.

---

## 11. Org-level security posture

**Practice:** require 2FA for all organization members (GitHub org setting, currently **off** for `Axonity-AI`). Enable secret scanning + push protection on every repo — free on public repos, requires GitHub Advanced Security (Team or Enterprise plan) on private ones. Default repo permission stays `read` (already correctly configured), and repo-creation rights should tighten once there are multiple members who shouldn't all be able to spin up new company repos unsupervised.

**Why FANG-adjacent:** org-level settings are the floor everything else stands on — a perfectly-configured repo doesn't help if an org member's un-2FA'd account gets phished. This is also the cheapest security investment available: it's a checkbox, not an engineering project.

**Current state (2026-08-08):** all three repos (`.github`, `axonity_chatbot`, `visual_search_ranking`) are now public, with secret scanning + push protection + Dependabot security updates enabled on each. That unlocked branch protection for free too (GitHub Rulesets, `.github/branch-protection-ruleset.json` in each repo, ready to apply) — deliberately not yet applied, since turning it on immediately requires every future change, including the founder's own, to go through a PR with a passing CI check before merging to `main`. Apply it when ready for that workflow shift, not before. Org-wide 2FA requirement is still off — that one's a GitHub Settings action best done by a human, not an API call made on your behalf, since GitHub's own UI warns about members who'd be locked out before you commit to it, which an API call wouldn't.

**Right-sized:** if any future project repo needs to stay *private* (client work under NDA, unreleased product, etc.), remember push protection and branch protection both require GitHub Team ($4/month/seat) on private repos — budget for it rather than assuming the public-repo defaults apply.

---

## 12. Incident response

**Practice:** every real incident (security, outage, data issue) gets a short, blameless postmortem in `docs/postmortems/`: what happened, timeline, root cause, blast radius, corrective actions taken, and what prevents recurrence. Blameless means the document interrogates the *process* gap (why did nothing catch this) rather than assigning fault to whoever made the mistake — mistakes are inevitable, the question is always why the system didn't catch it sooner.

**Why FANG-adjacent:** this is standard SRE/incident-management practice at every major tech company specifically because the alternative — no postmortem — means the same class of incident recurs, since nobody systematically asked "what would have prevented this." The corrective-actions section is what turns a bad afternoon into a permanent process improvement.

**Right-sized:** `docs/postmortems/0001-secret-leak-2026-08-06.md` is the worked example — it exists precisely because this org had its first real incident during the writing of this standard, and the corrective actions in that document are literally what became §5 of this file.

---

## Summary checklist

| Practice | Status across Axonity today (2026-08-08) | Mechanism |
|---|---|---|
| Trunk-based dev | Still partial — `axonity_chatbot`'s `phase_3` remains a long-lived branch; `phase_3` → `main` consolidation is still an open decision | Short branches + PRs |
| CODEOWNERS | Present on all 3 repos + template | `CODEOWNERS` file |
| CI gating (blocking) | `axonity_chatbot` and `visual_search_ranking` both have real, passing CI (secrets/lint/test/docker); `visual_search_ranking`'s `black`/`isort` checks are still `continue-on-error: true` (harmless report, not a gate) | `.github/workflows/ci.yml` |
| Type-check gate | **Template has it** (`typecheck` job, mypy) as of 2026-08-08 — added after a client review caught this doc promising it without it existing anywhere. **Not yet backported** to `visual_search_ranking` or `axonity_chatbot`'s Python backends (their frontends already have real `tsc` type-checking) — deliberately deferred, since bolting mypy onto never-type-annotated code tends to surface a real backlog of errors that deserves its own reviewed pass, not a drive-by | `pyproject.toml` `[tool.mypy]` + CI `typecheck` job |
| Secret scanning + push protection | **On for all 3 repos** (all now public) | GitHub security settings + pre-commit hook |
| Dependabot | **Enabled on all 3 repos** (version-update PRs + vulnerability alerts) | `.github/dependabot.yml` |
| Conventional Commits | Enforced via pre-commit on `axonity_chatbot` and `visual_search_ranking`; historical commits predate this and remain freeform | pre-commit commit-msg hook |
| Enforced coverage gate | `axonity_chatbot`'s `--cov-fail-under=85` (in `pytest.ini`) now runs inside real, passing CI — not independently re-verified as gating a failure this session | CI test job |
| ADRs / postmortems | `docs/adr/` present on all 3 repos + template; `docs/postmortems/` present on `.github`, `visual_search_ranking`, and the template (with the real 2026-08-06 incident writeup) | `docs/adr/`, `docs/postmortems/` |
| Versioning / releases | Never done, anywhere | Git tags + `CHANGELOG.md` |
| Branch protection | **Now available for free** on all 3 repos (public) — deliberately not yet applied; `.github/branch-protection-ruleset.json` is ready in each repo when the team is ready for mandatory PR review | Apply the prepared ruleset |
| Org 2FA requirement | Still off | GitHub org Settings (manual) |
