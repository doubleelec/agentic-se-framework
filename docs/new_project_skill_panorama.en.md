# Skill Panorama for New Software Projects

> This is the English counterpart of [`new_project_skill_panorama.zh.md`](new_project_skill_panorama.zh.md). The two versions share identical section numbering, table structure, and figure geometry; the Chinese edition is the source of truth for content changes.

## 1. Purpose and Theoretical Positioning

This document is not a "skill catalog" but an engineering methodology manual for new software projects. The core questions it answers are:

- When requirements are still vague, how should a project start without rushing headlong into coding;
- How to keep the process compatible with mainstream, foundational software engineering theory, so that it is easy to understand, promote, and tailor;
- How to elevate software architecture design from "drawing diagrams by experience" into a rigorous activity with stakeholders, concerns, quality attributes, and an evaluation loop;
- How the skills in the current `agentic-se-framework` workspace should map onto this methodology.

### 1.1 Theoretical Positioning and Core Principles

On the mainstream software engineering track, this methodology stays aligned in spirit with `SWEBOK`, `ISO/IEC/IEEE 12207`, `29148`, and `15289`; on software architecture it centers on `ISO/IEC/IEEE 42010`, quality attribute scenarios, `QAW`, `ATAM`, and `ADR`, establishing a complete, detailed, and deliberate architecture workflow:

- **Concurrent, iterative, recursive life cycle**: life cycle processes are not a rigid single line; requirements, architecture, design, implementation, verification, validation, operation, and maintenance are continuous activities along the same engineering mainline;
- **Architecture centered on description and decisions**: architecture is not a handful of isolated sketches, but an organized description of "stakeholders, concerns, viewpoints, views, correspondences, decisions (ADRs) and their rationale";
- **Quality attributes as scenarios**: quality attributes must not remain slogans (such as "high performance"); they must be turned into concrete, measurable scenarios;
- **Shift-left verification and real-scenario validation**: verification runs through requirements, design, prototypes, code review, and testing end to end;
- **Tailorable process, non-negotiable questions**: small projects may compress artifact forms, but must still answer "what problem is being solved, which quality attributes drive the structure, why it is designed this way, and how effectiveness is proven".

### 1.2 Scope and Skill Sources

This document builds on the currently published skill set:
- `vendor/mattpocock/local/*`: locally maintained and enhanced software engineering derivative skills;
- `core/*`: this repository's original architecture governance, ticket tracking, and delivery evolution skills.

What this document aims to establish is "a promotable mainline + tailorable branches + an auditable artifact system", not a rigid pipeline.

## 2. Methodology Overview

From the classical software engineering perspective, a sound mainline for a new project is not "code first" but:

1. Establish the collaboration and governance foundation;
2. Clarify the problem, stakeholders, goals, and constraints;
3. Establish domain language, boundaries, and architecture drivers, then synthesize them into a complete architecture description and an implementation process plan;
4. Produce specifications that are reviewable, verifiable, and traceable;
5. Decompose into executable work packages and establish state flow;
6. Verify unknowns, risks, and key assumptions early;
7. Enter implementation, integration, and layered verification;
8. Set deliberate gates for high-risk changes;
9. Before delivery, run conformance checks against conventions, specifications, and architecture;
10. Release, hand over, observe in operation, and feed follow-up inputs back into the maintenance loop.

Mapped onto the current skills, the trunk path typically is:

| Timing | Preferred skill(s) |
| :--- | :--- |
| Phase 0: Project bootstrap | [`setup-matt-pocock-skills`](#setup-matt-pocock-skills) |
| Phase 1: Requirements elicitation (choose one) | [`wayfinder`](#wayfinder) / [`grill-with-docs`](#grill-with-docs) |
| Phase 2: Concept unification, architecture synthesis & constraint enforcement | [`domain-modeling`](#domain-modeling) → [`codebase-design`](#codebase-design) → [`to-arch`](#to-arch) → [`governed-arch`](#governed-arch) |
| Phase 3: Specification & ticket decomposition | [`to-spec`](#to-spec) → [`to-tickets`](#to-tickets) |
| Phase 4: Single-slice coding & test loop | [`implement`](#implement) (incl. [`tdd`](#tdd) + [`code-review`](#code-review)) |
| Phase 5: Operation, diagnosis & asset evolution | [`to-issues`](#to-issues) → [`triage`](#triage) / [`diagnosing-bugs`](#diagnosing-bugs) → [`governed-arch`](#governed-arch) |
| Auxiliary: High-uncertainty exploration | [`research`](#research) / [`prototype`](#prototype) |
| Auxiliary: High-risk change guarding | [`failsafe-loop`](#failsafe-loop) |
| Auxiliary: Handover | [`handoff`](#handoff) |

The point is not that "the order must be one-size-fits-all", but that every phase must answer one clear engineering question and leave behind the corresponding artifacts.

<div style="margin: 20px 0 28px;">
  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1120 620" width="100%" height="auto" role="img" aria-label="Software engineering life cycle and skill mapping diagram">
    <defs>
      <marker id="arrow-main" viewBox="0 0 8 8" refX="7" refY="4" markerWidth="8" markerHeight="8" markerUnits="userSpaceOnUse" orient="auto">
        <path d="M1 1 L7 4 L1 7 Z" fill="#6f42ff"></path>
      </marker>
      <marker id="arrow-dashed" viewBox="0 0 8 8" refX="7" refY="4" markerWidth="8" markerHeight="8" markerUnits="userSpaceOnUse" orient="auto">
        <path d="M1 1 L7 4 L1 7 Z" fill="#cbd5e1"></path>
      </marker>
    </defs>
    <!-- Background -->
    <rect x="0" y="0" width="1120" height="620" rx="12" fill="#ffffff"></rect>

    <!-- Row 1: Phase goals (aligned with main phases) -->
    <rect x="8" y="14" width="168" height="32" rx="16" fill="#475569"></rect>
    <text x="92" y="35" text-anchor="middle" font-size="16" font-weight="700" fill="#ffffff">Phase Goals</text>

    <rect x="260" y="20" width="120" height="48" rx="8" fill="#f8fafc" stroke="#cbd5e1" stroke-dasharray="4 2"></rect>
    <text x="320" y="40" text-anchor="middle" font-size="14" fill="#334155">Clarify problem</text>
    <text x="320" y="58" text-anchor="middle" font-size="14" fill="#334155">and concerns</text>

    <rect x="440" y="20" width="120" height="48" rx="8" fill="#f8fafc" stroke="#cbd5e1" stroke-dasharray="4 2"></rect>
    <text x="500" y="40" text-anchor="middle" font-size="14" fill="#334155">Unify concepts</text>
    <text x="500" y="58" text-anchor="middle" font-size="14" fill="#334155">&amp; constraints</text>

    <rect x="620" y="20" width="120" height="48" rx="8" fill="#f8fafc" stroke="#cbd5e1" stroke-dasharray="4 2"></rect>
    <text x="680" y="40" text-anchor="middle" font-size="14" fill="#334155">Form contracts</text>
    <text x="680" y="58" text-anchor="middle" font-size="14" fill="#334155">&amp; work tickets</text>

    <rect x="780" y="20" width="120" height="48" rx="8" fill="#f8fafc" stroke="#cbd5e1" stroke-dasharray="4 2"></rect>
    <text x="840" y="40" text-anchor="middle" font-size="14" fill="#334155">Meet baselines</text>
    <text x="840" y="58" text-anchor="middle" font-size="14" fill="#334155">&amp; real scenarios</text>

    <!-- Vertical connectors (goal alignment) -->
    <line x1="320" y1="68" x2="320" y2="150" stroke="#cbd5e1" stroke-width="2" stroke-dasharray="3 3" marker-end="url(#arrow-dashed)"></line>
    <line x1="500" y1="68" x2="500" y2="150" stroke="#cbd5e1" stroke-width="2" stroke-dasharray="3 3" marker-end="url(#arrow-dashed)"></line>
    <line x1="680" y1="68" x2="680" y2="150" stroke="#cbd5e1" stroke-width="2" stroke-dasharray="3 3" marker-end="url(#arrow-dashed)"></line>
    <line x1="840" y1="68" x2="840" y2="150" stroke="#cbd5e1" stroke-width="2" stroke-dasharray="3 3" marker-end="url(#arrow-dashed)"></line>

    <!-- Row 2: Engineering main phases -->
    <rect x="8" y="96" width="168" height="32" rx="16" fill="#6f42ff"></rect>
    <text x="92" y="117" text-anchor="middle" font-size="16" font-weight="700" fill="#ffffff">Engineering Phases</text>

    <line x1="158" y1="180" x2="1050" y2="180" stroke="#6f42ff" stroke-width="3" marker-end="url(#arrow-main)"></line>

    <rect x="95" y="150" width="125" height="60" rx="14" fill="#f5f3ff" stroke="#c4b5fd"></rect>
    <text x="158" y="186" text-anchor="middle" font-size="15" font-weight="600" fill="#111827">Bootstrap</text>

    <rect x="250" y="150" width="140" height="60" rx="14" fill="#ede9fe" stroke="#8b5cf6"></rect>
    <text x="320" y="186" text-anchor="middle" font-size="15" font-weight="600" fill="#111827">Elicitation</text>

    <rect x="420" y="150" width="160" height="60" rx="14" fill="#ede9fe" stroke="#8b5cf6"></rect>
    <text x="500" y="176" text-anchor="middle" font-size="15" font-weight="600" fill="#111827">Arch &amp; Boundary</text>
    <text x="500" y="196" text-anchor="middle" font-size="15" font-weight="600" fill="#111827">Design</text>

    <rect x="610" y="150" width="140" height="60" rx="14" fill="#ede9fe" stroke="#8b5cf6"></rect>
    <text x="680" y="176" text-anchor="middle" font-size="15" font-weight="600" fill="#111827">Spec &amp; Ticket</text>
    <text x="680" y="196" text-anchor="middle" font-size="15" font-weight="600" fill="#111827">Split</text>

    <rect x="780" y="150" width="130" height="60" rx="14" fill="#ede9fe" stroke="#8b5cf6"></rect>
    <text x="845" y="186" text-anchor="middle" font-size="15" font-weight="600" fill="#111827">Iterative Loop</text>

    <rect x="940" y="150" width="140" height="60" rx="14" fill="#ede9fe" stroke="#8b5cf6"></rect>
    <text x="1010" y="186" text-anchor="middle" font-size="15" font-weight="600" fill="#111827">Run &amp; Evolve</text>

    <!-- Phase -> skill connectors -->
    <line x1="158" y1="210" x2="158" y2="260" stroke="#cbd5e1" stroke-width="2" stroke-dasharray="3 3" marker-end="url(#arrow-dashed)"></line>
    <line x1="320" y1="210" x2="320" y2="260" stroke="#cbd5e1" stroke-width="2" stroke-dasharray="3 3" marker-end="url(#arrow-dashed)"></line>
    <line x1="500" y1="210" x2="500" y2="260" stroke="#cbd5e1" stroke-width="2" stroke-dasharray="3 3" marker-end="url(#arrow-dashed)"></line>
    <line x1="680" y1="210" x2="680" y2="260" stroke="#cbd5e1" stroke-width="2" stroke-dasharray="3 3" marker-end="url(#arrow-dashed)"></line>
    <line x1="845" y1="210" x2="845" y2="260" stroke="#cbd5e1" stroke-width="2" stroke-dasharray="3 3" marker-end="url(#arrow-dashed)"></line>
    <line x1="1010" y1="210" x2="1010" y2="260" stroke="#cbd5e1" stroke-width="2" stroke-dasharray="3 3" marker-end="url(#arrow-dashed)"></line>

    <!-- Row 3: Executing skill line -->
    <rect x="8" y="220" width="168" height="32" rx="16" fill="#0f766e"></rect>
    <text x="92" y="241" text-anchor="middle" font-size="16" font-weight="700" fill="#ffffff">Executing Skills</text>

    <rect x="95" y="260" width="125" height="120" rx="8" fill="#ecfeff" stroke="#2dd4bf"></rect>
    <text x="158" y="325" text-anchor="middle" font-size="12" font-weight="600" fill="#0f766e">setup</text>

    <rect x="250" y="260" width="140" height="120" rx="8" fill="#ecfeff" stroke="#2dd4bf"></rect>
    <text x="320" y="305" text-anchor="middle" font-size="12" font-weight="600" fill="#0f766e">wayfinder</text>
    <text x="320" y="325" text-anchor="middle" font-size="12" font-weight="600" fill="#0f766e">grill-with-docs</text>
    <text x="320" y="345" text-anchor="middle" font-size="12" font-weight="600" fill="#0f766e">to-questionnaire</text>

    <rect x="420" y="260" width="160" height="120" rx="8" fill="#ecfeff" stroke="#2dd4bf"></rect>
    <text x="500" y="290" text-anchor="middle" font-size="12" font-weight="600" fill="#0f766e">domain-modeling</text>
    <text x="500" y="309" text-anchor="middle" font-size="12" font-weight="600" fill="#0f766e">codebase-design</text>
    <text x="500" y="328" text-anchor="middle" font-size="12" font-weight="600" fill="#0f766e">to-arch</text>
    <text x="500" y="347" text-anchor="middle" font-size="12" font-weight="600" fill="#0f766e">governed-arch</text>

    <!-- impl-loop orchestration dashed frame -->
    <rect x="598" y="246" width="324" height="142" rx="10" fill="#f0fdfa" fill-opacity="0.4" stroke="#0d9488" stroke-width="1.8" stroke-dasharray="5 3"></rect>
    <rect x="715" y="236" width="90" height="20" rx="6" fill="#0f766e"></rect>
    <text x="760" y="250" text-anchor="middle" font-size="11.5" font-weight="700" fill="#ffffff">impl-loop</text>

    <rect x="610" y="260" width="140" height="120" rx="8" fill="#ecfeff" stroke="#2dd4bf"></rect>
    <text x="680" y="315" text-anchor="middle" font-size="12" font-weight="600" fill="#0f766e">to-spec</text>
    <text x="680" y="335" text-anchor="middle" font-size="12" font-weight="600" fill="#0f766e">to-tickets</text>

    <rect x="780" y="260" width="130" height="120" rx="8" fill="#ecfeff" stroke="#2dd4bf"></rect>
    <text x="845" y="310" text-anchor="middle" font-size="12" font-weight="600" fill="#0f766e">implement</text>
    <text x="845" y="330" text-anchor="middle" font-size="12" font-weight="600" fill="#0f766e">(incl. tdd /</text>
    <text x="845" y="350" text-anchor="middle" font-size="12" font-weight="600" fill="#0f766e">code-review)</text>

    <rect x="940" y="260" width="140" height="120" rx="8" fill="#ecfeff" stroke="#2dd4bf"></rect>
    <text x="1010" y="295" text-anchor="middle" font-size="12" font-weight="600" fill="#0f766e">to-issues</text>
    <text x="1010" y="315" text-anchor="middle" font-size="12" font-weight="600" fill="#0f766e">triage</text>
    <text x="1010" y="335" text-anchor="middle" font-size="12" font-weight="600" fill="#0f766e">diagnosing-bugs</text>
    <text x="1010" y="355" text-anchor="middle" font-size="12" font-weight="600" fill="#0f766e">governed-arch</text>

    <!-- Skill -> artifact connectors -->
    <line x1="158" y1="380" x2="158" y2="430" stroke="#cbd5e1" stroke-width="2" stroke-dasharray="3 3" marker-end="url(#arrow-dashed)"></line>
    <line x1="320" y1="380" x2="320" y2="430" stroke="#cbd5e1" stroke-width="2" stroke-dasharray="3 3" marker-end="url(#arrow-dashed)"></line>
    <line x1="500" y1="380" x2="500" y2="430" stroke="#cbd5e1" stroke-width="2" stroke-dasharray="3 3" marker-end="url(#arrow-dashed)"></line>
    <line x1="680" y1="380" x2="680" y2="430" stroke="#cbd5e1" stroke-width="2" stroke-dasharray="3 3" marker-end="url(#arrow-dashed)"></line>
    <line x1="845" y1="380" x2="845" y2="430" stroke="#cbd5e1" stroke-width="2" stroke-dasharray="3 3" marker-end="url(#arrow-dashed)"></line>
    <line x1="1010" y1="380" x2="1010" y2="430" stroke="#cbd5e1" stroke-width="2" stroke-dasharray="3 3" marker-end="url(#arrow-dashed)"></line>

    <!-- Row 4: Artifact line (concise names) -->
    <rect x="8" y="390" width="168" height="32" rx="16" fill="#1d4ed8"></rect>
    <text x="92" y="411" text-anchor="middle" font-size="16" font-weight="700" fill="#ffffff">Artifacts</text>

    <rect x="95" y="430" width="125" height="88" rx="8" fill="#eff6ff" stroke="#60a5fa"></rect>
    <text x="158" y="458" text-anchor="middle" font-size="11.5" font-weight="600" fill="#1e40af">AGENTS.md</text>
    <text x="158" y="478" text-anchor="middle" font-size="11.5" font-weight="600" fill="#1e40af">issue-tracker.md</text>
    <text x="158" y="498" text-anchor="middle" font-size="11.5" font-weight="600" fill="#1e40af">triage-labels.md</text>

    <rect x="250" y="430" width="140" height="88" rx="8" fill="#eff6ff" stroke="#60a5fa"></rect>
    <text x="320" y="458" text-anchor="middle" font-size="11.5" font-weight="600" fill="#1e40af">map.md</text>
    <text x="320" y="478" text-anchor="middle" font-size="11.5" font-weight="600" fill="#1e40af">CONTEXT.md</text>
    <text x="320" y="498" text-anchor="middle" font-size="11.5" font-weight="600" fill="#1e40af">to-questionnaire-*.md</text>

    <rect x="400" y="430" width="200" height="88" rx="8" fill="#eff6ff" stroke="#60a5fa"></rect>
    <text x="500" y="452" text-anchor="middle" font-size="11.5" font-weight="600" fill="#1e40af">CONTEXT.md / ADR</text>
    <text x="500" y="472" text-anchor="middle" font-size="11.5" font-weight="600" fill="#1e40af">docs/architecture.md</text>
    <text x="500" y="492" text-anchor="middle" font-size="11.5" font-weight="600" fill="#1e40af">docs/action-plan.md</text>
    <text x="500" y="510" text-anchor="middle" font-size="11.5" font-weight="600" fill="#1e40af">architecture.toml / module.toml</text>

    <rect x="610" y="430" width="140" height="88" rx="8" fill="#eff6ff" stroke="#60a5fa"></rect>
    <text x="680" y="450" text-anchor="middle" font-size="10.5" font-weight="600" fill="#1e40af">.scratch/&lt;slug&gt;/</text>
    <text x="680" y="468" text-anchor="middle" font-size="10.5" font-weight="600" fill="#1e40af">spec.md</text>
    <text x="680" y="488" text-anchor="middle" font-size="10.5" font-weight="600" fill="#1e40af">.scratch/&lt;slug&gt;/</text>
    <text x="680" y="506" text-anchor="middle" font-size="10.5" font-weight="600" fill="#1e40af">tickets/NN-*.md</text>

    <rect x="780" y="430" width="130" height="88" rx="8" fill="#eff6ff" stroke="#60a5fa"></rect>
    <text x="845" y="458" text-anchor="middle" font-size="11.5" font-weight="600" fill="#1e40af">src/ + tests/</text>
    <text x="845" y="478" text-anchor="middle" font-size="11.5" font-weight="600" fill="#1e40af">review report</text>
    <text x="845" y="498" text-anchor="middle" font-size="11.5" font-weight="600" fill="#1e40af">failsafe snapshots</text>

    <rect x="940" y="430" width="140" height="88" rx="8" fill="#eff6ff" stroke="#60a5fa"></rect>
    <text x="1010" y="458" text-anchor="middle" font-size="11.5" font-weight="600" fill="#1e40af">docs/issues/*.md</text>
    <text x="1010" y="478" text-anchor="middle" font-size="11.5" font-weight="600" fill="#1e40af">_summary.md</text>
    <text x="1010" y="498" text-anchor="middle" font-size="11.5" font-weight="600" fill="#1e40af">diagnosis records</text>

    <!-- Bottom auxiliary band -->
    <line x1="20" y1="546" x2="1100" y2="546" stroke="#f59e0b" stroke-width="1.5" stroke-dasharray="6 4"></line>
    <rect x="10" y="558" width="1100" height="48" rx="10" fill="#fffbeb" stroke="#f59e0b" stroke-dasharray="5 3"></rect>
    <text x="28" y="587" font-size="15" font-weight="700" fill="#b45309">Auxiliary Skills</text>
    <text x="225" y="587" text-anchor="middle" font-size="14" font-weight="600" fill="#d97706">research</text>
    <text x="355" y="587" text-anchor="middle" font-size="14" font-weight="600" fill="#d97706">prototype</text>
    <text x="500" y="587" text-anchor="middle" font-size="14" font-weight="600" fill="#d97706">failsafe-loop</text>
    <text x="640" y="587" text-anchor="middle" font-size="14" font-weight="600" fill="#d97706">to-issues</text>
    <text x="775" y="587" text-anchor="middle" font-size="14" font-weight="600" fill="#d97706">improve-arch</text>
    <text x="905" y="587" text-anchor="middle" font-size="14" font-weight="600" fill="#d97706">teach</text>
    <text x="1025" y="587" text-anchor="middle" font-size="14" font-weight="600" fill="#d97706">handoff</text>
  </svg>
</div>

## 3. Operating Manual: Phase-by-Phase Guidance

The following is detailed operational guidance for each phase of the software engineering life cycle: which skills to use at each phase, how to use them, and which artifacts to expect.

### 3.1 Phase 0: Bootstrap (Collaboration Foundation)

**Goal**: Establish the collaboration foundation for the team (agents and humans).

**Skills and logical relations**: [mandatory single skill]

- **[`setup-matt-pocock-skills`](#setup-matt-pocock-skills)**
    - **How to use**: at the very start of the project, invoked directly by the human.
    - **What happens**: it generates `AGENTS.md` at the repository root and establishes conventions under `docs/agents/` for the issue tracker, triage labels, and domain docs.

**Phase artifacts**:
- `AGENTS.md`: collaboration foundation and agent behavior guide at the repository root
- `docs/agents/issue-tracker.md`: dual-stream tracker convention (Tickets / Issues)
- `docs/agents/triage-labels.md`: triage role and status label definitions
- `docs/agents/domain.md`: single-context domain documentation convention

### 3.2 Phase 1: Requirements Elicitation

**Goal**: Distill definite stakeholder concerns, goals, and boundaries out of vague slogans.

**Skills and logical relations**: [mutually exclusive pick ×1 + on-demand auxiliary]

- **[`grill-with-docs`](#grill-with-docs)** (choose one over wayfinder; fits small, well-bounded requirements)
    - **How to use**: throw out an initial idea and invoke the skill to grill you in depth.
    - **What happens**: multi-round dialogue forces hidden assumptions into the open; the embedded reusable `domain-modeling` writes terms into `CONTEXT.md` the moment they are settled, and deposits ADRs with restraint.
- **[`wayfinder`](#wayfinder)** (choose one over grill; fits large, fuzzy requirements)
    - **How to use**: invoke when requirements are large enough to span days of discussion, or when the road ahead is shrouded in fog.
    - **What happens**: instead of grilling directly, it builds a navigation map (`.scratch/<effort>/map.md`) and splits the problem into sub-tickets (`.scratch/<effort>/tickets/NN-<slug>.md`) to be resolved one by one. When working a specific ticket, switch to `grill-with-docs` or `research`.
- **[`to-questionnaire`](#to-questionnaire)** (on-demand auxiliary)
    - **How to use**: invoke when key information is not in your hands.
    - **What happens**: generates a structured questionnaire to send to external stakeholders for requirement gathering.

**Phase artifacts**:
- `.scratch/<effort>/map.md`: (if using `wayfinder`) fog-navigation map and resolution index
- `.scratch/<effort>/tickets/NN-<slug>.md`: (if using `wayfinder`) exploration sub-tickets
- `CONTEXT.md`: initial domain vocabulary and core entity definitions (terms land as soon as they settle; convergence continues through Phase 2)
- `docs/adr/NNNN-*.md`: initial architecture decision records (if key decisions settled during grilling)
- `to-questionnaire-*.md`: (if used) outbound stakeholder questionnaire (temporary, not committed)

### 3.3 Phase 2: Architecture and Boundary Design

**Goal**: Identify quality attributes, unify the domain language, design logical boundaries, synthesize them into a complete architecture description, then convert them into enforced constraints. This is the deep-water work chain from cognition to code.

**Skills and logical relations**: [sequential collaboration, execute in order]

1. **[`domain-modeling`](#domain-modeling)** (step 1: cognition layer)
    - **How to use**: invoke immediately after clarifying requirements.
    - **What happens**: unifies team vocabulary, identifies core entities, and deposits architecture decision records (ADRs). This is the prerequisite for all subsequent work. If Phase 1 has already produced an initial `CONTEXT.md` / ADR via `grill-with-docs`, this step performs incremental challenge and convergence on top of it rather than starting from zero.
2. **[`codebase-design`](#codebase-design)** (step 2: design layer)
    - **How to use**: once concepts are unified, use it to plan the code structure.
    - **What happens**: helps you cut module seams, ensuring high cohesion and testability by construction.
3. **[`to-arch`](#to-arch)** (step 3: synthesis layer)
    - **How to use**: invoke once unified language, key decisions, and seam plans are basically ready.
    - **What happens**: synthesizes the cognition scattered across `CONTEXT.md`, ADRs, quality attribute scenarios, and map resolutions into one complete architecture description — articulating design intent, stakeholder concerns, module decomposition, and necessary views. Upstream it is the "sink" where decisions converge; downstream it is the "source" for both the enforcement layer and the specification layer: `governed-arch` translates its boundary definitions into TOML, and `to-spec` draws its global frame from it.
    - **Artifacts**: two — the architecture description `docs/architecture.md` (structure follows `docs/templates/ARCHITECTURE-DESCRIPTION-FORMAT.md`; views embedded or relatively linked), and the implementation process plan `docs/action-plan.md` — prescribing the order of governance scaffolding first, module implementations next, integration tests last, marking which parts may run in parallel, which must serialize, and with what rationale.
    - **Boundary**: the `depends_on` topology in `architecture.toml` only constrains runtime "who may import whom"; it does not prescribe construction order — by leaning on seams with test doubles coming first, upper modules can equally be implemented and unit-tested early; what the topology really decides is integration order. Step ordering inside a module/feature belongs to `to-spec` and `to-tickets`; `action-plan.md` only orchestrates across modules.
4. **[`governed-arch`](#governed-arch)** (step 4: constraint layer)
    - **How to use**: translate boundary definitions from the architecture description into physically enforced constraints.
    - **What happens**: generates `architecture.toml` and `module.toml`, plus automated tests (such as `test_module_boundaries.py`), acting as the "enforcer" that keeps the architecture intact.

**Phase artifacts**:
- `CONTEXT.md`: converged, finalized unified domain language
- `docs/adr/NNNN-*.md`: finalized architecture decision records
- `docs/architecture.md`: global architecture description (synthesized by `to-arch`; includes stakeholders, viewpoints/views, quality attributes)
- `docs/action-plan.md`: system-wide wave-based construction plan and project recovery point (maintained by `to-arch`)
- `architecture.toml`: project-level architecture boundaries and dependency rules
- `<module>/module.toml`: per-module private/public boundary definitions and test constraints

### 3.4 Phase 3: Specification and Ticket Decomposition

**Goal**: Turn abstract designs and requirements into executable specification documents and concrete development tasks.

**Scope boundary**: cross-module system-level construction order has already been fixed by Phase 2's `docs/action-plan.md` (including the positions of governance scaffolding and integration tests); the `to-spec` and `to-tickets` of this phase only own step ordering inside a single feature — neither crosses into the other's scope. This phase runs automated under `impl-loop` or standalone on demand.

**Skills and logical relations**: [sequential collaboration, execute in order]

1. **[`to-spec`](#to-spec)**
    - **How to use**: invoke once architecture and requirements have stabilized (or invoked automatically by `impl-loop`).
    - **What happens**: generates a structured `spec.md`, clarifying functional requirements, non-functional requirements, and acceptance criteria.
2. **[`to-tickets`](#to-tickets)**
    - **How to use**: invoke based on `spec.md` (or invoked automatically by `impl-loop`).
    - **What happens**: following the conventions of `docs/agents/issue-tracker.md`, decomposes the specification into individual development tickets under `.scratch/<feature-slug>/tickets/`, declaring blocking relations ticket by ticket.

**Phase artifacts**:
- `.scratch/<feature-slug>/spec.md`: single-feature specification document
- `.scratch/<feature-slug>/tickets/NN-<slug>.md`: vertical-slice development tickets (with a Blocked-by dependency DAG, numbered from 01)

### 3.5 Phase 4: Implementation and the Iterative Loop

**Goal**: Write code that satisfies the specification, completing review, test-gate validation, and plan progress write-back within tight loops.

**Skills and logical relations**: [high-frequency loop: pick up ticket -> implement (TDD + review) -> gate validation -> on-completion write-back]

- **[`implement`](#implement)** (single-slice execution trunk, internalizing [`tdd`](#tdd) and [`code-review`](#code-review))
    - **How to use**: invoked internally by `impl-loop` per ticket, or called directly by human for single-ticket work.
    - **What happens**:
      1. **TDD red-green loop**: writes a failing test first at the planned seam, then the minimal implementation to green, guaranteeing regression coverage;
      2. **Type checks and unit testing**: runs typecheck and unit tests continuously;
      3. **Pre-merge review**: calls `code-review` before commit for dual-axis inspection (standards axis and spec axis);
      4. **Commit**: commits verified code and tests together to the current branch.
      *(Note: if architecture proves unsound, no seam can be found, or dependencies leak, pause implementation and fall back to `codebase-design` to re-cut seams)*
- **[`governed-arch`](#governed-arch)** (on-demand auxiliary: continuous validation)
    - **How to use**: invoke anytime while writing or refactoring cross-module code, or run its test scripts in CI.
    - **What happens**: runs boundary validation and tells you immediately whether a newly added `import` violates the architecture rules.

**Phase artifacts**:
- `src/` and `tests/`: code passing layered verification plus unit/integration test cases
- `docs/action-plan.md`: updated wave progress and new resume point (written back automatically by `impl-loop`)
- (after merge and release, clean up the temporary `.scratch/<feature-slug>/` directory)

### 3.6 Cross-Phase Delivery Orchestrator: [`impl-loop`](#impl-loop)

In the SVG panorama diagram, **Phase 3 (Specification & Decomposition)** and **Phase 4 (Iterative Loop)** are encompassed by the outer green dashed box, powered by the core orchestration skill **`impl-loop`**.

#### 3.6.1 Background and Core Value

In traditional or single-slice agent workflows, developers frequently switch between multiple isolated commands: invoking `/to-spec` to draft specs, `/to-tickets` to decompose tickets, typing `/implement` per ticket, running manual test gate commands, and manually updating `docs/action-plan.md`. This fragmented interaction pattern is highly prone to **state drift** and skipped verification gates.

`impl-loop` acts as the **end-to-end delivery engine**. It links Phase 3 specification artifacts with Phase 4 coding, testing, and review into a unified, gated delivery pipeline:

```text
               ┌───────────────────── impl-loop Delivery Loop ─────────────────────┐
               │                                                                   │
/to-arch ────> │  /to-spec ──> /to-tickets ──> [ per ticket: /implement ──> Gate ] │ ──> write back action-plan.md (done)
(construction  │  (Phase 3)      (Phase 3)                   (Phase 4)      (tests)│     advance wave resume point
 plan provider)└───────────────────────────────────────────────────────────────────┘
```

#### 3.6.2 Division of Labor & Responsibility Matrix

| Skill | Role | Core Responsibility |
| :--- | :--- | :--- |
| **`impl-loop`** | **Delivery Orchestrator** | Chains the entire workflow, detects and actively fulfills missing prerequisites, drives ticket implementations, enforces test gates, manages resume points, and atomically writes back to `action-plan.md` on completion |
| **`to-spec`** | **Spec Drafter** | Explores the codebase and drafts structured specification documents `spec.md` using domain vocabulary |
| **`to-tickets`** | **Ticket Decomposer** | Breaks `spec.md` into vertical-slice temporary tickets `tickets/NN-*.md`, declaring a Blocked-by dependency DAG |
| **`implement`** | **Single-Slice Executor** | Implements single tickets using `tdd` red-green cycles, runs unit tests, calls `code-review` before commit, and commits code |
| **`to-arch`** | **Top-Level Planner** | Provides the whole-system wave construction plan `docs/action-plan.md` and layered test strategy (`docs/architecture.md`) |

#### 3.6.3 Atomic Write-Back and Resume Semantics

- **Spec Completion Atomic Write-Back**: Once all tickets for a spec are resolved and the integration gate passes, `impl-loop` automatically marks the slice `done (<final_commit_sha>)` in `docs/action-plan.md`, records the test gate command, and advances the header resume point to the next wave, keeping construction progress 100% true.
- **Resume Semantics**: `impl-loop` is idempotent and resumable by design. Any new session can run `/impl-loop` to resume seamlessly from `docs/action-plan.md`.

### 3.7 Phase 5: Operation, Diagnosis, and Evolution

**Goal**: After go-live or milestone formation, respond to external feedback, troubleshoot production failures, and update global governance assets.

**Skills and logical relations**: [triggered by external events]

- **[`to-issues`](#to-issues)** (external feedback trigger, capture entry point)
    - **How to use**: invoke first upon receiving a bug report, small feature request, or standalone task.
    - **What happens**: writes it into the permanent issue stream under `docs/issues/` (global numbering, Type / Status / Created lines) and refreshes the `_summary.md` index; files persist permanently after fix closure.
- **[`triage`](#triage)** (triggered after items enter the stream)
    - **How to use**: classify and route entries across both streams — long-lived issues in `docs/issues/` as well as temporary tickets in `.scratch/`.
    - **What happens**: moves entries among the five triage roles (e.g. `needs-triage` → `ready-for-agent`) and sets processing order.
- **[`diagnosing-bugs`](#diagnosing-bugs)** (production failure or performance bottleneck trigger)
    - **How to use**: invoke when a complex bug or performance regression appears and you do not know where to start.
    - **What happens**: starts a dedicated diagnosis loop, digging deep into code or logs to find the root cause.
- **[`governed-arch`](#governed-arch)** (milestone trigger)
    - **How to use**: invoke before a major release or an operations-team handover.
    - **What happens**: regenerates/updates the latest module-architecture HTML documentation and dependency graphs in one shot, as outward-facing delivery assets.

**Phase artifacts**:
- `docs/issues/NNN-<slug>.md`: globally numbered permanent issues (three-digit numbering such as 001-fix-login.md)
- `docs/issues/_summary.md`: global issue index table (categorized by status and priority, kept in sync in real time)
- failure diagnosis analysis reports and root cause analysis records
- re-exported latest module architecture views and the evolution knowledge base

## 4. Phase Artifacts and Template References

To keep engineering quality traceable and consistent, the following table pins down the core artifacts expected from each phase together with their reference templates.

| Phase | Core artifacts (standard relative paths) | Recommended skills | Template/convention reference |
| :--- | :--- | :--- | :--- |
| **0. Bootstrap** | `AGENTS.md`<br>`docs/agents/issue-tracker.md`<br>`docs/agents/triage-labels.md` | `setup-skills` | issue-tracker.md |
| **1. Requirements elicitation** | `.scratch/<effort>/map.md`<br>`CONTEXT.md` (initial)<br>`docs/adr/NNNN-*.md` (initial) | `grill-with-docs`<br>`wayfinder` | QAS-FORMAT.md<br>CONTEXT-FORMAT.md<br>ADR-FORMAT.md |
| **2. Architecture design** | `CONTEXT.md` (final)<br>`docs/adr/NNNN-*.md`<br>`docs/architecture.md`<br>`docs/action-plan.md`<br>`architecture.toml` / `module.toml` | `domain-modeling`<br>`codebase-design`<br>`to-arch`<br>`governed-arch` | ARCHITECTURE-DESCRIPTION-FORMAT.md<br>VIEWPOINT-CATALOG.md<br>ADR-FORMAT.md |
| **3. Spec decomposition** | `.scratch/<feature-slug>/spec.md`<br>`.scratch/<feature-slug>/tickets/NN-*.md` | `to-spec`<br>`to-tickets`<br>(orchestrated by `impl-loop`) | SPEC-FORMAT.md |
| **4. Iterative implementation** | `src/` + `tests/`<br>`docs/action-plan.md` (progress write-back) | `impl-loop`<br>`implement` (incl. `tdd`/`review`)<br>`governed-arch` | per project conventions |
| **5. Operation & evolution** | `docs/issues/NNN-*.md`<br>`docs/issues/_summary.md`<br>diagnosis records / updated architecture diagrams | `to-issues`<br>`triage`<br>`diagnosing-bugs`<br>`governed-arch` | HANDOFF-FORMAT.md |

> Living-document note: `CONTEXT.md` and ADRs are living documents evolving across phases, owned by no single phase — created lazily in Phase 1 by the `domain-modeling` embedded in `grill-with-docs` (lazy file creation; terms land the moment they settle), then challenged and converged to final form in Phase 2 by explicitly invoking `domain-modeling`.

## 5. Auxiliary Skills and Practical Decision Table

Beyond the trunk path there exists a set of "auxiliary/cross-cutting skills" (corresponding to the bottom band in the SVG). They do not directly advance pipeline state transitions; like a plug-in toolbox, they fire on demand when the trunk is blocked, knowledge gaps exist, context needs restructuring, or high-risk operations occur (invocations should be non-blocking and highly purposeful; return to the trunk promptly once the specific problem is solved).

### 5.1 Auxiliary Skills at a Glance

| Skill | Trigger timing and purpose |
| :--- | :--- |
| [`research`](#research) | Key facts not in hand (API design, library capabilities, competitor approaches) |
| [`prototype`](#prototype) | High-uncertainty risk; scout ahead before formal implementation |
| [`failsafe-loop`](#failsafe-loop) | Extremely error-prone or destructive changes; force step-by-step verification and snapshots |
| [`to-issues`](#to-issues) | Capture bug reports, small feature requests, or standalone tasks into the permanent stream |
| [`improve-codebase-architecture`](#improve-codebase-architecture) | Design cannot land, or maintenance-period structure blocks new features |
| [`teach`](#teach) | Complex domain experience or scaffolding worth distilling, or onboarding new members |
| [`handoff`](#handoff) | Session end or task switch; compress context and leave a clean resume point |
| [`to-questionnaire`](#to-questionnaire) | Key information held by external stakeholders |

### 5.2 Practical Decision Table

| Current blocker / scenario | Preferred skill | Action |
| --- | --- | --- |
| Requirements huge and fuzzy, cannot be covered in one pass | [`wayfinder`](#wayfinder) | Build a navigation map and split out exploration sub-tickets |
| Single requirement but loose logic, many hidden assumptions | [`grill-with-docs`](#grill-with-docs) | Grill deeply to surface hidden assumptions; deposit terms and ADRs on the spot |
| Key facts not in hand | [`research`](#research) / [`to-questionnaire`](#to-questionnaire) | Research first-hand facts or send out stakeholder questionnaires |
| Term drift, concept confusion, unclear entity definitions | [`domain-modeling`](#domain-modeling) | Unify team vocabulary; maintain `CONTEXT.md` and ADRs |
| Logical boundaries and seams unclear | [`codebase-design`](#codebase-design) | Plan deep modules and testable seams |
| Need an architecture description articulating design intent and module decomposition | [`to-arch`](#to-arch) | Synthesize `docs/architecture.md` and the construction-wave `docs/action-plan.md` |
| Need enforced architecture and directory boundaries | [`governed-arch`](#governed-arch) | Generate TOML boundary rules and automated architecture tests |
| Logic converged; need execution and acceptance contracts | [`to-spec`](#to-spec) | Draft the structured specification `spec.md` |
| Requirements and architecture settled; need development slices | [`to-tickets`](#to-tickets) | Decompose into vertical-slice temporary tickets with a declared blocking DAG |
| Spec and tickets are ready, need end-to-end delivery and plan progress | [`impl-loop`](#impl-loop) | Chain ticket implementations, test gates, and action-plan progress write-back |
| Bug reports, small features, or standalone tasks need long-term tracking | [`to-issues`](#to-issues) | Record into the globally numbered permanent issue stream and sync the index |
| Ready to start coding | [`implement`](#implement) / [`tdd`](#tdd) | Implement features and unit tests in red-green-refactor rhythm |
| During implementation, design will not land, boundaries leak | [`improve-codebase-architecture`](#improve-codebase-architecture) | Re-cut seams and update ADRs / architecture description |
| Extremely destructive change needing step-wise review | [`failsafe-loop`](#failsafe-loop) | Introduce staged snapshot comparison and strict risk gates |
| Need to verify code against standards and spec | [`code-review`](#code-review) | Run dual-axis sub-agent review over standards and spec |
| Task handover or session end | [`handoff`](#handoff) | Compress session context into a clear handover point |
| Production troubleshooting or performance bottleneck localization | [`diagnosing-bugs`](#diagnosing-bugs) | Build a red/green reproduction loop and falsifiable hypotheses to find root cause |

## Appendix: Skill Quick Reference {#skill-appendix}

Every skill appearing in this panorama is summarized here, ordered by trunk flow; each entry gives "when to use it, what it does, how it works". `to-issues` is this repository's original skill (mine), complementary to upstream `to-tickets` rather than a name clash.

### setup-matt-pocock-skills
- **When to use**: at project start (Phase 0), to establish the agent-human collaboration foundation.
- **What it does**: generates `AGENTS.md` and establishes issue-tracker, triage-label, and domain-doc conventions under `docs/agents/`.
- **How it works**: first surveys the repo state (remote and any existing `AGENTS.md`), then asks section by section to confirm the three configuration groups, writing docs and `AGENTS.md` after draft confirmation.

### wayfinder
- **When to use**: requirements huge and fuzzy, spanning multiple days of discussion (Phase 1; choose one over `grill-with-docs`).
- **What it does**: builds navigation map `map.md`, splits the problem into tickets solved one by one; when working a specific ticket, hands off to `grill-with-docs` or `research`.
- **How it works**: first fixes destination and scope via grilling, then breadth-first maps the fog zones, creating map and decision tickets; after claiming a frontier ticket, parses and records resolutions until closed — one ticket per session.

### grill-with-docs
- **When to use**: small, well-bounded requirements (Phase 1; choose one over `wayfinder`).
- **What it does**: multi-round deep grilling surfaces hidden assumptions while recording terms and decisions along the way.
- **How it works**: runs a grilling session pressing on hidden assumptions question by question, maintaining vocabulary and ADRs with `domain-modeling`, producing a document combining Q&A results.

### domain-modeling
- **When to use**: invoked both as a standalone skill as step 1 of Phase 2, and embedded by `grill-with-docs` in Phase 1 (terms written into `CONTEXT.md` as they settle).
- **What it does**: unifies team vocabulary, identifies core entities, deposits ADRs — the prerequisite for all subsequent work.
- **How it works**: flags term conflicts against the glossary in real time and proposes canonical terms; probes boundaries by constructing scenarios; updates `CONTEXT.md` while discussing, writing ADRs when necessary.

### codebase-design
- **When to use**: planning code structure after concepts unify (Phase 2 step 2).
- **What it does**: cuts module seams, ensuring high cohesion and testability.
- **How it works**: describes modules and interfaces in unified vocabulary; judges module depth with the "delete test"; optimizes via dependency injection, returning results, narrowing interface surface — remembering "one adapter is a fake seam, two make a real one".

### to-arch
- **When to use**: once domain language, key decisions, and seam plans are basically ready (Phase 2 step 3), synthesize the first architecture description and implementation plan (init mode); during implementation, write back progress whenever any slice starts/finishes/blocks (update-progress mode); after milestones or major decisions, reconcile then re-converge (reconcile mode). This repository's original skill (mine); template copies bundled, same-named files under project-local `docs/templates/` take precedence.
- **What it does**: synthesizes `CONTEXT.md`, ADRs, quality attribute scenarios, and map resolutions into a complete architecture description `docs/architecture.md` — articulating design intent, stakeholder concerns, module decomposition, and necessary views; also produces the implementation process plan `docs/action-plan.md`, fixing the order of governance scaffolding first, module implementations next, integration tests last, plus parallel groupings (note `depends_on` does not decide construction order). Upstream it consolidates scattered decisions; downstream it serves as source of truth for `governed-arch`'s TOML translation and `to-spec`'s global frame.
- **How it works**: inventories existing artifacts first, listing decisions and viewpoint choices; gaps are routed by type to `grill-with-docs`/`wayfinder`/`research`/`domain-modeling`, insisting on zero fabrication. Then drafts the architecture description and the wave-based action plan (with parallel grouping and serialization rationale) section by section, landing each only after user confirmation per section. The action plan is a semi-finished product's self-narrating file — the header "current position" line and per-slice statuses update as work proceeds, so any fresh session reads just it to know where things stand and where to resume; milestones reconcile the TOML projection against real implementation via reconcile mode.

### governed-arch
- **When to use**: when designs become physical constraints, plus continuous validation during implementation and release (Phases 2/4/5).
- **What it does**: generates `architecture.toml`, `module.toml`, and automated boundary tests, acting as the "enforcer" keeping architecture intact; generates architecture HTML documentation and dependency graphs at release time.
- **How it works**: declares structure and module boundaries in TOML; public APIs lock interface signatures upon exposure; cross-module access goes only through facade gateway imports; governance tests gate everything, and results render into HTML documentation.

### to-spec
- **When to use**: after architecture and requirements stabilize (Phase 3 step 1).
- **What it does**: generates a structured `spec.md`, clarifying functional requirements, non-functional requirements, and acceptance criteria.
- **How it works**: explores the codebase first, drafts the spec in domain vocabulary, confirms highest-value seams with the user, then writes `spec.md` from the template, publishes, and marks ready-for-agent.

### to-tickets
- **When to use**: decomposing a ready specification into executable development slices (Phase 3 step 2). Upstream original skill, byte-for-byte restored per locked baseline.
- **What it does**: following `docs/agents/issue-tracker.md` conventions, drafts the spec as vertical-slice temporary dev tickets under `.scratch/<feature-slug>/tickets/` (`NN-<slug>.md`), annotating blocking relations per ticket; wide refactorings switch to expand-contract sequences.
- **How it works**: confirms granularity and dependencies with the user, then writes into `.scratch/<feature-slug>/tickets/`; tickets are short-term planning scaffolding discarded when the feature ends — no index, numbers start from `01` in dependency order, never reused across features.

### impl-loop
- **When to use**: when spec and tickets are ready and you need to drive the end-to-end delivery cycle, or continue an in-flight effort (Phase 3/4 orchestrator). This repository's original skill (mine).
- **What it does**: chains `/to-spec` -> `/to-tickets` -> `/implement` -> test gates, closing ticket by ticket and keeping the resume point true; when the spec completes and integration gate passes, automatically writes back to `docs/action-plan.md` to mark the slice done and advance the wave.
- **How it works**: claims tickets along the DAG and hands to `implement`, gating single tickets on unit tests, and closing the spec on integration tests; on completion performs atomic write-back: update slice status row, update Notes gate record, advance Resume Point header, and retire temporary scaffolding.

### to-issues
- **When to use**: capturing bug reports, small feature requests, or standalone tasks into the repository-level permanent issue stream; not for splitting specs into slices (that is `/to-tickets`' job). This repository's original skill (mine).
- **What it does**: creates `NNN-<slug>.md` files under `docs/issues/` with three-digit globally increasing numbers (never reused), carrying Type / Status / Created metadata and an Evidence section, refreshing the `_summary.md` global index in sync.
- **How it works**: gathers context first; bugs get low-cost reproduction attempts without blocking recording; life cycle needs-triage ⇄ needs-info → ready-for-agent | ready-for-human → fixed, wontfix reachable from any state, duplicates recorded as wontfix with a pointer. Conventions in `docs/agents/issue-tracker.md`.

### implement
- **When to use**: picking up a ticket to write code (Phase 4 trunk, paired with `tdd`).
- **What it does**: implements features in TDD rhythm; if architecture proves unsound (no seam found, tests failing), pauses and falls back to `codebase-design`.
- **How it works**: implements at the planned seam using `tdd`, running type checks and unit tests periodically en route and the full suite last; hands to `code-review` and commits when done.

### tdd
- **When to use**: the mandatory rhythm accompanying `implement` (Phase 4).
- **What it does**: guarantees test coverage via red-green-refactor loops so every feature is regression-verifiable.
- **How it works**: writes a failing test first, then the minimal implementation to green, one slice at a time; tests target public behavior only, avoiding implementation coupling and tautological tests.

### code-review
- **When to use**: feature complete, before merging into the main branch (Phase 4 pre-merge trigger).
- **What it does**: checks conformance against `spec.md`, repository standards, and specification requirements; outputs review verdicts.
- **How it works**: pins the diff base first and confirms non-empty; locates the spec source and coding-standard docs; dispatches parallel sub-agents reviewing along the two axes of "standards" and "spec", finally aggregating reports presented axis by axis.

### handoff
- **When to use**: session end, or handing work to another agent/human (Phase 4).
- **What it does**: compresses current context, leaving the next taker a clear starting point.
- **How it works**: compresses the session into a handoff document stored in `.scratch`, referencing existing artifacts instead of duplicating content, sanitized, with a suggested skill checklist attached.

### failsafe-loop
- **When to use**: changes that are extremely error-prone or destructive (Phase 4 on-demand intervention).
- **What it does**: forces phased execution, per-step verification, and snapshot comparison; stop on failure, guarding the high-risk gate.
- **How it works**: defines boundaries, invariants, and baselines before every step, then passes four gates in turn — tests, workflow, audit, comparison; unexpected drift halts and escalates immediately, and passage ends with a formatted commit and report.

### triage
- **When to use**: classifying and routing items after they enter the streams (Phase 5 trigger); applies both to long-lived issues in `docs/issues/` and temporary tickets in `.scratch/`.
- **What it does**: moves entries among the five triage roles (e.g. `needs-triage` → `ready-for-agent`), setting processing order.
- **How it works**: classifies by Type first (bug/enhancement etc.), collects context, deduplicates, and filters out-of-scope; verifies claims by reproduction, supplements info via grilling when needed, finally applies state transitions and writes an agent brief or flips to needs-info.

### diagnosing-bugs
- **When to use**: complex bugs or performance regressions where you don't know where to start (Phase 5 failure trigger).
- **What it does**: starts a dedicated diagnosis loop, digging into code and logs, locating root causes and closing the loop.
- **How it works**: builds a tight red/green reproduction loop first, reproducing and minimizing to load-bearing elements; generates 3–5 falsifiable hypotheses tested one by one; writes a regression test before fixing; cleans up and prevents recurrence last.

### research
- **When to use**: key facts not in hand — how to design an API, whether a library supports a feature, what competitors do (on-demand auxiliary).
- **What it does**: produces a Markdown research report based on high-trust sources; conclusions flow back into the trunk.
- **How it works**: dispatches background agents to research in parallel, tracking only first-hand authoritative sources with citations; results written as Markdown into the agreed repo location.

### prototype
- **When to use**: high-uncertainty risk — interaction flows, tech stack, state machine viability (before formal implementation).
- **What it does**: writes and runs throwaway code to validate assumptions; conclusions backfill ADRs or architecture design, code discarded after validation.
- **How it works**: first classifies logic vs UI question; uses temporary code, single-command runs, no persistence; shows full state after every action; commits to a temporary branch for traceability once decisions are absorbed.

### improve-codebase-architecture
- **When to use**: during implementation, design will not land (no seam found, module coupling), or maintenance-period structure blocks new features.
- **What it does**: re-cuts seams or refactors responsibilities, coordinating with `governed-arch` to update TOML constraints, locking in refactor gains.
- **How it works**: defines scan scope first to find hot-spot modules, generating an HTML review report; after picking candidates, digs into design via grilling, updating the domain model while deciding, writing back TOML constraints after refactoring.

### teach
- **When to use**: complex domain problems solved or unique scaffolding distilled, or preparing to onboard new members.
- **What it does**: extracts best practices, implicit rules, and domain-specific vocabulary, generating tutorials, glossaries, and other training material, converting them into long-lived organizational assets.
- **How it works**: clarifies mission and gathers high-trust resources first; one HTML per lesson, small and quickly completable; builds tight feedback loops with quiz exercises, producing references and learning records.

### to-questionnaire
- **When to use**: decisions depend on information held by stakeholders, experts, or third parties that you cannot supply alone.
- **What it does**: turns knowledge gaps into a Markdown questionnaire (`to-questionnaire-<slug>.md`) for the other party to fill; upon return, resume clarification on the trunk.
- **How it works**: grills only the sender (whom the questionnaire goes to, what answers are needed), targeting knowledge gaps between user and recipient; writes the Q&A sheet from template, important questions first.
