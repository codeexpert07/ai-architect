# Production AI Case Study Portfolio

The handbook should not use chatbots as the default representation of production AI. Real enterprise AI systems commonly combine machine learning, foundation models, deterministic business rules, workflow orchestration, event-driven architecture, human review, and conventional software services.

This portfolio defines the primary non-chatbot systems that the handbook will use as recurring architectural case studies.

## Case Study 1 — Intelligent Document Processing

### Business problem

An enterprise receives invoices, forms, reports, scanned documents, emails, and other unstructured or semi-structured content and needs to turn them into validated business records.

### Reference flow

```text
Document
   |
   v
Ingestion / Object Storage
   |
   v
Document Classification
   |
   v
OCR / Layout Understanding
   |
   v
Field & Entity Extraction
   |
   v
Schema Validation
   |
   v
Business Validation
   |
   v
Confidence Evaluation
   |
   +----------------------+----------------------+
   |                                             |
High confidence                              Low confidence
   |                                             |
   v                                             v
Automatic Processing                         Human Review
```

### Architectural concerns

- Asynchronous processing and durable workflows
- Multimodal models and document layout understanding
- Structured output and schema validation
- Confidence thresholds and abstention
- Human-in-the-loop review
- Idempotency, retries, and dead-letter handling
- Model and prompt versioning
- PII protection and tenant isolation
- Provenance and auditability
- Batch versus near-real-time processing
- Cost-aware model routing

### Core lesson

AI extraction is not the system of record. Model output must pass deterministic validation and business controls before it is allowed to drive downstream state changes.

---

## Case Study 2 — AI Software Engineering Platform

### Business problem

A software engineering platform analyzes pull requests, repository context, tests, dependencies, security findings, and architecture metadata to assist developers with code review and remediation.

### Reference flow

```text
Pull Request
     |
     v
Repository Context Builder
     |
     v
AI Orchestrator
     |
     +----------------+----------------+----------------+
     |                |                |                |
     v                v                v                v
Code Search      Test Analysis   Security Analysis  Architecture Analysis
     |                |                |                |
     +----------------+----------------+----------------+
                              |
                              v
                       Evidence Collector
                              |
                              v
                       Review Generator
                              |
                              v
                       Human Developer
```

### Tool boundary

The agent should operate through explicitly authorized tools rather than arbitrary execution:

```text
Agent
  |
  v
Tool Policy
  |
  v
Authorization
  |
  v
Tool Execution / Sandbox
  |
  v
Sanitized Result
  |
  v
Agent
```

### Architectural concerns

- Repository and dependency context construction
- Agent planning and tool calling
- Least-privilege tool authorization
- Sandboxed command execution
- Prompt injection through source code and repository content
- Deterministic security and static-analysis controls
- Evaluation against known defects and review datasets
- Token and context-budget management
- Human approval for repository mutations
- Traceability from finding to source evidence

### Core lesson

An AI agent is an untrusted decision component. Tools, permissions, execution environments, and side effects must remain under explicit platform control.

---

## Case Study 3 — Real-Time Fraud Detection

### Business problem

A financial platform evaluates transactions in real time and combines statistical/ML risk signals with deterministic policy before deciding whether to allow, review, or block a transaction.

### Reference flow

```text
Transaction API
      |
      v
Event Stream
      |
      v
Online Feature Computation
      |
      v
Model Serving
      |
      v
Risk Score
      |
      v
Rules / Policy Engine
      |
      +-----------+-----------+
      |           |           |
      v           v           v
    Allow       Review      Block
```

### Architectural concerns

- Low-latency inference
- Streaming and event-driven architecture
- Online/offline feature consistency
- Feature stores and feature freshness
- Model serving and autoscaling
- False-positive versus false-negative trade-offs
- Explainability and decision evidence
- Model drift and concept drift
- Shadow deployments and champion/challenger models
- Rollback and model governance

### Core lesson

A model score is an input to a production decision, not necessarily the decision itself. High-impact decisions should combine learned signals with explicit policy and governance.

---

## Case Study 4 — Production Incident Intelligence

### Business problem

An SRE platform correlates logs, metrics, traces, deployments, source changes, Kubernetes events, alerts, runbooks, and historical incidents to accelerate incident investigation and recommend remediation.

### Reference flow

```text
Logs -----------+
Metrics --------+
Traces ---------+
Deployments ----+
Git Changes ----+--> Incident Context Engine --> AI Reasoning
K8s Events -----+                                      |
Runbooks -------+                                      v
Historical Data-+                               Evidence / Hypothesis
                                                        |
                                                        v
                                                 Policy Evaluation
                                                        |
                                                        v
                                                  Human Approval
                                                        |
                                                        v
                                                  Remediation
```

### Architectural concerns

- Streaming and time-windowed context
- Observability data normalization
- RAG over runbooks and historical incidents
- Evidence-backed reasoning
- Tool calling against operational systems
- Autonomous action boundaries
- Approval workflows and break-glass controls
- Audit trails and incident timelines
- Evaluation using historical incidents
- Safe rollback and remediation controls

### Core lesson

The system should distinguish evidence, hypothesis, recommendation, and action. An LLM-generated hypothesis must not be treated as authorization to modify production infrastructure.

---

## Case Study 5 — Contract Intelligence

### Business problem

An enterprise analyzes a large contract corpus to identify clauses, obligations, renewal terms, liability exposure, termination conditions, and other risks.

### Reference flow

```text
Contract
   |
   v
Document Processing
   |
   v
Clause Segmentation
   |
   v
Clause Classification
   |
   v
Entity / Obligation Extraction
   |
   v
Semantic Analysis
   |
   v
Deterministic Risk Rules
   |
   v
Structured Contract Representation
   |
   +-------------------+-------------------+
   |                   |                   |
 Search / Analytics  Workflow           Review
```

### Architectural concerns

- Structured extraction from long documents
- Evidence and citation provenance
- Semantic comparison
- Deterministic risk rules alongside model reasoning
- Human review for high-impact findings
- Versioned document and model lineage
- Access control and tenant isolation
- Auditability and regulatory requirements

### Core lesson

Enterprise AI needs provenance. Important assertions should be traceable to the source document, location, model/configuration version, and processing event that produced them.

---

## Cross-Case Architectural Themes

The case studies intentionally overlap. The goal is to teach reusable architectural patterns rather than five isolated applications.

| Concern | Document | AI Engineering | Fraud | Incident | Contract |
|---|:---:|:---:|:---:|:---:|:---:|
| LLMs / foundation models | ✓ | ✓ | | ✓ | ✓ |
| Multimodal AI | ✓ | | | | ✓ |
| RAG | ✓ | ✓ | | ✓ | ✓ |
| Agents / tool calling | | ✓ | | ✓ | |
| Structured output | ✓ | ✓ | ✓ | ✓ | ✓ |
| Human-in-the-loop | ✓ | ✓ | ✓ | ✓ | ✓ |
| Real-time inference | | | ✓ | ✓ | |
| Event-driven architecture | ✓ | | ✓ | ✓ | ✓ |
| Model serving | ✓ | ✓ | ✓ | ✓ | ✓ |
| Security | ✓ | ✓✓ | ✓ | ✓✓ | ✓✓ |
| Governance / auditability | ✓✓ | ✓ | ✓✓ | ✓ | ✓✓ |
| Explainability / evidence | ✓ | ✓ | ✓✓ | ✓✓ | ✓✓ |
| Evaluation | ✓ | ✓✓ | ✓✓ | ✓✓ | ✓ |
| Cost optimization | ✓✓ | ✓✓ | ✓ | ✓ | ✓ |
| Autonomous actions | | ✓ | | ✓ | |

## How the Case Studies Map to the Handbook

The case studies should be reused across chapters instead of introduced only at the end:

- **Foundations:** establish why AI systems differ from traditional deterministic software.
- **Prompt and context engineering:** use document, contract, incident, and software-repository context as concrete examples.
- **RAG:** use contract clauses, runbooks, repository knowledge, and historical incidents rather than a conversational FAQ.
- **Tool calling and agents:** use the AI engineering and incident-intelligence systems.
- **Evaluation:** define task-specific datasets and production metrics for extraction, code review, fraud detection, and incident hypotheses.
- **Security:** use repository prompt injection, document poisoning, tenant isolation, operational tools, and sensitive financial data as threat scenarios.
- **Observability:** trace model calls, retrieval, tool calls, validation, latency, cost, and downstream outcomes.
- **Infrastructure:** contrast asynchronous document workloads, latency-sensitive fraud inference, and bursty incident workloads.
- **Enterprise architecture:** compare governance, compliance, human approval, data residency, and integration requirements across domains.
- **Architecture patterns:** derive reusable patterns and anti-patterns from the cases.

## Design Principle

The handbook should use chatbots only as one possible interface. The primary architectural question is not:

> "How do we build a chatbot?"

It is:

> **"How do we safely integrate probabilistic AI capabilities into a reliable production system with explicit data, control, security, evaluation, and operational boundaries?"**
