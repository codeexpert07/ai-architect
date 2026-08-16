# Chapter 4 Code Examples

These examples make the architecture concepts in Chapter 4 executable. Most examples are provider-neutral and use deterministic stand-ins so that the architectural boundary remains easy to understand. One dedicated example (`15_end_to_end_openai.py`) uses a real OpenAI Responses API call to demonstrate the complete path from application data classes to a validated LLM response.

## Why these examples exist

Chapter 4 is deliberately architecture-first. The examples are small reference implementations for the recurring production boundaries: prompt contracts, context selection, state management, security, validation, evaluation, cost, portability, and observability.

The provider-neutral examples explain the architecture without forcing every concept to depend on one vendor. The end-to-end example then shows how the same abstractions connect to a real model API.

## Examples by chapter concept

| Example | Chapter sections | Concepts demonstrated |
|---|---|---|
| `01_prompt_contract.py` | 4.1–4.5 | Prompt as an input contract, separation of instructions/data, observable behavior |
| `02_zero_and_few_shot.py` | 4.6–4.7 | Zero-shot, few-shot, dynamic example selection |
| `03_boundaries_and_output_validation.py` | 4.8–4.10 | Delimiters, structured output, schema validation, output contracts |
| `04_context_budget_and_assembly.py` | 4.11–4.12 | Token budgeting, context selection, explicit assembly pipeline |
| `05_authority_and_conversation_state.py` | 4.13–4.17 | Information authority, conversation state, compaction, ranking |
| `06_tool_and_retrieval_context.py` | 4.18–4.19 | Tool-result filtering, normalization, retrieval context |
| `07_injection_and_least_privilege.py` | 4.20–4.23 | Direct/indirect injection, authorization, least privilege, secret isolation |
| `08_prompt_versioning_and_evaluation.py` | 4.24–4.26 | Versioning, regression cases, behavioral evaluation |
| `09_deterministic_controls_and_cost.py` | 4.27–4.28 | Business-rule enforcement, token economics, latency, retries |
| `10_templates_and_model_portability.py` | 4.29–4.31 | Stable prefixes, templates, parameterization, model capability checks |
| `11_policy_composition_and_context_contracts.py` | 4.32–4.33 | Policy composition, typed context contracts, field allowlists |
| `12_failure_handling_and_observability.py` | 4.34–4.36 | Degraded context, explicit failure states, privacy-aware telemetry |
| `13_workflow_and_antipatterns.py` | 4.37–4.40 | Production workflow, anti-pattern replacements, enterprise separation of concerns |
| `14_document_qa_and_release_checklist.py` | 4.41–4.45 | Document Q&A, evidence filtering, production checklist, key takeaways |
| `15_end_to_end_openai.py` | Cross-cutting | Real LLM call, reusable data classes, structured output, deterministic validation, request correlation |

## End-to-end example

`15_end_to_end_openai.py` demonstrates this production-oriented flow:

```text
Authoritative application state
          │
          ▼
   SupportContext dataclass
          │
          ▼
   PromptContract dataclass
          │
          ▼
  OpenAI Responses API
          │
          ▼
   Pydantic structured output
          │
          ▼
 Deterministic business validation
          │
          ▼
       Application
```

The important boundary is that the LLM **does not become the source of truth**. `SupportContext` represents authoritative application state; the model receives a projection of that state and produces a proposed answer; deterministic application validation remains responsible for enforcing business rules.

## Running the examples

From the `examples` directory:

```bash
python -m pip install -r requirements.txt
```

Provider-neutral examples:

```bash
python python/01_prompt_contract.py
python python/02_zero_and_few_shot.py
# ...and so on
```

For the real LLM example, set an API key first:

```bash
export OPENAI_API_KEY="your-api-key"
export OPENAI_MODEL="gpt-5.5"  # optional
python python/15_end_to_end_openai.py
```

The example uses the OpenAI Python SDK's Responses API and structured-output parsing. The SDK reads `OPENAI_API_KEY` from the environment; never commit API keys to the repository.

Or run syntax validation across all examples:

```bash
python -m compileall python
```

## Important architectural caveats

- Prompt delimiters help structure input but are not a security boundary.
- Structured output/schema validation proves output shape, not truth or authorization.
- Injection detection in the examples is intentionally simplistic; production systems need layered controls.
- Token counts are illustrative; use the target provider/model's tokenizer and accounting rules in production.
- Model capability metadata is illustrative; capability discovery and configuration should come from the actual model gateway.
- Model-generated summaries are treated as derived data, not authoritative business state.
- The live OpenAI example is intentionally small. Production systems should additionally implement authentication, authorization, retries/backoff, rate-limit handling, timeout budgets, secret management, telemetry redaction, cost controls, and provider-specific error handling.
