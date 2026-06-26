# ESI Roadmap

## v0.1.0 (current)
- [x] `Result` dataclass — the ESI standard contract
- [x] `EpistemicMemory` wrapper
- [x] `SimpleMemoryBackend` — zero-dependency reference implementation
- [x] `confidence` — keyword coverage score
- [x] `freshness` — time + access decay

## v0.2.0 — Community contributions
- [ ] **`degradation` score** — detect when a memory has been compressed/summarized and may have lost precision. ← *good first issue*
- [ ] **`contradiction` detection** — flag when two memories conflict. ← *help wanted*
- [ ] **Mem0 backend** — ESI wrapper for [Mem0](https://github.com/mem0ai/mem0)
- [ ] **LangMem backend** — ESI wrapper for LangMem

## v0.3.0 — Advanced epistemic state
- [ ] **`source_quality`** — confidence in the original source of information
- [ ] **`difficulty` estimation** — query complexity score for energy-aware routing
- [ ] Energy-aware model routing: low confidence + high difficulty → larger model

## Research direction
The long-term goal is a formal **Forgetting-Calibration Coupling (FCC)** metric:
how well does an agent's uncertainty track what it has actually forgotten?

Current memory systems compress and prune — but don't update their confidence accordingly.
ESI proposes that forgetting should automatically increase epistemic uncertainty.

See the [benchmark](benchmarks/forgetting_benchmark.py) for a concrete demonstration.
