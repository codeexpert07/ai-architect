# Chapter 4 References

This chapter treats prompting and context as production engineering concerns. Prefer primary research for foundational concepts and current provider documentation for model-specific capabilities, limits, structured outputs, caching, tool use, and safety behavior.

## Foundational Research

1. Brown et al., **Language Models are Few-Shot Learners** — foundational work on few-shot and in-context learning.
   - https://arxiv.org/abs/2005.14165
2. Wei et al., **Chain-of-Thought Prompting Elicits Reasoning in Large Language Models** — important research on reasoning-oriented prompting.
   - https://arxiv.org/abs/2201.11903
3. Kojima et al., **Large Language Models are Zero-Shot Reasoners** — influential work on zero-shot reasoning prompts.
   - https://arxiv.org/abs/2205.11916
4. Yao et al., **ReAct: Synergizing Reasoning and Acting in Language Models** — connects model reasoning with external actions and tool use.
   - https://arxiv.org/abs/2210.03629
5. Liu et al., **Lost in the Middle: How Language Models Use Long Contexts** — important evidence for long-context information placement and retrieval concerns.
   - https://arxiv.org/abs/2307.03172
6. Zhou et al., **Least-to-Most Prompting Enables Complex Reasoning in Large Language Models** — useful research on decomposing complex tasks.
   - https://arxiv.org/abs/2205.10625
7. Gao et al., **Retrieval-Augmented Generation for Large Language Models: A Survey** — broad background for retrieval as context engineering.
   - https://arxiv.org/abs/2312.10997

## Current Model and Prompt Documentation

Provider capabilities change frequently. Consult the documentation for the exact model and API version used in production.

- OpenAI Platform documentation: https://platform.openai.com/docs/
- OpenAI prompting guidance: https://platform.openai.com/docs/guides/prompt-engineering
- Anthropic prompt engineering overview: https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/overview
- Google Gemini API documentation: https://ai.google.dev/gemini-api/docs
- Hugging Face Transformers documentation: https://huggingface.co/docs/transformers/

## Security

- OWASP Top 10 for LLM Applications: https://owasp.org/www-project-top-10-for-large-language-model-applications/
- OWASP GenAI Security Project: https://genai.owasp.org/
- NIST AI Risk Management Framework: https://www.nist.gov/itl/ai-risk-management-framework
- NIST Generative AI Profile: https://www.nist.gov/itl/ai-risk-management-framework/ai-rmf-generative-artificial-intelligence-profile

## Evaluation and Production Engineering

- OpenAI Evals: https://github.com/openai/evals
- MLflow GenAI documentation: https://mlflow.org/docs/latest/genai/
- Arize Phoenix documentation: https://phoenix.arize.com/
- LangSmith documentation: https://docs.smith.langchain.com/

## How to Use These References

Use research papers to understand the underlying idea and its limitations. Use current provider documentation to verify what a specific model actually supports. In production, treat model behavior, prompt templates, structured-output guarantees, token limits, caching semantics, and safety controls as versioned dependencies rather than permanent assumptions.
