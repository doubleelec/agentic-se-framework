# Failsafe Loop Profile - Project Specifics (Template)

This template defines the expected structure and parameters for executing failsafe loop steps in a repository. Copy this template to `docs/agents/failsafe-loop-profile.md` in the project root and fill in the specifics.

If a gate does not apply to this project, write `not_applicable` explicitly instead of leaving it ambiguous.

## Environment & Tools

- **Python Command:** The exact python executable path (e.g., `.\.venv\Scripts\python.exe` or `python`).
- **Snapshot Tool:** The command to take snapshot diffs before a step (e.g., `git diff > snapshot.patch`).
- **Default Step Output Root:** Where step-specific outputs should be written (e.g., `artifacts/failsafe/`).

## Baseline Resolution

- **Preferred Baseline Source:** Existing prior run, checked-in artifact, golden file, or `generate fresh baseline`.
- **Baseline Location:** Where the baseline artifact normally lives.
- **Reuse Rule:** When an existing baseline can be reused and when a fresh baseline must be generated.

## Gate Definitions

### 1. Test Gate
- **Command:** Command to run unit/integration tests (e.g., `pytest tests/`).
- **Standard:** Rules for handling test failures.

### 2. Workflow Gate
- **Command:** Command to run the primary pipeline or execution workflow, or `not_applicable`.
- **Standard:** Requirements like mandatory force rebuilds, fresh output directories, etc.

### 3. Audit Gate
- **Command:** Command to execute audit/verification scripts, or `not_applicable`.
- **Standard:** Expected outcomes or file validations.

### 4. Comparison Gate
- **Command:** Command to run structural comparisons between candidate and baseline, or `not_applicable`.
- **Stop Conditions:** Specific thresholds or diff patterns that must abort execution (e.g. non-zero output mismatches).

## Repo-Specific Rules & Notes

- List any specific guidelines, environment flags, or constraints that must be observed during step execution.
