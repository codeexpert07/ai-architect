"""Chapter 4.34-4.36: degraded context -> LLM -> privacy-aware telemetry."""

import os
import time
from dataclasses import dataclass
from enum import Enum

from openai import OpenAI
from pydantic import BaseModel, ValidationError


class ContextStatus(Enum):
    COMPLETE = "complete"
    DEGRADED = "degraded"
    UNAVAILABLE = "unavailable"


@dataclass(frozen=True)
class ContextResult:
    status: ContextStatus
    evidence: list[str]
    reason: str | None = None


class SupportDecision(BaseModel):
    answer: str
    should_escalate: bool


def handle_retrieval_failure(error: Exception, safe_fallback: str) -> ContextResult:
    if safe_fallback:
        return ContextResult(ContextStatus.DEGRADED, [safe_fallback], str(error))
    return ContextResult(ContextStatus.UNAVAILABLE, [], str(error))


def telemetry(
    prompt_version: str,
    sources: list[str],
    input_tokens: int,
    output_tokens: int,
    latency_ms: int,
    schema_valid: bool,
) -> dict[str, object]:
    return {
        "prompt_version": prompt_version,
        "context_sources": sources,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "latency_ms": latency_ms,
        "schema_valid": schema_valid,
    }


def main() -> None:
    started = time.perf_counter()
    try:
        raise TimeoutError("retrieval timeout")
    except TimeoutError as exc:
        context = handle_retrieval_failure(exc, "Use approved policy only.")

    response = OpenAI().responses.create(
        model=os.getenv("OPENAI_MODEL", "gpt-5.5"),
        instructions=(
            "If context is degraded, clearly state limitations and never invent "
            "missing evidence. Return JSON with answer and should_escalate."
        ),
        input=(
            f"STATUS={context.status.value}\nEVIDENCE={context.evidence}\n"
            "USER: Can I get a refund?"
        ),
    )

    usage = response.usage
    schema_valid = False
    try:
        # This example intentionally validates the model output after the call;
        # the telemetry records the actual result rather than assuming success.
        decision = SupportDecision.model_validate_json(response.output_text)
        schema_valid = True
        print(decision.model_dump_json(indent=2))
    except ValidationError as exc:
        print("Output validation failed:", exc)
        print(response.output_text)

    print(
        telemetry(
            "support/v3.4",
            ["fallback:policy"],
            usage.input_tokens if usage else 0,
            usage.output_tokens if usage else 0,
            int((time.perf_counter() - started) * 1000),
            schema_valid,
        )
    )


if __name__ == "__main__":
    main()
