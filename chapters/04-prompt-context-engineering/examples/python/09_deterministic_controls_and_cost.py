"""Chapter 4.27-4.28: LLM call plus deterministic business and cost controls."""

import os
from dataclasses import dataclass
from openai import OpenAI

@dataclass(frozen=True)
class Usage:
    input_tokens:int; output_tokens:int; input_price_per_million:float; output_price_per_million:float; latency_ms:int
    @property
    def cost(self)->float: return (self.input_tokens*self.input_price_per_million+self.output_tokens*self.output_price_per_million)/1_000_000

def enforce_business_rule(decision:str, refund_days:int)->str:
    return "ESCALATE" if decision=="REFUND" and refund_days>30 else decision

def main()->None:
    client=OpenAI()
    response=client.responses.create(model=os.getenv("OPENAI_MODEL","gpt-5.5"), instructions="Decide whether a refund request should be REFUND or ESCALATE. Return only one word.", input="Customer requests a refund 45 days after purchase.")
    decision=enforce_business_rule(response.output_text.strip().upper(),45)
    usage=response.usage
    print("model decision:",response.output_text.strip(),"final decision:",decision)
    if usage:
        print("provider usage:",usage.model_dump())
        print("Illustrative cost requires the actual model price configuration.")

if __name__=="__main__": main()
