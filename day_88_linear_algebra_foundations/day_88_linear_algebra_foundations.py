#!/usr/bin/env python3
"""
Linear Algebra Foundations
Scalars, vectors, vector notation, and vector spaces.

A self-contained implementation using Python's standard library.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import isclose, isfinite, sqrt
from typing import Iterable, Sequence


TOLERANCE = 1e-9


class LinearAlgebraError(Exception):
    """Base exception for linear algebra operations."""


class DimensionError(LinearAlgebraError):
    """Raised when vector dimensions are incompatible."""


class InvalidScalarError(LinearAlgebraError):
    """Raised when a scalar is not a finite real number."""


def validate_scalar(value: float) -> float:
    """Validate a real scalar represented by a finite Python number."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise InvalidScalarError("A scalar must be a real numeric value.")

    result = float(value)

    if not isfinite(result):
        raise InvalidScalarError("Scalars must be finite.")

    return result


@dataclass(frozen=True)
class Scalar:
    """A real scalar belonging to the field R."""

    value: float

    def __post_init__(self):
        object.__setattr__(self, "value", validate_scalar(self.value))

    def __add__(self, other: Scalar) -> Scalar:
        return Scalar(self.value + other.value)

    def __mul__(self, other: Scalar) -> Scalar:
        return Scalar(self.value * other.value)

    def __repr__(self) -> str:
        return f"Scalar({self.value:g})"


@dataclass(frozen=True)
class Vector:
    """
    An immutable vector in R^n.

    A vector is an ordered collection of real components.
    Its dimension is determined by the number of components.
    """

    components: tuple[float, ...]

    def __post_init__(self):
        values = tuple(validate_scalar(x) for x in self.components)

        if not values:
            raise DimensionError("A vector must have at least one component.")

        object.__setattr__(self, "components", values)

    @classmethod
    def from_values(cls, values: Iterable[float]) -> Vector:
        return cls(tuple(values))

    @property
    def dimension(self) -> int:
        return len(self.components)

    def _check_dimension(self, other: Vector) -> None:
        if self.dimension != other.dimension:
            raise DimensionError(
                f"Dimension mismatch: R^{self.dimension} and "
                f"R^{other.dimension}."
            )

    def __add__(self, other: Vector) -> Vector:
        self._check_dimension(other)

        return Vector(tuple(
            a + b for a, b in zip(self.components, other.components)
        ))

    def __sub__(self, other: Vector) -> Vector:
        self._check_dimension(other)

        return Vector(tuple(
            a - b for a, b in zip(self.components, other.components)
        ))

    def __neg__(self) -> Vector:
        return Vector(tuple(-x for x in self.components))

    def scale(self, scalar: float) -> Vector:
        scalar = validate_scalar(scalar)

        return Vector(tuple(
            scalar * component for component in self.components
        ))

    def dot(self, other: Vector) -> float:
        self._check_dimension(other)

        return sum(
            a * b for a, b in zip(self.components, other.components)
        )

    def norm(self) -> float:
        """Euclidean norm: ||v|| = sqrt(v1² + ... + vn²)."""
        return sqrt(self.dot(self))

    def normalize(self) -> Vector:
        magnitude = self.norm()

        if magnitude <= TOLERANCE:
            raise LinearAlgebraError(
                "The zero vector cannot be normalized."
            )

        return self.scale(1.0 / magnitude)

    def is_zero(self, tolerance: float = TOLERANCE) -> bool:
        return all(abs(x) <= tolerance for x in self.components)

    def approximately_equals(
        self,
        other: Vector,
        tolerance: float = TOLERANCE
    ) -> bool:
        self._check_dimension(other)

        return all(
            isclose(a, b, abs_tol=tolerance, rel_tol=tolerance)
            for a, b in zip(self.components, other.components)
        )

    def __repr__(self) -> str:
        values = ", ".join(f"{x:g}" for x in self.components)
        return f"({values})"


@dataclass(frozen=True)
class VectorSpace:
    """
    The real coordinate vector space R^n.

    Supports vector addition and scalar multiplication over R.
    """

    dimension: int
    field: str = "R"

    def __post_init__(self):
        if isinstance(self.dimension, bool) or not isinstance(
            self.dimension, int
        ):
            raise DimensionError("Dimension must be an integer.")

        if self.dimension <= 0:
            raise DimensionError("Dimension must be positive.")

        if self.field != "R":
            raise LinearAlgebraError(
                "This implementation supports the real field R only."
            )

    def validate(self, vector: Vector) -> None:
        if vector.dimension != self.dimension:
            raise DimensionError(
                f"Expected R^{self.dimension}, received "
                f"R^{vector.dimension}."
            )

    def zero(self) -> Vector:
        return Vector((0.0,) * self.dimension)

    def add(self, first: Vector, second: Vector) -> Vector:
        self.validate(first)
        self.validate(second)
        return first + second

    def scalar_multiply(self, scalar: float, vector: Vector) -> Vector:
        self.validate(vector)
        return vector.scale(scalar)

    def linear_combination(
        self,
        vectors: Sequence[Vector],
        coefficients: Sequence[float]
    ) -> Vector:
        """
        Compute c1*v1 + c2*v2 + ... + ck*vk.
        """
        if len(vectors) != len(coefficients):
            raise LinearAlgebraError(
                "The number of vectors and coefficients must match."
            )

        result = self.zero()

        for vector, coefficient in zip(vectors, coefficients):
            self.validate(vector)
            result = result + vector.scale(coefficient)

        return result

    def satisfies_closure(
        self,
        first: Vector,
        second: Vector,
        scalar: float
    ) -> bool:
        """Check addition and scalar-multiplication closure."""
        self.validate(first)
        self.validate(second)

        addition_result = first + second
        multiplication_result = first.scale(scalar)

        return (
            addition_result.dimension == self.dimension
            and multiplication_result.dimension == self.dimension
        )


def matrix_rank(
    vectors: Sequence[Vector],
    tolerance: float = TOLERANCE
) -> int:
    """
    Calculate the dimension of the span of the supplied vectors.

    Vectors are interpreted as columns of a matrix.
    Gaussian elimination uses partial pivoting.
    Time complexity: O(m*n*min(m,n)), approximately cubic
    for square matrices.
    """
    if not vectors:
        return 0

    dimension = vectors[0].dimension

    for vector in vectors:
        if vector.dimension != dimension:
            raise DimensionError("All vectors must have equal dimensions.")

    # Construct a matrix with vectors as columns.
    matrix = [
        [vector.components[row] for vector in vectors]
        for row in range(dimension)
    ]

    rows = len(matrix)
    columns = len(vectors)
    rank = 0

    for column in range(columns):
        if rank >= rows:
            break

        pivot = max(
            range(rank, rows),
            key=lambda row: abs(matrix[row][column])
        )

        if abs(matrix[pivot][column]) <= tolerance:
            continue

        matrix[rank], matrix[pivot] = matrix[pivot], matrix[rank]

        pivot_value = matrix[rank][column]

        for row in range(rank + 1, rows):
            factor = matrix[row][column] / pivot_value

            for col in range(column, columns):
                matrix[row][col] -= factor * matrix[rank][col]

        rank += 1

    return rank


def are_linearly_independent(
    vectors: Sequence[Vector]
) -> bool:
    if not vectors:
        return True

    return matrix_rank(vectors) == len(vectors)


def is_basis(
    vectors: Sequence[Vector],
    space: VectorSpace
) -> bool:
    """A basis must be independent and span the entire vector space."""
    for vector in vectors:
        space.validate(vector)

    return (
        len(vectors) == space.dimension
        and are_linearly_independent(vectors)
    )


def demonstrate_vector_space() -> None:
    print("=" * 65)
    print("LINEAR ALGEBRA FOUNDATIONS")
    print("=" * 65)

    # 1. Scalars
    print("\n1. SCALARS")

    alpha = Scalar(3)
    beta = Scalar(2)

    print("Scalar alpha:", alpha)
    print("Scalar beta:", beta)
    print("Addition:", alpha + beta)
    print("Multiplication:", alpha * beta)

    # 2. Vector notation
    print("\n2. VECTORS")

    u = Vector.from_values([2, 3])
    v = Vector.from_values([4, 1])

    print("u =", u)
    print("v =", v)
    print("Dimension of u:", u.dimension)
    print("u + v =", u + v)
    print("u - v =", u - v)
    print("-u =", -u)

    # 3. Scalar multiplication
    print("\n3. SCALAR MULTIPLICATION")

    print("3u =", u.scale(3))
    print("0u =", u.scale(0))
    print("(-2)u =", u.scale(-2))

    # 4. Inner product and magnitude
    print("\n4. DOT PRODUCT AND NORM")

    print("u . v =", u.dot(v))
    print("||u|| =", round(u.norm(), 6))
    print("Normalized u =", u.normalize())

    # 5. Vector space
    print("\n5. VECTOR SPACE R^2")

    space = VectorSpace(2)

    zero = space.zero()

    print("Zero vector:", zero)
    print("Additive identity:", u + zero)
    print("Additive inverse:", u + (-u))
    print("Closure:", space.satisfies_closure(u, v, 5))

    # 6. Linear combinations
    print("\n6. LINEAR COMBINATIONS")

    combination = space.linear_combination(
        [u, v],
        [2, 3]
    )

    print("2u + 3v =", combination)

    # 7. Linear independence and basis
    print("\n7. LINEAR INDEPENDENCE AND BASIS")

    e1 = Vector.from_values([1, 0])
    e2 = Vector.from_values([0, 1])

    print("Standard basis:", [e1, e2])
    print("Independent:", are_linearly_independent([e1, e2]))
    print("Is a basis of R^2:", is_basis([e1, e2], space))

    dependent = [
        Vector.from_values([1, 2]),
        Vector.from_values([2, 4])
    ]

    print("Dependent vectors:", dependent)
    print("Independent:", are_linearly_independent(dependent))

    # 8. Higher-dimensional space
    print("\n8. HIGHER-DIMENSIONAL VECTOR SPACE")

    space3 = VectorSpace(3)

    a = Vector.from_values([1, 2, 3])
    b = Vector.from_values([0, 1, 2])
    c = Vector.from_values([2, 3, 5])

    print("Vectors:", a, b, c)
    print("Span dimension:", matrix_rank([a, b, c]))
    print("Basis of R^3:", is_basis([a, b, c], space3))

    # 9. Validation and edge cases
    print("\n9. VALIDATION")

    try:
        _ = u + Vector.from_values([1, 2, 3])
    except DimensionError as error:
        print("Dimension error:", error)

    try:
        Vector.from_values([float("nan"), 2])
    except InvalidScalarError as error:
        print("Invalid scalar:", error)

    try:
        space.zero().normalize()
    except LinearAlgebraError as error:
        print("Normalization error:", error)

    try:
        VectorSpace(0)
    except DimensionError as error:
        print("Invalid vector space:", error)

    print("\n10. ASSERTIONS")

    assert (u + v).approximately_equals(
        Vector.from_values([6, 4])
    )

    assert u.dot(v) == 11
    assert u.scale(0).is_zero()
    assert isclose(e1.norm(), 1.0)
    assert matrix_rank([e1, e2]) == 2
    assert not are_linearly_independent(dependent)

    assert is_basis([e1, e2], space)

    assert space.linear_combination(
        [e1, e2],
        [5, 7]
    ).approximately_equals(
        Vector.from_values([5, 7])
    )

    print("All assertions passed.")


if __name__ == "__main__":
    demonstrate_vector_space()
