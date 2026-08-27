"""
Interface contract tests — verify that key public APIs maintain their
documented contracts (signatures, return types, frozen invariants).

These tests act as tripwires: if a contract changes, the test fails and
forces a review before the change propagates to downstream consumers.

Discovery is **federated**: rules are merged from the global architecture.toml
and all per-module module.toml files.
"""

import ast
import dataclasses
import importlib
import inspect
import re
import tomllib
from pathlib import Path

import pytest

PROJECT_ROOT = Path.cwd()
ARCHITECTURE_FILE = PROJECT_ROOT / "architecture.toml"

with open(ARCHITECTURE_FILE, "rb") as f:
    _ARCH = tomllib.load(f)

def discover_all_modules(base_dir: Path, submodules_list: list[str]) -> set[str]:
    """Recursively discover all module directories that have a module.toml."""
    discovered = set()
    for sub in submodules_list:
        sub_path = base_dir / sub
        if sub_path.is_dir():
            mod_toml = sub_path / "module.toml"
            if mod_toml.exists():
                rel_path = sub_path.relative_to(PROJECT_ROOT).as_posix()
                discovered.add(rel_path)
                with open(mod_toml, "rb") as f:
                    try:
                        cfg = tomllib.load(f)
                        inner_subs = cfg.get("module", {}).get("submodules", [])
                        discovered.update(discover_all_modules(sub_path, inner_subs))
                    except Exception:
                        pass
    return discovered


# All modules discovered recursively
ALL_MODULES = discover_all_modules(PROJECT_ROOT, _ARCH.get("submodules", []))
for key in _ARCH.get("module", {}).keys():
    ALL_MODULES.add(key)


def _discover_module_tomls() -> dict[str, dict]:
    """Find all module.toml files and return {module_name: parsed_dict}."""
    result = {}
    for mod in sorted(ALL_MODULES):
        mt = PROJECT_ROOT / mod / "module.toml"
        if mt.exists():
            with open(mt, "rb") as f:
                result[mod] = tomllib.load(f)
    return result


ALL_MODULE_TOMLS = _discover_module_tomls()




def _discover_all_interface_locks() -> dict:
    """Merge interface locks from architecture.toml and all */module.toml files."""
    merged = dict(_ARCH.get("interface_lock", {}))
    for _mod_name, mod_arch in ALL_MODULE_TOMLS.items():
        for key, val in mod_arch.get("interface_lock", {}).items():
            if key not in merged:
                merged[key] = val
    return merged


def _discover_all_invariants() -> dict:
    """Merge invariants from architecture.toml and all */module.toml files.

    module.toml may use [[invariant.X.rules]] (array-of-tables with id/desc/test_ref)
    while architecture.toml uses [invariant.X] rules = [...] (flat string list).
    Both formats are accepted.

    Union semantics: a domain declared in several sources contributes ALL its
    rules (root first, then modules in discovery order). The previous
    first-wins policy silently shadowed module-level bound rules whenever the
    root declared the same domain name (e.g. backtest_purity), leaving their
    test_refs outside meta-guard coverage. Rules are deduplicated on the
    (kind, id, test_ref) signature so re-declarations do not double-report.
    """
    def _rule_sig(rule):
        if isinstance(rule, dict):
            return ("dict", rule.get("id"), rule.get("test_ref"))
        return ("str", rule)

    sources = [_ARCH]
    for _mod_name, mod_arch in sorted(ALL_MODULE_TOMLS.items()):
        sources.append(mod_arch)

    merged: dict = {}
    for src in sources:
        for key, val in src.get("invariant", {}).items():
            if not isinstance(val, dict):
                if key not in merged:
                    merged[key] = val
                continue
            bucket = merged.setdefault(key, {"rules": []})
            existing = bucket.setdefault("rules", [])
            seen = {_rule_sig(r) for r in existing}
            for rule in val.get("rules", []):
                sig = _rule_sig(rule)
                if sig not in seen:
                    existing.append(rule)
                    seen.add(sig)
    return merged


ALL_INTERFACE_LOCKS = _discover_all_interface_locks()
ALL_INVARIANTS = _discover_all_invariants()


# ── Interface lock: file & function existence ─────────────────────────


def test_interface_locks_reference_existing_files():
    """All files referenced in [interface_lock.*] must exist."""
    locks = ALL_INTERFACE_LOCKS
    if not locks:
        pytest.skip("No interface_lock declarations found")

    errors = []
    for file_path_key in locks:
        full_path = PROJECT_ROOT / file_path_key
        if not full_path.exists():
            errors.append(f"interface_lock references non-existent file: {file_path_key}")

    if errors:
        pytest.fail("\n".join(errors))


def test_interface_locks_reference_existing_functions():
    """All functions referenced in [interface_lock.*] must exist in the target files."""
    locks = ALL_INTERFACE_LOCKS
    if not locks:
        pytest.skip("No interface_lock declarations found")

    errors = []
    for file_path_key, lock_cfg in locks.items():
        full_path = PROJECT_ROOT / file_path_key
        if not full_path.exists():
            continue

        with open(full_path, "r", encoding="utf-8") as f:
            try:
                tree = ast.parse(f.read())
            except SyntaxError:
                continue

        defined_names: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                defined_names.add(node.name)
            elif isinstance(node, ast.ClassDef):
                defined_names.add(node.name)
                for item in node.body:  # Only look at direct children to avoid deep nesting confusion
                    if isinstance(item, ast.FunctionDef):
                        defined_names.add(f"{node.name}.{item.name}")

        for locked_fn in lock_cfg.get("locked_functions", []):
            if locked_fn not in defined_names:
                errors.append(
                    f"interface_lock[{file_path_key}] references "
                    f"non-existent function: {locked_fn}"
                )

    if errors:
        pytest.fail("\n".join(errors))


# ── Deep signature verification (Phase 3.2) ──────────────────────────
# Use inspect.signature to verify that the actual code signature matches
# the specs declared in module.toml [interface_lock.*.specs.*].


def _resolve_function(file_path: str, func_qualified_name: str):
    """Dynamically resolve a function object from file path + qualified name."""
    rel = Path(file_path)
    module_dotted = str(rel.with_suffix("")).replace("/", ".").replace("\\", ".")
    try:
        mod = importlib.import_module(module_dotted)
    except (ImportError, ModuleNotFoundError):
        return None

    parts = func_qualified_name.split(".")
    obj = mod
    for part in parts:
        obj = getattr(obj, part, None)
        if obj is None:
            return None
    return obj


def test_interface_lock_specs_match_code():
    """Deep signature fingerprint verification.

    For each [interface_lock.*.specs.*] entry, use inspect.signature to verify
    that the actual function parameters match the declared spec (param names
    and defaults).
    """
    errors = []

    for file_path_key, lock_cfg in ALL_INTERFACE_LOCKS.items():
        specs = lock_cfg.get("specs", {})
        if not specs:
            continue

        for func_name, spec in specs.items():
            if "params" not in spec:
                continue

            func = _resolve_function(file_path_key, func_name)
            if func is None:
                errors.append(f"[{file_path_key}] could not resolve function {func_name}")
                continue

            if isinstance(func, type) and issubclass(func, __import__('enum').Enum):
                continue

            sig = inspect.signature(func)
            actual_params = list(sig.parameters.keys())
            declared_params = [p["name"] for p in spec.get("params", [])]

            if actual_params != declared_params:
                errors.append(
                    f"[{file_path_key}] signature mismatch for {func_name}:\n"
                    f"  module.toml declared:  {declared_params}\n"
                    f"  actual code signature: {actual_params}"
                )
                continue

            for decl_p in spec.get("params", []):
                p_name = decl_p["name"]
                p_default_str = decl_p.get("default", "NONE")
                if p_name not in sig.parameters:
                    continue

                actual_p = sig.parameters[p_name]
                if p_default_str == "NONE":
                    if actual_p.default is not inspect.Parameter.empty:
                        errors.append(
                            f"[{file_path_key}] {func_name}.{p_name}: "
                            f"declared default NONE but code has default {actual_p.default!r}"
                        )
                elif p_default_str == "None":
                    if actual_p.default is not None:
                        errors.append(
                            f"[{file_path_key}] {func_name}.{p_name}: "
                            f"declared default None but code default is {actual_p.default!r}"
                        )
                elif p_default_str == "<BASE_DIR>":
                    try:
                        if Path(actual_p.default).resolve() != PROJECT_ROOT.resolve():
                            errors.append(
                                f"[{file_path_key}] {func_name}.{p_name}: "
                                f"declared default <BASE_DIR> but actual value is {actual_p.default!r}"
                            )
                    except Exception:
                        errors.append(
                            f"[{file_path_key}] {func_name}.{p_name}: "
                            f"declared default <BASE_DIR> but the actual default is not a valid path: {actual_p.default!r}"
                        )
                else:
                    if actual_p.default is inspect.Parameter.empty:
                        errors.append(
                            f"[{file_path_key}] {func_name}.{p_name}: "
                            f"declared default {p_default_str} but code has no default"
                        )
                    elif str(actual_p.default) != p_default_str:
                        errors.append(
                            f"[{file_path_key}] {func_name}.{p_name}: "
                            f"declared default {p_default_str} but code default is {actual_p.default!r}"
                        )

    if errors:
        pytest.fail(
            "🔴 Interface signature fingerprint check failed (module.toml specs diverge from actual code):\n"
            + "\n".join(errors)
        )


# ── Coherence Guard (Phase 3.2) ──────────────────────────────────────
# Verify that locked function parameter names appear in the module.toml description
# or specs to ensure they are documented.


def _extract_contract_text(doc_path: Path) -> str:
    """Extract contract text from module.toml."""
    if not doc_path.exists():
        return ""
    return doc_path.read_text(encoding="utf-8")


def test_coherence_guard_params_in_toml():
    """Coherence Guard: locked function param names must be documented in module.toml.

    For each function with specs in module.toml, verify that all parameter names
    (excluding 'self') are mentioned in the specs (which they are by definition)
    and that descriptions are provided.
    """
    errors = []

    for file_path_key, lock_cfg in ALL_INTERFACE_LOCKS.items():
        specs = lock_cfg.get("specs", {})
        if not specs:
            continue

        parts = Path(file_path_key).parts
        if len(parts) < 1:
            continue

        doc_path = None
        # Priority: module.toml in the same folder or parent folder
        search_dirs = [PROJECT_ROOT / Path(*parts[:i+1]) for i in range(len(parts))]
        search_dirs.reverse() # Start from deepest
        
        for d in search_dirs:
            if (d / "module.toml").exists():
                doc_path = d / "module.toml"
                break

        if doc_path is None:
            errors.append(f"[{file_path_key}] could not locate its owning module.toml")
            continue

        for func_name, spec in specs.items():
            for param in spec.get("params", []):
                p_name = param.get("name")
                p_desc = param.get("description", "")
                if p_name == "self":
                    continue
                if not p_desc or p_desc == "NONE":
                    errors.append(
                        f"[{file_path_key}] {func_name} parameter '{p_name}' "
                        f"is missing a description in module.toml"
                    )

    if errors:
        pytest.fail(
            "🔴 Interface documentation check failed (incomplete parameter descriptions in module.toml):\n"
            + "\n".join(errors)
        )



# ── Invariant declarations are valid ──────────────────────────────────


def test_invariant_declarations_are_non_empty():
    """All [invariant.*] sections must have a non-empty rules list."""
    invariants = ALL_INVARIANTS
    if not invariants:
        pytest.skip("No invariant declarations found")

    errors = []
    for name, cfg in invariants.items():
        rules = cfg.get("rules", [])
        if not rules:
            errors.append(f"invariant.{name} has empty rules list")

    if errors:
        pytest.fail("\n".join(errors))


# ── Invariant test_ref completeness (meta-guard) ─────────────────────


def test_invariant_test_refs_exist():
    """Meta-guard: every invariant rule with a test_ref must point to an existing,
    live, non-hollow test function.

    Three binding-quality floors (added after the period-boundary regression
    class: a declared red line whose bound test is deleted, skipped, or gutted
    is indistinguishable from no red line at all):
    1. existence — file and function must exist (original floor);
    2. anti-skip — the bound test must not be short-circuited by a skip
       decorator or an unconditional runtime ``pytest.skip``;
    3. anti-hollow — the function body must contain at least one assert /
       raise / call. Pure ``pass`` or docstring-only bodies are vacuous
       bindings. Delegation-style wrappers (single forwarding call) pass.

    Rules without test_ref are treated as documentation-only.
    """
    errors = []

    for inv_name, inv_cfg in ALL_INVARIANTS.items():
        rules = inv_cfg.get("rules", [])
        for rule in rules:
            if not isinstance(rule, dict):
                continue  # flat string list (architecture.toml style)
            test_ref = rule.get("test_ref")
            if not test_ref:
                # Rules without test_ref are allowed (documentation only)
                continue

            if "::" not in test_ref:
                errors.append(
                    f"invariant.{inv_name}.rules[{rule['id']}] "
                    f"malformed test_ref (expected file::function): {test_ref}"
                )
                continue

            file_part, func_part = test_ref.rsplit("::", 1)
            test_file = PROJECT_ROOT / file_part
            if not test_file.exists():
                errors.append(
                    f"invariant.{inv_name}.rules[{rule['id']}] "
                    f"test_ref points to a nonexistent file: {file_part}"
                )
                continue

            with open(test_file, "r", encoding="utf-8") as f:
                try:
                    tree = ast.parse(f.read())
                except SyntaxError:
                    errors.append(
                        f"invariant.{inv_name}.rules[{rule['id']}] "
                        f"test_ref file has a syntax error: {file_part}"
                    )
                    continue

            cls_name, dot, meth_name = func_part.partition(".")
            target_fn = None
            if dot and meth_name:
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef) and node.name == cls_name:
                        target_fn = next(
                            (
                                m
                                for m in node.body
                                if isinstance(m, ast.FunctionDef) and m.name == meth_name
                            ),
                            None,
                        )
                        break
            else:
                target_fn = next(
                    (
                        node
                        for node in ast.walk(tree)
                        if isinstance(node, ast.FunctionDef) and node.name == func_part
                    ),
                    None,
                )
            if target_fn is None:
                errors.append(
                    f"invariant.{inv_name}.rules[{rule['id']}] "
                    f"test_ref points to a nonexistent test (function or Class.method supported): {test_ref}"
                )
                continue

            # Floor 2 — anti-skip: red lines must never be short-circuited.
            for dec in target_fn.decorator_list:
                try:
                    dec_src = ast.unparse(dec)
                except Exception:
                    dec_src = ""
                if ".skip" in dec_src or dec_src == "skip":
                    errors.append(
                        f"invariant.{inv_name}.rules[{rule['id']}] "
                        f"bound test is short-circuited by a skip decorator (red lines must never be skipped): {test_ref}"
                    )
            body_has_verdict_stmt = any(
                isinstance(n, (ast.Assert, ast.Raise)) for n in ast.walk(target_fn)
            )
            if not body_has_verdict_stmt:
                for node in ast.walk(target_fn):
                    if isinstance(node, ast.Call):
                        callee_name = getattr(node.func, "attr", None) or getattr(
                            node.func, "id", ""
                        )
                        if callee_name == "skip":
                            errors.append(
                                f"invariant.{inv_name}.rules[{rule['id']}] "
                                f"bound test consists solely of a skip (no assertions; red lines must never be skipped): {test_ref}"
                            )
                            break

            # Floor 3 — anti-hollow: body must reach a verdict somewhere.
            has_verdict = any(
                isinstance(n, (ast.Assert, ast.Raise, ast.Call))
                for n in ast.walk(target_fn)
            )
            if not has_verdict:
                errors.append(
                    f"invariant.{inv_name}.rules[{rule['id']}] "
                    f"bound test looks hollow (function body has no assert/raise/call;"
                    f"invalid red-line binding): {test_ref}"
                )

    if errors:
        pytest.fail(
            "🔴 Meta-gate check failed (invariant test_ref bindings broken or ineffective):\n"
            + "\n".join(errors)
        )


# ── public_api / __all__ consistency (L1) ─────────────────────────────


def _extract_all_from_init(init_path: Path) -> set[str] | None:
    """Extract the __all__ list from a Python __init__.py via AST. Returns None if no __all__."""
    if not init_path.exists():
        return None
    try:
        with open(init_path, "r", encoding="utf-8") as f:
            tree = ast.parse(f.read())
    except SyntaxError:
        return None
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for t in node.targets:
                if isinstance(t, ast.Name) and t.id == "__all__":
                    if isinstance(node.value, (ast.List, ast.Tuple)):
                        return {
                            elt.value
                            for elt in node.value.elts
                            if isinstance(elt, ast.Constant) and isinstance(elt.value, str)
                        }
    return None


def test_public_api_consistency():
    """L1: every [public_api] in any module.toml must match the __all__ in its __init__.py.

    For every module whose module.toml declares [public_api].exposed:
    - Read <dir>/__init__.py and extract __all__
    - The two sets must be equal
    - __init__.py must exist
    """
    # Collect [public_api] from all module.toml files
    public_api_map: dict[str, list[str]] = {}  # module_dir -> exposed list
    for mod_name, mod_arch in ALL_MODULE_TOMLS.items():
        pa = mod_arch.get("public_api", {})
        if "exposed" in pa:
            public_api_map[mod_name] = pa["exposed"]

    if not public_api_map:
        pytest.skip("No [public_api] declared in any module.toml")

    errors = []
    for mod_name, exposed_list in public_api_map.items():
        exposed_set = set(exposed_list)
        init_path = PROJECT_ROOT / mod_name / "__init__.py"
        all_set = _extract_all_from_init(init_path)
        if all_set is None:
            if not exposed_set:
                continue
            errors.append(
                f"[public_api] declared in {mod_name}/module.toml but "
                f"{init_path} missing __all__ or __init__.py"
            )
            continue
        if exposed_set != all_set:
            missing_in_init = exposed_set - all_set
            missing_in_toml = all_set - exposed_set
            err = f"[public_api] mismatch in {mod_name}/: "
            if missing_in_init:
                err += f"\n  in module.toml but not in __all__: {sorted(missing_in_init)}"
            if missing_in_toml:
                err += f"\n  in __all__ but not in module.toml: {sorted(missing_in_toml)}"
            errors.append(err)

    if errors:
        pytest.fail("L1 (public_api ≡ __all__) check failed:\n" + "\n".join(errors))


# ── L3: Gateway-Only Import (recursive facade resolution) ────────────────────────────
# Governance boundary = federated module (any dir holding module.toml); rules recurse:
#   - C == O: same deepest owner -> intra-federation import;
#     GOI does not apply; target legality is governed by test_module_boundaries.py.
#   - C != O: different deepest owners -> cross-federation import;
#     from-path must equal the owner's facade exactly; imported names must be in exposed.
#   - __init__.py facade files are structurally exempt (facades are built with deep imports,
#     otherwise circular imports arise).
#   - Non-governed dirs (tests/, audit/, scripts/) are absent from ALL_MODULE_TOMLS and thus never scanned.

_GOVERNED_DIRS = {"gm_venv", ".gm_venv", ".venv", "__pycache__"}


def _l3b_owner_index() -> list[str]:
    """Paths of federated modules (directories holding a module.toml), deepest first."""
    return sorted(ALL_MODULE_TOMLS.keys(), key=lambda m: -len(Path(m).parts))


def _l3b_owner_of(parts: tuple, owner_index: list[str]):
    """Return the deepest federated module owning the path (longest-prefix match), or None."""
    for mod in owner_index:
        mod_parts = Path(mod).parts
        if parts[: len(mod_parts)] == mod_parts:
            return mod
    return None


_L3B_SUBMODULE_NAME_CACHE: dict[str, set[str]] = {}


def _l3b_submodule_names(owner: str) -> set[str]:
    """Return submodule names directly under a federated module directory (case-sensitive).

    Names come from real directory entries: ``<name>.py`` files contribute their stem;
    ``<name>/`` directories (packages with ``__init__.py``) contribute the directory name.
    Do NOT probe with ``Path(f"{name}.py").is_file()`` — Windows filesystems
    are case-insensitive, so ``Task`` would falsely match ``task.py``.
    """
    if owner not in _L3B_SUBMODULE_NAME_CACHE:
        names: set[str] = set()
        owner_dir = PROJECT_ROOT / owner
        if owner_dir.is_dir():
            for entry in owner_dir.iterdir():
                if entry.is_file() and entry.suffix == ".py" and entry.name != "__init__.py":
                    names.add(entry.stem)
                elif entry.is_dir():
                    names.add(entry.name)
        _L3B_SUBMODULE_NAME_CACHE[owner] = names
    return _L3B_SUBMODULE_NAME_CACHE[owner]


def test_cross_module_from_imports_in_exposed():
    """L3 — Gateway-Only Import with recursive facade resolution.

    Every file is attributed to exactly one consumer (its deepest federated
    module); nested federations never rescan the same file (fixes legacy double counting).

    Rules:
    1. C == O: intra-federation import -> exempt (left to test_module_boundaries.py).
    2. C != O: cross-federation import -> from-path must equal exactly the owning federated
          module's dotted path, and every imported name must be in exposed; `from <owner>.<internal>
          import ...` is a facade bypass even when the imported name is exposed.
    3. `from <owner> import <submodule>` (wholesale submodule-object import) is treated as
          namespace-style export requiring an explicit policy decision; blocked here.
    4. Format floors: `from x import *` is forbidden; relative imports are forbidden outside facades.
    """
    exposed_map: dict[str, set[str]] = {}
    for mod_name, mod_arch in ALL_MODULE_TOMLS.items():
        pa = mod_arch.get("public_api", {})
        if "exposed" in pa:
            exposed_map[mod_name] = set(pa["exposed"])

    if not exposed_map:
        pytest.skip("No [public_api] declared in any module.toml")

    owner_index = _l3b_owner_index()

    files_by_owner: dict[str, list[Path]] = {}
    for mod in owner_index:
        mod_dir = PROJECT_ROOT / mod
        if not mod_dir.is_dir():
            continue
        for py_file in sorted(mod_dir.rglob("*.py")):
            parts = py_file.relative_to(PROJECT_ROOT).parts
            if any(p in _GOVERNED_DIRS for p in parts):
                continue
            if py_file.name == "__init__.py":
                continue
            if _l3b_owner_of(parts, owner_index) != mod:
                continue
            files_by_owner.setdefault(mod, []).append(py_file)

    errors = []
    for consumer, py_files in sorted(files_by_owner.items()):
        for py_file in py_files:
            try:
                with open(py_file, "r", encoding="utf-8") as f:
                    tree = ast.parse(f.read())
            except SyntaxError:
                continue
            rel = py_file.relative_to(PROJECT_ROOT).as_posix()

            for node in ast.walk(tree):
                if not isinstance(node, ast.ImportFrom):
                    continue
                if not node.module:
                    continue
                if node.level:
                    errors.append(
                        f"{rel}:{node.lineno} relative import in a non-facade file"
                        f"(relative imports are reserved for __init__.py facades)"
                    )
                    continue
                for alias in node.names:
                    if alias.name == "*":
                        errors.append(
                            f"{rel}:{node.lineno} 'from {node.module} import *' "
                            f"format-floor violation: star imports are forbidden"
                        )
                target_parts = tuple(node.module.split("."))
                target_owner = _l3b_owner_of(target_parts, owner_index)
                if target_owner is None:
                    continue  # stdlib / third-party / non-governed target
                if target_owner == consumer:
                    continue  # C == O, intra-federation -> left to test_module_boundaries.py
                if target_owner not in exposed_map:
                    continue  # target federated module declares no public surface

                owner_dotted = target_owner.replace("/", ".")
                if node.module != owner_dotted:
                    errors.append(
                        f"{rel}:{node.lineno} 'from {node.module} import ...' "
                        f"bypasses the facade of '{target_owner}'; rewrite it as "
                        f"'from {owner_dotted} import <name>' (name ∈ exposed)"
                    )
                    continue

                for alias in node.names:
                    name = alias.name
                    if name in _l3b_submodule_names(target_owner):
                        errors.append(
                            f"{rel}:{node.lineno} 'from {node.module} import {name}' "
                            f"imports a submodule object wholesale (namespace-style export requires an explicit policy)"
                        )
                    elif name not in exposed_map[target_owner]:
                        errors.append(
                            f"{rel}:{node.lineno} 'from {node.module} import {name}' "
                            f"but {target_owner}.exposed = "
                            f"{sorted(exposed_map[target_owner])}"
                        )

    if errors:
        pytest.fail("L3 (Gateway-Only Import) check failed:\n" + "\n".join(errors))
