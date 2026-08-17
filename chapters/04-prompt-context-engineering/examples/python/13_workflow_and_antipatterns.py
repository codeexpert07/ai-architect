"""Chapter 4.37-4.40: production workflow around a real model call."""

import os
from dataclasses import dataclass
from openai import OpenAI

@dataclass(frozen=True)
class Request:
    user_id:str; text:str

def design_workflow(request:Request)->list[str]:
    return ["define task","authorize retrieval","select context","compile prompt","invoke model","validate output","record telemetry"]

def anti_pattern_replacements()->dict[str,str]:
    return {"entire conversation forever":"recent turns + state + summary","all retrieved documents":"rank + filter + budget","model enforces authorization":"deterministic authorization","valid JSON means correct":"schema + semantic + authorization validation"}

def main()->None:
    request=Request("u-1","Where is my order?")
    workflow=design_workflow(request)
    context="AUTHORIZED ORDER STATE: order=A-100; status=SHIPPED"
    response=OpenAI().responses.create(model=os.getenv("OPENAI_MODEL","gpt-5.5"),instructions="Follow the production workflow. Use only authorized order state and do not invent tracking details.",input=f"WORKFLOW={workflow}\n{context}\nUSER={request.text}")
    print(response.output_text)
    print("anti-pattern replacements:",anti_pattern_replacements())

if __name__=="__main__": main()
