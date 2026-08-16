"""Chapter 4.27-4.28: deterministic controls and cost/latency accounting."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Usage:
    input_tokens: int
    output_tokens: int
    input_price_per_million: float
    output_price_per_million: float
    latency_ms: int
    retries: int = 0

    @property
    def cost(self) -> float:
        return (
            self.input_tokens * self.input_price_per_million
            + self.output_tokens * self.output_price_per_million
        ) / 1_000_000

    @property
    def effective_latency_ms(self) -> int:
        return self.latency_ms * (self.retries + 1)


def enforce_business_rule(decision: str, refund_days: int) -> str:
    # The model may propose a decision; deterministic code owns the invariant.
    if decision == "REFUND" and refund_days > 30:
        return "ESCALATE"
    return decision


if __name__ == "__main__":
    usage = Usage(2_000, 300, 2.0, 8.0, 900, retries=1)
    print(f"cost=${usage.cost:.6f}, effective_latency={usage.effective_latency_ms}ms")
    print(enforce_business_rule("REFUND", refund_days=45))
