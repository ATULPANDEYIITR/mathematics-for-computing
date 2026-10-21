#!/usr/bin/env python3
"""
Topic: Number Theory Fundamentals
Focus: divisibility, primes, composites, factors, and greatest common divisor.

The program builds these ideas progressively through executable functions and a
small command-line-style case study. It uses only the Python standard library.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import isqrt
from typing import Iterable


class NumberTheoryError(ValueError):
    """Raised when a number-theoretic operation receives invalid input."""


def validate_integer(n: int, *, name: str = "n") -> None:
    if isinstance(n, bool) or not isinstance(n, int):
        raise NumberTheoryError(f"{name} must be an integer.")


def validate_positive_integer(n: int, *, name: str = "n") -> None:
    validate_integer(n, name=name)
    if n <= 0:
        raise NumberTheoryError(f"{name} must be positive.")


def divides(a: int, b: int) -> bool:
    """Return True exactly when a divides b."""
    validate_integer(a, name="a")
    validate_integer(b, name="b")
    if a == 0:
        raise NumberTheoryError("Zero cannot be used as a divisor.")
    return b % a == 0


def divisors(n: int) -> list[int]:
    """
    Return all positive divisors of n in ascending order.

    Only candidates through sqrt(n) are tested. Each divisor found below the
    square root contributes a paired divisor above it.
    """
    validate_positive_integer(n)

    result: list[int] = []
    for candidate in range(1, isqrt(n) + 1):
        if n % candidate == 0:
            result.append(candidate)
            paired = n // candidate
            if paired != candidate:
                result.append(paired)

    return sorted(result)


def is_prime(n: int) -> bool:
    """
    Determine whether n is prime.

    A prime has exactly two positive divisors: 1 and itself.
    Testing through sqrt(n) is sufficient because any composite n has a
    factor no greater than sqrt(n).
    """
    validate_integer(n)

    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False

    limit = isqrt(n)
    candidate = 3
    while candidate <= limit:
        if n % candidate == 0:
            return False
        candidate += 2

    return True


def is_composite(n: int) -> bool:
    validate_positive_integer(n)
    return n > 1 and not is_prime(n)


def prime_factors(n: int) -> dict[int, int]:
    """
    Return the prime factorization as {prime: exponent}.

    Trial division stops as soon as the remaining value is prime.
    """
    validate_positive_integer(n)

    factors: dict[int, int] = {}
    remaining = n

    while remaining % 2 == 0 and remaining > 1:
        factors[2] = factors.get(2, 0) + 1
        remaining //= 2

    candidate = 3
    while candidate * candidate <= remaining:
        while remaining % candidate == 0:
            factors[candidate] = factors.get(candidate, 0) + 1
            remaining //= candidate
        candidate += 2

    if remaining > 1:
        factors[remaining] = factors.get(remaining, 0) + 1

    return factors


def gcd_euclid(a: int, b: int) -> int:
    """
    Compute gcd(a, b) with Euclid's algorithm.

    gcd(0, 0) is intentionally rejected because there is no unique greatest
    positive common divisor for that pair.
    """
    validate_integer(a, name="a")
    validate_integer(b, name="b")

    a, b = abs(a), abs(b)
    if a == 0 and b == 0:
        raise NumberTheoryError("gcd(0, 0) is undefined.")

    while b:
        a, b = b, a % b

    return a


def gcd_many(values: Iterable[int]) -> int:
    values = list(values)
    if not values:
        raise NumberTheoryError("At least one integer is required.")

    for value in values:
        validate_integer(value, name="value")

    result = 0
    for value in values:
        result = gcd_euclid(result, value)

    return result


def lcm(a: int, b: int) -> int:
    validate_integer(a, name="a")
    validate_integer(b, name="b")

    if a == 0 or b == 0:
        return 0

    return abs(a // gcd_euclid(a, b) * b)


def are_coprime(a: int, b: int) -> bool:
    return gcd_euclid(a, b) == 1


def classify(n: int) -> str:
    validate_integer(n)

    if n < 0:
        return "negative integer"
    if n == 0:
        return "zero"
    if n == 1:
        return "unit"
    if is_prime(n):
        return "prime"
    return "composite"


@dataclass(frozen=True)
class NumberProfile:
    value: int
    classification: str
    factors: tuple[int, ...]
    prime_factorization: tuple[tuple[int, int], ...]


def profile(n: int) -> NumberProfile:
    validate_positive_integer(n)

    factorization = prime_factors(n)
    return NumberProfile(
        value=n,
        classification=classify(n),
        factors=tuple(divisors(n)),
        prime_factorization=tuple(sorted(factorization.items())),
    )


def demonstrate() -> None:
    print("NUMBER THEORY FUNDAMENTALS")
    print("=" * 72)

    examples = [1, 2, 12, 17, 36, 97, 100]
    for n in examples:
        p = profile(n)
        factorization = " × ".join(
            f"{prime}^{exponent}" if exponent > 1 else str(prime)
            for prime, exponent in p.prime_factorization
        )
        print(f"{n:>3}: {p.classification:<10} divisors={list(p.factors)}")
        print(f"     prime factorization: {factorization}")

    print("\nDIVISIBILITY")
    print(f"3 divides 36: {divides(3, 36)}")
    print(f"5 divides 36: {divides(5, 36)}")

    print("\nEUCLID'S ALGORITHM")
    pairs = [(252, 105), (48, 18), (101, 23), (-84, 30)]
    for a, b in pairs:
        print(f"gcd({a}, {b}) = {gcd_euclid(a, b)}")

    print("\nCOMMON-DIVISOR APPLICATION")
    values = [84, 126, 210]
    common = gcd_many(values)
    print(f"Values: {values}")
    print(f"Greatest common divisor: {common}")
    print(f"Can divide all values into groups of size {common}: "
          f"{[value // common for value in values]}")

    print("\nCOPRIMALITY AND LCM")
    print(f"gcd(35, 64) = {gcd_euclid(35, 64)}")
    print(f"35 and 64 are coprime: {are_coprime(35, 64)}")
    print(f"lcm(12, 18) = {lcm(12, 18)}")

    print("\nEDGE-CASE VALIDATION")
    invalid_operations = [
        ("divides(0, 10)", lambda: divides(0, 10)),
        ("divisors(0)", lambda: divisors(0)),
        ("prime_factors(-8)", lambda: prime_factors(-8)),
        ("gcd(0, 0)", lambda: gcd_euclid(0, 0)),
    ]

    for description, operation in invalid_operations:
        try:
            operation()
        except NumberTheoryError as exc:
            print(f"{description}: rejected safely -> {exc}")

    # Security/production note: arbitrary-size Python integers avoid ordinary
    # machine integer overflow, but factorization can still become expensive.
    large_example = 600851475143
    print("\nLARGER FACTORIZATION")
    print(f"{large_example} -> {prime_factors(large_example)}")


if __name__ == "__main__":
    demonstrate()
