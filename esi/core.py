from dataclasses import dataclass, field
from typing import Optional, Any
import time


@dataclass
class Result:
    """Epistemic State Interface — the standard return type for any memory query.

    Every memory retrieval should expose not just *what* was remembered,
    but *how well* it was remembered.
    """
    answer: Optional[str]
    confidence: float          # 0.0–1.0: how well does this match the query?
    freshness: float           # 0.0–1.0: how recent is this memory? (1.0 = just stored)
    source: Optional[str] = None
    metadata: dict = field(default_factory=dict)

    def should_abstain(self, threshold: float = 0.3) -> bool:
        """Return True if the agent should abstain rather than answer."""
        return self.confidence < threshold

    def epistemic_score(self) -> float:
        """Combined epistemic quality score (geometric mean of confidence and freshness)."""
        return (self.confidence * self.freshness) ** 0.5

    def __repr__(self):
        status = "ABSTAIN" if self.should_abstain() else "ANSWER"
        return (
            f"Result({status} | answer={self.answer!r} | "
            f"confidence={self.confidence:.2f} | freshness={self.freshness:.2f})"
        )


class EpistemicMemory:
    """Drop-in wrapper that adds epistemic state to any memory backend.

    Usage:
        mem = EpistemicMemory(backend=SimpleMemoryBackend())
        mem.add("The user prefers espresso")
        result = mem.query("What coffee does the user like?")
        if not result.should_abstain():
            print(result.answer)
    """

    def __init__(self, backend=None, abstention_threshold: float = 0.3):
        if backend is None:
            from .backends.simple import SimpleMemoryBackend
            backend = SimpleMemoryBackend()
        self._backend = backend
        self.abstention_threshold = abstention_threshold

    def add(self, text: str, metadata: dict = None) -> None:
        """Store a memory in the backend."""
        self._backend.add(text, metadata or {})

    def query(self, query: str) -> Result:
        """Query memory and return an epistemic result."""
        return self._backend.query(query)

    def forget(self, query: str) -> int:
        """Remove memories matching the query. Returns count removed."""
        if hasattr(self._backend, "forget"):
            return self._backend.forget(query)
        return 0
