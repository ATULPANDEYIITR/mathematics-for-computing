#!/usr/bin/env python3
"""
Statistical Tests: t-test, z-test, chi-square test, and ANOVA.

Self-contained statistical testing toolkit using only the Python standard
library. Implements test statistics, distribution probabilities, assumptions,
effect sizes, confidence intervals, and example workflows.

Run:
    python statistical_tests.py
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass
from enum import Enum
from typing import Sequence


class StatisticalError(ValueError):
    """Raised when statistical input or assumptions are invalid."""


class TestType(Enum):
    ONE_SAMPLE_T = "one_sample_t"
    INDEPENDENT_T = "independent_t"
    PAIRED_T = "paired_t"
    Z_TEST = "z_test"
    CHI_SQUARE = "chi_square"
    ONE_WAY_ANOVA = "one_way_anova"


@dataclass(frozen=True)
class TestResult:
    test_name: str
    statistic: float
    p_value: float
    degrees_of_freedom: float | None
    alpha: float
    reject_null: bool
    effect_size: float | None = None
    confidence_interval: tuple[float, float] | None = None

    def display(self) -> None:
        print(f"\n{self.test_name}")
        print(f"Statistic: {self.statistic:.6f}")
        print(f"P-value: {self.p_value:.8f}")
        print(f"Degrees of freedom: {self.degrees_of_freedom}")
        print(f"Significance level: {self.alpha}")
        print(f"Decision: {'Reject H0' if self.reject_null else 'Fail to reject H0'}")

        if self.effect_size is not None:
            print(f"Effect size: {self.effect_size:.6f}")

        if self.confidence_interval is not None:
            print(
                "Confidence interval: "
                f"({self.confidence_interval[0]:.6f}, "
                f"{self.confidence_interval[1]:.6f})"
            )


def validate_alpha(alpha: float) -> None:
    if not 0 < alpha < 1:
        raise StatisticalError("Alpha must be between zero and one.")


def validate_sample(data: Sequence[float], name: str = "sample") -> list[float]:
    values = [float(x) for x in data]

    if len(values) < 2:
        raise StatisticalError(f"{name} must contain at least two observations.")

    if not all(math.isfinite(x) for x in values):
        raise StatisticalError(f"{name} contains a non-finite observation.")

    return values


def mean(data: Sequence[float]) -> float:
    return math.fsum(data) / len(data)


def variance(data: Sequence[float], ddof: int = 1) -> float:
    if len(data) <= ddof:
        raise StatisticalError("Insufficient observations for variance.")

    average = mean(data)
    return math.fsum((x - average) ** 2 for x in data) / (len(data) - ddof)


def standard_error(data: Sequence[float]) -> float:
    return math.sqrt(variance(data) / len(data))


def regularized_beta(x: float, a: float, b: float) -> float:
    """Regularized incomplete beta using a continued fraction."""

    if a <= 0 or b <= 0 or not 0 <= x <= 1:
        raise StatisticalError("Invalid incomplete beta parameters.")

    if x == 0:
        return 0.0
    if x == 1:
        return 1.0

    def fraction(a_: float, b_: float, x_: float) -> float:
        qab = a_ + b_
        qap = a_ + 1.0
        qam = a_ - 1.0
        c = 1.0
        d = 1.0 - qab * x_ / qap

        if abs(d) < 1e-300:
            d = 1e-300

        d = 1.0 / d
        h = d

        for m in range(1, 10001):
            m2 = 2 * m

            aa = m * (b_ - m) * x_ / (
                (qam + m2) * (a_ + m2)
            )

            d = 1.0 + aa * d
            if abs(d) < 1e-300:
                d = 1e-300

            c = 1.0 + aa / c
            if abs(c) < 1e-300:
                c = 1e-300

            d = 1.0 / d
            h *= d * c

            aa = -(a_ + m) * (qab + m) * x_ / (
                (a_ + m2) * (qap + m2)
            )

            d = 1.0 + aa * d
            if abs(d) < 1e-300:
                d = 1e-300

            c = 1.0 + aa / c
            if abs(c) < 1e-300:
                c = 1e-300

            d = 1.0 / d
            delta = d * c
            h *= delta

            if abs(delta - 1.0) < 3e-14:
                return h

        raise ArithmeticError("Beta continued fraction did not converge.")

    log_bt = (
        math.lgamma(a + b)
        - math.lgamma(a)
        - math.lgamma(b)
        + a * math.log(x)
        + b * math.log1p(-x)
    )

    bt = math.exp(log_bt)

    if x < (a + 1) / (a + b + 2):
        return max(0.0, min(1.0, bt * fraction(a, b, x) / a))

    return max(
        0.0,
        min(1.0, 1.0 - bt * fraction(b, a, 1.0 - x) / b)
    )


def regularized_gamma_q(a: float, x: float) -> float:
    """Upper regularized incomplete gamma function."""

    if a <= 0 or x < 0:
        raise StatisticalError("Invalid gamma parameters.")

    if x == 0:
        return 1.0

    gln = math.lgamma(a)

    if x < a + 1:
        ap = a
        term = 1.0 / a
        total = term

        for _ in range(10000):
            ap += 1
            term *= x / ap
            total += term

            if abs(term) < abs(total) * 3e-14:
                break
        else:
            raise ArithmeticError("Gamma series did not converge.")

        p = total * math.exp(-x + a * math.log(x) - gln)
        return max(0.0, min(1.0, 1.0 - p))

    b = x + 1.0 - a
    c = 1e300
    d = 1.0 / b
    h = d

    for i in range(1, 10001):
        an = -i * (i - a)
        b += 2.0

        d = an * d + b
        if abs(d) < 1e-300:
            d = 1e-300

        c = b + an / c
        if abs(c) < 1e-300:
            c = 1e-300

        d = 1.0 / d
        delta = d * c
        h *= delta

        if abs(delta - 1.0) < 3e-14:
            break
    else:
        raise ArithmeticError("Gamma continued fraction did not converge.")

    return max(
        0.0,
        min(1.0, math.exp(-x + a * math.log(x) - gln) * h)
    )


def normal_cdf(z: float) -> float:
    return 0.5 * math.erfc(-z / math.sqrt(2))


def normal_two_sided_p(z: float) -> float:
    return math.erfc(abs(z) / math.sqrt(2))


def t_two_sided_p(t: float, df: float) -> float:
    if df <= 0:
        raise StatisticalError("Degrees of freedom must be positive.")

    x = df / (df + t * t)
    return regularized_beta(x, df / 2, 0.5)


def chi_square_p(statistic: float, df: int) -> float:
    if statistic < 0 or df <= 0:
        raise StatisticalError("Invalid chi-square statistic or degrees of freedom.")

    return regularized_gamma_q(df / 2, statistic / 2)


def f_distribution_p(statistic: float, df1: int, df2: int) -> float:
    if statistic < 0 or df1 <= 0 or df2 <= 0:
        raise StatisticalError("Invalid F-distribution parameters.")

    x = df2 / (df2 + df1 * statistic)
    return regularized_beta(x, df2 / 2, df1 / 2)


def inverse_distribution(
    function,
    probability: float,
    lower: float,
    upper: float,
    iterations: int = 150
) -> float:
    """Numerically invert a monotonic cumulative distribution."""

    if not 0 < probability < 1:
        raise StatisticalError("Probability must be between zero and one.")

    for _ in range(iterations):
        midpoint = (lower + upper) / 2

        if function(midpoint) < probability:
            lower = midpoint
        else:
            upper = midpoint

    return (lower + upper) / 2


def t_critical(df: float, alpha: float) -> float:
    validate_alpha(alpha)

    return inverse_distribution(
        lambda x: 1 - t_two_sided_p(x, df) / 2,
        1 - alpha / 2,
        0,
        1e7
    )


def pooled_variance(a: Sequence[float], b: Sequence[float]) -> float:
    return (
        (len(a) - 1) * variance(a)
        + (len(b) - 1) * variance(b)
    ) / (len(a) + len(b) - 2)


def one_sample_t_test(
    data: Sequence[float],
    population_mean: float,
    alpha: float = 0.05
) -> TestResult:
    validate_alpha(alpha)
    x = validate_sample(data)

    if not math.isfinite(population_mean):
        raise StatisticalError("Population mean must be finite.")

    s = math.sqrt(variance(x))
    se = s / math.sqrt(len(x))

    if se == 0:
        raise StatisticalError("Cannot perform a t-test with zero variance.")

    statistic = (mean(x) - population_mean) / se
    df = len(x) - 1
    p = t_two_sided_p(statistic, df)
    critical = t_critical(df, alpha)

    return TestResult(
        "One-sample t-test",
        statistic,
        p,
        df,
        alpha,
        p < alpha,
        (mean(x) - population_mean) / s,
        (
            mean(x) - population_mean - critical * se,
            mean(x) - population_mean + critical * se
        )
    )


def independent_t_test(
    group_a: Sequence[float],
    group_b: Sequence[float],
    equal_variance: bool = False,
    alpha: float = 0.05
) -> TestResult:
    validate_alpha(alpha)
    a = validate_sample(group_a, "Group A")
    b = validate_sample(group_b, "Group B")

    difference = mean(a) - mean(b)
    va = variance(a)
    vb = variance(b)

    if equal_variance:
        df = len(a) + len(b) - 2
        pooled = pooled_variance(a, b)
        se = math.sqrt(pooled * (1 / len(a) + 1 / len(b)))
        effect = difference / math.sqrt(pooled)
    else:
        se2 = va / len(a) + vb / len(b)

        if se2 == 0:
            raise StatisticalError("Both groups have zero sampling variance.")

        se = math.sqrt(se2)
        df = se2 ** 2 / (
            (va / len(a)) ** 2 / (len(a) - 1)
            + (vb / len(b)) ** 2 / (len(b) - 1)
        )

        effect = difference / math.sqrt(
            (va + vb) / 2
        ) if va + vb > 0 else 0.0

    if se == 0:
        raise StatisticalError("Standard error is zero.")

    statistic = difference / se
    p = t_two_sided_p(statistic, df)
    critical = t_critical(df, alpha)

    return TestResult(
        "Independent two-sample t-test",
        statistic,
        p,
        df,
        alpha,
        p < alpha,
        effect,
        (
            difference - critical * se,
            difference + critical * se
        )
    )


def paired_t_test(
    before: Sequence[float],
    after: Sequence[float],
    alpha: float = 0.05
) -> TestResult:
    validate_alpha(alpha)

    if len(before) != len(after):
        raise StatisticalError("Paired samples must have equal lengths.")

    differences = [
        float(y) - float(x)
        for x, y in zip(before, after)
    ]

    return one_sample_t_test(differences, 0.0, alpha).__class__(
        "Paired t-test",
        one_sample_t_test(differences, 0.0, alpha).statistic,
        one_sample_t_test(differences, 0.0, alpha).p_value,
        one_sample_t_test(differences, 0.0, alpha).degrees_of_freedom,
        alpha,
        one_sample_t_test(differences, 0.0, alpha).reject_null,
        one_sample_t_test(differences, 0.0, alpha).effect_size,
        one_sample_t_test(differences, 0.0, alpha).confidence_interval
    )


def z_test(
    sample_mean: float,
    population_mean: float,
    population_std: float,
    sample_size: int,
    alpha: float = 0.05
) -> TestResult:
    validate_alpha(alpha)

    if sample_size <= 0:
        raise StatisticalError("Sample size must be positive.")

    if population_std <= 0 or not math.isfinite(population_std):
        raise StatisticalError("Population standard deviation must be positive.")

    if not all(map(math.isfinite, [sample_mean, population_mean])):
        raise StatisticalError("Means must be finite.")

    se = population_std / math.sqrt(sample_size)
    statistic = (sample_mean - population_mean) / se
    p = normal_two_sided_p(statistic)
    critical = 1.959963984540054

    # General two-sided normal critical value by bisection.
    critical = inverse_distribution(
        normal_cdf, 1 - alpha / 2, 0, 10
    )

    return TestResult(
        "One-sample z-test",
        statistic,
        p,
        None,
        alpha,
        p < alpha,
        (sample_mean - population_mean) / population_std,
        (
            sample_mean - population_mean - critical * se,
            sample_mean - population_mean + critical * se
        )
    )


def chi_square_goodness_of_fit(
    observed: Sequence[float],
    expected: Sequence[float],
    alpha: float = 0.05
) -> TestResult:
    validate_alpha(alpha)

    if len(observed) != len(expected) or len(observed) < 2:
        raise StatisticalError("Observed and expected arrays must have equal lengths.")

    if any(x < 0 or not math.isfinite(x) for x in observed):
        raise StatisticalError("Observed frequencies must be finite and nonnegative.")

    if any(x <= 0 or not math.isfinite(x) for x in expected):
        raise StatisticalError("Expected frequencies must be positive and finite.")

    statistic = math.fsum(
        (o - e) ** 2 / e
        for o, e in zip(observed, expected)
    )

    df = len(observed) - 1
    p = chi_square_p(statistic, df)

    return TestResult(
        "Chi-square goodness-of-fit test",
        statistic,
        p,
        df,
        alpha,
        p < alpha,
        math.sqrt(statistic / sum(observed))
    )


def chi_square_independence(
    table: Sequence[Sequence[float]],
    alpha: float = 0.05
) -> TestResult:
    validate_alpha(alpha)

    rows = len(table)

    if rows < 2:
        raise StatisticalError("At least two rows are required.")

    columns = len(table[0])

    if columns < 2 or any(len(row) != columns for row in table):
        raise StatisticalError("Contingency table must be rectangular and at least 2x2.")

    if any(
        not math.isfinite(value) or value < 0
        for row in table for value in row
    ):
        raise StatisticalError("Frequencies must be finite and nonnegative.")

    row_totals = [sum(row) for row in table]
    col_totals = [
        sum(table[i][j] for i in range(rows))
        for j in range(columns)
    ]

    total = sum(row_totals)

    if total <= 0:
        raise StatisticalError("Contingency table total must be positive.")

    expected = [
        [row_totals[i] * col_totals[j] / total for j in range(columns)]
        for i in range(rows)
    ]

    if any(value == 0 for row in expected for value in row):
        raise StatisticalError("Expected cell frequencies cannot be zero.")

    statistic = math.fsum(
        (table[i][j] - expected[i][j]) ** 2 / expected[i][j]
        for i in range(rows)
        for j in range(columns)
    )

    df = (rows - 1) * (columns - 1)
    p = chi_square_p(statistic, df)

    cramer_v = math.sqrt(
        statistic / (total * min(rows - 1, columns - 1))
    )

    return TestResult(
        "Chi-square test of independence",
        statistic,
        p,
        df,
        alpha,
        p < alpha,
        cramer_v
    )


def one_way_anova(
    groups: Sequence[Sequence[float]],
    alpha: float = 0.05
) -> TestResult:
    validate_alpha(alpha)

    if len(groups) < 2:
        raise StatisticalError("ANOVA requires at least two groups.")

    samples = [
        validate_sample(group, f"Group {i + 1}")
        for i, group in enumerate(groups)
    ]

    total_n = sum(map(len, samples))
    grand_mean = math.fsum(
        x for group in samples for x in group
    ) / total_n

    ss_between = math.fsum(
        len(group) * (mean(group) - grand_mean) ** 2
        for group in samples
    )

    ss_within = math.fsum(
        math.fsum((x - mean(group)) ** 2 for x in group)
        for group in samples
    )

    df_between = len(samples) - 1
    df_within = total_n - len(samples)

    ms_between = ss_between / df_between
    ms_within = ss_within / df_within

    if ms_within == 0:
        raise StatisticalError("ANOVA within-group variance is zero.")

    statistic = ms_between / ms_within
    p = f_distribution_p(statistic, df_between, df_within)

    eta_squared = ss_between / (ss_between + ss_within)

    return TestResult(
        "One-way ANOVA",
        statistic,
        p,
        df_within,
        alpha,
        p < alpha,
        eta_squared
    )


def bonferroni_adjust(
    p_values: Sequence[float]
) -> list[float]:
    """Control family-wise error across multiple comparisons."""

    if not p_values:
        raise StatisticalError("At least one p-value is required.")

    if any(not 0 <= p <= 1 for p in p_values):
        raise StatisticalError("P-values must be between zero and one.")

    return [min(1.0, p * len(p_values)) for p in p_values]


def run_examples() -> None:
    print("=" * 65)
    print("STATISTICAL TESTING TOOLKIT")
    print("=" * 65)

    # 1. One-sample t-test
    one_sample = one_sample_t_test(
        [51, 53, 49, 52, 55, 50, 54, 52],
        population_mean=50
    )
    one_sample.display()

    # 2. Independent t-test using Welch's method
    control = [68, 70, 72, 65, 71, 69, 67]
    treatment = [75, 78, 74, 80, 77, 76, 79]

    independent = independent_t_test(
        control, treatment, equal_variance=False
    )
    independent.display()

    # 3. Paired t-test
    before = [70, 72, 68, 75, 71, 69]
    after = [74, 76, 72, 78, 75, 73]

    paired = paired_t_test(before, after)
    paired.display()

    # 4. Z-test
    z_result = z_test(
        sample_mean=102,
        population_mean=100,
        population_std=10,
        sample_size=100
    )
    z_result.display()

    # 5. Chi-square goodness-of-fit
    goodness = chi_square_goodness_of_fit(
        observed=[45, 55, 50, 50],
        expected=[50, 50, 50, 50]
    )
    goodness.display()

    # 6. Chi-square independence
    contingency = [
        [40, 20],
        [30, 50]
    ]

    independence = chi_square_independence(contingency)
    independence.display()

    # 7. One-way ANOVA
    anova = one_way_anova([
        [18, 20, 19, 21, 17],
        [24, 25, 23, 26, 22],
        [29, 30, 28, 31, 27]
    ])
    anova.display()

    # 8. Multiple-comparison adjustment
    raw_p_values = [0.01, 0.03, 0.04, 0.20]
    adjusted = bonferroni_adjust(raw_p_values)

    print("\nBONFERRONI CORRECTION")
    for raw, corrected in zip(raw_p_values, adjusted):
        print(f"Raw p={raw:.4f}, Adjusted p={corrected:.4f}")

    # 9. Numerical validation
    assert abs(normal_cdf(0) - 0.5) < 1e-10
    assert abs(chi_square_p(0, 2) - 1.0) < 1e-10
    assert 0 <= independence.p_value <= 1
    assert 0 <= anova.p_value <= 1

    print("\nAll numerical validation checks passed.")

    # 10. Invalid-input handling
    try:
        one_sample_t_test([10], 8)
    except StatisticalError as error:
        print(f"\nExpected validation error: {error}")


if __name__ == "__main__":
    run_examples()
