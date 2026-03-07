# GCP-AI-Governor

An AI-driven cloud governance agent for Google Cloud infrastructure.

GCP-AI-Governor is designed to monitor infrastructure-relevant events, evaluate policy posture, and trigger safe remediation decisions through a controlled governance loop. The current release validates that loop locally through deterministic simulation. The target architecture extends this into a cloud-native control surface using Cloud Audit Logs, Eventarc, Cloud Run, Vertex AI reasoning, and auditable tool execution.

## Why this exists

Cloud IAM drift, unsafe privilege grants, and delayed remediation create unnecessary blast radius across modern cloud environments. GCP-AI-Governor is being built as a governance-grade enforcement layer that starts with deterministic local policy validation and evolves toward cloud-native autonomous remediation with explicit guardrails, dry-run defaults, and auditable reasoning.

## Current validated control loop

The current local system proves:

event -> policy evaluation -> decision -> simulated remediation

Validated decisions:
- `roles/owner` -> `revoke`
- `roles/viewer` -> `allow`
- `roles/iam.serviceAccountAdmin` -> `revoke`
- `heartbeat` -> `ignore`

## Current architecture

```mermaid
flowchart TD
    A[Developer / Admin] -->|Policy Input| B[Local Governance Simulator]
    B -->|Send Event| C[Flask Governance Daemon]
    C -->|Evaluate| D[Policy Engine]
    D -->|Decision| E[Action Execution Stub]
    E -->|Response| F[Smoke Tests / Simulator Output]
    C -->|Structured Logs| G[Console / Future Cloud Logging]
