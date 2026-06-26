"""ESI Quickstart — run this to see epistemic state in action."""
from esi import EpistemicMemory, SimpleMemoryBackend
import time

print("=== ESI Quickstart ===\n")

mem = EpistemicMemory(backend=SimpleMemoryBackend(max_age_seconds=2.0, decay_rate=0.5))

# Store a memory
mem.add("The user prefers espresso coffee")
print("Stored: 'The user prefers espresso coffee'")

# Query immediately — fresh, confident
result = mem.query("What coffee does the user prefer?")
print(f"\n[Fresh query]  {result}")
print(f"  → epistemic_score={result.epistemic_score():.2f}")
print(f"  → should_abstain={result.should_abstain()}")

# Wait — memory ages
print("\nWaiting 1.5s (memory ages)...")
time.sleep(1.5)

result = mem.query("What coffee does the user prefer?")
print(f"\n[Stale query]  {result}")
print(f"  → epistemic_score={result.epistemic_score():.2f}")
print(f"  → should_abstain={result.should_abstain()}")

# Unknown query — abstains
result = mem.query("What is the capital of Mars?")
print(f"\n[Unknown query]  {result}")
print(f"  → should_abstain={result.should_abstain()}")

print("\n=== Key insight ===")
print("Standard memory returns the same answer with the same confidence regardless of age.")
print("ESI memory knows what it knows, what it forgot, and how certain it is.")
