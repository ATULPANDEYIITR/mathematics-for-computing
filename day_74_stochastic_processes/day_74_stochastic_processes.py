#!/usr/bin/env python3
"""
STOCHASTIC PROCESSES
Random Walks, Markov Chains, and State Transitions

Python 3.10+
Standard-library implementation.
"""

from __future__ import annotations

import json
import math
import random
import statistics
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from enum import Enum
from pathlib import Path
from typing import Optional


class ProcessError(Exception):
    """Base exception for stochastic process failures."""


class ValidationError(ProcessError):
    """Invalid stochastic process configuration."""


class AbsorbingStateError(ProcessError):
    """A simulation cannot continue from an absorbing state."""


class ProcessType(Enum):
    RANDOM_WALK = "random_walk"
    MARKOV_CHAIN = "markov_chain"


@dataclass(frozen=True)
class Transition:
    source: str
    destination: str
    probability: float


@dataclass
class SimulationResult:
    process_type: str
    initial_state: str
    final_state: str
    states_visited: list[str]
    steps: int
    absorbed: bool
    seed: Optional[int] = None

    def to_dict(self) -> dict:
        return asdict(self)


def validate_probability(value: float) -> None:
    if not math.isfinite(value) or not 0.0 <= value <= 1.0:
        raise ValidationError(
            f"Probability must be finite and between 0 and 1: {value}"
        )


class MarkovChain:
    """
    Finite-state discrete-time Markov chain.

    The transition matrix follows the Markov property:
    P(X[t+1] = j | X[t], ..., X[0]) = P(X[t+1] = j | X[t]).
    """

    def __init__(
        self,
        transitions: dict[str, dict[str, float]],
        tolerance: float = 1e-9,
    ):
        if not transitions:
            raise ValidationError("At least one state is required.")

        if not 0 < tolerance < 0.01:
            raise ValidationError("Invalid numerical tolerance.")

        self.transitions = {}
        self.states = tuple(transitions.keys())
        self.tolerance = tolerance

        for state, destinations in transitions.items():
            if not state or not isinstance(state, str):
                raise ValidationError("State names must be non-empty strings.")

            if not destinations:
                raise ValidationError(
                    f"State {state} has no outgoing transitions."
                )

            normalized = {}

            for destination, probability in destinations.items():
                if destination not in transitions:
                    raise ValidationError(
                        f"Unknown destination: {destination}"
                    )

                validate_probability(probability)
                normalized[destination] = float(probability)

            total = math.fsum(normalized.values())

            if abs(total - 1.0) > tolerance:
                raise ValidationError(
                    f"Transition probabilities for {state} sum to {total}."
                )

            self.transitions[state] = normalized

    def is_absorbing(self, state: str) -> bool:
        if state not in self.transitions:
            raise ValidationError(f"Unknown state: {state}")

        outgoing = self.transitions[state]

        return (
            len(outgoing) == 1
            and abs(outgoing.get(state, 0.0) - 1.0) <= self.tolerance
        )

    def next_state(self, current: str, rng: random.Random) -> str:
        if current not in self.transitions:
            raise ValidationError(f"Unknown state: {current}")

        choices = self.transitions[current]
        destinations = list(choices.keys())
        probabilities = list(choices.values())

        return rng.choices(
            destinations,
            weights=probabilities,
            k=1,
        )[0]

    def simulate(
        self,
        initial_state: str,
        steps: int,
        seed: Optional[int] = None,
        stop_at_absorption: bool = True,
    ) -> SimulationResult:

        if initial_state not in self.transitions:
            raise ValidationError("Initial state does not exist.")

        if not isinstance(steps, int) or isinstance(steps, bool) or steps < 0:
            raise ValidationError("Steps must be a non-negative integer.")

        rng = random.Random(seed)
        path = [initial_state]
        current = initial_state

        for _ in range(steps):
            if stop_at_absorption and self.is_absorbing(current):
                break

            current = self.next_state(current, rng)
            path.append(current)

        return SimulationResult(
            process_type=ProcessType.MARKOV_CHAIN.value,
            initial_state=initial_state,
            final_state=current,
            states_visited=path,
            steps=len(path) - 1,
            absorbed=self.is_absorbing(current),
            seed=seed,
        )

    def stationary_distribution(
        self,
        iterations: int = 10000,
        initial_distribution: Optional[dict[str, float]] = None,
    ) -> dict[str, float]:
        """
        Estimate a limiting distribution using repeated matrix-vector
        multiplication.

        This is not a proof of stationarity. Periodic or reducible chains
        may fail to converge to a unique distribution.
        """

        if iterations <= 0:
            raise ValidationError("Iterations must be positive.")

        n = len(self.states)

        if initial_distribution is None:
            distribution = {
                state: 1.0 / n for state in self.states
            }
        else:
            if set(initial_distribution) != set(self.states):
                raise ValidationError("Distribution must cover every state.")

            for probability in initial_distribution.values():
                validate_probability(probability)

            total = math.fsum(initial_distribution.values())

            if abs(total - 1.0) > self.tolerance:
                raise ValidationError("Initial distribution must sum to one.")

            distribution = dict(initial_distribution)

        for _ in range(iterations):
            updated = {state: 0.0 for state in self.states}

            for source, source_probability in distribution.items():
                for destination, transition_probability in (
                    self.transitions[source].items()
                ):
                    updated[destination] += (
                        source_probability * transition_probability
                    )

            distribution = updated

        return distribution

    def transition_matrix(self) -> list[list[float]]:
        return [
            [
                self.transitions[source].get(destination, 0.0)
                for destination in self.states
            ]
            for source in self.states
        ]


class RandomWalk:
    """
    One-dimensional random walk with optional absorbing boundaries.
    """

    def __init__(
        self,
        start: int = 0,
        up_probability: float = 0.5,
        lower_boundary: Optional[int] = None,
        upper_boundary: Optional[int] = None,
    ):
        validate_probability(up_probability)

        if (
            lower_boundary is not None
            and upper_boundary is not None
            and lower_boundary >= upper_boundary
        ):
            raise ValidationError("Lower boundary must be below upper boundary.")

        if lower_boundary is not None and start < lower_boundary:
            raise ValidationError("Starting position is below the lower boundary.")

        if upper_boundary is not None and start > upper_boundary:
            raise ValidationError("Starting position is above the upper boundary.")

        self.start = start
        self.up_probability = up_probability
        self.lower_boundary = lower_boundary
        self.upper_boundary = upper_boundary

    def is_absorbed(self, position: int) -> bool:
        return (
            position == self.lower_boundary
            or position == self.upper_boundary
        )

    def simulate(
        self,
        steps: int,
        seed: Optional[int] = None,
    ) -> SimulationResult:

        if not isinstance(steps, int) or isinstance(steps, bool) or steps < 0:
            raise ValidationError("Steps must be a non-negative integer.")

        rng = random.Random(seed)
        position = self.start
        path = [str(position)]

        for _ in range(steps):
            if self.is_absorbed(position):
                break

            position += (
                1 if rng.random() < self.up_probability else -1
            )

            path.append(str(position))

        return SimulationResult(
            process_type=ProcessType.RANDOM_WALK.value,
            initial_state=str(self.start),
            final_state=str(position),
            states_visited=path,
            steps=len(path) - 1,
            absorbed=self.is_absorbed(position),
            seed=seed,
        )


class MonteCarloAnalyzer:
    """Statistical analysis of independent stochastic experiments."""

    @staticmethod
    def estimate_absorption_probability(
        chain: MarkovChain,
        initial_state: str,
        absorbing_states: set[str],
        experiments: int = 1000,
        steps: int = 100,
        seed: int = 42,
    ) -> dict:

        if experiments <= 0 or steps < 0:
            raise ValidationError("Invalid experiment configuration.")

        if not absorbing_states:
            raise ValidationError("At least one absorbing state is required.")

        for state in absorbing_states:
            if state not in chain.states or not chain.is_absorbing(state):
                raise ValidationError(
                    f"{state} is not a valid absorbing state."
                )

        rng = random.Random(seed)
        successful = 0
        final_states = Counter()
        absorption_times = []

        for _ in range(experiments):
            experiment_seed = rng.randrange(0, 2**63)

            result = chain.simulate(
                initial_state,
                steps,
                experiment_seed,
            )

            final_states[result.final_state] += 1

            if result.final_state in absorbing_states:
                successful += 1
                absorption_times.append(result.steps)

        probability = successful / experiments

        standard_error = math.sqrt(
            probability * (1.0 - probability) / experiments
        )

        return {
            "experiments": experiments,
            "successes": successful,
            "estimated_probability": probability,
            "standard_error": standard_error,
            "approximate_95_percent_interval": [
                max(0.0, probability - 1.96 * standard_error),
                min(1.0, probability + 1.96 * standard_error),
            ],
            "mean_absorption_time": (
                statistics.mean(absorption_times)
                if absorption_times else None
            ),
            "final_state_counts": dict(final_states),
        }


def build_weather_chain() -> MarkovChain:
    return MarkovChain({
        "Sunny": {
            "Sunny": 0.70,
            "Cloudy": 0.20,
            "Rainy": 0.10,
        },
        "Cloudy": {
            "Sunny": 0.30,
            "Cloudy": 0.40,
            "Rainy": 0.30,
        },
        "Rainy": {
            "Sunny": 0.20,
            "Cloudy": 0.30,
            "Rainy": 0.50,
        },
    })


def build_absorbing_chain() -> MarkovChain:
    return MarkovChain({
        "Operational": {
            "Operational": 0.65,
            "Degraded": 0.25,
            "Failed": 0.10,
        },
        "Degraded": {
            "Operational": 0.30,
            "Degraded": 0.40,
            "Failed": 0.30,
        },
        "Failed": {
            "Failed": 1.0,
        },
    })


def save_results(results: dict, filename: str = "stochastic_results.json") -> None:
    path = Path(filename)

    # Restrict output to a filename in the current working directory.
    if path.name != filename or path.is_absolute():
        raise ValidationError("Output must be a simple filename.")

    with path.open("w", encoding="utf-8") as file:
        json.dump(results, file, indent=2, allow_nan=False)


def run_demonstration() -> dict:
    print("=" * 65)
    print("STOCHASTIC PROCESSES LABORATORY")
    print("=" * 65)

    weather = build_weather_chain()

    weather_result = weather.simulate(
        initial_state="Sunny",
        steps=15,
        seed=42,
    )

    print("\n1. WEATHER MARKOV CHAIN")
    print("Transition matrix:", weather.transition_matrix())
    print("Observed path:", " -> ".join(weather_result.states_visited))
    print("Final state:", weather_result.final_state)

    print("\nEstimated limiting distribution:")
    limiting_distribution = weather.stationary_distribution(20000)

    for state, probability in limiting_distribution.items():
        print(f"{state}: {probability:.5f}")

    random_walk = RandomWalk(
        start=0,
        up_probability=0.55,
        lower_boundary=-5,
        upper_boundary=5,
    )

    walk_result = random_walk.simulate(
        steps=100,
        seed=42,
    )

    print("\n2. ABSORBING RANDOM WALK")
    print("Path:", " -> ".join(walk_result.states_visited))
    print("Final position:", walk_result.final_state)
    print("Absorbed:", walk_result.absorbed)

    reliability_chain = build_absorbing_chain()

    analysis = MonteCarloAnalyzer.estimate_absorption_probability(
        chain=reliability_chain,
        initial_state="Operational",
        absorbing_states={"Failed"},
        experiments=5000,
        steps=100,
        seed=12345,
    )

    print("\n3. MONTE CARLO RELIABILITY ANALYSIS")

    for key, value in analysis.items():
        print(f"{key}: {value}")

    results = {
        "weather_simulation": weather_result.to_dict(),
        "stationary_distribution": limiting_distribution,
        "random_walk": walk_result.to_dict(),
        "reliability_analysis": analysis,
    }

    save_results(results)

    print("\nResults saved to stochastic_results.json")

    return results


def run_tests() -> None:
    chain = MarkovChain({
        "A": {"A": 0.5, "B": 0.5},
        "B": {"A": 0.25, "B": 0.75},
    })

    first = chain.simulate("A", 20, seed=10)
    second = chain.simulate("A", 20, seed=10)

    assert first.states_visited == second.states_visited
    assert first.steps == 20

    walk = RandomWalk(
        start=0,
        up_probability=1.0,
        lower_boundary=-2,
        upper_boundary=2,
    )

    result = walk.simulate(10, seed=1)

    assert result.final_state == "2"
    assert result.absorbed

    try:
        MarkovChain({
            "A": {"A": 0.7, "B": 0.7},
            "B": {"B": 1.0},
        })
    except ValidationError:
        pass
    else:
        raise AssertionError("Invalid probabilities were accepted.")

    assert math.isclose(
        chain.stationary_distribution(10000)["A"],
        1 / 3,
        abs_tol=1e-5,
    )

    print("\nAll validation tests passed.")


if __name__ == "__main__":
    run_tests()
    run_demonstration()
