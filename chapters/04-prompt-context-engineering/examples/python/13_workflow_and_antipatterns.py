"""Chapter 4.37-4.40: replace anti-patterns with an explicit workflow.

The workflow separates authorization, context acquisition, prompt compilation,
and output validation from the model itself.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Request:
    user_id: str
    text: str


def design_workflow(request: Request) -> list[str]:
    return [
        "define task and success criteria",
        "identify authoritative sources",
        "identify untrusted inputs",
        "authorize retrieval/tools",
        "select minimal context",
        "compile versioned prompt",
        "invoke model",
        "validate output and business rules",
        "record privacy-aware telemetry",
    ]


def anti_pattern_replacements() -> dict[str, str]:
    return {
        "entire conversation forever": "recent turns + structured state + summary",
        "all retrieved documents": "rank + filter + deduplicate + budget",
        "model enforces authorization": "deterministic authorization before retrieval/tool use",
        "valid JSON means correct": "schema + semantic + authorization validation",
        "prompt quality by intuition": "representative evaluation + production metrics",
        "log every prompt": "redacted, privacy-aware telemetry",
    }


if __name__ == "__main__":
    print(design_workflow(Request("u-1", "Where is my order?")))
    for bad, better in anti_pattern_replacements().items():
        print(f"{bad} -> {better}")
