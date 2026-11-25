"""
Entropy and Cross-Entropy in Mathematics for Computing

Implements:
1. Shannon entropy
2. Cross-entropy
3. Kullback-Leibler divergence
4. Binary entropy
5. Conditional entropy
6. Joint entropy
7. Mutual information
8. Numerical stability and probability smoothing
9. Distribution validation and comparison
10. Practical classification-loss simulation

All logarithms use base 2. Results are measured in bits.
"""

from dataclasses import dataclass
from typing import Sequence
import math
import json
from pathlib import Path


class ProbabilityError(ValueError):
    """Raised when a probability distribution is invalid."""


@dataclass(frozen=True)
class Distribution:
    name: str
    probabilities: tuple[float, ...]

    def __post_init__(self):
        if not self.name.strip():
            raise ProbabilityError("Distribution name cannot be empty.")

        if not self.probabilities:
            raise ProbabilityError("Distribution cannot be empty.")

        for probability in self.probabilities:
            if not math.isfinite(probability):
                raise ProbabilityError("Probabilities must be finite.")

            if probability < 0 or probability > 1:
                raise ProbabilityError(
                    "Each probability must belong to [0, 1]."
                )

        if not math.isclose(
            sum(self.probabilities), 1.0, abs_tol=1e-10
        ):
            raise ProbabilityError(
                "Probabilities must sum to 1."
            )

    @property
    def size(self) -> int:
        return len(self.probabilities)


def validate_compatible(
    p: Distribution,
    q: Distribution
) -> None:
    if p.size != q.size:
        raise ProbabilityError(
            "Distributions must have identical dimensions."
        )


def entropy(distribution: Distribution) -> float:
    """
    Shannon entropy:
    H(P) = -sum(p(x) * log2(p(x)))

    Zero-probability terms contribute zero.
    """
    return -sum(
        p * math.log2(p)
        for p in distribution.probabilities
        if p > 0
    )


def cross_entropy(
    actual: Distribution,
    predicted: Distribution
) -> float:
    """
    Cross-entropy:
    H(P, Q) = -sum(p(x) * log2(q(x)))

    Returns infinity if Q assigns zero probability
    to an event with positive probability under P.
    """
    validate_compatible(actual, predicted)

    result = 0.0

    for p, q in zip(
        actual.probabilities,
        predicted.probabilities
    ):
        if p == 0:
            continue

        if q == 0:
            return math.inf

        result -= p * math.log2(q)

    return result


def kl_divergence(
    actual: Distribution,
    predicted: Distribution
) -> float:
    """
    KL divergence:
    D_KL(P || Q) = sum(p(x) * log2(p(x) / q(x)))

    KL divergence is asymmetric and non-negative.
    """
    validate_compatible(actual, predicted)

    result = 0.0

    for p, q in zip(
        actual.probabilities,
        predicted.probabilities
    ):
        if p == 0:
            continue

        if q == 0:
            return math.inf

        result += p * math.log2(p / q)

    # Eliminate tiny negative floating-point errors.
    return max(0.0, result)


def binary_entropy(p: float) -> float:
    """Entropy of a Bernoulli random variable."""
    if not math.isfinite(p) or not 0 <= p <= 1:
        raise ProbabilityError("p must belong to [0, 1].")

    if p == 0 or p == 1:
        return 0.0

    return -p * math.log2(p) - (
        1 - p
    ) * math.log2(1 - p)


def smooth_distribution(
    distribution: Distribution,
    alpha: float = 0.01
) -> Distribution:
    """
    Additive/Laplace smoothing.

    q_i = (p_i + alpha) / (1 + n * alpha)

    Useful when a model assigns zero probability to
    an event that must remain representable.
    """
    if not math.isfinite(alpha) or alpha <= 0:
        raise ProbabilityError(
            "Smoothing alpha must be positive and finite."
        )

    n = distribution.size
    denominator = 1.0 + n * alpha

    smoothed = tuple(
        (p + alpha) / denominator
        for p in distribution.probabilities
    )

    return Distribution(
        name=f"{distribution.name}_smoothed",
        probabilities=smoothed
    )


def joint_entropy(
    joint: Sequence[Sequence[float]]
) -> float:
    """Calculate entropy from a joint probability matrix."""
    if not joint or not joint[0]:
        raise ProbabilityError("Joint matrix cannot be empty.")

    columns = len(joint[0])

    if any(len(row) != columns for row in joint):
        raise ProbabilityError("Joint matrix must be rectangular.")

    flattened = tuple(
        value for row in joint for value in row
    )

    distribution = Distribution(
        "joint",
        flattened
    )

    return entropy(distribution)


def marginal_x(
    joint: Sequence[Sequence[float]]
) -> Distribution:
    """Calculate the marginal distribution of X."""
    rows = len(joint)
    columns = len(joint[0])

    return Distribution(
        "marginal_x",
        tuple(
            sum(joint[i][j] for j in range(columns))
            for i in range(rows)
        )
    )


def marginal_y(
    joint: Sequence[Sequence[float]]
) -> Distribution:
    """Calculate the marginal distribution of Y."""
    columns = len(joint[0])

    return Distribution(
        "marginal_y",
        tuple(
            sum(row[j] for row in joint)
            for j in range(columns)
        )
    )


def conditional_entropy_y_given_x(
    joint: Sequence[Sequence[float]]
) -> float:
    """
    H(Y|X) = H(X,Y) - H(X)
    """
    hx_y = joint_entropy(joint)
    hx = entropy(marginal_x(joint))

    return max(0.0, hx_y - hx)


def mutual_information(
    joint: Sequence[Sequence[float]]
) -> float:
    """
    I(X;Y) = H(X) + H(Y) - H(X,Y)
    """
    hx = entropy(marginal_x(joint))
    hy = entropy(marginal_y(joint))
    hxy = joint_entropy(joint)

    return max(0.0, hx + hy - hxy)


def classification_loss(
    actual_class: int,
    predicted_probabilities: Sequence[float]
) -> float:
    """
    Negative log-likelihood for one classification example.
    """
    if not 0 <= actual_class < len(predicted_probabilities):
        raise ProbabilityError("Invalid actual class index.")

    if not predicted_probabilities:
        raise ProbabilityError("Predictions cannot be empty.")

    predicted = Distribution(
        "prediction",
        tuple(predicted_probabilities)
    )

    probability = predicted.probabilities[actual_class]

    if probability == 0:
        return math.inf

    return -math.log2(probability)


def report_distribution(
    actual: Distribution,
    predicted: Distribution
) -> dict:
    validate_compatible(actual, predicted)

    h = entropy(actual)
    ce = cross_entropy(actual, predicted)
    kl = kl_divergence(actual, predicted)

    return {
        "actual_distribution": actual.name,
        "predicted_distribution": predicted.name,
        "entropy_bits": h,
        "cross_entropy_bits": ce,
        "kl_divergence_bits": kl,
        "identity_verified": (
            math.isclose(
                ce,
                h + kl,
                rel_tol=1e-9,
                abs_tol=1e-9
            )
                if math.isfinite(ce) and math.isfinite(kl)
                else False
        )
    }


def run_tests():
    p = Distribution("actual", (0.5, 0.3, 0.2))
    q = Distribution("predicted", (0.4, 0.4, 0.2))

    assert math.isclose(
        entropy(Distribution("uniform", (0.5, 0.5))),
        1.0
    )

    assert math.isclose(binary_entropy(0), 0.0)
    assert math.isclose(binary_entropy(1), 0.0)

    assert math.isclose(
        kl_divergence(p, p),
        0.0,
        abs_tol=1e-10
    )

    assert kl_divergence(p, q) >= 0

    assert math.isclose(
        cross_entropy(p, q),
        entropy(p) + kl_divergence(p, q),
        rel_tol=1e-9
    )

    assert math.isinf(
        cross_entropy(
            Distribution("p", (1.0, 0.0)),
            Distribution("q", (0.0, 1.0))
        )
    )

    joint = [
        [0.4, 0.1],
        [0.1, 0.4]
    ]

    assert mutual_information(joint) > 0

    assert math.isclose(
        conditional_entropy_y_given_x(joint),
        conditional_entropy_y_given_x(joint)
    )

    smoothed = smooth_distribution(
        Distribution("sparse", (1.0, 0.0))
    )

    assert all(x > 0 for x in smoothed.probabilities)
    assert math.isclose(sum(smoothed.probabilities), 1.0)

    try:
        Distribution("invalid", (0.7, 0.7))
        raise AssertionError("Invalid distribution was accepted.")
    except ProbabilityError:
        pass

    print("All tests passed.")


def main():
    actual = Distribution(
        "observed_class_distribution",
        (0.50, 0.30, 0.20)
    )

    predicted = Distribution(
        "model_probability_distribution",
        (0.40, 0.40, 0.20)
    )

    print("=" * 65)
    print("ENTROPY AND CROSS-ENTROPY ANALYSIS")
    print("=" * 65)

    results = report_distribution(actual, predicted)

    for key, value in results.items():
        print(f"{key:30}: {value}")

    print("\nBinary entropy examples:")

    for probability in (0.0, 0.1, 0.25, 0.5, 0.75, 1.0):
        print(
            f"P(X=1)={probability:.2f}, "
            f"H(X)={binary_entropy(probability):.6f} bits"
        )

    print("\nJoint probability analysis:")

    joint = [
        [0.4, 0.1],
        [0.1, 0.4]
    ]

    print(f"H(X,Y): {joint_entropy(joint):.6f} bits")
    print(f"H(X): {entropy(marginal_x(joint)):.6f} bits")
    print(f"H(Y): {entropy(marginal_y(joint)):.6f} bits")
    print(
        "H(Y|X): "
        f"{conditional_entropy_y_given_x(joint):.6f} bits"
    )
    print(
        "I(X;Y): "
        f"{mutual_information(joint):.6f} bits"
    )

    print("\nClassification example:")

    loss = classification_loss(
        actual_class=1,
        predicted_probabilities=(0.15, 0.70, 0.15)
    )

    print(f"Negative log-likelihood: {loss:.6f} bits")

    print("\nSmoothing example:")

    sparse = Distribution("sparse", (1.0, 0.0, 0.0))
    smoothed = smooth_distribution(sparse, alpha=0.1)

    print("Original:", sparse.probabilities)
    print("Smoothed:", smoothed.probabilities)

    run_tests()

    # Save reproducible numerical results.
    output = {
        "analysis": results,
        "joint_entropy": joint_entropy(joint),
        "mutual_information": mutual_information(joint),
        "classification_loss_bits": loss
    }

    output_path = Path("entropy_analysis.json")

    output_path.write_text(
        json.dumps(output, indent=4),
        encoding="utf-8"
    )

    print(f"\nResults saved to {output_path.resolve()}")


if __name__ == "__main__":
    main()
