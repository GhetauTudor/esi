# ESI Architecture

## Overview

ESI (Epistemic State Interface) is a thin standard layer that sits between an AI agent and its memory backend. It does one thing: ensure every memory query returns not just *what* was remembered, but *how well* it was remembered.

```
┌─────────────────────────────────────────────────┐
│                  Your AI Agent                  │
└─────────────────────┬───────────────────────────┘
                      │ mem.query("...")
                      ▼
┌─────────────────────────────────────────────────┐
│              EpistemicMemory                    │
│                                                 │
│   • Wraps any backend                           │
│   • Enforces Result return type                 │
│   • Provides should_abstain() decision          │
└─────────────────────┬───────────────────────────┘
                      │
          ┌───────────┴───────────┐
          ▼                       ▼
┌─────────────────┐   ┌───────────────────────┐
│ SimpleMemory    │   │ Mem0Backend           │
│ Backend         │   │ (+ any future backend)│
│                 │   │                       │
│ Zero deps       │   │ pip install mem0ai    │
│ In-memory       │   │ Wraps mem0.Memory()   │
└─────────────────┘   └───────────────────────┘
```

## The Result contract

Every `query()` call returns a `Result` object:

```python
@dataclass
class Result:
    answer: Optional[str]   # the retrieved memory, or None if abstaining
    confidence: float        # 0.0–1.0: how well does this match the query?
    freshness: float         # 0.0–1.0: how recent/reliable is this memory?
    source: Optional[str]   # optional: where this memory came from
    metadata: dict           # optional: backend-specific metadata
```

This is the **Epistemic State Interface standard**. Any backend that returns `Result` is ESI-compatible.

## Epistemic dimensions

### Confidence
Measures how well the stored memory answers the query.

- In `SimpleMemoryBackend`: keyword coverage (fraction of query tokens found in memory)
- In `Mem0Backend`: cosine similarity score from Mem0's vector search
- Range: `0.0` (no match) → `1.0` (perfect match)

### Freshness
Measures how much to trust the recency of the information.

- Formula: `exp(-decay_rate × normalized_age × 10) + log(1 + access_count) × 0.05`
- Decays exponentially with time since storage
- Grows slightly with access frequency (reinforcement — used memories stay fresh)
- Range: `0.0` (very old, untouched) → `1.0` (just stored)

### Planned dimensions (roadmap)

| Dimension | Meaning | Status |
|-----------|---------|--------|
| `degradation` | How much detail was lost to compression | Planned |
| `contradiction` | Whether conflicting memories exist | Planned |
| `source_quality` | Reliability of the original source | Planned |
| `difficulty` | Query complexity for energy routing | Planned |

## Abstention

An agent should abstain when its epistemic state is too uncertain:

```python
result = mem.query("What does the user prefer?")

if result.should_abstain(threshold=0.3):
    # Ask the user instead of guessing
    ...
```

The `epistemic_score()` geometric mean combines confidence and freshness for a single quality signal:

```python
result.epistemic_score()  # sqrt(confidence × freshness)
```

## Adding a new backend

Implement two methods and return `Result`:

```python
from esi.core import Result

class MyBackend:
    def add(self, text: str, metadata: dict = None) -> None:
        ...

    def query(self, query: str) -> Result:
        # your retrieval logic
        return Result(
            answer="...",
            confidence=0.85,
            freshness=0.92,
        )
```

Pass it to `EpistemicMemory`:

```python
mem = EpistemicMemory(backend=MyBackend())
```

That's the full contract.
