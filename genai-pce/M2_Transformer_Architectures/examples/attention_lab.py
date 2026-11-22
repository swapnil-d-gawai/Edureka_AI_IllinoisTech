"""Small, dependency-free self-attention and architecture-selection lab.

The matrices intentionally use tiny tuples so the numerical steps remain visible;
they are not a production transformer implementation.
"""

from dataclasses import dataclass
from math import exp, sqrt
from typing import Sequence

Vector = tuple[float, ...]
Matrix = tuple[Vector, ...]


@dataclass(frozen=True)
class ArchitectureRequest:
    # Dataclasses make task requirements explicit, while __post_init__ rejects a
    # request that has no meaningful task description.
    task: str
    requires_bidirectional_context: bool = False
    generates_new_text: bool = True
    transforms_conditioned_text: bool = False

    def __post_init__(self) -> None:
        if not self.task.strip():
            raise ValueError("task must not be empty")


def dot(left: Vector, right: Vector) -> float:
    if len(left) != len(right):
        raise ValueError("vectors must have equal dimensions")
    return sum(a * b for a, b in zip(left, right))


def stable_softmax(values: Sequence[float]) -> Vector:
    # Subtracting the maximum preserves the softmax result and avoids overflow from
    # exponentiating a very large score.
    if not values:
        raise ValueError("softmax needs values")
    peak = max(values)
    weights = [exp(value - peak) for value in values]
    total = sum(weights)
    return tuple(weight / total for weight in weights)


def self_attention(query: Matrix, key: Matrix, value: Matrix, *, causal: bool) -> Matrix:
    # Shape checks are input contracts. They catch errors before a matrix operation
    # can silently mix incompatible vectors.
    if len(query) != len(key) or len(query) != len(value) or not query:
        raise ValueError("Q, K, and V must have the same non-zero row count")
    dimension = len(key[0])
    if dimension == 0 or any(len(row) != dimension for row in (*query, *key)):
        raise ValueError("Q and K must be non-empty rectangular vectors")
    output_dimension = len(value[0])
    if output_dimension == 0 or any(len(row) != output_dimension for row in value):
        raise ValueError("V must contain non-empty rectangular vectors")

    result: list[Vector] = []
    for index, query_row in enumerate(query):
        # A masked future score is -infinity, whose exp(negative infinity) is zero.
        # Every row therefore attends only to current/past positions when causal=True.
        scores = [
            dot(query_row, key_row) / sqrt(dimension)
            if not causal or column <= index
            else float("-inf")
            for column, key_row in enumerate(key)
        ]
        attention = stable_softmax(scores)
        result.append(
            tuple(
                sum(attention[token] * value[token][feature] for token in range(len(value)))
                for feature in range(output_dimension)
            )
        )
    return tuple(result)


def choose_architecture(request: ArchitectureRequest) -> str:
    # This deterministic teaching heuristic illustrates task-shape selection;
    # production selection should still be benchmarked.
    if request.transforms_conditioned_text:
        return "encoder-decoder"
    if request.requires_bidirectional_context and not request.generates_new_text:
        return "encoder-only"
    return "decoder-only"


def token_budget(system: int, history: int, documents: int, answer: int) -> int:
    # The sum represents a shared window allocation, unlike model parameter count.
    values = (system, history, documents, answer)
    if any(value < 0 for value in values):
        raise ValueError("token budget components must be non-negative")
    return sum(values)


def rounded(matrix: Matrix) -> list[list[float]]:
    return [[round(value, 3) for value in row] for row in matrix]


def main() -> None:
    # Q=K here keeps the toy example compact; real learned projections differ.
    query: Matrix = ((1.0, 0.0), (0.0, 1.0), (1.0, 1.0), (-1.0, 1.0))
    key = query
    value: Matrix = ((1.0, 0.0), (0.0, 1.0), (1.0, 1.0), (0.5, 0.5))

    bidirectional = self_attention(query, key, value, causal=False)
    causal = self_attention(query, key, value, causal=True)
    print("Bidirectional value mixtures:", rounded(bidirectional))
    print("Causal value mixtures:", rounded(causal))
    print(
        "Architecture choices:",
        choose_architecture(
            ArchitectureRequest("risk classification", True, False, False)
        ),
        choose_architecture(ArchitectureRequest("case summary", False, True, True)),
        choose_architecture(ArchitectureRequest("investigation assistant")),
    )
    print("Shared context budget:", token_budget(400, 1_200, 4_000, 1_000))


if __name__ == "__main__":
    main()
