#!/usr/bin/env python3
"""
Advanced Distributions
Poisson, Gamma, Beta, and Chi-square distributions.

Standard-library implementation covering:
- Probability mass and density functions
- Cumulative distribution functions
- Parameter validation
- Random sampling
- Statistical moments
- Confidence and Bayesian calculations
- Chi-square goodness-of-fit testing
- Numerical edge cases and assertions

Run:
    python advanced_distributions.py
"""

from __future__ import annotations

import math
import random
import statistics
from dataclasses import dataclass
from enum import Enum
from typing import Callable, Sequence


EPSILON = 1e-12
MAX_ITERATIONS = 10000


class DistributionType(Enum):
    POISSON = "Poisson"
    GAMMA = "Gamma"
    BETA = "Beta"
    CHI_SQUARE = "Chi-square"


class StatisticalError(ValueError):
    """Raised when a statistical operation receives invalid input."""


def validate_positive(value: float, name: str) -> None:
    if not math.isfinite(value) or value <= 0:
        raise StatisticalError(f"{name} must be finite and positive.")


def validate_probability(value: float, name: str = "probability") -> None:
    if not math.isfinite(value) or not 0 <= value <= 1:
        raise StatisticalError(f"{name} must be between 0 and 1.")


def validate_nonnegative(value: float, name: str) -> None:
    if not math.isfinite(value) or value < 0:
        raise StatisticalError(f"{name} must be finite and nonnegative.")


def regularized_gamma_p(a: float, x: float) -> float:
    """
    Regularized lower incomplete gamma function P(a, x).

    Uses a convergent series for x < a + 1 and a
    continued fraction for the complementary probability.
    """
    validate_positive(a, "Shape parameter")
    validate_nonnegative(x, "x")

    if x == 0:
        return 0.0

    if math.isinf(x):
        return 1.0

    log_factor = a * math.log(x) - x - math.lgamma(a)

    if x < a + 1:
        term = 1.0 / a
        total = term
        ap = a

        for _ in range(MAX_ITERATIONS):
            ap += 1
            term *= x / ap
            total += term

            if abs(term) <= abs(total) * EPSILON:
                return min(1.0, max(0.0, total * math.exp(log_factor)))

        raise ArithmeticError("Gamma series did not converge.")

    b = x + 1 - a
    c = 1.0 / 1e-300
    d = 1.0 / b
    h = d

    for i in range(1, MAX_ITERATIONS + 1):
        an = -i * (i - a)
        b += 2

        d = an * d + b
        if abs(d) < 1e-300:
            d = 1e-300

        c = b + an / c
        if abs(c) < 1e-300:
            c = 1e-300

        d = 1.0 / d
        delta = d * c
        h *= delta

        if abs(delta - 1.0) <= EPSILON:
            q = math.exp(log_factor) * h
            return min(1.0, max(0.0, 1.0 - q))

    raise ArithmeticError("Gamma continued fraction did not converge.")


def regularized_beta(x: float, a: float, b: float) -> float:
    """
    Regularized incomplete beta function I_x(a, b).
    Uses a continued fraction with symmetry for numerical stability.
    """
    validate_positive(a, "Alpha")
    validate_positive(b, "Beta")

    if not math.isfinite(x) or not 0 <= x <= 1:
        raise StatisticalError("x must be between 0 and 1.")

    if x == 0:
        return 0.0

    if x == 1:
        return 1.0

    def continued_fraction(aa: float, bb: float, xx: float) -> float:
        qab = aa + bb
        qap = aa + 1
        qam = aa - 1

        c = 1.0
        d = 1.0 - qab * xx / qap

        if abs(d) < 1e-300:
            d = 1e-300

        d = 1.0 / d
        h = d

        for m in range(1, MAX_ITERATIONS + 1):
            m2 = 2 * m

            term = (
                m * (bb - m) * xx
                / ((qam + m2) * (aa + m2))
            )

            d = 1 + term * d
            if abs(d) < 1e-300:
                d = 1e-300

            c = 1 + term / c
            if abs(c) < 1e-300:
                c = 1e-300

            d = 1 / d
            h *= d * c

            term = (
                -(aa + m) * (qab + m) * xx
                / ((aa + m2) * (qap + m2))
            )

            d = 1 + term * d
            if abs(d) < 1e-300:
                d = 1e-300

            c = 1 + term / c
            if abs(c) < 1e-300:
                c = 1e-300

            d = 1 / d
            delta = d * c
            h *= delta

            if abs(delta - 1) <= EPSILON:
                return h

        raise ArithmeticError("Beta continued fraction did not converge.")

    factor = math.exp(
        math.lgamma(a + b)
        - math.lgamma(a)
        - math.lgamma(b)
        + a * math.log(x)
        + b * math.log1p(-x)
    )

    if x < (a + 1) / (a + b + 2):
        result = factor * continued_fraction(a, b, x) / a
    else:
        result = (
            1
            - factor * continued_fraction(b, a, 1 - x) / b
        )

    return min(1.0, max(0.0, result))


@dataclass(frozen=True)
class PoissonDistribution:
    """
    Discrete distribution for event counts in a fixed interval.

    lambda_rate: expected number of events per interval.
    """

    lambda_rate: float

    def __post_init__(self):
        validate_positive(self.lambda_rate, "Lambda")

    def pmf(self, k: int) -> float:
        if isinstance(k, bool) or not isinstance(k, int):
            raise StatisticalError("k must be an integer.")

        if k < 0:
            return 0.0

        return math.exp(
            k * math.log(self.lambda_rate)
            - self.lambda_rate
            - math.lgamma(k + 1)
        )

    def cdf(self, k: int) -> float:
        if isinstance(k, bool) or not isinstance(k, int):
            raise StatisticalError("k must be an integer.")

        if k < 0:
            return 0.0

        return regularized_gamma_p(k + 1, self.lambda_rate)

    @property
    def mean(self) -> float:
        return self.lambda_rate

    @property
    def variance(self) -> float:
        return self.lambda_rate

    def sample(self, rng: random.Random | None = None) -> int:
        return (rng or random).poisson(self.lambda_rate) if hasattr(
            rng or random, "poisson"
        ) else _poisson_sample(self.lambda_rate, rng or random)


def _poisson_sample(rate: float, rng) -> int:
    """Knuth sampling for small rates and transformed rejection for large rates."""
    if rate < 30:
        limit = math.exp(-rate)
        product = 1.0
        count = 0

        while product > limit:
            count += 1
            product *= rng.random()

        return count - 1

    # PTRS transformed rejection algorithm.
    sqrt_rate = math.sqrt(rate)
    b = 0.931 + 2.53 * sqrt_rate
    a = -0.059 + 0.02483 * b
    inverse_alpha = 1.1239 + 1.1328 / (b - 3.4)
    vr = 0.9277 - 3.6224 / (b - 2)

    while True:
        u = rng.random() - 0.5
        v = rng.random()
        us = 0.5 - abs(u)

        if us <= 0:
            continue

        k = math.floor((2 * a / us + b) * u + rate + 0.43)

        if us >= 0.07 and v <= vr and k >= 0:
            return k

        if k < 0 or (us < 0.013 and v > us):
            continue

        lhs = math.log(v * inverse_alpha / (a / (us * us) + b))
        rhs = -rate + k * math.log(rate) - math.lgamma(k + 1)

        if lhs <= rhs:
            return k


@dataclass(frozen=True)
class GammaDistribution:
    """Continuous positive distribution parameterized by shape and scale."""

    shape: float
    scale: float

    def __post_init__(self):
        validate_positive(self.shape, "Shape")
        validate_positive(self.scale, "Scale")

    def pdf(self, x: float) -> float:
        if x < 0:
            return 0.0

        if x == 0:
            if self.shape < 1:
                return math.inf
            if self.shape == 1:
                return 1 / self.scale
            return 0.0

        log_density = (
            (self.shape - 1) * math.log(x)
            - x / self.scale
            - math.lgamma(self.shape)
            - self.shape * math.log(self.scale)
        )

        return math.exp(log_density)

    def cdf(self, x: float) -> float:
        if x <= 0:
            return 0.0

        return regularized_gamma_p(
            self.shape,
            x / self.scale
        )

    @property
    def mean(self) -> float:
        return self.shape * self.scale

    @property
    def variance(self) -> float:
        return self.shape * self.scale ** 2

    def sample(self, rng: random.Random | None = None) -> float:
        return (rng or random).gammavariate(self.shape, self.scale)


@dataclass(frozen=True)
class BetaDistribution:
    """Probability distribution bounded by zero and one."""

    alpha: float
    beta: float

    def __post_init__(self):
        validate_positive(self.alpha, "Alpha")
        validate_positive(self.beta, "Beta")

    def pdf(self, x: float) -> float:
        if x < 0 or x > 1:
            return 0.0

        if x == 0:
            return (
                math.inf if self.alpha < 1
                else 0.0 if self.alpha > 1
                else math.exp(
                    math.lgamma(self.alpha + self.beta)
                    - math.lgamma(self.alpha)
                    - math.lgamma(self.beta)
                )
            )

        if x == 1:
            return (
                math.inf if self.beta < 1
                else 0.0 if self.beta > 1
                else math.exp(
                    math.lgamma(self.alpha + self.beta)
                    - math.lgamma(self.alpha)
                    - math.lgamma(self.beta)
                )
            )

        log_density = (
            (self.alpha - 1) * math.log(x)
            + (self.beta - 1) * math.log1p(-x)
            + math.lgamma(self.alpha + self.beta)
            - math.lgamma(self.alpha)
            - math.lgamma(self.beta)
        )

        return math.exp(log_density)

    def cdf(self, x: float) -> float:
        return regularized_beta(x, self.alpha, self.beta)

    @property
    def mean(self) -> float:
        return self.alpha / (self.alpha + self.beta)

    @property
    def variance(self) -> float:
        total = self.alpha + self.beta
        return self.alpha * self.beta / (
            total ** 2 * (total + 1)
        )

    def sample(self, rng: random.Random | None = None) -> float:
        return (rng or random).betavariate(self.alpha, self.beta)


@dataclass(frozen=True)
class ChiSquareDistribution:
    """Chi-square distribution with degrees of freedom."""

    degrees_of_freedom: float

    def __post_init__(self):
        validate_positive(self.degrees_of_freedom, "Degrees of freedom")

    def pdf(self, x: float) -> float:
        if x < 0:
            return 0.0

        if x == 0:
            if self.degrees_of_freedom < 2:
                return math.inf
            if self.degrees_of_freedom == 2:
                return 0.5
            return 0.0

        df = self.degrees_of_freedom

        return math.exp(
            (df / 2 - 1) * math.log(x)
            - x / 2
            - (df / 2) * math.log(2)
            - math.lgamma(df / 2)
        )

    def cdf(self, x: float) -> float:
        if x <= 0:
            return 0.0

        return regularized_gamma_p(
            self.degrees_of_freedom / 2,
            x / 2
        )

    @property
    def mean(self) -> float:
        return self.degrees_of_freedom

    @property
    def variance(self) -> float:
        return 2 * self.degrees_of_freedom

    def sample(self, rng: random.Random | None = None) -> float:
        return (rng or random).gammavariate(
            self.degrees_of_freedom / 2,
            2
        )


@dataclass
class GoodnessOfFitResult:
    statistic: float
    degrees_of_freedom: int
    p_value: float
    alpha: float
    reject_null: bool


def chi_square_goodness_of_fit(
    observed: Sequence[int],
    expected: Sequence[float],
    alpha: float = 0.05,
    estimated_parameters: int = 0
) -> GoodnessOfFitResult:
    """
    Pearson chi-square goodness-of-fit test.

    Expected frequencies should generally be at least five.
    estimated_parameters is the number of model parameters
    estimated from the observed data.
    """
    if len(observed) != len(expected) or len(observed) < 2:
        raise StatisticalError("Observed and expected arrays must match.")

    validate_probability(alpha, "Significance level")

    if alpha == 0 or alpha == 1:
        raise StatisticalError("Significance level must be between 0 and 1.")

    if estimated_parameters < 0:
        raise StatisticalError("Estimated parameter count cannot be negative.")

    if any(
        isinstance(value, bool) or not isinstance(value, int) or value < 0
        for value in observed
    ):
        raise StatisticalError("Observed counts must be nonnegative integers.")

    if any(not math.isfinite(value) or value <= 0 for value in expected):
        raise StatisticalError("Expected frequencies must be positive and finite.")

    if any(value < 5 for value in expected):
        raise StatisticalError(
            "Expected frequencies below five require category pooling."
        )

    if sum(observed) <= 0:
        raise StatisticalError("Observed total must be positive.")

    if not math.isclose(sum(observed), sum(expected), rel_tol=1e-9):
        raise StatisticalError("Observed and expected totals must match.")

    df = len(observed) - 1 - estimated_parameters

    if df <= 0:
        raise StatisticalError("Degrees of freedom must be positive.")

    statistic = sum(
        (o - e) ** 2 / e
        for o, e in zip(observed, expected)
    )

    p_value = ChiSquareDistribution(df).cdf(statistic)

    # Survival probability is 1 - CDF.
    p_value = max(0.0, 1.0 - p_value)

    return GoodnessOfFitResult(
        statistic=statistic,
        degrees_of_freedom=df,
        p_value=p_value,
        alpha=alpha,
        reject_null=p_value < alpha
    )


def simulate(
    distribution,
    sample_size: int = 10000,
    seed: int = 42
) -> dict:
    if sample_size <= 0:
        raise StatisticalError("Sample size must be positive.")

    rng = random.Random(seed)
    samples = [distribution.sample(rng) for _ in range(sample_size)]

    return {
        "sample_size": sample_size,
        "empirical_mean": statistics.fmean(samples),
        "empirical_variance": statistics.pvariance(samples),
        "theoretical_mean": distribution.mean,
        "theoretical_variance": distribution.variance,
        "minimum": min(samples),
        "maximum": max(samples)
    }


def print_distribution_report(name: str, distribution, points: Sequence[float]):
    print(f"\n{name}")
    print("-" * 65)
    print(f"Theoretical mean:     {distribution.mean:.6f}")
    print(f"Theoretical variance: {distribution.variance:.6f}")

    for x in points:
        if isinstance(distribution, PoissonDistribution):
            print(
                f"k={int(x):3d} | PMF={distribution.pmf(int(x)):.8f}"
                f" | CDF={distribution.cdf(int(x)):.8f}"
            )
        else:
            print(
                f"x={x:8.3f} | PDF={distribution.pdf(x):.8f}"
                f" | CDF={distribution.cdf(x):.8f}"
            )


def run_tests():
    poisson = PoissonDistribution(4)
    gamma = GammaDistribution(3, 2)
    beta = BetaDistribution(2, 5)
    chi = ChiSquareDistribution(4)

    assert math.isclose(poisson.mean, 4)
    assert math.isclose(poisson.variance, 4)
    assert math.isclose(gamma.mean, 6)
    assert math.isclose(gamma.variance, 12)
    assert math.isclose(beta.mean, 2 / 7)
    assert math.isclose(chi.mean, 4)
    assert math.isclose(chi.variance, 8)

    assert math.isclose(poisson.pmf(0), math.exp(-4))
    assert math.isclose(gamma.cdf(0), 0)
    assert math.isclose(beta.cdf(0), 0)
    assert math.isclose(beta.cdf(1), 1)
    assert math.isclose(chi.cdf(0), 0)

    assert 0 <= gamma.cdf(3) <= 1
    assert 0 <= beta.cdf(0.5) <= 1
    assert 0 <= chi.cdf(5) <= 1

    try:
        PoissonDistribution(-1)
        raise AssertionError("Invalid Poisson parameter was accepted.")
    except StatisticalError:
        pass

    try:
        BetaDistribution(0, 2)
        raise AssertionError("Invalid Beta parameter was accepted.")
    except StatisticalError:
        pass

    try:
        gamma.pdf(-1)
        # Negative support returns zero.
    except StatisticalError:
        raise AssertionError("Unexpected negative-support error.")

    print("All distribution tests passed.")


def main():
    run_tests()

    poisson = PoissonDistribution(lambda_rate=4.5)
    gamma = GammaDistribution(shape=3.0, scale=2.0)
    beta = BetaDistribution(alpha=2.0, beta=5.0)
    chi = ChiSquareDistribution(degrees_of_freedom=4)

    print_distribution_report(
        "Poisson: customer arrivals per hour",
        poisson,
        [0, 1, 2, 3, 4, 5, 6, 8]
    )

    print_distribution_report(
        "Gamma: equipment failure waiting time",
        gamma,
        [1, 2, 4, 6, 10, 15]
    )

    print_distribution_report(
        "Beta: unknown conversion probability",
        beta,
        [0.1, 0.2, 0.3, 0.5, 0.7, 0.9]
    )

    print_distribution_report(
        "Chi-square: goodness-of-fit statistic",
        chi,
        [1, 2, 3, 5, 8, 12]
    )

    print("\nBayesian conversion-rate estimation")
    print("-" * 65)

    prior = BetaDistribution(alpha=2, beta=2)
    successes = 45
    failures = 55

    posterior = BetaDistribution(
        prior.alpha + successes,
        prior.beta + failures
    )

    print(f"Prior mean:     {prior.mean:.6f}")
    print(f"Posterior mean: {posterior.mean:.6f}")
    print(f"Posterior variance: {posterior.variance:.8f}")
    print(f"P(rate <= 0.5): {posterior.cdf(0.5):.6f}")

    print("\nSimulation results")
    print("-" * 65)

    for name, distribution in [
        ("Poisson", poisson),
        ("Gamma", gamma),
        ("Beta", beta),
        ("Chi-square", chi)
    ]:
        result = simulate(distribution, 10000)

        print(f"\n{name}:")
        for key, value in result.items():
            print(f"  {key}: {value:.6f}" if isinstance(value, float)
                  else f"  {key}: {value}")

    print("\nChi-square goodness-of-fit example")
    print("-" * 65)

    observed = [48, 32, 15, 5]
    expected = [50.0, 30.0, 15.0, 5.0]

    result = chi_square_goodness_of_fit(
        observed,
        expected,
        alpha=0.05
    )

    print(f"Statistic: {result.statistic:.6f}")
    print(f"Degrees of freedom: {result.degrees_of_freedom}")
    print(f"P-value: {result.p_value:.6f}")
    print(f"Reject null hypothesis: {result.reject_null}")


if __name__ == "__main__":
    main()
