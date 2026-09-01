# agentic-se-framework

Glossary for the engineering-delivery domain of this framework - the loop that turns a spec into tested, reviewed work.

## Language

**spec**:
A scoped piece of deliverable work, produced by the `to-spec` skill and captured as `spec.md`. It is a planning-level unit: a whole feature, subsystem, or slice large enough to be separately designed and acceptance-tested.
_Avoid_: task, milestone, ticket

**ticket**:
A single, dependency-ordered unit of implementation produced by the `to-tickets` skill from one spec. Tickets are the execution-level grain; a spec typically decomposes into multiple tickets.
_Avoid_: task, issue, story

**unit test**:
A test whose scope is **one ticket**. Verifies the behavior of a component or module in isolation, at pre-agreed seams, using test doubles to isolate collaborators. It is the intra-ticket quality bar: written through tdd and closed by `implement`'s final unit-test pass.
_Avoid_: component test, isolation test

**integration test**:
A test whose scope is **one spec**. Run after all of a spec's tickets are done to verify the contracts across those tickets/modules and to confirm the spec's own acceptance criteria. It is the single-spec completion gate.
_Avoid_: contract test, feature test

**system test**:
A test whose scope is **two or more specs** (up to all specs / the whole effort). Run when specs depend on each other or at full-effort delivery, exercising cross-spec interactions end to end against the effort's aggregate acceptance criteria. It is the multi-spec / final-wave gate.
_Avoid_: e2e test, full regression

**test gate**:
A pass/fail checkpoint, declared upstream by `to-arch`, that blocks progressing a ticket (unit then per-layer gate), finishing a spec (integration), or finishing an effort (system). A gate has pass/fail semantics and stop-on-failure rules - distinct from a mechanical test *run*, which has no decision attached.
_Avoid_: test run, test suite, full test

**AI Agent**:
An AI-driven agent that takes local decisions during engineering activities (code generation, requirements elicitation, architecture decisions, diagnostics) and produces artifacts under explicit engineering constraints — artifact-level, boundary-level, gate-level.
_Avoid_: LLM, AI coder, copilot, chatbot

**Agentic Software Engineering Framework**:
The repository itself: a methodology that constrains AI agents producing software through engineered artifacts (CONTEXT.md, ADR, architecture description, spec, tickets), architectural boundaries (TOML), and verification gates (test gates, code-review, failsafe-loop). Abbreviated ASEF.
_Avoid_: Vibe-Coding framework, AI coding tool, automation framework, agentic-se (as a standalone term for the framework — `agentic-se-framework` is the repo slug only)

## Domain rule (term-level)

Test scope follows **deliverable grain**, and the grains nest: `ticket ⊂ spec ⊂ effort`. Therefore unit ⊂ integration ⊂ system by construction, and a higher layer's gate subsumes (re-runs) the layers below it where the plan requires.