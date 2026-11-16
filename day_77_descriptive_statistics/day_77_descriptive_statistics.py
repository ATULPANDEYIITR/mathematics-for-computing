#!/usr/bin/env python3
"""
Descriptive Statistics
Mean, Median, Mode, Variance, Standard Deviation, and Quantiles.

Features:
- Numeric data validation
- Population and sample statistics
- Arithmetic mean, median, and multimodal mode
- Population and sample variance
- Population and sample standard deviation
- Quantiles and percentiles
- Interquartile range and outlier detection
- Frequency distributions
- CSV import and JSON export
- Numerical stability using Welford's algorithm
- Unit tests and edge-case handling

Run:
    python descriptive_statistics.py
    python descriptive_statistics.py --csv data.csv --column value
    python descriptive_statistics.py --output statistics.json
"""

from __future__ import annotations

import argparse
import csv
import json
import logging
import math
import statistics
from collections import Counter
from dataclasses import asdict, dataclass
from enum import Enum
from pathlib import Path
from typing import Iterable, Optional


logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s"
)

logger = logging.getLogger("descriptive_statistics")


class StatisticsError(ValueError):
    """Raised when statistical operations cannot be performed."""


class VarianceType(Enum):
    POPULATION = "population"
    SAMPLE = "sample"


@dataclass(frozen=True)
class Dataset:
    name: str
    values: tuple[float, ...]

    def __post_init__(self):
        if not self.name.strip():
            raise StatisticsError("Dataset name cannot be empty.")

        if not self.values:
            raise StatisticsError("Dataset cannot be empty.")

        if any(not math.isfinite(value) for value in self.values):
            raise StatisticsError("Dataset contains non-finite values.")


@dataclass
class RunningStatistics:
    count: int = 0
    mean: float = 0.0
    m2: float = 0.0
    minimum: float = math.inf
    maximum: float = -math.inf

    def update(self, value: float) -> None:
        if not math.isfinite(value):
            raise StatisticsError("Observation must be finite.")

        self.count += 1

        delta = value - self.mean
        self.mean += delta / self.count
        delta2 = value - self.mean

        self.m2 += delta * delta2

        self.minimum = min(self.minimum, value)
        self.maximum = max(self.maximum, value)

    def variance(self, sample: bool = False) -> float:
        denominator = self.count - 1 if sample else self.count

        if denominator <= 0:
            raise StatisticsError(
                "Insufficient observations for requested variance."
            )

        return self.m2 / denominator

    def standard_deviation(self, sample: bool = False) -> float:
        return math.sqrt(self.variance(sample))


class DescriptiveStatistics:
    def __init__(self, dataset: Dataset):
        self.dataset = dataset
        self.values = dataset.values
        self.sorted_values = tuple(sorted(self.values))
        self.running = RunningStatistics()

        for value in self.values:
            self.running.update(value)

    @classmethod
    def from_values(
        cls,
        values: Iterable[float],
        name: str = "Dataset"
    ) -> DescriptiveStatistics:
        converted = []

        for value in values:
            if isinstance(value, bool):
                raise StatisticsError("Boolean values are not valid observations.")

            try:
                number = float(value)
            except (TypeError, ValueError, OverflowError) as exc:
                raise StatisticsError(
                    f"Invalid numeric observation: {value!r}"
                ) from exc

            if not math.isfinite(number):
                raise StatisticsError(
                    f"Non-finite observation: {value!r}"
                )

            converted.append(number)

        return cls(Dataset(name, tuple(converted)))

    @classmethod
    def from_csv(
        cls,
        filepath: str,
        column: str,
        name: Optional[str] = None
    ) -> DescriptiveStatistics:
        values = []

        with Path(filepath).open(
            "r",
            newline="",
            encoding="utf-8-sig"
        ) as file:
            reader = csv.DictReader(file)

            if not reader.fieldnames or column not in reader.fieldnames:
                raise StatisticsError(
                    f"Column {column!r} does not exist."
                )

            for row_number, row in enumerate(reader, start=2):
                raw = row.get(column)

                if raw is None or not raw.strip():
                    logger.warning(
                        "Skipping missing value at row %d.",
                        row_number
                    )
                    continue

                try:
                    values.append(float(raw))
                except ValueError as exc:
                    raise StatisticsError(
                        f"Invalid value at CSV row {row_number}: {raw}"
                    ) from exc

        return cls.from_values(
            values,
            name or Path(filepath).stem
        )

    @property
    def count(self) -> int:
        return len(self.values)

    def mean(self) -> float:
        return self.running.mean

    def median(self) -> float:
        return statistics.median(self.sorted_values)

    def mode(self) -> list[float]:
        frequencies = Counter(self.values)
        maximum_frequency = max(frequencies.values())

        if maximum_frequency == 1:
            return []

        return sorted(
            value
            for value, frequency in frequencies.items()
            if frequency == maximum_frequency
        )

    def frequency_distribution(self) -> dict[float, int]:
        return dict(sorted(Counter(self.values).items()))

    def variance(
        self,
        variance_type: VarianceType = VarianceType.POPULATION
    ) -> float:
        return self.running.variance(
            sample=variance_type == VarianceType.SAMPLE
        )

    def standard_deviation(
        self,
        variance_type: VarianceType = VarianceType.POPULATION
    ) -> float:
        return math.sqrt(self.variance(variance_type))

    def quantile(self, probability: float) -> float:
        """
        Linear interpolation using the R-7 quantile convention.

        Position = (n - 1) * probability
        """
        if not 0 <= probability <= 1:
            raise StatisticsError(
                "Quantile probability must be between 0 and 1."
            )

        position = (self.count - 1) * probability

        lower = math.floor(position)
        upper = math.ceil(position)

        if lower == upper:
            return self.sorted_values[lower]

        fraction = position - lower

        return (
            self.sorted_values[lower] * (1 - fraction)
            + self.sorted_values[upper] * fraction
        )

    def percentile(self, percentage: float) -> float:
        if not 0 <= percentage <= 100:
            raise StatisticsError(
                "Percentile must be between 0 and 100."
            )

        return self.quantile(percentage / 100)

    def quartiles(self) -> dict[str, float]:
        return {
            "Q1": self.quantile(0.25),
            "Q2": self.quantile(0.50),
            "Q3": self.quantile(0.75)
        }

    def interquartile_range(self) -> float:
        return self.quantile(0.75) - self.quantile(0.25)

    def outliers(self, multiplier: float = 1.5) -> list[float]:
        if not math.isfinite(multiplier) or multiplier < 0:
            raise StatisticsError(
                "Outlier multiplier must be finite and non-negative."
            )

        q1 = self.quantile(0.25)
        q3 = self.quantile(0.75)
        spread = q3 - q1

        lower_bound = q1 - multiplier * spread
        upper_bound = q3 + multiplier * spread

        return [
            value
            for value in self.values
            if value < lower_bound or value > upper_bound
        ]

    def summary(self) -> dict:
        quartiles = self.quartiles()

        return {
            "dataset": self.dataset.name,
            "count": self.count,
            "minimum": self.running.minimum,
            "maximum": self.running.maximum,
            "range": self.running.maximum - self.running.minimum,
            "mean": self.mean(),
            "median": self.median(),
            "mode": self.mode(),
            "population_variance": self.variance(
                VarianceType.POPULATION
            ),
            "sample_variance": (
                self.variance(VarianceType.SAMPLE)
                if self.count >= 2 else None
            ),
            "population_standard_deviation": self.standard_deviation(),
            "sample_standard_deviation": (
                self.standard_deviation(VarianceType.SAMPLE)
                if self.count >= 2 else None
            ),
            "quartiles": quartiles,
            "interquartile_range": self.interquartile_range(),
            "percentiles": {
                "P10": self.percentile(10),
                "P25": self.percentile(25),
                "P50": self.percentile(50),
                "P75": self.percentile(75),
                "P90": self.percentile(90),
                "P95": self.percentile(95)
            },
            "outliers": self.outliers(),
            "frequency_distribution": self.frequency_distribution()
        }


def run_tests() -> None:
    dataset = DescriptiveStatistics.from_values(
        [2, 4, 4, 4, 5, 5, 7, 9],
        "Test Dataset"
    )

    assert dataset.count == 8
    assert math.isclose(dataset.mean(), 5.0)
    assert math.isclose(dataset.median(), 4.5)
    assert dataset.mode() == [4.0]
    assert math.isclose(dataset.variance(), 4.0)
    assert math.isclose(dataset.variance(VarianceType.SAMPLE), 32 / 7)
    assert math.isclose(dataset.quantile(0.25), 4.0)
    assert math.isclose(dataset.quantile(0.75), 5.5)

    tied = DescriptiveStatistics.from_values([1, 1, 2, 2])
    assert tied.mode() == [1.0, 2.0]

    unique = DescriptiveStatistics.from_values([1, 2, 3])
    assert unique.mode() == []

    single = DescriptiveStatistics.from_values([10])
    assert single.variance() == 0.0

    try:
        single.variance(VarianceType.SAMPLE)
        raise AssertionError("Sample variance should reject one observation.")
    except StatisticsError:
        pass

    try:
        DescriptiveStatistics.from_values([1, float("nan")])
        raise AssertionError("NaN should be rejected.")
    except StatisticsError:
        pass

    try:
        dataset.quantile(1.5)
        raise AssertionError("Invalid quantile should be rejected.")
    except StatisticsError:
        pass

    print("All statistical tests passed.")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Descriptive Statistics Analysis"
    )

    parser.add_argument("--csv", help="Input CSV file.")
    parser.add_argument("--column", default="value")
    parser.add_argument("--output", help="Output JSON file.")
    parser.add_argument("--test", action="store_true")

    args = parser.parse_args()

    if args.test:
        run_tests()
        return

    if args.csv:
        analyzer = DescriptiveStatistics.from_csv(
            args.csv,
            args.column
        )
    else:
        observations = [
            12, 15, 18, 20, 15, 22, 25, 18,
            30, 35, 18, 40, 45, 50, 55, 60
        ]

        analyzer = DescriptiveStatistics.from_values(
            observations,
            "Employee Performance Measurements"
        )

    report = analyzer.summary()

    print(json.dumps(report, indent=4))

    if args.output:
        output_path = Path(args.output)
        output_path.write_text(
            json.dumps(report, indent=4),
            encoding="utf-8"
        )
        logger.info("Report saved to %s", output_path)


if __name__ == "__main__":
    main()
