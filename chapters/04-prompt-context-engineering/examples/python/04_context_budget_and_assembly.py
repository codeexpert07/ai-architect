"""Chapter 4.11-4.12: budget/select/assemble context -> real LLM."""

import os
from dataclasses import dataclass
from openai import OpenAI

@dataclass(frozen=True)
class ContextItem:
    source: str
    text: str
    authority: int
    relevance: float
    tokens: int

@dataclass(frozen=True)
class ContextBudget:
    capacity: int
    output_reserve: int
    policy_tokens: int
    @property
    def available_for_dynamic_context(self) -> int:
        return self.capacity - self.output_reserve - self.policy_tokens

def select_context(items: list[ContextItem], budget: ContextBudget) -> list[ContextItem]:
    remaining = budget.available_for_dynamic_context
    selected = []
    for item in sorted(items, key=lambda x: (x.authority * x.relevance) / max(x.tokens, 1), reverse=True):
        if item.tokens <= remaining:
            selected.append(item); remaining -= item.tokens
    return selected

def assemble(policy: str, request: str, items: list[ContextItem], budget: ContextBudget) -> str:
    evidence = "\n\n".join(f"[{x.source}] {x.text}" for x in select_context(items, budget))
    return f"POLICY\n{policy}\n\nEVIDENCE\n{evidence}\n\nREQUEST\n{request}"

def main() -> None:
    items = [
        ContextItem("billing-db", "Current balance: 1200", 10, .95, 8),
        ContextItem("old-chat", "Customer discussed billing last year", 3, .80, 20),
        ContextItem("policy", "Refunds are allowed within 30 days", 9, .90, 12),
    ]
    prompt = assemble("Use authoritative evidence only.", "Can I get a refund?", items, ContextBudget(100, 20, 10))
    response = OpenAI().responses.create(
        model=os.getenv("OPENAI_MODEL", "gpt-5.5"),
        instructions="Answer only from the bounded evidence. If insufficient, say so.",
        input=prompt,
    )
    print(response.output_text)

if __name__ == "__main__":
    main()
