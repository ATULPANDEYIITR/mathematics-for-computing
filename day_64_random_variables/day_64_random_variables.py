#!/usr/bin/env python3
"""
Random Variables: Discrete and Continuous Distributions

Demonstrates:
- Discrete random variables and probability mass functions (PMFs).
- Continuous random variables and probability density functions (PDFs).
- Cumulative distribution functions (CDFs).
- Expectation, variance, and random sampling.
- Binomial, normal, and uniform distributions.
- Monte Carlo estimation and empirical statistics.

Requires Python 3.10 or later. Uses only the standard library.
"""

from __future__ import annotations

import argparse
import math
import random
from abc import ABC, abstractmethod
from bisect import bisect_right
from dataclasses import dataclass
from statistics import fmean
from typing import Callable, Mapping, Sequence


class DistributionError(ValueError):
    """Raised when a probability distribution is invalid."""


def validate_number(value: float, name: str) -> float:
    """Convert a value to float and reject NaN."""
    try:
        result = float(value)
    except (TypeError, ValueError) as exc:
        raise DistributionError(f"{name} must be numeric.") from exc

    if math.isnan(result):
        raise DistributionError(f"{name} cannot be NaN.")

    return result


class RandomVariable(ABC):
    """Common interface for a random variable."""

    @property
    @abstractmethod
    def mean(self) -> float:
        pass

    @property
    @abstractmethod
    def variance(self) -> float:
        pass

    @abstractmethod
    def cdf(self, x: float) -> float:
        """Return P(X <= x)."""
        pass

    @abstractmethod
    def sample(self, rng: random.Random) -> float:
        pass


class DiscreteRandomVariable(RandomVariable):
    """
    A discrete random variable described by a probability mass function.

    The probability of each supported value is stored in a dictionary.
    Cumulative probabilities are precomputed for efficient CDF queries.
    """

    def __init__(self, probabilities: Mapping[float, float]) -> None:
        if not isinstance(probabilities, Mapping) or not probabilities:
            raise DistributionError("A non-empty probability mapping is required.")

        normalized: dict[float, float] = {}

        for raw_value, raw_probability in probabilities.items():
            value = validate_number(raw_value, "Support value")
            probability = validate_number(raw_probability, "Probability")

            if not math.isfinite(value):
                raise DistributionError("Discrete support values must be finite.")

            if not math.isfinite(probability) or not 0.0 <= probability <= 1.0:
                raise DistributionError("Each probability must be between 0 and 1.")

            if value in normalized:
                raise DistributionError(f"Duplicate support value: {value}")

            normalized[value] = probability

        total = math.fsum(normalized.values())

        if not math.isclose(total, 1.0, rel_tol=0.0, abs_tol=1e-9):
            raise DistributionError(
                f"Probabilities must sum to 1. Current total: {total}"
            )

        self._probabilities = dict(sorted(normalized.items()))
        self._support = tuple(self._probabilities.keys())
        self._masses = tuple(self._probabilities.values())

        cumulative: list[float] = []
        running_total = 0.0

        for probability in self._masses:
            running_total += probability
            cumulative.append(running_total)

        # Correct the last value for floating-point accumulation.
        cumulative[-1] = 1.0
        self._cumulative = tuple(cumulative)

        self._mean = math.fsum(
            value * probability
            for value, probability in self._probabilities.items()
        )

        self._variance = math.fsum(
            probability * (value - self._mean) ** 2
            for value, probability in self._probabilities.items()
        )

    @property
    def support(self) -> tuple[float, ...]:
        return self._support

    @property
    def probabilities(self) -> Mapping[float, float]:
        return self._probabilities.copy()

    @property
    def mean(self) -> float:
        return self._mean

    @property
    def variance(self) -> float:
        return self._variance

    def pmf(self, x: float) -> float:
        """Return P(X = x)."""
        value = validate_number(x, "x")
        if not math.isfinite(value):
            return 0.0
        return self._probabilities.get(value, 0.0)

    def cdf(self, x: float) -> float:
        """Return P(X <= x)."""
        value = validate_number(x, "x")
        index = bisect_right(self._support, value) - 1

        if index < 0:
            return 0.0

        return self._cumulative[index]

    def sample(self, rng: random.Random) -> float:
        """Generate one observation using inverse cumulative probabilities."""
        if not isinstance(rng, random.Random):
            raise TypeError("rng must be an instance of random.Random.")

        draw = rng.random()
        index = bisect_right(self._cumulative, draw)

        if index >= len(self._support):
            index = len(self._support) - 1

        return self._support[index]


class ContinuousRandomVariable(RandomVariable):
    """Base class for continuous random variables."""

    @abstractmethod
    def pdf(self, x: float) -> float:
        """Return the probability density at x."""
        pass


class NormalRandomVariable(ContinuousRandomVariable):
    """
    Normal distribution N(mu, sigma^2).

    sigma is the standard deviation, not the variance.
    """

    def __init__(self, mean: float, standard_deviation: float) -> None:
        self.mu = validate_number(mean, "mean")
        self.sigma = validate_number(
            standard_deviation, "standard_deviation"
        )

        if not math.isfinite(self.mu):
            raise DistributionError("Normal mean must be finite.")

        if not math.isfinite(self.sigma) or self.sigma <= 0.0:
            raise DistributionError("Standard deviation must be positive.")

    @property
    def mean(self) -> float:
        return self.mu

    @property
    def variance(self) -> float:
        return self.sigma**2

    def pdf(self, x: float) -> float:
        value = validate_number(x, "x")

        if math.isinf(value):
            return 0.0

        z = (value - self.mu) / self.sigma

        return (
            math.exp(-0.5 * z * z)
            / (self.sigma * math.sqrt(2.0 * math.pi))
        )

    def cdf(self, x: float) -> float:
        """Use the error function for an accurate normal CDF."""
        value = validate_number(x, "x")

        if value == math.inf:
            return 1.0

        if value == -math.inf:
            return 0.0

        z = (value - self.mu) / (self.sigma * math.sqrt(2.0))
        return 0.5 * (1.0 + math.erf(z))

    def sample(self, rng: random.Random) -> float:
        return rng.gauss(self.mu, self.sigma)


class UniformRandomVariable(ContinuousRandomVariable):
    """Continuous uniform distribution over [lower, upper]."""

    def __init__(self, lower: float, upper: float) -> None:
        self.lower = validate_number(lower, "lower")
        self.upper = validate_number(upper, "upper")

        if not math.isfinite(self.lower) or not math.isfinite(self.upper):
            raise DistributionError("Uniform bounds must be finite.")

        if self.lower >= self.upper:
            raise DistributionError("The lower bound must be below the upper bound.")

    @property
    def mean(self) -> float:
        return (self.lower + self.upper) / 2.0

    @property
    def variance(self) -> float:
        return (self.upper - self.lower) ** 2 / 12.0

    def pdf(self, x: float) -> float:
        value = validate_number(x, "x")

        if self.lower <= value <= self.upper:
            return 1.0 / (self.upper - self.lower)

        return 0.0

    def cdf(self, x: float) -> float:
        value = validate_number(x, "x")

        if value <= self.lower:
            return 0.0

        if value >= self.upper:
            return 1.0

        return (value - self.lower) / (self.upper - self.lower)

    def sample(self, rng: random.Random) -> float:
        return rng.uniform(self.lower, self.upper)


def binomial_distribution(
    trials: int,
    success_probability: float,
) -> DiscreteRandomVariable:
    """
    Construct a binomial random variable.

    X represents the number of successes in independent Bernoulli trials.
    """
    if isinstance(trials, bool) or not isinstance(trials, int):
        raise DistributionError("trials must be an integer.")

    if not 0 <= trials <= 1000:
        raise DistributionError("trials must be between 0 and 1000.")

    p = validate_number(success_probability, "success_probability")

    if not math.isfinite(p) or not 0.0 <= p <= 1.0:
        raise DistributionError("success_probability must be between 0 and 1.")

    probabilities: dict[int, float] = {}

    for k in range(trials + 1):
        probability = (
            math.comb(trials, k)
            * (p**k)
            * ((1.0 - p) ** (trials - k))
        )
        probabilities[k] = probability

    return DiscreteRandomVariable(probabilities)


@dataclass(frozen=True)
class MonteCarloEstimate:
    probability: float
    successes: int
    sample_count: int
    standard_error: float


def estimate_probability(
    variable: RandomVariable,
    event: Callable[[float], bool],
    sample_count: int,
    rng: random.Random,
) -> MonteCarloEstimate:
    """Estimate an event probability by repeated random sampling."""
    if isinstance(sample_count, bool) or not isinstance(sample_count, int):
        raise ValueError("sample_count must be an integer.")

    if not 1 <= sample_count <= 5_000_000:
        raise ValueError("sample_count must be between 1 and 5,000,000.")

    successes = 0

    for _ in range(sample_count):
        observation = variable.sample(rng)
        if event(observation):
            successes += 1

    estimate = successes / sample_count
    standard_error = math.sqrt(
        estimate * (1.0 - estimate) / sample_count
    )

    return MonteCarloEstimate(
        probability=estimate,
        successes=successes,
        sample_count=sample_count,
        standard_error=standard_error,
    )


@dataclass
class RunningStatistics:
    """Numerically stable online mean and variance using Welford's algorithm."""

    count: int = 0
    mean: float = 0.0
    _m2: float = 0.0

    def update(self, value: float) -> None:
        observation = validate_number(value, "observation")

        if not math.isfinite(observation):
            raise ValueError("Observed values must be finite.")

        self.count += 1
        delta = observation - self.mean
        self.mean += delta / self.count
        delta_after_update = observation - self.mean
        self._m2 += delta * delta_after_update

    @property
    def sample_variance(self) -> float:
        if self.count < 2:
            return 0.0
        return self._m2 / (self.count - 1)

    @property
    def population_variance(self) -> float:
        if self.count == 0:
            return 0.0
        return self._m2 / self.count


def validate_implementations() -> None:
    """Run deterministic checks for formulas and boundary conditions."""
    die = DiscreteRandomVariable(
        {1: 1 / 6, 2: 1 / 6, 3: 1 / 6,
         4: 1 / 6, 5: 1 / 6, 6: 1 / 6}
    )

    assert math.isclose(die.pmf(3), 1 / 6)
    assert math.isclose(die.cdf(3), 0.5)
    assert math.isclose(die.mean, 3.5)
    assert math.isclose(die.variance, 35 / 12)

    normal = NormalRandomVariable(0.0, 1.0)
    assert math.isclose(normal.cdf(0.0), 0.5)
    assert math.isclose(normal.pdf(0.0), 1 / math.sqrt(2 * math.pi))

    uniform = UniformRandomVariable(0.0, 10.0)
    assert math.isclose(uniform.cdf(5.0), 0.5)
    assert math.isclose(uniform.pdf(5.0), 0.1)
    assert uniform.cdf(-1.0) == 0.0
    assert uniform.cdf(11.0) == 1.0

    try:
        DiscreteRandomVariable({0: 0.4, 1: 0.4})
    except DistributionError:
        pass
    else:
        raise AssertionError("Invalid probability total was accepted.")

    try:
        NormalRandomVariable(0.0, 0.0)
    except DistributionError:
        pass
    else:
        raise AssertionError("Invalid normal standard deviation was accepted.")


def run_demo(sample_count: int, seed: int) -> None:
    validate_implementations()
    rng = random.Random(seed)

    print("=" * 68)
    print("RANDOM VARIABLES: DISCRETE AND CONTINUOUS")
    print("=" * 68)

    # Scenario 1: failed requests among four independent requests.
    failures = binomial_distribution(trials=4, success_probability=0.10)

    print("\n1. DISCRETE RANDOM VARIABLE")
    print("X = number of failed requests among four requests")
    print("\nProbability mass function:")

    for outcome, probability in failures.probabilities.items():
        print(f"P(X = {outcome}) = {probability:.6f}")

    print(f"\nP(X <= 2)       = {failures.cdf(2):.6f}")
    print(f"P(X = 2)        = {failures.pmf(2):.6f}")
    print(f"E[X]            = {failures.mean:.6f}")
    print(f"Var(X)          = {failures.variance:.6f}")

    discrete_estimate = estimate_probability(
        failures,
        lambda value: value >= 2,
        sample_count,
        rng,
    )

    print(
        f"P(X >= 2), Monte Carlo = "
        f"{discrete_estimate.probability:.6f}"
    )
    print(
        f"Monte Carlo standard error = "
        f"{discrete_estimate.standard_error:.6f}"
    )

    # Scenario 2: normally distributed API response time.
    latency = NormalRandomVariable(mean=120.0, standard_deviation=25.0)

    print("\n2. CONTINUOUS NORMAL RANDOM VARIABLE")
    print("Y = API response time in milliseconds")
    print(f"Mean                    = {latency.mean:.2f} ms")
    print(f"Variance                = {latency.variance:.2f} ms^2")
    print(f"PDF at 150 ms           = {latency.pdf(150):.8f}")
    print(f"CDF at 150 ms           = {latency.cdf(150):.6f}")
    print(f"P(Y > 180 ms)           = {1 - latency.cdf(180):.6f}")

    latency_estimate = estimate_probability(
        latency,
        lambda value: value > 180.0,
        sample_count,
        rng,
    )

    print(
        f"P(Y > 180 ms), Monte Carlo = "
        f"{latency_estimate.probability:.6f}"
    )

    # Scenario 3: uniformly distributed sensor measurement error.
    sensor_error = UniformRandomVariable(lower=-2.0, upper=2.0)

    print("\n3. CONTINUOUS UNIFORM RANDOM VARIABLE")
    print("Z = sensor measurement error")
    print(f"Mean                    = {sensor_error.mean:.4f}")
    print(f"Variance                = {sensor_error.variance:.4f}")
    print(f"PDF at 0                = {sensor_error.pdf(0):.4f}")
    print(f"CDF at 1                = {sensor_error.cdf(1):.4f}")
    print(f"P(-1 <= Z <= 1)         = "
          f"{sensor_error.cdf(1) - sensor_error.cdf(-1):.4f}")

    # Online empirical statistics for a separate latency sample.
    empirical = RunningStatistics()

    for _ in range(sample_count):
        empirical.update(latency.sample(rng))

    print("\n4. EMPIRICAL LATENCY STATISTICS")
    print(f"Observations             = {empirical.count}")
    print(f"Empirical mean           = {empirical.mean:.4f} ms")
    print(f"Empirical sample variance= {empirical.sample_variance:.4f}")

    print("\n5. VALIDATION")
    print("All deterministic distribution checks passed.")
    print("Random samples use a seeded pseudorandom generator.")
    print("The generator is intended for statistical simulation, not cryptography.")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Demonstrate discrete and continuous random variables."
    )
    parser.add_argument(
        "--samples",
        type=int,
        default=50_000,
        help="Number of Monte Carlo observations (default: 50000).",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=20261103,
        help="Random seed for reproducible results.",
    )

    args = parser.parse_args()

    if not 1 <= args.samples <= 5_000_000:
        parser.error("--samples must be between 1 and 5,000,000.")

    run_demo(args.samples, args.seed)


if __name__ == "__main__":
    main()
