---
name: to-issues
description: Capture a bug report, small feature request, or standalone task as a permanent issue in the repo's global local-markdown issue stream (docs/issues/) — globally unique never-reused numbers, a Type line, a triage Status line, and a _summary.md index kept in sync on every change. Use when the user reports a bug, asks to track a small self-contained item, or wants to update or look up a previously filed issue. Not for decomposing an effort into slices — that is /to-tickets.
disable-model-invocation: true
---

# To Issues

Capture **issues** — bugs, small features, and tasks that arrive one at a time and live until they are resolved or rejected. Where `/to-tickets` decomposes one effort into temporary planning tickets under `.scratch/<feature-slug>/`, this skill maintains a single **permanent stream** under `docs/issues/`: every issue gets a globally unique number that is never reused or renumbered, and its file stays in the stream as history after it closes.

The issue tracker and triage label vocabulary should have been provided to you — run `/setup-matt-pocock-skills` if not.

## When to use this vs /to-tickets

- **/to-issues** — the item stands alone: a bug, a tiny feature, a chore. It needs no spec and no decomposition.
- **/to-tickets** — the item needs a spec and several coordinated vertical slices.

If an issue later grows into a real effort, leave the issue file in place, link it from the new spec, and let `/to-tickets` own the decomposition. The issue closes only when the shipped work actually resolves it.

## Process

### 1. Gather context

Work from whatever is already in the conversation context. If the user passes a reference (a path, a log excerpt, an error message), read it fully before writing.

### 2. Attempt a quick reproduction (bugs only)

When cheap, try to reproduce the reported behaviour before filing. Record the outcome in the issue body: confirmed (with the steps that worked), failed-to-reproduce, or insufficient detail — the last is a strong `needs-info` signal. Do not block filing on reproduction; capture the report now, verify during triage.

### 3. Write the issue file

Find the next number: scan `docs/issues/` for `<NNN>-*.md` and take the highest existing number plus one, zero-padded to three digits. Numbers are **globally unique across the whole stream**, never reused, never renumbered — even after an issue closes, its file keeps its number forever.

Write `docs/issues/<NNN>-<slug>.md` (short kebab-case slug), using the template below:

<local-issue-template>

# <NNN> — <Issue title>

**Type:** bug
**Status:** needs-triage
**Created:** YYYY-MM-DD

## Description

What is wrong (or wanted), stated once, precisely.

## Evidence

For bugs: exact error messages, stack traces, minimal reproduction steps, environment versions — whatever a future reader needs to diagnose without this conversation. For features/tasks: motivation and the desired outcome.

## Comments

Appended over time: triage notes, findings, the resolving commit, links to absorbing issues.

</local-issue-template>

Unlike tickets, **do keep concrete evidence** — stack traces, logs, repro snippets, version strings do not go stale the way implementation plans do, and issues are often diagnosed months later, detached from the original conversation. Trim noise, but err on the side of preserving the diagnostic trail.

### 4. Refresh `_summary.md`

`_summary.md` is the overview layer of the stream and the first thing to read for the current picture; the per-issue files are the source of detail. Refresh it on **every** add, state change, and close. It is a **single append-only table**: rows sit in number order and never move — adding an issue appends one row at the end, and every lifecycle event edits cells **in place**. The `Open:` counter line is the quick current picture; scan the `Status` column for the live set:

<summary-template>

# Issues overview

Open: N — bugs X, features Y, tasks Z

| #   | Title         | Type    | Status       | Ref             |
| --- | ------------- | ------- | ------------ | --------------- |
| 001 | Example title | bug     | fixed        | fixed (abc1234) |
| 003 | Example title | feature | needs-triage |                 |

</summary-template>

- The `Ref` cell stays empty while the issue is open; on close it carries the outcome — `fixed (<commit>)`, or `wontfix (→ #NNN)` when the issue is a duplicate absorbed by another.
- Because rows never migrate, updates are always single-row in-place edits; the only structural operation in the whole file is appending.

### 5. Lifecycle

`Status:` uses the five canonical triage roles (see `docs/agents/triage-labels.md`) plus one terminal state:

```
needs-triage ──▶ needs-info ──▶ needs-triage      (questions answered)
     │
     ├─▶ ready-for-agent ──▶ fixed                (agent brief; fix landed)
     ├─▶ ready-for-human ──▶ fixed                (human-judgment or manual step)
     └─▶ wontfix                                   (reachable from any state)
```

- **fixed** — the resolving change landed. Append a closing comment with the commit reference, then update the issue's row in `_summary.md` in place: set `Status: fixed` and fill its `Ref` cell. The file itself stays in the stream permanently.
- **duplicate** — not its own state: close as `wontfix` and append a comment pointing at the issue that absorbs it; record `wontfix (→ #NNN)` in the row's `Ref` cell.
- **needs-info** — list the missing answers as explicit questions in a comment so the reporter can answer point by point.

### 6. Execute and close

A `ready-for-agent` issue is its own agent brief: the agent reads the issue file and its comments, does the work, and appends the outcome. When the fix lands, set `Status: fixed`, reference the commit, refresh `_summary.md`. A `ready-for-human` issue carries the same structure plus a note on why it cannot be delegated.
