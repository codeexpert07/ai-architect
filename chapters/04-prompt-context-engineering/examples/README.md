# Chapter 4 Code Examples

These examples make the architecture concepts in Chapter 4 executable. **Every example from `01` through `14` now contains a complete path from application-side context/prompt construction to a real OpenAI Responses API call and application-side handling of the result.** `15_end_to_end_openai.py` remains a cross-cutting reference that combines the strongest patterns into one example with structured output. `16_security_boundaries.py` is intentionally provider-neutral so the security controls are visible without hiding them behind an LLM SDK.

## Navigation

- [← Back to Chapter 4](../README.md)
- [Chapter 4 learning objectives](../README.md#learning-objectives)
- [Chapter 4 architecture overview](../README.md#41-why-prompt-engineering-is-an-architecture-concern)
- [Chapter 4 production checklist](../README.md#445-production-checklist)
- [Production architecture refinements](../PRODUCTION_REFINEMENTS.md)

Use the links in the table below to jump directly to the runnable implementation for each chapter concept.

## Examples by chapter concept

| Example | Chapter sections | Concepts demonstrated |
|---|---|---|
| [`01_prompt_contract.py`](./python/01_prompt_contract.py) | 4.1–4.5 | Prompt contract → OpenAI call → answer |
| [`02_zero_and_few_shot.py`](./python/02_zero_and_few_shot.py) | 4.6–4.7 | Example selection → zero/few-shot prompts → LLM classification |
| [`03_boundaries_and_output_validation.py`](./python/03_boundaries_and_output_validation.py) | 4.8–4.10 | Delimiters → untrusted input → structured LLM output → validation |
| [`04_context_budget_and_assembly.py`](./python/04_context_budget_and_assembly.py) | 4.11–4.12 | Token budget → context selection → assembled prompt → LLM answer |
| [`05_authority_and_conversation_state.py`](./python/05_authority_and_conversation_state.py) | 4.13–4.17 | State/compaction/ranking → context → LLM answer |
| [`06_tool_and_retrieval_context.py`](./python/06_tool_and_retrieval_context.py) | 4.18–4.19 | Tool filtering/retrieval normalization → LLM answer |
| [`07_injection_and_least_privilege.py`](./python/07_injection_and_least_privilege.py) | 4.20–4.23 | Authorization/injection checks → model call → safe answer |
| [`08_prompt_versioning_and_evaluation.py`](./python/08_prompt_versioning_and_evaluation.py) | 4.24–4.26 | Versioned prompt → baseline/candidate model evaluation → regression gate |
| [`09_deterministic_controls_and_cost.py`](./python/09_deterministic_controls_and_cost.py) | 4.27–4.28 | LLM decision → deterministic business rule → usage accounting |
| [`10_templates_and_model_portability.py`](./python/10_templates_and_model_portability.py) | 4.29–4.31 | Template/capability selection → real model invocation |
| [`11_policy_composition_and_context_contracts.py`](./python/11_policy_composition_and_context_contracts.py) | 4.32–4.33 | Typed context contract/policy composition → LLM |
| [`12_failure_handling_and_observability.py`](./python/12_failure_handling_and_observability.py) | 4.34–4.36 | Degraded context → LLM → actual schema validation → privacy-aware telemetry |
| [`13_workflow_and_antipatterns.py`](./python/13_workflow_and_antipatterns.py) | 4.37–4.40 | Production workflow → model invocation → application result |
| [`14_document_qa_and_release_checklist.py`](./python/14_document_qa_and_release_checklist.py) | 4.41–4.45 | Evidence filtering → document Q&A → deterministic release checks |
| [`15_end_to_end_openai.py`](./python/15_end_to_end_openai.py) | Cross-cutting | Reusable data classes → Responses API → structured output → deterministic authorization |
| [`16_security_boundaries.py`](./python/16_security_boundaries.py) | Production refinement | Tenant isolation → untrusted tool output → least privilege → side-effect approval |

## Standard end-to-end shape

Most examples follow this architecture:

```text
Application state / user input
            │
            ▼
   Concept-specific logic
   (selection / policy / budget /
    authorization / validation)
            │
            ▼
       Prompt / context
            │
            ▼
   OpenAI Responses API
            │
            ▼
     Model-generated result
            │
            ▼
 Deterministic application logic
 (schema / semantic / security /
   business-rule / telemetry)
```

The important boundary is that the LLM **does not become the source of truth**. Application code owns authorization and business invariants; the model is a probabilistic reasoning/generation component inside that workflow.

## Running the examples with uv

This directory is a **uv project**. Install [uv](https://docs.astral.sh/uv/) and run from the `examples` directory:

```bash
uv sync
export OPENAI_API_KEY="your-api-key"
export OPENAI_MODEL="gpt-5.5"  # optional
```

Then run any example through the project environment:

```bash
uv run python python/01_prompt_contract.py
uv run python python/02_zero_and_few_shot.py
uv run python python/03_boundaries_and_output_validation.py
uv run python python/16_security_boundaries.py
# ...or any other example
```

Syntax validation does not make model calls:

```bash
uv run python -m compileall python
```

When dependencies change, regenerate the lock file with:

```bash
uv lock
```

The examples intentionally require an API key because they demonstrate a **real provider integration**. Never commit API keys to the repository.

## Important architectural caveats

- Prompt delimiters help structure input but are not a security boundary.
- Structured output/schema validation proves output shape, not truth or authorization.
- Injection detection in the examples is intentionally simplistic; production systems need layered controls.
- Token counts are illustrative; use the target provider/model's tokenizer and accounting rules in production.
- Model capability metadata is illustrative; capability discovery and configuration should come from the actual model gateway.
- Model-generated summaries are derived data, not authoritative business state.
- The examples are intentionally small. Production systems additionally need authentication, authorization, retries/backoff, rate-limit handling, timeout budgets, secret management, telemetry redaction, cost controls, circuit breakers, and provider-specific error handling.
