from __future__ import annotations

"""
Recurrence Relations: Linear, Homogeneous, and Non-Homogeneous Recurrences

This self-contained script develops recurrence relations from direct evaluation
to efficient matrix-based evaluation and recurrence analysis.

No third-party packages are required.
"""

from dataclasses import dataclass
from fractions import Fraction
from functools import lru_cache
from math import isqrt
from typing import Callable, Iterable


Number = int | Fraction


def print_title(title: str) -> None:
    print("\n" + "=" * 78)
    print(title)
    print("=" * 78)


# ---------------------------------------------------------------------------
# Core recurrence representation
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class LinearRecurrence:
    """
    Represents

        a_n = c_1*a_(n-1) + c_2*a_(n-2) + ... + c_k*a_(n-k) + f(n)

    where f(n) = 0 for a homogeneous recurrence.

    initial_terms contains:
        a_0, a_1, ..., a_(k-1)
    coefficients contains:
        c_1, c_2, ..., c_k
    forcing contains the non-homogeneous term f(n).
    """

    coefficients: tuple[Number, ...]
    initial_terms: tuple[Number, ...]
    forcing: Callable[[int], Number] = lambda n: 0

    def __post_init__(self) -> None:
        if not self.coefficients:
            raise ValueError("At least one recurrence coefficient is required.")
        if len(self.coefficients) != len(self.initial_terms):
            raise ValueError(
                "The number of initial terms must equal the recurrence order."
            )

    @property
    def order(self) -> int:
        return len(self.coefficients)

    @property
    def is_homogeneous(self) -> bool:
        return all(self.forcing(n) == 0 for n in range(0, 8))

    def next_term(self, history: list[Number], n: int) -> Number:
        if len(history) < self.order:
            raise ValueError("Insufficient history for the requested recurrence.")
        recent = history[-self.order:]
        value = sum(
            coefficient * term
            for coefficient, term in zip(self.coefficients, reversed(recent))
        )
        return value + self.forcing(n)

    def generate(self, count: int) -> list[Number]:
        if count < 0:
            raise ValueError("count cannot be negative.")

        terms = list(self.initial_terms[:count])

        while len(terms) < count:
            n = len(terms)
            terms.append(self.next_term(terms, n))

        return terms


def generate_with_direct_function(
    initial_terms: Iterable[Number],
    coefficients: Iterable[Number],
    count: int,
    forcing: Callable[[int], Number] | None = None,
) -> list[Number]:
    recurrence = LinearRecurrence(
        tuple(coefficients),
        tuple(initial_terms),
        forcing or (lambda n: 0),
    )
    return recurrence.generate(count)


# ---------------------------------------------------------------------------
# Fundamental examples
# ---------------------------------------------------------------------------

def demonstrate_arithmetic_recurrence() -> None:
    print_title("Linear first-order recurrence")

    # a_n = a_(n-1) + 3, a_0 = 2
    recurrence = LinearRecurrence((1,), (2,), lambda n: 3)
    print("Recurrence: a_n = a_(n-1) + 3")
    print("Initial condition: a_0 = 2")
    print("Terms:", recurrence.generate(10))


def demonstrate_fibonacci() -> None:
    print_title("Homogeneous second-order recurrence")

    # F_n = F_(n-1) + F_(n-2)
    recurrence = LinearRecurrence((1, 1), (0, 1))
    print("Recurrence: F_n = F_(n-1) + F_(n-2)")
    print("Terms:", recurrence.generate(15))


def demonstrate_non_homogeneous() -> None:
    print_title("Non-homogeneous recurrence")

    # a_n = 2a_(n-1) + n
    recurrence = LinearRecurrence(
        coefficients=(2,),
        initial_terms=(1,),
        forcing=lambda n: n,
    )
    print("Recurrence: a_n = 2a_(n-1) + n")
    print("Initial condition: a_0 = 1")
    print("Terms:", recurrence.generate(10))


# ---------------------------------------------------------------------------
# Recurrence classification
# ---------------------------------------------------------------------------

def classify_recurrence(
    coefficients: Iterable[Number],
    forcing: Callable[[int], Number] | None = None,
) -> str:
    coefficient_tuple = tuple(coefficients)
    if not coefficient_tuple:
        raise ValueError("A recurrence needs at least one coefficient.")

    forcing = forcing or (lambda n: 0)

    if all(forcing(n) == 0 for n in range(0, 8)):
        return f"linear homogeneous recurrence of order {len(coefficient_tuple)}"

    return f"linear non-homogeneous recurrence of order {len(coefficient_tuple)}"


def demonstrate_classification() -> None:
    print_title("Classification")

    examples = [
        ((2,), lambda n: 0),
        ((1, 1), lambda n: 0),
        ((3, -2), lambda n: n),
        ((1, -1, 2), lambda n: 5),
    ]

    for coefficients, forcing in examples:
        print(classify_recurrence(coefficients, forcing))


# ---------------------------------------------------------------------------
# Naive recursion versus memoization
# ---------------------------------------------------------------------------

def fibonacci_naive(n: int) -> int:
    if n < 0:
        raise ValueError("n must be non-negative.")
    if n < 2:
        return n
    return fibonacci_naive(n - 1) + fibonacci_naive(n - 2)


@lru_cache(maxsize=None)
def fibonacci_memoized(n: int) -> int:
    if n < 0:
        raise ValueError("n must be non-negative.")
    if n < 2:
        return n
    return fibonacci_memoized(n - 1) + fibonacci_memoized(n - 2)


def fibonacci_iterative(n: int) -> int:
    if n < 0:
        raise ValueError("n must be non-negative.")

    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a


def demonstrate_evaluation_strategies() -> None:
    print_title("Evaluation strategies")

    print("Naive recursion F_10:", fibonacci_naive(10))
    print("Memoized recursion F_40:", fibonacci_memoized(40))
    print("Iterative F_100:", fibonacci_iterative(100))

    print(
        "Naive Fibonacci has exponential time growth because "
        "the same subproblems are recomputed."
    )
    print(
        "Memoization reduces repeated work to linear time for the sequence "
        "through n."
    )


# ---------------------------------------------------------------------------
# Matrix arithmetic for fast recurrence evaluation
# ---------------------------------------------------------------------------

Matrix = list[list[Number]]


def matrix_multiply(a: Matrix, b: Matrix) -> Matrix:
    if not a or not b:
        raise ValueError("Matrices cannot be empty.")

    if len(a[0]) != len(b):
        raise ValueError("Matrix dimensions are incompatible.")

    rows = len(a)
    columns = len(b[0])
    shared = len(b)

    result: Matrix = [[0 for _ in range(columns)] for _ in range(rows)]

    for i in range(rows):
        for k in range(shared):
            if a[i][k] == 0:
                continue
            for j in range(columns):
                result[i][j] += a[i][k] * b[k][j]

    return result


def matrix_power(matrix: Matrix, exponent: int) -> Matrix:
    if exponent < 0:
        raise ValueError("Matrix exponent must be non-negative.")

    size = len(matrix)
    if size == 0 or any(len(row) != size for row in matrix):
        raise ValueError("matrix_power requires a square matrix.")

    result: Matrix = [
        [1 if i == j else 0 for j in range(size)]
        for i in range(size)
    ]
    base = [row[:] for row in matrix]

    while exponent:
        if exponent & 1:
            result = matrix_multiply(result, base)
        base = matrix_multiply(base, base)
        exponent >>= 1

    return result


def companion_matrix(coefficients: tuple[Number, ...]) -> Matrix:
    """
    For

        a_n = c1*a_(n-1) + ... + ck*a_(n-k)

    construct a companion matrix whose state is

        [a_n, a_(n-1), ..., a_(n-k+1)]^T.
    """

    order = len(coefficients)
    matrix: Matrix = [[0 for _ in range(order)] for _ in range(order)]

    matrix[0] = list(coefficients)

    for row in range(1, order):
        matrix[row][row - 1] = 1

    return matrix


def nth_homogeneous_term(
    coefficients: tuple[Number, ...],
    initial_terms: tuple[Number, ...],
    n: int,
) -> Number:
    if n < 0:
        raise ValueError("n must be non-negative.")

    order = len(coefficients)

    if len(initial_terms) != order:
        raise ValueError("Initial-term count must equal recurrence order.")

    if n < order:
        return initial_terms[n]

    matrix = companion_matrix(coefficients)
    exponent = n - (order - 1)
    powered = matrix_power(matrix, exponent)

    state = [[initial_terms[-1 - i]] for i in range(order)]
    result = matrix_multiply(powered, state)

    return result[0][0]


def demonstrate_matrix_method() -> None:
    print_title("Fast evaluation with companion matrices")

    coefficients = (1, 1)
    initial_terms = (0, 1)

    for n in (10, 20, 50, 100):
        print(f"F_{n} =", nth_homogeneous_term(coefficients, initial_terms, n))

    print(
        "Sequential evaluation needs O(n) recurrence steps. "
        "Matrix exponentiation reduces exponentiation depth to O(log n), "
        "although matrix multiplication still carries arithmetic cost."
    )


# ---------------------------------------------------------------------------
# Characteristic polynomial for homogeneous recurrences
# ---------------------------------------------------------------------------

def characteristic_coefficients(
    coefficients: tuple[Number, ...],
) -> list[Number]:
    """
    For

        a_n = c1*a_(n-1) + ... + ck*a_(n-k)

    the characteristic polynomial is

        r^k - c1*r^(k-1) - ... - ck.

    The result is ordered from the highest power to the constant term.
    """

    return [1, *[-c for c in coefficients]]


def integer_quadratic_roots(
    coefficients: tuple[int, int],
) -> tuple[Fraction, Fraction] | None:
    """
    Handles the common second-order case

        a_n = c1*a_(n-1) + c2*a_(n-2)

    by solving

        r^2 - c1*r - c2 = 0

    when the discriminant is a perfect square.
    """

    c1, c2 = coefficients
    discriminant = c1 * c1 + 4 * c2

    if discriminant < 0:
        return None

    root = isqrt(discriminant)

    if root * root != discriminant:
        return None

    return (
        Fraction(c1 + root, 2),
        Fraction(c1 - root, 2),
    )


def demonstrate_characteristic_equation() -> None:
    print_title("Characteristic equation")

    coefficients = (3, -2)
    polynomial = characteristic_coefficients(coefficients)

    print("Recurrence: a_n = 3a_(n-1) - 2a_(n-2)")
    print("Characteristic polynomial coefficients:", polynomial)

    roots = integer_quadratic_roots(coefficients)
    print("Roots:", roots)

    if roots:
        print(
            "Distinct roots imply a homogeneous solution of the form "
            "A*r1^n + B*r2^n."
        )


# ---------------------------------------------------------------------------
# Solving constants for a second-order homogeneous recurrence
# ---------------------------------------------------------------------------

def solve_distinct_root_constants(
    root1: Fraction,
    root2: Fraction,
    a0: Number,
    a1: Number,
) -> tuple[Fraction, Fraction]:
    if root1 == root2:
        raise ValueError("Roots must be distinct.")

    # A + B = a0
    # A*r1 + B*r2 = a1
    denominator = root1 - root2

    A = Fraction(a1) - Fraction(a0) * root2
    A /= denominator
    B = Fraction(a0) - A

    return A, B


def demonstrate_closed_form() -> None:
    print_title("Closed form for distinct characteristic roots")

    # a_n = 3a_(n-1) - 2a_(n-2), a_0 = 1, a_1 = 3
    coefficients = (3, -2)
    roots = integer_quadratic_roots(coefficients)

    if roots is None:
        raise RuntimeError("Expected rational roots.")

    r1, r2 = roots
    A, B = solve_distinct_root_constants(r1, r2, 1, 3)

    print(f"Roots: r1={r1}, r2={r2}")
    print(f"Constants: A={A}, B={B}")

    for n in range(8):
        closed = A * r1**n + B * r2**n
        print(f"a_{n} =", closed)


# ---------------------------------------------------------------------------
# Non-homogeneous recurrence by converting to a state system
# ---------------------------------------------------------------------------

def generate_non_homogeneous_by_state(
    coefficients: tuple[Number, ...],
    initial_terms: tuple[Number, ...],
    forcing: Callable[[int], Number],
    count: int,
) -> list[Number]:
    """
    Directly evaluates a non-homogeneous recurrence while retaining the
    forcing term separately from the homogeneous linear combination.
    """

    recurrence = LinearRecurrence(coefficients, initial_terms, forcing)
    return recurrence.generate(count)


def demonstrate_forcing_functions() -> None:
    print_title("Different forcing functions")

    linear_forcing = LinearRecurrence(
        coefficients=(2,),
        initial_terms=(1,),
        forcing=lambda n: n,
    )

    constant_forcing = LinearRecurrence(
        coefficients=(2,),
        initial_terms=(1,),
        forcing=lambda n: 5,
    )

    exponential_forcing = LinearRecurrence(
        coefficients=(2,),
        initial_terms=(1,),
        forcing=lambda n: 2**n,
    )

    print("a_n = 2a_(n-1) + n")
    print(linear_forcing.generate(8))

    print("a_n = 2a_(n-1) + 5")
    print(constant_forcing.generate(8))

    print("a_n = 2a_(n-1) + 2^n")
    print(exponential_forcing.generate(8))


# ---------------------------------------------------------------------------
# Order validation and recurrence fitting
# ---------------------------------------------------------------------------

def verify_sequence(
    sequence: list[Number],
    coefficients: tuple[Number, ...],
    forcing: Callable[[int], Number] | None = None,
) -> list[tuple[int, Number, Number]]:
    """
    Return mismatches as (n, expected, actual).

    This is useful when validating whether observed data actually satisfies
    a proposed recurrence.
    """

    forcing = forcing or (lambda n: 0)
    order = len(coefficients)

    mismatches = []

    for n in range(order, len(sequence)):
        expected = (
            sum(
                coefficient * sequence[n - i - 1]
                for i, coefficient in enumerate(coefficients)
            )
            + forcing(n)
        )

        actual = sequence[n]

        if expected != actual:
            mismatches.append((n, expected, actual))

    return mismatches


def demonstrate_validation() -> None:
    print_title("Validating an observed sequence")

    sequence = [1, 1, 2, 3, 5, 8, 13, 21]
    mismatches = verify_sequence(sequence, (1, 1))

    print("Fibonacci validation mismatches:", mismatches)

    corrupted = sequence[:]
    corrupted[5] = 99

    mismatches = verify_sequence(corrupted, (1, 1))
    print("Corrupted sequence mismatches:", mismatches)


# ---------------------------------------------------------------------------
# Practical recurrence: population model
# ---------------------------------------------------------------------------

@dataclass
class PopulationModel:
    """
    A discrete population model:

        P_n = growth * P_(n-1) + seasonal_adjustment(n)

    The recurrence is linear and non-homogeneous when the seasonal term
    is non-zero.
    """

    growth: Fraction
    initial_population: int
    seasonal_adjustment: Callable[[int], int]

    def project(self, periods: int) -> list[Fraction]:
        if periods < 0:
            raise ValueError("periods must be non-negative.")
        if self.initial_population < 0:
            raise ValueError("Population cannot start negative.")

        population = [Fraction(self.initial_population)]

        for n in range(1, periods):
            next_population = (
                self.growth * population[-1]
                + self.seasonal_adjustment(n)
            )

            if next_population < 0:
                raise ValueError(
                    f"Model produced an invalid negative population at n={n}."
                )

            population.append(next_population)

        return population


def demonstrate_population_model() -> None:
    print_title("Practical non-homogeneous model")

    model = PopulationModel(
        growth=Fraction(11, 10),
        initial_population=1000,
        seasonal_adjustment=lambda n: -25 if n % 3 == 0 else 10,
    )

    projection = model.project(12)

    for period, population in enumerate(projection):
        print(f"period={period:2d}, population={population}")


# ---------------------------------------------------------------------------
# Complexity comparison
# ---------------------------------------------------------------------------

def recurrence_complexity_notes() -> None:
    print_title("Complexity and implementation decisions")

    notes = {
        "direct iterative recurrence": "O(n) recurrence evaluations and O(k) work per term",
        "naive recursive Fibonacci": "exponential time due to repeated subproblems",
        "memoized recurrence": "O(n) states for a first-order progression through n",
        "companion matrix exponentiation": "O(log n) matrix multiplications for fixed order",
        "closed form": "often O(1) structural evaluation, but numerical stability can vary",
    }

    for approach, complexity in notes.items():
        print(f"{approach}: {complexity}")

    print(
        "For large n, exact integer arithmetic may dominate runtime and memory "
        "even when the recurrence algorithm itself is asymptotically efficient."
    )


# ---------------------------------------------------------------------------
# Edge cases and failure handling
# ---------------------------------------------------------------------------

def demonstrate_edge_cases() -> None:
    print_title("Edge cases and validation")

    cases = [
        ("zero-order recurrence", lambda: LinearRecurrence((), ())),
        (
            "mismatched initial terms",
            lambda: LinearRecurrence((1, 2), (1,)),
        ),
        (
            "negative sequence count",
            lambda: LinearRecurrence((1,), (1,)).generate(-1),
        ),
        (
            "negative matrix exponent",
            lambda: matrix_power([[1, 0], [0, 1]], -1),
        ),
        (
            "negative Fibonacci index",
            lambda: fibonacci_iterative(-5),
        ),
    ]

    for name, operation in cases:
        try:
            operation()
        except (ValueError, IndexError) as exc:
            print(f"{name}: rejected safely -> {exc}")


# ---------------------------------------------------------------------------
# A general recurrence API
# ---------------------------------------------------------------------------

class RecurrenceEngine:
    """
    Small reusable API for evaluating a family of linear recurrences.

    The engine deliberately separates recurrence definition from evaluation
    strategy so that the same mathematical rule can be evaluated iteratively,
    recursively, or through a matrix representation when homogeneous.
    """

    def __init__(self, recurrence: LinearRecurrence):
        self.recurrence = recurrence

    def terms(self, count: int) -> list[Number]:
        return self.recurrence.generate(count)

    def validate(self, sequence: list[Number]) -> bool:
        return not verify_sequence(
            sequence,
            self.recurrence.coefficients,
            self.recurrence.forcing,
        )

    def nth(self, n: int) -> Number:
        if n < 0:
            raise ValueError("n must be non-negative.")

        if self.recurrence.is_homogeneous:
            return nth_homogeneous_term(
                self.recurrence.coefficients,
                self.recurrence.initial_terms,
                n,
            )

        # General non-homogeneous recurrences use direct iteration here.
        # This avoids pretending that arbitrary forcing functions can be
        # reduced to a homogeneous companion matrix without extra state.
        return self.recurrence.generate(n + 1)[n]


def demonstrate_reusable_engine() -> None:
    print_title("Reusable recurrence engine")

    recurrence = LinearRecurrence(
        coefficients=(2, -1),
        initial_terms=(1, 2),
    )

    engine = RecurrenceEngine(recurrence)

    print("Terms:", engine.terms(10))
    print("a_50:", engine.nth(50))
    print("Valid sequence:", engine.validate(engine.terms(10)))

    invalid = engine.terms(10)
    invalid[7] += 100
    print("Corrupted sequence valid:", engine.validate(invalid))


# ---------------------------------------------------------------------------
# Main demonstration
# ---------------------------------------------------------------------------

def main() -> None:
    print_title("RECURRENCE RELATIONS LABORATORY")

    demonstrate_arithmetic_recurrence()
    demonstrate_fibonacci()
    demonstrate_non_homogeneous()
    demonstrate_classification()
    demonstrate_evaluation_strategies()
    demonstrate_matrix_method()
    demonstrate_characteristic_equation()
    demonstrate_closed_form()
    demonstrate_forcing_functions()
    demonstrate_validation()
    demonstrate_population_model()
    recurrence_complexity_notes()
    demonstrate_edge_cases()
    demonstrate_reusable_engine()

    print_title("Completed")
    print(
        "The demonstrations covered linear recurrences, homogeneous "
        "recurrences, non-homogeneous recurrences, characteristic equations, "
        "forcing functions, validation, recursion, memoization, and matrix "
        "evaluation."
    )


if __name__ == "__main__":
    main()
