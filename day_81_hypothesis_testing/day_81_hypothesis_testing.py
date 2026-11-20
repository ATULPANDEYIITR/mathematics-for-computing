#!/usr/bin/env python3
"""
HYPOTHESIS TESTING
Null hypothesis, alternative hypothesis, p-values and statistical significance.

Implements:
- One-sample Z-test
- Two-tailed and one-tailed hypothesis tests
- P-value calculation
- Significance-level evaluation
- Confidence intervals
- Type I and Type II error concepts
- Multiple-testing correction using Bonferroni
- Reproducible simulations
- Input validation and unit tests

Python standard library only.
"""

from __future__ import annotations

import math
import random
import statistics
from dataclasses import dataclass
from enum import Enum
from typing import Sequence


class Alternative(Enum):
    TWO_SIDED = "two-sided"
    GREATER = "greater"
    LESS = "less"


class Decision(Enum):
    REJECT_NULL = "Reject the null hypothesis"
    FAIL_TO_REJECT = "Fail to reject the null hypothesis"


@dataclass(frozen=True)
class Hypothesis:
    null_mean: float
    alternative: Alternative
    alpha: float = 0.05

    def __post_init__(self):
        if not math.isfinite(self.null_mean):
            raise ValueError("Null mean must be finite.")

        if not 0 < self.alpha < 1:
            raise ValueError("Significance level must be between 0 and 1.")


@dataclass(frozen=True)
class TestResult:
    sample_size: int
    sample_mean: float
    population_sigma: float
    standard_error: float
    z_statistic: float
    p_value: float
    alpha: float
    confidence_interval: tuple[float, float]
    decision: Decision
    alternative: Alternative

    def display(self) -> None:
        print("\nHYPOTHESIS TEST RESULTS")
        print("-" * 55)
        print(f"Sample size:          {self.sample_size}")
        print(f"Sample mean:          {self.sample_mean:.4f}")
        print(f"Population sigma:     {self.population_sigma:.4f}")
        print(f"Standard error:       {self.standard_error:.4f}")
        print(f"Z statistic:          {self.z_statistic:.4f}")
        print(f"P-value:              {self.p_value:.6f}")
        print(f"Significance level:   {self.alpha}")
        print(
            f"Confidence interval:  "
            f"({self.confidence_interval[0]:.4f}, "
            f"{self.confidence_interval[1]:.4f})"
        )
        print(f"Alternative:          {self.alternative.value}")
        print(f"Decision:             {self.decision.value}")

        print("\nInterpretation:")
        if self.decision == Decision.REJECT_NULL:
            print(
                "The observed evidence is statistically significant "
                "at the selected significance level."
            )
        else:
            print(
                "The observed evidence is insufficient to reject "
                "the null hypothesis."
            )


def normal_cdf(z: float) -> float:
    """Cumulative distribution function of the standard normal."""
    return 0.5 * (1.0 + math.erf(z / math.sqrt(2.0)))


def normal_survival(z: float) -> float:
    """Numerically stable upper-tail probability."""
    return 0.5 * math.erfc(z / math.sqrt(2.0))


def calculate_p_value(
    z: float,
    alternative: Alternative
) -> float:
    """Calculate the p-value for a standard normal test statistic."""

    if alternative == Alternative.TWO_SIDED:
        return min(1.0, math.erfc(abs(z) / math.sqrt(2.0)))

    if alternative == Alternative.GREATER:
        return normal_survival(z)

    if alternative == Alternative.LESS:
        return normal_cdf(z)

    raise ValueError("Unsupported alternative hypothesis.")


def critical_z(alpha: float, alternative: Alternative) -> float:
    """Find the positive standard-normal critical value."""

    low, high = 0.0, 10.0
    target = alpha / 2 if alternative == Alternative.TWO_SIDED else alpha

    for _ in range(100):
        mid = (low + high) / 2

        if normal_survival(mid) > target:
            low = mid
        else:
            high = mid

    return (low + high) / 2


def one_sample_z_test(
    observations: Sequence[float],
    hypothesis: Hypothesis,
    population_sigma: float
) -> TestResult:
    """
    Perform a one-sample Z-test when population standard deviation
    is known and observations are independent.
    """

    if len(observations) < 2:
        raise ValueError("At least two observations are required.")

    if not math.isfinite(population_sigma) or population_sigma <= 0:
        raise ValueError("Population standard deviation must be positive.")

    if any(not math.isfinite(x) for x in observations):
        raise ValueError("Observations must contain finite numbers.")

    n = len(observations)
    sample_mean = statistics.fmean(observations)

    standard_error = population_sigma / math.sqrt(n)

    z = (
        sample_mean - hypothesis.null_mean
    ) / standard_error

    p_value = calculate_p_value(z, hypothesis.alternative)

    decision = (
        Decision.REJECT_NULL
        if p_value <= hypothesis.alpha
        else Decision.FAIL_TO_REJECT
    )

    # The confidence interval uses the matching two-sided confidence level.
    z_critical = critical_z(
        hypothesis.alpha,
        Alternative.TWO_SIDED
    )

    margin = z_critical * standard_error

    return TestResult(
        sample_size=n,
        sample_mean=sample_mean,
        population_sigma=population_sigma,
        standard_error=standard_error,
        z_statistic=z,
        p_value=p_value,
        alpha=hypothesis.alpha,
        confidence_interval=(
            sample_mean - margin,
            sample_mean + margin
        ),
        decision=decision,
        alternative=hypothesis.alternative
    )


def bonferroni_correction(
    p_values: Sequence[float],
    alpha: float
) -> list[dict]:
    """Control family-wise error across multiple hypothesis tests."""

    if not p_values:
        raise ValueError("At least one p-value is required.")

    if not 0 < alpha < 1:
        raise ValueError("Alpha must be between 0 and 1.")

    if any(not math.isfinite(p) or not 0 <= p <= 1 for p in p_values):
        raise ValueError("P-values must be finite and between 0 and 1.")

    adjusted_alpha = alpha / len(p_values)

    return [
        {
            "original_p": p,
            "adjusted_p": min(1.0, p * len(p_values)),
            "reject": p <= adjusted_alpha
        }
        for p in p_values
    ]


def simulate_null_distribution(
    sample_size: int = 30,
    repetitions: int = 5000,
    alpha: float = 0.05,
    seed: int = 42
) -> dict:
    """
    Simulate the Type I error rate under a true null hypothesis.
    """

    if sample_size < 2 or repetitions < 1:
        raise ValueError("Invalid simulation dimensions.")

    if not 0 < alpha < 1:
        raise ValueError("Invalid significance level.")

    rng = random.Random(seed)
    rejected = 0

    for _ in range(repetitions):
        sample = [
            rng.gauss(100, 15)
            for _ in range(sample_size)
        ]

        hypothesis = Hypothesis(
            null_mean=100,
            alternative=Alternative.TWO_SIDED,
            alpha=alpha
        )

        result = one_sample_z_test(
            sample,
            hypothesis,
            population_sigma=15
        )

        if result.decision == Decision.REJECT_NULL:
            rejected += 1

    return {
        "repetitions": repetitions,
        "rejections": rejected,
        "estimated_type_i_error": rejected / repetitions,
        "theoretical_alpha": alpha
    }


def calculate_sample_size(
    sigma: float,
    minimum_detectable_effect: float,
    alpha: float = 0.05,
    power: float = 0.80
) -> int:
    """
    Approximate sample size for a two-sided one-sample Z-test.

    Uses a numerical approximation for normal quantiles.
    """

    if sigma <= 0 or minimum_detectable_effect <= 0:
        raise ValueError("Sigma and effect size must be positive.")

    if not 0 < alpha < 1 or not 0 < power < 1:
        raise ValueError("Alpha and power must be between 0 and 1.")

    z_alpha = critical_z(alpha, Alternative.TWO_SIDED)
    z_power = critical_z(1 - power, Alternative.GREATER)

    n = (
        sigma * (z_alpha + z_power)
        / minimum_detectable_effect
    ) ** 2

    return math.ceil(n)


def run_tests() -> None:
    """Verify important statistical and validation behavior."""

    assert abs(normal_cdf(0) - 0.5) < 1e-10
    assert abs(normal_survival(0) - 0.5) < 1e-10

    assert abs(
        calculate_p_value(0, Alternative.TWO_SIDED) - 1
    ) < 1e-10

    assert calculate_p_value(
        2.0, Alternative.GREATER
    ) < 0.03

    assert calculate_p_value(
        -2.0, Alternative.LESS
    ) < 0.03

    results = bonferroni_correction(
        [0.01, 0.03, 0.20],
        0.05
    )

    assert results[0]["reject"]
    assert not results[1]["reject"]

    assert calculate_sample_size(15, 5) > 0

    try:
        Hypothesis(100, Alternative.TWO_SIDED, 1.5)
        raise AssertionError("Invalid alpha was accepted.")
    except ValueError:
        pass

    print("All statistical validation tests passed.")


def main() -> None:
    run_tests()

    # Example: testing whether a manufacturing process has
    # a different average output from its historical target.
    observations = [
        104, 108, 102, 107, 105,
        110, 106, 103, 109, 107,
        105, 108, 111, 104, 106,
        109, 107, 105, 110, 108
    ]

    hypothesis = Hypothesis(
        null_mean=100,
        alternative=Alternative.TWO_SIDED,
        alpha=0.05
    )

    result = one_sample_z_test(
        observations,
        hypothesis,
        population_sigma=8
    )

    result.display()

    print("\nMULTIPLE HYPOTHESIS TESTING")
    print("-" * 55)

    p_values = [0.001, 0.018, 0.032, 0.12, 0.40]

    for index, item in enumerate(
        bonferroni_correction(p_values, 0.05),
        start=1
    ):
        print(
            f"Test {index}: original p={item['original_p']:.3f}, "
            f"adjusted p={item['adjusted_p']:.3f}, "
            f"reject={item['reject']}"
        )

    print("\nTYPE I ERROR SIMULATION")
    simulation = simulate_null_distribution()

    for key, value in simulation.items():
        print(f"{key}: {value}")

    print("\nSAMPLE SIZE PLANNING")
    required_n = calculate_sample_size(
        sigma=15,
        minimum_detectable_effect=5,
        alpha=0.05,
        power=0.80
    )

    print(f"Required approximate sample size: {required_n}")


if __name__ == "__main__":
    main()
