#!/usr/bin/env python3
"""
Statistical Estimation
Point estimation, interval estimation, and estimator evaluation.

Features:
- Mean, variance, standard deviation, and proportion estimation
- Method of moments and maximum likelihood estimation
- Normal and Student's t confidence intervals
- Wilson confidence interval for proportions
- Bootstrap confidence intervals
- Bias, variance, MSE, and consistency demonstrations
- Input validation, reproducible sampling, and unit tests
"""

from __future__ import annotations

import math
import random
import statistics
import json
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path
from typing import Callable, Sequence


class EstimationError(Exception):
    """Raised when an estimation operation is invalid."""


class IntervalMethod(Enum):
    NORMAL = "normal"
    T = "student_t"
    WILSON = "wilson"
    BOOTSTRAP = "bootstrap"


@dataclass(frozen=True)
class PointEstimate:
    parameter: str
    estimate: float
    sample_size: int
    estimator: str


@dataclass(frozen=True)
class ConfidenceInterval:
    parameter: str
    lower: float
    upper: float
    confidence_level: float
    method: str

    @property
    def width(self) -> float:
        return self.upper - self.lower

    def contains(self, value: float) -> bool:
        return self.lower <= value <= self.upper


@dataclass
class EstimatorEvaluation:
    name: str
    repetitions: int
    true_value: float
    average_estimate: float
    bias: float
    variance: float
    mse: float


def validate_sample(data: Sequence[float]) -> list[float]:
    if not data:
        raise EstimationError("Sample cannot be empty.")

    values = [float(value) for value in data]

    if not all(math.isfinite(value) for value in values):
        raise EstimationError("Sample contains non-finite values.")

    return values


def validate_confidence(level: float) -> None:
    if not 0 < level < 1:
        raise EstimationError("Confidence level must be between 0 and 1.")


def mean_estimator(data: Sequence[float]) -> PointEstimate:
    values = validate_sample(data)

    return PointEstimate(
        parameter="population_mean",
        estimate=statistics.fmean(values),
        sample_size=len(values),
        estimator="arithmetic_mean"
    )


def variance_estimator(
    data: Sequence[float],
    unbiased: bool = True
) -> PointEstimate:
    values = validate_sample(data)

    n = len(values)

    if unbiased and n < 2:
        raise EstimationError(
            "At least two observations are required for unbiased variance."
        )

    estimate = statistics.variance(values) if unbiased else statistics.pvariance(values)

    return PointEstimate(
        parameter="population_variance",
        estimate=estimate,
        sample_size=n,
        estimator="sample_variance" if unbiased else "maximum_likelihood_variance"
    )


def proportion_estimator(data: Sequence[int]) -> PointEstimate:
    values = validate_sample(data)

    if any(value not in (0, 1) for value in values):
        raise EstimationError("Proportion estimation requires binary observations.")

    return PointEstimate(
        parameter="population_proportion",
        estimate=statistics.fmean(values),
        sample_size=len(values),
        estimator="sample_proportion"
    )


def normal_quantile(probability: float) -> float:
    """Approximate standard-normal quantile using the Acklam algorithm."""

    if not 0 < probability < 1:
        raise EstimationError("Probability must be between zero and one.")

    a = [
        -39.69683028665376,
        220.9460984245205,
        -275.9285104469687,
        138.3577518672690,
        -30.66479806614716,
        2.506628277459239
    ]

    b = [
        -54.47609879822406,
        161.5858368580409,
        -155.6989798598866,
        66.80131188771972,
        -13.28068155288572
    ]

    c = [
        -0.007784894002430293,
        -0.3223964580411365,
        -2.400758277161838,
        -2.549732539343734,
        4.374664141464968,
        2.938163982698783
    ]

    d = [
        0.007784695709041462,
        0.3224671290700398,
        2.445134137142996,
        3.754408661907416
    ]

    low = 0.02425
    high = 1 - low

    if probability < low:
        q = math.sqrt(-2 * math.log(probability))
        numerator = sum(c[i] * q ** (5 - i) for i in range(6))
        denominator = sum(d[i] * q ** (3 - i) for i in range(4)) + 1
        return numerator / denominator

    if probability <= high:
        q = probability - 0.5
        r = q * q

        numerator = sum(a[i] * q * r ** (2 - i) for i in range(6))
        denominator = sum(b[i] * r ** (2 - i) for i in range(5)) + 1

        return numerator / denominator

    q = math.sqrt(-2 * math.log(1 - probability))
    numerator = sum(c[i] * q ** (5 - i) for i in range(6))
    denominator = sum(d[i] * q ** (3 - i) for i in range(4)) + 1

    return -numerator / denominator


def student_t_quantile(probability: float, degrees_freedom: int) -> float:
    """
    Numerically calculate a Student's t quantile using
    bisection and the regularized incomplete beta function.
    """

    if degrees_freedom < 1:
        raise EstimationError("Degrees of freedom must be positive.")

    if not 0 < probability < 1:
        raise EstimationError("Probability must be between zero and one.")

    if probability == 0.5:
        return 0.0

    if probability < 0.5:
        return -student_t_quantile(1 - probability, degrees_freedom)

    def beta_fraction(a: float, b: float, x: float) -> float:
        maximum_iterations = 300
        epsilon = 3e-14
        tiny = 1e-300

        qab = a + b
        qap = a + 1
        qam = a - 1

        c = 1.0
        d = 1 - qab * x / qap
        d = 1 / max(abs(d), tiny) * (1 if d >= 0 else -1)
        h = d

        for m in range(1, maximum_iterations + 1):
            m2 = 2 * m

            aa = m * (b - m) * x / (
                (qam + m2) * (a + m2)
            )

            d = 1 + aa * d
            if abs(d) < tiny:
                d = tiny

            c = 1 + aa / c
            if abs(c) < tiny:
                c = tiny

            d = 1 / d
            h *= d * c

            aa = -(a + m) * (qab + m) * x / (
                (a + m2) * (qap + m2)
            )

            d = 1 + aa * d
            if abs(d) < tiny:
                d = tiny

            c = 1 + aa / c
            if abs(c) < tiny:
                c = tiny

            d = 1 / d

            delta = d * c
            h *= delta

            if abs(delta - 1) < epsilon:
                return h

        raise EstimationError("Incomplete beta calculation did not converge.")

    def regularized_beta(x: float, a: float, b: float) -> float:
        if x <= 0:
            return 0.0

        if x >= 1:
            return 1.0

        log_bt = (
            math.lgamma(a + b)
            - math.lgamma(a)
            - math.lgamma(b)
            + a * math.log(x)
            + b * math.log1p(-x)
        )

        bt = math.exp(log_bt)

        if x < (a + 1) / (a + b + 2):
            return bt * beta_fraction(a, b, x) / a

        return 1 - (
            bt * beta_fraction(b, a, 1 - x) / b
        )

    def cdf(t: float) -> float:
        x = degrees_freedom / (
            degrees_freedom + t * t
        )

        beta_value = regularized_beta(
            x,
            degrees_freedom / 2,
            0.5
        )

        if t >= 0:
            return 1 - 0.5 * beta_value

        return 0.5 * beta_value

    lower = 0.0
    upper = 1.0

    while cdf(upper) < probability:
        upper *= 2

        if upper > 1e12:
            raise EstimationError("Unable to bracket Student's t quantile.")

    for _ in range(150):
        middle = (lower + upper) / 2

        if cdf(middle) < probability:
            lower = middle
        else:
            upper = middle

    return (lower + upper) / 2


def mean_confidence_interval(
    data: Sequence[float],
    confidence: float = 0.95,
    method: IntervalMethod = IntervalMethod.T
) -> ConfidenceInterval:
    values = validate_sample(data)
    validate_confidence(confidence)

    n = len(values)

    if n < 2:
        raise EstimationError("At least two observations are required.")

    average = statistics.fmean(values)
    standard_error = statistics.stdev(values) / math.sqrt(n)

    if method == IntervalMethod.T:
        critical = student_t_quantile(
            (1 + confidence) / 2,
            n - 1
        )
    elif method == IntervalMethod.NORMAL:
        critical = normal_quantile((1 + confidence) / 2)
    else:
        raise EstimationError("Invalid method for mean estimation.")

    margin = critical * standard_error

    return ConfidenceInterval(
        parameter="population_mean",
        lower=average - margin,
        upper=average + margin,
        confidence_level=confidence,
        method=method.value
    )


def wilson_proportion_interval(
    data: Sequence[int],
    confidence: float = 0.95
) -> ConfidenceInterval:
    estimate = proportion_estimator(data)
    validate_confidence(confidence)

    n = estimate.sample_size
    p = estimate.estimate

    z = normal_quantile((1 + confidence) / 2)
    z2 = z * z

    denominator = 1 + z2 / n

    center = (p + z2 / (2 * n)) / denominator

    margin = (
        z * math.sqrt(
            p * (1 - p) / n + z2 / (4 * n * n)
        ) / denominator
    )

    return ConfidenceInterval(
        parameter="population_proportion",
        lower=max(0.0, center - margin),
        upper=min(1.0, center + margin),
        confidence_level=confidence,
        method=IntervalMethod.WILSON.value
    )


def bootstrap_mean_interval(
    data: Sequence[float],
    confidence: float = 0.95,
    repetitions: int = 5000,
    seed: int = 42
) -> ConfidenceInterval:
    values = validate_sample(data)
    validate_confidence(confidence)

    if repetitions < 100:
        raise EstimationError("Use at least 100 bootstrap repetitions.")

    rng = random.Random(seed)
    n = len(values)

    estimates = [
        statistics.fmean(
            rng.choices(values, k=n)
        )
        for _ in range(repetitions)
    ]

    estimates.sort()

    alpha = 1 - confidence

    lower_index = int((alpha / 2) * repetitions)
    upper_index = min(
        repetitions - 1,
        int((1 - alpha / 2) * repetitions)
    )

    return ConfidenceInterval(
        parameter="population_mean",
        lower=estimates[lower_index],
        upper=estimates[upper_index],
        confidence_level=confidence,
        method=IntervalMethod.BOOTSTRAP.value
    )


def method_of_moments_exponential(
    data: Sequence[float]
) -> PointEstimate:
    values = validate_sample(data)

    if any(value <= 0 for value in values):
        raise EstimationError(
            "Exponential observations must be positive."
        )

    rate = 1 / statistics.fmean(values)

    return PointEstimate(
        parameter="exponential_rate",
        estimate=rate,
        sample_size=len(values),
        estimator="method_of_moments"
    )


def maximum_likelihood_exponential(
    data: Sequence[float]
) -> PointEstimate:
    values = validate_sample(data)

    if any(value < 0 for value in values):
        raise EstimationError(
            "Exponential observations cannot be negative."
        )

    average = statistics.fmean(values)

    if average <= 0:
        raise EstimationError(
            "The MLE is undefined for an all-zero sample."
        )

    return PointEstimate(
        parameter="exponential_rate",
        estimate=1 / average,
        sample_size=len(values),
        estimator="maximum_likelihood"
    )


def evaluate_estimator(
    name: str,
    estimator: Callable[[Sequence[float]], float],
    true_value: float,
    repetitions: int = 2000,
    sample_size: int = 30,
    seed: int = 42
) -> EstimatorEvaluation:
    if repetitions < 2 or sample_size < 1:
        raise EstimationError("Invalid simulation dimensions.")

    if not math.isfinite(true_value):
        raise EstimationError("True value must be finite.")

    rng = random.Random(seed)

    estimates = [
        float(estimator([
            rng.gauss(true_value, 2.0)
            for _ in range(sample_size)
        ]))
        for _ in range(repetitions)
    ]

    if not all(math.isfinite(value) for value in estimates):
        raise EstimationError("Estimator produced non-finite values.")

    average = statistics.fmean(estimates)
    bias = average - true_value

    variance = statistics.pvariance(estimates)
    mse = statistics.fmean(
        (value - true_value) ** 2
        for value in estimates
    )

    return EstimatorEvaluation(
        name=name,
        repetitions=repetitions,
        true_value=true_value,
        average_estimate=average,
        bias=bias,
        variance=variance,
        mse=mse
    )


def run_tests() -> None:
    sample = [10, 12, 13, 15, 16]

    assert abs(mean_estimator(sample).estimate - 13.2) < 1e-10

    assert abs(
        variance_estimator(sample).estimate - 5.7
    ) < 1e-10

    interval = mean_confidence_interval(sample)

    assert interval.lower < 13.2 < interval.upper

    binary = [1, 0, 1, 1, 0, 1, 0, 1]

    proportion = proportion_estimator(binary)
    assert proportion.estimate == 0.625

    wilson = wilson_proportion_interval(binary)
    assert wilson.lower <= 0.625 <= wilson.upper

    exponential = [1, 2, 3, 4, 5]

    assert abs(
        method_of_moments_exponential(exponential).estimate - 1 / 3
    ) < 1e-10

    try:
        mean_estimator([])
        raise AssertionError("Empty samples must fail.")
    except EstimationError:
        pass

    try:
        proportion_estimator([0, 1, 2])
        raise AssertionError("Invalid binary data must fail.")
    except EstimationError:
        pass

    print("All statistical estimation tests passed.")


def main() -> None:
    observations = [
        48.2, 51.1, 49.5, 52.3, 47.8,
        50.6, 53.0, 49.9, 51.7, 48.9,
        52.1, 50.3
    ]

    print("\nSTATISTICAL ESTIMATION")
    print("=" * 55)

    point = mean_estimator(observations)
    variance = variance_estimator(observations)

    print("\nPoint Estimates")
    print(json.dumps(asdict(point), indent=2))
    print(json.dumps(asdict(variance), indent=2))

    print("\nInterval Estimation")

    t_interval = mean_confidence_interval(
        observations,
        0.95,
        IntervalMethod.T
    )

    normal_interval = mean_confidence_interval(
        observations,
        0.95,
        IntervalMethod.NORMAL
    )

    bootstrap_interval = bootstrap_mean_interval(
        observations,
        confidence=0.95,
        repetitions=5000
    )

    for result in (
        t_interval,
        normal_interval,
        bootstrap_interval
    ):
        print(json.dumps(asdict(result), indent=2))

    print("\nProportion Estimation")

    outcomes = [
        1, 1, 0, 1, 0, 1, 1, 0, 1, 1,
        0, 1, 0, 1, 1, 1, 0, 1, 0, 1
    ]

    print(json.dumps(
        asdict(proportion_estimator(outcomes)),
        indent=2
    ))

    print(json.dumps(
        asdict(wilson_proportion_interval(outcomes)),
        indent=2
    ))

    print("\nEstimator Evaluation")

    evaluation = evaluate_estimator(
        name="Sample Mean",
        estimator=lambda values: statistics.fmean(values),
        true_value=50.0,
        repetitions=2000,
        sample_size=30
    )

    print(json.dumps(asdict(evaluation), indent=2))

    print("\nMethod of Moments and Maximum Likelihood")

    positive_sample = [1.2, 0.8, 2.1, 1.5, 0.9, 1.7]

    print(json.dumps(
        asdict(method_of_moments_exponential(positive_sample)),
        indent=2
    ))

    print(json.dumps(
        asdict(maximum_likelihood_exponential(positive_sample)),
        indent=2
    ))

    run_tests()

    output = {
        "point_estimate": asdict(point),
        "variance_estimate": asdict(variance),
        "confidence_interval": asdict(t_interval),
        "bootstrap_interval": asdict(bootstrap_interval),
        "evaluation": asdict(evaluation)
    }

    output_path = Path("estimation_results.json")

    output_path.write_text(
        json.dumps(output, indent=2),
        encoding="utf-8"
    )

    print(f"\nResults saved to {output_path.resolve()}")


if __name__ == "__main__":
    main()
