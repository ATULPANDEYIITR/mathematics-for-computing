"""
EXPECTED VALUE AND MOMENTS
Topics:
- Mathematical expectation
- Discrete probability distributions
- Weighted outcomes
- Variance
- Standard deviation
- Raw moments
- Central moments
- Skewness and kurtosis
- Conditional expectation
- Covariance and correlation
- Empirical expectation
- Monte Carlo simulation

Python 3.10+
Standard library only.
"""

from dataclasses import dataclass
from math import sqrt, isclose, isfinite
from collections import Counter
from typing import Iterable, Sequence
from random import Random


class ProbabilityError(ValueError):
    """Raised when probability data is invalid."""


@dataclass(frozen=True)
class Outcome:
    value: float
    probability: float

    def __post_init__(self):
        if not isfinite(self.value):
            raise ProbabilityError("Outcome must be finite.")

        if not isfinite(self.probability):
            raise ProbabilityError("Probability must be finite.")

        if not 0.0 <= self.probability <= 1.0:
            raise ProbabilityError("Probability must be between 0 and 1.")


@dataclass(frozen=True)
class Statistics:
    expected_value: float
    variance: float
    standard_deviation: float
    raw_moments: dict[int, float]
    central_moments: dict[int, float]
    skewness: float | None
    kurtosis: float | None


class DiscreteDistribution:
    """Represents a finite discrete probability distribution."""

    def __init__(
        self,
        outcomes: Iterable[Outcome],
        name: str = "Distribution",
        tolerance: float = 1e-9
    ):
        self.name = name
        self.outcomes = tuple(outcomes)
        self.tolerance = tolerance

        if not self.outcomes:
            raise ProbabilityError("Distribution cannot be empty.")

        if not isfinite(tolerance) or tolerance <= 0:
            raise ProbabilityError("Tolerance must be positive and finite.")

        total = sum(item.probability for item in self.outcomes)

        if not isclose(total, 1.0, abs_tol=tolerance):
            raise ProbabilityError(
                f"Probabilities must sum to 1. Got {total}."
            )

    def expectation(self, function=lambda x: x) -> float:
        """Calculate E[g(X)] = sum(g(x) * P(X=x))."""
        result = 0.0

        for outcome in self.outcomes:
            transformed = function(outcome.value)

            if not isfinite(transformed):
                raise ValueError("Transformation produced a non-finite value.")

            result += transformed * outcome.probability

        return result

    def expected_value(self) -> float:
        return self.expectation()

    def raw_moment(self, order: int) -> float:
        if not isinstance(order, int) or order < 0:
            raise ValueError("Moment order must be a non-negative integer.")

        return self.expectation(lambda x: x ** order)

    def variance(self) -> float:
        mean = self.expected_value()
        result = self.expectation(lambda x: (x - mean) ** 2)

        return max(0.0, result)

    def standard_deviation(self) -> float:
        return sqrt(self.variance())

    def central_moment(self, order: int) -> float:
        if not isinstance(order, int) or order < 0:
            raise ValueError("Moment order must be non-negative.")

        mean = self.expected_value()

        return self.expectation(lambda x: (x - mean) ** order)

    def statistics(self) -> Statistics:
        mean = self.expected_value()
        variance = self.variance()
        deviation = sqrt(variance)

        raw = {
            order: self.raw_moment(order)
            for order in range(1, 5)
        }

        central = {
            order: self.central_moment(order)
            for order in range(1, 5)
        }

        if deviation == 0:
            skewness = None
            kurtosis = None
        else:
            skewness = central[3] / deviation ** 3
            kurtosis = central[4] / variance ** 2

        return Statistics(
            expected_value=mean,
            variance=variance,
            standard_deviation=deviation,
            raw_moments=raw,
            central_moments=central,
            skewness=skewness,
            kurtosis=kurtosis
        )

    def probability_greater_than(self, threshold: float) -> float:
        return sum(
            item.probability
            for item in self.outcomes
            if item.value > threshold
        )

    def probability_between(
        self,
        lower: float,
        upper: float
    ) -> float:
        if lower > upper:
            raise ValueError("Lower bound cannot exceed upper bound.")

        return sum(
            item.probability
            for item in self.outcomes
            if lower <= item.value <= upper
        )

    def conditional_expectation(
        self,
        condition
    ) -> float:
        """Calculate E[X | condition(X)]."""
        selected = [
            item for item in self.outcomes
            if condition(item.value)
        ]

        probability = sum(item.probability for item in selected)

        if probability <= self.tolerance:
            raise ProbabilityError(
                "Conditional event has zero probability."
            )

        return sum(
            item.value * item.probability
            for item in selected
        ) / probability

    def describe(self) -> None:
        stats = self.statistics()

        print(f"\n{self.name}")
        print("-" * 55)
        print(f"Expected value:       {stats.expected_value:.6f}")
        print(f"Variance:             {stats.variance:.6f}")
        print(f"Standard deviation:   {stats.standard_deviation:.6f}")
        print(f"Skewness:             {stats.skewness}")
        print(f"Kurtosis:             {stats.kurtosis}")

        print("\nRaw moments:")

        for order, value in stats.raw_moments.items():
            print(f"E[X^{order}]: {value:.6f}")

        print("\nCentral moments:")

        for order, value in stats.central_moments.items():
            print(f"E[(X - mean)^{order}]: {value:.6f}")


def covariance(
    distribution_x: DiscreteDistribution,
    distribution_y: DiscreteDistribution
) -> float:
    """
    Calculate covariance from paired joint outcomes.

    Each outcome value must be a tuple (x, y).
    """

    if not distribution_x.outcomes or not distribution_y.outcomes:
        raise ProbabilityError("Distributions cannot be empty.")

    raise ValueError(
        "Use joint_covariance() with a joint distribution."
    )


def joint_covariance(
    outcomes: Sequence[tuple[float, float, float]]
) -> float:
    """Calculate covariance from (X, Y, probability) records."""

    if not outcomes:
        raise ProbabilityError("Joint distribution cannot be empty.")

    total = 0.0

    for x, y, probability in outcomes:
        if not all(isfinite(v) for v in (x, y, probability)):
            raise ProbabilityError("All joint values must be finite.")

        if not 0 <= probability <= 1:
            raise ProbabilityError("Invalid joint probability.")

        total += probability

    if not isclose(total, 1.0, abs_tol=1e-9):
        raise ProbabilityError("Joint probabilities must sum to 1.")

    mean_x = sum(x * p for x, y, p in outcomes)
    mean_y = sum(y * p for x, y, p in outcomes)

    return sum(
        (x - mean_x) * (y - mean_y) * p
        for x, y, p in outcomes
    )


def correlation(
    outcomes: Sequence[tuple[float, float, float]]
) -> float | None:
    """Calculate Pearson correlation from a joint distribution."""

    covariance_value = joint_covariance(outcomes)

    mean_x = sum(x * p for x, y, p in outcomes)
    mean_y = sum(y * p for x, y, p in outcomes)

    variance_x = sum(
        (x - mean_x) ** 2 * p
        for x, y, p in outcomes
    )

    variance_y = sum(
        (y - mean_y) ** 2 * p
        for x, y, p in outcomes
    )

    if variance_x == 0 or variance_y == 0:
        return None

    return covariance_value / sqrt(variance_x * variance_y)


def empirical_statistics(
    observations: Sequence[float]
) -> dict[str, float]:
    """Calculate population-style empirical statistics."""

    if not observations:
        raise ValueError("Observations cannot be empty.")

    if not all(isfinite(x) for x in observations):
        raise ValueError("Observations must be finite.")

    n = len(observations)
    mean = sum(observations) / n

    variance = sum(
        (x - mean) ** 2
        for x in observations
    ) / n

    return {
        "count": n,
        "mean": mean,
        "variance": variance,
        "standard_deviation": sqrt(variance),
        "sample_variance": (
            sum((x - mean) ** 2 for x in observations) / (n - 1)
            if n > 1 else 0.0
        )
    }


def monte_carlo_expectation(
    distribution: DiscreteDistribution,
    trials: int = 100_000,
    seed: int = 42
) -> dict[str, float]:
    """Estimate expectation through reproducible random sampling."""

    if not isinstance(trials, int) or trials <= 0:
        raise ValueError("Trials must be a positive integer.")

    rng = Random(seed)

    values = [item.value for item in distribution.outcomes]
    weights = [item.probability for item in distribution.outcomes]

    samples = rng.choices(
        values,
        weights=weights,
        k=trials
    )

    mean = sum(samples) / trials

    variance = sum(
        (x - mean) ** 2
        for x in samples
    ) / trials

    return {
        "trials": trials,
        "estimated_expectation": mean,
        "theoretical_expectation": distribution.expected_value(),
        "absolute_error": abs(
            mean - distribution.expected_value()
        ),
        "estimated_standard_deviation": sqrt(variance)
    }


def main():
    print("=" * 65)
    print("EXPECTED VALUE AND MOMENTS ANALYSIS")
    print("=" * 65)

    # Example 1: Fair six-sided die.
    die = DiscreteDistribution(
        [
            Outcome(face, 1 / 6)
            for face in range(1, 7)
        ],
        name="Fair Six-Sided Die"
    )

    die.describe()

    # Example 2: Investment return distribution.
    investment = DiscreteDistribution(
        [
            Outcome(-1000, 0.10),
            Outcome(-200, 0.20),
            Outcome(300, 0.40),
            Outcome(1000, 0.20),
            Outcome(2500, 0.10)
        ],
        name="Investment Return"
    )

    investment.describe()

    print("\nInvestment probability analysis")
    print(
        "Probability of positive return:",
        investment.probability_greater_than(0)
    )

    print(
        "Expected return given positive return:",
        investment.conditional_expectation(lambda x: x > 0)
    )

    # Example 3: Joint probability distribution.
    joint_data = [
        (10, 20, 0.20),
        (20, 30, 0.30),
        (30, 20, 0.10),
        (40, 50, 0.40)
    ]

    print("\nJoint distribution analysis")
    print("Covariance:", joint_covariance(joint_data))
    print("Correlation:", correlation(joint_data))

    # Example 4: Empirical statistics.
    observations = [12, 15, 18, 20, 22, 25, 28]

    print("\nEmpirical statistics")

    for key, value in empirical_statistics(observations).items():
        print(f"{key}: {value:.6f}")

    # Example 5: Monte Carlo estimation.
    print("\nMonte Carlo estimation")

    simulation = monte_carlo_expectation(
        die,
        trials=100_000,
        seed=42
    )

    for key, value in simulation.items():
        print(f"{key}: {value:.6f}")

    # Example 6: Deterministic distribution.
    deterministic = DiscreteDistribution(
        [Outcome(50, 1.0)],
        name="Deterministic Outcome"
    )

    print("\nDeterministic distribution")
    print("Variance:", deterministic.variance())
    print("Standard deviation:", deterministic.standard_deviation())

    # Example 7: Validation.
    print("\nValidation tests")

    try:
        DiscreteDistribution([
            Outcome(10, 0.4),
            Outcome(20, 0.4)
        ])
    except ProbabilityError as error:
        print("Invalid distribution detected:", error)

    try:
        die.conditional_expectation(lambda x: x > 10)
    except ProbabilityError as error:
        print("Zero-probability condition detected:", error)

    # Mathematical correctness checks.
    assert isclose(die.expected_value(), 3.5)
    assert isclose(die.variance(), 35 / 12)
    assert isclose(deterministic.variance(), 0.0)
    assert isclose(
        joint_covariance([(0, 0, 0.5), (2, 2, 0.5)]),
        1.0
    )

    print("\nAll mathematical validation tests passed.")


if __name__ == "__main__":
    main()
