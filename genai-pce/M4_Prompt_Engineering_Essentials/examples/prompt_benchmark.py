"""Offline benchmark for zero-, one-, and few-shot prompt variants.

The deterministic model makes prompt/example effects visible without claiming that
the same effect will occur with a real LLM.
"""

from dataclasses import dataclass
from typing import Protocol

LABELS = ("billing", "delivery", "technical", "uncertain")


@dataclass(frozen=True)
class PromptSpec:
    # The dataclass is the prompt's versionable specification: task, label contract,
    # demonstrations, and output rule are separate fields rather than ad hoc prose.
    task: str
    labels: tuple[str, ...]
    examples: tuple[tuple[str, str], ...]
    output_rule: str = "Return exactly one label."

    def __post_init__(self) -> None:
        if not self.task.strip() or not self.examples and not self.labels:
            raise ValueError("task and at least one label are required")
        if len(set(self.labels)) != len(self.labels):
            raise ValueError("labels must be unique")
        for text, label in self.examples:
            if not text.strip() or label not in self.labels:
                raise ValueError("each example must have text and an allowed label")


@dataclass(frozen=True)
class Case:
    text: str
    expected: str

    def __post_init__(self) -> None:
        if self.expected not in LABELS or not self.text.strip():
            raise ValueError("invalid benchmark case")


@dataclass(frozen=True)
class Score:
    variant: str
    correct: int
    abstentions: int
    total: int
    estimated_tokens: int

    @property
    def accuracy(self) -> float:
        # Abstention has a separate count because raw accuracy can hide an unsafe guess.
        return self.correct / self.total if self.total else 0.0


class PromptModel(Protocol):
    # A Protocol lets the evaluator accept any classifier-shaped model implementation.
    def classify(self, prompt: str, text: str) -> str: ...


class DeterministicMockModel:
    def classify(self, prompt: str, text: str) -> str:
        # The mock reacts to fixed synonyms and to rendered examples. That makes the
        # prompt-cost versus coverage trade-off reproducible.
        lowered = text.lower()
        if "charged twice" in lowered or "invoice" in lowered:
            return "billing"
        if "tracking" in lowered or "delivery" in lowered:
            return "delivery"
        if "crash" in lowered or "error code" in lowered:
            return "technical"
        if "Example output: billing" in prompt and "debited again" in lowered:
            return "billing"
        if "Example output: delivery" in prompt and "courier" in lowered:
            return "delivery"
        if "Example output: technical" in prompt and "froze" in lowered:
            return "technical"
        return "uncertain"


def render(spec: PromptSpec, text: str) -> str:
    # Tags label untrusted customer data; they improve boundary clarity but do not by
    # themselves replace downstream validation and injection controls.
    blocks = [
        f"Task: {spec.task}",
        f"Allowed labels: {', '.join(spec.labels)}",
        spec.output_rule,
    ]
    for example, label in spec.examples:
        blocks.append(f"Example input: {example}\nExample output: {label}")
    blocks.append("<untrusted_customer_text>" + text + "</untrusted_customer_text>")
    return "\n".join(blocks)


def evaluate(name: str, spec: PromptSpec, cases: tuple[Case, ...], model: PromptModel) -> Score:
    if not cases:
        raise ValueError("cases must not be empty")
    predictions = [model.classify(render(spec, case.text), case.text) for case in cases]
    # Machine-check the output contract before computing any quality metric.
    invalid = [value for value in predictions if value not in spec.labels]
    if invalid:
        raise RuntimeError(f"model returned disallowed labels: {invalid}")
    prompt_tokens = sum(max(1, (len(render(spec, case.text)) + 3) // 4) for case in cases)
    return Score(
        name,
        sum(predicted == case.expected for predicted, case in zip(predictions, cases)),
        predictions.count("uncertain"),
        len(cases),
        prompt_tokens,
    )


def main() -> None:
    # These variants intentionally differ by examples while holding labels and cases.
    base = ("Classify a support ticket. Choose uncertain when evidence is insufficient.", LABELS)
    variants = {
        "zero-shot": PromptSpec(base[0], base[1], ()),
        "one-shot": PromptSpec(
            base[0],
            base[1],
            (("I was charged twice for the same order", "billing"),),
        ),
        "few-shot": PromptSpec(
            base[0],
            base[1],
            (
                ("I was charged twice for the same order", "billing"),
                ("The delivery tracking link is stale", "delivery"),
                ("The app crash shows error code E42", "technical"),
            ),
        ),
    }
    cases = (
        Case("My invoice contains a duplicate charge", "billing"),
        Case("The delivery tracking has not moved", "delivery"),
        Case("The checkout returns error code E17", "technical"),
        Case("My card was debited again for the same order", "billing"),
        Case("The courier lost the parcel", "delivery"),
        Case("Checkout froze when I opened the cart", "technical"),
        Case("Something feels wrong; please investigate", "uncertain"),
    )
    for name, spec in variants.items():
        score = evaluate(name, spec, cases, DeterministicMockModel())
        print(
            f"{score.variant}: accuracy={score.accuracy:.0%}, "
            f"abstentions={score.abstentions}, estimated_tokens={score.estimated_tokens}"
        )


if __name__ == "__main__":
    main()
