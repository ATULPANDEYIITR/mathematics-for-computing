#!/usr/bin/env python3
"""
Vector Operations: Addition, Scalar Multiplication, Dot Product and Norms.

A self-contained numerical implementation using Python's standard library.
Supports validation, immutable vector representations, numerical stability,
normalization, cosine similarity, distance calculations and JSON persistence.
"""

from __future__ import annotations

import json
import math
import sys
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Iterable, Sequence


class VectorError(Exception):
    """Base exception for vector operations."""


class DimensionMismatchError(VectorError):
    """Raised when vector dimensions are incompatible."""


class ZeroVectorError(VectorError):
    """Raised when normalization or cosine similarity is undefined."""


class VectorOperation(Enum):
    ADDITION = "addition"
    SCALAR_MULTIPLICATION = "scalar_multiplication"
    DOT_PRODUCT = "dot_product"
    L1_NORM = "l1_norm"
    L2_NORM = "l2_norm"
    L_INFINITY_NORM = "infinity_norm"


@dataclass(frozen=True)
class Vector:
    """Immutable mathematical vector with finite floating-point values."""

    values: tuple[float, ...]

    def __post_init__(self) -> None:
        if not self.values:
            raise VectorError("A vector must contain at least one element.")

        converted = tuple(float(value) for value in self.values)

        if not all(math.isfinite(value) for value in converted):
            raise VectorError("Vector elements must be finite numbers.")

        object.__setattr__(self, "values", converted)

    @classmethod
    def from_iterable(cls, values: Iterable[float]) -> Vector:
        return cls(tuple(values))

    @property
    def dimension(self) -> int:
        return len(self.values)

    def _check_dimension(self, other: Vector) -> None:
        if self.dimension != other.dimension:
            raise DimensionMismatchError(
                f"Dimension mismatch: {self.dimension} != {other.dimension}"
            )

    def add(self, other: Vector) -> Vector:
        """Element-wise vector addition: u + v."""
        self._check_dimension(other)
        return Vector(tuple(a + b for a, b in zip(
            self.values, other.values
        )))

    def subtract(self, other: Vector) -> Vector:
        """Element-wise subtraction: u - v."""
        self._check_dimension(other)
        return Vector(tuple(a - b for a, b in zip(
            self.values, other.values
        )))

    def scale(self, scalar: float) -> Vector:
        """Scalar multiplication: c * v."""
        scalar = float(scalar)

        if not math.isfinite(scalar):
            raise VectorError("Scalar must be finite.")

        return Vector(tuple(scalar * value for value in self.values))

    def dot(self, other: Vector) -> float:
        """Dot product using accurate floating-point summation."""
        self._check_dimension(other)

        result = math.fsum(
            a * b for a, b in zip(self.values, other.values)
        )

        if not math.isfinite(result):
            raise VectorError("Dot product overflowed.")

        return result

    def l1_norm(self) -> float:
        """Manhattan norm: sum of absolute component values."""
        return math.fsum(abs(value) for value in self.values)

    def l2_norm(self) -> float:
        """Euclidean norm using a numerically stable algorithm."""
        return math.hypot(*self.values)

    def infinity_norm(self) -> float:
        """Maximum absolute component value."""
        return max(abs(value) for value in self.values)

    def norm(self, order: int | float = 2) -> float:
        """Calculate an L-p norm for p >= 1, or infinity norm."""
        if order == math.inf:
            return self.infinity_norm()

        if not math.isfinite(order) or order < 1:
            raise VectorError("Norm order must be >= 1 or infinity.")

        if order == 1:
            return self.l1_norm()

        if order == 2:
            return self.l2_norm()

        maximum = self.infinity_norm()

        if maximum == 0:
            return 0.0

        result = maximum * math.fsum(
            (abs(value) / maximum) ** order
            for value in self.values
        ) ** (1.0 / order)

        if not math.isfinite(result):
            raise VectorError("Norm calculation overflowed.")

        return result

    def normalize(self) -> Vector:
        """Return a unit vector in the same direction."""
        magnitude = self.l2_norm()

        if magnitude == 0:
            raise ZeroVectorError("Cannot normalize a zero vector.")

        return self.scale(1.0 / magnitude)

    def cosine_similarity(self, other: Vector) -> float:
        """Calculate cosine similarity between two vectors."""
        self._check_dimension(other)

        left_norm = self.l2_norm()
        right_norm = other.l2_norm()

        if left_norm == 0 or right_norm == 0:
            raise ZeroVectorError(
                "Cosine similarity is undefined for zero vectors."
            )

        result = self.dot(other) / (left_norm * right_norm)

        # Floating-point rounding can produce tiny boundary violations.
        return max(-1.0, min(1.0, result))

    def distance(self, other: Vector) -> float:
        """Calculate Euclidean distance."""
        return self.subtract(other).l2_norm()

    def is_orthogonal(
        self, other: Vector, tolerance: float = 1e-10
    ) -> bool:
        """Determine whether two vectors are approximately orthogonal."""
        if tolerance < 0 or not math.isfinite(tolerance):
            raise VectorError("Tolerance must be finite and non-negative.")

        return abs(self.dot(other)) <= tolerance

    def to_dict(self) -> dict:
        return {
            "dimension": self.dimension,
            "values": list(self.values)
        }


class VectorEngine:
    """Service layer for vector calculations and operation reporting."""

    @staticmethod
    def execute(
        operation: VectorOperation,
        vector_a: Vector,
        vector_b: Vector | None = None,
        scalar: float | None = None
    ) -> float | Vector:

        if operation == VectorOperation.ADDITION:
            if vector_b is None:
                raise VectorError("Addition requires two vectors.")
            return vector_a.add(vector_b)

        if operation == VectorOperation.SCALAR_MULTIPLICATION:
            if scalar is None:
                raise VectorError("Scalar multiplication requires a scalar.")
            return vector_a.scale(scalar)

        if operation == VectorOperation.DOT_PRODUCT:
            if vector_b is None:
                raise VectorError("Dot product requires two vectors.")
            return vector_a.dot(vector_b)

        if operation == VectorOperation.L1_NORM:
            return vector_a.l1_norm()

        if operation == VectorOperation.L2_NORM:
            return vector_a.l2_norm()

        if operation == VectorOperation.L_INFINITY_NORM:
            return vector_a.infinity_norm()

        raise VectorError("Unsupported operation.")

    @staticmethod
    def compare(first: Vector, second: Vector) -> dict:
        first._check_dimension(second)

        return {
            "addition": first.add(second).values,
            "dot_product": first.dot(second),
            "euclidean_distance": first.distance(second),
            "cosine_similarity": first.cosine_similarity(second)
            if first.l2_norm() and second.l2_norm()
            else None,
            "first_vector_norm": first.l2_norm(),
            "second_vector_norm": second.l2_norm(),
            "orthogonal": first.is_orthogonal(second)
        }


def save_vectors(vectors: dict[str, Vector], filename: str) -> None:
    """Persist vectors as JSON using an atomic replacement."""
    destination = Path(filename)
    temporary = destination.with_suffix(destination.suffix + ".tmp")

    data = {
        name: vector.to_dict()
        for name, vector in vectors.items()
    }

    try:
        temporary.write_text(
            json.dumps(data, indent=2, allow_nan=False),
            encoding="utf-8"
        )
        temporary.replace(destination)
    except OSError:
        temporary.unlink(missing_ok=True)
        raise


def load_vectors(filename: str) -> dict[str, Vector]:
    """Load and validate vectors from a JSON document."""
    try:
        data = json.loads(Path(filename).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise VectorError(f"Unable to load vector file: {error}") from error

    if not isinstance(data, dict):
        raise VectorError("The JSON root must be an object.")

    result = {}

    for name, item in data.items():
        if not isinstance(item, dict):
            raise VectorError(f"Invalid vector record: {name}")

        values = item.get("values")

        if not isinstance(values, list):
            raise VectorError(f"Invalid values for vector: {name}")

        vector = Vector.from_iterable(values)

        if item.get("dimension") != vector.dimension:
            raise VectorError(f"Dimension metadata mismatch: {name}")

        result[name] = vector

    return result


def demonstrate() -> None:
    print("=" * 65)
    print("VECTOR OPERATIONS ENGINE")
    print("=" * 65)

    u = Vector((3, 4))
    v = Vector((4, 3))

    print("\nInput vectors")
    print("u =", u.values)
    print("v =", v.values)

    print("\nFundamental operations")
    print("Addition:", u.add(v).values)
    print("Subtraction:", u.subtract(v).values)
    print("Scalar multiplication (3u):", u.scale(3).values)
    print("Dot product:", u.dot(v))

    print("\nNorm calculations")
    print("L1 norm:", u.l1_norm())
    print("L2 norm:", u.l2_norm())
    print("L-infinity norm:", u.infinity_norm())
    print("L3 norm:", u.norm(3))

    print("\nAdvanced operations")
    print("Normalized u:", u.normalize().values)
    print("Euclidean distance:", u.distance(v))
    print("Cosine similarity:", u.cosine_similarity(v))
    print("Orthogonal:", u.is_orthogonal(v))

    print("\nOperation engine")
    result = VectorEngine.compare(u, v)

    for key, value in result.items():
        print(f"{key}: {value}")

    print("\nHigh-dimensional vector")
    high_dimension = Vector.from_iterable(range(1, 1001))
    print("Dimension:", high_dimension.dimension)
    print("L2 norm:", high_dimension.l2_norm())

    print("\nPersistence")
    filename = "vector_data.json"
    save_vectors({"u": u, "v": v}, filename)
    restored = load_vectors(filename)
    print("Restored:", {
        name: vector.values for name, vector in restored.items()
    })
    Path(filename).unlink(missing_ok=True)

    print("\nValidation and failure handling")

    try:
        u.add(Vector((1, 2, 3)))
    except DimensionMismatchError as error:
        print("Dimension error:", error)

    try:
        Vector((0, 0)).normalize()
    except ZeroVectorError as error:
        print("Zero-vector error:", error)

    try:
        Vector((1, float("inf")))
    except VectorError as error:
        print("Invalid vector:", error)

    print("\nAssertions")
    assert u.add(v).values == (7.0, 7.0)
    assert u.dot(v) == 24.0
    assert math.isclose(u.l2_norm(), 5.0)
    assert math.isclose(u.normalize().l2_norm(), 1.0)
    assert Vector((1, 0)).is_orthogonal(Vector((0, 1)))
    assert Vector((0, 0)).l2_norm() == 0

    print("All assertions passed.")
    print("=" * 65)


if __name__ == "__main__":
    try:
        demonstrate()
    except (VectorError, ArithmeticError, OSError) as error:
        print(f"Execution failed: {error}", file=sys.stderr)
        sys.exit(1)
