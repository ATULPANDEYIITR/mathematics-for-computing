"""
Central Limit Theorem: Sampling Distributions and Approximation Techniques

Demonstrates:
- Population distributions and population parameters
- Random sampling with and without replacement
- Sampling distributions of sample means
- Standard error and theoretical CLT behavior
- Normal approximation using the CLT
- Confidence intervals and empirical coverage
- Bootstrap percentile approximation
- Convergence analysis for different sample sizes
- Reproducible Monte Carlo simulation
- Input validation and CSV/JSON reporting

Python standard library only.
"""

from __future__ import annotations

import csv
import json
import math
import random
import statistics
from dataclasses import asdict, dataclass
from enum import Enum
from pathlib import Path
from typing import Callable, Sequence


OUTPUT_DIR = Path("clt_results")
SEED = 42


class DistributionType(Enum):
    BERNOULLI = "bernoulli"
    EXPONENTIAL = "exponential"
    UNIFORM = "uniform"
    SKEWED = "skewed"


class SamplingMethod(Enum):
    WITH_REPLACEMENT = "with_replacement"
    WITHOUT_REPLACEMENT = "without_replacement"


@dataclass(frozen=True)
class Population:
    name: str
    values: tuple[float, ...]
    distribution: DistributionType

    def __post_init__(self):
        if not self.values:
            raise ValueError("Population cannot be empty.")
        if any(not math.isfinite(x) for x in self.values):
            raise ValueError("Population values must be finite.")

    @property
    def mean(self) -> float:
        return statistics.fmean(self.values)

    @property
    def variance(self) -> float:
        return statistics.pvariance(self.values)

    @property
    def standard_deviation(self) -> float:
        return math.sqrt(self.variance)


@dataclass(frozen=True)
class SamplingResult:
    sample_size: int
    repetitions: int
    empirical_mean: float
    theoretical_mean: float
    empirical_sd: float
    theoretical_se: float
    normal_approximation_error: float
    confidence_interval_coverage: float


def validate_sample_size(n: int, population_size: int,
                         method: SamplingMethod) -> None:
    if not isinstance(n, int) or isinstance(n, bool) or n <= 0:
        raise ValueError("Sample size must be a positive integer.")

    if method == SamplingMethod.WITHOUT_REPLACEMENT:
        if n > population_size:
            raise ValueError("Sample size exceeds finite population.")


def normal_cdf(x: float) -> float:
    """Standard normal cumulative distribution function."""
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def normal_pdf(x: float) -> float:
    return math.exp(-0.5 * x * x) / math.sqrt(2.0 * math.pi)


def create_population(kind: DistributionType,
                      size: int = 10000,
                      seed: int = SEED) -> Population:
    if size <= 1:
        raise ValueError("Population size must exceed one.")

    rng = random.Random(seed)

    generators: dict[DistributionType, Callable[[], float]] = {
        DistributionType.BERNOULLI:
            lambda: float(rng.random() < 0.3),

        DistributionType.EXPONENTIAL:
            lambda: rng.expovariate(1.0),

        DistributionType.UNIFORM:
            lambda: rng.uniform(0.0, 100.0),

        DistributionType.SKEWED:
            lambda: rng.expovariate(0.5) ** 1.5,
    }

    values = tuple(generators[kind]() for _ in range(size))
    return Population(kind.value, values, kind)


def draw_sample(population: Population,
                n: int,
                method: SamplingMethod,
                rng: random.Random) -> list[float]:
    validate_sample_size(n, len(population.values), method)

    if method == SamplingMethod.WITH_REPLACEMENT:
        return rng.choices(population.values, k=n)

    return rng.sample(population.values, k=n)


def theoretical_standard_error(
    population: Population,
    n: int,
    method: SamplingMethod
) -> float:
    """
    Standard error of the sample mean.

    For simple random sampling without replacement, apply
    the finite population correction.
    """
    se = population.standard_deviation / math.sqrt(n)

    if method == SamplingMethod.WITHOUT_REPLACEMENT:
        correction = math.sqrt(
            (len(population.values) - n) /
            (len(population.values) - 1)
        )
        se *= correction

    return se


def monte_carlo_sampling_distribution(
    population: Population,
    sample_size: int,
    repetitions: int = 5000,
    method: SamplingMethod = SamplingMethod.WITH_REPLACEMENT,
    seed: int = SEED
) -> list[float]:
    if repetitions <= 1:
        raise ValueError("At least two repetitions are required.")

    validate_sample_size(sample_size, len(population.values), method)

    rng = random.Random(seed)
    means = []

    for _ in range(repetitions):
        sample = draw_sample(population, sample_size, method, rng)
        means.append(statistics.fmean(sample))

    return means


def confidence_interval(mean: float, standard_error: float,
                        z_value: float = 1.96) -> tuple[float, float]:
    if standard_error < 0 or z_value <= 0:
        raise ValueError("Invalid confidence interval parameters.")

    margin = z_value * standard_error
    return mean - margin, mean + margin


def bootstrap_interval(
    sample: Sequence[float],
    repetitions: int = 2000,
    confidence: float = 0.95,
    seed: int = SEED
) -> tuple[float, float]:
    if len(sample) < 2:
        raise ValueError("Bootstrap requires at least two observations.")

    if repetitions < 100:
        raise ValueError("Use at least 100 bootstrap repetitions.")

    if not 0 < confidence < 1:
        raise ValueError("Confidence must be between zero and one.")

    rng = random.Random(seed)
    means = [
        statistics.fmean(rng.choices(sample, k=len(sample)))
        for _ in range(repetitions)
    ]

    alpha = (1.0 - confidence) / 2.0

    return (
        statistics.quantiles(means, n=1000)[
            max(0, round(alpha * 1000) - 1)
        ],
        statistics.quantiles(means, n=1000)[
            min(998, round((1 - alpha) * 1000) - 1)
        ]
    )


def analyze_sampling_distribution(
    population: Population,
    sample_size: int,
    repetitions: int = 5000,
    method: SamplingMethod = SamplingMethod.WITH_REPLACEMENT,
    seed: int = SEED
) -> tuple[SamplingResult, list[float]]:
    means = monte_carlo_sampling_distribution(
        population, sample_size, repetitions, method, seed
    )

    empirical_mean = statistics.fmean(means)
    empirical_sd = statistics.stdev(means)

    theoretical_se = theoretical_standard_error(
        population, sample_size, method
    )

    if theoretical_se > 0:
        standardized_error = abs(
            empirical_sd - theoretical_se
        ) / theoretical_se
    else:
        standardized_error = 0.0

    z = 1.96
    covered = 0

    rng = random.Random(seed + 1)

    for _ in range(repetitions):
        sample = draw_sample(
            population, sample_size, method, rng
        )
        sample_mean = statistics.fmean(sample)

        sample_sd = statistics.stdev(sample) if sample_size > 1 else 0.0
        sample_se = sample_sd / math.sqrt(sample_size)

        if method == SamplingMethod.WITHOUT_REPLACEMENT:
            sample_se *= math.sqrt(
                (len(population.values) - sample_size) /
                (len(population.values) - 1)
            )

        lower, upper = confidence_interval(sample_mean, sample_se, z)

        if lower <= population.mean <= upper:
            covered += 1

    result = SamplingResult(
        sample_size=sample_size,
        repetitions=repetitions,
        empirical_mean=empirical_mean,
        theoretical_mean=population.mean,
        empirical_sd=empirical_sd,
        theoretical_se=theoretical_se,
        normal_approximation_error=standardized_error,
        confidence_interval_coverage=covered / repetitions
    )

    return result, means


def approximation_diagnostics(
    population: Population,
    sample_means: Sequence[float],
    theoretical_se: float
) -> dict:
    """
    Compare empirical sampling distribution with a normal model.

    The Kolmogorov-Smirnov distance is computed against the
    normal distribution with known population mean and CLT SE.
    """
    if theoretical_se == 0:
        return {
            "ks_distance": 0.0,
            "standardized_skewness": 0.0,
            "interpretation": "Degenerate sampling distribution"
        }

    ordered = sorted(sample_means)
    count = len(ordered)
    maximum_distance = 0.0

    for i, value in enumerate(ordered):
        z = (value - population.mean) / theoretical_se
        expected = normal_cdf(z)

        maximum_distance = max(
            maximum_distance,
            abs((i + 1) / count - expected),
            abs(i / count - expected)
        )

    empirical_sd = statistics.stdev(sample_means)

    if empirical_sd == 0:
        skewness = 0.0
    else:
        skewness = (
            sum((x - statistics.fmean(sample_means)) ** 3
                for x in sample_means) / count
        ) / empirical_sd ** 3

    return {
        "ks_distance": maximum_distance,
        "standardized_skewness": skewness,
        "interpretation": (
            "Approximation diagnostics, not a proof of normality"
        )
    }


def convergence_study(
    population: Population,
    sample_sizes: Sequence[int],
    repetitions: int = 3000
) -> list[dict]:
    results = []

    for n in sample_sizes:
        result, means = analyze_sampling_distribution(
            population, n, repetitions
        )

        diagnostics = approximation_diagnostics(
            population,
            means,
            result.theoretical_se
        )

        results.append({
            **asdict(result),
            **diagnostics
        })

    return results


def save_results(results: list[dict], directory: Path) -> None:
    directory.mkdir(parents=True, exist_ok=True)

    json_path = directory / "clt_results.json"
    csv_path = directory / "clt_results.csv"

    with json_path.open("w", encoding="utf-8") as file:
        json.dump(results, file, indent=4)

    if results:
        with csv_path.open("w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(
                file,
                fieldnames=list(results[0].keys())
            )
            writer.writeheader()
            writer.writerows(results)

    print(f"JSON report: {json_path.resolve()}")
    print(f"CSV report: {csv_path.resolve()}")


def run_tests() -> None:
    population = Population(
        "test",
        (1.0, 2.0, 3.0, 4.0),
        DistributionType.UNIFORM
    )

    assert math.isclose(population.mean, 2.5)
    assert math.isclose(normal_cdf(0), 0.5)
    assert normal_pdf(0) > 0

    try:
        validate_sample_size(5, 4, SamplingMethod.WITHOUT_REPLACEMENT)
        raise AssertionError("Expected sample-size validation failure.")
    except ValueError:
        pass

    try:
        confidence_interval(10, -1)
        raise AssertionError("Expected standard-error validation failure.")
    except ValueError:
        pass

    result, means = analyze_sampling_distribution(
        population, 2, 500
    )

    assert len(means) == 500
    assert abs(result.empirical_mean - population.mean) < 0.5


def main() -> None:
    run_tests()

    print("=" * 72)
    print("CENTRAL LIMIT THEOREM: MONTE CARLO EXPERIMENT")
    print("=" * 72)

    populations = [
        create_population(DistributionType.BERNOULLI),
        create_population(DistributionType.EXPONENTIAL),
        create_population(DistributionType.SKEWED),
        create_population(DistributionType.UNIFORM)
    ]

    all_results = []

    sample_sizes = [2, 5, 10, 30, 50, 100]

    for population in populations:
        print(f"\nPopulation: {population.name}")
        print(f"Population mean: {population.mean:.4f}")
        print(f"Population SD: {population.standard_deviation:.4f}")

        results = convergence_study(
            population, sample_sizes
        )

        for item in results:
            print(
                f"n={item['sample_size']:3d} | "
                f"Mean={item['empirical_mean']:.4f} | "
                f"SE={item['empirical_sd']:.4f} | "
                f"Theoretical SE={item['theoretical_se']:.4f} | "
                f"KS={item['ks_distance']:.4f} | "
                f"Coverage={item['confidence_interval_coverage']:.3f}"
            )

            item["population"] = population.name
            all_results.append(item)

    sample = draw_sample(
        populations[1],
        50,
        SamplingMethod.WITH_REPLACEMENT,
        random.Random(SEED)
    )

    lower, upper = bootstrap_interval(sample)

    print("\nBootstrap percentile interval:")
    print(f"Lower: {lower:.4f}")
    print(f"Upper: {upper:.4f}")

    save_results(all_results, OUTPUT_DIR)


if __name__ == "__main__":
    main()
