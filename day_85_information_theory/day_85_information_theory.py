#!/usr/bin/env python3
"""
Information Theory: Information, Entropy, Uncertainty and Self-Information.

Implements:
- Self-information and surprisal
- Shannon entropy
- Joint and conditional entropy
- Mutual information
- Cross-entropy and KL divergence
- Probability distribution validation
- Huffman coding
- Empirical entropy estimation
- Numerical stability and edge-case handling

Python 3.10+
Uses only the Python standard library.
"""

from __future__ import annotations

import heapq
import math
import random
from collections import Counter
from dataclasses import dataclass
from typing import Hashable, Iterable, Mapping, Sequence


class InformationTheoryError(ValueError):
    """Raised when an information-theoretic input is invalid."""


def validate_probability(probability: float) -> float:
    if isinstance(probability, bool) or not isinstance(probability, (int, float)):
        raise InformationTheoryError("Probability must be numeric.")

    probability = float(probability)

    if not math.isfinite(probability):
        raise InformationTheoryError("Probability must be finite.")

    if not 0.0 <= probability <= 1.0:
        raise InformationTheoryError("Probability must be between 0 and 1.")

    return probability


def validate_distribution(
    distribution: Mapping[Hashable, float],
    tolerance: float = 1e-9
) -> dict[Hashable, float]:
    if not isinstance(distribution, Mapping) or not distribution:
        raise InformationTheoryError("Distribution cannot be empty.")

    if tolerance <= 0 or not math.isfinite(tolerance):
        raise InformationTheoryError("Tolerance must be positive and finite.")

    result = {
        symbol: validate_probability(probability)
        for symbol, probability in distribution.items()
    }

    total = math.fsum(result.values())

    if abs(total - 1.0) > tolerance:
        raise InformationTheoryError(
            f"Probabilities must sum to 1. Current sum: {total}"
        )

    return result


def self_information(
    probability: float,
    base: float = 2.0
) -> float:
    """Calculate I(x) = -log_base(P(x))."""
    probability = validate_probability(probability)

    if not math.isfinite(base) or base <= 0 or base == 1:
        raise InformationTheoryError("Logarithm base must be positive and not 1.")

    if probability == 0:
        return math.inf

    return -math.log(probability, base)


def entropy(
    distribution: Mapping[Hashable, float],
    base: float = 2.0
) -> float:
    """Calculate Shannon entropy in the selected information unit."""
    probabilities = validate_distribution(distribution)

    if not math.isfinite(base) or base <= 0 or base == 1:
        raise InformationTheoryError("Invalid logarithm base.")

    return math.fsum(
        -p * math.log(p, base)
        for p in probabilities.values()
        if p > 0
    )


def maximum_entropy(number_of_outcomes: int, base: float = 2.0) -> float:
    if isinstance(number_of_outcomes, bool) or number_of_outcomes < 1:
        raise InformationTheoryError("Number of outcomes must be positive.")

    if not math.isfinite(base) or base <= 0 or base == 1:
        raise InformationTheoryError("Invalid logarithm base.")

    return math.log(number_of_outcomes, base)


def entropy_gap(distribution: Mapping[Hashable, float]) -> float:
    """Difference between maximum and actual entropy."""
    probabilities = validate_distribution(distribution)
    return maximum_entropy(len(probabilities)) - entropy(probabilities)


def normalized_entropy(
    distribution: Mapping[Hashable, float]
) -> float:
    probabilities = validate_distribution(distribution)

    if len(probabilities) == 1:
        return 0.0

    return entropy(probabilities) / maximum_entropy(len(probabilities))


def joint_entropy(
    joint_distribution: Mapping[tuple[Hashable, Hashable], float]
) -> float:
    return entropy(joint_distribution)


def marginal_distribution(
    joint_distribution: Mapping[tuple[Hashable, Hashable], float],
    axis: int
) -> dict[Hashable, float]:
    if axis not in (0, 1):
        raise InformationTheoryError("Axis must be 0 or 1.")

    joint = validate_distribution(joint_distribution)
    marginal: dict[Hashable, float] = {}

    for pair, probability in joint.items():
        if not isinstance(pair, tuple) or len(pair) != 2:
            raise InformationTheoryError("Joint outcomes must be pairs.")

        symbol = pair[axis]
        marginal[symbol] = marginal.get(symbol, 0.0) + probability

    return marginal


def conditional_entropy(
    joint_distribution: Mapping[tuple[Hashable, Hashable], float],
    given_axis: int = 1
) -> float:
    """
    Calculate H(X|Y) or H(Y|X).

    given_axis=1 means H(X|Y).
    given_axis=0 means H(Y|X).
    """
    joint = validate_distribution(joint_distribution)

    if given_axis not in (0, 1):
        raise InformationTheoryError("Axis must be 0 or 1.")

    conditioned = marginal_distribution(joint, given_axis)

    return math.fsum(
        probability * entropy(
            {
                pair[1 - given_axis]: value / probability
                for pair, value in joint.items()
                if pair[given_axis] == symbol
            }
        )
        for symbol, probability in conditioned.items()
        if probability > 0
    )


def mutual_information(
    joint_distribution: Mapping[tuple[Hashable, Hashable], float]
) -> float:
    """Calculate I(X;Y) = H(X) - H(X|Y)."""
    joint = validate_distribution(joint_distribution)

    hx = entropy(marginal_distribution(joint, 0))
    hy = entropy(marginal_distribution(joint, 1))
    hxy = entropy(joint)

    result = hx + hy - hxy

    # Remove small negative floating-point errors.
    return max(0.0, result)


def cross_entropy(
    actual: Mapping[Hashable, float],
    predicted: Mapping[Hashable, float],
    base: float = 2.0
) -> float:
    """Calculate H(P,Q) = -sum P(x) log Q(x)."""
    p = validate_distribution(actual)
    q = validate_distribution(predicted)

    if set(p) != set(q):
        raise InformationTheoryError(
            "Actual and predicted distributions must have identical outcomes."
        )

    if not math.isfinite(base) or base <= 0 or base == 1:
        raise InformationTheoryError("Invalid logarithm base.")

    result = 0.0

    for symbol, probability in p.items():
        if probability == 0:
            continue

        predicted_probability = q[symbol]

        if predicted_probability == 0:
            return math.inf

        result -= probability * math.log(predicted_probability, base)

    return result


def kl_divergence(
    actual: Mapping[Hashable, float],
    predicted: Mapping[Hashable, float],
    base: float = 2.0
) -> float:
    """Calculate D_KL(P||Q) = H(P,Q) - H(P)."""
    p = validate_distribution(actual)
    q = validate_distribution(predicted)

    if set(p) != set(q):
        raise InformationTheoryError("Outcome sets must match.")

    if not math.isfinite(base) or base <= 0 or base == 1:
        raise InformationTheoryError("Invalid logarithm base.")

    if any(probability > 0 and q[symbol] == 0
           for symbol, probability in p.items()):
        return math.inf

    result = math.fsum(
        probability * math.log(
            probability / q[symbol], base
        )
        for symbol, probability in p.items()
        if probability > 0
    )

    return max(0.0, result)


def empirical_distribution(
    observations: Iterable[Hashable]
) -> dict[Hashable, float]:
    counts = Counter(observations)
    total = sum(counts.values())

    if total == 0:
        raise InformationTheoryError("At least one observation is required.")

    return {
        symbol: count / total
        for symbol, count in counts.items()
    }


def add_laplace_smoothing(
    observations: Sequence[Hashable],
    possible_outcomes: Sequence[Hashable],
    alpha: float = 1.0
) -> dict[Hashable, float]:
    if not math.isfinite(alpha) or alpha <= 0:
        raise InformationTheoryError("Smoothing alpha must be positive.")

    if not possible_outcomes:
        raise InformationTheoryError("Outcome vocabulary cannot be empty.")

    if len(set(possible_outcomes)) != len(possible_outcomes):
        raise InformationTheoryError("Outcome vocabulary must be unique.")

    if any(item not in possible_outcomes for item in observations):
        raise InformationTheoryError("Observation outside vocabulary.")

    counts = Counter(observations)
    denominator = len(observations) + alpha * len(possible_outcomes)

    return {
        symbol: (counts[symbol] + alpha) / denominator
        for symbol in possible_outcomes
    }


@dataclass(order=True)
class HuffmanNode:
    weight: float
    order: int
    symbol: Hashable | None = None
    left: HuffmanNode | None = None
    right: HuffmanNode | None = None


def huffman_codes(
    distribution: Mapping[Hashable, float]
) -> dict[Hashable, str]:
    probabilities = validate_distribution(distribution)

    heap = []
    counter = 0

    for symbol, probability in probabilities.items():
        heapq.heappush(
            heap,
            HuffmanNode(probability, counter, symbol)
        )
        counter += 1

    if len(heap) == 1:
        return {heap[0].symbol: "0"}

    while len(heap) > 1:
        left = heapq.heappop(heap)
        right = heapq.heappop(heap)

        parent = HuffmanNode(
            left.weight + right.weight,
            counter,
            None,
            left,
            right
        )

        counter += 1
        heapq.heappush(heap, parent)

    codes = {}

    def traverse(node: HuffmanNode, prefix: str) -> None:
        if node.symbol is not None:
            codes[node.symbol] = prefix
            return

        if node.left is not None:
            traverse(node.left, prefix + "0")

        if node.right is not None:
            traverse(node.right, prefix + "1")

    traverse(heap[0], "")
    return codes


def expected_code_length(
    distribution: Mapping[Hashable, float],
    codes: Mapping[Hashable, str]
) -> float:
    probabilities = validate_distribution(distribution)

    if set(probabilities) != set(codes):
        raise InformationTheoryError("Code symbols must match outcomes.")

    if any(not isinstance(code, str) or not code or
           any(bit not in "01" for bit in code)
           for code in codes.values()):
        raise InformationTheoryError("Invalid binary code.")

    ordered = list(codes.values())

    for index, code in enumerate(ordered):
        if any(
            other.startswith(code)
            for other_index, other in enumerate(ordered)
            if index != other_index
        ):
            raise InformationTheoryError("Codes must be prefix-free.")

    return math.fsum(
        probabilities[symbol] * len(code)
        for symbol, code in codes.items()
    )


def conditional_mutual_information(
    distribution: Mapping[tuple[Hashable, Hashable, Hashable], float]
) -> float:
    """Calculate I(X;Y|Z) using H(X|Z) - H(X|Y,Z)."""
    joint = validate_distribution(distribution)

    def conditional_from_groups(
        group_positions: tuple[int, ...],
        target_position: int
    ) -> float:
        groups: dict[tuple, dict[Hashable, float]] = {}

        for outcome, probability in joint.items():
            if not isinstance(outcome, tuple) or len(outcome) != 3:
                raise InformationTheoryError("Outcomes must be triples.")

            group = tuple(outcome[i] for i in group_positions)
            target = outcome[target_position]

            groups.setdefault(group, {})
            groups[group][target] = (
                groups[group].get(target, 0.0) + probability
            )

        total = 0.0

        for group, values in groups.items():
            group_probability = math.fsum(values.values())
            conditional = {
                symbol: value / group_probability
                for symbol, value in values.items()
            }
            total += group_probability * entropy(conditional)

        return total

    hx_given_z = conditional_from_groups((2,), 0)
    hx_given_yz = conditional_from_groups((1, 2), 0)

    return max(0.0, hx_given_z - hx_given_yz)


def demonstrate() -> None:
    print("=" * 65)
    print("INFORMATION THEORY: PRACTICAL COMPUTATION")
    print("=" * 65)

    distribution = {
        "A": 0.50,
        "B": 0.25,
        "C": 0.125,
        "D": 0.125
    }

    print("\n1. SELF-INFORMATION")
    for symbol, probability in distribution.items():
        print(
            f"{symbol}: P={probability:.3f}, "
            f"I={self_information(probability):.3f} bits"
        )

    print("\n2. SHANNON ENTROPY")
    print(f"Entropy: {entropy(distribution):.4f} bits")
    print(f"Maximum entropy: {maximum_entropy(4):.4f} bits")
    print(f"Normalized entropy: {normalized_entropy(distribution):.4f}")

    print("\n3. UNCERTAINTY")
    print(f"Entropy gap: {entropy_gap(distribution):.4f} bits")

    actual = {
        "A": 0.50,
        "B": 0.30,
        "C": 0.20
    }

    predicted = {
        "A": 0.40,
        "B": 0.40,
        "C": 0.20
    }

    print("\n4. CROSS-ENTROPY AND KL DIVERGENCE")
    print(f"Cross-entropy: {cross_entropy(actual, predicted):.4f} bits")
    print(f"KL divergence: {kl_divergence(actual, predicted):.4f} bits")

    joint = {
        ("Sunny", "Hot"): 0.30,
        ("Sunny", "Cold"): 0.20,
        ("Rainy", "Hot"): 0.10,
        ("Rainy", "Cold"): 0.40
    }

    print("\n5. JOINT AND CONDITIONAL INFORMATION")
    print(f"H(X,Y): {joint_entropy(joint):.4f} bits")
    print(f"H(X): {entropy(marginal_distribution(joint, 0)):.4f} bits")
    print(f"H(Y): {entropy(marginal_distribution(joint, 1)):.4f} bits")
    print(f"H(X|Y): {conditional_entropy(joint, 1):.4f} bits")
    print(f"I(X;Y): {mutual_information(joint):.4f} bits")

    print("\n6. EMPIRICAL PROBABILITY ESTIMATION")
    observations = [
        "success", "success", "failure",
        "success", "failure", "success"
    ]

    empirical = empirical_distribution(observations)
    print("Observed distribution:", empirical)
    print(f"Empirical entropy: {entropy(empirical):.4f} bits")

    smoothed = add_laplace_smoothing(
        observations,
        ["success", "failure", "unknown"],
        alpha=1.0
    )
    print("Smoothed distribution:", smoothed)

    print("\n7. HUFFMAN ENCODING")
    codes = huffman_codes(distribution)

    for symbol, code in codes.items():
        print(f"{symbol}: {code}")

    average_length = expected_code_length(distribution, codes)

    print(f"Expected code length: {average_length:.4f} bits")
    print(f"Source entropy: {entropy(distribution):.4f} bits")

    print("\n8. EDGE CASES")
    print(f"Certain event information: {self_information(1):.4f} bits")
    print(f"Impossible event information: {self_information(0)}")
    print(f"Deterministic entropy: {entropy({'fixed': 1.0}):.4f} bits")

    try:
        entropy({"A": 0.6, "B": 0.6})
    except InformationTheoryError as error:
        print("Validation correctly rejected invalid input:", error)

    print("\n9. MATHEMATICAL INVARIANTS")
    assert abs(entropy(distribution) - 1.75) < 1e-9
    assert entropy(distribution) <= maximum_entropy(4)
    assert abs(kl_divergence(actual, actual)) < 1e-9
    assert mutual_information(joint) <= min(
        entropy(marginal_distribution(joint, 0)),
        entropy(marginal_distribution(joint, 1))
    ) + 1e-9

    assert average_length >= entropy(distribution) - 1e-9

    print("All mathematical assertions passed.")


if __name__ == "__main__":
    demonstrate()
