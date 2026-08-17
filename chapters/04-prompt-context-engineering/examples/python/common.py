"""Reusable architecture data classes for the Chapter 4 examples."""

from dataclasses import dataclass


@dataclass(frozen=True)
class PromptContract:
    """Provider-neutral representation of an application's model input contract."""

    role: str
    task: str
    constraints: tuple[str, ...]
    context: str
    user_request: str
    output_contract: str
    failure_behavior: str

    def render(self) -> str:
        return (
            f"ROLE\n{self.role}\n\n"
            f"TASK\n{self.task}\n\n"
            "CONSTRAINTS\n- "
            + "\n- ".join(self.constraints)
            + f"\n\nCONTEXT\n<context>\n{self.context}\n</context>\n\n"
            f"USER REQUEST\n<user_request>\n{self.user_request}\n</user_request>\n\n"
            f"OUTPUT CONTRACT\n{self.output_contract}\n\n"
            f"FAILURE BEHAVIOR\n{self.failure_behavior}\n"
        )


@dataclass(frozen=True)
class SupportContext:
    """Authoritative application state projected into model context."""

    plan: str
    renewal_date: str
    early_renewal_allowed: bool

    def render(self) -> str:
        return (
            f"Plan: {self.plan}\n"
            f"Renewal date: {self.renewal_date}\n"
            f"Early renewal allowed: {self.early_renewal_allowed}"
        )
