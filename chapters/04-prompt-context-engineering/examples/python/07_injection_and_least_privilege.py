"""Chapter 4.20-4.23: prompt-injection defense and least privilege.

This is an architecture example, not a complete security product. The key
point is that authorization and tool policy are deterministic controls outside
the model.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class User:
    user_id: str
    permissions: frozenset[str]


def authorize(user: User, permission: str) -> None:
    if permission not in user.permissions:
        raise PermissionError(f"missing permission: {permission}")


def is_suspicious_instruction(text: str) -> bool:
    indicators = (
        "ignore previous instructions",
        "reveal system prompt",
        "send secrets",
        "disable security",
    )
    lowered = text.lower()
    return any(indicator in lowered for indicator in indicators)


def prepare_external_content(user: User, document: str) -> str:
    authorize(user, "document.read")
    if is_suspicious_instruction(document):
        raise ValueError("external content requires security review")
    return f"<untrusted_document>\n{document}\n</untrusted_document>"


def execute_sensitive_tool(user: User, tool: str) -> None:
    authorize(user, f"tool:{tool}")
    print(f"authorized tool execution: {tool}")


if __name__ == "__main__":
    user = User("u-1", frozenset({"document.read", "tool:ticket.lookup"}))
    print(prepare_external_content(user, "Refund policy: 30 days."))
    execute_sensitive_tool(user, "ticket.lookup")
