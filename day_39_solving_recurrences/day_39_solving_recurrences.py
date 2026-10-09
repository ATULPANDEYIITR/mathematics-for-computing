"""
Solving Recurrences
===================

A self-contained executable study of recurrence solving through:

- Iteration / repeated substitution
- Substitution with an explicit induction check
- Characteristic equations for linear recurrences
- Homogeneous and non-homogeneous linear recurrences
- Repeated characteristic roots
- Complexity interpretation
- Numerical validation
- Symbolic-style coefficient solving using only the standard library

The implementations use recurrence relations that arise naturally in
algorithm analysis and discrete mathematics.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from math import isclose
from typing import Callable, Iterable


# ---------------------------------------------------------------------------
# Basic recurrence evaluation
# ---------------------------------------------------------------------------

def evaluate_recurrence(
    recurrence: Callable[[int, list[int]], int],
    base_values: list[int],
    target_n: int,
) -> int:
    """Evaluate a recurrence iteratively from its known base values.

    recurrence(n, values) must return T(n), using values containing
    T(0), ..., T(n-1).
    """
    if target_n < 0:
        raise ValueError("target_n must be non-negative")
    if not base_values:
        raise ValueError("At least one base value is required")

    values = list(base_values)

    if target_n < len(values):
        return values[target_n]

    for n in range(len(values), target_n + 1):
        values.append(recurrence(n, values))

    return values[target_n]


# ---------------------------------------------------------------------------
# Iteration example: T(n) = T(n - 1) + 3
#
# Repeated expansion gives:
#
# T(n) = T(n-1) + 3
#      = T(n-2) + 3 + 3
#      = ...
#      = T(0) + 3n
#
# ---------------------------------------------------------------------------

def additive_recurrence(n: int, values: list[int]) -> int:
    return values[n - 1] + 3


def additive_closed_form(n: int, base: int = 5) -> int:
    return base + 3 * n


# ---------------------------------------------------------------------------
# Iteration example: T(n) = 2T(n - 1) + 1
#
# Expanding:
#
# T(n) = 2T(n-1) + 1
#      = 2(2T(n-2) + 1) + 1
#      = 2^2 T(n-2) + 2 + 1
#      = 2^k T(n-k) + (2^k - 1)
#
# Setting k=n:
#
# T(n) = 2^n T(0) + 2^n - 1
#      = 6*2^n - 1 when T(0)=5.
# ---------------------------------------------------------------------------

def exponential_recurrence(n: int, values: list[int]) -> int:
    return 2 * values[n - 1] + 1


def exponential_closed_form(n: int, base: int = 5) -> int:
    return (base + 1) * (2**n) - 1


# ---------------------------------------------------------------------------
# Recurrence with a changing additive term:
#
# T(n) = T(n - 1) + n
#
# Iteration gives:
#
# T(n) = T(0) + 1 + 2 + ... + n
#      = T(0) + n(n+1)/2
# ---------------------------------------------------------------------------

def triangular_recurrence(n: int, values: list[int]) -> int:
    return values[n - 1] + n


def triangular_closed_form(n: int, base: int = 2) -> int:
    return base + n * (n + 1) // 2


# ---------------------------------------------------------------------------
# Recurrence with division:
#
# T(n) = T(floor(n/2)) + 1
#
# This is useful for understanding logarithmic growth. Iteration follows
# the sequence n, floor(n/2), floor(n/4), ... until zero.
# ---------------------------------------------------------------------------

def halving_steps(n: int) -> int:
    if n < 0:
        raise ValueError("n must be non-negative")

    count = 0
    while n > 0:
        n //= 2
        count += 1
    return count


# ---------------------------------------------------------------------------
# General substitution expansion
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class ExpansionStep:
    level: int
    expression: str


def show_first_order_expansion(
    coefficient: int,
    constant: int,
    base_symbol: str = "T(0)",
    levels: int = 5,
) -> list[ExpansionStep]:
    """Generate readable repeated substitutions for T(n)=aT(n-1)+c.

    This is deliberately an expansion utility rather than a symbolic algebra
    system. It records the mathematical structure without requiring a
    third-party symbolic package.
    """
    if levels < 0:
        raise ValueError("levels must be non-negative")

    steps: list[ExpansionStep] = []

    if levels == 0:
        return [ExpansionStep(0, base_symbol)]

    expression = f"{coefficient}T(n-1) + {constant}"
    steps.append(ExpansionStep(1, expression))

    for level in range(2, levels + 1):
        expression = (
            f"{coefficient}^{level}T(n-{level}) + "
            f"({coefficient}^{level - 1} + ... + {coefficient} + 1)"
        )
        steps.append(ExpansionStep(level, expression))

    return steps


# ---------------------------------------------------------------------------
# First-order linear recurrence:
#
# T(n) = a*T(n-1) + b
#
# For a != 1:
#
# T(n) = a^n*T(0) + b*(a^n - 1)/(a - 1)
#
# For a == 1:
#
# T(n) = T(0) + bn
# ---------------------------------------------------------------------------

def first_order_closed_form(
    n: int,
    a: int | Fraction,
    b: int | Fraction,
    initial: int | Fraction,
) -> Fraction:
    if n < 0:
        raise ValueError("n must be non-negative")

    a = Fraction(a)
    b = Fraction(b)
    initial = Fraction(initial)

    if a == 1:
        return initial + b * n

    return initial * a**n + b * (a**n - 1) / (a - 1)


def verify_first_order_formula(
    a: int,
    b: int,
    initial: int,
    max_n: int = 20,
) -> bool:
    values = [initial]

    for n in range(1, max_n + 1):
        values.append(a * values[-1] + b)

    return all(
        Fraction(values[n]) == first_order_closed_form(n, a, b, initial)
        for n in range(max_n + 1)
    )


# ---------------------------------------------------------------------------
# Characteristic equations
#
# For:
#
# T(n) = p*T(n-1) + q*T(n-2)
#
# assume T(n)=r^n:
#
# r^n = p*r^(n-1) + q*r^(n-2)
#
# Divide by r^(n-2):
#
# r^2 - p*r - q = 0
#
# The two roots determine the homogeneous solution.
# ---------------------------------------------------------------------------

def quadratic_roots(
    a: Fraction,
    b: Fraction,
    c: Fraction,
) -> tuple[complex, complex]:
    """Return the roots of ax^2 + bx + c = 0.

    Complex arithmetic keeps the function valid for negative discriminants.
    """
    if a == 0:
        raise ValueError("Quadratic coefficient cannot be zero")

    discriminant = complex(b * b - 4 * a * c)
    sqrt_discriminant = discriminant**0.5

    root1 = (-complex(b) + sqrt_discriminant) / (2 * complex(a))
    root2 = (-complex(b) - sqrt_discriminant) / (2 * complex(a))
    return root1, root2


def fibonacci_values(count: int) -> list[int]:
    if count < 0:
        raise ValueError("count must be non-negative")
    if count == 0:
        return []
    if count == 1:
        return [0]

    values = [0, 1]
    for _ in range(2, count):
        values.append(values[-1] + values[-2])
    return values


# Fibonacci recurrence:
#
# F(n)=F(n-1)+F(n-2)
#
# Characteristic equation:
#
# r^2-r-1=0
#
# roots:
#
# phi=(1+sqrt(5))/2
# psi=(1-sqrt(5))/2
#
# F(n)=(phi^n-psi^n)/sqrt(5)
#
def fibonacci_closed_form(n: int) -> float:
    if n < 0:
        raise ValueError("n must be non-negative")

    sqrt5 = 5**0.5
    phi = (1 + sqrt5) / 2
    psi = (1 - sqrt5) / 2

    return (phi**n - psi**n) / sqrt5


# ---------------------------------------------------------------------------
# General second-order homogeneous recurrence with distinct roots
#
# T(n) = p*T(n-1) + q*T(n-2)
#
# If roots r1 and r2 are distinct:
#
# T(n)=C1*r1^n + C2*r2^n
#
# C1 and C2 are determined by T(0) and T(1).
# ---------------------------------------------------------------------------

def solve_distinct_root_coefficients(
    r1: Fraction,
    r2: Fraction,
    initial0: Fraction,
    initial1: Fraction,
) -> tuple[Fraction, Fraction]:
    if r1 == r2:
        raise ValueError("Roots must be distinct")

    # C1 + C2 = T(0)
    # C1*r1 + C2*r2 = T(1)
    c1 = (initial1 - initial0 * r2) / (r1 - r2)
    c2 = initial0 - c1
    return c1, c2


def distinct_root_solution(
    n: int,
    r1: Fraction,
    r2: Fraction,
    initial0: Fraction,
    initial1: Fraction,
) -> Fraction:
    c1, c2 = solve_distinct_root_coefficients(
        r1, r2, initial0, initial1
    )
    return c1 * r1**n + c2 * r2**n


# ---------------------------------------------------------------------------
# Repeated characteristic root
#
# When the characteristic equation has a repeated root r:
#
# T(n) = (C1 + C2*n)r^n
#
# The n multiplier is essential. C1*r^n alone cannot represent the full
# two-dimensional solution space.
# ---------------------------------------------------------------------------

def repeated_root_solution(
    n: int,
    root: Fraction,
    initial0: Fraction,
    initial1: Fraction,
) -> Fraction:
    if n < 0:
        raise ValueError("n must be non-negative")

    if root == 0:
        if n == 0:
            return initial0
        if n == 1:
            return initial1
        return Fraction(0)

    c1 = Fraction(initial0)
    c2 = Fraction(initial1, 1) / root - c1
    return (c1 + c2 * n) * root**n


# Example:
# T(n)=4T(n-1)-4T(n-2)
#
# Characteristic equation:
# r^2-4r+4=(r-2)^2
#
# Therefore:
# T(n)=(C1+C2*n)2^n
#
def repeated_root_recurrence_values(
    initial0: int,
    initial1: int,
    count: int,
) -> list[int]:
    if count < 0:
        raise ValueError("count must be non-negative")
    if count == 0:
        return []

    values = [initial0]
    if count == 1:
        return values

    values.append(initial1)

    for n in range(2, count):
        values.append(4 * values[n - 1] - 4 * values[n - 2])

    return values


# ---------------------------------------------------------------------------
# Non-homogeneous recurrence
#
# T(n) = 2T(n-1) + 3
#
# The associated homogeneous recurrence is:
#
# T_h(n)=2T_h(n-1)
#
# A constant particular solution T_p=k gives:
#
# k=2k+3
# k=-3
#
# Therefore:
#
# T(n)=C*2^n-3
#
# Initial values determine C.
# ---------------------------------------------------------------------------

def nonhomogeneous_closed_form(
    n: int,
    initial: int,
    coefficient: int = 2,
    forcing: int = 3,
) -> Fraction:
    if coefficient == 1:
        return Fraction(initial) + forcing * n

    particular = Fraction(forcing, 1 - coefficient)
    homogeneous_constant = Fraction(initial) - particular

    return homogeneous_constant * coefficient**n + particular


def nonhomogeneous_values(
    initial: int,
    coefficient: int,
    forcing: int,
    count: int,
) -> list[int]:
    if count < 0:
        raise ValueError("count must be non-negative")
    if count == 0:
        return []

    values = [initial]
    for _ in range(1, count):
        values.append(coefficient * values[-1] + forcing)
    return values


# ---------------------------------------------------------------------------
# Polynomial forcing example
#
# T(n) = T(n-1) + n^2
#
# Iteration gives:
#
# T(n)=T(0)+sum(k^2, k=1..n)
#
# and:
#
# sum(k^2)=n(n+1)(2n+1)/6
# ---------------------------------------------------------------------------

def square_forcing_recurrence(n: int, values: list[int]) -> int:
    return values[-1] + n * n


def square_forcing_closed_form(n: int, initial: int = 7) -> int:
    return initial + n * (n + 1) * (2 * n + 1) // 6


# ---------------------------------------------------------------------------
# Recurrence validation
# ---------------------------------------------------------------------------

def validate_second_order(
    values: Iterable[int],
    p: int,
    q: int,
    initial_count: int = 2,
) -> tuple[bool, list[str]]:
    data = list(values)

    if len(data) < initial_count:
        return False, ["Not enough values to validate the recurrence."]

    errors: list[str] = []

    for n in range(2, len(data)):
        expected = p * data[n - 1] + q * data[n - 2]
        if data[n] != expected:
            errors.append(
                f"T({n})={data[n]}, but recurrence requires {expected}"
            )

    return not errors, errors


# ---------------------------------------------------------------------------
# Complexity measurements
# ---------------------------------------------------------------------------

def naive_fibonacci(n: int) -> int:
    """Naive recursive Fibonacci.

    This intentionally demonstrates the exponential recursion tree.
    """
    if n < 0:
        raise ValueError("n must be non-negative")
    if n <= 1:
        return n
    return naive_fibonacci(n - 1) + naive_fibonacci(n - 2)


def memoized_fibonacci(n: int, cache: dict[int, int] | None = None) -> int:
    """Memoized recurrence evaluation.

    Each Fibonacci state is solved once, reducing time from exponential
    recursion to linear dynamic programming.
    """
    if n < 0:
        raise ValueError("n must be non-negative")

    if cache is None:
        cache = {0: 0, 1: 1}

    if n not in cache:
        cache[n] = (
            memoized_fibonacci(n - 1, cache)
            + memoized_fibonacci(n - 2, cache)
        )

    return cache[n]


# ---------------------------------------------------------------------------
# Matrix exponentiation
#
# Fibonacci can also be represented as:
#
# [F(n+1)]   [1 1]^n [1]
# [F(n)  ] = [1 0]   [0]
#
# Binary exponentiation computes the matrix power in O(log n).
# This is an advanced recurrence-solving technique useful for very large n.
# ---------------------------------------------------------------------------

Matrix2x2 = tuple[tuple[int, int], tuple[int, int]]


def multiply_matrix(a: Matrix2x2, b: Matrix2x2) -> Matrix2x2:
    return (
        (
            a[0][0] * b[0][0] + a[0][1] * b[1][0],
            a[0][0] * b[0][1] + a[0][1] * b[1][1],
        ),
        (
            a[1][0] * b[0][0] + a[1][1] * b[1][0],
            a[1][0] * b[0][1] + a[1][1] * b[1][1],
        ),
    )


def matrix_power(matrix: Matrix2x2, exponent: int) -> Matrix2x2:
    if exponent < 0:
        raise ValueError("exponent must be non-negative")

    result: Matrix2x2 = ((1, 0), (0, 1))
    base = matrix

    while exponent:
        if exponent & 1:
            result = multiply_matrix(result, base)
        base = multiply_matrix(base, base)
        exponent >>= 1

    return result


def fibonacci_logarithmic(n: int) -> int:
    if n < 0:
        raise ValueError("n must be non-negative")

    if n == 0:
        return 0

    matrix = matrix_power(((1, 1), (1, 0)), n)
    return matrix[0][1]


# ---------------------------------------------------------------------------
# Demonstration and executable checks
# ---------------------------------------------------------------------------

def print_comparison(title: str, values: list[int], formula: Callable[[int], int | float]) -> None:
    print(f"\n{title}")
    print("-" * len(title))
    print(f"{'n':>4} {'recurrence':>14} {'closed form':>14} {'match':>8}")

    for n, value in enumerate(values):
        expected = formula(n)
        matches = isclose(float(value), float(expected), rel_tol=1e-10)
        print(f"{n:>4} {value:>14} {expected:>14} {str(matches):>8}")


def main() -> None:
    print("SOLVING RECURRENCES")
    print("===================")

    # Iteration: T(n)=T(n-1)+3, T(0)=5
    additive_values = evaluate_recurrence(
        additive_recurrence, [5], 10
    )
    # evaluate_recurrence returns only the requested target, so create the
    # complete sequence separately for comparison.
    additive_sequence = [5]
    for n in range(1, 11):
        additive_sequence.append(additive_sequence[-1] + 3)

    print_comparison(
        "Iteration: T(n) = T(n-1) + 3",
        additive_sequence,
        lambda n: additive_closed_form(n, 5),
    )

    assert additive_values == additive_closed_form(10, 5)

    # Iteration: T(n)=2T(n-1)+1
    exponential_sequence = [5]
    for _ in range(1, 9):
        exponential_sequence.append(2 * exponential_sequence[-1] + 1)

    print_comparison(
        "Iteration: T(n) = 2T(n-1) + 1",
        exponential_sequence,
        lambda n: exponential_closed_form(n, 5),
    )

    # Summation form from iteration.
    triangular_sequence = [2]
    for n in range(1, 9):
        triangular_sequence.append(triangular_sequence[-1] + n)

    print_comparison(
        "Iteration with variable forcing: T(n) = T(n-1) + n",
        triangular_sequence,
        lambda n: triangular_closed_form(n, 2),
    )

    # First-order formula verification.
    print("\nFirst-order closed-form verification")
    print("-----------------------------------")
    for a, b, initial in [(2, 3, 5), (1, 7, 4), (-1, 6, 2)]:
        valid = verify_first_order_formula(a, b, initial)
        print(
            f"T(n)={a}T(n-1)+{b}, T(0)={initial}: "
            f"{'verified' if valid else 'FAILED'}"
        )
        assert valid

    # Characteristic roots for Fibonacci.
    print("\nCharacteristic equation: Fibonacci")
    print("----------------------------------")
    roots = quadratic_roots(Fraction(1), Fraction(-1), Fraction(-1))
    print(f"Characteristic roots: {roots[0]} and {roots[1]}")

    fib = fibonacci_values(12)
    print(f"Recurrence values: {fib}")

    for n, value in enumerate(fib):
        exact_from_formula = fibonacci_closed_form(n)
        assert isclose(value, exact_from_formula, rel_tol=1e-10, abs_tol=1e-10)

    print("Closed form matches all displayed Fibonacci values.")

    # Distinct-root solution using a recurrence with integer roots.
    #
    # T(n)=5T(n-1)-6T(n-2)
    # characteristic equation:
    # r^2-5r+6=(r-2)(r-3)
    #
    # Let T(0)=1 and T(1)=4.
    # T(n)=C1*2^n+C2*3^n.
    #
    c1, c2 = solve_distinct_root_coefficients(
        Fraction(2), Fraction(3), Fraction(1), Fraction(4)
    )

    print("\nDistinct characteristic roots")
    print("----------------------------")
    print(f"C1 = {c1}, C2 = {c2}")

    distinct_values = [1, 4]
    for n in range(2, 9):
        distinct_values.append(
            5 * distinct_values[-1] - 6 * distinct_values[-2]
        )

    for n, value in enumerate(distinct_values):
        formula_value = distinct_root_solution(
            n, Fraction(2), Fraction(3), Fraction(1), Fraction(4)
        )
        assert value == formula_value

    print(f"Validated sequence: {distinct_values}")

    # Repeated root.
    repeated_values = repeated_root_recurrence_values(2, 8, 8)

    print("\nRepeated characteristic root")
    print("----------------------------")
    print("T(n) = 4T(n-1) - 4T(n-2)")
    print("Characteristic equation: (r-2)^2 = 0")
    print("General form: T(n) = (C1 + C2*n) * 2^n")
    print(f"Sequence: {repeated_values}")

    for n, value in enumerate(repeated_values):
        formula_value = repeated_root_solution(
            n, Fraction(2), Fraction(2), Fraction(8)
        )
        assert value == formula_value

    # Non-homogeneous recurrence.
    nonhomogeneous = nonhomogeneous_values(
        initial=5,
        coefficient=2,
        forcing=3,
        count=9,
    )

    print("\nNon-homogeneous recurrence")
    print("--------------------------")
    print("T(n) = 2T(n-1) + 3")
    print(f"Sequence: {nonhomogeneous}")

    for n, value in enumerate(nonhomogeneous):
        assert value == nonhomogeneous_closed_form(n, 5, 2, 3)

    # Polynomial forcing.
    square_values = [7]
    for n in range(1, 9):
        square_values.append(square_forcing_recurrence(n, square_values))

    print("\nPolynomial forcing")
    print("------------------")
    print("T(n) = T(n-1) + n^2")
    print(f"Sequence: {square_values}")

    for n, value in enumerate(square_values):
        assert value == square_forcing_closed_form(n, 7)

    # Validation of a second-order recurrence.
    valid, errors = validate_second_order(
        [0, 1, 1, 2, 3, 5, 8, 13],
        p=1,
        q=1,
    )

    print("\nRecurrence validation")
    print("---------------------")
    print(f"Valid Fibonacci sequence: {valid}")
    assert valid and not errors

    invalid, errors = validate_second_order(
        [0, 1, 1, 2, 99, 5],
        p=1,
        q=1,
    )

    print(f"Invalid sequence detected: {not invalid}")
    print(f"Validation errors: {errors}")
    assert not invalid

    # Halving recurrence.
    print("\nHalving recurrence")
    print("------------------")
    for n in [0, 1, 2, 8, 100, 1024, 1000000]:
        print(f"n={n:<8} T(n)=T(floor(n/2))+1 -> {halving_steps(n)}")

    # Complexity comparison.
    print("\nRecurrence evaluation strategies")
    print("--------------------------------")
    print(f"Naive Fibonacci F(10): {naive_fibonacci(10)}")
    print(f"Memoized Fibonacci F(40): {memoized_fibonacci(40)}")
    print(f"Matrix Fibonacci F(100): {fibonacci_logarithmic(100)}")

    # Matrix implementation agrees with iterative dynamic programming.
    fib_100 = fibonacci_values(101)[100]
    assert fibonacci_logarithmic(100) == fib_100

    print("Matrix exponentiation agrees with iterative Fibonacci evaluation.")

    # Expansion examples.
    print("\nRepeated substitution patterns")
    print("------------------------------")
    for step in show_first_order_expansion(2, 3, levels=4):
        print(f"Level {step.level}: {step.expression}")

    # Important conceptual checks.
    print("\nKey mathematical checks")
    print("-----------------------")
    assert first_order_closed_form(0, 2, 3, 5) == 5
    assert first_order_closed_form(1, 2, 3, 5) == 13
    assert repeated_root_solution(0, Fraction(2), Fraction(2), Fraction(8)) == 2
    assert repeated_root_solution(1, Fraction(2), Fraction(2), Fraction(8)) == 8

    print("Base cases and first recurrence transitions verified.")
    print("All executable recurrence demonstrations completed successfully.")


if __name__ == "__main__":
    main()
