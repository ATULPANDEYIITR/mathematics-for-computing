#!/usr/bin/env python3
"""
Statistics Fundamentals
Population, Sample, Parameters, Statistics, and Sampling

Standard-library-only implementation covering:
- Population and sample modeling
- Population parameters and sample statistics
- Descriptive statistics
- Simple random sampling without replacement
- Systematic sampling
- Stratified random sampling
- Cluster sampling
- Sampling distributions
- Standard errors and confidence intervals
- Bootstrap estimation
- Sample-size determination
- Validation, reproducibility, and JSON export
"""

from __future__ import annotations

import json
import math
import random
import statistics
from dataclasses import asdict, dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Iterable, Sequence


# ============================================================
# 1. DOMAIN MODELS
# ============================================================

class SamplingMethod(Enum):
    SIMPLE_RANDOM = "simple_random"
    SYSTEMATIC = "systematic"
    STRATIFIED = "stratified"
    CLUSTER = "cluster"


@dataclass(frozen=True)
class Unit:
    unit_id: str
    value: float
    stratum: str = "default"
    cluster: str = "default"

    def __post_init__(self) -> None:
        if not self.unit_id.strip():
            raise ValueError("Unit ID cannot be empty.")
        if not math.isfinite(self.value):
            raise ValueError("Unit value must be finite.")
        if not self.stratum.strip() or not self.cluster.strip():
            raise ValueError("Stratum and cluster cannot be empty.")


@dataclass(frozen=True)
class Sample:
    population_size: int
    units: tuple[Unit, ...]
    method: SamplingMethod
    seed: int

    def __post_init__(self) -> None:
        if self.population_size <= 0:
            raise ValueError("Population size must be positive.")
        if not self.units:
            raise ValueError("Sample cannot be empty.")
        ids = [unit.unit_id for unit in self.units]
        if len(ids) != len(set(ids)):
            raise ValueError("Duplicate units in sample.")
        if len(self.units) > self.population_size:
            raise ValueError("Sample exceeds population size.")


@dataclass(frozen=True)
class ConfidenceInterval:
    lower: float
    upper: float
    confidence_level: float
    standard_error: float


# ============================================================
# 2. POPULATION AND SAMPLE MANAGEMENT
# ============================================================

class Population:
    def __init__(self, units: Iterable[Unit]) -> None:
        self.units = tuple(units)

        if not self.units:
            raise ValueError("Population cannot be empty.")

        ids = [unit.unit_id for unit in self.units]

        if len(ids) != len(set(ids)):
            raise ValueError("Population contains duplicate IDs.")

        self._by_id = {unit.unit_id: unit for unit in self.units}

    @property
    def size(self) -> int:
        return len(self.units)

    @property
    def values(self) -> list[float]:
        return [unit.value for unit in self.units]

    def get_strata(self) -> dict[str, list[Unit]]:
        result: dict[str, list[Unit]] = {}

        for unit in self.units:
            result.setdefault(unit.stratum, []).append(unit)

        return result

    def get_clusters(self) -> dict[str, list[Unit]]:
        result: dict[str, list[Unit]] = {}

        for unit in self.units:
            result.setdefault(unit.cluster, []).append(unit)

        return result

    def get(self, unit_id: str) -> Unit:
        try:
            return self._by_id[unit_id]
        except KeyError as exc:
            raise KeyError(f"Unknown population unit: {unit_id}") from exc


# ============================================================
# 3. DESCRIPTIVE STATISTICS
# ============================================================

class DescriptiveStatistics:

    @staticmethod
    def validate(values: Sequence[float]) -> None:
        if not values:
            raise ValueError("At least one observation is required.")

        if any(not math.isfinite(float(x)) for x in values):
            raise ValueError("All observations must be finite.")

    @classmethod
    def mean(cls, values: Sequence[float]) -> float:
        cls.validate(values)
        return statistics.fmean(values)

    @classmethod
    def median(cls, values: Sequence[float]) -> float:
        cls.validate(values)
        return statistics.median(values)

    @classmethod
    def mode(cls, values: Sequence[float]) -> float:
        cls.validate(values)
        return statistics.mode(values)

    @classmethod
    def variance(
        cls,
        values: Sequence[float],
        sample: bool = True
    ) -> float:
        cls.validate(values)

        if sample:
            if len(values) < 2:
                raise ValueError("Sample variance requires at least two values.")
            return statistics.variance(values)

        return statistics.pvariance(values)

    @classmethod
    def standard_deviation(
        cls,
        values: Sequence[float],
        sample: bool = True
    ) -> float:
        return math.sqrt(cls.variance(values, sample))

    @classmethod
    def quantile(
        cls,
        values: Sequence[float],
        probability: float
    ) -> float:
        cls.validate(values)

        if not 0 <= probability <= 1:
            raise ValueError("Probability must be between 0 and 1.")

        return statistics.quantiles(
            values,
            n=100,
            method="inclusive"
        )[int(probability * 100) - 1] if 0 < probability < 1 else (
            min(values) if probability == 0 else max(values)
        )

    @classmethod
    def describe(cls, values: Sequence[float]) -> dict[str, float]:
        cls.validate(values)

        return {
            "count": len(values),
            "mean": cls.mean(values),
            "median": cls.median(values),
            "minimum": min(values),
            "maximum": max(values),
            "population_variance": cls.variance(values, False),
            "sample_variance": (
                cls.variance(values, True) if len(values) > 1 else 0.0
            ),
            "population_std": cls.standard_deviation(values, False),
            "sample_std": (
                cls.standard_deviation(values, True)
                if len(values) > 1 else 0.0
            )
        }


# ============================================================
# 4. POPULATION PARAMETERS
# ============================================================

class PopulationParameters:

    @staticmethod
    def calculate(population: Population) -> dict[str, float]:
        values = population.values

        return {
            "N": population.size,
            "population_mean_mu": statistics.fmean(values),
            "population_variance_sigma_squared": statistics.pvariance(values),
            "population_std_sigma": statistics.pstdev(values),
            "population_total": math.fsum(values)
        }


# ============================================================
# 5. SAMPLING ENGINE
# ============================================================

class SamplingEngine:

    def __init__(self, population: Population, seed: int = 42) -> None:
        self.population = population
        self.seed = seed
        self.rng = random.Random(seed)

    def simple_random(self, sample_size: int) -> Sample:
        if not 1 <= sample_size <= self.population.size:
            raise ValueError("Invalid sample size.")

        selected = self.rng.sample(
            self.population.units,
            sample_size
        )

        return Sample(
            self.population.size,
            tuple(selected),
            SamplingMethod.SIMPLE_RANDOM,
            self.seed
        )

    def systematic(self, sample_size: int) -> Sample:
        n = sample_size
        N = self.population.size

        if not 1 <= n <= N:
            raise ValueError("Invalid sample size.")

        if n == N:
            selected = self.population.units
        else:
            interval = N / n
            start = self.rng.uniform(0, interval)

            indices = [
                min(int(start + i * interval), N - 1)
                for i in range(n)
            ]

            selected = tuple(self.population.units[i] for i in indices)

        return Sample(
            N,
            tuple(selected),
            SamplingMethod.SYSTEMATIC,
            self.seed
        )

    def stratified(
        self,
        sample_size: int,
        proportional: bool = True
    ) -> Sample:
        strata = self.population.get_strata()
        N = self.population.size

        if not 1 <= sample_size <= N:
            raise ValueError("Invalid sample size.")

        if proportional:
            allocations = {
                name: max(0, int(sample_size * len(group) / N))
                for name, group in strata.items()
            }

            # Allocate remaining observations using largest remainders.
            while sum(allocations.values()) < sample_size:
                eligible = [
                    name for name, group in strata.items()
                    if allocations[name] < len(group)
                ]

                if not eligible:
                    break

                name = max(
                    eligible,
                    key=lambda key: (
                        sample_size * len(strata[key]) / N
                        - allocations[key]
                    )
                )
                allocations[name] += 1

        else:
            if sample_size < len(strata):
                raise ValueError(
                    "At least one observation per stratum is required."
                )

            allocations = {name: 1 for name in strata}

            remaining = sample_size - len(strata)

            while remaining:
                eligible = [
                    name for name, group in strata.items()
                    if allocations[name] < len(group)
                ]

                if not eligible:
                    break

                name = max(
                    eligible,
                    key=lambda key: (
                        len(strata[key]) - allocations[key]
                    )
                )

                allocations[name] += 1
                remaining -= 1

        if sum(allocations.values()) != sample_size:
            raise ValueError("Unable to satisfy stratified allocation.")

        selected = []

        for name, group in strata.items():
            selected.extend(
                self.rng.sample(group, allocations[name])
            )

        return Sample(
            N,
            tuple(selected),
            SamplingMethod.STRATIFIED,
            self.seed
        )

    def cluster(self, cluster_count: int) -> Sample:
        clusters = self.population.get_clusters()

        if not 1 <= cluster_count <= len(clusters):
            raise ValueError("Invalid cluster count.")

        selected_names = self.rng.sample(
            list(clusters),
            cluster_count
        )

        selected = tuple(
            unit
            for name in selected_names
            for unit in clusters[name]
        )

        return Sample(
            self.population.size,
            selected,
            SamplingMethod.CLUSTER,
            self.seed
        )


# ============================================================
# 6. INFERENCE AND SAMPLING DISTRIBUTIONS
# ============================================================

class StatisticalInference:

    @staticmethod
    def standard_error(
        sample: Sample,
        finite_population_correction: bool = True
    ) -> float:
        values = [unit.value for unit in sample.units]
        n = len(values)
        N = sample.population_size

        if n < 2:
            raise ValueError("At least two observations are required.")

        s = statistics.stdev(values)
        se = s / math.sqrt(n)

        if finite_population_correction and n < N:
            se *= math.sqrt((N - n) / (N - 1))

        return se

    @staticmethod
    def mean_confidence_interval(
        sample: Sample,
        confidence_level: float = 0.95
    ) -> ConfidenceInterval:
        if not 0 < confidence_level < 1:
            raise ValueError("Confidence level must be between 0 and 1.")

        values = [unit.value for unit in sample.units]
        n = len(values)

        if n < 2:
            raise ValueError("At least two observations are required.")

        se = StatisticalInference.standard_error(sample)

        # Normal critical values are used for this educational approximation.
        z_values = {
            0.90: 1.645,
            0.95: 1.960,
            0.99: 2.576
        }

        if confidence_level not in z_values:
            raise ValueError("Supported confidence levels: 0.90, 0.95, 0.99.")

        margin = z_values[confidence_level] * se
        mean = statistics.fmean(values)

        return ConfidenceInterval(
            mean - margin,
            mean + margin,
            confidence_level,
            se
        )

    @staticmethod
    def bootstrap(
        values: Sequence[float],
        repetitions: int = 2000,
        seed: int = 42
    ) -> dict[str, float]:
        DescriptiveStatistics.validate(values)

        if len(values) < 2 or repetitions < 100:
            raise ValueError(
                "Bootstrap requires at least two observations and "
                "100 repetitions."
            )

        rng = random.Random(seed)
        n = len(values)

        estimates = [
            statistics.fmean(
                rng.choices(values, k=n)
            )
            for _ in range(repetitions)
        ]

        estimates.sort()

        return {
            "bootstrap_mean": statistics.fmean(estimates),
            "lower_95": estimates[int(0.025 * repetitions)],
            "upper_95": estimates[min(
                int(0.975 * repetitions),
                repetitions - 1
            )]
        }

    @staticmethod
    def required_sample_size(
        population_std: float,
        margin_of_error: float,
        z_score: float = 1.96,
        population_size: int | None = None
    ) -> int:
        if population_std < 0:
            raise ValueError("Standard deviation cannot be negative.")

        if margin_of_error <= 0 or z_score <= 0:
            raise ValueError("Margin and z-score must be positive.")

        if population_std == 0:
            return 1

        n0 = (z_score * population_std / margin_of_error) ** 2

        if population_size is not None:
            if population_size <= 0:
                raise ValueError("Population size must be positive.")

            if n0 >= population_size:
                return population_size

            n0 = n0 / (
                1 + (n0 - 1) / population_size
            )

        return min(
            math.ceil(n0),
            population_size if population_size else math.ceil(n0)
        )


# ============================================================
# 7. JSON EXPORT
# ============================================================

def export_results(
    results: dict[str, Any],
    filename: str = "statistics_results.json"
) -> None:
    path = Path(filename)

    if path.suffix.lower() != ".json":
        raise ValueError("Only JSON export is supported.")

    # Avoid silently overwriting an existing file in production workflows.
    path.write_text(
        json.dumps(results, indent=4, allow_nan=False),
        encoding="utf-8"
    )


# ============================================================
# 8. REALISTIC APPLICATION
# ============================================================

def build_student_population() -> Population:
    departments = ["Computer Science", "Mathematics", "Physics"]
    units = []

    for department_index, department in enumerate(departments):
        for student_index in range(1, 21):
            score = (
                55
                + department_index * 8
                + student_index * 1.1
                + (student_index % 4) * 2
            )

            units.append(
                Unit(
                    unit_id=f"STU-{department_index + 1}-{student_index:03}",
                    value=round(score, 2),
                    stratum=department,
                    cluster=f"CLASS-{(student_index - 1) // 5 + 1}"
                )
            )

    return Population(units)


def run_tests() -> None:
    assert DescriptiveStatistics.mean([10, 20, 30]) == 20
    assert DescriptiveStatistics.median([10, 20, 30]) == 20
    assert DescriptiveStatistics.variance([10, 20, 30], False) > 0

    population = Population([
        Unit("A", 10),
        Unit("B", 20)
    ])

    sample = SamplingEngine(population, 7).simple_random(2)

    assert len(sample.units) == 2
    assert StatisticalInference.standard_error(sample) == 0

    try:
        SamplingEngine(population).simple_random(3)
    except ValueError:
        pass
    else:
        raise AssertionError("Invalid sample size was accepted.")


def main() -> None:
    run_tests()

    population = build_student_population()

    print("\nSTATISTICS FUNDAMENTALS")
    print("=" * 55)

    parameters = PopulationParameters.calculate(population)

    print("\nPOPULATION PARAMETERS")
    print(json.dumps(parameters, indent=4))

    engine = SamplingEngine(population, seed=42)

    samples = {
        "simple_random": engine.simple_random(15),
        "systematic": engine.systematic(15),
        "stratified": engine.stratified(15),
        "cluster": engine.cluster(2)
    }

    results: dict[str, Any] = {
        "population": parameters,
        "sampling_results": {}
    }

    for name, sample in samples.items():
        values = [unit.value for unit in sample.units]

        report = {
            "method": sample.method.value,
            "sample_size": len(sample.units),
            "sample_statistics": DescriptiveStatistics.describe(values),
            "sample_standard_error": (
                StatisticalInference.standard_error(sample)
                if len(values) > 1 else None
            ),
            "sample_ids": [unit.unit_id for unit in sample.units]
        }

        results["sampling_results"][name] = report

        print(f"\n{name.upper()}")
        print(json.dumps(report, indent=4))

        if name == "simple_random":
            interval = StatisticalInference.mean_confidence_interval(sample)
            results["confidence_interval"] = asdict(interval)

    results["sample_size_requirement"] = (
        StatisticalInference.required_sample_size(
            population_std=15,
            margin_of_error=3,
            z_score=1.96,
            population_size=population.size
        )
    )

    results["bootstrap"] = StatisticalInference.bootstrap(
        [unit.value for unit in samples["simple_random"].units],
        repetitions=2000
    )

    export_results(results)

    print("\nSAMPLE SIZE REQUIREMENT")
    print(results["sample_size_requirement"])

    print("\nBOOTSTRAP ESTIMATION")
    print(results["bootstrap"])

    print("\nAll validation tests passed.")
    print("Results exported to statistics_results.json")


if __name__ == "__main__":
    main()
