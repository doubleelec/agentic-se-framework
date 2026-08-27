---
name: governed-arch
description: Guidelines, methodology, and templates for recursive architecture governance. Unified TOML-based Architecture-as-Code system using architecture.toml and module.toml.
---

# Governed Architecture Skill

This skill enforces a TOML-based **Architecture-as-Code governance system** when creating, refactoring, splitting, or auditing modules. Use it for repositories that want explicit module boundaries, locked public contracts, generated architecture docs, and automated governance tests.

---

## 1. Core Principles

1. **TOML is the governance source of truth** — Architecture structure, module boundaries, public contracts, and invariants are declared in TOML files inside the repository.
2. **Architecture-as-Code** — The project structure is defined by `architecture.toml` at the root and `module.toml` in governed module directories, and enforced by tests.
3. **Recursive federated discovery** — Governed modules are discovered recursively through declared `submodules`, not by informal convention alone.
4. **Expose is Lock** — Every intentionally exposed API should be declared and governed as a contract.
5. **Gateway-Only Import (GOI)** — Cross-module imports must go through the owning federated module's public facade, applied recursively. Intra-module imports are exempt. See Section 4.
6. **Generated docs express design intent** — HTML architecture docs are generated from TOML governance files rather than maintained by hand.
7. **Root Cleanliness** — Project root is a code-free zone. No `.py` files are allowed; all code must reside within governed modules or designated subdirectories.
8. **Static checks are the default defense line** — the static-check stack for a governed project is **ruff (style/import hygiene) + mypy (type safety) + the `code-review` skill (holistic review)**, not a new-project-only nicety. Every governed project — new or retrofitted — is expected to run them. When establishing the static-check baseline, verify the `code-review` skill is installed alongside ruff and mypy. When the user asks for a "static check", run all three — ruff + mypy + `code-review` — rather than stopping at the tooling. If any part of the infrastructure is missing, establish it proactively rather than merely flagging its absence.

---

## 2. The Governance Hierarchy

```
architecture.toml             submodules = [...]                        ← Top-level Discovery
                              [module."<name>"].depends_on              ← Cross-module Deps
                              [module."<name>"].external_depends        ← Cross-module Deps (Explicit)
                              [module."<name>"].internal_depends        ← Same-module Siblings
                              [invariant.<domain>.rules]                ← Global Rules / Red Lines
   │
   └── <dir>/module.toml      [module]                                  ← Local Metadata (Responsibility/Flow)
                              require_invariants                        ← Critical-Semantics Flag (opt-in)
                              submodules = [...]                        ← Submodule Discovery
                              [submodule."<child>"].depends_on          ← Intra-module Deps (Legacy)
                              [submodule."<child>"].internal_depends    ← Same-module Siblings
                              [submodule."<child>"].external_depends    ← Cross-module Gateways
                              [public_api].exposed                      ← Public Surface
                              [interface_lock."<file>.py".specs."Fn"]   ← Signature Specs
                              [[invariant.<domain>.rules]]              ← Local Rules
   │
   └── <dir>/__init__.py      __all__ = [...]                            ← Dual Declaration
```

---

## 3. Module Metadata Standards

Every governed module should own a `module.toml` that describes:

- **`[module]` block**:
  - `name`: Relative module directory path (e.g. `"backtest/dag"`).
  - `description`: Detailed responsibility description.
  - `submodules`: The direct-child inventory of the module. Every real direct child file or directory that belongs to the governed structure must be listed here.
  - `consumers`: Downstream consumers and use cases.
  - `data_flow`: Detailed description of data inputs, processing logic, and outputs.
- **`require_invariants`** (optional): set to `true` for modules that own semantic red lines (windowing/partitioning, cross-stage handover, aggregation identities). Enforced by `test_required_invariant_coverage`: the module must declare at least one invariant rule carrying a non-empty `test_ref`, so removing every binding fails governance instead of passing silently.
- **Direct-child inventory rules**:
  - `module.submodules` is the discovery inventory, not the dependency contract.
  - An **orphan child** is a real direct child that exists on disk but is missing from `module.submodules`.
  - A **phantom child** is a declared child or `[submodule.*]` rule target that does not exist on disk.
  - A **deepest owner** is the most specific directory on a path that owns a `module.toml`; every governed `.py` file must belong to exactly one deepest owner.
- **`[public_api]` block**:
  - `exposed`: List of public classes, enums, or functions exported by `__init__.py`'s `__all__`.
  - `reason`: Design intent for exposing these specific APIs.
- **`[submodule.*]` block**:
  - This is the local dependency contract layer for direct children already listed in `module.submodules`.
  - `internal_depends` governs same-federation targets.
  - `external_depends` governs cross-federation targets.
  - `depends_on` remains supported as a legacy compatibility allowlist, but new projects should prefer the explicit split.
- **`[interface_lock]` specs**:
  - Every exposed name must have detailed specs. For classes, constructors (`Class.__init__`) and public methods (`Class.method`) are listed in `locked_functions` and specified under `specs` with `params`, `returns`, and `description`.
  - The diagram generator groups class methods under the parent class contract, rendering the class description in the main table and method parameters in the details section.
- **`[[invariant.*.rules]]`**:
  - `id`: Unique invariant ID.
  - `desc`: Detailed description of the rule or red-line constraint.
  - `test_ref`: Link to the automated test enforcing this constraint. Binding quality is meta-enforced by `test_interface_contracts.py::test_invariant_test_refs_exist`: the referenced test must exist, must not be short-circuited by skip decorators or an unconditional runtime `pytest.skip`, and must be non-hollow (its body contains at least one assert / raise / call — pure `pass` or docstring-only bodies are rejected).

---

## 4. Import Governance (Gateway-Only Import)

1. **Cross-module imports use the facade form**: `from <owner> import name`, where `<owner>` is the federated module owning the target file and `name` is in its `[public_api].exposed`. Any deeper path (`from <owner>.<internal> import ...`) is a facade bypass — even when the name is exposed.
2. **Ownership determines scope**: if the consumer file and the import target belong to the same federated module, the import is intra-module — GOI does not apply; `[submodule.*].depends_on` governs target legality.
3. **Never import through your own facade**: facade `__init__.py` files are built with deep imports, so a module-internal file importing its own facade causes a circular import. `__init__.py` files are exempt from GOI checks.
4. **Format floors**: no `from x import *`; no cross-module `import X.Y` module-object imports; relative imports are reserved for facade `__init__.py` files. Import style (sorting, grouping) belongs to isort/ruff, not to governance tests.

For the reasoning and examples behind these rules, see `resources/architecture_conventions.md`.

---

## 5. Governance Layers

The governance stack is intentionally split by policy ownership:

1. **Layer 1 — Public Surface**
   - owned by `test_interface_contracts.py`
   - enforces `public_api.exposed == __all__`, interface lock existence, and signature specs
2. **Layer 2 — Cross-Federation Access**
   - owned by `test_interface_contracts.py::test_cross_module_from_imports_in_exposed`
   - enforces GOI using deepest-owner resolution
3. **Layer 3 — Intra-Federation Dependency Graph**
   - owned by `test_module_boundaries.py::test_submodule_boundaries`
   - enforces actual import category vs `internal_depends` / `external_depends`
4. **Layer 4 — Metadata Integrity**
   - owned by `test_module_boundaries.py`
   - enforces direct-child inventory, orphan/phantom detection, and deepest-owner uniqueness

5. **Layer 5 (Optional) — Managed Storage Ownership**
   - owned by `test_module_boundaries.py::test_storage_zone_references_respect_ownership`
   - enforces that a managed storage zone (offline data root, cache, config store) is referenced by name only inside its declared owner modules — the storage twin of Gateway-Only Import
   - fully declarative via `[managed_storage.*]`: see Section 6.4

6. **Layer 6 — Semantic Red-Line Binding**
   - owned by `test_interface_contracts.py::test_invariant_test_refs_exist` and `test_module_boundaries.py::test_required_invariant_coverage`
   - enforces binding quality of `[[invariant.*.rules]]` (referenced test exists, never skipped, non-hollow) and opt-in coverage for critical modules via `[module].require_invariants = true`

**Why Layer 6 exists**: Layers 1–5 verify *shape*; they are blind to business semantics (window tiling, cross-stage handover, aggregation identities). A refactor can satisfy every structural check while silently breaking such contracts. Modules owning these semantics must register red lines bound to runtime guard tests and flag themselves with `require_invariants`; see `resources/architecture_conventions.md` ("Structural vs Semantic Governance") for the registration discipline.

This split is important: cross-federation gateway shape should not be duplicated by a second coarse top-level import check.

---

## 6. Global Infrastructure

### 6.1 Governance Files

The standard governance kit consists of:

- `architecture.toml` at the project root
- `module.toml` in each governed module directory
- `__init__.py` with `__all__` where public APIs are intentionally exported

### 6.2 Test Infrastructure (`tests/`)

Governance tests are now provided as a global library in the skill's `core/` directory. Projects should **not** maintain local copies of these scripts. Instead, they should create a Thin Wrapper to delegate execution to the global skill.

**Example `tests/test_governance.py`:**
```python
import sys
from pathlib import Path

SKILL_DIR = Path.home() / "<skills-dir>" / "governed-arch" / "core"  # your agent's skills directory
if not SKILL_DIR.exists():
    raise RuntimeError(f"Governance skill not found at {SKILL_DIR}")

sys.path.insert(0, str(SKILL_DIR))

# Import all generic governance tests
from test_interface_contracts import *
from test_module_boundaries import *
from test_architecture_kit_complete import *

# (Optional) Expose specific test functions if needed by your test_ref invariants
from test_interface_contracts import test_cross_module_from_imports_in_exposed as _test_cross_module
def test_cross_module_from_imports_in_exposed():
    return _test_cross_module()
```

| Test | What it enforces |
|:---|:---|
| `test_module_boundaries.py` | direct-child inventory integrity, orphan/phantom detection, deepest-owner safety, intra-federation dependency categories, (optional) declarative managed-storage ownership, and opt-in critical-module invariant coverage (`require_invariants`) |
| `test_interface_contracts.py` | `__all__` consistency, signature locking (Specs parameters/defaults), invariant ref binding quality (existence + anti-skip + anti-hollow), and Gateway-Only Import (recursive facade resolution) |
| `test_architecture_kit_complete.py` | ensures each declared module at `<path>` has a `module.toml` and a mirrored test directory at `tests/<path>/` |
| `tests/<module>/test_invariants.py` | (Local) module-local red-line rules, these are kept in the project. |

### 6.4 Optional: Managed Storage Ownership (Declarative)

The skill provides an **abstract data-access rule**: storage resources are owned by declared modules, and data access is funneled through the owner — the storage twin of Gateway-Only Import. A project declares each managed storage zone — a directory identity it reserves for managed data (offline roots, caches, config stores, ...) — together with the modules that own it:

```toml
# Managed storage zones (optional). Neutral example only.
# Each zone: `names` = directory names (exact path-component match, no regex);
#            `owners` = governed modules allowed to reference the zone by name.
[managed_storage.media_assets]
names  = ["media", ".media"]
owners = ["assets/provider", "assets/ingest"]

[managed_storage.session_cache]
names  = [".cache", "cache"]
owners = ["core/cache"]
```

- `names` — the zone's directory-name identities; a reference is an exact path component in a string literal (split on `/` and `\`). No regex is involved: declarations cannot introduce escaping bugs, and name collisions cannot produce false matches.
- `owners` — the governed modules that own the zone and may reference it by name. Everyone else must obtain paths through the owner's public facade.

Enforcement: `test_module_boundaries.py::test_storage_zone_references_respect_ownership` scans string literals in all governed modules; any non-owner module that hard-codes a zone name as a path component fails. When no `[managed_storage.*]` is declared, the test is skipped.

This is the generic mechanism only. Concrete directory names and owner lists belong in each project's `architecture.toml` — never embed project-specific path conventions in the shared skill; examples here use neutral vocabulary.

### 6.3 Documentation Infrastructure (`scripts/`)

Like tests, documentation generation is delegated to the global skill via a Thin Wrapper.

**Example `scripts/generate_diagrams.py`:**
```python
import sys
from pathlib import Path

SKILL_DIR = Path.home() / "<skills-dir>" / "governed-arch" / "core"  # your agent's skills directory
sys.path.insert(0, str(SKILL_DIR))

from generate_diagrams import main

if __name__ == "__main__":
    main()
```

---

## 7. When To Use

Use this skill when the task involves:

- creating a new governed project structure
- creating a new governed module
- splitting or reorganizing module boundaries
- making public APIs explicit
- adding or updating interface locks
- adding architecture invariants
- introducing generated architecture docs and governance tests
- setting up or repairing the static check baseline (ruff + mypy + code-review skill) for a governed project

Do not force this skill onto trivial scripts or one-off edits that do not touch architecture, module structure, or public contracts.

---

## 8. Default Workflows

**Action Plan integration**: when the project carries a `docs/action-plan.md` (authored by the `to-arch` skill), both workflows below map onto it — New Project Initialization corresponds to **Wave 0 (governance scaffolding)**, and each newly governed module corresponds to a planned slice. Whenever a workflow step fulfils part of a slice, update that slice's status (`in-progress` / `done (<ref>)`) in `action-plan.md` in the same session; the plan is the project's resume point and must never go stale.

### 7.1 New Project Initialization

1. Create `architecture.toml`.
2. Register top-level governed modules in `submodules`.
3. Create governed module directories and add `module.toml`.
4. Register each module's direct children in `module.submodules`.
5. Add `[submodule.*]` dependency contracts only after the inventory is correct.
6. Create a Thin Wrapper for governance tests (e.g. `tests/test_governance.py`).
7. Create a Thin Wrapper for documentation (e.g. `scripts/generate_diagrams.py`).
8. Run tests and generate HTML docs.
9. **Establish the static-check baseline** — the baseline is **ruff + mypy + the `code-review` skill**. Add `ruff` + `mypy` configuration to `pyproject.toml`. Copy the baseline block from `templates/pyproject_ruff_mypy.toml`, adjust the per-file-ignores to the project's layout, install both tools into the project virtualenv, and record a zero-baseline target (`ruff check .` → All checks passed!, `mypy <packages>` → no issues) in the project's rules file. Verify the `code-review` skill is available (e.g. in your agent's skills directory); if it is missing, surface it as part of the baseline so the full stack (ruff + mypy + code-review) is in place before declaring the baseline complete.

### 7.2 Existing Project Retrofit

1. Capture the real top-level structure in `architecture.toml`.
2. Add `module.toml` module by module.
3. Bring `module.submodules` into sync with the real direct-child inventory.
4. Remove orphan and phantom child declarations before tightening dependency rules.
5. Introduce the Thin Wrapper for governance test suite.
6. Align `public_api` with `__all__`.
7. Lock truly exposed contracts.
8. Add invariants only after the structure is stable.
9. **Establish or repair the static-check baseline** — mirror the new-project step: the baseline is **ruff + mypy + the `code-review` skill**. If `ruff` + `mypy` configuration is missing from `pyproject.toml`, add it now using `templates/pyproject_ruff_mypy.toml` (do not just note the absence); if it exists, verify it runs clean and align it with the current layout. Confirm the `code-review` skill is installed (e.g. in your agent's skills directory); if absent, flag it so the baseline can be completed before it is considered sound.
10. Generate HTML docs via Thin Wrapper.

---

## 9. Templates & Core Library

The files in this skill are divided into `templates/` (for copying to your project) and `core/` (for referencing via thin wrapper):

**Templates (Copy to project):**
1. **[templates/architecture.toml](templates/architecture.toml)** — The top-level Architecture-as-Code manifest for governed modules and cross-module rules.
2. **[templates/module.toml](templates/module.toml)** — The module-level Architecture-as-Code manifest for local governance.
3. **[templates/test_invariants.py](templates/test_invariants.py)** — Boilerplate for module-local invariant guards.
4. **[templates/pyproject_ruff_mypy.toml](templates/pyproject_ruff_mypy.toml)** — ruff + mypy baseline config block to merge into a governed project's `pyproject.toml` (§8.1 step 9, §8.2 step 9)
5. **[templates/test_semantic_guards.py](templates/test_semantic_guards.py)** — copy-paste helpers for runtime semantic guards: window tiling, disjoint report bars, telescoping composition. Bind via `test_ref`; mutation-check once before trusting..

**Core Library (Delegate via Thin Wrapper):**
1. **[core/generate_diagrams.py](core/generate_diagrams.py)** — The HTML architecture report generator.
2. **[core/test_module_boundaries.py](core/test_module_boundaries.py)** — Boundary enforcement for governed modules and submodules.
3. **[core/test_interface_contracts.py](core/test_interface_contracts.py)** — Contract enforcement for public APIs, interface locks, invariant bindings, and Gateway-Only Import.
4. **[core/test_architecture_kit_complete.py](core/test_architecture_kit_complete.py)** — Completeness guard for the governance kit.

---

## 10. Resources

Use the supporting documents in `resources/` when you need more context than the templates alone provide:

1. **[resources/architecture_conventions.md](resources/architecture_conventions.md)** — Core governance concepts and the role of each test layer.
2. **[resources/html_generation_conventions.md](resources/html_generation_conventions.md)** — How generated HTML docs should work and be maintained.
3. **[resources/migration_playbook.md](resources/migration_playbook.md)** — Recommended migration order for new and existing projects.
