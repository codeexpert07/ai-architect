"""Chapter 4.24-4.26: versioned prompt -> LLM -> regression evaluation."""

import os
from dataclasses import dataclass

from openai import OpenAI


@dataclass(frozen=True)
class PromptVersion:
    name: str
    version: str


CASES = [
    ("charged twice for one invoice", "BILLING"),
    ("cannot reset password", "ACCOUNT"),
    ("checkout returns 503", "TECHNICAL"),
]


def classify(text: str, prompt: PromptVersion) -> str:
    response = OpenAI().responses.create(
        model=os.getenv("OPENAI_MODEL", "gpt-5.5"),
        instructions=(
            f"You are {prompt.name} version {prompt.version}. "
            "Classify as BILLING, ACCOUNT, TECHNICAL, or OTHER. Return only the category."
        ),
        input=text,
    )
    return response.output_text.strip().upper()


def evaluate(prompt: PromptVersion) -> dict[str, object]:
    results = [classify(text, prompt) for text, _ in CASES]
    correct = sum(actual == expected for actual, (_, expected) in zip(results, CASES))
    return {"accuracy": correct / len(CASES), "results": results}


def compare(baseline: dict[str, object], candidate: dict[str, object]) -> dict[str, object]:
    baseline_accuracy = float(baseline["accuracy"])
    candidate_accuracy = float(candidate["accuracy"])
    return {
        "baseline_accuracy": baseline_accuracy,
        "candidate_accuracy": candidate_accuracy,
        "delta": candidate_accuracy - baseline_accuracy,
        "regression": candidate_accuracy < baseline_accuracy,
    }


def main() -> None:
    baseline = evaluate(PromptVersion("ticket-classifier", "3.3"))
    candidate = evaluate(PromptVersion("ticket-classifier", "3.4"))
    comparison = compare(baseline, candidate)
    print("Baseline:", baseline)
    print("Candidate:", candidate)
    print("Regression report:", comparison)
    if comparison["regression"]:
        raise SystemExit("Prompt regression detected")


if __name__ == "__main__":
    main()
