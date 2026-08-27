# Issue tracker: Dual-stream Local Markdown

This repo tracks work items as markdown files in **two separate streams**. Skills read this file to know where their output belongs.

> **Maintenance note**: this file is hand-maintained and intentionally diverges from the single-stream seed templates embedded in `/setup-matt-pocock-skills`. If that skill is re-run in this repo, keep this file instead of regenerating it from `issue-tracker-local.md`.

|                  | Tickets                                | Issues                            |
| ---------------- | -------------------------------------- | --------------------------------- |
| Produced by      | `/to-tickets`, `/wayfinder`            | `/to-issues`                      |
| Location         | `.scratch/<feature-slug>/`             | `docs/issues/`                    |
| Lifetime         | Temporary — planning scaffold          | Permanent — long-lived ledger     |
| Numbering        | Per-effort, from `01`, dependency order | Global, from `001`, time order    |
| Index            | none                                   | `_summary.md` (global, kept in sync) |

## Stream 1 — Tickets (temporary)

Tracer-bullet slices of **one effort**, deleted when the effort ships.

- One effort per directory: `.scratch/<feature-slug>/`
- The spec is `.scratch/<feature-slug>/spec.md`
- Tickets are one file each at `.scratch/<feature-slug>/tickets/<NN>-<slug>.md`, numbered from `01` in dependency order (blockers first), never a single combined file
- Each ticket declares its blockers via a `Blocked by:` line; triage state is a `Status:` line near the top (see `triage-labels.md`)
- Comments append under a `## Comments` heading

### Wayfinding operations (`/wayfinder`)

The **map** is `.scratch/<effort>/map.md` (Notes / Decisions-so-far / Fog body); **child tickets** are `.scratch/<effort>/tickets/NN-<slug>.md` with the question in the body. A `Type:` line records the ticket type (`research`/`prototype`/`grilling`/`task`); a `Status:` line records `claimed`/`resolved`. A ticket is unblocked when every file in its `Blocked by:` list is `resolved`. Frontier scan: open, unblocked, unclaimed — first by number wins. Claim before working (`Status: claimed`); resolve by appending an `## Answer` and adding a context pointer to the map's Decisions-so-far.

## Stream 2 — Issues (permanent)

Bugs, small features, and standalone tasks that arrive one at a time. The stream is **append-only history**: closed issues keep their files forever.

- Single global directory: `docs/issues/`
- One issue per file: `<NNN>-<slug>.md`, three-digit zero-padded, globally incrementing, **never reused or renumbered**
- Body carries `Type: bug | feature | task`, `Status:`, and `Created:` lines near the top
- Status vocabulary: the five canonical triage roles plus terminal `fixed`; duplicates close as `wontfix` with a pointer comment
- Evidence is welcome here — stack traces, logs, repro steps, version strings (issues are diagnosed long after the original conversation)
- `docs/issues/_summary.md` is the overview layer: refresh it on every add, state change, and close; read it first for the current picture

## Routing rule

- Item needs a spec and multiple coordinated slices → `/to-tickets` → Stream 1
- Item stands alone (bug, tiny feature, chore) → `/to-issues` → Stream 2
- An issue that grows into an effort keeps its file; link it from the new spec in `.scratch/`

## Triage

The `/triage` skill operates on both streams. Label strings are the canonical five roles recorded in `triage-labels.md`.
