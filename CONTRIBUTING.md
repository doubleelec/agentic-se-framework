# Contributing to agentic-se-framework

Thanks for your interest in contributing. This guide keeps onboarding short by pointing to the governance documents that already define how this repository works.

## Setup

1. Clone the repository.
2. Copy `manifests/install-targets.example.toml` to `manifests/install-targets.toml` and point the paths at your machine. This file is gitignored; never commit it.
3. Publish skills to your IDE targets with `./ops/install.ps1` when needed.

## Read first

- `README.md` — repository layout, getting started, working model, credits
- `MAINTENANCE.md` — daily workflow, upstream sync, hotfix capture, branching, install deletion policy
- `AGENTS.md` — workspace conventions: dual issue streams, triage labels, domain docs, embedded-upstream snapshot rules (`core/` pattern)

## Making changes

- Core methodology skills live under `core/`; third-party derivatives stay under `vendor/mattpocock/local/`, mirroring upstream paths.
- Keep new skills consistent with the existing structure: `SKILL.md` plus optional `templates/`, `resources/`, and (for embedded tooling) a thin-wrapper-friendly `core/`.
- Documentation pairs with code: if a change alters behavior described in `docs/new_project_skill_panorama.zh.md`, update its English counterpart `docs/new_project_skill_panorama.en.md` too; `ops/check_bilingual.ps1` verifies heading parity.

## Before opening a PR

- No personal paths, credentials, or internal endpoints in tracked files; machine-specific configuration belongs in gitignored local manifests.
- Run relevant checks: `ops/diff_installed.ps1` after installs; governed projects run their architecture tests (`tests/test_governance.py`).
- Describe what changed, why, and which artifacts (specs, tickets, issues) it touches.

## Reporting issues

Use the dual-stream tracker described in `docs/agents/issue-tracker.md`: long-lived issues in `docs/issues/`, temporary exploration tickets under `.scratch/<feature-slug>/`.

## License

By contributing, you agree that your contributions are licensed under the MIT License of this repository. Modifications of upstream material must preserve the attribution described in the third-party notice in `LICENSE`.
