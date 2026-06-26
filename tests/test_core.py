"""Tests for the ESI core contract and simple backend."""
import time
import pytest
from esi import EpistemicMemory, Result, SimpleMemoryBackend


def make_mem(**kwargs):
    return EpistemicMemory(backend=SimpleMemoryBackend(**kwargs))


class TestResult:
    def test_abstain_below_threshold(self):
        r = Result(answer="x", confidence=0.2, freshness=1.0)
        assert r.should_abstain(threshold=0.3)

    def test_no_abstain_above_threshold(self):
        r = Result(answer="x", confidence=0.8, freshness=1.0)
        assert not r.should_abstain(threshold=0.3)

    def test_epistemic_score_is_geometric_mean(self):
        r = Result(answer="x", confidence=0.64, freshness=1.0)
        assert abs(r.epistemic_score() - 0.8) < 0.01


class TestSimpleBackend:
    def test_fresh_memory_has_high_freshness(self):
        mem = make_mem()
        mem.add("The user prefers espresso coffee")
        result = mem.query("What coffee does the user prefer?")
        assert result.freshness > 0.9
        assert result.confidence > 0.3
        assert result.answer is not None

    def test_unknown_query_abstains(self):
        mem = make_mem()
        mem.add("The user prefers espresso coffee")
        result = mem.query("What is the capital of Mars?")
        assert result.answer is None
        assert result.confidence == 0.0

    def test_stale_memory_has_low_freshness(self):
        mem = make_mem(max_age_seconds=0.001)
        mem.add("The user prefers espresso coffee")
        time.sleep(0.05)
        result = mem.query("What coffee does the user prefer?")
        assert result.freshness < 0.5

    def test_forget_removes_memories(self):
        mem = make_mem()
        mem.add("The user prefers espresso coffee")
        removed = mem.forget("espresso coffee")
        assert removed == 1
        result = mem.query("What coffee does the user prefer?")
        assert result.answer is None

    def test_empty_memory_abstains(self):
        mem = make_mem()
        result = mem.query("anything")
        assert result.answer is None
        assert result.confidence == 0.0
