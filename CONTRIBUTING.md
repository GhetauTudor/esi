# Contributing to ESI

Thank you for your interest in contributing!

## Good first issues

The best places to start:

1. **`degradation` score** ([see ROADMAP](ROADMAP.md)) — implement a score that detects when a memory has been summarized or compressed, potentially losing precision.

2. **Mem0 backend** — wrap the [Mem0](https://github.com/mem0ai/mem0) memory system to return `Result` objects with confidence + freshness.

3. **Improve freshness formula** — the current exponential decay is simple. More sophisticated models (e.g., Ebbinghaus forgetting curve) are welcome.

## How to contribute

1. Fork the repo
2. Create a branch: `git checkout -b feature/your-feature`
3. Add tests for your changes
4. Run tests: `python -m pytest tests/ -v`
5. Submit a PR

## Code style

- Python 3.9+
- No external dependencies in `esi/core.py` or `esi/backends/simple.py`
- Type hints on all public functions
- Tests for all new behavior

## Questions?

Open an issue — happy to discuss ideas before you build them.
