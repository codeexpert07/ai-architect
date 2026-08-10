from dataclasses import dataclass


@dataclass(frozen=True)
class GenerationRequest:
    system_instruction: str
    user_input: str
    model: str
    temperature: float = 0.2
    max_output_tokens: int = 500


@dataclass(frozen=True)
class GenerationResponse:
    text: str
    model: str
    input_tokens: int
    output_tokens: int


class AiTextGenerator:
    def generate(self, request: GenerationRequest) -> GenerationResponse:
        raise NotImplementedError


class CustomerSupportService:
    def __init__(self, generator: AiTextGenerator) -> None:
        self._generator = generator

    def draft_reply(self, customer_message: str) -> str:
        request = GenerationRequest(
            system_instruction="Answer using only approved support guidance.",
            user_input=customer_message,
            model="configured-by-platform",
        )
        return self._generator.generate(request).text
