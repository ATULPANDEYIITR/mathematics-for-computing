"""
Continuous Distributions
Uniform, Exponential, and Normal Distributions

A self-contained statistical simulation and analysis program.

Features:
- Probability density functions (PDF)
- Cumulative distribution functions (CDF)
- Quantile functions
- Random sampling
- Descriptive statistics
- Theoretical and empirical probabilities
- Confidence intervals
- Distribution comparisons
- Kolmogorov-Smirnov-style empirical distance
- Reproducible simulations
- Input validation and automated tests

Run:
    python continuous_distributions.py
"""

from __future__ import annotations

import math
import random
import statistics
from dataclasses import dataclass
from enum import Enum
from typing import Callable, Sequence


class DistributionError(ValueError):
    """Raised when distribution parameters or observations are invalid."""


class DistributionType(Enum):
    UNIFORM = "Uniform"
    EXPONENTIAL = "Exponential"
    NORMAL = "Normal"


def validate_probability(p: float) -> None:
    if not math.isfinite(p) or not 0.0 <= p <= 1.0:
        raise DistributionError("Probability must be between 0 and 1.")


def validate_sample_size(size: int) -> None:
    if isinstance(size, bool) or not isinstance(size, int) or size <= 0:
        raise DistributionError("Sample size must be a positive integer.")


def validate_finite(value: float, name: str) -> None:
    if not math.isfinite(value):
        raise DistributionError(f"{name} must be finite.")


@dataclass(frozen=True)
class SampleStatistics:
    count: int
    mean: float
    variance: float
    standard_deviation: float
    minimum: float
    maximum: float
    median: float


class ContinuousDistribution:
    """Common interface for continuous probability distributions."""

    def pdf(self, x: float) -> float:
        raise NotImplementedError

    def cdf(self, x: float) -> float:
        raise NotImplementedError

    def quantile(self, p: float) -> float:
        raise NotImplementedError

    def sample(self, size: int, rng: random.Random) -> list[float]:
        raise NotImplementedError

    def probability_between(self, lower: float, upper: float) -> float:
        validate_finite(lower, "Lower bound")
        validate_finite(upper, "Upper bound")

        if lower > upper:
            raise DistributionError("Lower bound cannot exceed upper bound.")

        return self.cdf(upper) - self.cdf(lower)


@dataclass(frozen=True)
class UniformDistribution(ContinuousDistribution):
    """Continuous uniform distribution on [a, b]."""

    a: float
    b: float

    def __post_init__(self):
        validate_finite(self.a, "a")
        validate_finite(self.b, "b")

        if self.a >= self.b:
            raise DistributionError("Uniform distribution requires a < b.")

    @property
    def mean(self) -> float:
        return (self.a + self.b) / 2.0

    @property
    def variance(self) -> float:
        return (self.b - self.a) ** 2 / 12.0

    def pdf(self, x: float) -> float:
        validate_finite(x, "x")
        if self.a <= x <= self.b:
            return 1.0 / (self.b - self.a)
        return 0.0

    def cdf(self, x: float) -> float:
        validate_finite(x, "x")
        if x < self.a:
            return 0.0
        if x >= self.b:
            return 1.0
        return (x - self.a) / (self.b - self.a)

    def quantile(self, p: float) -> float:
        validate_probability(p)
        return self.a + p * (self.b - self.a)

    def sample(self, size: int, rng: random.Random) -> list[float]:
        validate_sample_size(size)
        return [rng.uniform(self.a, self.b) for _ in range(size)]


@dataclass(frozen=True)
class ExponentialDistribution(ContinuousDistribution):
    """Exponential distribution parameterized by rate lambda."""

    rate: float

    def __post_init__(self):
        validate_finite(self.rate, "Rate")
        if self.rate <= 0:
            raise DistributionError("Rate must be positive.")

    @property
    def mean(self) -> float:
        return 1.0 / self.rate

    @property
    def variance(self) -> float:
        return 1.0 / (self.rate ** 2)

    def pdf(self, x: float) -> float:
        validate_finite(x, "x")
        if x < 0:
            return 0.0
        return self.rate * math.exp(-self.rate * x)

    def cdf(self, x: float) -> float:
        validate_finite(x, "x")
        if x <= 0:
            return 0.0
        return -math.expm1(-self.rate * x)

    def survival_function(self, x: float) -> float:
        validate_finite(x, "x")
        if x <= 0:
            return 1.0
        return math.exp(-self.rate * x)

    def quantile(self, p: float) -> float:
        validate_probability(p)

        if p == 1.0:
            return math.inf

        return -math.log1p(-p) / self.rate

    def sample(self, size: int, rng: random.Random) -> list[float]:
        validate_sample_size(size)
        return [rng.expovariate(self.rate) for _ in range(size)]


def normal_cdf_standard(z: float) -> float:
    """Standard normal CDF using the complementary error function."""
    return 0.5 * math.erfc(-z / math.sqrt(2.0))


def normal_quantile_standard(p: float) -> float:
    """
    Inverse standard normal CDF using the Acklam rational approximation.

    Newton refinement improves the approximation in the central region.
    """

    validate_probability(p)

    if p == 0.0:
        return -math.inf
    if p == 1.0:
        return math.inf

    a = [
        -3.969683028665376e1,
        2.209460984245205e2,
        -2.759285104469687e2,
        1.383577518672690e2,
        -3.066479806614716e1,
        2.506628277459239,
    ]

    b = [
        -5.447609879822406e1,
        1.615858368580409e2,
        -1.556989798598866e2,
        6.680131188771972e1,
        -1.328068155288572e1,
    ]

    c = [
        -7.784894002430293e-3,
        -3.223964580411365e-1,
        -2.400758277161838,
        -2.549732539343734,
        4.374664141464968,
        2.938163982698783,
    ]

    d = [
        7.784695709041462e-3,
        3.224671290700398e-1,
        2.445134137142996,
        3.754408661907416,
    ]

    low = 0.02425
    high = 1.0 - low

    if p < low:
        q = math.sqrt(-2.0 * math.log(p))
        x = (
            (((((c[0] * q + c[1]) * q + c[2]) * q + c[3]) * q + c[4]) * q + c[5])
            / ((((d[0] * q + d[1]) * q + d[2]) * q + d[3]) * q + 1.0)
        )

    elif p > high:
        q = math.sqrt(-2.0 * math.log1p(-p))
        x = -(
            (((((c[0] * q + c[1]) * q + c[2]) * q + c[3]) * q + c[4]) * q + c[5])
            / ((((d[0] * q + d[1]) * q + d[2]) * q + d[3]) * q + 1.0)
        )

    else:
        q = p - 0.5
        r = q * q

        x = (
            (((((a[0] * r + a[1]) * r + a[2]) * r + a[3]) * r + a[4]) * r + a[5]) * q
            / (((((b[0] * r + b[1]) * r + b[2]) * r + b[3]) * r + b[4]) * r + 1.0)
        )

    # Newton correction is safe in the central range.
    if 1e-12 < p < 1.0 - 1e-12:
        error = normal_cdf_standard(x) - p
        density = math.exp(-0.5 * x * x) / math.sqrt(2.0 * math.pi)

        if density > 1e-300:
            x -= error / density

    return x


@dataclass(frozen=True)
class NormalDistribution(ContinuousDistribution):
    """Normal distribution parameterized by mean and standard deviation."""

    mu: float
    sigma: float

    def __post_init__(self):
        validate_finite(self.mu, "Mean")
        validate_finite(self.sigma, "Standard deviation")

        if self.sigma <= 0:
            raise DistributionError("Standard deviation must be positive.")

    @property
    def mean(self) -> float:
        return self.mu

    @property
    def variance(self) -> float:
        return self.sigma ** 2

    def pdf(self, x: float) -> float:
        validate_finite(x, "x")

        z = (x - self.mu) / self.sigma

        return (
            math.exp(-0.5 * z * z)
            / (self.sigma * math.sqrt(2.0 * math.pi))
        )

    def cdf(self, x: float) -> float:
        validate_finite(x, "x")

        z = (x - self.mu) / (self.sigma * math.sqrt(2.0))

        return 0.5 * math.erfc(-z)

    def quantile(self, p: float) -> float:
        return self.mu + self.sigma * normal_quantile_standard(p)

    def sample(self, size: int, rng: random.Random) -> list[float]:
        validate_sample_size(size)
        return [rng.gauss(self.mu, self.sigma) for _ in range(size)]

    def standardize(self, x: float) -> float:
        validate_finite(x, "x")
        return (x - self.mu) / self.sigma


def calculate_statistics(values: Sequence[float]) -> SampleStatistics:
    if not values:
        raise DistributionError("Cannot calculate statistics for empty data.")

    for value in values:
        validate_finite(value, "Observation")

    return SampleStatistics(
        count=len(values),
        mean=statistics.fmean(values),
        variance=statistics.variance(values) if len(values) > 1 else 0.0,
        standard_deviation=statistics.stdev(values) if len(values) > 1 else 0.0,
        minimum=min(values),
        maximum=max(values),
        median=statistics.median(values),
    )


def empirical_probability(
    values: Sequence[float],
    condition: Callable[[float], bool],
) -> float:
    if not values:
        raise DistributionError("Sample cannot be empty.")

    return sum(1 for value in values if condition(value)) / len(values)


def confidence_interval_mean(
    values: Sequence[float],
    z_score: float = 1.96,
) -> tuple[float, float]:
    """
    Approximate 95% or configurable normal-based confidence interval.

    For small samples, a Student t critical value is preferable.
    """

    if len(values) < 2:
        raise DistributionError("At least two observations are required.")

    validate_finite(z_score, "Z score")

    if z_score <= 0:
        raise DistributionError("Z score must be positive.")

    stats = calculate_statistics(values)
    margin = z_score * stats.standard_deviation / math.sqrt(stats.count)

    return stats.mean - margin, stats.mean + margin


def empirical_cdf(values: Sequence[float], x: float) -> float:
    validate_finite(x, "x")

    if not values:
        raise DistributionError("Sample cannot be empty.")

    return sum(value <= x for value in values) / len(values)


def ks_empirical_distance(
    values: Sequence[float],
    distribution: ContinuousDistribution,
) -> float:
    """
    Calculate the two-sided empirical CDF distance.

    This returns the KS statistic D, not a calibrated p-value.
    """

    if not values:
        raise DistributionError("Sample cannot be empty.")

    sorted_values = sorted(values)

    for value in sorted_values:
        validate_finite(value, "Observation")

    n = len(sorted_values)
    distance = 0.0

    for index, value in enumerate(sorted_values):
        theoretical = distribution.cdf(value)

        d_plus = (index + 1) / n - theoretical
        d_minus = theoretical - index / n

        distance = max(distance, d_plus, d_minus)

    return distance


def histogram(
    values: Sequence[float],
    bins: int = 10,
) -> list[tuple[float, float, int]]:
    if not values:
        raise DistributionError("Sample cannot be empty.")

    if isinstance(bins, bool) or not isinstance(bins, int) or bins <= 0:
        raise DistributionError("Bins must be a positive integer.")

    for value in values:
        validate_finite(value, "Observation")

    minimum = min(values)
    maximum = max(values)

    if minimum == maximum:
        return [(minimum, maximum, len(values))]

    width = (maximum - minimum) / bins
    counts = [0] * bins

    for value in values:
        index = min(int((value - minimum) / width), bins - 1)
        counts[index] += 1

    return [
        (
            minimum + i * width,
            minimum + (i + 1) * width,
            counts[i],
        )
        for i in range(bins)
    ]


def analyze_distribution(
    name: str,
    distribution: ContinuousDistribution,
    size: int,
    seed: int,
    lower: float,
    upper: float,
) -> list[float]:

    rng = random.Random(seed)
    values = distribution.sample(size, rng)
    stats = calculate_statistics(values)

    theoretical_probability = distribution.probability_between(
        lower, upper
    )

    observed_probability = empirical_probability(
        values,
        lambda x: lower <= x <= upper,
    )

    ci = confidence_interval_mean(values)

    print(f"\n{'=' * 65}")
    print(name)
    print("=" * 65)

    print(f"Sample size:                  {stats.count}")
    print(f"Theoretical mean:             {distribution.mean:.6f}")
    print(f"Empirical mean:               {stats.mean:.6f}")
    print(f"Theoretical variance:         {distribution.variance:.6f}")
    print(f"Empirical variance:           {stats.variance:.6f}")
    print(f"Empirical standard deviation: {stats.standard_deviation:.6f}")
    print(f"Minimum:                      {stats.minimum:.6f}")
    print(f"Maximum:                      {stats.maximum:.6f}")
    print(f"Median:                       {stats.median:.6f}")
    print(f"Theoretical interval P:       {theoretical_probability:.6f}")
    print(f"Empirical interval P:         {observed_probability:.6f}")
    print(f"Mean confidence interval:     ({ci[0]:.6f}, {ci[1]:.6f})")
    print(
        f"Empirical KS distance:        "
        f"{ks_empirical_distance(values, distribution):.6f}"
    )

    print("\nHistogram:")
    for start, end, count in histogram(values, 10):
        bar = "#" * min(count, 60)
        print(f"[{start:10.4f}, {end:10.4f}) {count:5d} {bar}")

    return values


def run_tests() -> None:
    uniform = UniformDistribution(0, 10)
    exponential = ExponentialDistribution(0.5)
    normal = NormalDistribution(100, 15)

    assert math.isclose(uniform.pdf(5), 0.1)
    assert math.isclose(uniform.cdf(5), 0.5)
    assert math.isclose(uniform.quantile(0.5), 5.0)

    assert exponential.pdf(-1) == 0.0
    assert math.isclose(exponential.cdf(2), 1 - math.exp(-1))
    assert math.isclose(exponential.quantile(0.5), math.log(2) / 0.5)
    assert math.isclose(exponential.survival_function(2), math.exp(-1))

    assert math.isclose(normal.pdf(100), 1 / (15 * math.sqrt(2 * math.pi)))
    assert math.isclose(normal.cdf(100), 0.5)
    assert math.isclose(normal.quantile(0.5), 100)
    assert math.isclose(normal.standardize(115), 1)

    assert math.isclose(normal_quantile_standard(0.975), 1.9599639845, abs_tol=1e-7)

    try:
        UniformDistribution(5, 5)
        raise AssertionError("Invalid uniform parameters were accepted.")
    except DistributionError:
        pass

    try:
        ExponentialDistribution(0)
        raise AssertionError("Invalid exponential rate was accepted.")
    except DistributionError:
        pass

    try:
        NormalDistribution(0, -1)
        raise AssertionError("Invalid normal standard deviation was accepted.")
    except DistributionError:
        pass

    try:
        uniform.quantile(1.5)
        raise AssertionError("Invalid probability was accepted.")
    except DistributionError:
        pass

    try:
        uniform.sample(0, random.Random(1))
        raise AssertionError("Invalid sample size was accepted.")
    except DistributionError:
        pass

    print("\nAll validation tests passed.")


def main() -> None:
    print("CONTINUOUS DISTRIBUTIONS: STATISTICAL ANALYSIS")
    print("Uniform, Exponential, and Normal")

    run_tests()

    sample_size = 100_000

    uniform = UniformDistribution(0, 100)
    exponential = ExponentialDistribution(0.2)
    normal = NormalDistribution(50, 10)

    analyze_distribution(
        "UNIFORM DISTRIBUTION",
        uniform,
        sample_size,
        42,
        20,
        80,
    )

    analyze_distribution(
        "EXPONENTIAL DISTRIBUTION",
        exponential,
        sample_size,
        42,
        1,
        5,
    )

    analyze_distribution(
        "NORMAL DISTRIBUTION",
        normal,
        sample_size,
        42,
        40,
        60,
    )

    print("\nQUANTILE COMPARISON")

    probabilities = [0.05, 0.25, 0.50, 0.75, 0.95]

    distributions = {
        "Uniform": uniform,
        "Exponential": exponential,
        "Normal": normal,
    }

    print(f"{'Probability':>12}", end="")
    for name in distributions:
        print(f"{name:>18}", end="")
    print()

    for probability in probabilities:
        print(f"{probability:12.2f}", end="")

        for distribution in distributions.values():
            print(f"{distribution.quantile(probability):18.4f}", end="")

        print()

    print("\nANALYSIS COMPLETED SUCCESSFULLY.")


if __name__ == "__main__":
    main()
