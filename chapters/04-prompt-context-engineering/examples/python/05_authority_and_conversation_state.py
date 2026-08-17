"""Chapter 4.13-4.17: state/authority/ranking -> real LLM."""

import os
from dataclasses import dataclass
from openai import OpenAI

@dataclass
class ConversationState:
    durable_facts: dict[str, str]
    task_state: dict[str, str]
    recent_turns: list[str]
    summary: str = ""
    def compact(self, keep_turns: int = 3) -> None:
        if len(self.recent_turns) > keep_turns:
            self.summary = (self.summary + " " + " ".join(self.recent_turns[:-keep_turns])).strip()
            self.recent_turns = self.recent_turns[-keep_turns:]

@dataclass(frozen=True)
class Evidence:
    source: str; authority: int; freshness: float; relevance: float; tokens: int; text: str

def rank_evidence(items: list[Evidence], max_tokens: int) -> list[Evidence]:
    chosen=[]; used=0
    for item in sorted(items, key=lambda x: (x.authority*x.freshness*x.relevance)/max(x.tokens,1), reverse=True):
        if used + item.tokens <= max_tokens: chosen.append(item); used += item.tokens
    return chosen

def main() -> None:
    state = ConversationState({"plan":"Enterprise"}, {"workflow":"ORDER_RETURN"}, ["start", "verify order", "damage reported", "pickup requested"])
    state.compact()
    evidence = rank_evidence([
        Evidence("transaction",10,1,.95,10,"Current order status: pickup requested"),
        Evidence("old-summary",4,.8,.9,15,"Earlier conversation"),
    ], 20)
    context = f"DURABLE STATE: {state.durable_facts}\nTASK STATE: {state.task_state}\nSUMMARY: {state.summary}\nRECENT: {state.recent_turns}\nEVIDENCE: {[e.text for e in evidence]}"
    response = OpenAI().responses.create(model=os.getenv("OPENAI_MODEL","gpt-5.5"), instructions="Use authoritative state/evidence and answer the user's next request.", input=context + "\n\nUSER: When will my pickup happen?")
    print(response.output_text)

if __name__ == "__main__":
    main()
