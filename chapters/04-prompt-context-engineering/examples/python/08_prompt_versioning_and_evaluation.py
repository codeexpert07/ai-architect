"""Chapter 4.24-4.26: version prompts and run behavioral regression tests."""

from dataclasses import dataclass


@dataclass(frozen=True)
class PromptVersion:
    name: str
    version: str


CASES = [
    ("charged twice for one invoice", "BILLING"),
    ("cannot reset password", "ACCOUNT"),
    ("checkout returns 503", "TECHNICAL"),
]


def classify_with_policy(text: str, prompt: PromptVersion) -> str:
    # Deterministic stand-in for an LLM so the test harness is runnable without
    # a provider. Replace this function with the model gateway in production.
    text = text.lower()
    if "invoice" in text or "charged" in text:
        return "BILLING"
    if "password" in text:
        return "ACCOUNT"
    if "503" in text:
        return "TECHNICAL"
    return "OTHER"


def evaluate(prompt: PromptVersion) -> dict[str, float]:
    correct = sum(classify_with_policy(text, prompt) == expected for text, expected in CASES)
    return {"accuracy": correct / len(CASES)}


if __name__ == "__main__":
    v3 = PromptVersion("ticket-classifier", "3.4")
    print(v3, evaluate(v3))
