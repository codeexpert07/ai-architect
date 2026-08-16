"""Chapter 4.29-4.31: stable prompt prefixes, portability and templates."""

from dataclasses import dataclass


@dataclass(frozen=True)
class PromptTemplate:
    policy_version: str
    task: str
    output_contract: str

    def render(self, context: str, user_input: str) -> str:
        # Keep policy/task stable; inject runtime data only into explicit slots.
        return f"""POLICY VERSION: {self.policy_version}
TASK: {self.task}

CONTEXT
<context>{context}</context>

USER INPUT
<user_input>{user_input}</user_input>

OUTPUT CONTRACT
{self.output_contract}"""


@dataclass(frozen=True)
class ModelCapabilities:
    name: str
    supports_structured_output: bool
    max_context_tokens: int


def select_model(candidates: list[ModelCapabilities], required_context: int) -> ModelCapabilities:
    eligible = [m for m in candidates if m.max_context_tokens >= required_context]
    if not eligible:
        raise RuntimeError("no compatible model")
    return eligible[0]


if __name__ == "__main__":
    template = PromptTemplate("support/v3.4", "Answer the support question.", "JSON: answer, source")
    print(template.render("Plan=Enterprise", "What is my renewal date?"))
    print(select_model([
        ModelCapabilities("model-a", True, 16_000),
        ModelCapabilities("model-b", True, 128_000),
    ], required_context=20_000))
