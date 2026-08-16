"""Chapter 4.34-4.36: degraded context -> LLM -> privacy-aware telemetry."""

import os
import time
from dataclasses import dataclass
from enum import Enum
from openai import OpenAI

class ContextStatus(Enum): COMPLETE="complete"; DEGRADED="degraded"; UNAVAILABLE="unavailable"
@dataclass(frozen=True)
class ContextResult:
    status:ContextStatus; evidence:list[str]; reason:str|None=None

def handle_retrieval_failure(error:Exception,safe_fallback:str)->ContextResult:
    return ContextResult(ContextStatus.DEGRADED,[safe_fallback],str(error)) if safe_fallback else ContextResult(ContextStatus.UNAVAILABLE,[],str(error))

def telemetry(prompt_version:str,sources:list[str],input_tokens:int,output_tokens:int,latency_ms:int,schema_valid:bool)->dict[str,object]:
    return {"prompt_version":prompt_version,"context_sources":sources,"input_tokens":input_tokens,"output_tokens":output_tokens,"latency_ms":latency_ms,"schema_valid":schema_valid}

def main()->None:
    started=time.perf_counter()
    try: raise TimeoutError("retrieval timeout")
    except TimeoutError as exc: context=handle_retrieval_failure(exc,"Use approved policy only.")
    response=OpenAI().responses.create(model=os.getenv("OPENAI_MODEL","gpt-5.5"),instructions="If context is degraded, clearly state limitations and never invent missing evidence.",input=f"STATUS={context.status.value}\nEVIDENCE={context.evidence}\nUSER: Can I get a refund?")
    usage=response.usage
    print(response.output_text)
    print(telemetry("support/v3.4",["fallback:policy"],usage.input_tokens if usage else 0,usage.output_tokens if usage else 0,int((time.perf_counter()-started)*1000),True))

if __name__=="__main__": main()
