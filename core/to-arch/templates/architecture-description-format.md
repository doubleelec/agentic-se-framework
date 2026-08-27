# Architecture Description Format

> to-arch bundled copy - provenance: `docs/templates/ARCHITECTURE-DESCRIPTION-FORMAT.md` in the Skills workspace (2026-08-26). If the project carries its own copy at that path, the project-local file takes precedence.

This document defines the standard structure for an Architecture Description, based on ISO/IEC/IEEE 42010.
This artifact is typically generated and maintained during the architecture design phase.

## 1. Identification and Scope
- **System Name**: Name of the system being described.
- **Purpose**: A brief statement of what the system does and why it exists.
- **Scope**: Boundaries of the architecture described in this document.

## 2. Stakeholders and Concerns
List the key stakeholders and their primary architectural concerns.
- **[Stakeholder Role]**: e.g., End User, System Administrator, Developer, Business Sponsor.
  - **Concerns**: e.g., Data privacy, System uptime, Maintainability, Time-to-market.

## 3. Quality Attribute Scenarios (QAS)
Reference or list the highest priority Quality Attribute Scenarios that drive the architecture.
*(See `QUALITY-ATTRIBUTE-SCENARIO-FORMAT.md` for the format)*
- **Scenario 1**: ...
- **Scenario 2**: ...

## 4. Viewpoints and Views
Describe the system from multiple perspectives to address the identified concerns.
*(Only include views that are necessary to address the concerns of the stakeholders).*

### 4.1 Context View
- **Purpose**: Shows the system's boundaries and its interactions with external entities.
- **Model/Diagram**: (Link to diagram or textual description)
- **Elements**: External systems, users, data feeds.

### 4.2 Logical Decomposition View
- **Purpose**: Shows the internal structure, modules, and their responsibilities.
- **Model/Diagram**: (Link to module dependency graph or TOML definition)
- **Elements**: Core modules, interfaces, dependencies.

### 4.3 Runtime/Concurrency View (Optional)
- **Purpose**: Shows how the system behaves during execution, focusing on processes, threads, and data flow.
- **Model/Diagram**: (Link to sequence diagrams or activity diagrams)
- **Elements**: Processes, message queues, event streams.

### 4.4 Deployment/Physical View (Optional)
- **Purpose**: Shows the mapping of software components to physical or virtual infrastructure.
- **Model/Diagram**: (Link to infrastructure diagram)
- **Elements**: Servers, containers, networks, databases.

## 5. Architecture Decisions
List or link to the key Architecture Decision Records (ADRs) that shape this architecture.
- [ADR-0001: Monolith vs Microservices](docs/adr/0001-monolith-vs-microservices.md)
- [ADR-0002: Event-Driven Billing](docs/adr/0002-event-driven-billing.md)

## 6. Constraints and Risks
- **Technical Constraints**: e.g., Must run on existing on-premise hardware.
- **Business Constraints**: e.g., Must launch by Q3.
- **Identified Risks**: Architectural risks and mitigation strategies.
