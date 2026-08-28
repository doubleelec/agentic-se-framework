# Maintenance Guide

## Roles

- `origin`: private primary remote for the `agentic-se-framework` workspace
- `upstream clone`: local clone under `vendor/mattpocock/upstream/`, used only for upstream intake and not committed to the main repo
- `Deployment Targets`: Trae, Antigravity, etc. (deployment targets only)

## First-Time Setup

1. Copy `manifests/install-targets.example.toml` to `manifests/install-targets.toml`.
2. Edit the target paths to match your machine.
3. The real `install-targets.toml` is gitignored and machine-specific; never commit it.

## Daily Workflow

1. Modify skills under `vendor/mattpocock/local/skills/` or `core/`.
2. Review changes with `git status` and `git diff`.
3. Commit locally in this framework workspace.
4. Publish with `ops/install.ps1`.
5. Push to the primary remote.

### Install Deletion Policy

Install replaces only the skills listed in `manifests/skills.toml`, one by one (backup -> replace). It must NEVER prune, mirror-delete, or clean up directories in an install root that are absent from the manifest: install targets are shared scopes, and unmanifested directories may belong to other projects or be retired skills kept on purpose (e.g. `send-me-email`). Retiring a skill from targets is always an explicit, manual `ops/uninstall.ps1` step.

## Install Conflict Judging

`ops/install.ps1` never blindly overwrites a deployment target:

1. Every install records a per-file SHA256 content baseline in `logs/install-state/`.
2. The next install re-hashes the target and compares it against that baseline.
   Any difference means the skill was modified inside the IDE after install, and
   the whole install batch is aborted before a single file is touched (mtime is
   not trusted; backdated edits are still caught). Old state files without a
   baseline fall back to the previous mtime comparison.
3. If no baseline exists but the target directory does, the target is compared
   against the repo source; an unexplained difference also aborts the install.
4. The installer never overwrites a diverged target; there is no force flag.
   Resolving a conflict is always an explicit step:
   - To keep the installed copy (a deliberate edit): run
     `ops/capture_hotfix.ps1 -TargetName <target> -SkillName <name>`, commit,
     then republish.
   - To discard it and redeploy from source: run
     `ops/uninstall.ps1 -TargetName <target> -SkillName <name>` (backs up
     first), then republish.

## Upstream Sync Workflow

1. Update the local `vendor/mattpocock/upstream/` clone with `ops/sync_upstream.ps1`.
2. Review upstream changes skill by skill.
3. Port accepted changes into `vendor/mattpocock/local/skills/` and keep the path as close to upstream as possible.
4. Update `vendor/mattpocock/local/upstream_lock.toml` to record the new upstream commit and any mapping changes.
5. Document local divergence where needed.
6. Commit and publish.

## Hotfix Workflow

Use this only when a skill was edited directly in an external deployment directory.

1. Run `ops/diff_installed.ps1` to confirm drift.
2. Run `ops/capture_hotfix.ps1 -SkillName <name>`.
3. Review the captured source change in this workspace.
4. Commit immediately.
5. Republish from source to make install and source consistent again.

## Branching Guidance

- `main` / `master`: stable framework release state
- `feat/<topic>`: normal feature or methodology enhancements
- `sync/upstream-<date>`: upstream intake batches
- `hotfix/<topic>`: captured install-side fixes

## Repository Policy

- Do not treat the IDE install directories as a source repository.
- Do not edit `vendor/mattpocock/upstream/` for long-lived customizations.
- Keep long-lived customizations in `vendor/mattpocock/local/` or `core/`.
- The upstream clone is rebuildable and intentionally excluded from the main repository.
- Never commit personal paths or credentials; keep them only in gitignored local config such as `manifests/install-targets.toml`.
