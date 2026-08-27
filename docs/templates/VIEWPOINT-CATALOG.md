# Viewpoint Catalog

This catalog defines the standard architectural viewpoints available for use in Architecture Descriptions.
A Viewpoint establishes the conventions, rules, and languages for constructing a specific type of View to address a specific set of concerns.

## 1. Context Viewpoint
- **Concerns Addressed**: System scope, external dependencies, integration points, user roles.
- **Typical Stakeholders**: Business Sponsors, Product Managers, System Integrators.
- **Required Elements**: The System (as a black box), External Actors (Human or System), Interaction links.
- **Recommended Notation**: C4 Model (System Context diagram), UML Use Case Diagram, or simple block diagrams.

## 2. Logical Decomposition Viewpoint
- **Concerns Addressed**: Modularity, responsibilities, separation of concerns, maintainability, dependency management.
- **Typical Stakeholders**: Software Architects, Developers.
- **Required Elements**: Modules/Components, Interfaces/APIs, Dependency relationships.
- **Recommended Notation**: C4 Model (Container/Component diagrams), UML Component Diagram, `architecture.toml` declarations.

## 3. Runtime/Concurrency Viewpoint
- **Concerns Addressed**: Performance, scalability, deadlock avoidance, data consistency, asynchronous behavior.
- **Typical Stakeholders**: Software Architects, Performance Engineers, Developers.
- **Required Elements**: Processes, Threads, Event queues, Data flows, Synchronization points.
- **Recommended Notation**: UML Sequence Diagram, UML Activity Diagram, Data Flow Diagrams.

## 4. Deployment Viewpoint
- **Concerns Addressed**: Hosting, network topology, availability, disaster recovery, capacity planning.
- **Typical Stakeholders**: DevOps, System Administrators, Security Engineers.
- **Required Elements**: Nodes (Servers, Containers), Networks, Deployment Artifacts.
- **Recommended Notation**: UML Deployment Diagram, Cloud Provider Architecture Diagrams.

## 5. Security Viewpoint
- **Concerns Addressed**: Authentication, authorization, data encryption, compliance, vulnerability mitigation.
- **Typical Stakeholders**: Security Engineers, Auditors, Business Sponsors.
- **Required Elements**: Trust boundaries, Security controls (Firewalls, IAM), Sensitive data stores.
- **Recommended Notation**: Threat models, Data flow diagrams with trust boundaries marked.

## Usage Guidelines
Do not create views for every viewpoint in every project. Select only the viewpoints that address the highest-priority concerns of your stakeholders.
