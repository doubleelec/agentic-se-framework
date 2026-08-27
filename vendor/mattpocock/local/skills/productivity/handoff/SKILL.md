---
name: handoff
description: Compact the current conversation into a handoff document for another agent to pick up.
argument-hint: "What will the next session be used for?"
disable-model-invocation: true
---

Write a handoff document summarising the current conversation so a fresh agent can continue the work.

Save it to the current project's `.scratch/` directory (create it if missing) — NOT the OS temporary directory and NOT the repo root.

Filename convention: `handoff-<session_topic>-<YYYYMMDD_HHMMSS>.md`
- `<session_topic>`: a short kebab-case slug summarising the session's focus (e.g. `backtest-decision-price-fix`, `live-engine-alignment`).
- `<YYYYMMDD_HHMMSS>`: local timestamp at generation time (24-hour).
Example: `handoff-backtest-decision-price-fix-20260810_171030.md`.

Include a "suggested skills" section in the document, naming which skills the next agent should call the Skill tool for.

Do not duplicate content already captured in other artifacts (specs, plans, ADRs, issues, commits, diffs). Reference them by path or URL instead.

Redact any sensitive information, such as API keys, passwords, or personally identifiable information.

If the user passed arguments, treat them as a description of what the next session will focus on and tailor the doc accordingly.
