#!/usr/bin/env python3
"""
Euclidean Algorithm Case Study

Models:
- Classical Euclidean algorithm for GCD
- Extended Euclidean algorithm
- Bézout identity
- Modular inverse derived from Bézout coefficients
- Linear Diophantine equations
- Repository-style batch validation and audit output

The implementation uses only the Python standard library.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import gcd
from typing import Iterable


@dataclass(frozen=True)
class ExtendedGCDResult:
    a: int
    b: int
    gcd_value: int
    coefficient_x: int
    coefficient_y: int

    @property
    def bezout_value(self) -> int:
        return self.a * self.coefficient_x + self.b * self.coefficient_y

    def is_valid(self) -> bool:
        return self.bezout_value == self.gcd_value


@dataclass(frozen=True)
class DiophantineSolution:
    x: int
    y: int
    gcd_value: int


class EuclideanAlgorithm:
    @staticmethod
    def validate_integer(value: int, name: str) -> None:
        if not isinstance(value, int) or isinstance(value, bool):
            raise TypeError(f"{name} must be an integer")

    @classmethod
    def gcd_iterative(cls, a: int, b: int) -> int:
        """Compute gcd using repeated remainder reduction."""
        cls.validate_integer(a, "a")
        cls.validate_integer(b, "b")

        a, b = abs(a), abs(b)

        while b != 0:
            a, b = b, a % b

        return a

    @classmethod
    def gcd_recursive(cls, a: int, b: int) -> int:
        """Recursive form of the Euclidean recurrence gcd(a,b)=gcd(b,a mod b)."""
        cls.validate_integer(a, "a")
        cls.validate_integer(b, "b")

        a, b = abs(a), abs(b)

        if b == 0:
            return a

        return cls.gcd_recursive(b, a % b)

    @classmethod
    def extended_gcd(cls, a: int, b: int) -> ExtendedGCDResult:
        """
        Return g, x, y satisfying:

            ax + by = g

        where g = gcd(a,b) and g >= 0.

        Iterative coefficient propagation avoids recursion-depth concerns
        for unusually large integer inputs.
        """
        cls.validate_integer(a, "a")
        cls.validate_integer(b, "b")

        original_a, original_b = a, b

        old_r, r = abs(a), abs(b)
        old_s, s = 1, 0
        old_t, t = 0, 1

        while r != 0:
            quotient = old_r // r

            old_r, r = r, old_r - quotient * r
            old_s, s = s, old_s - quotient * s
            old_t, t = t, old_t - quotient * t

        x = old_s if a >= 0 else -old_s
        y = old_t if b >= 0 else -old_t

        result = ExtendedGCDResult(
            a=original_a,
            b=original_b,
            gcd_value=old_r,
            coefficient_x=x,
            coefficient_y=y,
        )

        if not result.is_valid():
            raise ArithmeticError("Extended Euclidean invariant was violated")

        return result

    @classmethod
    def modular_inverse(cls, value: int, modulus: int) -> int:
        """
        Compute value^(-1) mod modulus.

        An inverse exists exactly when gcd(value, modulus) = 1.
        """
        cls.validate_integer(value, "value")
        cls.validate_integer(modulus, "modulus")

        if modulus <= 1:
            raise ValueError("modulus must be greater than 1")

        result = cls.extended_gcd(value, modulus)

        if result.gcd_value != 1:
            raise ValueError(
                f"{value} has no modular inverse modulo {modulus}; "
                f"gcd={result.gcd_value}"
            )

        return result.coefficient_x % modulus

    @classmethod
    def solve_linear_diophantine(
        cls, a: int, b: int, c: int
    ) -> DiophantineSolution:
        """
        Find one integer solution to:

            ax + by = c

        A solution exists iff gcd(a,b) divides c.
        """
        cls.validate_integer(a, "a")
        cls.validate_integer(b, "b")
        cls.validate_integer(c, "c")

        if a == 0 and b == 0:
            if c == 0:
                return DiophantineSolution(0, 0, 0)
            raise ValueError("No solution exists for 0x + 0y = nonzero c")

        result = cls.extended_gcd(a, b)

        if c % result.gcd_value != 0:
            raise ValueError(
                f"No integer solution because gcd({a}, {b}) "
                f"does not divide {c}"
            )

        multiplier = c // result.gcd_value

        return DiophantineSolution(
            x=result.coefficient_x * multiplier,
            y=result.coefficient_y * multiplier,
            gcd_value=result.gcd_value,
        )


def trace_euclidean_algorithm(a: int, b: int) -> list[tuple[int, int, int, int]]:
    """
    Return quotient/remainder steps.

    Each tuple contains:
        (current_a, current_b, quotient, remainder)
    """
    if not isinstance(a, int) or not isinstance(b, int):
        raise TypeError("Both inputs must be integers")

    a, b = abs(a), abs(b)
    trace: list[tuple[int, int, int, int]] = []

    while b != 0:
        quotient, remainder = divmod(a, b)
        trace.append((a, b, quotient, remainder))
        a, b = b, remainder

    return trace


def validate_batch(cases: Iterable[tuple[int, int]]) -> None:
    """Cross-check the implementation against Python's math.gcd."""
    failures: list[str] = []

    for a, b in cases:
        expected = gcd(a, b)
        actual = EuclideanAlgorithm.gcd_iterative(a, b)

        if actual != expected:
            failures.append(
                f"gcd({a}, {b}): expected {expected}, got {actual}"
            )

        extended = EuclideanAlgorithm.extended_gcd(a, b)

        if extended.gcd_value != expected:
            failures.append(
                f"extended_gcd({a}, {b}) returned "
                f"{extended.gcd_value}, expected {expected}"
            )

        if not extended.is_valid():
            failures.append(
                f"Bézout identity failed for ({a}, {b})"
            )

    if failures:
        raise AssertionError("\n".join(failures))


def demonstrate_gcd() -> None:
    pairs = [
        (252, 105),
        (1071, 462),
        (48, 18),
        (0, 42),
        (-84, 30),
        (0, 0),
    ]

    print("GCD calculations")
    print("================")

    for a, b in pairs:
        result = EuclideanAlgorithm.gcd_iterative(a, b)
        print(f"gcd({a}, {b}) = {result}")


def demonstrate_trace() -> None:
    print("\nEuclidean reduction trace")
    print("=========================")

    a, b = 1071, 462

    for left, right, quotient, remainder in trace_euclidean_algorithm(a, b):
        print(
            f"{left} = {quotient} * {right} + {remainder}"
        )


def demonstrate_bezout() -> None:
    print("\nBézout identity")
    print("===============")

    a, b = 240, 46
    result = EuclideanAlgorithm.extended_gcd(a, b)

    print(f"a = {a}")
    print(f"b = {b}")
    print(f"gcd = {result.gcd_value}")
    print(f"x = {result.coefficient_x}")
    print(f"y = {result.coefficient_y}")
    print(
        f"{a}({result.coefficient_x}) + "
        f"{b}({result.coefficient_y}) = {result.bezout_value}"
    )


def demonstrate_modular_inverse() -> None:
    print("\nModular inverse")
    print("===============")

    value, modulus = 17, 3120
    inverse = EuclideanAlgorithm.modular_inverse(value, modulus)

    print(f"{value}^(-1) mod {modulus} = {inverse}")
    print(f"Verification: ({value} * {inverse}) mod {modulus} = "
          f"{(value * inverse) % modulus}")


def demonstrate_diophantine() -> None:
    print("\nLinear Diophantine equation")
    print("===========================")

    a, b, c = 35, 15, 10
    solution = EuclideanAlgorithm.solve_linear_diophantine(a, b, c)

    print(f"Equation: {a}x + {b}y = {c}")
    print(f"x = {solution.x}")
    print(f"y = {solution.y}")
    print(f"gcd({a}, {b}) = {solution.gcd_value}")
    print(
        f"Verification: {a}({solution.x}) + "
        f"{b}({solution.y}) = {a * solution.x + b * solution.y}"
    )


def demonstrate_failures() -> None:
    print("\nFailure conditions")
    print("==================")

    failure_cases = [
        ("modular inverse", lambda: EuclideanAlgorithm.modular_inverse(6, 15)),
        (
            "Diophantine equation",
            lambda: EuclideanAlgorithm.solve_linear_diophantine(6, 10, 7),
        ),
        (
            "invalid modulus",
            lambda: EuclideanAlgorithm.modular_inverse(3, 1),
        ),
    ]

    for name, operation in failure_cases:
        try:
            operation()
        except (ValueError, TypeError) as exc:
            print(f"{name}: rejected safely -> {exc}")


def run_self_tests() -> None:
    cases = [
        (0, 0),
        (0, 1),
        (1, 0),
        (1, 1),
        (48, 18),
        (18, 48),
        (-48, 18),
        (48, -18),
        (-48, -18),
        (270, 192),
        (1071, 462),
        (2**100, 2**80),
    ]

    validate_batch(cases)

    known_inverse = EuclideanAlgorithm.modular_inverse(3, 11)
    assert known_inverse == 4
    assert (3 * known_inverse) % 11 == 1

    solution = EuclideanAlgorithm.solve_linear_diophantine(35, 15, 10)
    assert 35 * solution.x + 15 * solution.y == 10

    try:
        EuclideanAlgorithm.solve_linear_diophantine(6, 10, 7)
    except ValueError:
        pass
    else:
        raise AssertionError("Expected unsolvable Diophantine equation")

    print("\nSelf-tests: PASS")


def main() -> None:
    demonstrate_gcd()
    demonstrate_trace()
    demonstrate_bezout()
    demonstrate_modular_inverse()
    demonstrate_diophantine()
    demonstrate_failures()
    run_self_tests()


if __name__ == "__main__":
    main()
