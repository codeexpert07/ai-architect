# Contributing to the AI Architect Handbook

This repository is developed as a chapter-oriented, production-focused self-study handbook. Each chapter should be independently understandable and independently maintainable.

## Chapter Directory Convention

Every chapter should use its own directory under `chapters/`:

```text
chapters/
└── NN-chapter-name/
    ├── README.md
    ├── java/
    ├── python/
    ├── diagrams/
    └── exercises/
```

### Directory responsibilities

- `README.md` — chapter content, learning objectives, explanations, examples, best practices, pitfalls, summary, and references.
- `java/` — Java implementations and runnable examples specific to the chapter.
- `python/` — Python implementations and runnable examples specific to the chapter.
- `diagrams/` — reusable or detailed architecture diagrams and their source assets.
- `exercises/` — hands-on exercises, labs, datasets, and solution material where appropriate.

Directories may be omitted until they contain an actual artifact; Git does not track empty directories.

## Chapter Naming

Use a zero-padded chapter number and a concise kebab-case name, for example:

```text
01-ai-architect-mindset
02-generative-ai-fundamentals
03-llm-internals
```

## Chapter Content Standards

Each chapter should normally contain:

1. Prerequisites
2. Learning objectives
3. Conceptual explanation
4. Architecture diagrams where useful
5. Practical examples
6. Production considerations
7. Security and reliability considerations where relevant
8. Common pitfalls
9. Exercises
10. Chapter summary
11. Further reading / references
12. Interview questions when appropriate

Not every chapter needs identical section numbering, but the reader should be able to discover the learning objectives and references easily.

## Diagram Convention

Use **ASCII diagrams for small, inline conceptual diagrams** when they improve readability and render naturally in Markdown and Git diffs.

Use the chapter's `diagrams/` directory for **larger, reusable, or presentation-quality diagrams**. Mermaid is the preferred source format for diagrams that benefit from structured editing; generated SVG/PNG assets may be added when they provide a meaningful rendering benefit.

The source diagram should remain the source of truth. Do not maintain duplicate ASCII and rendered versions of the same detailed diagram unless the duplication is intentional and documented.

## Code Examples

Code should be runnable or close to runnable whenever practical. Examples should favor clarity and architectural relevance over unnecessary framework complexity.

Java and Python examples should remain inside the chapter that teaches the concept unless they are genuinely shared infrastructure.

## Pull Requests

A chapter PR should explain:

- What chapter or chapter section was added or changed.
- Why the change is useful to the reader.
- Any new code, diagrams, exercises, or references.
- Validation performed.

Keep commits focused. Prefer one logical commit for a chapter contribution when practical.
