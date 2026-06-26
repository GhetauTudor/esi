"""Zero-dependency in-memory backend for ESI.

No external libraries required — works out of the box.
Designed for demos, testing, and small agents.
"""
import time
import math
from typing import List, Tuple, Optional
from ..core import Result


class SimpleMemoryBackend:
    """Keyword-overlap memory with time-based freshness decay.

    Confidence  = coverage of query keywords found in stored text
    Freshness   = exponential decay based on time since storage and access count

    This is the reference implementation of the ESI standard.
    """

    QUESTION_WORDS = {
        "what", "who", "where", "when", "why", "how", "which", "is", "are", "do", "does",
        "the", "a", "an", "of", "in", "on", "at", "to", "for", "and", "or", "but",
    }

    def __init__(self, decay_rate: float = 0.1, max_age_seconds: float = 3600.0):
        """
        Args:
            decay_rate: Controls how fast freshness decays (higher = faster decay).
            max_age_seconds: Age at which freshness reaches ~0 (default: 1 hour).
        """
        self._memories: List[dict] = []
        self.decay_rate = decay_rate
        self.max_age_seconds = max_age_seconds

    def add(self, text: str, metadata: dict = None) -> None:
        self._memories.append({
            "text": text,
            "stored_at": time.time(),
            "access_count": 0,
            "metadata": metadata or {},
        })

    def _tokenize(self, text: str) -> set:
        words = set(text.lower().split())
        return words - self.QUESTION_WORDS

    def _confidence(self, query_tokens: set, memory_text: str) -> float:
        """Fraction of query keywords found in the memory."""
        if not query_tokens:
            return 0.0
        memory_tokens = self._tokenize(memory_text)
        overlap = query_tokens & memory_tokens
        return len(overlap) / len(query_tokens)

    def _freshness(self, stored_at: float, access_count: int) -> float:
        """Exponential decay from 1.0 (just stored) toward 0.0 (very old/unused)."""
        age = time.time() - stored_at
        normalized_age = age / self.max_age_seconds
        # Slight boost for frequently accessed memories (reinforcement)
        reinforcement = math.log1p(access_count) * 0.05
        raw = math.exp(-self.decay_rate * normalized_age * 10) + reinforcement
        return min(1.0, max(0.0, raw))

    def query(self, query: str, top_k: int = 1) -> Result:
        if not self._memories:
            return Result(answer=None, confidence=0.0, freshness=0.0)

        query_tokens = self._tokenize(query)
        scored: List[Tuple[float, float, dict]] = []

        for mem in self._memories:
            conf = self._confidence(query_tokens, mem["text"])
            fresh = self._freshness(mem["stored_at"], mem["access_count"])
            scored.append((conf, fresh, mem))

        # Rank by confidence first, then freshness as tiebreaker
        scored.sort(key=lambda x: (x[0], x[1]), reverse=True)
        best_conf, best_fresh, best_mem = scored[0]

        if best_conf < 0.1:
            return Result(answer=None, confidence=0.0, freshness=best_fresh)

        # Mark as accessed (reinforcement)
        best_mem["access_count"] += 1

        return Result(
            answer=best_mem["text"],
            confidence=best_conf,
            freshness=best_fresh,
            metadata=best_mem["metadata"],
        )

    def forget(self, query: str) -> int:
        query_tokens = self._tokenize(query)
        before = len(self._memories)
        self._memories = [
            m for m in self._memories
            if self._confidence(query_tokens, m["text"]) < 0.5
        ]
        return before - len(self._memories)

    def __len__(self):
        return len(self._memories)
