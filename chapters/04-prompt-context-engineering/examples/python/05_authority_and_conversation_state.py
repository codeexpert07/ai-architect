"""Chapter 4.13-4.17: authority, conversation state, compaction and ranking."""

from dataclasses import dataclass


@dataclass
class ConversationState:
    durable_facts: dict[str, str]
    task_state: dict[str, str]
    recent_turns: list[str]
    summary: str = ""

    def compact(self, keep_turns: int = 3) -> None:
        if len(self.recent_turns) > keep_turns:
            old = self.recent_turns[:-keep_turns]
            self.summary = (self.summary + " " + " ".join(old)).strip()
            self.recent_turns = self.recent_turns[-keep_turns:]


@dataclass(frozen=True)
class Evidence:
    source: str
    authority: int
    freshness: float
    relevance: float
    tokens: int
    text: str


def rank_evidence(items: list[Evidence], max_tokens: int) -> list[Evidence]:
    ranked = sorted(
        items,
        key=lambda x: (x.authority * x.freshness * x.relevance) / max(x.tokens, 1),
        reverse=True,
    )
    chosen: list[Evidence] = []
    used = 0
    for item in ranked:
        if used + item.tokens <= max_tokens:
            chosen.append(item)
            used += item.tokens
    return chosen


if __name__ == "__main__":
    state = ConversationState(
        durable_facts={"plan": "Enterprise"},
        task_state={"workflow": "ORDER_RETURN"},
        recent_turns=["start", "verify order", "damage reported", "pickup requested"],
    )
    state.compact()
    print(state)

    evidence = [
        Evidence("transaction", 10, 1.0, 0.95, 10, "Current order status"),
        Evidence("old-summary", 4, 0.8, 0.9, 15, "Earlier conversation"),
    ]
    print(rank_evidence(evidence, max_tokens=20))
