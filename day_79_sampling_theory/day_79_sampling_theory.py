#!/usr/bin/env python3
"""
Sampling Theory: Random Sampling, Stratified Sampling, Sampling Bias,
and Sample Size Determination.

Python 3.10+
Standard-library implementation.
"""

from __future__ import annotations

import math
import random
import statistics
from collections import Counter, defaultdict
from dataclasses import dataclass
from enum import Enum
from typing import Callable, Generic, Sequence, TypeVar


T = TypeVar("T")


class SamplingError(Exception):
    """Base exception for sampling operations."""


class InvalidPopulationError(SamplingError):
    pass


class InvalidSampleSizeError(SamplingError):
    pass


class SamplingMethod(Enum):
    SIMPLE_RANDOM = "simple_random"
    STRATIFIED = "stratified"
    SYSTEMATIC = "systematic"


@dataclass(frozen=True)
class Person:
    person_id: int
    department: str
    age: int
    income: float
    response: float

    def __post_init__(self):
        if self.person_id <= 0:
            raise ValueError("Person ID must be positive.")
        if not 18 <= self.age <= 100:
            raise ValueError("Age must be between 18 and 100.")
        if self.income < 0 or not math.isfinite(self.income):
            raise ValueError("Income must be finite and non-negative.")
        if not math.isfinite(self.response):
            raise ValueError("Response must be finite.")


@dataclass(frozen=True)
class SamplingResult(Generic[T]):
    method: SamplingMethod
    selected: tuple[T, ...]
    population_size: int
    sample_size: int
    seed: int | None

    @property
    def sampling_fraction(self) -> float:
        return self.sample_size / self.population_size


@dataclass(frozen=True)
class Estimate:
    mean: float
    standard_error: float
    confidence_margin: float
    confidence_level: float
    lower_bound: float
    upper_bound: float


class SamplingTheory:
    """Sampling algorithms and statistical estimation."""

    @staticmethod
    def validate_population(population: Sequence[T]) -> None:
        if not population:
            raise InvalidPopulationError("Population cannot be empty.")

        if len(population) != len(set(id(x) for x in population)):
            raise InvalidPopulationError(
                "Population contains repeated object references."
            )

    @staticmethod
    def validate_sample_size(n: int, N: int) -> None:
        if not isinstance(n, int) or isinstance(n, bool):
            raise InvalidSampleSizeError("Sample size must be an integer.")

        if n <= 0 or n > N:
            raise InvalidSampleSizeError(
                f"Sample size must be between 1 and {N}."
            )

    @staticmethod
    def simple_random(
        population: Sequence[T],
        n: int,
        seed: int | None = 42
    ) -> SamplingResult[T]:
        """Simple random sampling without replacement."""

        SamplingTheory.validate_population(population)
        SamplingTheory.validate_sample_size(n, len(population))

        rng = random.Random(seed)
        selected = rng.sample(list(population), n)

        return SamplingResult(
            SamplingMethod.SIMPLE_RANDOM,
            tuple(selected),
            len(population),
            n,
            seed
        )

    @staticmethod
    def stratified(
        population: Sequence[T],
        n: int,
        stratum: Callable[[T], str],
        seed: int | None = 42,
        allocation: str = "proportional"
    ) -> SamplingResult[T]:
        """
        Stratified sampling.

        Proportional allocation:
            n_h = n * N_h / N

        Integer allocations use largest-remainder rounding.
        Every non-empty stratum receives at least one observation
        when the requested sample size permits it.
        """

        SamplingTheory.validate_population(population)
        N = len(population)
        SamplingTheory.validate_sample_size(n, N)

        if allocation not in {"proportional", "equal"}:
            raise ValueError("Allocation must be proportional or equal.")

        groups: dict[str, list[T]] = defaultdict(list)

        for item in population:
            key = stratum(item)
            if not key:
                raise ValueError("Stratum identifiers cannot be empty.")
            groups[key].append(item)

        strata = sorted(groups.items())
        H = len(strata)

        if n < H:
            raise InvalidSampleSizeError(
                "Sample size must cover every non-empty stratum."
            )

        sizes = [len(items) for _, items in strata]

        if allocation == "equal":
            weights = [1.0] * H
        else:
            weights = [size / N for size in sizes]

        raw = [n * weight / sum(weights) for weight in weights]
        allocated = [math.floor(value) for value in raw]

        # Guarantee representation of each non-empty stratum.
        for i in range(H):
            if allocated[i] == 0:
                allocated[i] = 1

        # Remove excess allocation from strata with the least
        # favorable fractional remainder, without removing the last item.
        while sum(allocated) > n:
            candidates = [
                i for i in range(H) if allocated[i] > 1
            ]
            if not candidates:
                raise InvalidSampleSizeError("Cannot satisfy allocation.")
            index = min(
                candidates,
                key=lambda i: raw[i] - math.floor(raw[i])
            )
            allocated[index] -= 1

        remainders = [
            raw[i] - math.floor(raw[i]) for i in range(H)
        ]

        while sum(allocated) < n:
            candidates = [
                i for i in range(H)
                if allocated[i] < sizes[i]
            ]
            if not candidates:
                raise InvalidSampleSizeError("Allocation exceeds capacity.")

            index = max(
                candidates,
                key=lambda i: (
                    remainders[i],
                    sizes[i] - allocated[i]
                )
            )
            allocated[index] += 1
            remainders[index] = -1.0

        rng = random.Random(seed)
        selected: list[T] = []

        for (name, members), count in zip(strata, allocated):
            selected.extend(rng.sample(members, count))

        rng.shuffle(selected)

        return SamplingResult(
            SamplingMethod.STRATIFIED,
            tuple(selected),
            N,
            n,
            seed
        )

    @staticmethod
    def systematic(
        population: Sequence[T],
        n: int,
        seed: int | None = 42
    ) -> SamplingResult[T]:
        """
        Systematic sampling using a randomized start.

        A random phase is used with evenly spaced positions.
        The method requires an ordered population.
        """

        SamplingTheory.validate_population(population)
        N = len(population)
        SamplingTheory.validate_sample_size(n, N)

        rng = random.Random(seed)
        interval = N / n
        start = rng.random() * interval

        indices = [
            min(N - 1, int(start + i * interval))
            for i in range(n)
        ]

        if len(set(indices)) != n:
            raise SamplingError("Systematic selection produced duplicates.")

        return SamplingResult(
            SamplingMethod.SYSTEMATIC,
            tuple(population[i] for i in indices),
            N,
            n,
            seed
        )

    @staticmethod
    def sample_mean(values: Sequence[float]) -> float:
        if not values:
            raise ValueError("Cannot calculate a mean from an empty sample.")
        return statistics.fmean(values)

    @staticmethod
    def standard_error(
        values: Sequence[float],
        population_size: int | None = None
    ) -> float:
        """
        Standard error of the mean with optional finite population
        correction for sampling without replacement.
        """

        n = len(values)

        if n < 2:
            raise ValueError("At least two observations are required.")

        if population_size is not None:
            if population_size < n:
                raise ValueError("Population size cannot be smaller than n.")
            if population_size <= 0:
                raise ValueError("Population size must be positive.")

        sample_sd = statistics.stdev(values)
        se = sample_sd / math.sqrt(n)

        if population_size is not None:
            fpc = math.sqrt((population_size - n) / (population_size - 1))
            se *= fpc

        return se

    @staticmethod
    def confidence_interval(
        values: Sequence[float],
        confidence_level: float = 0.95,
        population_size: int | None = None
    ) -> Estimate:
        """
        Approximate normal confidence interval.

        Uses the normal critical value for common confidence levels.
        For small samples, a Student-t critical value should be used
        in formal inference.
        """

        if not 0 < confidence_level < 1:
            raise ValueError("Confidence level must be between 0 and 1.")

        critical_values = {
            0.90: 1.645,
            0.95: 1.960,
            0.99: 2.576
        }

        key = min(
            critical_values,
            key=lambda x: abs(x - confidence_level)
        )

        if abs(key - confidence_level) > 0.0001:
            raise ValueError(
                "Supported confidence levels are 0.90, 0.95 and 0.99."
            )

        mean = SamplingTheory.sample_mean(values)
        se = SamplingTheory.standard_error(values, population_size)
        margin = critical_values[key] * se

        return Estimate(
            mean,
            se,
            margin,
            confidence_level,
            mean - margin,
            mean + margin
        )


class SampleSizeCalculator:
    """Sample size calculations for proportions and means."""

    @staticmethod
    def proportion_sample_size(
        confidence_z: float = 1.96,
        margin_of_error: float = 0.05,
        expected_proportion: float = 0.5,
        population_size: int | None = None
    ) -> int:
        """
        Cochran formula:

        n0 = Z² * p * (1-p) / e²

        Finite population correction:

        n = n0 / (1 + (n0 - 1)/N)
        """

        if confidence_z <= 0:
            raise ValueError("Z value must be positive.")

        if not 0 < margin_of_error < 1:
            raise ValueError("Margin of error must be between 0 and 1.")

        if not 0 < expected_proportion < 1:
            raise ValueError("Expected proportion must be between 0 and 1.")

        n0 = (
            confidence_z ** 2
            * expected_proportion
            * (1 - expected_proportion)
            / margin_of_error ** 2
        )

        if population_size is None:
            return math.ceil(n0)

        if population_size <= 0:
            raise ValueError("Population size must be positive.")

        if population_size <= 1:
            return population_size

        adjusted = n0 / (
            1 + (n0 - 1) / population_size
        )

        return min(population_size, math.ceil(adjusted))

    @staticmethod
    def mean_sample_size(
        confidence_z: float,
        population_sd: float,
        margin_of_error: float,
        population_size: int | None = None
    ) -> int:
        if confidence_z <= 0 or population_sd <= 0:
            raise ValueError("Z and standard deviation must be positive.")

        if margin_of_error <= 0:
            raise ValueError("Margin of error must be positive.")

        n0 = (
            confidence_z * population_sd / margin_of_error
        ) ** 2

        if population_size is None:
            return math.ceil(n0)

        if population_size <= 0:
            raise ValueError("Population size must be positive.")

        if population_size <= 1:
            return population_size

        adjusted = n0 / (1 + (n0 - 1) / population_size)

        return min(population_size, math.ceil(adjusted))

    @staticmethod
    def adjust_for_nonresponse(
        required_sample: int,
        expected_response_rate: float
    ) -> int:
        if required_sample <= 0:
            raise ValueError("Required sample must be positive.")

        if not 0 < expected_response_rate <= 1:
            raise ValueError("Response rate must be in (0, 1].")

        return math.ceil(required_sample / expected_response_rate)


class BiasDiagnostics:
    """Descriptive diagnostics for sampling representation."""

    @staticmethod
    def distribution(
        items: Sequence[T],
        key: Callable[[T], str]
    ) -> dict[str, float]:
        if not items:
            raise ValueError("Items cannot be empty.")

        counts = Counter(key(item) for item in items)
        total = len(items)

        return {
            group: count / total
            for group, count in sorted(counts.items())
        }

    @staticmethod
    def representation_gap(
        population: Sequence[T],
        sample: Sequence[T],
        key: Callable[[T], str]
    ) -> dict[str, float]:
        pop = BiasDiagnostics.distribution(population, key)
        sampled = BiasDiagnostics.distribution(sample, key)

        groups = set(pop) | set(sampled)

        return {
            group: sampled.get(group, 0.0) - pop.get(group, 0.0)
            for group in sorted(groups)
        }

    @staticmethod
    def weighted_mean(
        stratum_means: dict[str, float],
        population_weights: dict[str, float]
    ) -> float:
        if set(stratum_means) != set(population_weights):
            raise ValueError("Every stratum needs a corresponding weight.")

        if not math.isclose(sum(population_weights.values()), 1.0):
            raise ValueError("Population weights must sum to 1.")

        return sum(
            stratum_means[group] * population_weights[group]
            for group in stratum_means
        )


def build_population(size: int = 1000) -> list[Person]:
    """Create a reproducible synthetic employee population."""

    if size < 10:
        raise ValueError("Population must contain at least 10 people.")

    rng = random.Random(2026)
    departments = ["Engineering", "Finance", "Operations", "Research"]
    probabilities = [0.40, 0.20, 0.25, 0.15]

    population = []

    for person_id in range(1, size + 1):
        department = rng.choices(
            departments,
            weights=probabilities,
            k=1
        )[0]

        age = rng.randint(21, 65)
        income = round(rng.uniform(25000, 180000), 2)

        # A synthetic outcome with department and age effects.
        department_effect = {
            "Engineering": 8,
            "Finance": 5,
            "Operations": 2,
            "Research": 10
        }[department]

        response = (
            35
            + department_effect
            + 0.35 * age
            + rng.gauss(0, 12)
        )

        population.append(
            Person(
                person_id,
                department,
                age,
                income,
                response
            )
        )

    return population


def demonstrate() -> None:
    population = build_population(1000)

    print("=" * 68)
    print("SAMPLING THEORY LABORATORY")
    print("=" * 68)

    print(f"Population size: {len(population)}")

    required = SampleSizeCalculator.proportion_sample_size(
        confidence_z=1.96,
        margin_of_error=0.05,
        expected_proportion=0.5,
        population_size=len(population)
    )

    adjusted = SampleSizeCalculator.adjust_for_nonresponse(
        required,
        expected_response_rate=0.85
    )

    print(f"Required sample with finite population correction: {required}")
    print(f"Recruitment target at 85% response: {adjusted}")

    random_sample = SamplingTheory.simple_random(
        population, 100, seed=17
    )

    stratified_sample = SamplingTheory.stratified(
        population,
        100,
        lambda person: person.department,
        seed=17,
        allocation="proportional"
    )

    systematic_sample = SamplingTheory.systematic(
        population, 100, seed=17
    )

    samples = [
        random_sample,
        stratified_sample,
        systematic_sample
    ]

    for result in samples:
        values = [person.response for person in result.selected]

        estimate = SamplingTheory.confidence_interval(
            values,
            0.95,
            result.population_size
        )

        print(f"\nMethod: {result.method.value}")
        print(f"Sample size: {result.sample_size}")
        print(f"Sampling fraction: {result.sampling_fraction:.3f}")
        print(f"Estimated mean: {estimate.mean:.2f}")
        print(f"Standard error: {estimate.standard_error:.2f}")
        print(
            f"95% approximate interval: "
            f"[{estimate.lower_bound:.2f}, {estimate.upper_bound:.2f}]"
        )

        gaps = BiasDiagnostics.representation_gap(
            population,
            result.selected,
            lambda person: person.department
        )

        print("Department representation gaps:")
        for department, gap in gaps.items():
            print(f"  {department:15s}: {gap:+.3f}")

    # Demonstrate correct population weighting.
    population_groups: dict[str, list[Person]] = defaultdict(list)
    sample_groups: dict[str, list[Person]] = defaultdict(list)

    for person in population:
        population_groups[person.department].append(person)

    for person in stratified_sample.selected:
        sample_groups[person.department].append(person)

    means = {
        group: statistics.fmean(p.response for p in members)
        for group, members in sample_groups.items()
    }

    weights = {
        group: len(members) / len(population)
        for group, members in population_groups.items()
    }

    weighted = BiasDiagnostics.weighted_mean(means, weights)
    print(f"\nStratified population-weighted estimate: {weighted:.2f}")

    # Edge-case validation.
    print("\nValidation checks:")

    try:
        SamplingTheory.simple_random(population, 0)
    except InvalidSampleSizeError as exc:
        print(f"Invalid sample size correctly rejected: {exc}")

    try:
        SampleSizeCalculator.proportion_sample_size(
            margin_of_error=0
        )
    except ValueError as exc:
        print(f"Invalid margin correctly rejected: {exc}")

    print("\nExecution completed successfully.")


if __name__ == "__main__":
    demonstrate()
