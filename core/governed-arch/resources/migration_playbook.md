# Migration Playbook

This playbook describes how to apply governed-arch to a project.

## Scenario A: New Project Initialization

Use this path when the project is still forming and you want governance from the start.

### Recommended Order

1. Create `architecture.toml`
2. Register top-level governed modules in `submodules`
3. Create each governed module directory
4. Add `module.toml` to each governed module
5. Register the direct-child inventory in `module.submodules`
6. Add `[submodule.*]` only for real direct children
7. Add `__init__.py` and declare `__all__` where public API exists
8. Add the governance tests under `tests/`
9. Add `scripts/generate_diagrams.py`
10. Run tests
11. Generate HTML docs

### Good Default Strategy

Start with:

- a small number of top-level modules
- simple `depends_on` declarations
- only the most important public APIs locked
- only the most important invariants declared

Then tighten the system gradually.

## Scenario B: Existing Project Retrofit

Use this path when the repository already exists and governance must be introduced incrementally.

### Recommended Order

1. Inventory the real top-level modules already present
2. Create `architecture.toml` from the current structure
3. Add `module.toml` module by module
4. Register each module's real direct-child inventory in `module.submodules`
5. Remove orphan and phantom child declarations before tightening dependency rules
6. Introduce the governance test suite
7. Run the tests and accept that the first run may expose many mismatches
8. Fix structure drift before adding more rules (e.g., move source files from root to governed modules)
9. Add `public_api` and `__all__` alignment
10. Add interface locks for the truly exposed APIs
11. Add module-local invariants only after structure is stable
12. Generate HTML docs as a readable review artifact

### Retrofit Rule

Do not try to encode every architectural wish immediately.

Prefer this order:

- capture reality
- stabilize `module.submodules` inventory
- stabilize boundaries
- lock public contracts
- add stricter invariants later

### Inventory First Rule

Do not start by writing dependency rules against incomplete metadata.

Fix these classes of drift first:

- **orphan child**: exists on disk but missing from `module.submodules`
- **phantom child**: declared in `module.submodules` or `[submodule.*]` but missing on disk
- **owner ambiguity**: a governed `.py` file is not clearly attributable to one deepest owner

Only after the inventory is clean should you tighten `internal_depends` and `external_depends`.

## When to Use This Skill

Use governed-arch when the task involves:

- creating a new governed module
- splitting a module or directory
- introducing or changing public interfaces
- adding architecture contracts or invariants
- making module boundaries explicit and testable

## When Not to Use It

Do not force this skill onto:

- tiny throwaway scripts
- repositories with no meaningful module boundaries
- one-off edits that do not touch architecture, module structure, or public contracts

## Migration Success Criteria

The migration is in a good state when:

- governed modules are all registered
- `module.toml` files exist where expected
- `module.submodules` matches the real direct-child inventory
- orphan and phantom children are eliminated
- boundary and contract tests pass
- exposed APIs are intentionally declared
- HTML docs can be generated from TOML without manual patching
