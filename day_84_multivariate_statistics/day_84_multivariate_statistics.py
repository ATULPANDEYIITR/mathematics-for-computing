#!/usr/bin/env python3
"""
MULTIVARIATE STATISTICS
Multiple Regression, Multivariate Distributions, and Covariance Structures.

Self-contained implementation using Python standard-library modules only.
"""

from __future__ import annotations

import json
import math
import random
import statistics
from dataclasses import dataclass
from typing import Sequence


class StatisticalError(Exception):
    """Base exception for statistical computation failures."""


class ValidationError(StatisticalError):
    """Raised when input data violate statistical requirements."""


def validate_matrix(matrix: Sequence[Sequence[float]]) -> list[list[float]]:
    if not matrix:
        raise ValidationError("Matrix cannot be empty.")

    result = [list(map(float, row)) for row in matrix]
    width = len(result[0])

    if width == 0 or any(len(row) != width for row in result):
        raise ValidationError("Matrix must be rectangular and nonempty.")

    if any(not math.isfinite(value) for row in result for value in row):
        raise ValidationError("Matrix contains non-finite values.")

    return result


def transpose(matrix: Sequence[Sequence[float]]) -> list[list[float]]:
    return [list(row) for row in zip(*matrix)]


def matmul(
    a: Sequence[Sequence[float]],
    b: Sequence[Sequence[float]]
) -> list[list[float]]:
    a = validate_matrix(a)
    b = validate_matrix(b)

    if len(a[0]) != len(b):
        raise ValidationError("Incompatible matrix dimensions.")

    bt = transpose(b)

    return [
        [sum(x * y for x, y in zip(row, col)) for col in bt]
        for row in a
    ]


def solve_linear_system(
    matrix: Sequence[Sequence[float]],
    vector: Sequence[float],
    tolerance: float = 1e-12
) -> list[float]:
    """Solve Ax=b using Gaussian elimination with partial pivoting."""

    a = validate_matrix(matrix)
    b = list(map(float, vector))
    n = len(a)

    if len(a) != n or len(b) != n or len(a[0]) != n:
        raise ValidationError("Linear system must be square.")

    if any(not math.isfinite(value) for value in b):
        raise ValidationError("Right-hand side contains non-finite values.")

    augmented = [a[i] + [b[i]] for i in range(n)]

    for col in range(n):
        pivot = max(range(col, n), key=lambda r: abs(augmented[r][col]))

        if abs(augmented[pivot][col]) < tolerance:
            raise StatisticalError(
                "Singular or numerically unstable matrix."
            )

        augmented[col], augmented[pivot] = (
            augmented[pivot],
            augmented[col]
        )

        pivot_value = augmented[col][col]

        for j in range(col, n + 1):
            augmented[col][j] /= pivot_value

        for row in range(n):
            if row == col:
                continue

            factor = augmented[row][col]

            for j in range(col, n + 1):
                augmented[row][j] -= factor * augmented[col][j]

    return [augmented[i][n] for i in range(n)]


def covariance_matrix(
    observations: Sequence[Sequence[float]]
) -> list[list[float]]:
    """Calculate the unbiased sample covariance matrix."""

    x = validate_matrix(observations)
    n = len(x)
    p = len(x[0])

    if n < 2:
        raise ValidationError("At least two observations are required.")

    means = [sum(row[j] for row in x) / n for j in range(p)]

    return [
        [
            sum(
                (row[i] - means[i]) * (row[j] - means[j])
                for row in x
            ) / (n - 1)
            for j in range(p)
        ]
        for i in range(p)
    ]


def correlation_matrix(
    observations: Sequence[Sequence[float]]
) -> list[list[float]]:
    cov = covariance_matrix(observations)
    p = len(cov)

    std = [math.sqrt(cov[i][i]) for i in range(p)]

    if any(value == 0 for value in std):
        raise StatisticalError("Correlation undefined for constant variables.")

    return [
        [
            cov[i][j] / (std[i] * std[j])
            for j in range(p)
        ]
        for i in range(p)
    ]


def cholesky(matrix: Sequence[Sequence[float]]) -> list[list[float]]:
    """Compute lower-triangular Cholesky factorization."""

    a = validate_matrix(matrix)
    n = len(a)

    if len(a) != n or len(a[0]) != n:
        raise ValidationError("Covariance matrix must be square.")

    for i in range(n):
        for j in range(n):
            if not math.isclose(a[i][j], a[j][i], rel_tol=1e-9, abs_tol=1e-12):
                raise ValidationError("Matrix must be symmetric.")

    lower = [[0.0] * n for _ in range(n)]

    for i in range(n):
        for j in range(i + 1):
            value = a[i][j] - sum(
                lower[i][k] * lower[j][k]
                for k in range(j)
            )

            if i == j:
                if value <= 0:
                    raise StatisticalError(
                        "Matrix is not positive definite."
                    )
                lower[i][j] = math.sqrt(value)
            else:
                lower[i][j] = value / lower[j][j]

    return lower


def mahalanobis_distance(
    observation: Sequence[float],
    mean: Sequence[float],
    covariance: Sequence[Sequence[float]]
) -> float:
    """Calculate multivariate Mahalanobis distance."""

    x = list(map(float, observation))
    mu = list(map(float, mean))

    if len(x) != len(mu):
        raise ValidationError("Observation and mean dimensions differ.")

    lower = cholesky(covariance)

    if len(lower) != len(x):
        raise ValidationError("Covariance dimension mismatch.")

    difference = [x[i] - mu[i] for i in range(len(x))]
    whitened = []

    for i in range(len(x)):
        value = (
            difference[i] -
            sum(lower[i][j] * whitened[j] for j in range(i))
        ) / lower[i][i]

        whitened.append(value)

    return math.sqrt(sum(value * value for value in whitened))


def multivariate_normal_density(
    observation: Sequence[float],
    mean: Sequence[float],
    covariance: Sequence[Sequence[float]]
) -> float:
    """Evaluate the multivariate normal probability density."""

    x = list(map(float, observation))
    mu = list(map(float, mean))
    lower = cholesky(covariance)
    n = len(mu)

    if len(x) != n or len(lower) != n:
        raise ValidationError("Dimension mismatch.")

    distance = mahalanobis_distance(x, mu, covariance)

    log_determinant = 2 * sum(
        math.log(lower[i][i]) for i in range(n)
    )

    log_density = (
        -0.5 * n * math.log(2 * math.pi)
        - 0.5 * log_determinant
        - 0.5 * distance ** 2
    )

    return math.exp(log_density)


@dataclass
class RegressionResult:
    coefficients: list[float]
    predictions: list[float]
    residuals: list[float]
    r_squared: float
    adjusted_r_squared: float
    mse: float
    rmse: float
    residual_variance: float

    def predict(self, features: Sequence[Sequence[float]]) -> list[float]:
        x = validate_matrix(features)

        if len(x[0]) + 1 != len(self.coefficients):
            raise ValidationError("Prediction feature dimension mismatch.")

        return [
            self.coefficients[0] +
            sum(
                self.coefficients[j + 1] * row[j]
                for j in range(len(row))
            )
            for row in x
        ]

    def to_dict(self) -> dict:
        return {
            "coefficients": self.coefficients,
            "r_squared": self.r_squared,
            "adjusted_r_squared": self.adjusted_r_squared,
            "mse": self.mse,
            "rmse": self.rmse,
            "residual_variance": self.residual_variance
        }


def multiple_regression(
    features: Sequence[Sequence[float]],
    target: Sequence[float]
) -> RegressionResult:
    """
    Estimate OLS coefficients using the normal equations.

    beta = (X'X)^(-1) X'y

    The linear solver uses pivoting and rejects singular designs.
    """

    x = validate_matrix(features)
    y = list(map(float, target))

    n = len(x)
    p = len(x[0])

    if len(y) != n:
        raise ValidationError("Feature and target counts differ.")

    if any(not math.isfinite(v) for v in y):
        raise ValidationError("Target contains non-finite values.")

    if n <= p + 1:
        raise ValidationError(
            "More observations than estimated coefficients are required."
        )

    design = [[1.0] + row for row in x]
    xt = transpose(design)

    xtx = matmul(xt, design)
    xty = [
        sum(xt[i][j] * y[j] for j in range(n))
        for i in range(p + 1)
    ]

    coefficients = solve_linear_system(xtx, xty)

    predictions = [
        sum(a * b for a, b in zip(row, coefficients))
        for row in design
    ]

    residuals = [
        actual - predicted
        for actual, predicted in zip(y, predictions)
    ]

    mean_y = statistics.mean(y)

    ss_res = sum(r ** 2 for r in residuals)
    ss_total = sum((v - mean_y) ** 2 for v in y)

    if ss_total == 0:
        raise StatisticalError(
            "R-squared is undefined for a constant target."
        )

    r_squared = 1 - ss_res / ss_total
    adjusted_r_squared = (
        1 - (1 - r_squared) * (n - 1) / (n - p - 1)
    )

    mse = ss_res / n
    residual_variance = ss_res / (n - p - 1)

    return RegressionResult(
        coefficients=coefficients,
        predictions=predictions,
        residuals=residuals,
        r_squared=r_squared,
        adjusted_r_squared=adjusted_r_squared,
        mse=mse,
        rmse=math.sqrt(mse),
        residual_variance=residual_variance
    )


def variance_inflation_factors(
    features: Sequence[Sequence[float]]
) -> list[float]:
    """Estimate VIF by regressing each predictor on the remaining predictors."""

    x = validate_matrix(features)
    p = len(x[0])

    if p < 2:
        raise ValidationError("VIF requires at least two predictors.")

    results = []

    for target_index in range(p):
        remaining = [
            [row[j] for j in range(p) if j != target_index]
            for row in x
        ]

        target = [row[target_index] for row in x]

        try:
            result = multiple_regression(remaining, target)
        except StatisticalError as exc:
            raise StatisticalError(
                f"VIF cannot be calculated for predictor {target_index}."
            ) from exc

        if result.r_squared >= 1 - 1e-12:
            raise StatisticalError("Perfect multicollinearity detected.")

        results.append(1 / (1 - result.r_squared))

    return results


def generate_multivariate_normal(
    mean: Sequence[float],
    covariance: Sequence[Sequence[float]],
    sample_count: int,
    seed: int = 42
) -> list[list[float]]:
    """Generate reproducible multivariate normal observations."""

    mu = list(map(float, mean))

    if sample_count <= 0:
        raise ValidationError("Sample count must be positive.")

    lower = cholesky(covariance)

    if len(lower) != len(mu):
        raise ValidationError("Mean and covariance dimensions differ.")

    rng = random.Random(seed)
    samples = []

    for _ in range(sample_count):
        z = [rng.gauss(0, 1) for _ in mu]

        samples.append([
            mu[i] + sum(lower[i][j] * z[j] for j in range(i + 1))
            for i in range(len(mu))
        ])

    return samples


def run_example() -> None:
    print("=" * 65)
    print("MULTIVARIATE STATISTICS ANALYSIS")
    print("=" * 65)

    # Predictors: advertising expenditure and employee training hours.
    features = [
        [10, 2], [12, 3], [14, 4], [16, 3],
        [18, 5], [20, 6], [22, 5], [24, 7],
        [26, 8], [28, 7], [30, 9], [32, 10]
    ]

    # Target: observed monthly sales.
    target = [
        40, 44, 49, 50, 57, 63,
        65, 72, 78, 80, 87, 94
    ]

    result = multiple_regression(features, target)

    print("\n1. MULTIPLE LINEAR REGRESSION")
    print("Intercept:", round(result.coefficients[0], 4))
    print("Coefficients:", [
        round(v, 4) for v in result.coefficients[1:]
    ])
    print("R-squared:", round(result.r_squared, 4))
    print("Adjusted R-squared:", round(result.adjusted_r_squared, 4))
    print("RMSE:", round(result.rmse, 4))
    print("Residual variance:", round(result.residual_variance, 4))

    print("\n2. NEW OBSERVATION PREDICTION")
    prediction = result.predict([[25, 6]])
    print("Predicted sales:", round(prediction[0], 4))

    print("\n3. COVARIANCE STRUCTURE")

    cov = covariance_matrix(features)
    corr = correlation_matrix(features)

    print("Covariance matrix:")
    print(json.dumps(cov, indent=2))

    print("Correlation matrix:")
    print(json.dumps(corr, indent=2))

    print("\n4. MULTICOLLINEARITY")

    print("Variance inflation factors:", [
        round(v, 4)
        for v in variance_inflation_factors(features)
    ])

    print("\n5. MULTIVARIATE NORMAL DISTRIBUTION")

    mean = [50.0, 60.0]

    covariance = [
        [100.0, 30.0],
        [30.0, 144.0]
    ]

    observation = [55.0, 65.0]

    distance = mahalanobis_distance(
        observation, mean, covariance
    )

    density = multivariate_normal_density(
        observation, mean, covariance
    )

    print("Mean:", mean)
    print("Observation:", observation)
    print("Mahalanobis distance:", round(distance, 6))
    print("Probability density:", f"{density:.10f}")

    print("\n6. MULTIVARIATE RANDOM SAMPLING")

    samples = generate_multivariate_normal(
        mean, covariance, sample_count=1000
    )

    empirical_covariance = covariance_matrix(samples)

    print("Generated observations:", len(samples))
    print("Empirical covariance matrix:")
    print(json.dumps(empirical_covariance, indent=2))

    print("\n7. VALIDATION AND EDGE CASES")

    try:
        solve_linear_system(
            [[1, 2], [2, 4]],
            [3, 6]
        )
    except StatisticalError as exc:
        print("Singular matrix correctly rejected:", exc)

    try:
        covariance_matrix([[1, 2]])
    except ValidationError as exc:
        print("Insufficient observations correctly rejected:", exc)

    try:
        cholesky([[1, 2], [2, 1]])
    except StatisticalError as exc:
        print("Non-positive-definite matrix rejected:", exc)

    # Verify that a fitted model reproduces its training observations.
    assert len(result.predictions) == len(target)
    assert 0 <= result.r_squared <= 1
    assert result.rmse >= 0

    print("\nAll computational assertions passed.")


if __name__ == "__main__":
    run_example()
