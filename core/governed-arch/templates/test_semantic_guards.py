"""Reusable semantic-guard patterns for cross-stage contracts.

Why this template exists
------------------------
Structural governance (imports, signatures, dependency graphs, inventories)
verifies shape, not meaning. Contracts like the following regress silently
unless someone writes a runtime guard AND registers it:

- window tiling:     periods partition a timeline without gaps or overlaps
- report windows:    front-closed / back-open handover (no shared bars)
- composition:       product(1 + part_return_i) - 1 == total_return
- handover equality: state produced at stage N == state consumed at stage N+1

Usage
-----
Copy the helpers you need into your module test suite, feed them REAL
artifacts (engine output, aggregated JSON, ...), and bind them via
[[invariant.*.rules]] test_ref in module.toml. Then mutation-check once:
temporarily break the protected behavior and confirm the guard fails.
A guard that cannot fail guards nothing.
"""
from math import isclose


def assert_tiles_contiguous(windows):
    """Nominal windows tile the axis exactly: prev.end == next.start for all pairs.

    windows: iterable of (start, end) pairs of any comparable type (dates, ints).
    """
    ws = sorted(windows)
    if len(ws) < 2:
        return
    for (_, prev_end), (next_start, _) in zip(ws, ws[1:]):
        assert prev_end == next_start, (
            f"nominal windows not contiguous: prev end {prev_end!r} != "
            f"next start {next_start!r}"
        )


def assert_report_bars_disjoint(first_index, second_index):
    """Adjacent stages share no reported bars (front-closed / back-open handover).

    Each argument is a sequence of comparable bar keys (timestamps, bar ids).
    """
    first_set, second_set = set(first_index), set(second_index)
    shared = first_set & second_set
    assert not shared, f"adjacent stages share bars: {sorted(shared)}"
    assert min(second_set) > max(first_set), (
        "second stage must start strictly after the previous stage ends"
    )


def assert_composition_identity(part_returns, total_return, *, rel_tol=1e-9, abs_tol=1e-12):
    """product(1 + part_i) - 1 == total_return (telescoping identity).

    Guards aggregation seams: locally reported metrics must recompose into the
    published global metric, otherwise a reporting layer changed semantics.
    """
    composed = 1.0
    for part in part_returns:
        composed *= 1.0 + part
    assert isclose(composed - 1.0, total_return, rel_tol=rel_tol, abs_tol=abs_tol), (
        f"local parts compose to {composed - 1.0!r} but global total is "
        f"{total_return!r}"
    )
