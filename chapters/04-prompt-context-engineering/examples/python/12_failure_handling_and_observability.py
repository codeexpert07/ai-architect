"""Chapter 4.34-4.36: explicit degradation and privacy-aware observability."""

from dataclasses import dataclass
from enum import Enum


class ContextStatus(Enum):
    COMPLETE = "complete"
    DEGRADED = "degraded"
    UNAVAILABLE = "unavailable"


@dataclass(frozen=True)
class ContextResult:
    status: ContextStatus
    evidence: list[str]
    reason: str | None = None


def handle_retrieval_failure(error: Exception, safe_fallback: str) -> ContextResult:
    # Do not silently pretend that missing evidence was retrieved.
    if safe_fallback:
        return ContextResult(ContextStatus.DEGRADED, [safe_fallback], str(error))
    return ContextResult(ContextStatus.UNAVAILABLE, [], str(error))


def telemetry(prompt_version: str, sources: list[str], input_tokens: int, output_tokens: int,
              latency_ms: int, schema_valid: bool) -> dict[str, object]:
    # Log identifiers and metrics, not the customer's raw prompt/response.
    return {
        "prompt_version": prompt_version,
        "context_sources": sources,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "latency_ms": latency_ms,
        "schema_valid": schema_valid,
    }


if __name__ == "__main__":
    print(handle_retrieval_failure(TimeoutError("retrieval timeout"), "Use approved policy only."))
    print(telemetry("support/v3.4", ["kb:123", "policy:42"], 1850, 260, 1240, True))
