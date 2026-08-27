# Architecture Conventions

This document explains the core conventions behind the governed-arch skill.

## Purpose

The goal of this governance model is to make architecture explicit, reviewable, testable, and documentable from files that live inside the repository.

The core idea is:

- `architecture.toml` governs top-level modules and global rules
- each module directory owns a `module.toml`
- `public_api`, `interface_lock`, and invariants are enforced by tests
- HTML documentation is generated from TOML rather than handwritten drift-prone docs

## Governance Layers

The governance stack is intentionally split into four non-overlapping layers:

- **Layer 1: Public Surface**
  - `test_interface_contracts.py`
  - enforces exposed API declaration, lock existence, and signature stability
- **Layer 2: Cross-Federation Access**
  - `test_interface_contracts.py::test_cross_module_from_imports_in_exposed`
  - enforces Gateway-Only Import through deepest-owner resolution
- **Layer 3: Intra-Federation Dependency Graph**
  - `test_module_boundaries.py::test_submodule_boundaries`
  - enforces actual same-federation vs cross-federation dependency categories
- **Layer 4: Metadata Integrity**
  - `test_module_boundaries.py`
  - enforces direct-child inventory, orphan/phantom detection, and deepest-owner uniqueness

The key rule is simple: one policy dimension should have one owner. A coarse top-level import check must not duplicate GOI.

### Root Layer

`architecture.toml` is the top-level manifest.

Use it to declare:

- top-level governed modules
- cross-module dependencies
- optional global interface locks
- optional global invariants
- optional exception and path policies

**Root Cleanliness Rule**:
The project root is a **code-free zone**. No `.py` files are allowed. All source code and functional scripts must be organized into governed modules or appropriate subdirectories (e.g., `tests/`, `scripts/`). Only non-executable configuration files (like `architecture.toml`, `pyproject.toml`, `.gitignore`) may reside at the root.

### Module Layer

Each governed module owns one `module.toml`.

Use it to declare:

- module responsibility
- direct children via `submodules`
- internal dependency rules via `[submodule.*]`
- public API via `[public_api]`
- local interface locks
- local invariants

### Direct-Child Inventory Terms

- **Direct child inventory**: the real direct child files and directories under a governed module directory, excluding governance infrastructure like `module.toml`, `__init__.py`, and ignored infrastructure directories.
- **Orphan child**: a real direct child that exists on disk but is missing from `module.submodules`.
- **Phantom child**: a `module.submodules` entry or `[submodule.*]` declaration that points to a missing child.
- **Deepest owner**: the most specific directory on a path that owns a `module.toml`. Every governed `.py` file must have exactly one deepest owner.

`module.submodules` is therefore the inventory layer. `[submodule.*]` is the dependency contract layer. The two are related, but they are not interchangeable.

### Code Layer

Code must match the governance metadata:

- `public_api.exposed` must match `__all__`
- locked functions must exist
- locked signatures must match the declared specs
- imports must respect declared dependency rules
- cross-module imports must use the facade form (Gateway-Only Import, recursive)

## Public API Rules

`Expose is Lock` is the default rule:

- if a symbol is exposed for other modules to consume, it must be intentionally declared
- if it is intentionally declared, it should have a matching contract
- contract changes should be deliberate and reviewable

## Import Governance (Gateway-Only Import)

The governance boundary for imports is the federated module — any directory owning a `module.toml` — applied recursively. Nested modules with their own `module.toml` are independent gateways.

### Why the facade form

The facade form is semantics, not cosmetics: `from pkg.dag import ExecPool` lets `pkg/dag` rename, split, or move its internal files freely, while `from pkg.dag.task import Task` welds the consumer to an internal file layout.

### Ownership resolution

Checkers resolve ownership — the deepest directory on the path that owns a `module.toml` — rather than string prefixes:

```python
owner_of(path)   # deepest directory on the path that owns a module.toml
C = owner_of(consumer_file)
O = owner_of(import_target)
# C == O → intra-module: GOI exempt, test_module_boundaries.py governs target legality
# C != O → cross-module: the from-path must equal O and every name must be in O.exposed
```

Examples:

- `from pkg.dag import ExecPool` issued from `pkg/continuous/` is legal: the target's owner is `pkg/dag`, the from-path is exactly that facade, and `ExecPool` is exposed there.
- `from pkg.dag.task import Task` issued from **outside** `pkg/dag` is a facade bypass — even if `Task` is listed in `pkg/dag.exposed`.
- The same deep import issued from **inside** `pkg/dag` is intra-module and legal.

### Facades are load-bearing

Facade `__init__.py` files are built with deep imports (`from .x import ...`). Module-internal files must therefore never import through their own facade — doing so creates a circular import. The `__init__.py` exemption in GOI checks is a structural requirement, not an accidental special case.

### Format floors

- No `from x import *`.
- No cross-module `import X.Y` module-object imports.
- Relative imports are reserved for facade `__init__.py` files (this also keeps AST checkers free of `node.level` handling).
- Style-only concerns (import sorting, grouping) belong to isort/ruff, not to governance tests.
- Governance tests never replace the static-check stack (ruff + mypy + the `code-review` skill): they enforce structure and contracts, while ruff/mypy enforce style and type safety and `code-review` provides holistic review. The *static check tool configuration* itself (ruff + mypy blocks in `pyproject.toml`) is part of the governance kit's baseline — it is the **default defense line** for a governed project, established in both new-project initialization (§8.1 step 9) and existing-project retrofit (§8.2 step 9) via `templates/pyproject_ruff_mypy.toml`. The same steps verify the `code-review` skill is installed so the full stack (ruff + mypy + code-review) is in place. Missing infrastructure is created proactively, not merely reported. Governance tests remain agnostic to which style tools a project runs in CI.

## Invariant Rules

Use invariants for red-line rules that must not silently drift.

Good invariant examples:

- a governed module must not import an internal layer directly
- a generated artifact must always be written atomically
- an exposed API must keep a compatible signature

Avoid putting project-private business cases into the shared skill unless they are rewritten as generic patterns.

## Managed Storage Ownership (Abstract Rule)

The skill provides a generic data-access rule: storage resources are owned by declared modules, and data access is funneled through the owner — the storage twin of Gateway-Only Import. A project reserves certain directory identities as managed storage zones (offline data roots, caches, config stores, ...); only the modules declared as owners of a zone may reference its names.

The rule is declarative and project-agnostic:

```toml
[managed_storage.<zone_name>]
names  = ["<directory name>", ...]
owners = ["<module>", ...]
```

- `names` — the zone's directory-name identities. A reference means the name appears as an exact path component in a string literal (split on both `/` and `\`). No regex is involved, so declarations cannot introduce escaping bugs and name collisions cannot produce false matches.
- `owners` — governed modules permitted to reference the zone by name. Everyone else must obtain such paths through the owner's public facade.

Enforcement lives in `test_module_boundaries.py::test_storage_zone_references_respect_ownership`. It is skipped when no `[managed_storage.*]` is declared.

Only the mechanism is shared. Concrete directory names and owner lists are per-project configuration in `architecture.toml`; never embed a specific project's storage conventions into the skill code or docs — examples in the skill always use neutral vocabulary.

## Test Suite Roles

The standard governance test suite has four required layers:

- `test_module_boundaries.py`
  checks metadata integrity, direct-child inventory, and submodule dependency categories
- `test_interface_contracts.py`
  checks `public_api`, interface locks, signatures, invariant `test_ref` bindings, and Gateway-Only Import
- `test_architecture_kit_complete.py`
  checks that governed modules have the expected governance kit
- `tests/<module>/test_invariants.py`
  keeps project-local red-line rules near the governed module

## Documentation Rules

Generated HTML docs are derived from TOML governance files.

The intended source of truth is:

- TOML for structure and contracts
- tests for enforcement
- generated HTML for readable design intent

Do not treat generated HTML as the primary editable architecture source.

## Structural vs Semantic Governance

Layers 1–5 verify *shape*: surface declarations, gateway imports, dependency
categories, inventories, storage ownership. They are blind to business
semantics — "period windows tile time without overlap", "state handed over at
stage N equals state consumed at stage N+1", "locally reported returns compose
into the published global return". A refactor can pass every structural check
while silently breaking such contracts; the regression surfaces only through
manual audit, weeks later.

Discipline for semantic contracts:

1. Register each red line as an `[[invariant.<domain>.rules]]` entry with a
   precise `id`, an operational `desc`, and a `test_ref` pointing at a real
   **runtime** guard over real artifacts (not a static scan, not a vacuous
   assert over synthetic placeholders only).
2. Mutation-check the guard once: temporarily break the production behavior it
   protects and confirm the bound test fails. A guard that cannot fail guards
   nothing.
3. Mark modules that own such contracts with `[module] require_invariants = true`;
   `test_required_invariant_coverage` then fails if every binding is removed.
4. Meta-guards keep bindings alive: `test_invariant_test_refs_exist` rejects
   deleted tests, skip-short-circuited tests, and hollow (assert-free) bodies.
5. Prefer reusable shapes from `templates/test_semantic_guards.py`
   (tiling contiguity, disjoint report bars, telescoping composition).
