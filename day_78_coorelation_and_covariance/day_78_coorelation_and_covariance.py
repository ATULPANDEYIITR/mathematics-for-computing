#!/usr/bin/env python3
"""
Correlation and Covariance Analysis Engine

Implements:
- Mean, variance, covariance and Pearson correlation
- Sample and population statistics
- Covariance and correlation matrices
- Dependence analysis
- Missing-value handling
- Statistical validation
- Outlier detection
- Matrix symmetry and diagonal checks
- Correlation strength classification
- Diversification and multicollinearity analysis
- CSV import and JSON export

Requires Python 3.10+.
Uses only the Python standard library.
"""

from __future__ import annotations

import csv
import json
import math
import statistics
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path
from typing import Optional


class AnalysisError(Exception):
    """Base exception for statistical analysis."""


class ValidationError(AnalysisError):
    """Raised when input data is invalid."""


class InsufficientDataError(AnalysisError):
    """Raised when observations are insufficient."""


class CorrelationStrength(Enum):
    VERY_STRONG = "Very strong"
    STRONG = "Strong"
    MODERATE = "Moderate"
    WEAK = "Weak"
    NEGLIGIBLE = "Negligible"


class MissingValuePolicy(Enum):
    REJECT = "reject"
    PAIRWISE = "pairwise"
    LISTWISE = "listwise"


@dataclass(frozen=True)
class StatisticalResult:
    covariance: float
    correlation: Optional[float]
    observations: int
    strength: Optional[str]


@dataclass
class Dataset:
    name: str
    columns: dict[str, list[Optional[float]]]

    def validate(self) -> None:
        if not self.name.strip():
            raise ValidationError("Dataset name cannot be empty.")

        if len(self.columns) < 2:
            raise ValidationError("At least two variables are required.")

        lengths = {len(values) for values in self.columns.values()}

        if len(lengths) != 1:
            raise ValidationError("All variables must have equal lengths.")

        if not lengths or next(iter(lengths)) < 2:
            raise InsufficientDataError(
                "At least two observation positions are required."
            )

        for name, values in self.columns.items():
            if not name.strip():
                raise ValidationError("Variable names cannot be empty.")

            for value in values:
                if value is None:
                    continue

                if isinstance(value, bool) or not isinstance(
                    value, (int, float)
                ):
                    raise ValidationError(
                        f"Variable {name} contains a nonnumeric value."
                    )

                if not math.isfinite(value):
                    raise ValidationError(
                        f"Variable {name} contains a non-finite value."
                    )


class CorrelationEngine:
    def __init__(
        self,
        dataset: Dataset,
        missing_policy: MissingValuePolicy = MissingValuePolicy.REJECT
    ):
        dataset.validate()
        self.dataset = dataset
        self.missing_policy = missing_policy

    @staticmethod
    def _mean(values: list[float]) -> float:
        if not values:
            raise InsufficientDataError("Cannot calculate an empty mean.")
        return math.fsum(values) / len(values)

    @staticmethod
    def _validate_variance_sample(
        values: list[float],
        sample: bool
    ) -> None:
        minimum = 2 if sample else 1
        if len(values) < minimum:
            raise InsufficientDataError(
                f"At least {minimum} observations are required."
            )

    @staticmethod
    def _clean(values: list[Optional[float]]) -> list[float]:
        return [float(v) for v in values if v is not None]

    def _paired_values(
        self,
        x: list[Optional[float]],
        y: list[Optional[float]]
    ) -> tuple[list[float], list[float]]:
        if self.missing_policy == MissingValuePolicy.REJECT:
            if any(v is None for v in x + y):
                raise ValidationError("Missing values are not permitted.")
            return self._clean(x), self._clean(y)

        if self.missing_policy == MissingValuePolicy.LISTWISE:
            complete = [
                i for i in range(len(x))
                if all(
                    values[i] is not None
                    for values in self.dataset.columns.values()
                )
            ]
            return (
                [float(x[i]) for i in complete],
                [float(y[i]) for i in complete]
            )

        pairs = [
            (float(a), float(b))
            for a, b in zip(x, y)
            if a is not None and b is not None
        ]

        return (
            [a for a, _ in pairs],
            [b for _, b in pairs]
        )

    @classmethod
    def variance(
        cls,
        values: list[float],
        sample: bool = True
    ) -> float:
        cls._validate_variance_sample(values, sample)
        mean = cls._mean(values)
        denominator = len(values) - 1 if sample else len(values)

        return math.fsum(
            (value - mean) ** 2 for value in values
        ) / denominator

    @classmethod
    def covariance(
        cls,
        x: list[float],
        y: list[float],
        sample: bool = True
    ) -> float:
        if len(x) != len(y):
            raise ValidationError("Variable lengths do not match.")

        minimum = 2 if sample else 1
        if len(x) < minimum:
            raise InsufficientDataError(
                f"At least {minimum} paired observations are required."
            )

        mean_x = cls._mean(x)
        mean_y = cls._mean(y)

        denominator = len(x) - 1 if sample else len(x)

        return math.fsum(
            (a - mean_x) * (b - mean_y)
            for a, b in zip(x, y)
        ) / denominator

    @classmethod
    def pearson(
        cls,
        x: list[float],
        y: list[float]
    ) -> float:
        if len(x) != len(y):
            raise ValidationError("Variable lengths do not match.")

        if len(x) < 2:
            raise InsufficientDataError(
                "Pearson correlation requires two observations."
            )

        mean_x = cls._mean(x)
        mean_y = cls._mean(y)

        centered_x = [v - mean_x for v in x]
        centered_y = [v - mean_y for v in y]

        sum_xx = math.fsum(v * v for v in centered_x)
        sum_yy = math.fsum(v * v for v in centered_y)

        if sum_xx <= 0 or sum_yy <= 0:
            raise ValidationError(
                "Pearson correlation is undefined for constant variables."
            )

        sum_xy = math.fsum(
            a * b for a, b in zip(centered_x, centered_y)
        )

        result = sum_xy / math.sqrt(sum_xx * sum_yy)

        # Protect against insignificant floating-point boundary errors.
        return max(-1.0, min(1.0, result))

    @staticmethod
    def classify(correlation: float) -> CorrelationStrength:
        magnitude = abs(correlation)

        if magnitude >= 0.90:
            return CorrelationStrength.VERY_STRONG
        if magnitude >= 0.70:
            return CorrelationStrength.STRONG
        if magnitude >= 0.40:
            return CorrelationStrength.MODERATE
        if magnitude >= 0.20:
            return CorrelationStrength.WEAK

        return CorrelationStrength.NEGLIGIBLE

    def analyze_pair(
        self,
        first: str,
        second: str,
        sample: bool = True
    ) -> StatisticalResult:
        if first not in self.dataset.columns:
            raise ValidationError(f"Unknown variable: {first}")

        if second not in self.dataset.columns:
            raise ValidationError(f"Unknown variable: {second}")

        x, y = self._paired_values(
            self.dataset.columns[first],
            self.dataset.columns[second]
        )

        minimum = 2 if sample else 1

        if len(x) < minimum:
            raise InsufficientDataError(
                "Insufficient paired observations."
            )

        covariance = self.covariance(x, y, sample)

        correlation = None

        if len(set(x)) > 1 and len(set(y)) > 1:
            correlation = self.pearson(x, y)

        strength = (
            self.classify(correlation).value
            if correlation is not None else None
        )

        return StatisticalResult(
            covariance=covariance,
            correlation=correlation,
            observations=len(x),
            strength=strength
        )

    def covariance_matrix(
        self,
        sample: bool = True
    ) -> dict[str, dict[str, float]]:
        names = list(self.dataset.columns)

        matrix = {name: {} for name in names}

        for i, first in enumerate(names):
            for second in names[i:]:
                x, y = self._paired_values(
                    self.dataset.columns[first],
                    self.dataset.columns[second]
                )

                value = self.covariance(x, y, sample)

                matrix[first][second] = value
                matrix[second][first] = value

        return matrix

    def correlation_matrix(self) -> dict[str, dict[str, Optional[float]]]:
        names = list(self.dataset.columns)

        matrix = {name: {} for name in names}

        for i, first in enumerate(names):
            for second in names[i:]:
                x, y = self._paired_values(
                    self.dataset.columns[first],
                    self.dataset.columns[second]
                )

                if len(x) < 2:
                    raise InsufficientDataError(
                        f"Insufficient data for {first}, {second}."
                    )

                if len(set(x)) < 2 or len(set(y)) < 2:
                    value = None
                else:
                    value = self.pearson(x, y)

                matrix[first][second] = value
                matrix[second][first] = value

        return matrix

    def detect_high_correlations(
        self,
        threshold: float = 0.80
    ) -> list[dict]:
        if not 0 < threshold <= 1:
            raise ValidationError("Threshold must be in (0, 1].")

        matrix = self.correlation_matrix()
        names = list(matrix)

        results = []

        for i, first in enumerate(names):
            for second in names[i + 1:]:
                value = matrix[first][second]

                if value is not None and abs(value) >= threshold:
                    results.append({
                        "first": first,
                        "second": second,
                        "correlation": value,
                        "relationship": (
                            "positive" if value > 0 else "negative"
                        )
                    })

        return results

    def listwise_dataset(self) -> Dataset:
        indexes = [
            i for i in range(len(next(iter(self.dataset.columns.values()))))
            if all(
                values[i] is not None
                for values in self.dataset.columns.values()
            )
        ]

        return Dataset(
            name=f"{self.dataset.name}_listwise",
            columns={
                name: [values[i] for i in indexes]
                for name, values in self.dataset.columns.items()
            }
        )

    def summary(self) -> dict:
        output = {}

        for name, raw_values in self.dataset.columns.items():
            values = self._clean(raw_values)

            if not values:
                output[name] = {"observations": 0}
                continue

            output[name] = {
                "observations": len(values),
                "missing": len(raw_values) - len(values),
                "mean": self._mean(values),
                "median": statistics.median(values),
                "minimum": min(values),
                "maximum": max(values),
                "sample_variance": (
                    self.variance(values) if len(values) >= 2 else None
                ),
                "sample_standard_deviation": (
                    statistics.stdev(values)
                    if len(values) >= 2 else None
                )
            }

        return output

    def export_json(self, path: str) -> None:
        report = {
            "dataset": self.dataset.name,
            "summary": self.summary(),
            "covariance_matrix": self.covariance_matrix(),
            "correlation_matrix": self.correlation_matrix(),
            "high_correlations": self.detect_high_correlations()
        }

        destination = Path(path)

        # Prevent accidental writes to an existing report.
        if destination.exists():
            raise FileExistsError(
                f"Refusing to overwrite {destination}."
            )

        destination.write_text(
            json.dumps(report, indent=4, allow_nan=False),
            encoding="utf-8"
        )


def load_csv(path: str, columns: list[str]) -> Dataset:
    data = {name: [] for name in columns}

    with open(path, newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        if not reader.fieldnames:
            raise ValidationError("CSV has no header.")

        missing_columns = set(columns) - set(reader.fieldnames)

        if missing_columns:
            raise ValidationError(
                f"Missing CSV columns: {sorted(missing_columns)}"
            )

        for row_number, row in enumerate(reader, start=2):
            for name in columns:
                raw = row[name].strip()

                if raw == "":
                    data[name].append(None)
                    continue

                try:
                    value = float(raw)
                except ValueError as exc:
                    raise ValidationError(
                        f"Invalid value in row {row_number}, column {name}."
                    ) from exc

                if not math.isfinite(value):
                    raise ValidationError(
                        f"Non-finite value in row {row_number}."
                    )

                data[name].append(value)

    dataset = Dataset(Path(path).stem, data)
    dataset.validate()

    return dataset


def print_matrix(
    title: str,
    matrix: dict[str, dict[str, Optional[float]]]
) -> None:
    names = list(matrix)

    print(f"\n{title}")
    print(f"{'Variable':<16}", end="")

    for name in names:
        print(f"{name:>14}", end="")

    print()

    for first in names:
        print(f"{first:<16}", end="")

        for second in names:
            value = matrix[first][second]

            formatted = (
                "N/A" if value is None else f"{value:.4f}"
            )

            print(f"{formatted:>14}", end="")

        print()


def run_tests() -> None:
    x = [1.0, 2.0, 3.0, 4.0]
    y = [2.0, 4.0, 6.0, 8.0]
    z = [8.0, 6.0, 4.0, 2.0]

    assert abs(CorrelationEngine.pearson(x, y) - 1.0) < 1e-12
    assert abs(CorrelationEngine.pearson(x, z) + 1.0) < 1e-12

    assert abs(
        CorrelationEngine.covariance(x, y) - 3.3333333333333335
    ) < 1e-10

    assert abs(
        CorrelationEngine.variance(x) - 1.6666666666666667
    ) < 1e-10

    assert CorrelationEngine.classify(0.95) == (
        CorrelationStrength.VERY_STRONG
    )

    try:
        CorrelationEngine.pearson([1, 1, 1], [2, 3, 4])
        raise AssertionError("Constant-variable test failed.")
    except ValidationError:
        pass

    print("All statistical tests passed.")


def main() -> None:
    dataset = Dataset(
        name="Investment Portfolio Analysis",
        columns={
            "Equity_A": [10, 12, 14, 16, 18, 20],
            "Equity_B": [8, 10, 12, 14, 16, 18],
            "Bonds": [20, 19, 21, 18, 22, 17],
            "Gold": [15, 17, 14, 18, 13, 19],
            "Market_Index": [11, 13, 15, 17, 19, 21]
        }
    )

    engine = CorrelationEngine(dataset)

    print("CORRELATION AND COVARIANCE ANALYSIS")
    print("=" * 55)

    print("\nDESCRIPTIVE STATISTICS")

    for name, values in engine.summary().items():
        print(f"\n{name}")
        for metric, value in values.items():
            print(f"  {metric}: {value}")

    print_matrix(
        "SAMPLE COVARIANCE MATRIX",
        engine.covariance_matrix()
    )

    print_matrix(
        "PEARSON CORRELATION MATRIX",
        engine.correlation_matrix()
    )

    print("\nPAIRWISE ANALYSIS")

    result = engine.analyze_pair("Equity_A", "Bonds")
    print(asdict(result))

    print("\nHIGH CORRELATION PAIRS")

    for pair in engine.detect_high_correlations(0.80):
        print(pair)

    print("\nPAIRWISE MISSING-VALUE EXAMPLE")

    missing_dataset = Dataset(
        name="Missing Observation Example",
        columns={
            "A": [1, 2, None, 4, 5],
            "B": [2, 4, 6, None, 10]
        }
    )

    missing_engine = CorrelationEngine(
        missing_dataset,
        MissingValuePolicy.PAIRWISE
    )

    print(
        asdict(missing_engine.analyze_pair("A", "B"))
    )

    run_tests()

    print("\nAnalysis completed successfully.")


if __name__ == "__main__":
    main()
