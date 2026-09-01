# Release Operations Guide

How to operate the public release outlet without leaking private signal.
This file is **public** — it ships inside release snapshots. Write it exactly as
you would write documentation for strangers: placeholder identities, no real
URLs, no personal paths.

## Privacy statement (read this first)

Public release is **permanent**. Within minutes of a push, anything shipped in a
snapshot can be forked, cached, searched, and archived; deleting it later does
not undelete the copies. Treat these commitments as binding on every release:

1. **Never ship personal identity.** Not in tracked files, not in author or
   committer metadata, not in tags, not in URLs.
2. **Never ship private infrastructure.** No internal-forge hostnames or clone
   URLs, no tokens or credentials, no absolute home paths.
3. **When in doubt, leave it out.** A missing feature is fixable; leaked
   personal data is not. Prefer placeholders (`<you>`, `<public-...>`) over
   real values.
4. **Enforce mechanically AND by eye.** The red-line scan below catches known
   patterns, but the person/agent running the release must still review the
   staged file list and the snapshot's commit metadata before every push.

A release that skips this statement's checklist is not a release — it is a
privacy incident waiting to be archived.

## Remote topology

Two remotes, strictly separated roles. Never merge their habits.

| Remote   | Role                              | Branch | Push frequency      |
| :------- | :-------------------------------- | :----- | :------------------ |
| `origin` | Private development line          | `master` | anytime (routine) |
| `public` | Public release outlet             | `main`   | milestones only    |

Check the live configuration with `git remote -v`. The real URLs live only in
`.git/config` — this file never records them.

- `origin` may be any private forge. Refer to it as `origin` here, never by its
  hostname.
- `public` is assumed to be GitHub. Keep the remote URL out of this file's scope
  (real one is local config only).

## Privacy red lines (no exceptions)

Anything below is **forbidden in every file that a release snapshot ships** —
including this one, `AGENTS.md`, `README.md`, and any `docs/**`:

1. Real internal-forge hostnames, repository URLs, or SSH/HTTPS clone URLs
   (example pattern: `git@<internal-forge>...`). Use placeholders instead.
2. Personal email addresses or usernames (the author identity used by `git
   config --global user.email` is private signal — see identity override below).
3. Absolute personal paths (e.g. a Windows user-profile path such as
   `<drive>:\Users\<name>\repo`).
4. Private tokens, deployment credentials, install-target files (those are
   gitignored; only `.example.toml` templates ship).
5. Anything that could de-anonymize the maintainer beyond what the public
   repo name itself already reveals.

## Commit identity override (mandatory on release)

The machine's global git identity (from `git config --global user.email`) is
private signal and must **never** appear in public commits. Release snapshots
must be created with an explicit public identity. Same rule applies to tags.

```bash
git -c user.name="agentic-se-framework" \
    -c user.email="<public-noreply@example.com>" \
    commit -m "chore: release agentic-se-framework <version>"
```

Before any release push, verify the snapshot's author/committer metadata:

```bash
git log --format="%an <%ae> | %cn <%ce>" -1
# Must show the public identity above — not the machine's private one.
```

For tag releases, annotate with the same override:

```bash
git -c user.name="agentic-se-framework" \
    -c user.email="<public-noreply@example.com>" \
    tag -a "v<version>" -m "agentic-se-framework <version>"
```

## Panorama diagram single-source refresh

`README.md` embeds `docs/html/panorama.en.svg` and `panorama.zh.svg` as static
preview images.

**English edition is single-sourced**: edit only the standalone
`docs/html/panorama.en.svg`, then re-inject the `<svg>` block into its two
inline copies (`docs/agentic_se_framework.en.md` and
`docs/html/agentic_se_framework.en.html`):

```powershell
ops/refresh_panorama.ps1          # re-inject md + html from the SVG
ops/refresh_panorama.ps1 -Check   # pre-release gate; fails on drift
```

The root `<svg>` element MUST keep `xmlns="http://www.w3.org/2000/svg"`: the
standalone file is loaded through an `<img>` tag, where browsers parse SVG as
XML and reject a missing namespace (broken image on the GitHub project page).

**Chinese edition** keeps its inline SVG in
`docs/agentic_se_framework.zh.md` as the source; `panorama.zh.svg` is an
extracted snapshot — re-extract by hand if the zh diagram changes, or extend
`refresh_panorama.ps1` with a `-Lang zh` mode.

After any refresh, re-run the red-line scan below — the SVGs must stay free of
the private tokens like any other shipped file.

## Release procedure (milestone snapshot)

Public history must stay clean: never mirror `origin` history (early history
contains private paths/emails/forge addresses). The public `main` branch grows
one normal commit per release — each release commit's parent is the previous
public release, so GitHub shows an accumulating commit count instead of a
perpetual `1 commit` from orphan roots.

**Automated script (preferred).** Run the flow through `ops/release.ps1`
rather than the manual commands below. The script encodes this procedure and
adds four guards against the classic failure modes: it hard-fails when
`git fetch public` errors (a snapshot built on a stale `public/main` base
makes the next push a non-fast-forward), resets `public-main` to the exact
remote tip before overlaying, skips the commit entirely when the overlay
produces no delta (a duplicated snapshot diverges the branch), and runs the
red-line scan before committing. If its push step fails (e.g. a terminal
without GitHub credentials), the snapshot commit is already safe on local
`public-main` — retry the push from a credentialed terminal, never rebuild.

Manual reference (what the script automates):

```bash
# 1. sync the local release branch to the latest public release
git fetch public
git checkout -B public-main public/main

# 2. overlay the milestone content from master — tracked files only, so
#    .gitignore keeps private files out; `origin` history is NOT copied
git checkout master -- .

# 3. if a file from a previous release must no longer ship, remove it
#    explicitly (e.g. `git rm --cached <path>`): the overlay only adds/overwrites

# 4. stage & VERIFY before committing — anything below must be absent
git add -A
git status
#   - no manifests/install-targets.toml (personal)
#   - no logs/, no vendor/mattpocock/upstream/, no .scratch/
git grep -I -i -n -E "doubleelec|qq\.com|weixin|[CDE]:[\\/]Users" -- . ':!docs/agents/release.md' ':!ops/release.ps1' ':!LICENSE' ':!README.md'
#   - empty (license owner name allowed only in LICENSE; this file's own
#     scan-string is excluded via ':!docs/agents/release.md'; the release
#     script is excluded because it embeds the same scan-string literally;
#     README is excluded because it deliberately carries the public Pages URL)

# 5. commit with the PUBLIC identity override (see above)
git commit -m "chore: release agentic-se-framework <version>"

# 6. push — a fast-forward onto the previous release; commits accumulate
git push public public-main:main
```

After pushing, switch back to the development line:

```bash
git checkout master
```

## Verification checklist (run before every release push)

- [ ] `LICENSE`, `CODE_OF_CONDUCT.md`, `CONTRIBUTING.md` present in snapshot
- [ ] `manifests/install-targets.toml` (personal) is NOT staged
- [ ] `git grep -I -i -n -E "doubleelec|qq\.com|weixin|[CDE]:[\\/]Users"` empty
      outside LICENSE, `docs/agents/release.md` (the guide's own scan tokens),
      `ops/release.ps1` (the script embeds the same scan-string literally),
      and `README.md` (its deliberate public Pages URL)
- [ ] Author/committer metadata show the public identity, not the machine's
- [ ] `ops/refresh_panorama.ps1 -Check` passes (English md/html match
      `docs/html/panorama.en.svg`); zh `panorama.zh.svg` present and in sync
      with `docs/agentic_se_framework.zh.md` (see refresh procedure above)
- [ ] No orphan-snapshot leftovers staged (e.g. temporary branch files)
- [ ] Public remote URL is HTTPS (local SSH client is too old for GitHub's
      post-quantum KEX handshake)
- [ ] Privacy statement (top of this file) re-read and its four commitments
      confirmed against the staged snapshot

## Troubleshooting

- `choose_kex: unsupported KEX method sntrup761x25519-sha512@openssh.com`
  → local OpenSSH predates GitHub's post-quantum KEX; use HTTPS for `public`.
- HTTPS push to `public` fails with
  `schannel: AcquireCredentialsHandle failed: SEC_E_NO_CREDENTIALS (0x8009030e)`
  → Windows schannel has no GitHub credential. The release commit is already
  on `public-main` locally; the push is a one-line operation. Run it from a
  PowerShell that has GitHub credentials cached (the one you normally use to
  `git push` to GitHub), do NOT recreate the snapshot:
  ```powershell
  cd <repo>
  git checkout public-main
  git push public public-main:main
  git checkout master
  ```
  The release identity was set at commit time and travels with the commit, so
  the push only needs network auth, not a re-commit. To pre-cache the
  credential, run `git credential-manager github login` once, or use a
  Personal Access Token via `git -c credential.helper= -c credential.helper='!gh auth git-credential' push ...`.
- Push rejected at `public` with `non-fast-forward` → the local `public-main`
  was rebuilt on a stale base (an earlier `git fetch public` failed, or the
  remote advanced between two snapshot builds), so the branch shares no
  ancestry with the remote tip. Prevention: always release through
  `ops/release.ps1`, which gates on the fetch and resets to the remote tip
  before building, and never rebuild a snapshot after a failed push. Recovery:
  ```bash
  git fetch public
  git checkout public-main
  git reset --hard public/main   # drop the diverged local snapshot commits
  # re-run ops/release.ps1 (or redo the manual procedure) on the fresh base
  ```
  Do NOT `--force` push to fix this: overwriting a public release commit is a
  history rewrite on a permanent outlet (see the privacy statement).
- Forgot the identity override → rewrite the snapshot commit with the public
  identity and force-push only if the outlet has no collaborators yet;
  otherwise coordinate before rewriting public history.