---
name: to-arch
description: Author and maintain the system's two execution blueprints - the Architecture Description (docs/architecture.md) and the living Action Plan (docs/action-plan.md). Use when the user asks for a full architecture design document or a whole-system build order (init), at milestones or after major decisions to reconcile docs against the governed implementation (reconcile), or whenever a planned slice starts, finishes, or blocks so the plan's progress stays true (update-progress).
argument-hint: "[init | reconcile | update-progress] - omit to auto-detect"
---

# To Arch

Turn scattered upstream decisions into the two artifacts the execution layer consumes:

1. **Architecture Description** - `docs/architecture.md`: why the system is shaped the way it is (design thinking, stakeholder concerns, module decomposition, selected views).
2. **Action Plan** - `docs/action-plan.md`: the cross-module construction order (governance scaffolding -> module builds -> integration testing) with parallel groups and serial justifications. It doubles as the project's **resume point**: anyone opening a half-built system reads this one file to know what is done, what is in flight, and how to continue.

Upstream inputs: `CONTEXT.md`, `docs/adr/*.md`, quality-attribute scenarios, a wayfinder map (if any). Downstream consumers: `governed-arch` translates boundaries into TOML enforcement; `/to-spec` reads the description for its global frame; every slice of work lives on the plan.

## Mode

Pick exactly one, state it to the user, then run only that path:

| Mode             | Enter when                                                              | Output                          |
| ---------------- | ----------------------------------------------------------------------- | ------------------------------- |
| **init**         | no `docs/architecture.md` yet                                           | both artifacts, drafted then written |
| **reconcile**    | description exists; milestone, major new decision, or drift check asked | updated sections + refreshed plan |
| **update-progress** | only progress changed (a slice started / finished / blocked)          | plan statuses and header only   |

## Step 1 - Inventory (init & reconcile)

Read what exists: `CONTEXT.md` (its glossary is binding vocabulary), every `docs/adr/*.md`, quality-attribute scenario docs, wayfinder map issues, existing `architecture.toml` / `module.toml`, and - in reconcile - the real code tree.

Produce two working lists before writing anything:

- **Decision inventory**: each significant decision found, with its ADR link.
- **Viewpoint selection**: consult `resources/viewpoint-catalog.md` and select only viewpoints addressing concerns real stakeholders have expressed. A concern without a covering viewpoint is a gap; a viewpoint without a concern is deletion bait.

Handle gaps by kind - **zero-invention**: every sentence in both artifacts must trace to an artifact or an explicit user statement; an untraceable assertion is a defect.

- decision-shaped gap (module split? sync vs events?) -> list it, recommend `/grill-with-docs` (small) or `/wayfinder` (large);
- fact-shaped gap (external API behaviour, protocol details) -> recommend `/research`;
- terminology gap -> recommend `/domain-modeling`.

Completion criterion: every module that exists or is planned appears in exactly one inventory row, and every selected viewpoint cites the concern it covers.

## Step 2 - Draft the Architecture Description (init; incremental edits in reconcile)

Follow the section structure in `templates/architecture-description-format.md`. If the project carries its own `docs/templates/ARCHITECTURE-DESCRIPTION-FORMAT.md`, the project-local copy wins.

- Thin by default: include a view only because its concern was selected in Step 1.
- Vocabulary comes from `CONTEXT.md`; words listed under `_Avoid_` are banned.
- Every architectural decision line links its ADR; open questions land in "Constraints and Risks" as explicit unknowns.

Completion criterion: every template section is either filled or marked intentionally blank with a one-line reason - there is no third state.

## Step 3 - Draft the Action Plan (init; refresh in reconcile)

Use this shape:

<action-plan-template>

# Action Plan - <system name>

> Resume point: Wave <k> - in flight: <slice ids or none> - blocked: <slice ids or none>
> Updated: YYYY-MM-DD

## Waves

### Wave 0 - Governance scaffolding
Directory skeleton, `architecture.toml` + `module.toml` skeletons, thin-wrapper governance tests, static-check baseline. This is `governed-arch`'s new-project workflow.

### Wave <n> - <name>
The slices in this wave, one line each saying what "done" means.

### Final wave - Integration testing
Cross-module integration happens here; within it, order follows `depends_on`: providers integrate before the consumers that import them.

## Serial constraints

Every must-be-serial pair states its reason: shared module - shared interface lock - undecided data contract - integration order. No stated reason, no constraint.

## Progress

The chapters above are the stable plan definition; this final table is the only progress record.

| ID  | Slice                  | Kind    | Wave | Status              | Notes                                     |
| --- | ---------------------- | ------- | ---- | ------------------- | ----------------------------------------- |
| S0  | governance scaffolding | scaffold| 0    | pending             | folders + TOML kit + thin-wrapper tests   |
| S1  | <module A>             | module  | 1    | pending             | spec: TBD                                 |

Status is one of `pending | in-progress | done (<ref>) | blocked (<reason>)`.

</action-plan-template>

Rules:

- **Waves carry the schedule; topology carries legality.** `depends_on` says who may import whom at runtime - it does not dictate construction order. Thanks to seams, an upper module can be built and unit-tested first against test doubles. Place modules in whichever wave serves delivery; reserve dependency reasoning for the integration wave.
- **Refer, don't duplicate.** Intra-feature step order belongs to `/to-spec` plus `/to-tickets` blocking DAGs; runtime import legality belongs to `architecture.toml`. This plan records only cross-slice edges.
- **Stable plan, live ledger.** `Waves` and `Serial constraints` are the plan definition and stay byte-stable; only the resume-point header and the final `Progress` table move.
- **Progress lives here.** The moment a slice starts, finishes, or blocks - in any session, by any agent - update its row in the final `Progress` table and the resume-point header in the same edit. A fresh session (human or agent) must be able to continue the project from this file alone: read the header, find the current wave in `Waves`, take the first non-done slice from the `Progress` table, follow its notes.

Completion criterion: every slice has a status; every serial edge has a stated reason; the header answers "where are we, what next" without reading anything else.

## Step 4 - Confirm, then write

Walk the user through the drafts one section at a time. On confirmation write `docs/architecture.md` and `docs/action-plan.md`. In reconcile / update-progress modes write diffs only.

## Step 5 - Hand off downstream

State what runs next: `governed-arch` executes Wave 0; features enter `/to-spec` -> `/to-tickets` in wave order; progress changes return here as **update-progress**; milestone checks arrive as **reconcile**.

## Write-back rules (reference)

- Durable conclusion learned during implementation -> new ADR via `/domain-modeling` first.
- An ADR changes a view's content -> sync the matching description section in the same session.
- Only status moved -> touch `action-plan.md` only.
- Reconcile finds drift between description and reality -> record it under "Constraints and Risks"; overturning a decision means a superseding ADR, never a silent edit.
