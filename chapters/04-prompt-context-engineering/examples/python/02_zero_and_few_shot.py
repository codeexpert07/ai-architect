"""Chapter 4.6-4.7: zero-shot/few-shot prompt -> real LLM classification."""

import os
from openai import OpenAI

EXAMPLES = [
    ("I cannot log in after changing my password.", "ACCOUNT"),
    ("The invoice shows two identical charges.", "BILLING"),
    ("The API returns HTTP 503 during checkout.", "TECHNICAL"),
]


def select_examples(ticket: str, limit: int = 2) -> list[tuple[str, str]]:
    keywords = set(ticket.lower().split())
    return sorted(
        EXAMPLES,
        key=lambda item: len(keywords & set(item[0].lower().split())),
        reverse=True,
    )[:limit]


def zero_shot_prompt(ticket: str) -> str:
    return "Classify as BILLING, ACCOUNT, TECHNICAL, or OTHER. Return only the category.\n\nTicket:\n" + ticket


def few_shot_prompt(ticket: str) -> str:
    examples = "\n\n".join(f"Input: {x}\nOutput: {y}" for x, y in select_examples(ticket))
    return f"Classify the ticket.\n\n{examples}\n\nInput: {ticket}\nOutput:"


def call_model(prompt: str) -> str:
    response = OpenAI().responses.create(
        model=os.getenv("OPENAI_MODEL", "gpt-5.5"),
        instructions="Follow the classification task exactly and return only the requested category.",
        input=prompt,
    )
    return response.output_text.strip()


def main() -> None:
    ticket = "The API fails with HTTP 503 during checkout."
    print("Zero-shot:", call_model(zero_shot_prompt(ticket)))
    print("Few-shot:", call_model(few_shot_prompt(ticket)))


if __name__ == "__main__":
    main()
