"""Benchmark: does ESI freshness track actual forgetting?

Generates the hook chart: standard memory (always confident) vs
ESI memory (confidence drops as memories age).
"""
import time
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from esi import EpistemicMemory, SimpleMemoryBackend


def run_benchmark(steps: int = 20, sleep_per_step: float = 0.05):
    """Simulate queries at increasing time after storing a memory."""
    mem = EpistemicMemory(
        backend=SimpleMemoryBackend(decay_rate=0.3, max_age_seconds=steps * sleep_per_step)
    )
    mem.add("The user prefers espresso coffee")

    times, esi_scores, baseline_scores = [], [], []

    for i in range(steps):
        time.sleep(sleep_per_step)
        result = mem.query("What coffee does the user prefer?")
        t = (i + 1) * sleep_per_step
        times.append(t)
        esi_scores.append(result.freshness)
        baseline_scores.append(1.0)  # standard memory: always 100% confident
        print(f"t={t:.2f}s | freshness={result.freshness:.3f} | answer={result.answer!r}")

    return times, esi_scores, baseline_scores


def plot_results(times, esi_scores, baseline_scores, output_path="esi_forgetting_demo.png"):
    try:
        import matplotlib.pyplot as plt
        import matplotlib
        matplotlib.use("Agg")

        fig, ax = plt.subplots(figsize=(10, 5))
        ax.plot(times, baseline_scores, "b-", linewidth=2.5,
                label="Standard memory (always 100% confident)", alpha=0.8)
        ax.plot(times, esi_scores, "orange", linewidth=2.5,
                label="ESI memory (freshness tracks forgetting)", alpha=0.9)
        ax.fill_between(times, esi_scores, baseline_scores, alpha=0.15, color="red",
                        label="Hallucination risk zone")
        ax.axhline(0.3, color="red", linestyle="--", alpha=0.5, label="Abstention threshold (0.3)")
        ax.set_xlabel("Time after storing memory (seconds)", fontsize=13)
        ax.set_ylabel("Confidence / Freshness Score", fontsize=13)
        ax.set_title("ESI: Agent Memory Epistemic State Over Time\n"
                     '"Your agent\'s memory forgets. It should know it forgot."',
                     fontsize=14, fontweight="bold")
        ax.legend(loc="upper right", fontsize=11)
        ax.set_ylim(0, 1.1)
        ax.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(output_path, dpi=150, bbox_inches="tight")
        print(f"\nChart saved → {output_path}")
    except ImportError:
        print("matplotlib not installed — skipping chart generation")


if __name__ == "__main__":
    times, esi_scores, baseline_scores = run_benchmark()
    plot_results(times, esi_scores, baseline_scores)
