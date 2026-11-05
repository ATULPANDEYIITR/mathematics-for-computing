#!/usr/bin/env python3
"""
Probability Distributions
Bernoulli, Binomial, Geometric, and Negative Binomial.

A self-contained implementation covering probability mass functions,
cumulative probabilities, theoretical moments, random sampling,
empirical estimation, and statistical validation.
"""

from __future__ import annotations

import math
import random
import statistics
from dataclasses import dataclass
from enum import Enum
from collections import Counter
from typing import Callable


class DistributionType(Enum):
    BERNOULLI = "Bernoulli"
    BINOMIAL = "Binomial"
    GEOMETRIC = "Geometric"
    NEGATIVE_BINOMIAL = "Negative Binomial"


class ProbabilityError(ValueError):
    """Raised when distribution parameters or outcomes are invalid."""


def validate_probability(p: float) -> None:
    if isinstance(p, bool) or not isinstance(p, (int, float)):
        raise ProbabilityError("Probability must be numeric.")
    if not math.isfinite(p) or not 0.0 <= p <= 1.0:
        raise ProbabilityError("Probability must be between 0 and 1.")


def validate_integer(value: int, name: str, minimum: int = 0) -> None:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ProbabilityError(f"{name} must be an integer.")
    if value < minimum:
        raise ProbabilityError(f"{name} must be at least {minimum}.")


def combination(n: int, k: int) -> int:
    if k < 0 or k > n:
        return 0
    return math.comb(n, k)


@dataclass(frozen=True)
class DistributionStatistics:
    mean: float
    variance: float
    standard_deviation: float


class ProbabilityDistribution:
    """Common interface for discrete probability distributions."""

    def __init__(self, probability: float):
        validate_probability(probability)
        self.p = float(probability)

    def pmf(self, outcome: int) -> float:
        raise NotImplementedError

    def cdf(self, outcome: int) -> float:
        raise NotImplementedError

    def sample(self, rng: random.Random | None = None) -> int:
        raise NotImplementedError

    def statistics(self) -> DistributionStatistics:
        raise NotImplementedError

    def sample_many(
        self, count: int, rng: random.Random | None = None
    ) -> list[int]:
        validate_integer(count, "Sample count", 1)
        generator = rng or random.Random()
        return [self.sample(generator) for _ in range(count)]

    def empirical_distribution(self, count: int, seed: int = 42) -> dict:
        observations = self.sample_many(count, random.Random(seed))
        frequencies = Counter(observations)

        return {
            "sample_size": count,
            "mean": statistics.fmean(observations),
            "variance": statistics.pvariance(observations),
            "frequencies": dict(sorted(frequencies.items())),
        }


class BernoulliDistribution(ProbabilityDistribution):
    """
    One trial with two possible outcomes:
    1 = success, 0 = failure.
    """

    def pmf(self, outcome: int) -> float:
        if outcome == 1:
            return self.p
        if outcome == 0:
            return 1.0 - self.p
        return 0.0

    def cdf(self, outcome: int) -> float:
        if outcome < 0:
            return 0.0
        return 1.0 - self.p if outcome == 0 else 1.0

    def sample(self, rng: random.Random | None = None) -> int:
        return int((rng or random).random() < self.p)

    def statistics(self) -> DistributionStatistics:
        variance = self.p * (1.0 - self.p)
        return DistributionStatistics(
            self.p, variance, math.sqrt(variance)
        )


class BinomialDistribution(ProbabilityDistribution):
    """
    Number of successes in n independent Bernoulli trials.
    """

    def __init__(self, n: int, probability: float):
        super().__init__(probability)
        validate_integer(n, "Number of trials", 0)
        self.n = n

    def pmf(self, outcome: int) -> float:
        if not isinstance(outcome, int) or isinstance(outcome, bool):
            return 0.0
        if outcome < 0 or outcome > self.n:
            return 0.0

        return (
            combination(self.n, outcome)
            * self.p**outcome
            * (1.0 - self.p) ** (self.n - outcome)
        )

    def cdf(self, outcome: int) -> float:
        if outcome < 0:
            return 0.0
        if outcome >= self.n:
            return 1.0
        return min(1.0, math.fsum(self.pmf(k) for k in range(outcome + 1)))

    def sample(self, rng: random.Random | None = None) -> int:
        generator = rng or random
        return sum(generator.random() < self.p for _ in range(self.n))

    def statistics(self) -> DistributionStatistics:
        mean = self.n * self.p
        variance = self.n * self.p * (1.0 - self.p)
        return DistributionStatistics(mean, variance, math.sqrt(variance))


class GeometricDistribution(ProbabilityDistribution):
    """
    Number of independent trials required to obtain the first success.

    Support: 1, 2, 3, ...
    """

    def pmf(self, outcome: int) -> float:
        if not isinstance(outcome, int) or isinstance(outcome, bool):
            return 0.0
        if outcome < 1 or self.p == 0.0:
            return 0.0
        if self.p == 1.0:
            return float(outcome == 1)

        return (1.0 - self.p) ** (outcome - 1) * self.p

    def cdf(self, outcome: int) -> float:
        if outcome < 1:
            return 0.0
        if self.p == 0.0:
            return 0.0
        if self.p == 1.0:
            return 1.0
        return 1.0 - (1.0 - self.p) ** outcome

    def sample(self, rng: random.Random | None = None) -> int:
        if self.p == 0.0:
            raise ProbabilityError(
                "A first success cannot occur when p = 0."
            )
        if self.p == 1.0:
            return 1

        generator = rng or random
        return math.floor(
            math.log1p(-generator.random()) / math.log1p(-self.p)
        ) + 1

    def statistics(self) -> DistributionStatistics:
        if self.p == 0.0:
            return DistributionStatistics(math.inf, math.inf, math.inf)

        mean = 1.0 / self.p
        variance = (1.0 - self.p) / self.p**2

        return DistributionStatistics(mean, variance, math.sqrt(variance))


class NegativeBinomialDistribution(ProbabilityDistribution):
    """
    Number of trials required to achieve r successes.

    Support: r, r+1, r+2, ...
    """

    def __init__(self, r: int, probability: float):
        super().__init__(probability)
        validate_integer(r, "Required successes", 1)
        self.r = r

    def pmf(self, outcome: int) -> float:
        if not isinstance(outcome, int) or isinstance(outcome, bool):
            return 0.0
        if outcome < self.r or self.p == 0.0:
            return 0.0
        if self.p == 1.0:
            return float(outcome == self.r)

        failures = outcome - self.r

        return (
            combination(outcome - 1, self.r - 1)
            * self.p**self.r
            * (1.0 - self.p) ** failures
        )

    def cdf(self, outcome: int) -> float:
        if outcome < self.r:
            return 0.0
        if self.p == 0.0:
            return 0.0
        if self.p == 1.0:
            return 1.0
        return min(
            1.0,
            math.fsum(self.pmf(k) for k in range(self.r, outcome + 1)),
        )

    def sample(self, rng: random.Random | None = None) -> int:
        if self.p == 0.0:
            raise ProbabilityError(
                "Required successes cannot occur when p = 0."
            )
        if self.p == 1.0:
            return self.r

        generator = rng or random
        successes = 0
        trials = 0

        while successes < self.r:
            trials += 1
            successes += generator.random() < self.p

        return trials

    def statistics(self) -> DistributionStatistics:
        if self.p == 0.0:
            return DistributionStatistics(math.inf, math.inf, math.inf)

        mean = self.r / self.p
        variance = self.r * (1.0 - self.p) / self.p**2

        return DistributionStatistics(mean, variance, math.sqrt(variance))


def estimate_bernoulli_probability(observations: list[int]) -> float:
    """Maximum-likelihood estimate of Bernoulli success probability."""
    if not observations:
        raise ProbabilityError("Observations cannot be empty.")

    if any(value not in (0, 1) or isinstance(value, bool)
           for value in observations):
        raise ProbabilityError("Bernoulli observations must be 0 or 1.")

    return sum(observations) / len(observations)


def probability_at_least(
    distribution: ProbabilityDistribution, threshold: int
) -> float:
    """Calculate P(X >= threshold)."""
    return max(0.0, 1.0 - distribution.cdf(threshold - 1))


def display_distribution(
    name: str, distribution: ProbabilityDistribution,
    outcomes: range
) -> None:
    print(f"\n{name}")
    print("-" * 65)

    for outcome in outcomes:
        print(
            f"Outcome={outcome:3d} | "
            f"PMF={distribution.pmf(outcome):.8f} | "
            f"CDF={distribution.cdf(outcome):.8f}"
        )

    stats = distribution.statistics()

    print(f"Mean: {stats.mean:.6f}")
    print(f"Variance: {stats.variance:.6f}")
    print(f"Standard deviation: {stats.standard_deviation:.6f}")


def run_tests() -> None:
    bernoulli = BernoulliDistribution(0.3)
    assert math.isclose(bernoulli.pmf(1), 0.3)
    assert math.isclose(bernoulli.pmf(0), 0.7)

    binomial = BinomialDistribution(5, 0.5)
    assert math.isclose(binomial.pmf(2), 10 / 32)
    assert math.isclose(sum(binomial.pmf(k) for k in range(6)), 1.0)

    geometric = GeometricDistribution(0.25)
    assert math.isclose(geometric.pmf(1), 0.25)
    assert math.isclose(geometric.cdf(2), 0.4375)

    negative_binomial = NegativeBinomialDistribution(3, 0.5)
    assert math.isclose(negative_binomial.pmf(4), 0.1875)
    assert math.isclose(negative_binomial.cdf(4), 0.3125)

    assert binomial.pmf(-1) == 0.0
    assert geometric.pmf(0) == 0.0
    assert negative_binomial.pmf(2) == 0.0

    assert estimate_bernoulli_probability([1, 0, 1, 1]) == 0.75

    try:
        BinomialDistribution(-1, 0.5)
        raise AssertionError("Negative trial count was accepted.")
    except ProbabilityError:
        pass

    try:
        BernoulliDistribution(1.5)
        raise AssertionError("Invalid probability was accepted.")
    except ProbabilityError:
        pass

    print("All statistical validation tests passed.")


def main() -> None:
    rng = random.Random(42)

    run_tests()

    distributions = [
        ("Bernoulli: Website request success", BernoulliDistribution(0.8), range(0, 2)),
        ("Binomial: Successful transactions", BinomialDistribution(10, 0.7), range(0, 11)),
        ("Geometric: Attempts until first success", GeometricDistribution(0.25), range(1, 8)),
        ("Negative Binomial: Attempts for three successes",
         NegativeBinomialDistribution(3, 0.4), range(3, 11)),
    ]

    for name, distribution, outcomes in distributions:
        display_distribution(name, distribution, outcomes)

        samples = distribution.sample_many(10000, rng)
        empirical_mean = statistics.fmean(samples)

        print(f"Simulated mean (10,000 samples): {empirical_mean:.6f}")
        print(f"Theoretical mean: {distribution.statistics().mean:.6f}")

    print("\nBusiness probability calculations")
    print("-" * 65)

    transactions = BinomialDistribution(20, 0.95)
    print(
        "Probability of at least 18 successful transactions: "
        f"{probability_at_least(transactions, 18):.6f}"
    )

    retries = GeometricDistribution(0.2)
    print(
        "Probability that the first success occurs within 5 attempts: "
        f"{retries.cdf(5):.6f}"
    )

    support_calls = NegativeBinomialDistribution(5, 0.6)
    print(
        "Probability of completing 5 successful calls within 8 attempts: "
        f"{support_calls.cdf(8):.6f}"
    )

    observations = [1, 0, 1, 1, 0, 1, 1, 1]
    estimate = estimate_bernoulli_probability(observations)
    print(f"Estimated transaction success probability: {estimate:.4f}")

    print("\nExecution completed successfully.")


if __name__ == "__main__":
    main()
