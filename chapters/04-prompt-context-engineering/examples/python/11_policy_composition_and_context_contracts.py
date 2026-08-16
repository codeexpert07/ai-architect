"""Chapter 4.32-4.33: compose typed policies and context contracts."""

from dataclasses import dataclass


@dataclass(frozen=True)
class ContextContract:
    name: str
    authority: str
    ttl_seconds: int
    max_tokens: int
    required_permission: str
    allowed_fields: frozenset[str]
    prohibited_fields: frozenset[str]


def compile_context(contract: ContextContract, data: dict[str, object], permissions: set[str]) -> dict[str, object]:
    if contract.required_permission not in permissions:
        raise PermissionError(contract.required_permission)
    if contract.allowed_fields & contract.prohibited_fields:
        raise ValueError("context contract has overlapping fields")
    return {
        key: value
        for key, value in data.items()
        if key in contract.allowed_fields
    }


@dataclass(frozen=True)
class Policy:
    name: str
    version: str
    instructions: tuple[str, ...]


def compose_policies(policies: list[Policy]) -> str:
    # Real systems should add conflict detection and capability validation.
    return "\n".join(
        f"[{policy.name}@{policy.version}]\n" + "\n".join(policy.instructions)
        for policy in policies
    )


if __name__ == "__main__":
    contract = ContextContract(
        "CustomerProfile", "high", 300, 800, "customer.read",
        frozenset({"locale", "plan", "account_status"}),
        frozenset({"password_hash", "access_token"}),
    )
    print(compile_context(contract, {
        "locale": "en-IN", "plan": "Enterprise", "password_hash": "secret"
    }, {"customer.read"}))
