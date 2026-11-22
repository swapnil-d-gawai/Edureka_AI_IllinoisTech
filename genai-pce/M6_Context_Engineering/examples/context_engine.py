"""Offline chunking, metadata-filtered retrieval, and bounded memory.

The lexical ranker is intentionally simple. The important production pattern is to
separate ingestion, authorization-aware retrieval, bounded memory, and answering.
"""

from dataclasses import dataclass, field
from re import findall


@dataclass(frozen=True)
class Document:
    # Source metadata is part of the evidence record, not presentation-only text.
    doc_id: str
    tenant: str
    jurisdiction: str
    effective_year: int
    text: str

    def __post_init__(self) -> None:
        if not all((self.doc_id.strip(), self.tenant.strip(), self.jurisdiction.strip())):
            raise ValueError("document metadata must not be empty")
        if not 2000 <= self.effective_year <= 2100 or not self.text.strip():
            raise ValueError("invalid effective_year or empty text")


@dataclass(frozen=True)
class Chunk:
    # offset preserves local lineage back to the source document for later audit.
    doc_id: str
    tenant: str
    jurisdiction: str
    effective_year: int
    text: str
    offset: int


@dataclass(frozen=True)
class Turn:
    role: str
    text: str

    def __post_init__(self) -> None:
        if self.role not in {"user", "assistant"} or not self.text.strip():
            raise ValueError("invalid conversation turn")


@dataclass
class Memory:
    # list and dict are mutable, so default_factory creates a new store per Memory
    # instance rather than accidentally sharing state across conversations.
    max_recent_turns: int
    turns: list[Turn] = field(default_factory=list)
    facts: dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not 1 <= self.max_recent_turns <= 100:
            raise ValueError("max_recent_turns must be between 1 and 100")

    def append(self, turn: Turn) -> None:
        self.turns.append(turn)
        self.turns = self.turns[-self.max_recent_turns :]

    def remember(self, key: str, value: str) -> None:
        if not key.strip() or not value.strip() or len(value) > 500:
            raise ValueError("memory facts must be non-empty and at most 500 characters")
        self.facts[key] = value


def chunk(document: Document, size: int = 18, overlap: int = 4) -> tuple[Chunk, ...]:
    if size < 2 or not 0 <= overlap < size:
        raise ValueError("chunk size/overlap are invalid")
    words = document.text.split()
    result: list[Chunk] = []
    # Repeating `overlap` words can preserve a boundary relationship. It also increases
    # storage and retrieval cost, so overlap should be benchmarked rather than guessed.
    step = size - overlap
    for start in range(0, len(words), step):
        piece = words[start : start + size]
        if not piece:
            continue
        result.append(
            Chunk(
                document.doc_id,
                document.tenant,
                document.jurisdiction,
                document.effective_year,
                " ".join(piece),
                start,
            )
        )
        if start + size >= len(words):
            break
    return tuple(result)


def terms(text: str) -> set[str]:
    # Sets make this tiny lexical retriever deterministic and easy to inspect.
    return set(findall(r"[a-z0-9]+", text.lower()))


def retrieve(
    query: str,
    chunks: tuple[Chunk, ...],
    *,
    tenant: str,
    jurisdiction: str,
    limit: int = 2,
) -> tuple[Chunk, ...]:
    if not query.strip() or not tenant.strip() or not jurisdiction.strip() or not 1 <= limit <= 20:
        raise ValueError("invalid retrieval request")
    query_terms = terms(query)
    # Tenant and jurisdiction filters are applied before scoring. Similarity alone is
    # never an authorization decision.
    eligible = [
        item
        for item in chunks
        if item.tenant == tenant and item.jurisdiction == jurisdiction
    ]
    ranked = sorted(
        eligible,
        key=lambda item: (len(query_terms & terms(item.text)), item.effective_year),
        reverse=True,
    )
    return tuple(item for item in ranked[:limit] if query_terms & terms(item.text))


def grounded_answer(question: str, evidence: tuple[Chunk, ...]) -> str:
    # The mock answer deliberately exposes source IDs and abstains without evidence;
    # it does not pretend to paraphrase facts it cannot verify.
    if not evidence:
        return "Insufficient approved evidence for this tenant and jurisdiction."
    sources = ", ".join(sorted({item.doc_id for item in evidence}))
    return f"Answer only from the retrieved policy context. Sources: {sources}."


def main() -> None:
    # One document is applicable, one is another jurisdiction, and one belongs to an
    # explicit other tenant to make metadata filtering visible in the output.
    documents = (
        Document(
            "POL-EU-24",
            "acme",
            "EU",
            2024,
            "EU refunds are reviewed within ten business days. Escalate suspected fraud and preserve evidence.",
        ),
        Document(
            "POL-US-23",
            "acme",
            "US",
            2023,
            "US refunds require a receipt. Expedited review is available for duplicate charges.",
        ),
        Document(
            "POL-EU-PRIVATE",
            "other",
            "EU",
            2025,
            "Other tenant private refund rules must never be retrieved for acme.",
        ),
    )
    chunks = tuple(piece for document in documents for piece in chunk(document))
    evidence = retrieve("How quickly are EU refunds reviewed?", chunks, tenant="acme", jurisdiction="EU")
    memory = Memory(max_recent_turns=3)
    memory.append(Turn("user", "How quickly are EU refunds reviewed?"))
    memory.append(Turn("assistant", grounded_answer("", evidence)))
    memory.remember("jurisdiction", "EU")
    print("Evidence IDs:", [item.doc_id for item in evidence])
    print("Grounded response:", grounded_answer("refund review", evidence))
    print("Recent turns:", memory.turns)
    print("Tenant isolation:", retrieve("private refund", chunks, tenant="acme", jurisdiction="EU"))


if __name__ == "__main__":
    main()
