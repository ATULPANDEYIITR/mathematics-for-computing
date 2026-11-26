#!/usr/bin/env python3
"""
Information-Theoretic Measures
Mutual Information, Conditional Entropy, and Information Gain.

Implements categorical probability distributions, Shannon entropy,
conditional entropy, mutual information, information gain, feature
ranking, and a decision-tree split evaluator.

Python 3.10+
Standard library only.
"""

from __future__ import annotations

import math
import json
import logging
from collections import Counter, defaultdict
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Hashable, Iterable, Optional, Sequence


logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s"
)

logger = logging.getLogger("information_theory")

EPSILON = 1e-12


class InformationTheoryError(Exception):
    """Base exception for information-theoretic operations."""


class InvalidDistributionError(InformationTheoryError):
    """Raised when probability distributions are invalid."""


class InvalidDatasetError(InformationTheoryError):
    """Raised when dataset dimensions or values are invalid."""


class InformationMeasure(str, Enum):
    ENTROPY = "entropy"
    CONDITIONAL_ENTROPY = "conditional_entropy"
    MUTUAL_INFORMATION = "mutual_information"
    INFORMATION_GAIN = "information_gain"


@dataclass(frozen=True)
class ProbabilityDistribution:
    probabilities: dict[Hashable, float]

    def __post_init__(self):
        if not self.probabilities:
            raise InvalidDistributionError(
                "Probability distribution cannot be empty."
            )

        for value, probability in self.probabilities.items():
            if not isinstance(probability, (int, float)):
                raise InvalidDistributionError(
                    f"Invalid probability for {value!r}."
                )

            if not math.isfinite(probability) or probability < 0:
                raise InvalidDistributionError(
                    f"Probability must be finite and non-negative: {value!r}"
                )

        total = sum(self.probabilities.values())

        if not math.isclose(total, 1.0, abs_tol=EPSILON):
            raise InvalidDistributionError(
                f"Probabilities must sum to 1. Received {total}."
            )

    @classmethod
    def from_counts(
        cls,
        counts: dict[Hashable, int]
    ) -> ProbabilityDistribution:

        if not counts:
            raise InvalidDistributionError("Counts cannot be empty.")

        if any(
            not isinstance(value, int) or value < 0
            for value in counts.values()
        ):
            raise InvalidDistributionError(
                "Counts must be non-negative integers."
            )

        total = sum(counts.values())

        if total == 0:
            raise InvalidDistributionError(
                "Total observation count must be positive."
            )

        return cls({
            key: count / total
            for key, count in counts.items()
        })


def entropy(
    values: Iterable[Hashable],
    base: float = 2.0
) -> float:
    """
    Calculate Shannon entropy.

    H(X) = -sum(p(x) * log2(p(x)))

    Returns entropy in bits by default.
    """

    if not math.isfinite(base) or base <= 0 or math.isclose(base, 1.0):
        raise ValueError("Logarithm base must be positive and different from 1.")

    observations = list(values)

    if not observations:
        raise InvalidDatasetError(
            "Entropy requires at least one observation."
        )

    counts = Counter(observations)
    distribution = ProbabilityDistribution.from_counts(dict(counts))

    return -sum(
        probability * math.log(probability, base)
        for probability in distribution.probabilities.values()
        if probability > 0
    )


def entropy_from_counts(
    counts: dict[Hashable, int],
    base: float = 2.0
) -> float:

    distribution = ProbabilityDistribution.from_counts(counts)

    if not math.isfinite(base) or base <= 0 or math.isclose(base, 1.0):
        raise ValueError("Invalid logarithm base.")

    return -sum(
        p * math.log(p, base)
        for p in distribution.probabilities.values()
        if p > 0
    )


def conditional_entropy(
    target: Sequence[Hashable],
    condition: Sequence[Hashable],
    base: float = 2.0
) -> float:
    """
    Calculate H(Y|X).

    H(Y|X) = sum_x P(x) H(Y|X=x)
    """

    validate_columns(target, condition)

    total = len(target)
    groups = defaultdict(list)

    for x, y in zip(condition, target):
        groups[x].append(y)

    result = 0.0

    for group in groups.values():
        weight = len(group) / total
        result += weight * entropy(group, base)

    return result


def mutual_information(
    first: Sequence[Hashable],
    second: Sequence[Hashable],
    base: float = 2.0
) -> float:
    """
    Calculate I(X;Y).

    I(X;Y) = H(Y) - H(Y|X)

    Equivalent to H(X) + H(Y) - H(X,Y).
    """

    validate_columns(first, second)

    result = entropy(second, base) - conditional_entropy(
        second, first, base
    )

    # Remove insignificant floating-point errors.
    return max(0.0, result)


def joint_entropy(
    first: Sequence[Hashable],
    second: Sequence[Hashable],
    base: float = 2.0
) -> float:

    validate_columns(first, second)

    return entropy(
        list(zip(first, second)),
        base
    )


def conditional_mutual_information(
    x: Sequence[Hashable],
    y: Sequence[Hashable],
    z: Sequence[Hashable],
    base: float = 2.0
) -> float:
    """
    Calculate I(X;Y|Z).

    I(X;Y|Z) = H(Y|Z) - H(Y|X,Z)
    """

    validate_columns(x, y)
    validate_columns(x, z)

    if len(x) != len(y) or len(x) != len(z):
        raise InvalidDatasetError("All columns must have equal lengths.")

    yz = list(zip(y, z))
    xz = list(zip(x, z))

    return max(
        0.0,
        conditional_entropy(y, z, base)
        - conditional_entropy(yz, xz, base)
    )


def information_gain(
    target: Sequence[Hashable],
    feature: Sequence[Hashable],
    base: float = 2.0
) -> float:
    """
    Calculate information gain for splitting on a feature.

    IG(Y,X) = H(Y) - H(Y|X)
    """

    validate_columns(target, feature)

    return mutual_information(target, feature, base)


def normalized_mutual_information(
    first: Sequence[Hashable],
    second: Sequence[Hashable]
) -> float:
    """
    Calculate symmetric normalized mutual information.

    NMI = 2 * I(X;Y) / (H(X) + H(Y))
    """

    validate_columns(first, second)

    hx = entropy(first)
    hy = entropy(second)

    denominator = hx + hy

    if denominator <= EPSILON:
        return 1.0 if list(first) == list(second) else 0.0

    return 2.0 * mutual_information(first, second) / denominator


def validate_columns(
    first: Sequence[Any],
    second: Sequence[Any]
) -> None:

    if len(first) != len(second):
        raise InvalidDatasetError(
            "Columns must contain the same number of observations."
        )

    if len(first) == 0:
        raise InvalidDatasetError(
            "Columns cannot be empty."
        )

    try:
        for value in list(first) + list(second):
            hash(value)
    except TypeError as exc:
        raise InvalidDatasetError(
            "Observations must contain hashable values."
        ) from exc


@dataclass
class FeatureResult:
    feature_name: str
    entropy: float
    conditional_entropy: float
    mutual_information: float
    information_gain: float
    normalized_mutual_information: float


class InformationAnalyzer:
    """
    Analyzes categorical datasets and ranks features
    according to their information gain.
    """

    def __init__(
        self,
        features: dict[str, Sequence[Hashable]],
        target: Sequence[Hashable]
    ):

        if not features:
            raise InvalidDatasetError("At least one feature is required.")

        self.features = {
            name: list(values)
            for name, values in features.items()
        }

        self.target = list(target)

        for name, values in self.features.items():
            validate_columns(
                self.target,
                values
            )

    def analyze_feature(
        self,
        feature_name: str
    ) -> FeatureResult:

        if feature_name not in self.features:
            raise KeyError(f"Unknown feature: {feature_name}")

        feature = self.features[feature_name]

        hy = entropy(self.target)
        h_y_given_x = conditional_entropy(
            self.target,
            feature
        )

        mi = mutual_information(
            feature,
            self.target
        )

        return FeatureResult(
            feature_name=feature_name,
            entropy=hy,
            conditional_entropy=h_y_given_x,
            mutual_information=mi,
            information_gain=max(0.0, hy - h_y_given_x),
            normalized_mutual_information=normalized_mutual_information(
                feature,
                self.target
            )
        )

    def rank_features(self) -> list[FeatureResult]:

        results = [
            self.analyze_feature(name)
            for name in self.features
        ]

        return sorted(
            results,
            key=lambda result: (
                -result.information_gain,
                result.feature_name
            )
        )

    def select_features(
        self,
        minimum_gain: float = 0.0
    ) -> list[str]:

        if minimum_gain < 0:
            raise ValueError("Minimum gain cannot be negative.")

        return [
            result.feature_name
            for result in self.rank_features()
            if result.information_gain >= minimum_gain
        ]


def print_analysis(
    analyzer: InformationAnalyzer
) -> None:

    results = analyzer.rank_features()

    print("\nINFORMATION-THEORETIC FEATURE ANALYSIS")
    print("=" * 100)

    print(
        f"{'Feature':<20}"
        f"{'H(Y)':>12}"
        f"{'H(Y|X)':>15}"
        f"{'MI':>15}"
        f"{'IG':>15}"
        f"{'NMI':>15}"
    )

    print("-" * 100)

    for result in results:
        print(
            f"{result.feature_name:<20}"
            f"{result.entropy:>12.5f}"
            f"{result.conditional_entropy:>15.5f}"
            f"{result.mutual_information:>15.5f}"
            f"{result.information_gain:>15.5f}"
            f"{result.normalized_mutual_information:>15.5f}"
        )


def export_results(
    analyzer: InformationAnalyzer,
    filename: str
) -> None:

    results = [
        result.__dict__
        for result in analyzer.rank_features()
    ]

    output = {
        "target_entropy": entropy(analyzer.target),
        "observations": len(analyzer.target),
        "feature_results": results
    }

    path = Path(filename)

    # Refuse accidental output to an existing directory.
    if path.exists() and path.is_dir():
        raise IsADirectoryError(str(path))

    path.write_text(
        json.dumps(output, indent=4),
        encoding="utf-8"
    )


def demonstrate_decision_tree_split() -> None:
    """
    Classic categorical classification example.

    The feature Outlook partitions observations into
    subsets and its information gain measures the
    reduction in target uncertainty.
    """

    target = [
        "No", "No", "Yes", "Yes", "Yes",
        "No", "Yes", "No", "Yes", "Yes",
        "Yes", "Yes", "Yes", "No"
    ]

    features = {
        "Outlook": [
            "Sunny", "Sunny", "Overcast", "Rain",
            "Rain", "Rain", "Overcast", "Sunny",
            "Sunny", "Rain", "Sunny", "Overcast",
            "Overcast", "Rain"
        ],
        "Temperature": [
            "Hot", "Hot", "Hot", "Mild",
            "Cool", "Cool", "Cool", "Mild",
            "Cool", "Mild", "Mild", "Mild",
            "Hot", "Mild"
        ],
        "Humidity": [
            "High", "High", "High", "High",
            "Normal", "Normal", "Normal", "High",
            "Normal", "Normal", "Normal", "High",
            "Normal", "High"
        ],
        "Wind": [
            "Weak", "Strong", "Weak", "Weak",
            "Weak", "Strong", "Strong", "Weak",
            "Weak", "Weak", "Strong", "Strong",
            "Weak", "Strong"
        ]
    }

    analyzer = InformationAnalyzer(features, target)
    print_analysis(analyzer)

    ranked = analyzer.rank_features()

    if ranked:
        best = ranked[0]

        print("\nBest initial decision-tree split:")
        print(f"Feature: {best.feature_name}")
        print(f"Information gain: {best.information_gain:.5f} bits")


def run_tests() -> None:
    """Validate mathematical identities and edge cases."""

    fair_coin = ["H", "T", "H", "T"]

    assert math.isclose(entropy(fair_coin), 1.0)

    constant = ["A", "A", "A", "A"]
    assert math.isclose(entropy(constant), 0.0)

    x = [0, 0, 1, 1]
    y = [0, 0, 1, 1]

    assert math.isclose(mutual_information(x, y), 1.0)
    assert math.isclose(information_gain(y, x), 1.0)
    assert math.isclose(normalized_mutual_information(x, y), 1.0)

    independent_x = [0, 0, 1, 1]
    independent_y = [0, 1, 0, 1]

    assert math.isclose(
        mutual_information(independent_x, independent_y),
        0.0,
        abs_tol=EPSILON
    )

    assert math.isclose(
        conditional_entropy(y, x),
        0.0,
        abs_tol=EPSILON
    )

    assert math.isclose(
        joint_entropy(x, y),
        1.0
    )

    try:
        entropy([])
        raise AssertionError("Empty entropy input should fail.")
    except InvalidDatasetError:
        pass

    try:
        ProbabilityDistribution({"A": 0.7, "B": 0.7})
        raise AssertionError("Invalid distribution should fail.")
    except InvalidDistributionError:
        pass

    try:
        mutual_information([1, 2], [1])
        raise AssertionError("Mismatched columns should fail.")
    except InvalidDatasetError:
        pass

    print("\nAll mathematical and validation tests passed.")


def main() -> None:

    run_tests()
    demonstrate_decision_tree_split()

    target = ["Approved", "Rejected", "Approved", "Rejected"]
    features = {
        "CreditScore": ["High", "Low", "High", "Low"],
        "Region": ["North", "South", "South", "North"]
    }

    analyzer = InformationAnalyzer(features, target)

    print("\nSelected features:")
    print(analyzer.select_features(minimum_gain=0.1))

    export_results(
        analyzer,
        "information_analysis.json"
    )

    logger.info("Analysis exported successfully.")


if __name__ == "__main__":
    main()
