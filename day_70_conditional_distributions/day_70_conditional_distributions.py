"""
Conditional Distributions
=========================

Implements:
1. Joint and marginal probability distributions.
2. Conditional probability mass functions.
3. Conditional density for a bivariate normal distribution.
4. Conditional expectation.
5. Conditional variance.
6. Law of total expectation and total variance.
7. Numerical validation and simulation.
8. JSON export and reproducible examples.

Python 3.10+
Standard library only.
"""

from __future__ import annotations

import json
import math
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Hashable, Mapping, Optional, Tuple


class DistributionError(ValueError):
    """Raised when a probability distribution is invalid."""


def validate_probability(value: float, name: str = "probability") -> None:
    if not math.isfinite(value) or not 0.0 <= value <= 1.0:
        raise DistributionError(f"{name} must be between 0 and 1.")


@dataclass(frozen=True)
class ConditionalStatistics:
    condition: Hashable
    probability: float
    expectation: float
    variance: float


class DiscreteJointDistribution:
    """
    Represents a joint probability mass function P(X=x, Y=y).

    The internal dictionary maps (x, y) to joint probabilities.
    """

    def __init__(
        self,
        probabilities: Mapping[Tuple[Hashable, Hashable], float],
    ) -> None:
        if not probabilities:
            raise DistributionError("The joint distribution cannot be empty.")

        self.joint: Dict[Tuple[Hashable, Hashable], float] = {}

        for pair, probability in probabilities.items():
            if not isinstance(pair, tuple) or len(pair) != 2:
                raise DistributionError("Each outcome must be an (x, y) pair.")

            if not math.isfinite(probability) or probability < 0:
                raise DistributionError("Joint probabilities must be finite and nonnegative.")

            self.joint[pair] = float(probability)

        total = math.fsum(self.joint.values())

        if not math.isclose(total, 1.0, rel_tol=1e-10, abs_tol=1e-10):
            raise DistributionError(
                f"Joint probabilities must sum to 1. Found {total:.12f}."
            )

        self.x_values = tuple(dict.fromkeys(x for x, _ in self.joint))
        self.y_values = tuple(dict.fromkeys(y for _, y in self.joint))

    def joint_probability(self, x: Hashable, y: Hashable) -> float:
        return self.joint.get((x, y), 0.0)

    def marginal_x(self, x: Hashable) -> float:
        return math.fsum(
            probability
            for (x_value, _), probability in self.joint.items()
            if x_value == x
        )

    def marginal_y(self, y: Hashable) -> float:
        return math.fsum(
            probability
            for (_, y_value), probability in self.joint.items()
            if y_value == y
        )

    def conditional_pmf_y_given_x(
        self, x: Hashable
    ) -> Dict[Hashable, float]:
        denominator = self.marginal_x(x)

        if denominator <= 0:
            raise DistributionError(
                f"P(X={x}) is zero. Conditional distribution is undefined."
            )

        result = {
            y: self.joint_probability(x, y) / denominator
            for y in self.y_values
        }

        self._validate_conditional(result)
        return result

    def conditional_pmf_x_given_y(
        self, y: Hashable
    ) -> Dict[Hashable, float]:
        denominator = self.marginal_y(y)

        if denominator <= 0:
            raise DistributionError(
                f"P(Y={y}) is zero. Conditional distribution is undefined."
            )

        result = {
            x: self.joint_probability(x, y) / denominator
            for x in self.x_values
        }

        self._validate_conditional(result)
        return result

    @staticmethod
    def _validate_conditional(distribution: Mapping[Hashable, float]) -> None:
        total = math.fsum(distribution.values())

        if not math.isclose(total, 1.0, abs_tol=1e-10):
            raise DistributionError("Conditional probabilities do not sum to 1.")

    @staticmethod
    def expectation(
        distribution: Mapping[Hashable, float],
    ) -> float:
        if not distribution:
            raise DistributionError("Cannot calculate expectation of an empty distribution.")

        return math.fsum(
            float(value) * probability
            for value, probability in distribution.items()
        )

    @staticmethod
    def variance(
        distribution: Mapping[Hashable, float],
    ) -> float:
        mean = DiscreteJointDistribution.expectation(distribution)

        variance = math.fsum(
            (float(value) - mean) ** 2 * probability
            for value, probability in distribution.items()
        )

        return max(0.0, variance)

    def conditional_statistics(
        self, x: Hashable
    ) -> ConditionalStatistics:
        conditional = self.conditional_pmf_y_given_x(x)

        return ConditionalStatistics(
            condition=x,
            probability=self.marginal_x(x),
            expectation=self.expectation(conditional),
            variance=self.variance(conditional),
        )

    def conditional_covariance(self) -> float:
        """Calculate covariance of X and Y using the joint distribution."""

        mean_x = math.fsum(
            float(x) * probability
            for (x, _), probability in self.joint.items()
        )

        mean_y = math.fsum(
            float(y) * probability
            for (_, y), probability in self.joint.items()
        )

        return math.fsum(
            (float(x) - mean_x) * (float(y) - mean_y) * probability
            for (x, y), probability in self.joint.items()
        )

    def law_of_total_expectation(self) -> float:
        """
        E[Y] = E[E[Y | X]]
        """

        return math.fsum(
            self.marginal_x(x)
            * self.expectation(self.conditional_pmf_y_given_x(x))
            for x in self.x_values
            if self.marginal_x(x) > 0
        )

    def law_of_total_variance(self) -> float:
        """
        Var(Y) = E[Var(Y | X)] + Var(E[Y | X])
        """

        conditional_means = {}
        expected_conditional_variance = 0.0

        for x in self.x_values:
            probability = self.marginal_x(x)

            if probability == 0:
                continue

            conditional = self.conditional_pmf_y_given_x(x)

            conditional_means[x] = (
                self.expectation(conditional),
                probability,
            )

            expected_conditional_variance += (
                probability * self.variance(conditional)
            )

        mean_of_conditional_means = math.fsum(
            mean * probability
            for mean, probability in conditional_means.values()
        )

        variance_of_conditional_means = math.fsum(
            probability * (mean - mean_of_conditional_means) ** 2
            for mean, probability in conditional_means.values()
        )

        return (
            expected_conditional_variance
            + variance_of_conditional_means
        )

    def report(self) -> dict:
        results = {}

        for x in self.x_values:
            if self.marginal_x(x) == 0:
                continue

            conditional = self.conditional_pmf_y_given_x(x)
            statistics = self.conditional_statistics(x)

            results[str(x)] = {
                "P_X": self.marginal_x(x),
                "conditional_pmf": conditional,
                "conditional_expectation": statistics.expectation,
                "conditional_variance": statistics.variance,
            }

        return results


@dataclass(frozen=True)
class BivariateNormal:
    """
    Bivariate normal distribution.

    X and Y have means mu_x and mu_y, standard deviations
    sigma_x and sigma_y, and correlation rho.

    Y | X=x is normally distributed with:

    Conditional mean:
        mu_y + rho * sigma_y / sigma_x * (x - mu_x)

    Conditional variance:
        sigma_y^2 * (1 - rho^2)
    """

    mu_x: float
    mu_y: float
    sigma_x: float
    sigma_y: float
    rho: float

    def __post_init__(self) -> None:
        if not all(
            math.isfinite(value)
            for value in (
                self.mu_x,
                self.mu_y,
                self.sigma_x,
                self.sigma_y,
                self.rho,
            )
        ):
            raise DistributionError("All parameters must be finite.")

        if self.sigma_x <= 0 or self.sigma_y <= 0:
            raise DistributionError("Standard deviations must be positive.")

        if not -1.0 < self.rho < 1.0:
            raise DistributionError("Correlation must be strictly between -1 and 1.")

    def conditional_mean_y(self, x: float) -> float:
        if not math.isfinite(x):
            raise DistributionError("Conditioning value must be finite.")

        return (
            self.mu_y
            + self.rho
            * self.sigma_y
            / self.sigma_x
            * (x - self.mu_x)
        )

    def conditional_variance_y(self) -> float:
        return self.sigma_y**2 * (1.0 - self.rho**2)

    def conditional_std_y(self) -> float:
        return math.sqrt(self.conditional_variance_y())

    def conditional_density_y_given_x(
        self, y: float, x: float
    ) -> float:
        if not math.isfinite(y):
            raise DistributionError("Density evaluation point must be finite.")

        mean = self.conditional_mean_y(x)
        variance = self.conditional_variance_y()

        return (
            math.exp(-((y - mean) ** 2) / (2.0 * variance))
            / math.sqrt(2.0 * math.pi * variance)
        )

    def sample_conditional(
        self, x: float, count: int, seed: int = 42
    ) -> list[float]:
        if count <= 0:
            raise DistributionError("Sample count must be positive.")

        rng = random.Random(seed)

        return [
            rng.gauss(
                self.conditional_mean_y(x),
                self.conditional_std_y(),
            )
            for _ in range(count)
        ]


def run_examples() -> None:
    print("=" * 65)
    print("CONDITIONAL DISTRIBUTIONS")
    print("=" * 65)

    # Example 1: A joint distribution of study hours and exam outcome.
    # X = study category: 0, 1, 2
    # Y = exam outcome: 0, 1, 2

    probabilities = {
        (0, 0): 0.10,
        (0, 1): 0.10,
        (0, 2): 0.05,
        (1, 0): 0.05,
        (1, 1): 0.20,
        (1, 2): 0.15,
        (2, 0): 0.05,
        (2, 1): 0.10,
        (2, 2): 0.20,
    }

    distribution = DiscreteJointDistribution(probabilities)

    print("\n1. Joint and marginal distributions")

    for x in distribution.x_values:
        print(f"P(X={x}) = {distribution.marginal_x(x):.4f}")

    print("\n2. Conditional PMF: P(Y=y | X=1)")

    conditional = distribution.conditional_pmf_y_given_x(1)

    for y, probability in conditional.items():
        print(f"P(Y={y} | X=1) = {probability:.4f}")

    print("\n3. Conditional expectation and variance")

    statistics = distribution.conditional_statistics(1)

    print(f"E[Y | X=1] = {statistics.expectation:.4f}")
    print(f"Var(Y | X=1) = {statistics.variance:.4f}")

    print("\n4. Conditional statistics for every X")

    for x in distribution.x_values:
        statistics = distribution.conditional_statistics(x)

        print(
            f"X={x}: "
            f"P(X)={statistics.probability:.3f}, "
            f"E[Y|X]={statistics.expectation:.4f}, "
            f"Var(Y|X)={statistics.variance:.4f}"
        )

    print("\n5. Covariance")

    print(f"Cov(X,Y) = {distribution.conditional_covariance():.4f}")

    print("\n6. Law of total expectation")

    direct_expectation = math.fsum(
        float(y) * probability
        for (_, y), probability in distribution.joint.items()
    )

    conditional_expectation = distribution.law_of_total_expectation()

    print(f"Direct E[Y] = {direct_expectation:.4f}")
    print(f"E[E[Y|X]] = {conditional_expectation:.4f}")

    assert math.isclose(
        direct_expectation,
        conditional_expectation,
        abs_tol=1e-10,
    )

    print("\n7. Law of total variance")

    direct_variance = DiscreteJointDistribution.variance(
        {
            y: distribution.marginal_y(y)
            for y in distribution.y_values
        }
    )

    decomposed_variance = distribution.law_of_total_variance()

    print(f"Direct Var(Y) = {direct_variance:.4f}")
    print(f"Total variance decomposition = {decomposed_variance:.4f}")

    assert math.isclose(
        direct_variance,
        decomposed_variance,
        abs_tol=1e-10,
    )

    print("\n8. Continuous conditional density")

    normal = BivariateNormal(
        mu_x=10.0,
        mu_y=50.0,
        sigma_x=2.0,
        sigma_y=8.0,
        rho=0.75,
    )

    x = 12.0
    y = 58.0

    print(f"E[Y | X={x}] = {normal.conditional_mean_y(x):.4f}")
    print(f"Var(Y | X) = {normal.conditional_variance_y():.4f}")
    print(
        f"f(Y={y} | X={x}) = "
        f"{normal.conditional_density_y_given_x(y, x):.6f}"
    )

    print("\n9. Conditional simulation")

    samples = normal.sample_conditional(x, count=10000)

    sample_mean = math.fsum(samples) / len(samples)

    sample_variance = math.fsum(
        (value - sample_mean) ** 2 for value in samples
    ) / len(samples)

    print(f"Simulated conditional mean = {sample_mean:.4f}")
    print(f"Theoretical conditional mean = {normal.conditional_mean_y(x):.4f}")
    print(f"Simulated conditional variance = {sample_variance:.4f}")
    print(f"Theoretical conditional variance = {normal.conditional_variance_y():.4f}")

    # Monte Carlo values fluctuate, so use a tolerance.
    assert abs(sample_mean - normal.conditional_mean_y(x)) < 0.5

    print("\n10. Export conditional statistics")

    output = {
        "discrete_results": distribution.report(),
        "continuous_parameters": {
            "conditional_mean": normal.conditional_mean_y(x),
            "conditional_variance": normal.conditional_variance_y(),
            "conditional_density": normal.conditional_density_y_given_x(y, x),
        },
    }

    output_path = Path("conditional_distribution_results.json")

    output_path.write_text(
        json.dumps(output, indent=4),
        encoding="utf-8",
    )

    print(f"Results exported to {output_path.resolve()}")

    print("\n11. Validation and failure handling")

    try:
        distribution.conditional_pmf_y_given_x(99)
    except DistributionError as error:
        print(f"Expected conditioning failure: {error}")

    try:
        BivariateNormal(0, 0, 1, 1, 1.0)
    except DistributionError as error:
        print(f"Expected parameter failure: {error}")

    print("\nAll deterministic mathematical assertions passed.")


if __name__ == "__main__":
    run_examples()
