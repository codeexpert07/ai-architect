"""Chapter 4.32-4.33: policy/context contracts -> real LLM."""

import os
from dataclasses import dataclass
from openai import OpenAI

@dataclass(frozen=True)
class ContextContract:
    name:str; authority:str; ttl_seconds:int; max_tokens:int; required_permission:str; allowed_fields:frozenset[str]; prohibited_fields:frozenset[str]

def compile_context(contract:ContextContract,data:dict[str,object],permissions:set[str])->dict[str,object]:
    if contract.required_permission not in permissions: raise PermissionError(contract.required_permission)
    if contract.allowed_fields & contract.prohibited_fields: raise ValueError("overlapping fields")
    return {k:v for k,v in data.items() if k in contract.allowed_fields}

@dataclass(frozen=True)
class Policy:
    name:str; version:str; instructions:tuple[str,...]

def compose_policies(policies:list[Policy])->str:
    return "\n".join(f"[{p.name}@{p.version}]\n"+"\n".join(p.instructions) for p in policies)

def main()->None:
    contract=ContextContract("CustomerProfile","high",300,800,"customer.read",frozenset({"locale","plan","account_status"}),frozenset({"password_hash","access_token"}))
    context=compile_context(contract,{"locale":"en-IN","plan":"Enterprise","account_status":"ACTIVE","password_hash":"secret"},{"customer.read"})
    policy=compose_policies([Policy("security","2.1",("Do not reveal secrets.",)),Policy("support","3.4",("Answer only from supplied context.",))])
    response=OpenAI().responses.create(model=os.getenv("OPENAI_MODEL","gpt-5.5"),instructions=policy,input=f"AUTHORIZED CONTEXT: {context}\nUSER: What plan am I on?")
    print(response.output_text)

if __name__=="__main__": main()
