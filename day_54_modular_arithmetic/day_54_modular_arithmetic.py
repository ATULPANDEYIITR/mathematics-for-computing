#!/usr/bin/env python3
"""Modular arithmetic: congruences, addition, multiplication, and powers."""

from dataclasses import dataclass
from typing import Iterable


class ModularArithmeticError(ValueError):
    """Raised when a modular operation has invalid parameters."""


def validate_modulus(modulus: int) -> None:
    if isinstance(modulus, bool) or not isinstance(modulus, int):
        raise ModularArithmeticError("Modulus must be an integer.")
    if modulus <= 0:
        raise ModularArithmeticError("Modulus must be positive.")


def normalize(value: int, modulus: int) -> int:
    validate_modulus(modulus)
    if isinstance(value, bool) or not isinstance(value, int):
        raise ModularArithmeticError("Value must be an integer.")
    return value % modulus


def congruent(a: int, b: int, modulus: int) -> bool:
    """Return whether a and b belong to the same residue class."""
    return normalize(a - b, modulus) == 0


def modular_add(a: int, b: int, modulus: int) -> int:
    """Compute addition in Z/modulus Z."""
    return (normalize(a, modulus) + normalize(b, modulus)) % modulus


def modular_multiply(a: int, b: int, modulus: int) -> int:
    """Compute multiplication without constructing an unbounded product."""
    validate_modulus(modulus)
    a = normalize(a, modulus)
    b = normalize(b, modulus)
    result = 0

    # Repeated doubling keeps intermediate values bounded by the modulus.
    while b:
        if b & 1:
            result = (result + a) % modulus
        a = (a + a) % modulus
        b >>= 1

    return result


def modular_power(base: int, exponent: int, modulus: int) -> int:
    """Binary exponentiation; negative exponents require a modular inverse."""
    validate_modulus(modulus)
    if isinstance(exponent, bool) or not isinstance(exponent, int):
        raise ModularArithmeticError("Exponent must be an integer.")
    if exponent < 0:
        base = modular_inverse(base, modulus)
        exponent = -exponent

    base = normalize(base, modulus)
    result = 1 % modulus

    while exponent:
        if exponent & 1:
            result = modular_multiply(result, base, modulus)
        base = modular_multiply(base, base, modulus)
        exponent >>= 1

    return result


def extended_gcd(a: int, b: int) -> tuple[int, int, int]:
    """Return (g, x, y), satisfying ax + by = g = gcd(a, b)."""
    old_r, r = a, b
    old_s, s = 1, 0
    old_t, t = 0, 1

    while r:
        quotient = old_r // r
        old_r, r = r, old_r - quotient * r
        old_s, s = s, old_s - quotient * s
        old_t, t = t, old_t - quotient * t

    if old_r < 0:
        return -old_r, -old_s, -old_t
    return old_r, old_s, old_t


def modular_inverse(value: int, modulus: int) -> int:
    """Find x such that value*x is congruent to 1 modulo modulus."""
    validate_modulus(modulus)
    if modulus == 1:
        raise ModularArithmeticError(
            "The trivial ring modulo 1 has no multiplicative identity distinct from zero."
        )

    value = normalize(value, modulus)
    gcd, coefficient, _ = extended_gcd(value, modulus)

    if gcd != 1:
        raise ModularArithmeticError(
            f"No inverse exists: gcd({value}, {modulus}) = {gcd}."
        )

    return coefficient % modulus


def modular_sum(values: Iterable[int], modulus: int) -> int:
    """Accumulate a sequence while reducing after every addition."""
    validate_modulus(modulus)
    result = 0
    for value in values:
        result = modular_add(result, value, modulus)
    return result


@dataclass(frozen=True)
class Residue:
    """A normalized element of the ring Z/nZ."""

    value: int
    modulus: int

    def __post_init__(self) -> None:
        validate_modulus(self.modulus)
        if isinstance(self.value, bool) or not isinstance(self.value, int):
            raise ModularArithmeticError("Residue value must be an integer.")
        object.__setattr__(self, "value", self.value % self.modulus)

    def _check(self, other: "Residue") -> None:
        if not isinstance(other, Residue):
            raise TypeError("Expected another Residue.")
        if self.modulus != other.modulus:
            raise ModularArithmeticError("Residues must use the same modulus.")

    def __add__(self, other: "Residue") -> "Residue":
        self._check(other)
        return Residue(self.value + other.value, self.modulus)

    def __mul__(self, other: "Residue") -> "Residue":
        self._check(other)
        return Residue(
            modular_multiply(self.value, other.value, self.modulus),
            self.modulus,
        )

    def __pow__(self, exponent: int) -> "Residue":
        return Residue(
            modular_power(self.value, exponent, self.modulus),
            self.modulus,
        )

    def __str__(self) -> str:
        return f"{self.value} (mod {self.modulus})"


def run_tests() -> None:
    assert normalize(-17, 5) == 3
    assert congruent(17, 2, 5)
    assert not congruent(17, 3, 5)
    assert modular_add(-7, 12, 5) == 0
    assert modular_multiply(123456, 789012, 97) == (
        123456 * 789012 % 97
    )
    assert modular_power(3, 100, 7) == pow(3, 100, 7)
    assert modular_power(3, -1, 11) == 4
    assert modular_inverse(-3, 11) == 7
    assert modular_sum([1, -2, 8, 14], 5) == 1
    assert str(Residue(-2, 7)) == "5 (mod 7)"
    assert Residue(3, 7) * Residue(5, 7) == Residue(1, 7)

    for modulus in range(2, 20):
        for a in range(-10, 11):
            assert modular_power(a, 0, modulus) == 1
            for b in range(-5, 6):
                assert modular_add(a, b, modulus) == (a + b) % modulus
                assert modular_multiply(a, b, modulus) == (a * b) % modulus

    for invalid_modulus in (0, -1):
        try:
            modular_add(1, 2, invalid_modulus)
        except ModularArithmeticError:
            pass
        else:
            raise AssertionError("Invalid modulus was accepted.")

    for value, modulus in ((6, 9), (0, 7)):
        try:
            modular_inverse(value, modulus)
        except ModularArithmeticError:
            pass
        else:
            raise AssertionError("Non-invertible value was accepted.")

    print("All modular arithmetic tests passed.")


def main() -> None:
    run_tests()

    modulus = 17
    a, b = 123, -45

    print(f"Modulus: {modulus}")
    print(f"Normalized values: {normalize(a, modulus)}, "
          f"{normalize(b, modulus)}")
    print(f"Congruent: {congruent(a, b, modulus)}")
    print(f"Addition: {a} + {b} = {modular_add(a, b, modulus)} mod {modulus}")
    print(f"Multiplication: {a} * {b} = "
          f"{modular_multiply(a, b, modulus)} mod {modulus}")
    print(f"Power: 3^100 mod 17 = {modular_power(3, 100, modulus)}")
    print(f"Inverse: 5^(-1) mod 17 = {modular_inverse(5, modulus)}")


if __name__ == "__main__":
    main()
