# Quality Attribute Scenario Format

Quality Attribute Scenarios (QAS) are used to turn vague requirements (like "high performance") into concrete, testable, and evaluable statements.

## Structure

Each scenario should include:

- **Source**: The entity (human, system, environment) that generates the stimulus.
- **Stimulus**: The condition that needs to be responded to (e.g., a burst of traffic, a hardware failure).
- **Artifact**: The part of the system that is stimulated.
- **Environment**: The conditions under which the stimulus occurs (e.g., normal operation, peak load).
- **Response**: The activity that occurs as a result of the stimulus.
- **Response Measure**: The measurable criteria for the response (e.g., latency < 200ms, 99.9% availability).

## Examples

### Performance
> **Scenario**: When a user submits a search query (Stimulus) under normal load (Environment), the system (Artifact) should return results (Response) within 500ms (Response Measure).

### Availability
> **Scenario**: When a database node fails (Stimulus) during peak hours (Environment), the load balancer (Artifact) should redirect traffic to a healthy node (Response) within 5 seconds, and the system should remain fully operational (Response Measure).

### Modifiability
> **Scenario**: When a developer wants to add a new payment gateway (Stimulus) during development (Environment), the payment module (Artifact) should allow the addition without modifying existing gateway implementations (Response) within 2 person-days (Response Measure).

## Usage in Architecture
QAS are recorded in `CONTEXT.md` or as part of an ADR to justify architectural choices.
