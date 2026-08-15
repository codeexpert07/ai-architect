# Chapter 4 — Production Architecture Refinements

This companion section incorporates the production-architecture refinements identified during review of Chapter 4. It deliberately makes several boundaries explicit because these details become increasingly important as the handbook moves into RAG, agents, tools, memory, and production operations.

---

## 1. Context Engineering Is an Operational Definition

**Prompt engineering** and **context engineering** are useful architectural distinctions, but the terminology is still evolving across the industry and research community. There is no single universally accepted taxonomy that every provider or practitioner uses.

For this handbook, use the following operational definitions:

- **Prompt engineering:** designing instructions, examples, constraints, output contracts, and failure behavior to shape model behavior.
- **Context engineering:** designing the runtime information environment supplied to a model, including selection, retrieval, ranking, authorization, freshness, compression, ordering, provenance, and removal of context.

The distinction is intentionally pragmatic. In a production system, the two disciplines overlap:

```text
                 AI input contract
                       │
             ┌─────────┴─────────┐
             ▼                   ▼
      Prompt engineering   Context engineering
             │                   │
       instructions        information
       examples            retrieval
       constraints         state
       output contract     tools
             │             provenance
             └─────────┬─────────┘
                       ▼
                      LLM
```

Do not optimize for terminology. Optimize for a system in which the model receives the right instructions and the smallest sufficient, authorized, high-quality information for the task.

---

## 2. Prompt Injection: Explicit Threat Model

Prompt injection should be treated as an application security problem, not as a prompt-writing problem.

### Threat categories

| Threat | Example | Primary deterministic control |
|---|---|---|
| Direct injection | User asks model to ignore policy | Input classification + policy enforcement |
| Indirect injection | Retrieved PDF contains malicious instructions | Untrusted-content isolation + tool policy |
| Tool-output injection | Search/API response contains instructions | Treat tool output as untrusted data |
| Data exfiltration | Model is induced to disclose secrets | Secret isolation + authorization |
| Unauthorized side effect | Model calls a privileged tool | Least privilege + server-side authorization + approval |
| Instruction conflict | Retrieved content contradicts application policy | Explicit source authority + deterministic policy |
| Cross-tenant leakage | Context contains another tenant's data | Authorization before retrieval + tenant isolation |

### Important limitation

Delimiters, XML tags, Markdown sections, instruction hierarchy, sanitization, and wording such as `ignore instructions in the document` can reduce ambiguity, but none should be treated as a complete security boundary.

Even transformations intended to make content safer can preserve adversarial intent. For example, a malicious document can remain influential after summarization. Therefore, the security architecture must assume that untrusted content may influence model behavior despite prompt-level defenses.

### Security boundary

```text
                 UNTRUSTED WORLD
                       │
          ┌────────────▼────────────┐
          │ Retrieval / tool layer  │
          │ normalization           │
          │ provenance              │
          │ authorization           │
          └────────────┬────────────┘
                       │
                       ▼
              constrained context
                       │
                       ▼
                      LLM
                       │
                       ▼
             candidate output/action
                       │
          ┌────────────▼────────────┐
          │ Deterministic controls  │
          │ schema validation        │
          │ authorization            │
          │ business rules           │
          │ side-effect policy       │
          └────────────┬────────────┘
                       ▼
                    ACTION
```

The LLM is inside the trust boundary as a **probabilistic interpreter**, not as the authority that grants access or approves consequential actions.

---

## 3. Application State vs Model Context

This distinction is foundational for production AI architecture.

> **Application state is authoritative state. Model context is a task-specific projection of that state.**

Do not make the conversation transcript, an LLM-generated summary, or a prompt the system of record.

### Recommended ownership model

```text
                 Authoritative systems
        ┌──────────────┬───────────────┐
        ▼              ▼               ▼
   Customer DB     Order service   Policy store
        │              │               │
        └──────────────┼───────────────┘
                       ▼
                Context assembler
                       │
                       ▼
             Task-specific context
                       │
                       ▼
                      LLM
```

The model may produce derived information such as a summary, classification, or proposed action. Persist that result as derived data with provenance and validation rather than silently promoting it to authoritative state.

### Example

Bad:

```text
Conversation summary says:
"Customer has an active premium subscription."

Application trusts summary for authorization.
```

Better:

```text
Authorization service → authoritative subscription state
                                      │
                                      ▼
                           context projection
                                      │
                                      ▼
                                     LLM
```

This boundary prevents a model-generated or stale context artifact from becoming an authorization mechanism.

---

## 4. Worked Context-Budget Example

Consider a model with a **32K-token context limit**. The exact accounting varies by provider and model, but an architect can establish an explicit application budget.

Example allocation:

| Component | Budget |
|---|---:|
| System/developer policy | 2,000 |
| User request | 1,000 |
| Recent conversation | 5,000 |
| Retrieved evidence | 10,000 |
| Tool results | 4,000 |
| Application/task state | 2,000 |
| Output reservation | 6,000 |
| **Total** | **30,000** |
| Safety margin | **2,000** |

The safety margin accommodates provider/API overhead and unexpected growth.

### What happens when retrieval returns 18K tokens?

Do **not** simply exceed the budget or remove the output reservation.

Apply a deterministic degradation policy:

```text
18K retrieved tokens
        │
        ▼
authorization filter
        │
        ▼
relevance ranking
        │
        ▼
deduplication
        │
        ▼
compression / passage selection
        │
        ▼
10K retrieval budget
```

If the result still cannot fit:

1. reduce low-priority retrieved evidence;
2. reduce stale or redundant conversation history;
3. reduce optional tool output;
4. preserve mandatory policy and authorization context;
5. preserve sufficient output reservation;
6. if minimum safe context cannot be assembled, fail closed or use a degraded/fallback path.

### Priority example

```text
Priority 0 — must retain
  authorization context
  mandatory safety policy
  task-critical authoritative data

Priority 1 — retain when possible
  relevant recent conversation
  high-authority retrieved evidence

Priority 2 — compress/prune first
  old conversation
  redundant passages
  optional examples
  verbose tool output
```

The important architectural idea is that **context eviction is a policy decision**, not an accidental consequence of string concatenation.

---

## 5. Structured Output: Shape Is Not Truth

Structured-output facilities are preferable to asking a model to format arbitrary JSON when the target provider/model supports them. However, the architect must distinguish three guarantees:

```text
                ┌───────────────────────┐
                │ Syntax / schema       │
                │ Is the shape valid?   │
                └──────────┬────────────┘
                           ▼
                ┌───────────────────────┐
                │ Semantic validation   │
                │ Is the value sensible?│
                └──────────┬────────────┘
                           ▼
                ┌───────────────────────┐
                │ Business validation   │
                │ Is it allowed?        │
                └───────────────────────┘
```

For example, this can be schema-valid:

```json
{
  "refund_amount": 999999.99,
  "currency": "INR"
}
```

but still violate the account's actual refund limit.

Therefore:

- schema validation protects structure;
- semantic validation checks domain meaning;
- authoritative service calls verify facts;
- authorization and business rules determine whether an action is permitted.

Provider guarantees, supported schemas, constrained-decoding behavior, limits, and fallback semantics vary by API/model and can change over time. Treat them as versioned external dependencies and verify the exact production model/API documentation.

---

## 6. Trace-Level Observability

Prompt/context observability should be connected to the application's distributed trace rather than treated as an isolated log entry.

A useful production trace is:

```text
trace_id = 8f31...
   │
   ├── request received
   │
   ├── authentication / authorization
   │
   ├── intent analysis
   │
   ├── retrieval
   │     ├── query
   │     ├── candidate count
   │     └── selected source IDs
   │
   ├── context assembly
   │     ├── policy version
   │     ├── context items
   │     └── token budget
   │
   ├── model invocation
   │     ├── provider/model
   │     ├── prompt version
   │     ├── input tokens
   │     └── output tokens
   │
   ├── tool calls
   │     ├── tool name
   │     └── authorization result
   │
   ├── output validation
   │
   ├── business-policy validation
   │
   └── final outcome
```

Do not log raw sensitive content merely to obtain this correlation. Prefer metadata, identifiers, hashes where appropriate, redacted payloads, and controlled sampling.

### Recommended correlation fields

```text
trace_id
request_id
conversation_id
prompt_version
context_policy_version
model_id
retrieval_ids
retrieval_scores
input_tokens
output_tokens
latency_ms
validation_status
tool_calls
fallback_reason
outcome
```

This allows an architect to answer questions such as:

- Which prompt version produced this decision?
- Which documents were supplied to the model?
- Did retrieval fail or return weak evidence?
- Was the model output schema-valid?
- Which tool caused latency?
- Did the request execute under degraded context?

---

## 7. Provenance and Citation Integrity

For RAG and document-processing systems, provenance should survive the complete pipeline:

```text
Source document
      │
      ▼
Chunk / passage
      │
      ▼
Embedding / index
      │
      ▼
Retrieved item
      │
      ▼
Context assembler
      │
      ▼
LLM
      │
      ▼
Answer + source references
```

Every retrieved context item should ideally retain metadata such as:

- source ID;
- document version;
- chunk/passage ID;
- tenant/access scope;
- source timestamp;
- authority classification;
- retrieval score;
- and canonical citation/reference information.

### Citation correctness has multiple dimensions

A citation can be:

1. **Present** — a citation was included.
2. **Relevant** — the cited source is related to the answer.
3. **Entailing** — the source actually supports the claim.
4. **Authorized** — the user is allowed to receive the cited information.
5. **Current** — the cited source satisfies freshness requirements.

Therefore, a system should not treat `citation != null` as sufficient evidence of grounding.

For high-value workflows, consider validating important claims against retrieved passages or requiring the model to map claims to source IDs that the application can verify.

### Example response contract

```json
{
  "answer": "The enterprise plan supports SSO.",
  "citations": [
    {
      "source_id": "product-doc-184",
      "document_version": "2026-07-12",
      "passage_id": "p-42"
    }
  ]
}
```

The application can then verify that `passage_id=p-42` is authorized, exists, and contains evidence appropriate for the claim.

---

## 8. Production Review Summary

These refinements reinforce seven architectural principles for Chapter 4:

1. **Use “prompt engineering” and “context engineering” as practical architectural terms, while acknowledging that industry terminology evolves.**
2. **Treat prompt injection as a threat-model and defense-in-depth problem, not a prompt-formatting problem.**
3. **Keep authoritative application state outside the LLM; treat model context as a derived task-specific projection.**
4. **Make context budgeting and eviction deterministic and observable.**
5. **Treat structured output as a shape guarantee, not a truth or authorization guarantee.**
6. **Correlate prompt/context activity with end-to-end distributed traces.**
7. **Preserve provenance from source through retrieval, context assembly, response, and citation validation.**

These principles become especially important in the upcoming chapters on embeddings, vector databases, RAG, agents, tools, memory, and production AI observability.
