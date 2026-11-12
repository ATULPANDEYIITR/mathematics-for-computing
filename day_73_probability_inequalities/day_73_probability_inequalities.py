#!/usr/bin/env python3
"""
Probability Inequalities: Markov, Chebyshev, Jensen, and Chernoff Bounds.

A self-contained implementation of probability bounds using finite
discrete distributions and moment-generating functions.

Python 3.10+
Standard library only.
"""

from __future__ import annotations

import math
import random
import unittest
from dataclasses import dataclass
from enum import Enum
from typing import Callable, Iterable, Sequence


class ProbabilityError(ValueError):
    """Raised when a probability model or bound is invalid."""


class BoundType(Enum):
    MARKOV = "Markov"
    CHEBYSHEV = "Chebyshev"
    JENSEN = "Jensen"
    CHERNOFF = "Chernoff"


@dataclass(frozen=True)
class DiscreteDistribution:
    """Finite discrete probability distribution."""

    values: tuple[float, ...]
    probabilities: tuple[float, ...]

    def __post_init__(self) -> None:
        if not self.values:
            raise ProbabilityError("Distribution cannot be empty.")

        if len(self.values) != len(self.probabilities):
            raise ProbabilityError("Values and probabilities must match.")

        if not all(math.isfinite(x) for x in self.values):
            raise ProbabilityError("Values must be finite.")

        if not all(
            math.isfinite(p) and p >= 0
            for p in self.probabilities
        ):
            raise ProbabilityError("Probabilities must be finite and nonnegative.")

        if not math.isclose(
            sum(self.probabilities), 1.0, rel_tol=1e-10, abs_tol=1e-10
        ):
            raise ProbabilityError("Probabilities must sum to one.")

    @classmethod
    def from_pairs(
        cls, pairs: Iterable[tuple[float, float]]
    ) -> "DiscreteDistribution":
        data = list(pairs)
        return cls(
            tuple(float(x) for x, _ in data),
            tuple(float(p) for _, p in data),
        )

    def expectation(
        self, function: Callable[[float], float] = lambda x: x
    ) -> float:
        result = sum(
            p * function(x)
            for x, p in zip(self.values, self.probabilities)
        )
        if not math.isfinite(result):
            raise ProbabilityError("Expectation is not finite.")
        return result

    @property
    def mean(self) -> float:
        return self.expectation()

    @property
    def variance(self) -> float:
        mu = self.mean
        return sum(
            p * (x - mu) ** 2
            for x, p in zip(self.values, self.probabilities)
        )

    @property
    def standard_deviation(self) -> float:
        return math.sqrt(self.variance)

    def probability(self, predicate: Callable[[float], bool]) -> float:
        return sum(
            p
            for x, p in zip(self.values, self.probabilities)
            if predicate(x)
        )

    def sample(self, count: int, seed: int = 42) -> list[float]:
        if count <= 0:
            raise ProbabilityError("Sample count must be positive.")

        rng = random.Random(seed)
        return rng.choices(
            self.values,
            weights=self.probabilities,
            k=count,
        )


def validate_nonnegative_expectation(
    distribution: DiscreteDistribution,
) -> None:
    if any(x < 0 for x in distribution.values):
        raise ProbabilityError(
            "The random variable must be nonnegative."
        )


def markov_bound(
    distribution: DiscreteDistribution,
    threshold: float,
) -> float:
    """
    P(X >= a) <= E[X] / a, for X >= 0 and a > 0.
    """
    validate_nonnegative_expectation(distribution)

    if not math.isfinite(threshold) or threshold <= 0:
        raise ProbabilityError("Threshold must be positive and finite.")

    return min(1.0, distribution.mean / threshold)


def chebyshev_bound(
    distribution: DiscreteDistribution,
    deviation: float,
) -> float:
    """
    P(|X - E[X]| >= t) <= Var(X) / t^2.
    """
    if not math.isfinite(deviation) or deviation <= 0:
        raise ProbabilityError("Deviation must be positive and finite.")

    return min(1.0, distribution.variance / deviation**2)


def jensen_inequality(
    distribution: DiscreteDistribution,
    convex_function: Callable[[float], float],
) -> dict[str, float]:
    """
    For a convex function:
        f(E[X]) <= E[f(X)].

    Convexity is a mathematical precondition supplied by the caller.
    """
    left = convex_function(distribution.mean)
    right = distribution.expectation(convex_function)

    if not math.isfinite(left) or not math.isfinite(right):
        raise ProbabilityError("Function produced a non-finite result.")

    return {
        "function_at_mean": left,
        "mean_of_function": right,
        "difference": right - left,
        "inequality_holds": float(left <= right + 1e-10),
    }


def log_sum_exp(values: Sequence[float]) -> float:
    """Numerically stable logarithm of a sum of exponentials."""
    if not values:
        raise ProbabilityError("Cannot calculate log-sum-exp of empty data.")

    maximum = max(values)

    if maximum == -math.inf:
        return -math.inf

    return maximum + math.log(
        sum(math.exp(value - maximum) for value in values)
    )


def log_mgf(
    distribution: DiscreteDistribution,
    parameter: float,
) -> float:
    """
    Calculate log(E[e^(lambda X)]) using a stable log-sum-exp.
    """
    if not math.isfinite(parameter):
        raise ProbabilityError("MGF parameter must be finite.")

    terms = [
        math.log(p) + parameter * x
        for x, p in zip(distribution.values, distribution.probabilities)
        if p > 0
    ]

    result = log_sum_exp(terms)

    if not math.isfinite(result):
        raise ProbabilityError("MGF calculation is not finite.")

    return result


@dataclass(frozen=True)
class ChernoffResult:
    threshold: float
    bound: float
    optimal_parameter: float
    exact_probability: float


def chernoff_bound(
    distribution: DiscreteDistribution,
    threshold: float,
    parameter_max: float = 20.0,
    steps: int = 2000,
) -> ChernoffResult:
    """
    Upper-tail Chernoff bound:

        P(X >= a) <= inf(lambda >= 0)
                      exp(log M_X(lambda) - lambda*a).

    A bounded numerical grid approximates the infimum.
    This is valid for any finite distribution with a finite MGF.
    """
    if not math.isfinite(threshold):
        raise ProbabilityError("Threshold must be finite.")

    if not math.isfinite(parameter_max) or parameter_max <= 0:
        raise ProbabilityError("Parameter maximum must be positive.")

    if steps < 1:
        raise ProbabilityError("Steps must be positive.")

    best_bound = 1.0
    best_parameter = 0.0

    for index in range(steps + 1):
        parameter = parameter_max * index / steps

        exponent = (
            log_mgf(distribution, parameter)
            - parameter * threshold
        )

        bound = 0.0 if exponent < -745 else min(1.0, math.exp(exponent))

        if bound < best_bound:
            best_bound = bound
            best_parameter = parameter

    exact = distribution.probability(lambda x: x >= threshold)

    return ChernoffResult(
        threshold=threshold,
        bound=best_bound,
        optimal_parameter=best_parameter,
        exact_probability=exact,
    )


def bernoulli_sum_distribution(
    trials: int,
    success_probability: float,
) -> DiscreteDistribution:
    """
    Exact finite distribution of a sum of independent,
    identically distributed Bernoulli random variables.
    """
    if trials < 0:
        raise ProbabilityError("Number of trials cannot be negative.")

    if trials > 1000:
        raise ProbabilityError("Use at most 1000 trials for this example.")

    if not 0 <= success_probability <= 1:
        raise ProbabilityError("Success probability must be in [0, 1].")

    probabilities = []

    for k in range(trials + 1):
        probability = (
            math.comb(trials, k)
            * success_probability**k
            * (1 - success_probability) ** (trials - k)
        )
        probabilities.append(probability)

    return DiscreteDistribution(
        tuple(float(k) for k in range(trials + 1)),
        tuple(probabilities),
    )


def empirical_probability(
    observations: Sequence[float],
    predicate: Callable[[float], bool],
) -> float:
    if not observations:
        raise ProbabilityError("Observations cannot be empty.")

    return sum(predicate(x) for x in observations) / len(observations)


def run_tests() -> None:
    distribution = DiscreteDistribution(
        values=(0, 1, 2, 3, 4),
        probabilities=(0.1, 0.2, 0.4, 0.2, 0.1),
    )

    assert math.isclose(distribution.mean, 2.0)
    assert math.isclose(distribution.variance, 1.4)

    assert markov_bound(distribution, 3) >= distribution.probability(
        lambda x: x >= 3
    )

    assert chebyshev_bound(distribution, 1) >= distribution.probability(
        lambda x: abs(x - distribution.mean) >= 1
    )

    jensen = jensen_inequality(distribution, lambda x: x**2)
    assert jensen["inequality_holds"] == 1.0

    binomial = bernoulli_sum_distribution(20, 0.5)
    result = chernoff_bound(binomial, 15)

    assert result.bound >= result.exact_probability - 1e-10

    try:
        markov_bound(distribution, -1)
        raise AssertionError("Invalid threshold was accepted.")
    except ProbabilityError:
        pass

    try:
        DiscreteDistribution((1, 2), (0.4, 0.4))
        raise AssertionError("Invalid probabilities were accepted.")
    except ProbabilityError:
        pass

    print("All probability inequality tests passed.")


def main() -> None:
    run_tests()

    distribution = DiscreteDistribution(
        values=(0, 1, 2, 3, 4, 5),
        probabilities=(0.05, 0.10, 0.20, 0.30, 0.20, 0.15),
    )

    threshold = 4.0
    deviation = 2.0

    print("\nDISCRETE DISTRIBUTION ANALYSIS")
    print(f"Mean: {distribution.mean:.4f}")
    print(f"Variance: {distribution.variance:.4f}")
    print(f"Standard deviation: {distribution.standard_deviation:.4f}")

    exact_upper = distribution.probability(
        lambda x: x >= threshold
    )

    print("\nMARKOV INEQUALITY")
    print(f"Threshold: {threshold}")
    print(f"Upper bound: {markov_bound(distribution, threshold):.6f}")
    print(f"Exact probability: {exact_upper:.6f}")

    print("\nCHEBYSHEV INEQUALITY")
    print(
        f"Upper bound: {chebyshev_bound(distribution, deviation):.6f}"
    )
    print(
        "Exact probability: "
        f"{distribution.probability(lambda x: abs(x - distribution.mean) >= deviation):.6f}"
    )

    print("\nJENSEN INEQUALITY")
    result = jensen_inequality(distribution, lambda x: x**2)
    for key, value in result.items():
        print(f"{key}: {value}")

    print("\nCHERNOFF INEQUALITY")
    binomial = bernoulli_sum_distribution(30, 0.5)
    result = chernoff_bound(binomial, 20)

    print(f"Threshold: {result.threshold}")
    print(f"Optimized parameter: {result.optimal_parameter:.6f}")
    print(f"Chernoff upper bound: {result.bound:.8f}")
    print(f"Exact probability: {result.exact_probability:.8f}")

    observations = distribution.sample(10000)
    observed = empirical_probability(
        observations,
        lambda x: x >= threshold,
    )

    print("\nMONTE CARLO VALIDATION")
    print(f"Empirical probability: {observed:.6f}")
    print(f"Theoretical probability: {exact_upper:.6f}")


if __name__ == "__main__":
    main()
