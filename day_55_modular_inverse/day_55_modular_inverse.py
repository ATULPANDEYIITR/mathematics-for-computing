#!/usr/bin/env python3
"""Modular inverses using the extended Euclidean algorithm."""

from dataclasses import dataclass
from math import gcd
from typing import Optional


class ModularInverseError(ValueError):
    """Raised when a modular inverse does not exist or input is invalid."""


@dataclass(frozen=True)
class BezoutResult:
    gcd_value: int
    x: int
    y: int


def validate_modulus(modulus: int) -> None:
    if isinstance(modulus, bool) or not isinstance(modulus, int):
        raise ModularInverseError("Modulus must be an integer.")
    if modulus <= 1:
        raise ModularInverseError("Modulus must be greater than 1.")


def extended_gcd(a: int, b: int) -> BezoutResult:
    """Return g, x, y such that a*x + b*y = g = gcd(a, b)."""
    if isinstance(a, bool) or isinstance(b, bool):
        raise ModularInverseError("Inputs must be integers.")
    if not isinstance(a, int) or not isinstance(b, int):
        raise ModularInverseError("Inputs must be integers.")

    old_r, r = abs(a), abs(b)
    old_s, s = 1, 0
    old_t, t = 0, 1

    while r:
        quotient = old_r // r
        old_r, r = r, old_r - quotient * r
        old_s, s = s, old_s - quotient * s
        old_t, t = t, old_t - quotient * t

    # Restore signs so the identity holds for negative inputs.
    x = old_s if a >= 0 else -old_s
    y = old_t if b >= 0 else -old_t
    return BezoutResult(old_r, x, y)


def modular_inverse(a: int, modulus: int) -> int:
    """Find x in [0, modulus) such that a*x is congruent to 1."""
    validate_modulus(modulus)

    if isinstance(a, bool) or not isinstance(a, int):
        raise ModularInverseError("Value must be an integer.")

    result = extended_gcd(a, modulus)
    if result.gcd_value != 1:
        raise ModularInverseError(
            f"No inverse exists: gcd({a}, {modulus}) = "
            f"{result.gcd_value}."
        )

    return result.x % modulus


def inverse_or_none(a: int, modulus: int) -> Optional[int]:
    """Return None if an inverse does not exist."""
    try:
        return modular_inverse(a, modulus)
    except ModularInverseError:
        return None


def modular_power(base: int, exponent: int, modulus: int) -> int:
    """Calculate base**exponent modulo modulus, including negative exponents."""
    validate_modulus(modulus)

    if isinstance(base, bool) or not isinstance(base, int):
        raise ModularInverseError("Base must be an integer.")
    if isinstance(exponent, bool) or not isinstance(exponent, int):
        raise ModularInverseError("Exponent must be an integer.")

    if exponent < 0:
        base = modular_inverse(base, modulus)
        exponent = -exponent

    return pow(base, exponent, modulus)


def demonstrate() -> None:
    examples = [
        (3, 11),
        (10, 17),
        (-3, 11),
        (7, 26),
        (6, 15),
    ]

    print("Modular inverse calculations")
    for value, modulus in examples:
        inverse = inverse_or_none(value, modulus)
        if inverse is None:
            print(f"{value} mod {modulus}: no inverse")
        else:
            print(
                f"{value} mod {modulus}: inverse={inverse}, "
                f"verification={(value * inverse) % modulus}"
            )

    print("\nNegative exponent:")
    print(f"3^(-1) mod 11 = {modular_power(3, -1, 11)}")
    print(f"3^(-2) mod 11 = {modular_power(3, -2, 11)}")

    print("\nBezout identity:")
    result = extended_gcd(30, 18)
    print(
        f"gcd={result.gcd_value}, x={result.x}, y={result.y}, "
        f"check={30 * result.x + 18 * result.y}"
    )


def run_tests() -> None:
    assert extended_gcd(30, 18).gcd_value == 6
    assert modular_inverse(3, 11) == 4
    assert modular_inverse(10, 17) == 12
    assert modular_inverse(-3, 11) == 7
    assert modular_inverse(1, 7) == 1
    assert modular_inverse(20, 7) == 6
    assert modular_power(3, -1, 11) == 4
    assert modular_power(3, -2, 11) == 5
    assert inverse_or_none(6, 15) is None

    for modulus in range(2, 30):
        for value in range(-30, 31):
            inverse = inverse_or_none(value, modulus)
            if gcd(value, modulus) == 1:
                assert inverse is not None
                assert (value * inverse) % modulus == 1
                assert 0 <= inverse < modulus
            else:
                assert inverse is None

    for invalid_modulus in (0, 1, -5):
        try:
            modular_inverse(3, invalid_modulus)
        except ModularInverseError:
            pass
        else:
            raise AssertionError("Invalid modulus was accepted.")

    print("All tests passed.")


if __name__ == "__main__":
    run_tests()
    demonstrate()
