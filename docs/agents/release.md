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

## Panorama SVG snapshot refresh

`README.md` embeds `docs/html/panorama.en.svg` and `panorama.zh.svg` as static
preview images. These are **snapshots**: if the source panorama diagrams in
`docs/new_project_skill_panorama.{en,zh}.md` change, the SVGs must be
re-extracted or the release ships a stale picture.

Refresh procedure (run against the working tree on `master` before snapshotting):

1. In the source `.md`, locate the inline `<svg ...> ... </svg>` block (one per
   language edition).
2. Extract that block verbatim into `docs/html/panorama.<lang>.svg` (same
   `viewBox`, same content; no HTML wrapper). The root `<svg>` element MUST keep
   `xmlns="http://www.w3.org/2000/svg"` in both the `.md` source and the
   extracted `.svg`: the standalone file is loaded through an `<img>` tag, where
   browsers parse SVG as XML and reject a missing namespace (broken image on the
   GitHub project page). Keep source and snapshot byte-identical, `xmlns`
   included.
3. Re-run the red-line scan below — the SVGs must stay free of the private
   tokens like any other shipped file.

## Release procedure (milestone snapshot)

Public history must stay clean: never mirror `origin` history (early history
contains private paths/emails/forge addresses). Publish a fresh orphan snapshot
instead.

```bash
# 1. from a clean working tree on master
git checkout --orphan public-main

# 2. stage everything; .gitignore excludes private files
git add -A

# 3. VERIFY before committing — anything below must be absent
git status
#   - no manifests/install-targets.toml (personal)
#   - no logs/, no vendor/mattpocock/upstream/, no .scratch/
git grep -I -i -n -E "doubleelec|qq\.com|weixin|[CDE]:[\\/]Users" -- . ':!docs/agents/release.md' ':!LICENSE' ':!README.md'
#   - empty (license owner name allowed only in LICENSE; this file's own
#     scan-string is excluded via ':!docs/agents/release.md'; README is
#     excluded because it deliberately carries the public Pages URL)

# 4. commit with the PUBLIC identity override (see above)
git commit -m "chore: release agentic-se-framework <version>"

# 5. push the snapshot only
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
      and `README.md` (its deliberate public Pages URL)
- [ ] Author/committer metadata show the public identity, not the machine's
- [ ] Panorama SVGs (`docs/html/panorama.{en,zh}.svg`) present and in sync with
      `docs/new_project_skill_panorama.{en,zh}.md` (see refresh procedure above)
- [ ] No orphan-snapshot leftovers staged (e.g. temporary branch files)
- [ ] Public remote URL is HTTPS (local SSH client is too old for GitHub's
      post-quantum KEX handshake)
- [ ] Privacy statement (top of this file) re-read and its four commitments
      confirmed against the staged snapshot

## Troubleshooting

- `choose_kex: unsupported KEX method sntrup761x25519-sha512@openssh.com`
  → local OpenSSH predates GitHub's post-quantum KEX; use HTTPS for `public`.
- Push rejected at `public` → confirm the snapshot commit is orphan-based and
  you're pushing `public-main:main`, never a mirror of `origin/master`.
- Forgot the identity override → rewrite the snapshot commit with the public
  identity and force-push only if the outlet has no collaborators yet;
  otherwise coordinate before rewriting public history.