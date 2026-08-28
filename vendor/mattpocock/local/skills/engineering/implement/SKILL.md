---
name: implement
description: "Implement a piece of work based on a spec or ticket using TDD at pre-agreed seams, followed by typechecks, unit tests, and code review before committing."
---

Implement the work described by the user in the spec or tickets.

Use /tdd where possible, at pre-agreed seams.

Run typechecking regularly, single test files regularly, and the unit test suite once at the end. Fix failures before committing. When a caller owns stronger gates (integration / system / spec acceptance, e.g. the `impl-loop` skill), stop at unit tests and let the caller's gate cover the rest.

Once done, use /code-review to review the work.

Commit your work to the current branch.
