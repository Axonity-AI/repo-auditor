# Onboarding — Your First Weeks at Axonity

This is for anyone joining an Axonity project who has never worked inside a
review-gated engineering workflow before. It assumes **no prior knowledge**. If
you've only ever pushed straight to `main` on your own projects, you're the
intended reader.

It explains *what to do*. [ENGINEERING_STANDARDS.md](ENGINEERING_STANDARDS.md)
explains *why we do it* — read that second, once these mechanics feel routine.

---

## 1. One-time setup

Clone the repo, then run:

```bash
./scripts/setup.sh
```

That installs dependencies and — importantly — installs the **pre-commit
hooks**. Git hooks are not part of a clone (deliberately: otherwise cloning a
repo would let a stranger run code on your machine), so this step cannot be
automatic. If you skip it, you lose the local safety net described in §5.

Verify it worked:

```bash
pre-commit run --all-files
```

The first run may reformat files. Review that diff before committing it.

---

## 2. The loop you'll repeat every day

```
branch  →  commit  →  push  →  open a PR  →  CI runs  →  review  →  merge
```

Nothing reaches `main` except through that path. Not "usually" — always,
including for the person who owns the company. `main` is protected, so a direct
push is rejected by GitHub itself.

Why: `main` is the branch we assume is always working. The moment someone
pushes something broken to it, everyone else's work is built on sand. Making it
mechanically impossible is easier than remembering.

---

## 3. What a pull request actually is

A PR is a **proposal to merge one branch into another**, plus a place to discuss
it. That's all. It is not a formality and it is not a code-quality ceremony —
it's the unit of work.

Concretely:

```bash
# 1. Start from an up-to-date main
git checkout main
git pull

# 2. Make a branch. Name it for what it does.
git checkout -b feat/add-defect-threshold-calibration

# 3. Work. Commit as you go (see §4 for the message format).
git add src/calibration.py tests/test_calibration.py
git commit -m "feat: add per-product threshold calibration"

# 4. Push the branch
git push -u origin feat/add-defect-threshold-calibration

# 5. Open the PR
gh pr create --fill
```

GitHub then shows the diff, runs CI against it, and lets a reviewer comment on
specific lines.

**Keep PRs small.** A 200-line PR gets a real review. A 2,000-line PR gets
"looks good to me," which is worth nothing to you. If a change is getting large,
split it: one PR that adds the function, one that wires it up.

**Write the description for someone who wasn't there.** What does this change,
and why? If you made a judgement call, say what you considered and rejected.
This is the part that becomes your interview story later.

---

## 4. Commit messages: Conventional Commits

Every commit message starts with a type:

```
feat: add per-product threshold calibration
fix: correct off-by-one in project root resolution
docs: explain the synthetic data ablation setup
test: add regression test for empty input
refactor: extract embedding cache into its own module
chore: bump ruff to 0.6.9
```

The `commit-msg` hook rejects messages that don't match, so you'll find out
immediately rather than at review time.

Why bother: the type prefix is machine-readable. It's what lets a release tool
generate a changelog and pick the next version number automatically. Even before
we do that, it makes `git log` scannable — you can see at a glance whether a
week was features or firefighting.

---

## 5. CI, and what to do when it's red

**CI** ("continuous integration") is a set of checks GitHub runs automatically on
every PR. Ours live in [.github/workflows/ci.yml](.github/workflows/ci.yml) and
run as separate jobs so a failure tells you *which* thing broke:

| Job | What it checks | If it fails |
|---|---|---|
| `secrets` | No API keys, tokens or private keys anywhere in the repo or its history | **Stop.** See §6 — this one is different. |
| `lint` | Code style and formatting (ruff) | Run `ruff check --fix .` and `ruff format .` |
| `typecheck` | Type annotations are consistent (mypy) | Read the error; it names a file and line |
| `test` | The test suite passes (pytest) | Run `pytest` locally and fix |
| `docker` | The container image still builds | Usually a missing dependency in `requirements.txt` |

These are **blocking**. A red check means the merge button is disabled. That is
the entire point of them.

### The rule that matters

**When CI is red, fix the cause. Never route around the check.**

Things that look like fixes but aren't: deleting the failing test, adding
`continue-on-error: true` to the job, committing with `--no-verify`, or adding a
blanket `# type: ignore`. Each of these turns a check that gates merges into a
check that decorates them — the check still shows up, still looks green-ish, and
protects nothing. If you genuinely believe a check is wrong, say so in the PR
and we'll change the check deliberately.

### A worked example

You push, and CI goes red on `test`. Click the failed job and you see:

```
FAILED tests/test_calibration.py::test_threshold_bounds
E   assert 1.02 <= 1.0
```

What to do:

1. Reproduce it locally: `pytest tests/test_calibration.py::test_threshold_bounds`
2. Understand it. Here the threshold exceeded 1.0, so either the clamp is
   missing or the test's assumption is wrong.
3. Decide which is actually broken — the code or the test. Both happen.
4. Fix, commit, push. CI re-runs on the new commit automatically.

Step 3 is the one people skip. A test failing is information; find out what it's
telling you before you change anything.

---

## 6. Secrets — the one thing with no recoverable mistake

Never commit an API key, password, token, `.env` file, or private key.

This is not hypothetical here. In August 2026 a real Anthropic key and a real
OpenAI key were pushed to a repo that later went public, and both had to be
rotated. The full write-up is in
[docs/postmortems/0001-secret-leak-2026-08-06.md](docs/postmortems/0001-secret-leak-2026-08-06.md)
— read it, it's short.

The important property: **git history is forever by default.** Deleting a key in
a later commit does not remove it; it's still in the previous commit, and
anything public gets scraped within minutes. Once a secret is pushed, the only
real fix is to rotate the secret — assume it's burned.

Three layers protect against it, and you should understand that they're
independent:

1. **Pre-commit hook** (gitleaks) — catches it on your machine, before the commit exists.
2. **GitHub push protection** — catches it at the server if you skipped the hook.
3. **CI `secrets` job** — scans the whole history on every PR.

Secrets go in a local `.env` file (which is gitignored) or in GitHub Actions
secrets. Never in source, never in a notebook, never in a config file you plan
to "clean up later."

---

## 7. ADRs — writing down *why*

An **ADR** (Architecture Decision Record) is a short markdown file recording a
decision you made and the reasoning behind it. They live in
[docs/adr/](docs/adr/) and are numbered sequentially.

Write one whenever you make a choice that a reasonable person could have made
differently and that would be expensive to reverse. Choosing a model
architecture, a database, an evaluation metric, a data representation — yes.
Naming a variable — no.

The value is entirely in the future. Six months on, nobody remembers why the
metric is F1-at-a-fixed-threshold instead of AUROC, and without a record you
either re-litigate it or cargo-cult it. For you specifically, it's also the
single most useful interview artifact you will produce: it's written evidence
that you reasoned rather than guessed.

### A real one, in full

```markdown
# 3. Use embedding-kNN rather than supervised segmentation for the V1 detector

Date: 2026-08-20
Status: Accepted

## Context

We need a defect detector for the V1. Three options were on the table:
supervised segmentation (needs pixel labels), embedding-based nearest-neighbour
against a "known good" bank, and a reconstruction autoencoder.

Our dataset has ~40 labelled defects per product family. That is thin for
supervised segmentation, which typically wants hundreds.

## Decision

Use frozen pretrained features + kNN against a normal-image bank for the V1.

## Consequences

Good: no training run needed, so the whole loop is minutes not hours, and it
gives us a strong baseline to measure everything else against. Works with the
label count we actually have.

Bad: inference needs the reference bank in memory, which will not scale past a
few thousand reference images without an index. Accepted for V1; noted as the
first thing to revisit if we productionise.

We will revisit if labelled defects exceed ~300 per family.
```

Copy [docs/adr/0000-template.md](docs/adr/0000-template.md) to start one. It
should take fifteen minutes. If it's taking an hour, you're writing a design doc
instead.

---

## 8. Using AI coding tools here

AI assistance is expected, not merely tolerated. Use it for scaffolding,
boilerplate, unfamiliar APIs, debugging, and review. The constraint is on
*ownership*, not on tooling:

- **You own the problem statement, architecture, experiment design, success
  metrics and scope** — write or explicitly approve these before major
  implementation, not after.
- **Every significant modelling or design decision gets a short record** (§7):
  what you chose, what you rejected, and why.
- **If a model proposes a library or approach, verify it against the official
  docs** before it goes in. Confident-sounding and correct are different things.
- **You must be able to modify, debug or defend any important code path**
  without the assistant. If you can't explain what a function does, it isn't
  ready to merge — regardless of whether the tests pass.
- **No claim on a résumé or in a demo unless the repo contains the evidence.**

The short version: the model can write code; you own the engineering. That
distinction is the entire thing being assessed.

---

## 9. Definition of done

A change is done when *all* of these are true — not when the code works:

- [ ] It does what the PR description says it does
- [ ] Tests cover the new behaviour, including at least one failure case
- [ ] All CI checks are green, with nothing silenced or bypassed
- [ ] A human has reviewed and approved it
- [ ] Docs updated if behaviour visible to anyone else changed
- [ ] An ADR exists if a real decision was made
- [ ] You can explain every line you're merging

"It works on my machine" is the beginning of this list, not the end.

---

## 10. Cadence, and how to be stuck well

- **Weekly demo.** Show what runs. A broken demo with an honest explanation is
  fine and normal; a polished slide about work that doesn't run is not.
- **Written weekly update:** what you did, what you learned, what's blocking
  you, what's next. Short. This is how remote work stays unblocked.
- **PRs get reviewed within one working day.** If yours is sitting longer, ping.

**When you're stuck:** spend a genuine effort window on it — roughly an hour —
then ask. Include what you tried and what you expected to happen. Being stuck is
information, and hiding it for three days converts a ten-minute answer into a
lost week. Nobody is assessed on never being stuck. People are assessed on what
they do about it.
