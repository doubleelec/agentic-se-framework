"""
Boundary and metadata guards for recursive federated governance.

Responsibility split:
- metadata integrity is enforced here
- intra-federation and declared dependency categories are enforced here
- cross-federation gateway shape is enforced in test_interface_contracts.py
"""

import ast
import tomllib
from pathlib import Path

import pytest

PROJECT_ROOT = Path.cwd()
ARCHITECTURE_FILE = PROJECT_ROOT / "architecture.toml"
SKIP_DIRS = {"gm_venv", ".gm_venv", ".venv", "__pycache__"}
IGNORED_CHILDREN = SKIP_DIRS | {".git", ".idea", ".vscode"}

with open(ARCHITECTURE_FILE, "rb") as f:
    _ARCH = tomllib.load(f)


def discover_all_modules(base_dir: Path, submodules_list: list[str]) -> set[str]:
    """Recursively discover all governed module directories."""
    discovered = set()
    for sub in submodules_list:
        sub_path = base_dir / sub
        if not sub_path.is_dir():
            continue
        mod_toml = sub_path / "module.toml"
        if not mod_toml.exists():
            continue
        rel_path = sub_path.relative_to(PROJECT_ROOT).as_posix()
        discovered.add(rel_path)
        with open(mod_toml, "rb") as f:
            try:
                cfg = tomllib.load(f)
            except Exception:
                continue
        inner_subs = cfg.get("module", {}).get("submodules", [])
        discovered.update(discover_all_modules(sub_path, inner_subs))
    return discovered


ALL_MODULES: set[str] = discover_all_modules(PROJECT_ROOT, _ARCH.get("submodules", []))
for key in _ARCH.get("module", {}).keys():
    ALL_MODULES.add(key)

# ── Abstract rule: managed storage ownership ─────────────────────────────
# Storage resources are owned by declared modules; data access is funneled
# through the owner (the storage twin of Gateway-Only Import). Projects
# declare each managed storage zone — a directory identity reserved for
# managed data (offline roots, caches, config stores, ...) — in
# architecture.toml:
#   [managed_storage.<zone_name>]
#   names  = ["<directory name>", ...]   # exact path-component match, no regex
#   owners = ["<module>", ...]           # modules allowed to reference the zone
# Any governed module NOT listed in a zone's `owners` is forbidden from
# hard-coding a zone directory name as a path component in string literals.
# The rule is skipped entirely when no [managed_storage.*] is declared.
STORAGE_ZONES: dict[str, dict] = _ARCH.get("managed_storage", {})


def _module_toml_path(module_name: str) -> Path:
    return PROJECT_ROOT / module_name / "module.toml"


def _load_module_toml(module_name: str) -> dict:
    with open(_module_toml_path(module_name), "rb") as f:
        return tomllib.load(f)


def _actual_direct_children(module_name: str) -> set[str]:
    """Direct-child inventory used by module.submodules."""
    module_dir = PROJECT_ROOT / module_name
    children = set()
    if not module_dir.is_dir():
        return children
    for entry in module_dir.iterdir():
        if entry.name in IGNORED_CHILDREN:
            continue
        if entry.name in {"module.toml", "__init__.py"}:
            continue
        if entry.is_file() and entry.suffix == ".py":
            children.add(entry.name)
        elif entry.is_dir():
            children.add(entry.name)
    return children


def _normalize_rule_child(module_name: str, raw_key: str) -> tuple[str | None, str | None]:
    """Normalize a [submodule.*] key to the governed module's direct child inventory."""
    if "/" not in raw_key:
        return raw_key, None
    prefix = f"{module_name}/"
    if not raw_key.startswith(prefix):
        return None, (
            f"{module_name}/module.toml [submodule.{raw_key!r}] is out of scope;"
            f"rules may only declare direct children of {module_name}/"
        )
    rel = raw_key[len(prefix) :]
    if "/" in rel:
        return None, (
            f"{module_name}/module.toml [submodule.{raw_key!r}] is not a direct child;"
            "declare direct files or directories only"
        )
    return rel, None


def _iter_rule_specs():
    """Yield (owner_module, child_key, child_cfg)."""
    for module_name in sorted(ALL_MODULES):
        mod_toml_path = _module_toml_path(module_name)
        if not mod_toml_path.exists():
            continue
        mod_toml = _load_module_toml(module_name)
        for raw_key, cfg in mod_toml.get("submodule", {}).items():
            child_key, error = _normalize_rule_child(module_name, raw_key)
            yield module_name, raw_key, child_key, cfg, error


def _iter_module_py_files(module_name: str):
    module_dir = PROJECT_ROOT / module_name
    if not module_dir.is_dir():
        return
    for py_file in sorted(module_dir.rglob("*.py")):
        rel = py_file.relative_to(PROJECT_ROOT)
        parts = rel.as_posix().split("/")
        if any(part in SKIP_DIRS for part in parts[:-1]):
            continue
        yield py_file


def _owner_candidates(rel_path: Path) -> list[str]:
    path_str = rel_path.as_posix()
    owners = []
    for module_name in sorted(ALL_MODULES):
        if path_str.startswith(module_name + "/"):
            owners.append(module_name)
    return owners


def _contains_zone_name(literal: str, names: set[str]) -> str | None:
    """Return the zone name that appears as an exact path component in the literal.

    Path components are split on both `/` and `\\`; a zone is "referenced" only when
    one of its declared directory names is an exact, complete component. This is
    deliberately regex-free: no escaping footguns, and name collisions cannot
    produce false matches (a zone named `.store` never matches a component
    like `.storehouse`).
    """
    for part in literal.split("/") + literal.split("\\"):
        if part in names:
            return part
    return None


def _scan_storage_zone_literals(filepath: Path, names: set[str]) -> list[str]:
    """Scan a file for hard-coded string literals referencing a storage zone."""
    with open(filepath, "r", encoding="utf-8") as f:
        try:
            tree = ast.parse(f.read())
        except SyntaxError:
            return []
    violations = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            hit = _contains_zone_name(node.value, names)
            if hit:
                violations.append(f"L{node.lineno}: {node.value[:80]!r} (zone name {hit!r})")
    return violations


def _scan_absolute_imports(filepath: Path) -> set[str]:
    """Collect absolute import modules only; relative imports are handled by GOI."""
    with open(filepath, "r", encoding="utf-8") as f:
        try:
            tree = ast.parse(f.read())
        except SyntaxError:
            return set()
    imports = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.add(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module and node.level == 0:
                imports.add(node.module)
    return imports


def _collect_rule_files(module_name: str, child_key: str) -> list[Path]:
    """Files governed by a direct-child rule."""
    target = PROJECT_ROOT / module_name / child_key
    if target.is_file():
        return [target]
    if not target.is_dir():
        return []
    # Nested federated modules own their own internal files via the deepest owner.
    # The parent rule still exists for direct-child inventory and structural
    # metadata, but must not re-govern the child's internal implementation files.
    if (target / "module.toml").exists():
        return []

    direct_files = []
    for py_file in sorted(target.glob("*.py")):
        if py_file.name in {"__init__.py", "module.toml"}:
            continue
        direct_files.append(py_file)
    return direct_files


def _owner_of_import(import_name: str) -> str | None:
    """Resolve the deepest owning federated module for an absolute import path."""
    import_parts = tuple(import_name.split("."))
    for module_name in sorted(ALL_MODULES, key=lambda m: -len(Path(m).parts)):
        module_parts = tuple(module_name.split("/"))
        if import_parts[: len(module_parts)] == module_parts:
            return module_name
    return None


def _classify_import(import_name: str, source_file: Path, owner_module: str) -> tuple[str, str] | None:
    """Classify an observed import as internal or external."""
    rel_parent = source_file.parent.relative_to(PROJECT_ROOT).as_posix()
    parent_dotted = rel_parent.replace("/", ".")

    sibling_prefix = f"{parent_dotted}."
    if parent_dotted and import_name.startswith(sibling_prefix):
        sibling = import_name[len(sibling_prefix) :].split(".")[0]
        return "internal", sibling

    target_owner = _owner_of_import(import_name)
    if target_owner is None:
        return None

    if target_owner == owner_module:
        owner_dotted = owner_module.replace("/", ".")
        remainder = import_name[len(owner_dotted) :].lstrip(".")
        target = owner_module.split("/")[-1] if not remainder else remainder.split(".")[0]
        return "internal", target

    return "external", target_owner


def _rule_actual_dependencies(module_name: str, child_key: str) -> tuple[set[str], set[str]]:
    actual_internal = set()
    actual_external = set()
    for py_file in _collect_rule_files(module_name, child_key):
        for import_name in _scan_absolute_imports(py_file):
            classified = _classify_import(import_name, py_file, module_name)
            if classified is None:
                continue
            dep_kind, dep_name = classified
            if dep_kind == "internal":
                actual_internal.add(dep_name)
            else:
                actual_external.add(dep_name)
    return actual_internal, actual_external


def test_no_orphan_submodules():
    """Every direct child under a governed module must appear in module.submodules."""
    errors = []
    for module_name in sorted(ALL_MODULES):
        mod_toml = _load_module_toml(module_name)
        declared = set(mod_toml.get("module", {}).get("submodules", []))
        actual = _actual_direct_children(module_name)
        orphans = sorted(actual - declared)
        for orphan in orphans:
            errors.append(
                f"{module_name}/ has an unregistered direct child {orphan!r};"
                f"add {orphan!r} to [module].submodules in {module_name}/module.toml"
            )
    if errors:
        pytest.fail("The following governed children are missing from module.submodules:\n" + "\n".join(errors))


def test_no_phantom_submodules():
    """Every declared child and every [submodule.*] rule must resolve to something real."""
    errors = []
    for module_name in sorted(ALL_MODULES):
        mod_toml = _load_module_toml(module_name)
        actual_children = _actual_direct_children(module_name)

        for child in mod_toml.get("module", {}).get("submodules", []):
            if child not in actual_children:
                errors.append(
                    f"{module_name}/module.toml module.submodules declares {child!r},"
                    "but that direct child does not exist; remove the declaration or restore the entry"
                )

    for module_name, raw_key, child_key, _cfg, error in _iter_rule_specs():
        if error:
            errors.append(error)
            continue
        actual_children = _actual_direct_children(module_name)
        if child_key not in actual_children:
            errors.append(
                f"{module_name}/module.toml [submodule.{raw_key!r}] points to a nonexistent direct child;"
                "remove the declaration or restore the corresponding file/directory"
            )

    if errors:
        pytest.fail("The following submodule declarations cannot be resolved to real objects:\n" + "\n".join(errors))


def test_module_submodules_complete():
    """module.submodules must be the exact direct-child inventory."""
    errors = []
    for module_name in sorted(ALL_MODULES):
        mod_toml = _load_module_toml(module_name)
        declared = set(mod_toml.get("module", {}).get("submodules", []))
        actual = _actual_direct_children(module_name)
        if declared == actual:
            continue
        missing = sorted(actual - declared)
        phantom = sorted(declared - actual)
        chunks = [f"{module_name}/module.toml [module].submodules disagrees with the actual direct children"]
        if missing:
            chunks.append(f"  missing from inventory: {missing}")
        if phantom:
            chunks.append(f"  declared but absent: {phantom}")
        errors.append("\n".join(chunks))
    if errors:
        pytest.fail("The following modules have a direct-child inventory inconsistent with module.submodules:\n" + "\n".join(errors))


def test_governed_files_have_single_deepest_owner():
    """Every governed .py file must have exactly one deepest owning module."""
    seen = set()
    errors = []
    for module_name in sorted(ALL_MODULES):
        for py_file in _iter_module_py_files(module_name):
            rel = py_file.relative_to(PROJECT_ROOT)
            if rel in seen:
                continue
            seen.add(rel)
            owners = _owner_candidates(rel)
            if not owners:
                errors.append(f"{rel.as_posix()} has no owning module")
                continue
            max_depth = max(len(Path(owner).parts) for owner in owners)
            deepest = [owner for owner in owners if len(Path(owner).parts) == max_depth]
            if len(deepest) != 1:
                errors.append(
                    f"{rel.as_posix()} has an ambiguous deepest owner: {sorted(deepest)}"
                )
    if errors:
        pytest.fail("The following governed .py files have ambiguous deepest owners:\n" + "\n".join(errors))


def test_storage_zone_references_respect_ownership():
    """Managed storage ownership rule.

    Storage resources are owned by declared modules, and data access is
    funneled through the owner — the storage twin of Gateway-Only Import.
    Zones come from `[managed_storage.*]` in architecture.toml:
      names  = directory names (exact path-component match, no regex)
      owners = modules permitted to reference the zone by name
    Any other governed module that hard-codes a zone name as a path component
    violates the rule: it must obtain the path through the owner's facade.
    Skipped when no zones are declared.
    """
    if not STORAGE_ZONES:
        pytest.skip("architecture.toml defines no [managed_storage.*]; skipping storage-zone ownership checks")
    errors = []
    for zone_name, zone_cfg in sorted(STORAGE_ZONES.items()):
        names = set(zone_cfg.get("names", []))
        if not names:
            continue
        owners = set(zone_cfg.get("owners", []))
        for module_name in sorted(ALL_MODULES):
            if module_name in owners:
                continue
            for py_file in _iter_module_py_files(module_name):
                violations = _scan_storage_zone_literals(py_file, names)
                if violations:
                    rel = py_file.relative_to(PROJECT_ROOT).as_posix()
                    errors.append(
                        f"[{zone_name}] {rel} references a managed storage zone from a non-owner module:\n  "
                        + "\n  ".join(violations)
                    )
    if errors:
        pytest.fail(
            "The following files name a managed storage zone inside non-owner modules"
            "(data access must funnel through the owner facade; hard-coded zone names are forbidden):\n"
            + "\n".join(errors)
        )


def test_submodule_boundaries():
    """Enforce intra-federation rules and declared dependency categories.

    This file owns:
    - module.submodules inventory integrity
    - same-federation dependency legality
    - actual import category vs declared internal/external category

    Cross-federation gateway shape is intentionally left to
    test_interface_contracts.py::test_cross_module_from_imports_in_exposed.
    """
    errors = []
    has_rules = False

    for module_name, raw_key, child_key, cfg, error in _iter_rule_specs():
        if error:
            errors.append(error)
            continue

        has_rules = True
        legacy = set(cfg.get("depends_on", []))
        declared_internal = set(cfg.get("internal_depends", []))
        declared_external = set(cfg.get("external_depends", []))
        declared_all = legacy | declared_internal | declared_external
        actual_internal, actual_external = _rule_actual_dependencies(module_name, child_key)
        display_key = f"{module_name}/{child_key}"

        for dep in sorted(actual_internal):
            if dep not in declared_all and f"{dep}.py" not in declared_all:
                errors.append(
                    f"{display_key} observed an intra-federation dependency {dep!r} that is not declared in internal_depends/depends_on"
                )
                continue
            if not legacy and dep in declared_external and dep not in declared_internal:
                errors.append(
                    f"{display_key} observed an intra-federation dependency {dep!r}, but it is wrongly listed under external_depends"
                )

        for dep in sorted(actual_external):
            dep_alias = dep.split("/")[-1]
            if dep not in declared_all and dep_alias not in declared_all:
                errors.append(
                    f"{display_key} observed a cross-federation dependency {dep!r} that is not declared in external_depends/depends_on"
                )
                continue
            if not legacy and dep in declared_internal and dep not in declared_external:
                errors.append(
                    f"{display_key} observed a cross-federation dependency {dep!r}, but it is wrongly listed under internal_depends"
                )
            elif not legacy and dep_alias in declared_internal and dep_alias not in declared_external:
                errors.append(
                    f"{display_key} observed a cross-federation dependency {dep!r}, but it is wrongly listed under internal_depends"
                )

    if not has_rules:
        pytest.skip("No [submodule.*] rules found in any module.toml")

    if errors:
        pytest.fail(
            "The following submodules violate module.toml dependency classification or completeness requirements:\n"
            + "\n".join(errors)
        )


# ── [[design.flows]] schema guard ──────────────────────────────────────
DESIGN_FLOW_KINDS = {"flow", "gates", "priority", "principles"}


def _iter_design_flows():
    '''Yield (module_name, flows_list) for modules declaring [design].flows.'''
    for module_name in sorted(ALL_MODULES):
        mod_toml_path = _module_toml_path(module_name)
        if not mod_toml_path.exists():
            continue
        mod_toml = _load_module_toml(module_name)
        flows = mod_toml.get("design", {}).get("flows", [])
        if isinstance(flows, list):
            yield module_name, flows


def test_design_flows_schema():
    '''[[design.flows]] schema guard.

    Optional chapter - modules that do not declare [design] are untouched.
    When present, each flow block must have a unique id, a title, a valid
    kind, and each step must have a title plus desc or check.
    '''
    errors = []
    for module_name, flows in _iter_design_flows():
        seen_ids = set()
        for flow in flows:
            flow_id = flow.get("id", "")
            if not flow_id:
                errors.append(f"{module_name}/module.toml: [[design.flows]] is missing required field id")
            elif flow_id in seen_ids:
                errors.append(f"{module_name}/module.toml: [[design.flows]] id {flow_id!r} is duplicated")
            else:
                seen_ids.add(flow_id)
            if not flow.get("title"):
                errors.append(f"{module_name}/module.toml: [[design.flows]] is missing required field title (id={flow_id!r})")
            kind = flow.get("kind", "")
            if kind not in DESIGN_FLOW_KINDS:
                errors.append(
                    f"{module_name}/module.toml: [[design.flows]] id={flow_id!r} has invalid kind={kind!r}; "
                    f"allowed values: {sorted(DESIGN_FLOW_KINDS)}"
                )
            for step in flow.get("steps", []):
                if not step.get("title"):
                    errors.append(
                        f"{module_name}/module.toml: [[design.flows]] id={flow_id!r} contains a step without title"
                    )
                if not (step.get("desc") or step.get("check")):
                    errors.append(
                        f"{module_name}/module.toml: [[design.flows]] id={flow_id!r} "
                        f"step={step.get('title', '')!r} must provide desc or check"
                    )
    if errors:
        pytest.fail("The following modules have [[design.flows]] sections violating the schema:\n" + "\n".join(errors))


def test_design_flow_links_resolve():
    '''[[design.flows]] reference integrity guard.

    Optional chapter - only modules that declare [design].flows are checked.
    Every step ref must resolve to a real contract anchor: its owning
    class/function must be exposed AND carry at least one non-empty lock
    spec. Every step invariant must be declared either in the module's own
    invariant rules or in the architecture-wide invariant rules. Broken
    links fail here; the renderer degrades them to plain text so the HTML
    never crashes on a dangling anchor.
    '''
    global_inv = set()
    for cat, data in _ARCH.get("invariant", {}).items():
        for rule in data.get("rules", []):
            if isinstance(rule, dict) and rule.get("id"):
                global_inv.add(rule["id"])

    errors = []
    for module_name, flows in _iter_design_flows():
        mod_toml = _load_module_toml(module_name)
        exposed = [e.lower() for e in mod_toml.get("public_api", {}).get("exposed", [])]
        all_locks = dict(_ARCH.get("interface_lock", {}))
        all_locks.update(mod_toml.get("interface_lock", {}))
        specs_map = {}
        for path, data in all_locks.items():
            if path.startswith(module_name):
                for spec_key, spec in data.get("specs", {}).items():
                    specs_map[spec_key.lower()] = spec

        mod_inv = set()
        for cat, data in mod_toml.get("invariant", {}).items():
            for rule in data.get("rules", []):
                if isinstance(rule, dict) and rule.get("id"):
                    mod_inv.add(rule["id"])

        def ref_has_anchor(r):
            cls = str(r).split(".")[0].lower()
            if cls not in exposed:
                return False
            if "." in str(r):
                return any(k.startswith(cls + ".") and specs_map[k] for k in specs_map)
            return any(k == cls and specs_map[k] for k in specs_map)

        for flow in flows:
            for step in flow.get("steps", []):
                raw_ref = step.get("ref")
                refs = raw_ref if isinstance(raw_ref, list) else ([raw_ref] if raw_ref else [])
                for r in refs:
                    if not ref_has_anchor(r):
                        errors.append(
                            f"{module_name}/module.toml: [[design.flows]] ref {r!r} has no matching contract anchor"
                        )
                raw_inv = step.get("invariant")
                invs = raw_inv if isinstance(raw_inv, list) else ([raw_inv] if raw_inv else [])
                for i in invs:
                    if i not in mod_inv and i not in global_inv:
                        errors.append(
                            f"{module_name}/module.toml: [[design.flows]] invariant {i!r} "
                            "is not declared in module or global invariants"
                        )
    if errors:
        pytest.fail("[[design.flows]] reference-integrity check failed:\n" + "\n".join(errors))

# ── Critical-module invariant coverage (opt-in)──────────────────────────────────────
def test_required_invariant_coverage():
    '''A module with [module].require_invariants = true must own at least one invariant rule bound to a test_ref.

    Motivation: structural governance (imports/signatures/dependencies/inventory) cannot protect business
    semantics — window tiling, cross-stage handover, aggregation identities. Critical modules must register
    semantic red lines explicitly and bind automated tests; regressions would otherwise surface only via manual audit.
    '''
    errors = []
    checked = 0
    for module_name in sorted(ALL_MODULES):
        mod_toml_path = _module_toml_path(module_name)
        if not mod_toml_path.exists():
            continue
        mod_toml = _load_module_toml(module_name)
        if not mod_toml.get("module", {}).get("require_invariants"):
            continue
        checked += 1
        bound_rules = []
        for cat, data in mod_toml.get("invariant", {}).items():
            for rule in data.get("rules", []):
                if isinstance(rule, dict) and rule.get("test_ref"):
                    bound_rules.append(f"{cat}.{rule.get('id', '?')}")
        if not bound_rules:
            errors.append(
                f"{module_name}/module.toml sets require_invariants=true "
                "but declares no invariant rule bound to a test_ref;"
                "critical semantic red lines must be registered and bound to automated tests"
            )
    if not checked:
        pytest.skip("no module enables require_invariants; skipping critical invariant coverage")
    if errors:
        pytest.fail(
            "The following critical modules lack bound semantic invariants:\n" + "\n".join(errors)
        )