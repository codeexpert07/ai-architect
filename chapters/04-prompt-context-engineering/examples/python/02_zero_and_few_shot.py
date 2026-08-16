"""Chapter 4.6-4.7: zero-shot and few-shot prompting.

Examples are data selected for the current task; they are not application
policy. A real system can replace select_examples() with semantic retrieval.
"""

EXAMPLES = [
    ("I cannot log in after changing my password.", "ACCOUNT"),
    ("The invoice shows two identical charges.", "BILLING"),
    ("The API returns HTTP 503 during checkout.", "TECHNICAL"),
]


def zero_shot_prompt(ticket: str) -> str:
    return (
        "Classify the ticket as BILLING, ACCOUNT, TECHNICAL, or OTHER. "
        "Return only the category.\n\nTicket:\n" + ticket
    )


def select_examples(ticket: str, limit: int = 2) -> list[tuple[str, str]]:
    # Tiny deterministic stand-in for a real similarity selector.
    keywords = set(ticket.lower().split())
    scored = sorted(
        EXAMPLES,
        key=lambda item: len(keywords & set(item[0].lower().split())),
        reverse=True,
    )
    return scored[:limit]


def few_shot_prompt(ticket: str) -> str:
    demonstrations = "\n\n".join(
        f"Input: {example}\nOutput: {label}"
        for example, label in select_examples(ticket)
    )
    return f"""Classify the ticket.

{demonstrations}

Input: {ticket}
Output:"""


if __name__ == "__main__":
    print(zero_shot_prompt("The customer was charged twice."))
    print("---")
    print(few_shot_prompt("The API fails with HTTP 503."))
