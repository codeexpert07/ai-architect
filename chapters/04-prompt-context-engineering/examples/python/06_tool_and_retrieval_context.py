"""Chapter 4.18-4.19: treat tool output and retrieved evidence as context.

The model should receive the smallest authorized representation, not a raw API
response or database dump.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class ToolResult:
    fields: dict[str, object]
    authorized_fields: set[str]
    max_items: int = 20


def sanitize_tool_result(result: ToolResult) -> dict[str, object]:
    return {
        key: value
        for key, value in result.fields.items()
        if key in result.authorized_fields
    }


def normalize_search_results(results: list[dict[str, object]], limit: int = 3) -> list[dict[str, object]]:
    # Keep only fields useful to the model. Real systems should also apply
    # tenant authorization, provenance checks, freshness rules and deduplication.
    normalized = []
    for result in results[:limit]:
        normalized.append({
            "title": result.get("title"),
            "source": result.get("source"),
            "snippet": result.get("snippet"),
        })
    return normalized


if __name__ == "__main__":
    raw = ToolResult(
        fields={"order_id": "A-100", "status": "SHIPPED", "access_token": "secret"},
        authorized_fields={"order_id", "status"},
    )
    print(sanitize_tool_result(raw))
