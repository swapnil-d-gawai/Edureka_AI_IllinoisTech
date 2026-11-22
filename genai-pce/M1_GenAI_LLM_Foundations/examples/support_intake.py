"""Offline, policy-gated GenAI support-intake example.

The mock model proposes text, but validated application code owns classification,
approval, and the final business action. No network or credentials are used.
"""

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class Ticket:
    # A frozen dataclass gives this small input object named fields and prevents
    # accidental mutation after construction; __post_init__ validates it.
    ticket_id: str
    customer_text: str

    def __post_init__(self) -> None:
        if not self.ticket_id.strip() or len(self.ticket_id) > 40:
            raise ValueError("ticket_id must contain 1-40 characters")
        if not self.customer_text.strip() or len(self.customer_text) > 2_000:
            raise ValueError("customer_text must contain 1-2000 characters")


@dataclass(frozen=True)
class ModelConfig:
    provider: str = "mock"
    model: str = "deterministic-v1"
    max_output_chars: int = 600

    def __post_init__(self) -> None:
        if self.provider not in {"mock"}:
            raise ValueError("only the offline mock provider is configured")
        if not 1 <= self.max_output_chars <= 2_000:
            raise ValueError("max_output_chars must be between 1 and 2000")


class TextProvider(Protocol):
    # Protocol describes the provider boundary using structural typing: any object
    # with a generate(system, user) method can be supplied, even without inheritance.
    def generate(self, system: str, user: str) -> str: ...


class MockProvider:
    """Deterministic stand-in that keeps the exercise fully offline.

    A real provider adapter should implement the same Protocol while leaving policy
    decisions outside the provider.
    """

    def __init__(self, config: ModelConfig) -> None:
        self.config = config

    def generate(self, system: str, user: str) -> str:
        category = user.split("category=", 1)[1].split(";")[0]
        templates = {
            "refund": "We can review the return. No refund is promised until policy eligibility is verified.",
            "shipping": "We can check the shipment status; share the order identifier if available.",
            "product": "A product specialist can help confirm compatibility and next steps.",
            "unclear": "We need one clarification before routing this request to a specialist.",
        }
        text = templates[category]
        return text[: self.config.max_output_chars]


@dataclass(frozen=True)
class IntakeDecision:
    ticket_id: str
    category: str
    draft: str
    approved: bool
    policy_action: str


def classify(text: str) -> str:
    # Exact rules are intentionally auditable and cheaper than an LLM for these labels.
    normalized = " " + " ".join(text.lower().split()) + " "
    rules = {
        "refund": (" refund ", " return ", " charged twice "),
        "shipping": (" delivery ", " shipped ", " package ", " tracking "),
        "product": (" compatible ", " specification ", " does it work "),
    }
    for category, needles in rules.items():
        if any(needle in normalized for needle in needles):
            return category
    return "unclear"


def apply_policy(category: str) -> tuple[bool, str]:
    # Consequential authorization belongs here, not in persuasive generated prose.
    if category == "unclear":
        return False, "escalate_for_clarification"
    if category == "refund":
        return False, "human_approval_required"
    return True, "approved_draft"


def process(ticket: Ticket, provider: TextProvider) -> IntakeDecision:
    # Data/control flow: validate input at construction -> classify -> draft ->
    # reject empty output -> independently apply policy.
    category = classify(ticket.customer_text)
    prompt = (
        f"category={category}; task=draft_support_reply; "
        f"customer_text={ticket.customer_text!r}"
    )
    draft = provider.generate(
        "Use only the supplied policy. Do not promise actions or request sensitive data.",
        prompt,
    )
    if not draft.strip():
        raise RuntimeError("model returned an empty draft")
    approved, action = apply_policy(category)
    return IntakeDecision(ticket.ticket_id, category, draft, approved, action)


def main() -> None:
    # Fixed fixtures make the successful offline behavior easy to reproduce.
    tickets = [
        Ticket("A-101", "My delivery has not arrived and the package tracking is stale."),
        Ticket("A-102", "Please refund the duplicate charge on my order."),
        Ticket("A-103", "Is this charger compatible with my laptop?"),
        Ticket("A-104", "I need help with something important."),
    ]
    provider = MockProvider(ModelConfig())
    for ticket in tickets:
        decision = process(ticket, provider)
        print(
            f"{decision.ticket_id}: category={decision.category}, "
            f"approved={decision.approved}, action={decision.policy_action}\n"
            f"  {decision.draft}"
        )


if __name__ == "__main__":
    main()
