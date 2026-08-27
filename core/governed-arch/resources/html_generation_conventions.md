# HTML Generation Conventions

This document explains how governed architecture HTML docs are produced and how they should be used.

## Purpose

Generated HTML is for:

- reviewing design intent
- inspecting dependencies visually
- reading public interface contracts
- surfacing red-line invariants

It is not the primary source of truth.

The primary source of truth remains:

- `architecture.toml`
- `module.toml`
- the governed test suite

## Default Inputs

The diagram generator reads:

- `architecture.toml` at the project root
- every discovered `module.toml`

## Default Outputs

The default output directory is:

- `docs/html/governed-arch/`

Typical generated files:

- `docs/html/governed-arch/architecture-full.html`
- `docs/html/governed-arch/<module>.html`

The `governed-arch` subdirectory keeps generated architecture reports
namespaced apart from other HTML docs produced in the same project
(e.g. a project's own `docs/html/`).

## What the Generator Should Render

At minimum, generated docs should include:

- top-level module dependency graph
- per-module internal structure
- per-module external dependencies
- public API and interface contracts
- invariant lists

## Update Timing

Re-generate HTML docs whenever any of the following change:

- `architecture.toml`
- any `module.toml`
- any `interface_lock` spec
- invariant declarations that should be reflected in docs

## Editing Policy

Do not hand-edit generated HTML as if it were source architecture documentation.

If a rendered contract or diagram is wrong, fix one of:

- governance TOML
- the diagram generation script
- the governed source code

then generate the docs again.

## Core Flows & Algorithms (`[[design.flows]]`)

Optional structured chapter rendered on per-module pages after the
architecture diagram and before the governed interface contracts.

Declared in `[design].flows` inside a `module.toml`; each block picks its
rendering with `kind`:

- `flow` — a Mermaid `flowchart TD`; steps become sequential nodes.
- `gates` — an HTML table with numbered gate badges.
- `priority` — an HTML table with priority badges (P0–P3).
- `principles` — card-style definition entries.

Cross-references:

- `ref` values render as hyperlinks to the matching interface-contract anchor.
- `invariant` / `constraint` values render as hyperlinks to the
  semantic-invariant anchor (`id="invariant-<id>"`).

Modules that do not declare `[design]` render exactly as before; the chapter
is purely additive.

## Styling Policy

Compact, high-density output is acceptable and often preferable for architecture reports.

However, readability still matters:

- labels should remain legible when diagrams shrink
- tables should favor scanning over decoration
- layout should support both overview and detail sections
