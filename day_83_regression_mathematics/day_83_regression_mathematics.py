#!/usr/bin/env python3
"""
Regression Mathematics: Simple Linear Regression, Least Squares, and Residuals.

Implements:
- Dataset validation
- Descriptive statistics
- Ordinary Least Squares (OLS)
- Slope and intercept estimation
- Fitted values and predictions
- Residual calculations
- Sum of Squares decomposition
- R-squared, RMSE, MAE, and residual diagnostics
- Prediction and model validation
- CSV dataset loading
- Numerical edge-case handling

Requires Python 3.10+.
Uses only the Python standard library.
"""

from __future__ import annotations

import csv
import math
import statistics
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Optional


class RegressionError(Exception):
    """Base exception for regression operations."""


class ValidationError(RegressionError):
    """Raised when input data is invalid."""


class InsufficientDataError(RegressionError):
    """Raised when the dataset contains too few observations."""


class NumericalError(RegressionError):
    """Raised when a numerical calculation is unstable."""


@dataclass(frozen=True)
class Observation:
    x: float
    y: float

    def __post_init__(self):
        if not math.isfinite(self.x):
            raise ValidationError("Independent variable must be finite.")

        if not math.isfinite(self.y):
            raise ValidationError("Dependent variable must be finite.")


@dataclass(frozen=True)
class DescriptiveStatistics:
    count: int
    mean_x: float
    mean_y: float
    variance_x: float
    variance_y: float
    covariance_xy: float


@dataclass(frozen=True)
class RegressionMetrics:
    sse: float
    ssr: float
    sst: float
    r_squared: float
    rmse: float
    mae: float
    residual_mean: float
    residual_standard_deviation: float


@dataclass(frozen=True)
class LinearRegressionModel:
    slope: float
    intercept: float
    metrics: RegressionMetrics
    statistics: DescriptiveStatistics
    fitted_values: tuple[float, ...]
    residuals: tuple[float, ...]
    observation_count: int

    def predict(self, x: float) -> float:
        if not math.isfinite(x):
            raise ValidationError("Prediction input must be finite.")

        result = self.intercept + self.slope * x

        if not math.isfinite(result):
            raise NumericalError("Prediction exceeds numeric limits.")

        return result

    def predict_many(self, values: Iterable[float]) -> list[float]:
        return [self.predict(x) for x in values]

    def equation(self) -> str:
        sign = "+" if self.slope >= 0 else "-"
        return (
            f"y = {self.intercept:.6f} "
            f"{sign} {abs(self.slope):.6f}x"
        )

    def residual_report(self) -> list[dict]:
        return [
            {
                "observation": index + 1,
                "actual": actual,
                "fitted": fitted,
                "residual": residual,
                "squared_residual": residual ** 2,
            }
            for index, (actual, fitted, residual) in enumerate(
                zip(
                    self._actual_values,
                    self.fitted_values,
                    self.residuals,
                )
            )
        ]

    # Actual values are retained internally for diagnostic reporting.
    _actual_values: tuple[float, ...] = ()


class SimpleLinearRegression:
    """
    Ordinary Least Squares regression with one independent variable.

    Model:
        y_hat = intercept + slope * x

    Slope:
        b1 = sum((x - mean_x)(y - mean_y))
             / sum((x - mean_x)^2)

    Intercept:
        b0 = mean_y - b1 * mean_x

    Residual:
        e_i = y_i - y_hat_i
    """

    def __init__(self, observations: Iterable[Observation]):
        self.observations = tuple(observations)
        self._validate_dataset()

    def _validate_dataset(self):
        if len(self.observations) < 3:
            raise InsufficientDataError(
                "At least three observations are required."
            )

        if not all(
            isinstance(item, Observation)
            for item in self.observations
        ):
            raise ValidationError(
                "Every dataset entry must be an Observation."
            )

        if len({item.x for item in self.observations}) < 2:
            raise ValidationError(
                "Independent variable must contain distinct values."
            )

    def descriptive_statistics(self) -> DescriptiveStatistics:
        x_values = [item.x for item in self.observations]
        y_values = [item.y for item in self.observations]

        mean_x = statistics.fmean(x_values)
        mean_y = statistics.fmean(y_values)

        variance_x = statistics.variance(x_values)
        variance_y = statistics.variance(y_values)

        covariance_xy = sum(
            (x - mean_x) * (y - mean_y)
            for x, y in zip(x_values, y_values)
        ) / (len(x_values) - 1)

        return DescriptiveStatistics(
            count=len(x_values),
            mean_x=mean_x,
            mean_y=mean_y,
            variance_x=variance_x,
            variance_y=variance_y,
            covariance_xy=covariance_xy,
        )

    def fit(self) -> LinearRegressionModel:
        x_values = [item.x for item in self.observations]
        y_values = [item.y for item in self.observations]

        n = len(self.observations)

        mean_x = statistics.fmean(x_values)
        mean_y = statistics.fmean(y_values)

        # Centered calculations improve numerical stability.
        centered_x = [x - mean_x for x in x_values]
        centered_y = [y - mean_y for y in y_values]

        sxx = math.fsum(value ** 2 for value in centered_x)

        sxy = math.fsum(
            x * y
            for x, y in zip(centered_x, centered_y)
        )

        if sxx <= 0 or not math.isfinite(sxx):
            raise NumericalError(
                "Cannot estimate slope because X has no usable variance."
            )

        slope = sxy / sxx
        intercept = mean_y - slope * mean_x

        fitted_values = tuple(
            intercept + slope * x
            for x in x_values
        )

        residuals = tuple(
            actual - fitted
            for actual, fitted in zip(y_values, fitted_values)
        )

        sse = math.fsum(e ** 2 for e in residuals)

        sst = math.fsum(
            (y - mean_y) ** 2
            for y in y_values
        )

        # In OLS with an intercept, SST = SSR + SSE.
        ssr = math.fsum(
            (fitted - mean_y) ** 2
            for fitted in fitted_values
        )

        if sst <= 0:
            raise NumericalError(
                "R-squared cannot be calculated for constant Y."
            )

        r_squared = 1.0 - sse / sst

        # Avoid tiny floating-point excursions.
        r_squared = min(1.0, max(0.0, r_squared))

        mae = math.fsum(
            abs(error) for error in residuals
        ) / n

        rmse = math.sqrt(sse / n)

        residual_mean = statistics.fmean(residuals)

        residual_std = math.sqrt(
            sse / (n - 2)
        )

        metrics = RegressionMetrics(
            sse=sse,
            ssr=ssr,
            sst=sst,
            r_squared=r_squared,
            rmse=rmse,
            mae=mae,
            residual_mean=residual_mean,
            residual_standard_deviation=residual_std,
        )

        descriptive = self.descriptive_statistics()

        model = LinearRegressionModel(
            slope=slope,
            intercept=intercept,
            metrics=metrics,
            statistics=descriptive,
            fitted_values=fitted_values,
            residuals=residuals,
            observation_count=n,
            _actual_values=tuple(y_values),
        )

        self._validate_model(model)

        return model

    @staticmethod
    def _validate_model(model: LinearRegressionModel):
        if not math.isfinite(model.slope):
            raise NumericalError("Invalid regression slope.")

        if not math.isfinite(model.intercept):
            raise NumericalError("Invalid regression intercept.")

        if abs(math.fsum(model.residuals)) > (
            1e-8 * max(1.0, sum(abs(v) for v in model._actual_values))
        ):
            raise NumericalError(
                "OLS residuals do not satisfy the zero-sum condition."
            )

        if not math.isclose(
            model.metrics.sst,
            model.metrics.sse + model.metrics.ssr,
            rel_tol=1e-8,
            abs_tol=1e-8,
        ):
            raise NumericalError(
                "Sum of squares decomposition failed."
            )


def load_csv(
    file_path: str | Path,
    x_column: str,
    y_column: str,
) -> list[Observation]:
    """Load numeric observations from a CSV file."""

    path = Path(file_path)

    if not path.is_file():
        raise FileNotFoundError(f"Dataset not found: {path}")

    observations = []

    with path.open("r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        if not reader.fieldnames:
            raise ValidationError("CSV file has no header.")

        if x_column not in reader.fieldnames:
            raise ValidationError(f"Missing column: {x_column}")

        if y_column not in reader.fieldnames:
            raise ValidationError(f"Missing column: {y_column}")

        for row_number, row in enumerate(reader, start=2):
            try:
                x = float(row[x_column])
                y = float(row[y_column])

                observations.append(Observation(x, y))

            except (ValueError, TypeError, KeyError) as error:
                raise ValidationError(
                    f"Invalid numeric data on row {row_number}."
                ) from error

    if not observations:
        raise InsufficientDataError("CSV contains no observations.")

    return observations


def display_model(model: LinearRegressionModel):
    print("\n" + "=" * 65)
    print("SIMPLE LINEAR REGRESSION")
    print("=" * 65)

    print(f"Observations       : {model.observation_count}")
    print(f"Regression equation: {model.equation()}")
    print(f"Slope              : {model.slope:.6f}")
    print(f"Intercept          : {model.intercept:.6f}")

    print("\nMODEL PERFORMANCE")
    print("-" * 65)

    print(f"R-squared          : {model.metrics.r_squared:.6f}")
    print(f"RMSE               : {model.metrics.rmse:.6f}")
    print(f"MAE                : {model.metrics.mae:.6f}")

    print("\nSUM OF SQUARES")
    print("-" * 65)

    print(f"SSE                : {model.metrics.sse:.6f}")
    print(f"SSR                : {model.metrics.ssr:.6f}")
    print(f"SST                : {model.metrics.sst:.6f}")

    print("\nRESIDUAL DIAGNOSTICS")
    print("-" * 65)

    print(f"Residual mean      : {model.metrics.residual_mean:.10f}")
    print(
        "Residual std. dev. : "
        f"{model.metrics.residual_standard_deviation:.6f}"
    )

    print("\nOBSERVATION-LEVEL RESULTS")
    print("-" * 65)

    print(
        f"{'No.':<6}{'Actual':<12}"
        f"{'Fitted':<12}{'Residual':<12}"
    )

    for item in model.residual_report():
        print(
            f"{item['observation']:<6}"
            f"{item['actual']:<12.3f}"
            f"{item['fitted']:<12.3f}"
            f"{item['residual']:<12.3f}"
        )

    print("\nPREDICTIONS")
    print("-" * 65)

    for x in (6, 7, 8, 10):
        print(f"X = {x:<5} Predicted Y = {model.predict(x):.4f}")


def run_tests():
    """Verify important mathematical properties."""

    observations = [
        Observation(1, 3),
        Observation(2, 5),
        Observation(3, 7),
        Observation(4, 9),
        Observation(5, 11),
    ]

    model = SimpleLinearRegression(observations).fit()

    assert math.isclose(model.slope, 2.0)
    assert math.isclose(model.intercept, 1.0)
    assert math.isclose(model.metrics.r_squared, 1.0)
    assert math.isclose(model.predict(6), 13.0)
    assert math.isclose(sum(model.residuals), 0.0, abs_tol=1e-10)

    try:
        SimpleLinearRegression([
            Observation(2, 3),
            Observation(2, 5),
            Observation(2, 7),
        ]).fit()
        raise AssertionError("Constant X should fail.")

    except ValidationError:
        pass

    try:
        Observation(float("nan"), 10)
        raise AssertionError("NaN should fail.")

    except ValidationError:
        pass

    print("\nAll regression tests passed.")


def main():
    observations = [
        Observation(1, 2.1),
        Observation(2, 3.9),
        Observation(3, 6.2),
        Observation(4, 7.8),
        Observation(5, 10.1),
        Observation(6, 11.9),
        Observation(7, 14.2),
        Observation(8, 15.8),
    ]

    regression = SimpleLinearRegression(observations)
    model = regression.fit()

    display_model(model)
    run_tests()


if __name__ == "__main__":
    try:
        main()
    except RegressionError as error:
        print(f"Regression error: {error}")
    except Exception as error:
        print(f"Unexpected error: {error}")
        raise
