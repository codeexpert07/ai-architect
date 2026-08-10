# Chapter 2 — Generative AI Fundamentals

## Prerequisites

Before starting this chapter, you should understand the AI architect mindset from Chapter 1, including the distinction between deterministic application logic and probabilistic model behavior.

You do **not** need to know how to train a neural network. The goal is to build enough conceptual depth to make sound architecture decisions around generative AI systems.

## Learning Objectives

By the end of this chapter, you should be able to:

- Explain what generative AI is and how it differs from predictive AI.
- Describe the relationship between foundation models, generative models, and application models.
- Explain the major stages of model development: pretraining, adaptation, alignment, and inference.
- Understand the basic lifecycle of a generative AI request.
- Explain tokens, context, decoding, temperature, top-p, and related inference controls at an architectural level.
- Distinguish model capability from application capability.
- Choose between hosted APIs, managed model platforms, and self-hosted models using explicit trade-offs.
- Identify where hallucination, bias, nondeterminism, and distribution shift enter an AI system.
- Design a production-oriented boundary around a generative model.
- Recognize when prompting, retrieval, fine-tuning, or deterministic code is the appropriate solution.

---

## 2.1 What Is Generative AI?

**Generative AI** refers to systems that learn patterns from data and can generate new content that is statistically consistent with those patterns.

The generated artifact may be:

- Text
- Source code
- Images
- Audio
- Speech
- Video
- Structured data
- Embeddings or other learned representations
- A multimodal combination of the above

The important architectural distinction is between a system that primarily **predicts or classifies** an existing outcome and one that **synthesizes a new artifact**.

For example:

| Workload | Typical AI behavior |
|---|---|
| Fraud detection | Predict/classify risk |
| Spam filtering | Classify |
| Demand forecasting | Predict a numeric/time-series outcome |
| Image classification | Classify |
| Chat assistant | Generate text |
| Code assistant | Generate or transform code |
| Image generator | Generate pixels/visual content |
| Document summarization | Generate a compressed representation |
| Speech synthesis | Generate audio |

The distinction is useful, but modern systems often combine both. A production application may use a classifier to route a request, a retrieval system to obtain evidence, and a generative model to formulate the response.

### Architect's View

Do not treat “generative AI” as a single technology. It is a family of model capabilities exposed through an application architecture.

```text
                         GENERATIVE AI SYSTEM

   User Input ──► Understanding / Routing ──► Context Construction
                                      │                │
                                      │                ▼
                                      │          Retrieval / Tools
                                      │                │
                                      └───────► Model Inference
                                                     │
                                                     ▼
                                             Output Validation
                                                     │
                                                     ▼
                                              User / Workflow
```

The model is one component in this pipeline, not the whole system.

---

## 2.2 Generative AI, Machine Learning, and Deep Learning

These terms are related but should not be used interchangeably.

```text
Artificial Intelligence
└── Machine Learning
    └── Deep Learning
        ├── Discriminative / Predictive Models
        └── Generative Models
            ├── Language Models
            ├── Diffusion Models
            ├── Generative Audio Models
            └── Multimodal Models
```

This is a conceptual hierarchy rather than a strict taxonomy. Some systems combine multiple techniques.

### Machine Learning

Machine learning learns a mapping or behavior from data rather than relying entirely on hand-written rules.

### Deep Learning

Deep learning uses neural networks with multiple learned layers. Modern foundation models are generally deep-learning systems.

### Generative Modeling

A generative model learns enough structure from data to produce new samples or continuations.

For an AI architect, the useful question is not “Is this deep learning?” but:

> **What capability does the learned model provide, and what system responsibilities remain outside it?**

---

## 2.3 Foundation Models

A **foundation model** is a broadly trained model intended to support many downstream tasks rather than one narrowly defined business function.

Examples of capabilities include:

- Language understanding and generation
- Code generation
- Vision understanding
- Image generation
- Speech recognition
- Speech generation
- Cross-modal reasoning

A foundation model is normally only the starting point for an application.

```text
                    Foundation Model
                           │
             ┌─────────────┼─────────────┐
             ▼             ▼             ▼
          Prompting      RAG         Fine-tuning
             │             │             │
             └─────────────┼─────────────┘
                           ▼
                    AI Application
                           │
             ┌─────────────┼─────────────┐
             ▼             ▼             ▼
         Business       Security      Operations
          Logic        & Guardrails   & Evaluation
```

### Model Capability vs Product Capability

A common architecture mistake is assuming that a powerful model automatically creates a powerful product.

It does not.

A product's effective capability depends on at least:

```text
Product Capability
≈ Model Capability
  × Context Quality
  × Workflow Quality
  × Tool Quality
  × Evaluation Quality
  × Operational Reliability
```

This is not a mathematical law. It is a useful architectural mental model: a severe weakness in one layer can dominate the overall experience.

---

## 2.4 How a Generative Model Learns

At a high level, modern generative models learn statistical relationships in large datasets by optimizing a loss function.

For a language model, one simplified objective is next-token prediction:

```text
Input tokens:   The application should
Target token:   scale

Input tokens:   The application should scale
Target token:   reliably
```

During training, the model repeatedly predicts targets, compares predictions with the training target, calculates a loss, and updates its parameters through optimization.

The resulting parameters encode learned statistical patterns. They do **not** constitute a conventional database of facts that can simply be queried like rows in PostgreSQL.

This distinction matters because:

- A model can know a pattern without being able to reproduce it reliably.
- A model can generate a plausible statement that is false.
- Updating a source document does not automatically update the model parameters.
- Enterprise knowledge is therefore often better supplied through retrieval or tools than by expecting the model's weights to contain current business data.

---

## 2.5 Pretraining, Adaptation, and Alignment

Modern model development commonly consists of several stages. The exact terminology differs between model providers and research programs, but the architectural concepts are broadly useful.

### Stage 1 — Pretraining

The model learns general representations and patterns from a very large corpus.

For language models this can include learning:

- Syntax
- Semantics
- Code patterns
- World knowledge patterns
- Reasoning-related patterns
- Relationships between concepts

Pretraining is computationally expensive and is normally performed by specialized model developers rather than application teams.

### Stage 2 — Adaptation / Instruction Tuning

The base model can be adapted to follow instructions and perform desired classes of tasks more effectively.

This stage may involve supervised examples, preference data, parameter-efficient techniques, or other adaptation methods.

### Stage 3 — Alignment and Safety Tuning

Additional training and policy mechanisms can improve the model's behavior around:

- Instruction following
- Helpfulness
- Safety
- Refusal behavior
- Style
- Tool use
- Structured responses

The precise training method varies by model.

### Stage 4 — Application-Time Conditioning

At runtime, the application adds:

- System instructions
- User input
- Retrieved information
- Conversation state
- Tool results
- Output schemas
- Policies

This final stage is where most application architects operate.

```text
Large Training Corpus
        │
        ▼
   Pretraining
        │
        ▼
 Base/Foundation Model
        │
        ▼
Instruction / Safety Adaptation
        │
        ▼
   Deployable Model
        │
        ▼
Runtime Context + Tools + Policies
        │
        ▼
     Application
```

---

## 2.6 Base Models vs Instruction-Following Models

A **base model** is trained primarily to model its training objective. An **instruction-following model** has additional adaptation intended to make it respond usefully to human instructions.

Architecturally, this distinction matters because the application contract changes.

A base model may be suitable for specialized continuation or further adaptation, while an instruction-following model is generally easier to integrate into an interactive application.

When evaluating models, identify the model's intended usage rather than assuming that all models with similar parameter counts have equivalent behavior.

---

## 2.7 The Inference Lifecycle

**Inference** is the process of using a trained model to produce an output for an input.

A simplified language-model inference path is:

```text
User Request
     │
     ▼
Input Validation
     │
     ▼
Context Assembly
     │
     ├── System Instructions
     ├── User Input
     ├── Conversation State
     ├── Retrieved Evidence
     └── Tool Results
     │
     ▼
Tokenization
     │
     ▼
Model Forward Pass
     │
     ▼
Next-Token Probabilities
     │
     ▼
Decoding / Sampling
     │
     ├── token
     ├── token
     ├── token
     └── ...
     │
     ▼
Detokenization
     │
     ▼
Output Validation / Guardrails
     │
     ▼
Application Response
```

This lifecycle explains why AI latency is different from ordinary REST latency. A response may require multiple network calls, retrieval operations, model computation, and token generation.

---

## 2.8 Tokens and Context

Language models generally operate on **tokens**, not directly on characters or words.

A token may represent:

- A complete word
- Part of a word
- Punctuation
- Whitespace-related text
- A code fragment

The exact tokenization depends on the model and tokenizer.

A useful approximation is:

```text
Text
  ↓
Tokenizer
  ↓
Token IDs
  ↓
Model
  ↓
Token IDs
  ↓
Tokenizer / Decoder
  ↓
Text
```

### Why Architects Care About Tokens

Token count influences:

- Context-window usage
- Latency
- Cost
- Throughput
- Prompt design
- Retrieval strategy
- Conversation history management

Do not assume that character count, word count, and token count are interchangeable.

### Context Window

The context window is the amount of tokenized information a model can process for a request, subject to the model's specific limits and API behavior.

A larger context window does not automatically mean better results. Excessive context can increase cost, latency, and distraction while still failing to provide the most relevant evidence.

This leads to an important principle:

> **Context capacity is not the same as context quality.**

Detailed context engineering is covered later in the handbook.

---

## 2.9 Decoding: How the Model Chooses Output

At each generation step, a language model produces a probability distribution over possible next tokens.

Conceptually:

```text
Prompt
  │
  ▼
Model
  │
  ▼
Token probabilities
  │
  ├── "the"      0.42
  ├── "a"        0.21
  ├── "your"     0.11
  ├── "this"     0.08
  └── other      0.18
  │
  ▼
Decoding strategy
  │
  ▼
Selected token
```

The model itself supplies probabilities; the serving system applies a decoding strategy to choose the next token.

### Greedy Decoding

Select the highest-probability token at each step.

Advantages:

- Simple
- Reproducible under stable conditions
- Useful for some deterministic-style workloads

Limitations:

- Can produce repetitive or locally optimal text
- May not produce the most useful overall continuation

### Temperature

Temperature modifies the sharpness of the probability distribution used during sampling.

Conceptually:

```text
Lower temperature  → more concentrated choices
Higher temperature → more varied choices
```

Temperature is **not** a direct quality control. Increasing it does not make a model “smarter”; it changes output diversity.

For production systems, choose it based on the task and validate behavior empirically.

### Top-p

Top-p sampling limits sampling to a dynamically selected set of likely tokens whose cumulative probability reaches a configured threshold.

It is another way to control diversity while avoiding very low-probability candidates.

### Top-k

Top-k sampling restricts choices to the k most probable tokens.

Not every provider exposes every decoding control, and the exact semantics can differ.

### Architectural Guidance

Treat generation parameters as part of the **application configuration and evaluation surface**. A change to temperature, top-p, stop sequences, or output limits can change product behavior and should therefore be traceable and testable.

---

## 2.10 Determinism and Reproducibility

AI systems are often described as nondeterministic, but reproducibility is more nuanced.

Variation can come from:

- Sampling configuration
- Random seeds, where supported
- Model updates
- Provider-side serving changes
- Dynamic context
- Retrieval results
- Tool results
- Conversation state
- Infrastructure or routing differences

Even when sampling is configured for deterministic behavior, a provider may change the underlying model implementation or serving stack.

Therefore, production reproducibility should rely on **versioned inputs and controlled environments**, not on the assumption that identical API calls will always yield byte-for-byte identical output.

For critical workflows, store enough metadata to reconstruct the request context safely:

- Model identifier/version
- Prompt/template version
- Relevant application version
- Retrieval configuration
- Retrieved document identifiers/version
- Tool inputs and outputs where appropriate
- Decoding configuration
- Evaluation result

Avoid storing sensitive prompt content indiscriminately; observability must follow data-protection requirements.

---

## 2.11 Hallucination: Why Plausible Does Not Mean True

A generative model is optimized to produce likely outputs under its training and runtime context. It is not inherently a truth database.

A model can therefore generate a fluent answer that is unsupported or false.

Common causes include:

- Missing information
- Ambiguous requests
- Weak or conflicting context
- Outdated learned knowledge
- Poor retrieval
- Prompt ambiguity
- Model limitations
- Excessive generation freedom

### Architectural Response

Do not try to solve hallucination with a single prompt instruction such as “never hallucinate.”

Use layered controls:

```text
             User Request
                  │
                  ▼
          Relevant Context
                  │
                  ▼
          Model Generation
                  │
        ┌─────────┴─────────┐
        ▼                   ▼
  Output Validation     Evidence Check
        │                   │
        └─────────┬─────────┘
                  ▼
          Business Policy
                  │
                  ▼
             Final Output
```

Depending on the use case, controls may include retrieval, citations, structured output, deterministic validation, confidence thresholds, secondary verification, and human review.

---

## 2.12 Generative AI Is Not a Database

A model's parameters encode learned representations. They should not be treated as an authoritative transactional datastore.

Consider an employee policy assistant.

Bad architecture:

```text
Policy changed in database
        │
        X
   Assume model knows
```

Better architecture:

```text
Current Policy Store
        │
        ▼
 Retrieval / Query
        │
        ▼
Relevant Policy Evidence
        │
        ▼
      LLM
        │
        ▼
Grounded Explanation
```

Use the appropriate system of record for authoritative state. Use the model to understand, transform, summarize, explain, or reason over information supplied to it.

---

## 2.13 Prompting, Retrieval, Fine-Tuning, or Code?

One of the most important architecture decisions is selecting the right mechanism for a requirement.

| Requirement | Usually consider first |
|---|---|
| Change wording/style | Prompting |
| Give current enterprise knowledge | Retrieval / tools |
| Enforce a deterministic calculation | Code |
| Teach a stable output format | Prompt + structured output |
| Adapt behavior to a specialized dataset | Fine-tuning / adaptation |
| Enforce authorization | Application security |
| Guarantee a business invariant | Deterministic code |
| Execute an external action | Tool with explicit authorization |

These are not mutually exclusive.

For example, a customer-support assistant may use:

```text
Prompt
  +
Retrieved product documentation
  +
Customer/account data from authorized tools
  +
Deterministic refund policy
  +
LLM response generation
```

### A Useful Decision Rule

Ask:

> **Is the requirement about knowledge, behavior, computation, or control?**

- **Knowledge** → retrieval or tools are often appropriate.
- **Behavior/style** → prompting or model adaptation may help.
- **Computation/invariants** → deterministic code.
- **Control/authorization** → application and platform controls.

---

## 2.14 Structured Output

Many enterprise applications do not want free-form prose. They need data that can safely flow into another component.

For example:

```json
{
  "customerId": "C1024",
  "intent": "REFUND_REQUEST",
  "priority": "HIGH",
  "reason": "Duplicate charge"
}
```

Structured-output mechanisms can constrain generation toward a schema. However, schema validity is not equivalent to semantic correctness.

A response can be valid JSON and still contain:

- The wrong customer
- An invalid business decision
- An unauthorized action
- Incorrect values

Therefore use two layers:

```text
Schema Validation
       ↓
Business Validation
       ↓
Authorization
       ↓
Workflow Action
```

Never treat syntactically valid model output as automatically trustworthy.

---

## 2.15 Multimodal Generative AI

Modern AI systems increasingly operate across multiple modalities.

A multimodal system may accept:

- Text
- Images
- Audio
- Video
- Documents

and may produce one or more of these modalities.

A simplified architecture is:

```text
Text ─────┐
Image ────┤
Audio ────┼──► Multimodal Model ──► Text / Image / Audio
Video ────┤
Document ─┘
```

The architect must account for modality-specific concerns:

- File size and upload limits
- Content extraction
- OCR quality
- Audio/video preprocessing
- Storage cost
- Privacy
- Malware scanning
- Content safety
- Latency

For documents, it is often useful to separate ingestion from inference so that expensive preprocessing can be performed asynchronously and reused.

---

## 2.16 Model Size Is Not the Same as Model Quality

Parameter count is an incomplete model-selection metric.

A smaller model can be preferable when:

- The task is narrow.
- Latency is critical.
- High concurrency is required.
- The workload is cost-sensitive.
- Data must remain within a controlled environment.
- The task can be solved reliably with a smaller model.

A larger model may be justified when:

- Complex reasoning is required.
- The workload is diverse.
- Quality requirements dominate latency and cost.
- The model provides capabilities unavailable in smaller alternatives.

The correct selection process is empirical:

```text
Requirements
    ↓
Candidate Models
    ↓
Representative Evaluation Set
    ↓
Quality + Latency + Cost + Safety
    ↓
Production Decision
```

Do not optimize for benchmark scores alone.

---

## 2.17 Hosted, Managed, and Self-Hosted Models

A production architect commonly evaluates three deployment models.

### Hosted Model API

The application calls a model provider's API.

```text
Application ──Internet/Private Link──► Model Provider
```

Advantages:

- Fastest time to market
- No GPU fleet management
- Provider handles model serving
- Easy experimentation

Trade-offs:

- External dependency
- Provider pricing and quotas
- Data-governance considerations
- Potential provider/model changes

### Managed Model Platform

A cloud or enterprise platform manages model hosting and related infrastructure.

Advantages:

- Enterprise integration
- IAM and networking controls
- Governance features
- Potential regional/data-residency options

Trade-offs:

- Platform coupling
- Infrastructure cost
- Model availability depends on the platform

### Self-Hosted Model

The organization operates model inference infrastructure.

Advantages:

- Greater infrastructure control
- Potential data-isolation benefits
- Ability to tune serving for known workloads
- Potential economics at sufficient scale

Trade-offs:

- GPU capacity planning
- Model serving operations
- Upgrades and patching
- Reliability engineering
- Performance optimization
- Security and supply-chain responsibility

### Decision Matrix

| Concern | Hosted API | Managed platform | Self-hosted |
|---|---|---|---|
| Time to market | Excellent | Very good | Poorer |
| Operational burden | Low | Medium | High |
| Infrastructure control | Low | Medium | High |
| Data control | Provider-dependent | Platform-dependent | Highest |
| Scaling simplicity | High | High | Requires engineering |
| Custom serving | Limited | Medium | High |
| Fixed infrastructure ownership | Low | Medium | High |

The correct choice depends on requirements, not ideology.

---

## 2.18 Generative AI Application Architecture

A minimal production-oriented architecture can be represented as:

```text
┌─────────────────────────────────────────────────────────────┐
│                         Client                              │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│ API / Authentication / Rate Limiting / Tenant Isolation     │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│ AI Application / Orchestrator                              │
│ - prompt/version management                                 │
│ - workflow                                                 │
│ - model routing                                             │
│ - policy enforcement                                        │
└───────────────┬─────────────────────┬───────────────────────┘
                │                     │
                ▼                     ▼
        ┌──────────────┐      ┌─────────────────┐
        │ Context/Data │      │ Model Gateway   │
        │ RAG/Tools    │      │ Provider/Local  │
        └──────────────┘      └────────┬────────┘
                                       │
                                       ▼
                                ┌────────────┐
                                │   Model    │
                                └─────┬──────┘
                                      │
                                      ▼
                           Validation / Guardrails
                                      │
                                      ▼
                                Application
                                      │
                                      ▼
                         Observability / Evaluation
```

This architecture creates explicit boundaries between business logic, context, model infrastructure, and operational controls.

---

## 2.19 Failure Modes to Design For

A production AI architecture should assume failure.

### Model Unavailable

Possible responses:

- Retry transient failures with bounded backoff.
- Fail over to another model/provider where appropriate.
- Return a controlled degraded response.
- Route simple workloads to a smaller local model.

Do not blindly retry expensive requests indefinitely.

### Model Timeout

Use:

- Explicit deadlines
- Cancellation
- Bounded retries
- Fallback behavior
- User-visible status where necessary

### Invalid Output

Use schema validation and reject or repair outputs where safe.

### Hallucinated Output

Use evidence, retrieval, validation, policy checks, or human review depending on impact.

### Provider Rate Limit

Use:

- Per-tenant quotas
- Backpressure
- Queueing for asynchronous workloads
- Model routing
- Capacity planning

### Context Too Large

Possible strategies:

- Retrieve fewer documents
- Compress or summarize context
- Remove redundant history
- Route to an appropriate model
- Split the workflow into stages

### Unsafe or Unauthorized Action

The model should never be the final authorization authority. Enforce authorization in deterministic application infrastructure.

---

## 2.20 Security Fundamentals

Generative AI introduces a security model that extends traditional application security.

### Prompt Injection

An attacker may attempt to influence model instructions through user input or external content.

### Indirect Prompt Injection

Instructions can be embedded in documents, web pages, emails, or retrieved knowledge.

### Data Leakage

Sensitive information may enter prompts or appear in generated output.

### Tool Abuse

An agent may be tricked into invoking an otherwise legitimate tool in an unsafe way.

### Excessive Agency

A model with broad permissions can turn a language-model failure into a system-level failure.

### Architectural Controls

Use:

- Strong identity and tenant isolation
- Least-privilege tool permissions
- Server-side authorization
- Input/output filtering where appropriate
- Data classification
- Secret isolation
- Audit logging
- Network controls
- Rate limits and quotas
- Human approval for high-impact actions

The security boundary must exist outside the model.

---

## 2.21 Cost and Capacity Planning

Generative AI cost has both variable and fixed components.

### Variable Costs

- Input tokens
- Output tokens
- Model calls
- Embedding calls
- Tool/API calls
- Retrieval infrastructure

### Fixed or Semi-Fixed Costs

- GPU infrastructure
- Model serving
- Databases
- Object storage
- Observability platforms
- Network infrastructure

A useful architecture-level model is:

```text
Monthly AI Cost
≈ Requests
 × Average model calls/request
 × Average token consumption
 × Effective price/token
 + Supporting infrastructure
```

For self-hosting, capacity planning should additionally consider:

- GPU memory
- Model size
- Quantization
- Concurrent requests
- Tokens per second
- Batch size
- Context length
- Availability requirements

Do not compare API pricing directly with GPU rental cost without considering engineering, storage, networking, observability, redundancy, and utilization.

---

## 2.22 Evaluation Before Production

A generative AI feature should have a representative evaluation set before production launch.

A useful evaluation set contains examples covering:

- Normal requests
- Edge cases
- Ambiguous requests
- Adversarial inputs
- Sensitive-data scenarios
- Long-context scenarios
- Known failure cases
- Business-critical cases

Evaluate multiple dimensions:

| Dimension | Example question |
|---|---|
| Correctness | Is the answer factually/business correct? |
| Groundedness | Is it supported by supplied evidence? |
| Relevance | Does it answer the actual request? |
| Safety | Does it follow safety/policy requirements? |
| Format | Does it satisfy the output contract? |
| Latency | Is response time acceptable? |
| Cost | Is cost per successful task acceptable? |

Evaluation should compare versions, not merely produce one score.

```text
Model A + Prompt v1 → Evaluation → Baseline
Model A + Prompt v2 → Evaluation → Compare
Model B + Prompt v2 → Evaluation → Compare
```

A model change is a production change even when no application source code changes.

---

## 2.23 Observability Requirements

At minimum, production systems should be able to answer:

1. Which application version handled the request?
2. Which model/version was used?
3. Which prompt/template version was used?
4. How much input/output was generated?
5. How long did retrieval and inference take?
6. Which tools were invoked?
7. Which policies or guardrails were triggered?
8. What was the estimated cost?
9. Was the response successful from the user's perspective?

A typical trace can look like:

```text
Trace: request-8f31
│
├── API authentication
├── Tenant authorization
├── Prompt template v17
├── Retrieval query
│   ├── document-102
│   └── document-887
├── Model: selected-model/version
│   ├── input tokens
│   └── output tokens
├── Output validation
├── Business policy check
└── Response
```

Do not log secrets or sensitive content merely because it is useful for debugging. Redaction, retention, access control, and sampling must be part of the observability design.

---

## 2.24 Common Architectural Mistakes

### Mistake 1 — Starting With the Model

**Problem:** The team chooses a model before defining the workload.

**Better:** Define quality, latency, privacy, volume, cost, and failure requirements first.

### Mistake 2 — Treating the Model as the Application

**Problem:** Business rules are placed inside prompts.

**Better:** Keep business invariants and authorization in deterministic services.

### Mistake 3 — Sending the Entire Database to the Model

**Problem:** High cost, poor relevance, privacy risk, context overflow.

**Better:** Retrieve only authorized, relevant context.

### Mistake 4 — Assuming JSON Means Correctness

**Problem:** Schema validation passes but values are wrong.

**Better:** Add semantic and business validation.

### Mistake 5 — No Model Versioning

**Problem:** Behavior changes without traceability.

**Better:** Version model identifiers, prompts, evaluation sets, and relevant configuration.

### Mistake 6 — Logging Everything

**Problem:** Sensitive data becomes widely accessible through logs.

**Better:** Apply data minimization, redaction, access controls, and retention policies.

### Mistake 7 — Infinite Agent Retries

**Problem:** A failure becomes a cost explosion or denial-of-wallet event.

**Better:** Bound retries, loops, tool calls, tokens, and execution time.

### Mistake 8 — Using an LLM for Deterministic Work

**Problem:** Arithmetic, authorization, policy checks, or transactional logic become probabilistic.

**Better:** Use normal software for deterministic invariants.

---

## 2.25 Production Design Checklist

Before approving a generative AI architecture, verify:

### Business

- [ ] The AI capability has a measurable business outcome.
- [ ] A degraded mode exists when AI is unavailable.
- [ ] High-impact decisions have an appropriate approval path.

### Model

- [ ] Candidate models were evaluated on representative workloads.
- [ ] Model/version identifiers are traceable.
- [ ] Inference parameters are configuration-controlled.

### Context

- [ ] Context sources are identified and authorized.
- [ ] Current business data comes from authoritative systems.
- [ ] Context size and retrieval quality are measured.

### Security

- [ ] Authorization is enforced outside the model.
- [ ] Tool permissions follow least privilege.
- [ ] Sensitive data handling is explicitly designed.
- [ ] Prompt injection and indirect injection are considered.

### Reliability

- [ ] Timeouts and bounded retries exist.
- [ ] Rate limits and quotas exist.
- [ ] Provider/model failure has a defined behavior.
- [ ] Expensive loops are bounded.

### Quality

- [ ] Representative evaluation data exists.
- [ ] Quality thresholds are defined.
- [ ] Regression evaluation is automated where practical.

### Operations

- [ ] Model, prompt, retrieval, and tool activity can be traced.
- [ ] Token usage and cost are measurable.
- [ ] Sensitive data is protected in telemetry.

---

## 2.26 Hands-On Exercises

### Exercise 1 — Model Selection

You are building an internal HR assistant for 50,000 employees.

Requirements:

- Average response under 5 seconds.
- Enterprise policies must remain current.
- Employee data must be tenant/identity aware.
- Cost must be predictable.
- The assistant must explain policy answers with evidence.

Design a model-selection and application architecture. Explain why you chose the deployment model and what you would benchmark.

### Exercise 2 — Deterministic vs Generative

For an insurance application, classify each capability as **LLM**, **retrieval/tool**, **deterministic code**, or **human approval**:

1. Extract claim information from a PDF.
2. Calculate the approved reimbursement amount.
3. Explain why a claim was rejected.
4. Approve a payment above a high-value threshold.
5. Find the current policy clause.

Document your reasoning rather than simply naming a technology.

### Exercise 3 — Failure Design

Design a failure strategy for a customer-support assistant when:

- The primary model times out.
- Retrieval is unavailable.
- The provider returns a rate-limit error.
- The model produces invalid structured output.
- A tool invocation requests an unauthorized customer record.

For each case, define timeout, retry, fallback, and user-visible behavior.

### Exercise 4 — Cost Estimation

Assume a workload generates 100,000 requests per month. Estimate the monthly token consumption and model cost using a provider's current pricing. Then identify three architectural changes that could reduce cost without materially reducing task success.

Do not optimize cost before defining an acceptable quality threshold.

### Exercise 5 — Production Review

Review an architecture where a browser sends a user prompt directly to an LLM provider and displays the result.

Identify at least ten production concerns and redesign the architecture using the principles in this chapter.

---

## 2.27 Java Example — Model Boundary

The following example illustrates an important architectural principle: business code should depend on an application-level AI interface rather than spreading provider-specific calls throughout the domain layer.

```java
public interface AiTextGenerator {
    AiResponse generate(AiRequest request);
}

public record AiRequest(
        String systemInstruction,
        String userInput,
        String model,
        double temperature) {
}

public record AiResponse(
        String text,
        String model,
        int inputTokens,
        int outputTokens) {
}
```

A service can then depend on the interface:

```java
public final class CustomerSupportService {

    private final AiTextGenerator generator;

    public CustomerSupportService(AiTextGenerator generator) {
        this.generator = generator;
    }

    public String draftReply(String customerMessage) {
        AiRequest request = new AiRequest(
                "Answer using only approved support guidance.",
                customerMessage,
                "configured-by-platform",
                0.2);

        AiResponse response = generator.generate(request);
        return response.text();
    }
}
```

In production, the implementation behind `AiTextGenerator` would also need timeout handling, telemetry, authorization-aware context, output validation, and provider-specific error mapping.

The goal is **controlled coupling**, not a lowest-common-denominator abstraction that hides every provider capability.

---

## 2.28 Python Example — Explicit Generation Configuration

A similar boundary can be expressed in Python:

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class GenerationRequest:
    system_instruction: str
    user_input: str
    model: str
    temperature: float = 0.2
    max_output_tokens: int = 500


@dataclass(frozen=True)
class GenerationResponse:
    text: str
    model: str
    input_tokens: int
    output_tokens: int
```

The application can pass this contract to a provider adapter instead of coupling business workflows to a specific SDK.

```python
class AiTextGenerator:
    def generate(self, request: GenerationRequest) -> GenerationResponse:
        raise NotImplementedError
```

For a production implementation, make retries, deadlines, telemetry, provider errors, and sensitive-data handling explicit rather than burying them in a generic exception handler.

---

## 2.29 Key Architectural Principles

1. **Generative AI is a capability, not an application architecture.**
2. **Foundation models are reusable intelligence components, not authoritative business databases.**
3. **Model capability and product capability are different things.**
4. **Context quality often matters more than simply increasing context size or model size.**
5. **Generation parameters are part of production behavior and must be versioned/evaluated.**
6. **Structured output improves integration safety but does not guarantee semantic correctness.**
7. **Use retrieval for current knowledge and deterministic code for invariants.**
8. **Model selection must be driven by workload requirements and representative evaluation.**
9. **Hosted, managed, and self-hosted models each have legitimate architectural use cases.**
10. **The model is never the final authorization authority.**
11. **Every production AI dependency needs a failure and degradation strategy.**
12. **Cost, quality, latency, security, and reliability must be optimized together.**

---

## Chapter Summary

Generative AI systems are probabilistic software components capable of synthesizing text, code, images, audio, and other content. Modern foundation models are created through large-scale training and adaptation, then conditioned at runtime by instructions, context, retrieval, tools, and application policies.

For an AI architect, the most important lesson is that **model inference is only one stage of a larger system**. The production architecture must control what information enters the model, how the output is constrained and validated, what actions it can cause, how failures are handled, and how quality and cost are measured.

The next chapters will go deeper into the internals of large language models, then build toward prompt engineering, embeddings, RAG, agents, MCP, evaluation, security, and enterprise architecture.

> **A production AI system is not “an LLM behind an API.” It is a controlled software system in which a probabilistic model operates inside deterministic engineering boundaries.**

---

## Further Reading

The following primary sources are useful for continuing the concepts introduced here:

- Vaswani et al., *Attention Is All You Need* — foundational Transformer architecture paper.
- Brown et al., *Language Models are Few-Shot Learners* — influential work on large language-model scaling and in-context learning.
- Bommasani et al., *On the Opportunities and Risks of Foundation Models* — broad foundation-model perspective.
- Goodfellow, Bengio, and Courville, *Deep Learning* — deep-learning fundamentals.
- Stanford CRFM — research and educational material on foundation models.
- NIST AI Risk Management Framework — risk-management perspective for AI systems.

### Reference URLs

- https://arxiv.org/abs/1706.03762
- https://arxiv.org/abs/2005.14165
- https://arxiv.org/abs/2108.07258
- https://www.deeplearningbook.org/
- https://crfm.stanford.edu/
- https://www.nist.gov/itl/ai-risk-management-framework

---

## Interview Questions

1. What is the difference between generative and discriminative AI?
2. What is a foundation model?
3. Explain pretraining, instruction tuning, and alignment.
4. Why should an LLM not be treated as a system of record?
5. What is inference and how does decoding affect it?
6. What are temperature, top-k, and top-p?
7. Why can a model produce a fluent but incorrect answer?
8. When would you use RAG instead of fine-tuning?
9. When should deterministic code replace an LLM?
10. What are the trade-offs between hosted and self-hosted inference?
11. How would you design a provider abstraction without hiding important provider capabilities?
12. How would you make an AI request traceable in production?
13. What metadata would you record for an AI request?
14. How would you design a fallback when the primary model provider is unavailable?
15. Why does valid JSON from an LLM not guarantee correctness?
16. How would you prevent an AI assistant from accessing another tenant's data?
17. How would you estimate AI cost at architecture-design time?
18. What is the difference between model capability and product capability?
19. How would you evaluate a new model before replacing the current production model?
20. Why is context quality often more important than simply increasing context-window size?
