---
name: impl-loop
description: End-to-end delivery loop that drives a feature from spec to done by chaining /to-spec -> /to-tickets -> /implement -> test gates, ticket by ticket. impl-loop is the cross-slice engine (progress, gates, resume); the existing implement skill stays the single-slice executor (it calls /tdd and /code-review internally). Use when the user wants the whole delivery cycle run or an in-flight effort continued.
argument-hint: "[<feature-slug>] - omit to auto-detect"
---

# Impl Loop

## Purpose and boundary

`impl-loop` orchestrates the delivery loop across stages and slices:

```text
/to-spec  ->  /to-tickets  ->  [ per ticket: /implement  ->  test gate ]  ->  done
```

It is **not** a reimplementation of `implement`. The division of labor is fixed:

| Skill       | Owns                                                        |
| ----------- | ----------------------------------------------------------- |
| `impl-loop` | cross-slice progress, gate enforcement, resume, hand-offs   |
| `implement` | one ticket's build: `/tdd` where possible, `/code-review`, commit |
| `to-arch`   | the test strategy itself, declared in the two blueprints    |

impl-loop never decides *which* test layer to run and never re-runs `/code-review` - `implement` already reviews internally.

## Inputs (preconditions)

Before looping, locate these. If an artifact is missing, **actively execute the corresponding skill workflow** (via its skill or SOP) rather than halting or asking the user to type slash commands:

| Artifact                          | Missing? Active Action                                    |
| --------------------------------- | --------------------------------------------------------- |
| `.scratch/<slug>/spec.md`         | Actively run `to-spec` workflow to draft and publish spec |
| `.scratch/<slug>/tickets/NN-*.md` | Actively run `to-tickets` workflow to draft ticket DAG    |
| `docs/action-plan.md` (test gates)| Actively run `to-arch` (init/reconcile)                   |

If the user names no `<feature-slug>`, auto-detect: one open effort directory under `.scratch/` wins; multiple or none -> ask.

## The test gate (core rule)

The gate for a finished ticket is **declared upstream**, not chosen here. Resolve in this order:

1. The ticket's wave/slice row in `docs/action-plan.md` - its declared test gate (spec `<id>`, test layer, verify command - unit / integration / system, from `CONTEXT.md`'s vocabulary).
2. The test architecture layout in `docs/architecture.md` (`# 7. Test Architecture`: which layer the touched module belongs to, tools, directory conventions, overrides).
3. Neither covers the current ticket -> **stop and align with `to-arch`** (or the user). Never invent a gate.

Rationale: only `to-arch` knows the step design, so only it knows what test strength each step can reach by its end. The layers are grain-scoped (unit → one ticket, integration → one spec, system → two+ specs), so later steps gate on stronger tests - typically unit early, integration when a spec's tickets complete, system in the final wave for a multi-spec effort.

## The loop

For each ticket in `tickets/` in dependency order (blockers first, skip `Status: resolved`/`fixed`):

1. **Claim** - set the ticket's `Status:` to `claimed` (in-progress equivalent per the issue-tracker conventions).
2. **Implement** - actively execute the `implement` workflow for this ticket:
   - Implement at pre-agreed seams using TDD (`/tdd`, red-green-refactor)
   - Run type checks and the ticket's unit test suite
   - Run `/code-review` before commit
   - Commit the ticket's work to the branch.
   Inside the loop, `implement` stops at the unit test suite; do not let it run heavier suites alone.
3. **Gate** - run the resolved test gate (see above) on top of the unit tests `implement` already ran. All declared layers must pass.
   - **Pass** -> mark the ticket `resolved`, append a one-line `## Answer`/comment pointing at the commit, update the slice's row in `docs/action-plan.md`'s Progress table and the resume-point header in the same edit (`to-arch` update-progress semantics), then continue to the next ticket.
   - **Fail** -> bounded retry: attempt a fix via `implement` feedback once; if the gate still fails, stop the loop, report the failing gate and ticket, and leave the ticket `claimed` with a comment and suggested remediation (e.g. `/improve-codebase-architecture` if seam is flawed, or `/grill-with-docs` if requirements conflict).
4. **Spec completion gate** - after the last ticket of the spec, run the **integration test** for this spec (per `action-plan.md`): verify the contracts across this spec's tickets plus this spec's acceptance criteria. A single run of `impl-loop` closes **one spec**. If the effort spans two or more specs, an external **system test** gate sits in the final wave of `action-plan.md` (cross-spec / whole-effort) - not inside this run, and owned by `to-arch`'s plan.

One ticket in flight at a time. Do not batch tickets into one gate.

## Resume semantics

`impl-loop` is resumable by design. On entry, read `docs/action-plan.md`'s resume-point header and the tickets' `Status:` lines, take the first open unblocked ticket, and continue the loop from step 1. Every gate pass updates the Progress table, so any fresh session can resume from the plan alone.

## On completion

When the spec's tickets are all `resolved` and its **integration gate** passes (and, where the plan declares one for this run, the system gate):

1. **Update the slice row in `docs/action-plan.md`** (applying `to-arch` update-progress semantics):
   - Set `Status` to `done (<final_commit_sha>)`
   - Update `Notes` to `all <N> tickets resolved, integration gate passed (<gate_command>)`
2. **Advance the resume-point header in `docs/action-plan.md`**:
   - If other slices in the current Wave remain in-flight or pending, refresh the in-flight/blocked list
   - If all slices in the current Wave are done, advance the header to `Resume point: Wave <k+1>`
   - If all Waves (including the Final Wave system integration) have completed, mark `Effort complete`
3. **Summarize and retire scaffolding**:
   - Summarize tickets delivered, commits made, gates passed (with exact commands)
   - The effort directory `.scratch/<slug>/` may now be retired per the issue-tracker rules (deleted when the effort ships).
