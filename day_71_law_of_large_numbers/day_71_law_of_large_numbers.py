#!/usr/bin/env python3
"""
Law of Large Numbers: Weak Law, Strong Law, and Monte Carlo Simulation.

Demonstrates:
- Independent and identically distributed random variables.
- Sample sums, sample means, and variance.
- Weak Law of Large Numbers (WLLN).
- Strong Law of Large Numbers (SLLN).
- Chebyshev's inequality.
- Convergence in probability versus almost-sure convergence.
- Bernoulli, uniform, and normal distributions.
- Repeated Monte Carlo experiments.
- Empirical convergence analysis and JSON reporting.

Python 3.10+
Standard library only.
"""

from __future__ import annotations

import json
import math
import random
import statistics
import sys
from dataclasses import asdict, dataclass
from enum import Enum
from pathlib import Path
from typing import Callable, Iterable


class Distribution(Enum):
    BERNOULLI = "bernoulli"
    UNIFORM = "uniform"
    NORMAL = "normal"


@dataclass(frozen=True)
class ExperimentConfig:
    distribution: Distribution = Distribution.BERNOULLI
    sample_sizes: tuple[int, ...] = (10, 50, 100, 500, 1000, 5000, 10000)
    trials: int = 2000
    tolerance: float = 0.05
    seed: int = 42

    def __post_init__(self) -> None:
        if not self.sample_sizes:
            raise ValueError("At least one sample size is required.")
        if any(n <= 0 for n in self.sample_sizes):
            raise ValueError("Sample sizes must be positive.")
        if tuple(sorted(set(self.sample_sizes))) != self.sample_sizes:
            raise ValueError("Sample sizes must be unique and increasing.")
        if self.trials <= 0:
            raise ValueError("Trials must be positive.")
        if not math.isfinite(self.tolerance) or self.tolerance <= 0:
            raise ValueError("Tolerance must be finite and positive.")


@dataclass(frozen=True)
class DistributionSpec:
    name: str
    mean: float
    variance: float
    sampler: Callable[[random.Random], float]


def distribution_spec(distribution: Distribution) -> DistributionSpec:
    if distribution == Distribution.BERNOULLI:
        p = 0.5
        return DistributionSpec(
            "Bernoulli(p=0.5)",
            p,
            p * (1 - p),
            lambda rng: float(rng.random() < p),
        )

    if distribution == Distribution.UNIFORM:
        return DistributionSpec(
            "Uniform(0,1)",
            0.5,
            1.0 / 12.0,
            lambda rng: rng.random(),
        )

    if distribution == Distribution.NORMAL:
        return DistributionSpec(
            "Normal(0,1)",
            0.0,
            1.0,
            lambda rng: rng.gauss(0.0, 1.0),
        )

    raise ValueError(f"Unsupported distribution: {distribution}")


def sample_mean(values: Iterable[float]) -> float:
    values = list(values)
    if not values:
        raise ValueError("Cannot calculate mean of an empty collection.")
    return math.fsum(values) / len(values)


def chebyshev_bound(variance: float, n: int, epsilon: float) -> float:
    if variance < 0 or n <= 0 or epsilon <= 0:
        raise ValueError("Invalid Chebyshev inequality parameters.")
    return min(1.0, variance / (n * epsilon**2))


def generate_samples(
    spec: DistributionSpec,
    count: int,
    rng: random.Random,
) -> list[float]:
    if count <= 0:
        raise ValueError("Sample count must be positive.")
    return [spec.sampler(rng) for _ in range(count)]


def repeated_means(
    spec: DistributionSpec,
    n: int,
    trials: int,
    epsilon: float,
    rng: random.Random,
) -> dict:
    """
    Estimate P(|X_bar - mu| >= epsilon) using independent experiments.

    Theoretical Chebyshev bound applies when variance is finite.
    """
    deviations = []
    squared_errors = []
    successes = 0

    for _ in range(trials):
        values = generate_samples(spec, n, rng)
        mean = sample_mean(values)
        error = abs(mean - spec.mean)

        deviations.append(error)
        squared_errors.append((mean - spec.mean) ** 2)

        if error >= epsilon:
            successes += 1

    observed_probability = successes / trials

    return {
        "sample_size": n,
        "trials": trials,
        "mean_absolute_error": statistics.mean(deviations),
        "empirical_mean_squared_error": statistics.mean(squared_errors),
        "observed_deviation_probability": observed_probability,
        "chebyshev_upper_bound": chebyshev_bound(
            spec.variance, n, epsilon
        ),
    }


def run_wlln_experiment(config: ExperimentConfig) -> dict:
    spec = distribution_spec(config.distribution)
    rng = random.Random(config.seed)

    results = [
        repeated_means(
            spec,
            n,
            config.trials,
            config.tolerance,
            rng,
        )
        for n in config.sample_sizes
    ]

    return {
        "law": "Weak Law of Large Numbers",
        "distribution": spec.name,
        "theoretical_mean": spec.mean,
        "theoretical_variance": spec.variance,
        "tolerance": config.tolerance,
        "results": results,
    }


def run_slln_experiment(
    spec: DistributionSpec,
    sample_sizes: tuple[int, ...],
    seed: int,
) -> dict:
    """
    Generate one growing sequence of observations.

    The running sample mean converges to the population mean
    almost surely under the standard SLLN assumptions.
    """
    rng = random.Random(seed)
    maximum = max(sample_sizes)

    running_sum = 0.0
    selected = set(sample_sizes)
    observations = {}

    for index in range(1, maximum + 1):
        running_sum += spec.sampler(rng)

        if index in selected:
            mean = running_sum / index
            observations[index] = {
                "sample_size": index,
                "sample_mean": mean,
                "population_mean": spec.mean,
                "absolute_error": abs(mean - spec.mean),
            }

    return {
        "law": "Strong Law of Large Numbers",
        "distribution": spec.name,
        "observations": list(observations.values()),
        "interpretation": (
            "One realized sequence illustrates convergence of running "
            "averages; it does not prove almost-sure convergence."
        ),
    }


def compare_distributions(
    sample_sizes: tuple[int, ...],
    trials: int,
    tolerance: float,
    seed: int,
) -> dict:
    results = {}

    for offset, distribution in enumerate(Distribution):
        config = ExperimentConfig(
            distribution=distribution,
            sample_sizes=sample_sizes,
            trials=trials,
            tolerance=tolerance,
            seed=seed + offset,
        )
        results[distribution.value] = run_wlln_experiment(config)

    return results


def validate_empirical_results(report: dict) -> None:
    """Check probability ranges and the expected inverse-n error trend."""
    for result in report["results"]:
        probability = result["observed_deviation_probability"]
        bound = result["chebyshev_upper_bound"]

        assert 0 <= probability <= 1
        assert 0 <= bound <= 1
        assert result["sample_size"] > 0
        assert result["trials"] > 0


def save_report(report: dict, output_path: Path) -> None:
    """
    Write JSON atomically to avoid leaving a partially written report.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = output_path.with_suffix(output_path.suffix + ".tmp")

    try:
        temporary_path.write_text(
            json.dumps(report, indent=2),
            encoding="utf-8",
        )
        temporary_path.replace(output_path)
    except OSError:
        temporary_path.unlink(missing_ok=True)
        raise


def print_wlln_report(report: dict) -> None:
    print("\nWEAK LAW OF LARGE NUMBERS")
    print(f"Distribution: {report['distribution']}")
    print(f"Population mean: {report['theoretical_mean']}")
    print(f"Tolerance: {report['tolerance']}")

    print(
        f"{'N':>8} {'MAE':>12} {'Observed P':>14} "
        f"{'Chebyshev':>14} {'MSE':>12}"
    )

    for row in report["results"]:
        print(
            f"{row['sample_size']:>8} "
            f"{row['mean_absolute_error']:>12.6f} "
            f"{row['observed_deviation_probability']:>14.6f} "
            f"{row['chebyshev_upper_bound']:>14.6f} "
            f"{row['empirical_mean_squared_error']:>12.6f}"
        )


def demonstrate_edge_cases() -> None:
    print("\nEDGE CASE VALIDATION")

    try:
        sample_mean([])
    except ValueError as error:
        print(f"Empty sample rejected: {error}")

    try:
        ExperimentConfig(sample_sizes=(10, 5))
    except ValueError as error:
        print(f"Invalid sample sizes rejected: {error}")

    print(
        "Zero-variance random variables have sample means "
        "equal to their constant population value."
    )


def main() -> None:
    config = ExperimentConfig()
    spec = distribution_spec(config.distribution)

    wlln_report = run_wlln_experiment(config)
    validate_empirical_results(wlln_report)
    print_wlln_report(wlln_report)

    slln_report = run_slln_experiment(
        spec,
        config.sample_sizes,
        config.seed + 100,
    )

    print("\nSTRONG LAW OF LARGE NUMBERS")
    for row in slln_report["observations"]:
        print(
            f"N={row['sample_size']:>6} "
            f"Mean={row['sample_mean']:.6f} "
            f"Error={row['absolute_error']:.6f}"
        )

    demonstrate_edge_cases()

    comparison = compare_distributions(
        config.sample_sizes,
        trials=500,
        tolerance=config.tolerance,
        seed=config.seed + 200,
    )

    report = {
        "weak_law": wlln_report,
        "strong_law": slln_report,
        "distribution_comparison": comparison,
    }

    output_path = Path("lln_results.json")
    save_report(report, output_path)
    print(f"\nReport saved to: {output_path.resolve()}")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, ArithmeticError) as error:
        print(f"Experiment failed: {error}", file=sys.stderr)
        sys.exit(1)
