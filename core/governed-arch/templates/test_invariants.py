# tests/<module_name>/test_invariants.py
import ast
import os
import pytest

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

def test_module_invariants_placeholder():
    """Placeholder invariant guard for a governed module.

    Replace the example checks below with project-specific red-line rules.
    Keep the general pattern:
    - walk the governed module
    - inspect source files
    - collect all violations
    - fail once with a readable summary
    """
    module_dir = os.path.join(PROJECT_ROOT, "<module_name>")
    errors = []
    for root, dirs, files in os.walk(module_dir):
        for f in files:
            if not f.endswith(".py"):
                continue
            py_file = os.path.join(root, f)
            with open(py_file, "r", encoding="utf-8") as file_obj:
                try:
                    tree = ast.parse(file_obj.read())
                except SyntaxError:
                    continue
            for node in ast.walk(tree):
                # Example placeholder:
                # collect a violation when a project-specific forbidden pattern is found.
                #
                # if isinstance(node, ast.ImportFrom) and node.module == "forbidden_layer":
                #     rel = os.path.relpath(py_file, PROJECT_ROOT)
                #     errors.append(
                #         f"{rel} L{node.lineno}: forbidden import from forbidden_layer"
                #     )
                pass
    if errors:
        pytest.fail(
            "Invariant violations detected in <module_name>:\n" + "\n".join(errors)
        )
