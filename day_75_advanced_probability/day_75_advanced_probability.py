#!/usr/bin/env python3
"""
Advanced Probability
Topics:
- Discrete-time stochastic processes
- Markov chains and transition matrices
- Stationary distributions
- Irreducibility and periodicity
- Ergodicity and long-run convergence
- Martingales and conditional expectations
- Stochastic simulation and empirical estimation

Python 3.10+
Standard library only.
"""

from __future__ import annotations

import math
import random
import statistics
from collections import Counter
from dataclasses import dataclass
from enum import Enum
from typing import Callable, Sequence


# ============================================================
# 1. DOMAIN TYPES AND VALIDATION
# ============================================================

class ProbabilityError(ValueError):
    """Raised when a probability model is invalid."""


class ChainClassification(Enum):
    ERGODIC = "ergodic"
    IRREDUCIBLE_PERIODIC = "irreducible_periodic"
    REDUCIBLE = "reducible"


@dataclass(frozen=True)
class SimulationResult:
    states: tuple[int, ...]
    empirical_distribution: tuple[float, ...]
    transition_counts: dict[tuple[int, int], int]


@dataclass(frozen=True)
class StationaryResult:
    distribution: tuple[float, ...]
    iterations: int
    converged: bool
    residual: float


def validate_probability(value: float) -> None:
    if not math.isfinite(value) or not 0.0 <= value <= 1.0:
        raise ProbabilityError(f"Invalid probability: {value}")


# ============================================================
# 2. DISCRETE PROBABILITY DISTRIBUTIONS
# ============================================================

def normalize_weights(weights: Sequence[float]) -> list[float]:
    if not weights:
        raise ProbabilityError("Weights cannot be empty.")

    if any(not math.isfinite(x) or x < 0 for x in weights):
        raise ProbabilityError("Weights must be finite and nonnegative.")

    total = math.fsum(weights)

    if total <= 0:
        raise ProbabilityError("At least one weight must be positive.")

    return [x / total for x in weights]


def categorical_sample(
    probabilities: Sequence[float],
    rng: random.Random
) -> int:
    cumulative = 0.0
    value = rng.random()

    for index, probability in enumerate(probabilities):
        cumulative += probability

        if value < cumulative:
            return index

    return len(probabilities) - 1


def expectation(
    values: Sequence[float],
    probabilities: Sequence[float]
) -> float:
    if len(values) != len(probabilities):
        raise ProbabilityError("Values and probabilities must match.")

    return math.fsum(
        value * probability
        for value, probability in zip(values, probabilities)
    )


def variance(
    values: Sequence[float],
    probabilities: Sequence[float]
) -> float:
    mean = expectation(values, probabilities)

    return math.fsum(
        probability * (value - mean) ** 2
        for value, probability in zip(values, probabilities)
    )


# ============================================================
# 3. FINITE-STATE MARKOV CHAIN
# ============================================================

class MarkovChain:
    def __init__(
        self,
        transition_matrix: Sequence[Sequence[float]],
        labels: Sequence[str] | None = None
    ):
        self.matrix = tuple(
            tuple(float(x) for x in row)
            for row in transition_matrix
        )

        self.n = len(self.matrix)

        if self.n == 0:
            raise ProbabilityError("A chain must contain states.")

        if any(len(row) != self.n for row in self.matrix):
            raise ProbabilityError("Transition matrix must be square.")

        for i, row in enumerate(self.matrix):
            if any(
                not math.isfinite(x) or x < 0 or x > 1
                for x in row
            ):
                raise ProbabilityError(
                    f"Invalid transition probability in row {i}."
                )

            if not math.isclose(
                math.fsum(row), 1.0, abs_tol=1e-10
            ):
                raise ProbabilityError(
                    f"Transition probabilities in row {i} "
                    "must sum to one."
                )

        self.labels = tuple(
            labels if labels is not None
            else [f"State-{i}" for i in range(self.n)]
        )

        if len(self.labels) != self.n:
            raise ProbabilityError("State labels do not match matrix.")

        if len(set(self.labels)) != self.n:
            raise ProbabilityError("State labels must be unique.")

    def transition(self, state: int, rng: random.Random) -> int:
        self._validate_state(state)
        return categorical_sample(self.matrix[state], rng)

    def _validate_state(self, state: int) -> None:
        if not isinstance(state, int) or not 0 <= state < self.n:
            raise ProbabilityError(f"Unknown state: {state}")

    def distribution_after(
        self,
        initial: Sequence[float],
        steps: int
    ) -> tuple[float, ...]:
        if steps < 0:
            raise ProbabilityError("Steps cannot be negative.")

        distribution = normalize_weights(initial)

        if len(distribution) != self.n:
            raise ProbabilityError("Initial distribution size mismatch.")

        for _ in range(steps):
            distribution = [
                math.fsum(
                    distribution[i] * self.matrix[i][j]
                    for i in range(self.n)
                )
                for j in range(self.n)
            ]

        return tuple(distribution)

    def simulate(
        self,
        initial_state: int,
        steps: int,
        seed: int = 42
    ) -> SimulationResult:
        self._validate_state(initial_state)

        if steps < 0:
            raise ProbabilityError("Steps cannot be negative.")

        rng = random.Random(seed)
        path = [initial_state]
        counts = Counter()

        current = initial_state

        for _ in range(steps):
            following = self.transition(current, rng)
            counts[(current, following)] += 1
            path.append(following)
            current = following

        visits = Counter(path)
        total = len(path)

        empirical = tuple(
            visits[i] / total for i in range(self.n)
        )

        return SimulationResult(
            tuple(path),
            empirical,
            dict(counts)
        )

    # --------------------------------------------------------
    # 4. GRAPH-BASED CHAIN CLASSIFICATION
    # --------------------------------------------------------

    def reachable(self, start: int) -> set[int]:
        self._validate_state(start)

        visited = {start}
        stack = [start]

        while stack:
            current = stack.pop()

            for destination, probability in enumerate(
                self.matrix[current]
            ):
                if probability > 0 and destination not in visited:
                    visited.add(destination)
                    stack.append(destination)

        return visited

    def is_irreducible(self) -> bool:
        return all(
            len(self.reachable(state)) == self.n
            for state in range(self.n)
        )

    def period(self, state: int = 0) -> int:
        """
        Calculate the period using graph-distance differences.

        The GCD of d(u) + 1 - d(v) over all positive
        transitions u -> v gives the communicating-class period.
        """
        self._validate_state(state)

        distances = {state: 0}
        queue = [state]

        for current in queue:
            for destination, probability in enumerate(
                self.matrix[current]
            ):
                if probability > 0 and destination not in distances:
                    distances[destination] = distances[current] + 1
                    queue.append(destination)

        if len(distances) != self.n:
            raise ProbabilityError(
                "Period calculation requires an irreducible chain."
            )

        result = 0

        for source in range(self.n):
            for destination, probability in enumerate(
                self.matrix[source]
            ):
                if probability > 0:
                    difference = (
                        distances[source] + 1 - distances[destination]
                    )
                    result = math.gcd(result, abs(difference))

        return result

    def classify(self) -> ChainClassification:
        if not self.is_irreducible():
            return ChainClassification.REDUCIBLE

        if self.period() == 1:
            return ChainClassification.ERGODIC

        return ChainClassification.IRREDUCIBLE_PERIODIC

    # --------------------------------------------------------
    # 5. STATIONARY DISTRIBUTION
    # --------------------------------------------------------

    def stationary_distribution(
        self,
        tolerance: float = 1e-12,
        max_iterations: int = 100_000
    ) -> StationaryResult:
        """
        Solve pi P = pi through power iteration.

        The initial distribution is uniform.
        Power iteration is not guaranteed to converge for
        periodic chains. Such cases are reported explicitly.
        """
        if tolerance <= 0 or not math.isfinite(tolerance):
            raise ProbabilityError("Tolerance must be positive.")

        if max_iterations <= 0:
            raise ProbabilityError("Iteration limit must be positive.")

        distribution = [1.0 / self.n] * self.n

        for iteration in range(1, max_iterations + 1):
            following = [
                math.fsum(
                    distribution[i] * self.matrix[i][j]
                    for i in range(self.n)
                )
                for j in range(self.n)
            ]

            residual = max(
                abs(following[i] - distribution[i])
                for i in range(self.n)
            )

            distribution = following

            if residual < tolerance:
                return StationaryResult(
                    tuple(distribution),
                    iteration,
                    True,
                    residual
                )

        residual = max(
            abs(
                math.fsum(
                    distribution[i] * self.matrix[i][j]
                    for i in range(self.n)
                ) - distribution[j]
            )
            for j in range(self.n)
        )

        return StationaryResult(
            tuple(distribution),
            max_iterations,
            False,
            residual
        )


# ============================================================
# 6. MARTINGALE MODEL
# ============================================================

class MartingaleAnalyzer:
    """
    Construct a martingale from transition-dependent rewards.

    Let R(X_n, X_(n+1)) be a reward.

    Define:
        g(i) = E[R(X_n, X_(n+1)) | X_n = i]

    Then:
        M_n = sum(k=0 to n-1) [R_k - g(X_k)]

    satisfies E[M_(n+1) | F_n] = M_n.
    """

    def __init__(
        self,
        chain: MarkovChain,
        reward: Callable[[int, int], float]
    ):
        self.chain = chain
        self.reward = reward

        self.conditional_means = tuple(
            math.fsum(
                probability * reward(state, destination)
                for destination, probability in enumerate(
                    chain.matrix[state]
                )
            )
            for state in range(chain.n)
        )

    def analyze(
        self,
        path: Sequence[int]
    ) -> dict[str, object]:
        if len(path) < 2:
            raise ProbabilityError("Path must contain at least two states.")

        cumulative = [0.0]
        residuals = []

        for index in range(len(path) - 1):
            current = path[index]
            following = path[index + 1]

            self.chain._validate_state(current)
            self.chain._validate_state(following)

            observed = self.reward(current, following)
            expected = self.conditional_means[current]

            increment = observed - expected

            residuals.append(increment)
            cumulative.append(cumulative[-1] + increment)

        return {
            "martingale_values": tuple(cumulative),
            "increments": tuple(residuals),
            "terminal_value": cumulative[-1],
            "mean_increment": statistics.fmean(residuals)
        }


# ============================================================
# 7. ERGODIC LONG-RUN ANALYSIS
# ============================================================

def long_run_reward(
    stationary: Sequence[float],
    state_rewards: Sequence[float]
) -> float:
    if len(stationary) != len(state_rewards):
        raise ProbabilityError("Reward vector size mismatch.")

    return expectation(state_rewards, stationary)


def compare_distributions(
    theoretical: Sequence[float],
    empirical: Sequence[float]
) -> dict[str, float]:
    if len(theoretical) != len(empirical):
        raise ProbabilityError("Distribution sizes differ.")

    errors = [
        abs(a - b) for a, b in zip(theoretical, empirical)
    ]

    return {
        "maximum_absolute_error": max(errors),
        "total_variation_distance": 0.5 * math.fsum(errors)
    }


# ============================================================
# 8. EXECUTABLE STOCHASTIC EXPERIMENT
# ============================================================

def main() -> None:
    print("=" * 65)
    print("ADVANCED PROBABILITY: MARKOV CHAINS AND MARTINGALES")
    print("=" * 65)

    # A three-state weather process.
    chain = MarkovChain(
        [
            [0.70, 0.20, 0.10],
            [0.25, 0.50, 0.25],
            [0.20, 0.30, 0.50]
        ],
        labels=["Sunny", "Cloudy", "Rainy"]
    )

    print("\n1. TRANSITION MATRIX")

    for label, row in zip(chain.labels, chain.matrix):
        print(f"{label:10}: {row}")

    # Basic probability calculations.
    print("\n2. PROBABILITY CALCULATIONS")

    probabilities = [0.2, 0.5, 0.3]
    values = [10, 20, 50]

    print("Expected value:", expectation(values, probabilities))
    print("Variance:", variance(values, probabilities))

    # Classification.
    print("\n3. ERGODICITY")

    classification = chain.classify()

    print("Classification:", classification.value)
    print("Irreducible:", chain.is_irreducible())
    print("Period:", chain.period())

    # Stationary distribution.
    print("\n4. STATIONARY DISTRIBUTION")

    stationary = chain.stationary_distribution()

    print("Distribution:", stationary.distribution)
    print("Converged:", stationary.converged)
    print("Iterations:", stationary.iterations)
    print("Residual:", stationary.residual)

    if not stationary.converged:
        raise RuntimeError("Stationary iteration did not converge.")

    # Theoretical long-run reward.
    rewards = [100.0, 60.0, 20.0]

    average_reward = long_run_reward(
        stationary.distribution,
        rewards
    )

    print("\n5. LONG-RUN REWARD")
    print("Expected long-run reward:", average_reward)

    # Simulate a long trajectory.
    print("\n6. STOCHASTIC SIMULATION")

    result = chain.simulate(
        initial_state=0,
        steps=100_000,
        seed=2026
    )

    print("Simulated transitions:", len(result.states) - 1)

    print("\nEmpirical distribution:")

    for label, probability in zip(
        chain.labels,
        result.empirical_distribution
    ):
        print(f"{label:10}: {probability:.6f}")

    errors = compare_distributions(
        stationary.distribution,
        result.empirical_distribution
    )

    print("Maximum error:", errors["maximum_absolute_error"])
    print("Total variation distance:",
          errors["total_variation_distance"])

    # Reward depends on the transition itself.
    def reward(source: int, destination: int) -> float:
        return float(destination - source)

    analyzer = MartingaleAnalyzer(chain, reward)

    short_path = result.states[:101]
    martingale = analyzer.analyze(short_path)

    print("\n7. MARTINGALE ANALYSIS")

    print("Conditional reward means:",
          analyzer.conditional_means)

    print("First 10 increments:",
          martingale["increments"][:10])

    print("Terminal martingale value:",
          martingale["terminal_value"])

    print("Sample mean increment:",
          martingale["mean_increment"])

    # Verify the conditional expectation algebraically.
    for state in range(chain.n):
        expected_increment = math.fsum(
            chain.matrix[state][destination] *
            (
                reward(state, destination)
                - analyzer.conditional_means[state]
            )
            for destination in range(chain.n)
        )

        assert abs(expected_increment) < 1e-10

    print("Conditional martingale identities: VERIFIED")

    # Periodic-chain edge case.
    periodic = MarkovChain([
        [0.0, 1.0],
        [1.0, 0.0]
    ])

    periodic_result = periodic.stationary_distribution(
        max_iterations=100
    )

    print("\n8. PERIODIC CHAIN EDGE CASE")
    print("Period:", periodic.period())
    print("Classification:", periodic.classify().value)
    print("Power iteration converged:",
          periodic_result.converged)

    # Reducible-chain edge case.
    reducible = MarkovChain([
        [0.8, 0.2],
        [0.0, 1.0]
    ])

    print("\n9. REDUCIBLE CHAIN EDGE CASE")
    print("Classification:", reducible.classify().value)

    print("\n10. VALIDATION")

    try:
        MarkovChain([
            [0.4, 0.4],
            [0.2, 0.9]
        ])
    except ProbabilityError as error:
        print("Invalid matrix correctly rejected:", error)

    print("\nExperiment completed successfully.")


if __name__ == "__main__":
    main()
