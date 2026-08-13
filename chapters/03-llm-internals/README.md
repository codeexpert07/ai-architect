# Chapter 3 — Large Language Model Internals

## Prerequisites

You should be comfortable with the production-oriented GenAI concepts from Chapter 2: inference, tokens, context windows, model selection, decoding, and the distinction between probabilistic model behavior and deterministic application logic.

This chapter intentionally avoids advanced mathematics and implementation code. The goal is **architectural fluency**: understand the internal mechanisms that create system-level constraints, costs, latency characteristics, and design trade-offs.

> **Theory first. Code starts when we begin communicating with models.**

---

## Learning Objectives

By the end of this chapter, you should be able to:

- Explain what a large language model actually does during inference.
- Explain tokenization, token embeddings, positional information, and the transformation from text to model representations.
- Describe the major components of a Transformer block.
- Explain self-attention, causal attention, multi-head attention, feed-forward networks, residual connections, and normalization at an architectural level.
- Distinguish pretraining, fine-tuning, inference, and runtime context.
- Explain next-token prediction, logits, probabilities, and decoding.
- Distinguish encoder-only, decoder-only, and encoder-decoder architectures.
- Explain context length, prefill, decode, KV cache, batching, and inference latency.
- Understand model parameters, active parameters, memory footprint, quantization, and GPU capacity planning.
- Explain why model size alone is not a sufficient model-selection criterion.
- Understand long-context, mixture-of-experts, multimodal, and structured-output implications.
- Identify the architectural levers for improving quality, latency, throughput, and cost.
- Evaluate hosted versus self-hosted inference at an architectural level.
- Understand why model behavior must be evaluated and regression-tested like a production dependency.

---

## 3.1 Why an AI Architect Needs LLM Internals

An architect does not need to implement backpropagation, train a foundation model, or write CUDA kernels. However, treating an LLM as a generic HTTP endpoint creates important blind spots.

Understanding the inference pipeline helps answer questions such as:

- Why did latency increase when the prompt became larger?
- Why is first-token latency different from total generation latency?
- Why does a long conversation consume more memory and cost more?
- Why can a smaller model be a better production choice than a larger model?
- Why does self-hosting require much more memory than the raw parameter count suggests?
- Why does KV caching matter?
- Why can streaming improve user experience without reducing total compute?
- Why can a larger context window make an application worse rather than better?
- Why should changing a model version trigger regression evaluation?

The objective is not to become a model researcher. It is to understand enough of the mechanism to predict **architectural consequences**.

---

## 3.2 The LLM in One Sentence

A decoder-style language model can be summarized as:

> **Given the tokens currently in context, estimate a probability distribution for the next token, select a token according to a decoding policy, append it to the sequence, and repeat until a stopping condition is reached.**

Conceptually:

```text
Input text
   │
   ▼
Tokenizer
   │
   ▼
Token IDs
   │
   ▼
Embeddings + positional information
   │
   ▼
Transformer blocks
   │
   ▼
Logits over vocabulary
   │
   ▼
Decoding policy
   │
   ▼
Next token
   │
   └──────────────► repeat
```

This is the central mental model for the rest of the chapter.

An autoregressive LLM does not normally create the complete response in one operation. It repeatedly predicts the next token.

---

## 3.3 From Text to Tokens

Neural networks operate on numerical representations. Text therefore passes through a tokenizer before entering the neural network.

```text
"Design a payment service"
          │
          ▼
       Tokenizer
          │
          ▼
     Token sequence
          │
          ▼
       Token IDs
```

A token is not necessarily a word. Depending on the tokenizer, it can represent a whole word, part of a word, punctuation, whitespace-related text, or another subword unit.

### Architectural consequences

Tokens influence:

- **Cost:** providers commonly meter input and output tokens.
- **Context:** context windows are expressed in tokens.
- **Latency:** more input tokens generally require more processing.
- **Retrieval:** retrieved documents consume context budget.
- **Prompt design:** seemingly small textual changes can change token count.
- **Multilingual behavior:** different languages can have different tokenization efficiency.

Never build an architecture around assumptions such as “one token equals one word.”

### Token budget is an architectural resource

A useful production mindset is to treat tokens like a resource similar to CPU time, database I/O, or network bandwidth.

```text
Request budget
   │
   ├── system instructions
   ├── conversation history
   ├── retrieved context
   ├── tool results
   └── expected output

Total token budget
   │
   ├── quality implications
   ├── latency implications
   └── cost implications
```

This becomes especially important in RAG and agentic systems, where context can grow through retrieved documents, tool responses, and accumulated state.

---

## 3.4 Token Embeddings

A token ID is an integer. The Transformer needs a dense numerical representation, so the token ID is mapped through a learned embedding table to a vector.

Conceptually:

```text
Token ID
   │
   ▼
Embedding table
   │
   ▼
Dense vector
```

During training, these representations become useful for capturing statistical relationships between tokens and linguistic patterns.

### Do not confuse two types of embeddings

There are two concepts that will appear throughout this handbook:

| Concept | Purpose |
|---|---|
| LLM token embedding | Internal representation used by the language model |
| Application embedding | Vector representation used for semantic search, retrieval, clustering, etc. |

Both are vectors, but they serve different architectural purposes. The later embeddings/vector-database chapter will cover application embeddings in depth.

---

## 3.5 Position Matters

A model must distinguish between sequences such as:

```text
Java calls Python
Python calls Java
```

The tokens are similar, but their ordering changes meaning.

Transformers therefore need positional information. Different model families use different mechanisms, including learned positional representations and rotary position representations.

For an architect, the key point is:

> **Attention determines relationships among token representations, while positional mechanisms provide information about sequence position.**

Position handling matters when reasoning about:

- context limits,
- long-context behavior,
- model compatibility,
- memory requirements,
- and inference performance.

---

## 3.6 Transformer Architecture

The Transformer was introduced in *Attention Is All You Need* and became the dominant architecture behind modern language models.

A simplified decoder-only Transformer can be visualized as:

```text
Token IDs
   │
   ▼
Token embeddings
   +
Position information
   │
   ▼
┌──────────────────────────────┐
│ Transformer block            │
│                              │
│   Self-attention             │
│          │                   │
│   Residual + normalization   │
│          │                   │
│   Feed-forward network       │
│          │                   │
│   Residual + normalization   │
└──────────────────────────────┘
   │
   ├── repeated many times
   ▼
Final representation
   │
   ▼
Output projection
   │
   ▼
Vocabulary logits
```

Exact implementations vary. Modern architectures can change normalization placement, attention mechanisms, activation functions, positional representations, or the feed-forward design.

The stable architectural idea is that repeated Transformer blocks transform representations by combining **contextual information exchange** with **learned nonlinear transformations**.

---

## 3.7 Self-Attention

Self-attention allows the representation of one token to incorporate information from other tokens in the same context.

Consider:

```text
The architect approved the design because it was scalable.
```

The representation of “it” can benefit from relationships with other tokens, including “design” and “scalable.”

Attention is commonly described using three concepts:

- **Query (Q):** what this position is looking for.
- **Key (K):** what each position offers for matching.
- **Value (V):** the information that is aggregated after relevance is determined.

Conceptually:

```text
Token representations
        │
   ┌────┼────┐
   ▼    ▼    ▼
   Q    K    V
   │    │    │
   └─compare─┘
        │
        ▼
   attention weights
        │
        ▼
weighted values
        │
        ▼
updated representation
```

The underlying operation is scaled dot-product attention. An architect does not need to derive the equation, but should understand the consequence: attention requires computation involving relationships among positions in the context.

### Why this matters architecturally

Attention helps explain why context length is such an important systems concern. Longer sequences mean more information must be processed and represented, although the exact cost depends on the architecture and serving optimizations.

---

## 3.8 Causal Attention

A decoder-only generative model must not use future tokens when predicting the current token.

For a sequence:

```text
The service should return a valid response
```

the model cannot use the future token “response” to predict the preceding token.

A causal mask creates a triangular visibility pattern:

```text
             Visible keys
             1  2  3  4  5
Query 1      ✓  ·  ·  ·  ·
Query 2      ✓  ✓  ·  ·  ·
Query 3      ✓  ✓  ✓  ·  ·
Query 4      ✓  ✓  ✓  ✓  ·
Query 5      ✓  ✓  ✓  ✓  ✓
```

This prevents information leakage during training and matches autoregressive generation.

Causal attention is one of the reasons decoder-only models are naturally suited to next-token generation.

---

## 3.9 Multi-Head Attention

Transformers generally use multiple attention heads rather than one single attention operation.

Conceptually:

```text
Hidden representation
        │
   ┌────┼─────┐
   ▼    ▼     ▼
 Head 1 Head 2 ... Head N
   │    │     │
   └────┼─────┘
        ▼
    projection
        │
        ▼
   block output
```

Different heads can learn different relationships or patterns.

The term “head” does not mean a separate model. It is a learned attention subspace within the Transformer block.

### MHA, MQA, and GQA

Modern serving systems may use different key/value sharing strategies:

- **Multi-Head Attention (MHA):** conventional separate key/value representations for attention heads.
- **Multi-Query Attention (MQA):** multiple query heads share key/value representations.
- **Grouped-Query Attention (GQA):** groups of query heads share key/value representations.

These designs can materially affect KV-cache memory and inference throughput. This is a good example of an internal model design choice becoming a production architecture concern.

---

## 3.10 Feed-Forward Networks

Attention allows information to move between token positions. Transformer blocks also contain a feed-forward network, often called an MLP block.

Conceptually:

```text
Token representation
        │
        ▼
Learned projection
        │
        ▼
Nonlinear transformation
        │
        ▼
Learned projection
        │
        ▼
Updated representation
```

The feed-forward network performs learned nonlinear transformations for each position after contextual information has been incorporated.

A significant portion of a model's parameters can reside in these components.

### Mixture-of-Experts

Some modern architectures use **Mixture-of-Experts (MoE)** designs. Instead of activating one large feed-forward network for every token, a routing mechanism selects a subset of experts.

```text
Token representation
        │
        ▼
     Router
     /   \
    ▼     ▼
 Expert A  Expert B   ... many experts
    │       │
    └───┬───┘
        ▼
   combined output
```

This creates an important distinction between:

- total parameters,
- active parameters per token,
- memory required to host the model,
- and compute required for each token.

Therefore, “the model has X billion parameters” is not sufficient information for capacity planning.

---

## 3.11 Residual Connections and Normalization

Deep Transformer networks use residual paths so information can flow around transformations.

```text
Input ────────────────┐
  │                   │
  ▼                   │
Transformation        │
  │                   │
  └───────► Add ◄─────┘
             │
             ▼
           Output
```

Normalization helps stabilize representations throughout the network.

You may encounter architectures described as **pre-norm** or **post-norm**, depending on where normalization occurs relative to attention and feed-forward transformations.

For an application architect, the important point is not implementation detail. These components are part of what makes very deep Transformer stacks trainable and usable at scale.

---

## 3.12 Training vs Inference

A foundation model is created through a training process that repeatedly adjusts model parameters based on a training objective.

At a high level:

```text
Training data
    │
    ▼
Tokenization
    │
    ▼
Model forward pass
    │
    ▼
Prediction vs target
    │
    ▼
Loss
    │
    ▼
Parameter update
    │
    └──────► repeat at very large scale
```

Inference is different:

```text
Request context
    │
    ▼
Model weights
    │
    ▼
Forward computation
    │
    ▼
Generated tokens
```

| Concern | Training | Inference |
|---|---|---|
| Goal | Learn parameters | Produce output |
| Parameter updates | Yes | Normally no |
| Gradients | Required | Normally no |
| Data | Very large training corpus | Request-specific context |
| Infrastructure | Training clusters | Serving infrastructure |
| Architect involvement | Usually indirect | Direct |

This distinction is fundamental to understanding RAG, memory, fine-tuning, and agent systems.

---

## 3.13 Why a Document Does Not Automatically Become Model Knowledge

Suppose an application sends a document to a model as part of a request.

The document becomes **runtime context**. It does not automatically modify the model's weights.

```text
Document
   │
   ▼
Runtime context ─────► inference
                         │
                         ▼
                       answer

Model weights remain unchanged
```

This distinction leads to three different architectural mechanisms:

1. **Prompt/context:** provide information at inference time.
2. **Retrieval:** dynamically select relevant information and provide it as context.
3. **Fine-tuning:** modify model behavior through additional training.

Later chapters will examine retrieval and fine-tuning in depth.

---

## 3.14 Next-Token Prediction

For a decoder-style language model, a common training objective is to predict the next token.

Conceptually:

```text
The database connection pool  →  must
The database connection pool must  →  be
The database connection pool must be  →  bounded
```

The model learns statistical patterns from enormous amounts of training data.

This produces an important architectural warning:

> **An LLM is optimized to model token distributions, not to act as a formal database of truth.**

Useful reasoning-like behavior can emerge from learned representations and computation, but high-impact systems should still use authoritative data and deterministic verification where correctness matters.

---

## 3.15 Logits, Probabilities, and Decoding

After the Transformer stack processes the context, the model produces scores called **logits** over its vocabulary.

```text
Transformer representation
          │
          ▼
Output projection
          │
          ▼
Vocabulary logits
          │
          ▼
Probability distribution
          │
          ▼
Decoding policy
          │
          ▼
Selected next token
```

A probability distribution is commonly derived from logits using softmax.

The important architectural distinction is:

- **Model:** computes scores for possible next tokens.
- **Decoding policy:** determines how a token is selected.
- **Application:** decides what to do with the generated sequence.

### Temperature

Temperature changes the effective sharpness of the probability distribution.

Lower temperature generally makes selection more concentrated around high-probability tokens. Higher temperature generally permits more variation.

### Top-k

Top-k restricts candidate selection to a fixed number of highest-scoring candidates.

### Top-p

Top-p restricts candidate selection to the smallest group of tokens whose cumulative probability reaches a chosen threshold.

These are generation controls, not mechanisms for making a model more knowledgeable.

---

## 3.16 Stopping Generation

Generation continues until a stopping condition is reached. Common conditions include:

- a designated end-of-sequence token,
- a configured maximum output-token limit,
- a stop sequence,
- structured-output completion,
- tool-call completion,
- or an application-level cancellation.

This matters operationally because an unbounded or poorly controlled output can increase cost and latency.

A production architecture should therefore treat output limits and cancellation as first-class controls.

---

## 3.17 Encoder-Only, Decoder-Only, and Encoder-Decoder Models

Transformers are not synonymous with chat LLMs.

### Encoder-only

Encoder models create contextual representations of an input sequence.

Common workloads include:

- classification,
- semantic representation,
- retrieval,
- entity extraction,
- and ranking.

BERT-family models are a familiar example.

### Decoder-only

Decoder models use causal attention and generate autoregressively.

Common workloads include:

- chat,
- code generation,
- completion,
- tool orchestration,
- and general text generation.

Most modern general-purpose chat LLMs use decoder-style architectures.

### Encoder-decoder

An encoder processes the source sequence and a decoder generates output conditioned on it.

Common workloads include:

- translation,
- summarization,
- and other sequence-to-sequence transformations.

The architectural lesson is simple:

> **Choose the model architecture according to workload characteristics, not according to the assumption that every AI problem is a chat problem.**

---

## 3.18 Context Window

The **context window** is the amount of tokenized information a model can process as context for an inference request, subject to the model and serving system's limits.

Context may include:

```text
System instructions
+ conversation history
+ user request
+ retrieved documents
+ tool results
+ structured state
+ previous agent messages
```

A larger context window is useful, but it is not free.

### Larger context can mean

- more input processing,
- higher latency,
- higher cost,
- more memory pressure,
- more opportunities for irrelevant information,
- and more difficult context management.

Therefore:

> **Maximum context is a capacity limit, not a recommendation to fill the window.**

---

## 3.19 Context Quality vs Context Quantity

A common early-stage mistake is to assume:

```text
More context = better answer
```

A better mental model is:

```text
Relevant context
        +
Correct context
        +
Well-structured context
        +
Sufficient context
        =
Useful context
```

An architect should prefer the smallest context that gives the model the information required for the task.

This principle becomes critical in RAG and agentic architectures, where context is assembled dynamically.

---

## 3.20 Prefill and Decode

Autoregressive inference is commonly understood as two major phases.

### Prefill

The system processes the existing input context before generating the first output token.

```text
Large input context
       │
       ▼
    Prefill
       │
       ▼
KV cache + initial state
       │
       ▼
First generated token
```

Prefill is strongly affected by input length and is often compute-intensive.

### Decode

After the initial context has been processed, generation proceeds token by token.

```text
Previous token + KV cache
          │
          ▼
        Decode
          │
          ▼
     Next token
          │
          └────► repeat
```

Decode is strongly affected by output length, model architecture, memory bandwidth, scheduling, and concurrency.

### Why the distinction matters

A system can have:

- good throughput but poor time-to-first-token,
- good first-token latency but poor long-output performance,
- or different bottlenecks for short and long requests.

Therefore, production inference should not be summarized by one number such as tokens/second.

---

## 3.21 KV Cache

During autoregressive generation, the model repeatedly needs attention information from previously processed tokens.

Recomputing all prior key and value representations for every generated token would be inefficient. The **KV cache** stores relevant key/value states so that later decode steps can reuse them.

Conceptually:

```text
Initial context
     │
     ▼
Prefill
     │
     ▼
KV cache
     │
     ├──────────────┐
     ▼              │
Decode token 1      │
     │              │
     ▼              │
Decode token 2 ◄────┘
     │
     ▼
Decode token 3
```

### Why architects care

KV cache:

- reduces redundant computation during decoding,
- improves generation efficiency,
- consumes accelerator memory,
- grows with context and generation state,
- becomes a major constraint under high concurrency.

This is one reason GPU capacity cannot be estimated from model weights alone.

---

## 3.22 Model Parameters and Memory

Parameter count is one of the most visible model metrics, but it is not the same as runtime memory.

At a high level:

```text
Inference memory
    │
    ├── model weights
    ├── KV cache
    ├── activations / temporary buffers
    ├── runtime and framework overhead
    ├── batching overhead
    └── safety/headroom
```

A simplified weight-memory estimate is:

> **weight memory ≈ parameter count × bytes per parameter**

For example, lower-precision representations reduce weight memory. But the resulting estimate is only a starting point.

### Why the estimate is insufficient

Actual capacity depends on:

- precision,
- model architecture,
- context length,
- concurrency,
- KV-cache implementation,
- batch size,
- runtime overhead,
- accelerator topology,
- and desired headroom.

An architect should never select a GPU based only on “the model has X billion parameters.”

---

## 3.23 Precision and Quantization

Model weights can be represented using different numerical precisions.

Common categories include:

- 32-bit floating point,
- 16-bit floating point or related 16-bit formats,
- 8-bit representations,
- 4-bit representations,
- and other specialized formats.

**Quantization** reduces numerical precision to reduce memory and potentially improve inference efficiency.

Conceptually:

```text
Higher precision
   │
   ├── more memory
   └── potentially higher fidelity

Lower precision
   │
   ├── less memory
   ├── potentially better economics
   └── possible quality degradation
```

Quantization is therefore an engineering trade-off, not a free optimization.

Quality must be evaluated on the actual workload. A model can pass generic benchmarks and still degrade materially on a domain-specific task.

---

## 3.24 Model Size vs Capability

It is tempting to assume:

```text
larger model = better model
```

In practice, production model quality depends on multiple dimensions:

- model architecture,
- training data,
- post-training,
- instruction following,
- reasoning capability,
- tool-use behavior,
- context handling,
- domain fit,
- quantization,
- inference configuration,
- and evaluation methodology.

A smaller model can be preferable when:

- the task is narrow,
- latency is critical,
- traffic is high,
- privacy requires local inference,
- or cost dominates quality differences.

Model selection is therefore an optimization problem across **quality, latency, cost, reliability, and governance**.

---

## 3.25 Dense Models vs Mixture-of-Experts

A dense model activates essentially the full model computation for each token.

An MoE model contains multiple expert networks and a routing mechanism that selects a subset for each token.

This creates two different parameter concepts:

```text
Total parameters
      ≠
Active parameters per token
```

MoE can provide high total capacity while reducing the computation performed for each token relative to a dense model of the same total parameter count.

However, hosting still requires the relevant weights to be available, and distributed serving can introduce additional complexity.

Architectural considerations include:

- memory placement,
- expert routing,
- network traffic,
- load imbalance,
- batching,
- and serving-engine support.

---

## 3.26 Batching and Throughput

Accelerators are more efficiently utilized when multiple requests can share computation.

Traditional batching groups requests together before execution. LLM serving commonly uses **continuous batching**, where requests can enter and leave a running batch dynamically.

Conceptually:

```text
Request A ────────┐
Request B ────────┼──► Scheduler ──► GPU
Request C ────────┘
                      ▲
Request D joins ──────┘
```

Continuous batching is particularly useful because generated outputs have different lengths.

### Throughput vs latency

Batching can improve accelerator utilization and aggregate throughput, but excessive batching or queueing can hurt individual request latency.

An architect therefore needs explicit service objectives such as:

- p50 latency,
- p95 latency,
- p99 latency,
- time to first token,
- output token rate,
- requests per second,
- tokens per second,
- and cost per request.

---

## 3.27 TTFT and Generation Latency

For interactive applications, **Time to First Token (TTFT)** is an important user-experience metric.

A useful decomposition is:

```text
Request received
      │
      ▼
Queue / scheduling
      │
      ▼
Prefill
      │
      ▼
First token
      │
      ▼
Decode stream
      │
      ▼
Final token
```

Therefore:

> **Total latency and perceived latency are not the same thing.**

Streaming can make an application feel much faster because users see output as it is generated, even if the total generation time is unchanged.

### Metrics to track

At minimum, production systems should distinguish:

- request latency,
- queue latency,
- TTFT,
- inter-token latency or generation rate,
- total output tokens,
- input tokens,
- and cancellation rate.

Use percentile metrics rather than averages alone.

---

## 3.28 Why Long Output Is Expensive

Autoregressive generation means each generated token requires another decode step.

Therefore, increasing the output limit can increase:

- compute,
- latency,
- memory activity,
- and cost.

An architect should not blindly set very large maximum output limits.

Better controls include:

- task-specific output limits,
- structured output,
- stop conditions,
- concise response instructions,
- and application-level cancellation.

---

## 3.29 Long-Context Architectures

Large context windows create opportunities for:

- long documents,
- long conversations,
- code repositories,
- multi-step agent state,
- and large tool results.

But long context introduces architectural risks.

### Risk 1 — Cost

More tokens increase processing and commonly increase provider charges.

### Risk 2 — Latency

Large inputs increase prefill work.

### Risk 3 — Memory

Long contexts can increase KV-cache requirements, especially under concurrency.

### Risk 4 — Relevance dilution

Important information can be surrounded by large amounts of irrelevant information.

### Risk 5 — Context management complexity

An application must decide what information to retain, summarize, retrieve, discard, or reintroduce.

The correct architectural response is not simply “buy a model with a larger context window.”

---

## 3.30 Model Context Is Not Application Memory

A model's context window is temporary inference state. It should not automatically be treated as durable memory.

```text
Durable application state
          │
          ▼
   Context assembly
          │
   ┌──────┼────────┐
   ▼      ▼        ▼
 history retrieval tool state
   │      │        │
   └──────┼────────┘
          ▼
      Model context
          │
          ▼
       Inference
```

This distinction becomes essential in agentic architectures.

A durable memory system may use databases, object stores, vector stores, event logs, or specialized memory services. The model sees only the subset that the application places into its current context.

---

## 3.31 Structured Output

Many production applications need machine-consumable results rather than free-form prose.

Examples include:

- classification results,
- extraction results,
- workflow decisions,
- API arguments,
- structured plans,
- and tool invocations.

The architectural progression is:

```text
Free-form generation
        │
        ▼
Constrained / structured generation
        │
        ▼
Schema validation
        │
        ▼
Deterministic application logic
```

Structured output can reduce downstream parsing ambiguity, but schema validation remains important.

The model should not be the sole authority for enforcing business invariants.

---

## 3.32 Multimodal Models

Modern foundation models can process more than text. Depending on the model, inputs can include:

- images,
- audio,
- video,
- documents,
- and other modalities.

A simplified conceptual architecture is:

```text
Text ───────┐
Image ──────┼──► modality processing ──► shared model representation
Audio ──────┘                                  │
                                               ▼
                                          generation
```

The exact architecture varies significantly between model families.

For an architect, the important implications include:

- input size and tokenization may differ by modality,
- latency characteristics change,
- data governance becomes more complex,
- storage and transmission requirements increase,
- and evaluation must cover modality-specific failure modes.

Do not assume a text-only architecture can simply accept an image without changing its capacity and governance model.

---

## 3.33 Fine-Tuning vs Context vs Retrieval

These mechanisms solve different problems.

| Mechanism | Primary purpose | Changes model weights? | Runtime context required? |
|---|---|---:|---:|
| Prompting | Control behavior/instructions | No | Yes |
| Retrieval | Supply current/relevant knowledge | No | Yes |
| Fine-tuning | Adapt learned behavior/style/task performance | Yes | Not necessarily |

A useful decision principle is:

> **Use runtime context for information that should be selected or updated dynamically; use fine-tuning when the model's behavior itself needs adaptation.**

Do not use fine-tuning merely because you have a large document collection. That is usually a retrieval problem.

---

## 3.34 Inference Serving Architecture

A production self-hosted inference system is much more than model weights on a GPU.

A conceptual architecture is:

```text
Client
  │
  ▼
API / Gateway
  │
  ▼
Authentication / policy
  │
  ▼
Request queue / scheduler
  │
  ▼
Inference engine
  │
  ├── model weights
  ├── KV-cache management
  ├── batching
  └── accelerator execution
  │
  ▼
Streaming response
```

Production concerns include:

- authentication and authorization,
- rate limiting,
- quotas,
- routing,
- admission control,
- batching,
- cancellation,
- observability,
- model loading,
- health checks,
- autoscaling,
- graceful degradation,
- and capacity management.

The inference engine is therefore an architectural component, not an implementation footnote.

---

## 3.35 Hosted vs Self-Hosted Inference

### Hosted model API

Advantages:

- minimal infrastructure management,
- rapid model adoption,
- provider-managed accelerator capacity,
- simpler scaling.

Trade-offs:

- network dependency,
- provider pricing,
- provider availability,
- data-governance considerations,
- model/version dependency,
- less control over serving internals.

### Self-hosted model

Advantages:

- greater control,
- potentially better economics at sustained high utilization,
- deployment locality,
- customized serving configuration,
- stronger control over data movement.

Trade-offs:

- accelerator procurement or cloud GPU cost,
- model serving complexity,
- capacity planning,
- upgrades,
- patching,
- observability,
- and operational expertise.

The correct choice depends on workload volume, latency, compliance, model availability, engineering capability, and total cost of ownership.

---

## 3.36 Model Routing

A production system may use multiple models instead of sending every request to one model.

```text
                         ┌──► Small / fast model
Request ─► Router ───────┼──► General model
                         └──► High-quality model
```

Routing signals may include:

- task type,
- required quality,
- context size,
- latency objective,
- customer tier,
- data sensitivity,
- language,
- model availability,
- and cost budget.

### Avoid untestable routing logic

Routing rules should be:

- explicit,
- measurable,
- observable,
- versioned,
- and evaluated against representative workloads.

A router that grows into hundreds of undocumented special cases becomes another source of production risk.

---

## 3.37 Caching

LLM systems can benefit from multiple forms of caching.

Possible layers include:

- exact request/result caching,
- semantic caching,
- retrieval-result caching,
- prompt-prefix or provider-supported caching,
- and application state caching.

Caching can reduce latency and cost, but semantic caching introduces correctness considerations.

Before returning a cached model response, consider:

- whether the underlying data changed,
- whether authorization is identical,
- whether the user context is equivalent,
- whether the model version changed,
- and whether freshness requirements permit reuse.

Never let a cache bypass authorization boundaries.

---

## 3.38 Model Upgrades and Regression Evaluation

Changing a model is not equivalent to changing a stateless HTTP implementation behind an unchanged API.

A model upgrade can change:

- factual behavior,
- instruction following,
- formatting,
- tool selection,
- refusal behavior,
- latency,
- token usage,
- and cost.

Therefore:

```text
New model version
       │
       ▼
Offline evaluation
       │
       ▼
Representative workload tests
       │
       ▼
Canary / controlled rollout
       │
       ▼
Production monitoring
       │
       ▼
Full rollout
```

A production model should be treated as a versioned dependency with an evaluation and rollback strategy.

---

## 3.39 Capacity Planning

A useful capacity-planning model separates several dimensions.

### Model dimensions

- parameter count,
- active parameters,
- precision,
- architecture,
- context limit,
- and KV-cache characteristics.

### Workload dimensions

- requests per second,
- average input tokens,
- p95 input tokens,
- average output tokens,
- p95 output tokens,
- concurrency,
- burstiness,
- and streaming behavior.

### Service dimensions

- TTFT target,
- total latency target,
- availability target,
- GPU utilization target,
- and acceptable queueing.

### Capacity-planning principle

Do not ask:

> “How many GPUs does this model need?”

Ask:

> “How much accelerator capacity is required to serve this workload at the required quality, latency, concurrency, availability, and cost?”

That is the architect's question.

---

## 3.40 Common Architectural Mistakes

### Mistake 1 — Treating the LLM as a CPU-like function

**Problem:** The team ignores token generation, prefill, decode, queueing, and KV-cache behavior.

**Better:** Model inference as a specialized resource-intensive workload.

### Mistake 2 — Sizing GPUs from parameter count alone

**Problem:** Weights fit, but concurrency causes memory exhaustion or unacceptable latency.

**Better:** Include KV cache, context length, runtime overhead, batching, concurrency, and headroom.

### Mistake 3 — Sending unlimited context

**Problem:** Cost and latency increase while relevance may decrease.

**Better:** Retrieve, summarize, compress, and prioritize context.

### Mistake 4 — Ignoring tokenization

**Problem:** Cost and latency estimates are based on words or characters.

**Better:** Measure real token usage using the target model/tokenizer.

### Mistake 5 — Treating model upgrades as ordinary API upgrades

**Problem:** Behavior changes without regression testing.

**Better:** Version, evaluate, canary, monitor, and roll back models deliberately.

### Mistake 6 — Confusing token embeddings with retrieval embeddings

**Problem:** The team assumes any vector produced inside an LLM is directly suitable for semantic search.

**Better:** Select and evaluate application embedding models deliberately.

### Mistake 7 — Optimizing only tokens/second

**Problem:** Aggregate throughput improves but user-visible latency remains poor.

**Better:** Measure TTFT, queueing, prefill, decode rate, total latency, and end-to-end latency.

### Mistake 8 — Assuming reasoning eliminates verification

**Problem:** Model output is treated as proof.

**Better:** Use authoritative data and deterministic validation for important decisions.

### Mistake 9 — Treating context as durable memory

**Problem:** The application relies on conversation context as the system of record.

**Better:** Store durable state outside the model and assemble relevant context at inference time.

### Mistake 10 — Choosing the largest model by default

**Problem:** Cost and latency are unnecessarily high.

**Better:** Select the smallest model that meets the measured quality requirement.

---

## 3.41 Theory-Only Architecture Exercises

These exercises deliberately contain **no implementation code**. The objective is to verify conceptual understanding before we introduce model APIs and SDKs in later chapters.

### Exercise 1 — Explain an LLM to an Application Architect

Explain the complete path from a user entering a prompt to receiving a streamed response. Include tokenization, embeddings, Transformer processing, logits, decoding, prefill, decode, and stopping conditions.

### Exercise 2 — Context Cost Analysis

A support application sends the complete conversation history plus retrieved documents on every request. Identify the architectural risks and propose a context-management strategy.

### Exercise 3 — GPU Capacity Thinking

You are evaluating a 16-billion-parameter model for an internal coding assistant. Estimate the model-weight memory at 16-bit precision, then list all additional memory and workload dimensions that must be considered before selecting accelerators.

### Exercise 4 — Model Routing

Design a routing policy for:

- a small low-cost model,
- a general-purpose model,
- and a high-quality reasoning model.

Define measurable routing criteria and explain how you would prevent the router from becoming an untestable collection of special cases.

### Exercise 5 — Architecture Review

Review an architecture where every request is sent to the largest available model with the entire conversation history and every retrieved document.

Identify at least ten issues involving latency, cost, relevance, authorization, capacity, and reliability. Propose a revised architecture.

### Exercise 6 — Hosted vs Self-Hosted

For an enterprise workload, create a decision matrix comparing hosted inference and self-hosted inference across cost, latency, privacy, availability, operational complexity, scalability, and model choice.

### Exercise 7 — Model Upgrade

A new model is 20% cheaper and appears better on public benchmarks. Define an evaluation plan that determines whether it should replace the production model.

---

## 3.42 Key Architectural Principles

1. **An LLM is an autoregressive probabilistic computation, not a database.**
2. **Tokens are a fundamental unit of context, generation, cost, and inference work.**
3. **Transformers combine attention, nonlinear transformations, residual paths, and normalization to transform token representations.**
4. **Decoder-only LLMs generate output incrementally.**
5. **Prefill and decode have different performance characteristics and should be measured separately.**
6. **KV cache improves decoding efficiency but creates a major memory dimension.**
7. **GPU capacity planning must include weights, KV cache, runtime overhead, concurrency, and headroom.**
8. **Quantization can materially improve inference economics, but quality must be validated empirically.**
9. **Total parameters, active parameters, memory footprint, and compute cost are different concepts.**
10. **A larger context window is not automatically a better context strategy.**
11. **Model upgrades are production dependency changes and require regression evaluation.**
12. **The inference engine is part of the architecture; model weights alone are not a serving system.**
13. **Streaming changes perceived latency but does not eliminate computation.**
14. **Model routing can optimize quality, latency, cost, and governance when it is based on measurable policies.**
15. **Durable application state should remain outside the model context.**
16. **Deterministic software and authoritative systems should enforce business invariants around probabilistic models.**
17. **Model selection is a multi-objective optimization problem, not a parameter-count competition.**

---

## Chapter Summary

A modern language model converts token sequences into probability distributions over possible next tokens. Decoder-style LLMs use Transformer blocks to repeatedly transform token representations through attention and nonlinear layers, then decode one token at a time.

For an AI architect, the most important internal concepts are the ones that create system-level consequences. Tokenization affects cost and context. Context length affects prefill work and memory. Autoregressive decoding creates a streaming workload. KV caching improves decode efficiency while consuming memory. Model weights are only one part of the inference footprint. Quantization changes the memory/economics trade-off. Batching affects accelerator utilization and latency. Model architecture affects capacity planning.

These mechanisms allow an architect to reason about model selection, inference architecture, self-hosting, latency optimization, capacity planning, model routing, and production reliability without becoming a machine-learning researcher.

> **You do not need to build the Transformer to architect the system around it—but you should understand the constraints the Transformer creates.**

---

## Interview Questions

1. What is an LLM doing during inference?
2. Why are tokens important to an AI architect?
3. What is the role of the token embedding layer?
4. Why does a Transformer need positional information?
5. Explain self-attention using Q, K, and V.
6. Why does a decoder-only model require causal attention?
7. What is multi-head attention?
8. What are MHA, MQA, and GQA, and why do they matter for inference?
9. What does the feed-forward network do inside a Transformer block?
10. What are residual connections and normalization used for?
11. What is the difference between training and inference?
12. Why does sending a document to a model not normally change its weights?
13. What are logits and how are they related to decoding?
14. What is temperature? What are top-k and top-p?
15. What is the difference between encoder-only, decoder-only, and encoder-decoder models?
16. What is a context window?
17. Why is more context not necessarily better context?
18. What are prefill and decode phases?
19. What is a KV cache and why does it matter for self-hosted inference?
20. Why is model parameter count insufficient for GPU capacity planning?
21. What is quantization and what trade-off does it introduce?
22. What is the difference between total parameters and active parameters in an MoE model?
23. What is continuous batching?
24. What is TTFT and why is it important?
25. Why can streaming improve perceived latency without reducing total generation time?
26. What additional memory should be considered beyond model weights?
27. Why should application memory not be confused with model context?
28. When should you consider fine-tuning instead of retrieval or prompting?
29. How would you design a model-routing strategy for multiple models?
30. Why should model upgrades be regression-tested even when the API contract remains unchanged?
31. What factors determine hosted versus self-hosted inference?
32. Why should deterministic business logic remain outside the LLM?

---

## Chapter Boundary: Where Coding Begins

This chapter intentionally contains **no Java or Python implementation examples**.

That is deliberate. At this stage, implementation would mostly demonstrate abstractions without teaching the architecture. The handbook should first establish the mental model of tokens, Transformers, inference, context, decoding, memory, latency, and model serving.

Once we reach chapters covering **actual model communication**, coding becomes valuable because we can demonstrate:

- model API invocation,
- request/response contracts,
- streaming,
- structured output,
- embeddings APIs,
- RAG pipelines,
- tool calling,
- agent orchestration,
- retries and timeouts,
- observability,
- evaluation,
- and production integration patterns.

That separation keeps the early chapters focused on architecture rather than SDK syntax.
