---
name: failsafe-loop
description: Breaks risky engineering work into explicit, gated steps with mandatory verification, artifact snapshots, and stop-on-diff rules. Use when the user asks to proceed phase by phase, wants every step tested before continuing, requires backtest or audit gates, or wants result comparisons after each change.
---

# Failsafe Loop

## Purpose

This skill is for high-risk or behavior-sensitive engineering work where correctness must be preserved through repeated gates instead of a single final test.

Use it for:
- refactors that must preserve behavior
- stability fixes mixed with structural cleanup
- backtest or simulation pipelines with expensive outputs
- tasks where the user explicitly wants “test -> run -> audit -> compare”
- work that must stop immediately on unexpected result drift

This skill assumes a project-specific profile at:
- `docs/agents/failsafe-loop-profile.md`

If that file does not exist:
- create `docs/agents/` if needed
- copy the template from this skill into `docs/agents/failsafe-loop-profile.md`
- fill in the project-specific commands and stop conditions before running the loop

## Step Planning

Before editing:
1. Define the exact step boundary.
2. Define the invariant for this step.
3. Locate or define the baseline artifact to compare against (see Step 0).
4. Define the output directory for this step.
5. Estimate expected runtime and mention any slow gate up front.

**Good step boundaries:**
- extract one module without changing behavior
- replace one shared mutable state mechanism
- fix one nondeterministic cache write path
- switch one adapter seam while preserving outputs

**Bad step boundaries:**
- “clean up the whole pipeline”
- “refactor step04/05/06 together”
- mixing correctness fixes with unrelated design cleanup

## Core Rules

- Keep only one active implementation step at a time.
- Do not batch multiple risky refactors into one gate.
- Always write artifacts to a fresh step-specific output directory.
- Prefer deterministic comparison artifacts over narrative judgment.
- If return, end_nav, trade count, pool diff, or other agreed invariants change unexpectedly, stop and report.
- If the user has already approved “no need to stop unless there is a real diff”, keep moving through successful gates without extra approval pauses.

## Mandatory Loop (Execution Steps)

### Step 0: Locate or Establish Baseline
Before making any code modifications, determine the comparison baseline:
1. Check [docs/agents/failsafe-loop-profile.md](docs/agents/failsafe-loop-profile.md) to see how baselines are resolved or where they are located.
2. **Critical Check**: Even if a baseline path is specified in the profile, **always ask the user to confirm if that baseline is still valid** (as the profile definition might be stale).
3. Ask the user if an existing prior run can be reused as the baseline (to save runtime on heavy pipelines).
4. If no valid or confirmed pre-existing baseline is available, run the workflow on unmodified code to generate and record the baseline.


### Iterative Process (For each step, execute in this order):
1. **Save snapshot:** (if the step is substantial, > ~50 lines, or multi-file)
2. **Implement:** Execute the current step ONLY.
3. **Run test gate:** See [docs/agents/failsafe-loop-profile.md](docs/agents/failsafe-loop-profile.md) for specific project test commands. If the profile explicitly marks this gate as `not_applicable`, skip it and report that choice.
4. **Run workflow gate:** Run the target workflow into a new step-specific output directory. If execution fails or crashes (e.g. traceback, syntax error), immediately stop and trigger **On-Stop Action** (do not run later gates). If the profile marks this gate as `not_applicable`, skip it and report that choice.
5. **Run audit gate:** Verify the results against project audit standards. If the profile marks this gate as `not_applicable`, skip it and report that choice.
6. **Compare against baseline:** Use machine-readable comparisons where possible. If the profile marks this gate as `not_applicable`, skip it and report that choice.
7. **Decide pass or stop:** Evaluate against stop conditions.
   - If **Pass**: Proceed to step 8.
   - If **Stop** (Validation fail or unexpected drift): Trigger **On-Stop Action**.
8. **Git commit:** If the decision is "pass", commit the changes with the structured format:
   `refactor(failsafe): stepXX - [step_name] passed all gates`

## On-Stop Action (Handling Gate Failures)
If a gate fails or an unexpected drift is detected:
1. **Pause & Analyze**: Do NOT automatically delete or revert code. Report the failure details and comparison diffs to the user.
2. **Resolve via Options**:
   - **Option A (Fix In-Place)**: Keep the dirty code in the workspace. Debug the issue, fix it, and rerun the gates of the current step.
   - **Option B (Stash & Restart)**: If the approach is fundamentally incorrect, save the current changes into a patch file (for example, `.scratch/failed_attempt_stepXX.patch`) to preserve the work, then only clean the working directory with explicit user approval before retrying the step.

## Reporting Rule (Required Deliverables)

After each successful step, report:
- Step name and scope (what changed)
- What commands passed
- Where outputs were written
- Where comparison artifacts were written
- Audit result / Clear pass/fail conclusion
- Whether any residual risk remains

If all gates pass and the user asked not to stop unnecessarily, proceed directly to the next planned step.
If any invariant changes unexpectedly, stop immediately and report before making more edits.

## Detailed Engineering Reference

For all specific project commands, tool paths, test standards, default configurations, and repo-specific notes, refer to:
[docs/agents/failsafe-loop-profile.md](docs/agents/failsafe-loop-profile.md)
