# agentic-se-framework

## Agent skills

### Issue tracker

Work items live in two streams: temporary tickets under `.scratch/<feature-slug>/` (`/to-tickets`) and permanent issues under `docs/issues/` (`/to-issues`). See `docs/agents/issue-tracker.md`.

### Triage labels

Use the default canonical triage labels for this repo. See `docs/agents/triage-labels.md`.

### Domain docs

This repo uses a single-context layout. See `docs/agents/domain.md`.

### Embedded upstream snapshots (the `core/` pattern)

Skills under `core/<name>/` that vendor a third-party codebase
(e.g. `llm-as-a-verifier`, future `vendor/*` forks) MUST keep the
snapshot and the skill-layer customisation mechanically separated so
that one-way rebase from upstream stays a low-conflict, reviewable
operation.  Follow these rules on every skill that embeds an upstream
fork:

1. **Snapshot lives in a dedicated subdirectory, treat it as read-only.**
   Copy the upstream package verbatim under
   `core/<name>/core/<upstream-package>/`.  Treat the `core/`
   tree as if it were checked out from upstream: rebase operations
   replace the whole snapshot wholesale.  Any behaviour added *for the
   skill* must NOT live inside `core/`.

2. **Skill-layer customisations go next to the runner, NOT in core.**
   All model-specific code (endpoints, credential env vars, concurrency
   caps, client markers, backend routing, skips of engine-internal
   optimisations that hosted APIs don't support) lives in the skill
   root in a standalone adapter module (e.g.
   `<skill>/adapter.py`).  The runner imports that
   adapter directly (never re-exported from inside core).  The goal is
   that diffing `core/<package>/` against the upstream fork should show
   only bounded, optional-style call-sites — never a new backend
   embedded as if/elif ladders.

3. **Minimise the bridge to pure-add, bounded, no-op-default hooks.**
   When the snapshot genuinely needs to dispatch to the skill-layer,
   add a pair of tiny, documented extension hooks in the snapshot: a
   module-level global attribute with a unique name (e.g.
   `_EXT_SKIP_PREFILL`, `_EXT_MAX_WORKERS`) that defaults to `None`,
   and a guarded call-site of the form
   `hook = globals().get("_EXT_FOO"); if hook is not None: r = hook(); if r is not None: use r`.
   The upstream-only branch (no adapter installed) must retain 100 %
   identical behaviour.  Never add an `elif "ling" in base_url` or a
   `create_*_client()` variant inside core; those belong in the adapter
   and register themselves at runner startup via `install(core_module)`.

Verification checklist for PRs touching an embedded skill:

- [ ] `git diff --no-index vendor/<upstream>/local/<pkg> core/<name>/core/<pkg>`
      contains only the pre-approved hook call-sites and comments,
      nothing backend-specific.
- [ ] Every adapter module exports an `install(core_module)` that is
      idempotent; runner.py calls it once before any scoring flow.
- [ ] No module under `core/` imports anything from the skill root;
      dependencies flow strictly *skill layer → core*, never the reverse.
- [ ] A regression test (kept under `core/<name>/tests/` as a
      pure dev asset, never surfaced in SKILL.md or the runner CLI)
      exercises each hook with and without the adapter installed and
      confirms the "silent-failure" class of bugs is caught early.

## Repository remotes & public release

This repo keeps two remotes with strictly separate roles:

- `origin` — private development line on the internal forge (`master`). All
  routine work, commits, and backups flow here.
- `public` — public release outlet on GitHub (`main`). It holds **sanitized
  release snapshots only**, never a mirror of `origin` history.

Rules:

1. **Never mirror `origin` history to `public`.** Early history contains
   personal absolute paths, emails, and internal forge addresses. Always
   publish via a fresh orphan snapshot (below).
2. **Release via sanitized orphan snapshot, per milestone:**
   ```bash
   git checkout --orphan public-main
   git add -A
   git status          # verify: no personal paths / credentials / internal addresses
   git commit -m "chore: release agentic-se-framework <version>"
   git push public public-main:main
   ```
   `.gitignore` covers `manifests/install-targets.toml`, `.scratch/`, `logs/`,
   `vendor/mattpocock/upstream/`; those must never appear in `git status` above.
3. **Pre-push verification checklist:**
   - `LICENSE`, `CODE_OF_CONDUCT.md`, `CONTRIBUTING.md` present
   - run the red-line scan (token list kept in `docs/agents/release.md`,
     which excludes itself and `LICENSE`; command tokens are listed there,
     not inlined here, so this file does not trip its own scan):
     `git grep -I -i -n -E "<tokens>" -- . ':!docs/agents/release.md' ':!LICENSE' ':!README.md'` empty
     (except `LICENSE` copyright line, `<your-name>` placeholders, and the
     public GitHub Pages URL in `README.md`)
   - `install-targets.toml` (personal) not tracked; only the `.example.toml` template is
4. **`public` uses HTTPS** (local OpenSSH is too old for GitHub's post-quantum
   KEX; SSH to `github.com` fails host-key negotiation).
5. **Push only at milestones/tags** — the public side is a release outlet, not a
   development mirror. Tags may be pushed alongside the snapshot for versioning.

Detailed operations guide, including privacy red lines (what a release snapshot
must never contain) and the mandatory commit-identity override for public
commits: `docs/agents/release.md`.
