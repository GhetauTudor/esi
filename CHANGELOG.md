# Changelog

All notable changes to ESI will be documented here.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).
ESI uses [Semantic Versioning](https://semver.org/).

---

## [Unreleased]

### Planned
- `degradation` score — detect compressed/summarized memories
- `contradiction` detection — flag conflicting memories
- Mem0 backend (live integration)
- LangMem backend
- `difficulty` estimation for energy-aware model routing

---

## [0.1.0] — 2026-06-27

### Added
- `Result` dataclass — the ESI standard contract (`answer`, `confidence`, `freshness`)
- `EpistemicMemory` wrapper — drop-in epistemic state for any memory backend
- `SimpleMemoryBackend` — zero-dependency reference implementation
  - Keyword-coverage confidence scoring
  - Exponential freshness decay with access-count reinforcement
  - `forget()` support
- `Mem0Backend` — ESI wrapper for [mem0ai](https://github.com/mem0ai/mem0)
- `should_abstain()` — abstention decision based on configurable threshold
- `epistemic_score()` — geometric mean of confidence × freshness
- Benchmark + forgetting demo chart
- GitHub Actions CI on Python 3.9–3.12
- Full test suite (8 tests)

[Unreleased]: https://github.com/GhetauTudor/esi/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/GhetauTudor/esi/releases/tag/v0.1.0
