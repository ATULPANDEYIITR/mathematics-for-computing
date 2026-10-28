from __future__ import annotations

from dataclasses import dataclass
from math import isqrt
from random import randrange
from typing import Iterable


class NumberTheoryError(ValueError):
    """Raised when a number-theory operation receives invalid input."""


def validate_modulus(modulus: int) -> None:
    if not isinstance(modulus, int):
        raise NumberTheoryError("Modulus must be an integer.")
    if modulus <= 0:
        raise NumberTheoryError("Modulus must be positive.")


def gcd(a: int, b: int) -> int:
    """Compute the greatest common divisor using Euclid's algorithm."""
    a, b = abs(a), abs(b)
    while b:
        a, b = b, a % b
    return a


def extended_gcd(a: int, b: int) -> tuple[int, int, int]:
    """
    Return (g, x, y) such that ax + by = g = gcd(a, b).
    """
    old_r, r = a, b
    old_x, x = 1, 0
    old_y, y = 0, 1

    while r:
        q = old_r // r
        old_r, r = r, old_r - q * r
        old_x, x = x, old_x - q * x
        old_y, y = y, old_y - q * y

    if old_r < 0:
        return -old_r, -old_x, -old_y
    return old_r, old_x, old_y


def modular_inverse(a: int, modulus: int) -> int:
    """Return a^-1 mod modulus when the inverse exists."""
    validate_modulus(modulus)
    g, x, _ = extended_gcd(a, modulus)
    if g != 1:
        raise NumberTheoryError(
            f"{a} has no modular inverse modulo {modulus}."
        )
    return x % modulus


def mod_pow(base: int, exponent: int, modulus: int) -> int:
    """
    Binary exponentiation.

    Supports non-negative exponents and avoids constructing base**exponent
    directly, keeping the number of modular multiplications logarithmic.
    """
    validate_modulus(modulus)

    if exponent < 0:
        raise NumberTheoryError("Exponent must be non-negative.")

    result = 1 % modulus
    base %= modulus

    while exponent:
        if exponent & 1:
            result = (result * base) % modulus
        base = (base * base) % modulus
        exponent >>= 1

    return result


def sieve(limit: int) -> list[bool]:
    """
    Return a primality table for [0, limit].
    sieve[i] is True exactly when i is prime.
    """
    if limit < 0:
        raise NumberTheoryError("Sieve limit cannot be negative.")

    prime = [True] * (limit + 1)

    if limit >= 0:
        prime[0] = False
    if limit >= 1:
        prime[1] = False

    for p in range(2, isqrt(limit) + 1):
        if prime[p]:
            start = p * p
            prime[start : limit + 1 : p] = [False] * (
                ((limit - start) // p) + 1
            )

    return prime


def primes_up_to(limit: int) -> list[int]:
    return [i for i, value in enumerate(sieve(limit)) if value]


def trial_division_is_prime(n: int) -> bool:
    """Deterministic primality test suitable for ordinary-sized integers."""
    if n < 2:
        return False
    if n in (2, 3):
        return True
    if n % 2 == 0:
        return False

    divisor = 3
    while divisor * divisor <= n:
        if n % divisor == 0:
            return False
        divisor += 2

    return True


def miller_rabin_is_prime(n: int, rounds: int = 12) -> bool:
    """
    Probabilistic Miller-Rabin primality test.

    For arbitrary Python integers this is a probable-prime test because
    the witness set is sampled. It is substantially faster than trial
    division for large candidates.
    """
    if not isinstance(n, int):
        return False
    if n < 2:
        return False

    small_primes = (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37)
    for p in small_primes:
        if n == p:
            return True
        if n % p == 0:
            return False

    # n - 1 = d * 2^s with d odd.
    d = n - 1
    s = 0
    while d % 2 == 0:
        d //= 2
        s += 1

    for _ in range(rounds):
        a = randrange(2, n - 1)
        x = mod_pow(a, d, n)

        if x in (1, n - 1):
            continue

        for _ in range(s - 1):
            x = (x * x) % n
            if x == n - 1:
                break
        else:
            return False

    return True


def factorize(n: int) -> dict[int, int]:
    """
    Return the prime factorization of a positive integer.

    Example:
        360 -> {2: 3, 3: 2, 5: 1}
    """
    if n <= 0:
        raise NumberTheoryError("Factorization requires a positive integer.")

    factors: dict[int, int] = {}
    remaining = n

    count = 0
    while remaining % 2 == 0 and remaining > 1:
        count += 1
        remaining //= 2
    if count:
        factors[2] = count

    divisor = 3
    while divisor * divisor <= remaining:
        count = 0
        while remaining % divisor == 0:
            count += 1
            remaining //= divisor
        if count:
            factors[divisor] = count
        divisor += 2

    if remaining > 1:
        factors[remaining] = factors.get(remaining, 0) + 1

    return factors


def euler_totient(n: int) -> int:
    """Compute Euler's phi(n) from the distinct prime factors."""
    if n <= 0:
        raise NumberTheoryError("Totient requires a positive integer.")

    result = n
    for p in factorize(n):
        result -= result // p
    return result


def chinese_remainder_theorem(
    residues: Iterable[int],
    moduli: Iterable[int],
) -> int:
    """
    Solve x = residues[i] (mod moduli[i]) for pairwise-coprime moduli.
    Returns the smallest non-negative solution.
    """
    residues = list(residues)
    moduli = list(moduli)

    if not residues or len(residues) != len(moduli):
        raise NumberTheoryError("Residues and moduli must have equal non-zero length.")

    for modulus in moduli:
        validate_modulus(modulus)

    for i in range(len(moduli)):
        for j in range(i + 1, len(moduli)):
            if gcd(moduli[i], moduli[j]) != 1:
                raise NumberTheoryError("Moduli must be pairwise coprime.")

    total_modulus = 1
    for modulus in moduli:
        total_modulus *= modulus

    result = 0

    for residue, modulus in zip(residues, moduli):
        partial = total_modulus // modulus
        inverse = modular_inverse(partial, modulus)
        result += (residue % modulus) * partial * inverse

    return result % total_modulus


@dataclass(frozen=True)
class ModularArithmetic:
    modulus: int

    def __post_init__(self) -> None:
        validate_modulus(self.modulus)

    def add(self, a: int, b: int) -> int:
        return (a + b) % self.modulus

    def multiply(self, a: int, b: int) -> int:
        return (a * b) % self.modulus

    def power(self, base: int, exponent: int) -> int:
        return mod_pow(base, exponent, self.modulus)

    def inverse(self, value: int) -> int:
        return modular_inverse(value, self.modulus)


def run_examples() -> None:
    print("NUMBER THEORY ALGORITHMS")
    print("=" * 70)

    print("\n1. Greatest common divisor")
    print("gcd(252, 105) =", gcd(252, 105))

    print("\n2. Extended Euclidean algorithm")
    g, x, y = extended_gcd(240, 46)
    print(f"gcd={g}, x={x}, y={y}")
    assert 240 * x + 46 * y == g

    print("\n3. Fast modular exponentiation")
    print("3^100 mod 13 =", mod_pow(3, 100, 13))
    assert mod_pow(3, 100, 13) == pow(3, 100, 13)

    print("\n4. Primes up to 50")
    print(primes_up_to(50))

    print("\n5. Primality testing")
    for value in (1, 2, 17, 97, 100, 104729):
        print(
            f"{value}: "
            f"trial={trial_division_is_prime(value)}, "
            f"miller_rabin={miller_rabin_is_prime(value)}"
        )

    print("\n6. Prime factorization")
    print("360 =", factorize(360))

    print("\n7. Euler totient")
    print("phi(36) =", euler_totient(36))

    print("\n8. Modular inverse")
    inverse = modular_inverse(7, 26)
    print("7^-1 mod 26 =", inverse)
    assert (7 * inverse) % 26 == 1

    print("\n9. Chinese remainder theorem")
    crt = chinese_remainder_theorem(
        residues=[2, 3, 2],
        moduli=[3, 5, 7],
    )
    print("x = 2 mod 3, x = 3 mod 5, x = 2 mod 7")
    print("smallest x =", crt)
    assert crt == 23

    print("\n10. Modular arithmetic object")
    arithmetic = ModularArithmetic(17)
    print("(13 + 11) mod 17 =", arithmetic.add(13, 11))
    print("(13 * 11) mod 17 =", arithmetic.multiply(13, 11))
    print("13^20 mod 17 =", arithmetic.power(13, 20))
    print("13^-1 mod 17 =", arithmetic.inverse(13))

    print("\n11. Edge-case validation")
    invalid_cases = [
        lambda: mod_pow(2, -1, 7),
        lambda: modular_inverse(6, 15),
        lambda: ModularArithmetic(0),
        lambda: chinese_remainder_theorem([1, 2], [4, 6]),
    ]

    for operation in invalid_cases:
        try:
            operation()
        except NumberTheoryError as exc:
            print("Rejected:", exc)
        else:
            raise AssertionError("Invalid input was not rejected.")

    print("\nAll executable checks passed.")


if __name__ == "__main__":
    run_examples()
