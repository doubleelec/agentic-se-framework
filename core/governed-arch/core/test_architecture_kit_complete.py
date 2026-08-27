"""
Architecture Kit Completeness Test — Verify that governed modules
have their full governance kit:
1. module.toml (with [module] section)
2. tests/<module>/ directory for unit tests
"""

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


def test_root_cleanliness():
    """Verify that the project root does not contain ANY .py files.
    Infrastructure should use non-py formats (toml, txt, yaml, etc.) or reside in modules.
    """
    errors = []
    for item in PROJECT_ROOT.iterdir():
        if item.is_file() and item.suffix == ".py":
            errors.append(f"Source file detected at project root: {item.name}")

    if errors:
        pytest.fail(
            "🔴 Root-cleanliness check failed (absolute constraint). No .py files are allowed at the project root.\n"
            "Move feature code into modules, test configuration into tests/, or build configuration into pyproject.toml:\n"
            + "\n".join(errors)
        )


def test_governed_modules_completeness():
    """Verify that all modules registered recursively
    have the complete governance kit and standard fields:
    - module.toml with mandatory [module] and [public_api] sections
    - tests/<module>/ directory
    """
    errors = []

    for mod in sorted(ALL_MODULES):
        mod_dir = PROJECT_ROOT / mod
        if not mod_dir.exists():
            errors.append(f"Module directory does not exist: {mod}/")
            continue

        # 1. Check module.toml and its sections
        module_toml_path = mod_dir / "module.toml"
        if not module_toml_path.exists():
            errors.append(f"[{mod}] module.toml is missing")
        else:
            with open(module_toml_path, "rb") as f:
                try:
                    cfg = tomllib.load(f)
                except Exception as e:
                    errors.append(f"[{mod}] failed to parse module.toml: {e}")
                    continue
                
                # Check [module] section
                if "module" not in cfg:
                    errors.append(f"[{mod}] module.toml is missing the [module] metadata section")
                else:
                    m = cfg["module"]
                    for field in ("name", "description", "submodules", "consumers", "data_flow"):
                        if field not in m:
                            errors.append(f"[{mod}] module.toml [module] is missing field '{field}'")
                
                # Check [public_api] section
                if "public_api" not in cfg:
                    errors.append(f"[{mod}] module.toml is missing the [public_api] interface section")
                else:
                    api = cfg["public_api"]
                    for field in ("exposed", "reason"):
                        if field not in api:
                            errors.append(f"[{mod}] module.toml [public_api] is missing field '{field}'")

        # 2. Check tests/<module>/
        test_dir = PROJECT_ROOT / "tests" / mod
        if not test_dir.exists() or not test_dir.is_dir():
            errors.append(f"[{mod}] missing unit-test directory tests/{mod}/")

    if errors:
        pytest.fail(
            "🔴 The Architecture Kit is incomplete. Every module's module.toml "
            "must contain complete [module] and [public_api] sections, and a tests/<module>/ directory must exist:\n"
            + "\n".join(errors)
        )
