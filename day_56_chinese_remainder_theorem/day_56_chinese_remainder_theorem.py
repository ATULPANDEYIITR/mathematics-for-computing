from __future__ import annotations

from dataclasses import dataclass
from math import gcd, prod
from typing import Iterable


class CRTError(ValueError):
    """Raised when a congruence system cannot be solved under the requested rules."""


@dataclass(frozen=True)
class Congruence:
    remainder: int
    modulus: int

    def __post_init__(self) -> None:
        if self.modulus <= 1:
            raise CRTError("Each modulus must be greater than 1.")
        object.__setattr__(self, "remainder", self.remainder % self.modulus)


@dataclass(frozen=True)
class CRTResult:
    remainder: int
    modulus: int

    def contains(self, value: int) -> bool:
        return value % self.modulus == self.remainder


def extended_gcd(a: int, b: int) -> tuple[int, int, int]:
    """Return gcd(a,b), x, y such that ax + by = gcd(a,b)."""
    old_r, r = abs(a), abs(b)
    old_s, s = 1, 0
    old_t, t = 0, 1

    while r:
        q = old_r // r
        old_r, r = r, old_r - q * r
        old_s, s = s, old_s - q * s
        old_t, t = t, old_t - q * t

    x = old_s if a >= 0 else -old_s
    y = old_t if b >= 0 else -old_t
    return old_r, x, y


def mod_inverse(a: int, modulus: int) -> int:
    """Return a^-1 modulo modulus when it exists."""
    g, x, _ = extended_gcd(a, modulus)
    if g != 1:
        raise CRTError(f"{a} has no inverse modulo {modulus}.")
    return x % modulus


def pairwise_coprime(congruences: Iterable[Congruence]) -> bool:
    items = list(congruences)
    return all(
        gcd(items[i].modulus, items[j].modulus) == 1
        for i in range(len(items))
        for j in range(i + 1, len(items))
    )


def solve_coprime_crt(congruences: list[Congruence]) -> CRTResult:
    """
    Solve x ≡ ai (mod mi) for pairwise-coprime moduli.

    Uses x = sum(ai * Mi * yi), where Mi = M/mi and
    yi is the inverse of Mi modulo mi.
    """
    if not congruences:
        raise CRTError("At least one congruence is required.")
    if not pairwise_coprime(congruences):
        raise CRTError("The direct CRT construction requires pairwise-coprime moduli.")

    M = prod(c.modulus for c in congruences)
    x = 0

    for c in congruences:
        partial = M // c.modulus
        inverse = mod_inverse(partial, c.modulus)
        x += c.remainder * partial * inverse

    return CRTResult(x % M, M)


def merge_congruences(a: Congruence, b: Congruence) -> CRTResult:
    """
    Merge two congruences, allowing non-coprime moduli.

    A solution exists iff:
        a.remainder == b.remainder (mod gcd(a.modulus,b.modulus)).
    """
    m1, m2 = a.modulus, b.modulus
    g = gcd(m1, m2)

    difference = b.remainder - a.remainder
    if difference % g != 0:
        raise CRTError("The congruences are inconsistent.")

    m1_reduced = m1 // g
    m2_reduced = m2 // g
    rhs = difference // g

    k = (rhs * mod_inverse(m1_reduced % m2_reduced, m2_reduced)) % m2_reduced
    lcm = m1 * m2_reduced
    x = (a.remainder + m1 * k) % lcm

    return CRTResult(x, lcm)


def solve_general_crt(congruences: list[Congruence]) -> CRTResult:
    """Solve a compatible system even when moduli are not pairwise coprime."""
    if not congruences:
        raise CRTError("At least one congruence is required.")

    result = CRTResult(congruences[0].remainder, congruences[0].modulus)

    for c in congruences[1:]:
        result = CRTResult(*merge_congruences(
            Congruence(result.remainder, result.modulus), c
        ).__dict__.values())

    return result


def verify(result: CRTResult, congruences: Iterable[Congruence]) -> bool:
    return all(result.contains(c.remainder) for c in congruences)


def solve_linear_congruence(a: int, b: int, modulus: int) -> list[int]:
    """
    Solve ax ≡ b (mod modulus).

    If d=gcd(a,m), a solution exists only when d divides b.
    There are d distinct solutions modulo m.
    """
    if modulus <= 1:
        raise CRTError("Modulus must be greater than 1.")

    d = gcd(a, modulus)
    if b % d != 0:
        return []

    a1 = a // d
    b1 = b // d
    m1 = modulus // d
    base = (b1 * mod_inverse(a1 % m1, m1)) % m1

    return sorted((base + k * m1) % modulus for k in range(d))


def demonstrate_rsa_style_recombination() -> None:
    """
    CRT can accelerate RSA private operations.

    These small values are educational only, not cryptographically secure.
    """
    p, q = 61, 53
    n = p * q
    ciphertext = 2790
    private_exponent = 2753

    dp = private_exponent % (p - 1)
    dq = private_exponent % (q - 1)

    m_p = pow(ciphertext, dp, p)
    m_q = pow(ciphertext, dq, q)

    combined = solve_coprime_crt([
        Congruence(m_p, p),
        Congruence(m_q, q),
    ])

    direct = pow(ciphertext, private_exponent, n)

    assert combined.remainder == direct
    print("RSA-style CRT recombination:")
    print(f"  modulus n = {n}")
    print(f"  direct result = {direct}")
    print(f"  CRT result = {combined.remainder}")


def main() -> None:
    system = [
        Congruence(2, 3),
        Congruence(3, 5),
        Congruence(2, 7),
    ]

    result = solve_coprime_crt(system)
    assert result.remainder == 23
    assert verify(result, system)
    print("Pairwise-coprime CRT:")
    print(f"  x ≡ {result.remainder} (mod {result.modulus})")

    compatible = [
        Congruence(2, 6),
        Congruence(8, 9),
    ]
    general = solve_general_crt(compatible)
    assert general.remainder == 44
    assert verify(general, compatible)
    print("\nGeneralized CRT:")
    print(f"  x ≡ {general.remainder} (mod {general.modulus})")

    inconsistent = [
        Congruence(1, 4),
        Congruence(2, 6),
    ]
    try:
        solve_general_crt(inconsistent)
    except CRTError as exc:
        print(f"\nExpected inconsistency: {exc}")

    solutions = solve_linear_congruence(14, 30, 100)
    print("\nLinear congruence 14x ≡ 30 (mod 100):")
    print(f"  solutions = {solutions}")
    assert all((14 * x - 30) % 100 == 0 for x in solutions)

    demonstrate_rsa_style_recombination()

    # Input validation and large-integer behavior use Python's arbitrary precision.
    large = solve_coprime_crt([
        Congruence(12345678901234567890, 1000000007),
        Congruence(98765432109876543210, 1000000009),
    ])
    assert verify(large, [
        Congruence(12345678901234567890, 1000000007),
        Congruence(98765432109876543210, 1000000009),
    ])
    print("\nLarge-integer verification: passed")


if __name__ == "__main__":
    main()
