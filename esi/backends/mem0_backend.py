"""Mem0 backend for ESI.

Wraps the Mem0 memory system (https://github.com/mem0ai/mem0)
and returns ESI Result objects with confidence + freshness.

Install mem0:
    pip install mem0ai

Usage:
    from mem0 import Memory
    from esi import EpistemicMemory
    from esi.backends.mem0_backend import Mem0Backend

    mem = EpistemicMemory(backend=Mem0Backend(user_id="alice"))
    mem.add("The user prefers espresso coffee")
    result = mem.query("What coffee does the user like?")
    print(result.confidence, result.freshness)
"""
import time
import math
from typing import Optional
from ..core import Result


class Mem0Backend:
    """ESI wrapper for Mem0 memory.

    Confidence  = Mem0's own relevance score (normalized to 0–1)
    Freshness   = exponential decay based on memory creation time
    """

    def __init__(
        self,
        user_id: str = "default",
        decay_rate: float = 0.1,
        max_age_seconds: float = 86400.0,
        mem0_config: Optional[dict] = None,
    ):
        """
        Args:
            user_id: Mem0 user identifier (memories are namespaced per user).
            decay_rate: Controls freshness decay speed.
            max_age_seconds: Age at which freshness reaches ~0 (default: 24h).
            mem0_config: Optional Mem0 config dict (passed to Memory()).
        """
        try:
            from mem0 import Memory
        except ImportError as e:
            raise ImportError(
                "mem0ai is required for Mem0Backend. "
                "Install it with: pip install mem0ai"
            ) from e

        self.user_id = user_id
        self.decay_rate = decay_rate
        self.max_age_seconds = max_age_seconds
        self._mem = Memory(**(mem0_config or {}))

    def add(self, text: str, metadata: dict = None) -> None:
        """Store a memory in Mem0."""
        self._mem.add(text, user_id=self.user_id, metadata=metadata or {})

    def query(self, query: str) -> Result:
        """Query Mem0 and return an ESI Result."""
        results = self._mem.search(query, user_id=self.user_id, limit=1)

        # Mem0 returns a list of dicts with 'memory', 'score', 'created_at'
        if not results:
            return Result(answer=None, confidence=0.0, freshness=0.0)

        top = results[0]
        answer = top.get("memory", "")
        score = float(top.get("score", 0.0))

        # Normalize score to 0–1 (Mem0 scores are cosine similarity, already 0–1)
        confidence = max(0.0, min(1.0, score))

        # Compute freshness from creation timestamp if available
        created_at = top.get("created_at")
        freshness = self._compute_freshness(created_at)

        if confidence < 0.1:
            return Result(answer=None, confidence=0.0, freshness=freshness)

        return Result(
            answer=answer,
            confidence=confidence,
            freshness=freshness,
            metadata={k: v for k, v in top.items() if k not in ("memory", "score")},
        )

    def forget(self, memory_id: str) -> int:
        """Delete a specific memory by its Mem0 ID."""
        try:
            self._mem.delete(memory_id=memory_id, user_id=self.user_id)
            return 1
        except Exception:
            return 0

    def _compute_freshness(self, created_at) -> float:
        """Compute freshness from Mem0's created_at timestamp."""
        if created_at is None:
            return 1.0  # unknown age → assume fresh

        try:
            # Mem0 returns ISO 8601 strings or Unix timestamps
            if isinstance(created_at, (int, float)):
                stored_ts = float(created_at)
            else:
                from datetime import datetime, timezone
                dt = datetime.fromisoformat(str(created_at).replace("Z", "+00:00"))
                stored_ts = dt.timestamp()

            age = time.time() - stored_ts
            normalized_age = age / self.max_age_seconds
            return max(0.0, math.exp(-self.decay_rate * normalized_age * 10))
        except Exception:
            return 1.0
