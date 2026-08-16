"""Chapter 4.29-4.31: template + capability selection -> real LLM."""

import os
from dataclasses import dataclass
from openai import OpenAI

@dataclass(frozen=True)
class PromptTemplate:
    policy_version:str; task:str; output_contract:str
    def render(self,context:str,user_input:str)->str:
        return f"POLICY VERSION: {self.policy_version}\nTASK: {self.task}\nCONTEXT: <context>{context}</context>\nUSER: <user_input>{user_input}</user_input>\nOUTPUT: {self.output_contract}"

@dataclass(frozen=True)
class ModelCapabilities:
    name:str; supports_structured_output:bool; max_context_tokens:int

def select_model(candidates:list[ModelCapabilities],required_context:int)->ModelCapabilities:
    eligible=[m for m in candidates if m.max_context_tokens>=required_context]
    if not eligible: raise RuntimeError("no compatible model")
    return eligible[0]

def main()->None:
    model=select_model([ModelCapabilities(os.getenv("OPENAI_MODEL","gpt-5.5"),True,128000)],20000)
    template=PromptTemplate("support/v3.4","Answer the support question.","Concise answer with source")
    prompt=template.render("Plan=Enterprise; renewal=2026-12-01","What is my renewal date?")
    response=OpenAI().responses.create(model=model.name,instructions="Follow the versioned template and do not invent facts.",input=prompt)
    print("selected:",model); print(response.output_text)

if __name__=="__main__": main()
