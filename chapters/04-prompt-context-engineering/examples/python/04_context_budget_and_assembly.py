"""Chapter 4.11-4.12: token budgeting and explicit context assembly."""

from dataclasses import dataclass


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
    selected: list[ContextItem] = []
    # Highest-value evidence first; the scoring policy is intentionally simple.
    ranked = sorted(items, key=lambda x: (x.authority * x.relevance) / max(x.tokens, 1), reverse=True)
    for item in ranked:
        if item.tokens <= remaining:
            selected.append(item)
            remaining -= item.tokens
    return selected


def assemble(system_policy: str, user_request: str, items: list[ContextItem], budget: ContextBudget) -> str:
    chosen = select_context(items, budget)
    evidence = "\n\n".join(f"[{x.source}] {x.text}" for x in chosen)
    return f"""SYSTEM POLICY\n{system_policy}\n\nEVIDENCE\n{evidence}\n\nUSER REQUEST\n{user_request}"""


if __name__ == "__main__":
    items = [
        ContextItem("billing-db", "Current balance: 1200", 10, 0.95, 8),
        ContextItem("old-chat", "Customer discussed billing last year", 3, 0.80, 20),
        ContextItem("policy", "Refunds are allowed within 30 days", 9, 0.90, 12),
    ]
    budget = ContextBudget(capacity=100, output_reserve=20, policy_tokens=10)
    print(assemble("Use authoritative evidence only.", "Can I get a refund?", items, budget))
