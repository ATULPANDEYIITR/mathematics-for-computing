"""
Joint Distributions
-------------------
Implements:
1. Discrete joint probability mass functions (Joint PMF).
2. Continuous bivariate probability density functions (Joint PDF).
3. Marginal distributions.
4. Conditional distributions.
5. Expected values and variances.
6. Covariance and correlation.
7. Independence testing.
8. Bivariate normal distribution.
9. Validation and numerical tests.

Python 3.10+
Standard library only.
"""

from dataclasses import dataclass
from math import exp, log, pi, sqrt
from collections import defaultdict
from typing import Dict, Tuple, Iterable


class DistributionError(ValueError):
    """Raised when a probability distribution is invalid."""


@dataclass(frozen=True)
class JointOutcome:
    x: float
    y: float
    probability: float


class DiscreteJointDistribution:
    """Represents a finite discrete joint probability distribution."""

    def __init__(
        self,
        outcomes: Iterable[JointOutcome],
        tolerance: float = 1e-10
    ):
        self.tolerance = tolerance
        self.pmf: Dict[Tuple[float, float], float] = {}

        for outcome in outcomes:
            x = float(outcome.x)
            y = float(outcome.y)
            probability = float(outcome.probability)

            if not all(map(lambda v: v == v and abs(v) != float("inf"),
                           (x, y, probability))):
                raise DistributionError("Values must be finite.")

            if probability < 0:
                raise DistributionError("Probability cannot be negative.")

            key = (x, y)

            if key in self.pmf:
                raise DistributionError(
                    f"Duplicate outcome: {key}"
                )

            self.pmf[key] = probability

        if not self.pmf:
            raise DistributionError("Distribution cannot be empty.")

        total = sum(self.pmf.values())

        if abs(total - 1.0) > tolerance:
            raise DistributionError(
                f"Probabilities must sum to 1. Found {total:.12f}."
            )

        # Remove negligible floating-point normalization differences.
        self.pmf = {
            key: probability / total
            for key, probability in self.pmf.items()
        }

    def joint_probability(self, x: float, y: float) -> float:
        return self.pmf.get((float(x), float(y)), 0.0)

    def marginal_x(self) -> Dict[float, float]:
        result = defaultdict(float)

        for (x, _), probability in self.pmf.items():
            result[x] += probability

        return dict(sorted(result.items()))

    def marginal_y(self) -> Dict[float, float]:
        result = defaultdict(float)

        for (_, y), probability in self.pmf.items():
            result[y] += probability

        return dict(sorted(result.items()))

    def conditional_y_given_x(
        self,
        x: float
    ) -> Dict[float, float]:
        marginal = self.marginal_x().get(float(x), 0.0)

        if marginal == 0:
            raise DistributionError(
                f"P(X={x}) is zero; conditional distribution undefined."
            )

        result = {}

        for (outcome_x, outcome_y), probability in self.pmf.items():
            if outcome_x == float(x):
                result[outcome_y] = probability / marginal

        return dict(sorted(result.items()))

    def conditional_x_given_y(
        self,
        y: float
    ) -> Dict[float, float]:
        marginal = self.marginal_y().get(float(y), 0.0)

        if marginal == 0:
            raise DistributionError(
                f"P(Y={y}) is zero; conditional distribution undefined."
            )

        result = {}

        for (outcome_x, outcome_y), probability in self.pmf.items():
            if outcome_y == float(y):
                result[outcome_x] = probability / marginal

        return dict(sorted(result.items()))

    @staticmethod
    def expectation(distribution: Dict[float, float]) -> float:
        return sum(value * probability
                   for value, probability in distribution.items())

    def expected_x(self) -> float:
        return self.expectation(self.marginal_x())

    def expected_y(self) -> float:
        return self.expectation(self.marginal_y())

    @staticmethod
    def variance(distribution: Dict[float, float]) -> float:
        mean = DiscreteJointDistribution.expectation(distribution)

        return sum(
            probability * (value - mean) ** 2
            for value, probability in distribution.items()
        )

    def variance_x(self) -> float:
        return self.variance(self.marginal_x())

    def variance_y(self) -> float:
        return self.variance(self.marginal_y())

    def expected_xy(self) -> float:
        return sum(
            x * y * probability
            for (x, y), probability in self.pmf.items()
        )

    def covariance(self) -> float:
        return self.expected_xy() - (
            self.expected_x() * self.expected_y()
        )

    def correlation(self) -> float:
        denominator = sqrt(self.variance_x() * self.variance_y())

        if denominator == 0:
            raise DistributionError(
                "Correlation undefined when either variable has zero variance."
            )

        return self.covariance() / denominator

    def are_independent(
        self,
        tolerance: float = 1e-9
    ) -> bool:
        marginal_x = self.marginal_x()
        marginal_y = self.marginal_y()

        for (x, y), probability in self.pmf.items():
            expected = marginal_x[x] * marginal_y[y]

            if abs(probability - expected) > tolerance:
                return False

        # Also check combinations absent from the joint support.
        for x, px in marginal_x.items():
            for y, py in marginal_y.items():
                if abs(self.joint_probability(x, y) - px * py) > tolerance:
                    return False

        return True

    def display(self):
        print("\nJoint PMF")
        print("-" * 40)

        for (x, y), probability in sorted(self.pmf.items()):
            print(f"P(X={x}, Y={y}) = {probability:.4f}")

        print("\nMarginal distribution of X")
        print(self.marginal_x())

        print("\nMarginal distribution of Y")
        print(self.marginal_y())

        print("\nStatistical measures")
        print(f"E[X]       : {self.expected_x():.6f}")
        print(f"E[Y]       : {self.expected_y():.6f}")
        print(f"Var(X)     : {self.variance_x():.6f}")
        print(f"Var(Y)     : {self.variance_y():.6f}")
        print(f"E[XY]      : {self.expected_xy():.6f}")
        print(f"Cov(X,Y)   : {self.covariance():.6f}")
        print(f"Correlation: {self.correlation():.6f}")
        print(f"Independent: {self.are_independent()}")


class BivariateNormal:
    """Bivariate normal probability density function."""

    def __init__(
        self,
        mean_x: float,
        mean_y: float,
        sigma_x: float,
        sigma_y: float,
        rho: float
    ):
        values = (mean_x, mean_y, sigma_x, sigma_y, rho)

        if not all(
            value == value and abs(value) != float("inf")
            for value in values
        ):
            raise DistributionError("Parameters must be finite.")

        if sigma_x <= 0 or sigma_y <= 0:
            raise DistributionError(
                "Standard deviations must be positive."
            )

        if not -1 < rho < 1:
            raise DistributionError(
                "Correlation must lie strictly between -1 and 1."
            )

        self.mean_x = mean_x
        self.mean_y = mean_y
        self.sigma_x = sigma_x
        self.sigma_y = sigma_y
        self.rho = rho

    def pdf(self, x: float, y: float) -> float:
        zx = (x - self.mean_x) / self.sigma_x
        zy = (y - self.mean_y) / self.sigma_y

        exponent = -(
            zx ** 2
            - 2 * self.rho * zx * zy
            + zy ** 2
        ) / (2 * (1 - self.rho ** 2))

        denominator = (
            2 * pi * self.sigma_x * self.sigma_y
            * sqrt(1 - self.rho ** 2)
        )

        return exp(exponent) / denominator

    def covariance(self) -> float:
        return self.rho * self.sigma_x * self.sigma_y

    def marginal_x_pdf(self, x: float) -> float:
        z = (x - self.mean_x) / self.sigma_x

        return exp(-0.5 * z ** 2) / (
            self.sigma_x * sqrt(2 * pi)
        )

    def marginal_y_pdf(self, y: float) -> float:
        z = (y - self.mean_y) / self.sigma_y

        return exp(-0.5 * z ** 2) / (
            self.sigma_y * sqrt(2 * pi)
        )


def demonstrate_discrete_distribution():
    """
    Example:
    X = employee training level.
    Y = assessment result.

    The probabilities represent a valid joint PMF.
    """

    outcomes = [
        JointOutcome(0, 0, 0.10),
        JointOutcome(0, 1, 0.15),
        JointOutcome(1, 0, 0.20),
        JointOutcome(1, 1, 0.30),
        JointOutcome(2, 0, 0.05),
        JointOutcome(2, 1, 0.20),
    ]

    distribution = DiscreteJointDistribution(outcomes)
    distribution.display()

    print("\nConditional distribution P(Y | X=1)")
    print(distribution.conditional_y_given_x(1))

    print("\nConditional distribution P(X | Y=1)")
    print(distribution.conditional_x_given_y(1))

    return distribution


def demonstrate_continuous_distribution():
    print("\nBivariate Normal Distribution")
    print("-" * 40)

    distribution = BivariateNormal(
        mean_x=70.0,
        mean_y=75.0,
        sigma_x=10.0,
        sigma_y=12.0,
        rho=0.65
    )

    print(f"Joint PDF at (70, 75): {distribution.pdf(70, 75):.8f}")
    print(f"Joint PDF at (80, 85): {distribution.pdf(80, 85):.8f}")

    print(
        f"Marginal PDF of X at 70: "
        f"{distribution.marginal_x_pdf(70):.8f}"
    )

    print(
        f"Marginal PDF of Y at 75: "
        f"{distribution.marginal_y_pdf(75):.8f}"
    )

    print(f"Covariance: {distribution.covariance():.4f}")
    print(f"Correlation: {distribution.rho:.4f}")


def run_tests():
    distribution = DiscreteJointDistribution([
        JointOutcome(0, 0, 0.25),
        JointOutcome(0, 1, 0.25),
        JointOutcome(1, 0, 0.25),
        JointOutcome(1, 1, 0.25),
    ])

    assert abs(distribution.expected_x() - 0.5) < 1e-10
    assert abs(distribution.expected_y() - 0.5) < 1e-10
    assert abs(distribution.variance_x() - 0.25) < 1e-10
    assert abs(distribution.covariance()) < 1e-10
    assert abs(distribution.correlation()) < 1e-10
    assert distribution.are_independent()

    dependent = DiscreteJointDistribution([
        JointOutcome(0, 0, 0.5),
        JointOutcome(1, 1, 0.5),
    ])

    assert not dependent.are_independent()
    assert abs(dependent.correlation() - 1.0) < 1e-10

    try:
        DiscreteJointDistribution([
            JointOutcome(0, 0, 0.4),
            JointOutcome(1, 1, 0.4),
        ])
    except DistributionError:
        pass
    else:
        raise AssertionError("Invalid probability total was accepted.")

    try:
        distribution.conditional_y_given_x(5)
    except DistributionError:
        pass
    else:
        raise AssertionError("Undefined conditional PMF was accepted.")

    print("\nAll validation tests passed.")


def main():
    print("=" * 55)
    print("JOINT DISTRIBUTION ANALYSIS")
    print("=" * 55)

    demonstrate_discrete_distribution()
    demonstrate_continuous_distribution()
    run_tests()


if __name__ == "__main__":
    main()
