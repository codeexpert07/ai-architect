"""Chapter 4.24-4.26: versioned prompt -> LLM -> regression evaluation."""

import os
from dataclasses import dataclass
from openai import OpenAI

@dataclass(frozen=True)
class PromptVersion:
    name: str
    version: str

CASES=[("charged twice for one invoice","BILLING"),("cannot reset password","ACCOUNT"),("checkout returns 503","TECHNICAL")]

def classify(text: str, prompt: PromptVersion) -> str:
    response=OpenAI().responses.create(model=os.getenv("OPENAI_MODEL","gpt-5.5"), instructions=f"You are {prompt.name} version {prompt.version}. Classify as BILLING, ACCOUNT, TECHNICAL, or OTHER. Return only the category.", input=text)
    return response.output_text.strip().upper()

def evaluate(prompt: PromptVersion) -> dict[str,float]:
    results=[classify(text,prompt) for text,_ in CASES]
    correct=sum(actual==expected for actual,(_,expected) in zip(results,CASES))
    return {"accuracy":correct/len(CASES),"results":results}

def main() -> None:
    print(PromptVersion("ticket-classifier","3.4"), evaluate(PromptVersion("ticket-classifier","3.4")))

if __name__=="__main__": main()
