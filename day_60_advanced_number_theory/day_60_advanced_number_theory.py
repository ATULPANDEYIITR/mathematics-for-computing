#!/usr/bin/env python3
"""
Advanced Number Theory
Quadratic residues, discrete logarithms, and computational number theory.

Algorithms:
- Modular arithmetic and extended Euclidean algorithm
- Modular multiplicative inverses
- Miller-Rabin primality testing
- Pollard Rho integer factorization
- Legendre symbols and quadratic reciprocity
- Tonelli-Shanks modular square roots
- Multiplicative order
- Baby-Step Giant-Step discrete logarithms
- Pohlig-Hellman discrete logarithms
- Chinese Remainder Theorem
"""

from __future__ import annotations

import math
import random
import secrets
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Optional


MAX_BSGS_ENTRIES = 2_000_000
SMALL_PRIMES = (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37)


class NumberTheoryError(ValueError):
    """Raised when a mathematical operation has invalid parameters."""


class ComputationLimitError(RuntimeError):
    """Raised when a computation exceeds configured resource limits."""


class JobStatus(Enum):
    PENDING = auto()
    RUNNING = auto()
    SOLVED = auto()
    NO_SOLUTION = auto()
    FAILED = auto()


def normalize(value: int, modulus: int) -> int:
    if modulus <= 0:
        raise NumberTheoryError("Modulus must be positive.")
    return value % modulus


def modular_power(base: int, exponent: int, modulus: int) -> int:
    """Binary modular exponentiation in O(log exponent) operations."""
    if modulus <= 0:
        raise NumberTheoryError("Modulus must be positive.")
    if exponent < 0:
        raise NumberTheoryError("Exponent cannot be negative.")

    result = 1 % modulus
    base %= modulus

    while exponent:
        if exponent & 1:
            result = result * base % modulus
        base = base * base % modulus
        exponent >>= 1

    return result


def extended_gcd(a: int, b: int) -> tuple[int, int, int]:
    """Return (gcd, x, y), satisfying ax + by = gcd(a, b)."""
    old_r, r = abs(a), abs(b)
    old_s, s = 1, 0
    old_t, t = 0, 1

    while r:
        quotient = old_r // r
        old_r, r = r, old_r - quotient * r
        old_s, s = s, old_s - quotient * s
        old_t, t = t, old_t - quotient * t

    return old_r, old_s * (1 if a >= 0 else -1), old_t * (
        1 if b >= 0 else -1
    )


def modular_inverse(a: int, modulus: int) -> int:
    """Return a^(-1) modulo modulus."""
    if modulus <= 1:
        raise NumberTheoryError("Modulus must exceed one.")

    gcd_value, x, _ = extended_gcd(a, modulus)

    if gcd_value != 1:
        raise NumberTheoryError(
            f"{a} has no modular inverse modulo {modulus}."
        )

    return x % modulus


def is_probable_prime(n: int, rounds: int = 16) -> bool:
    """
    Miller-Rabin primality test.

    Deterministic for unsigned integers below 2^64 using the
    established seven-base witness set. Larger inputs use
    independently sampled witnesses and provide a probable-prime test.
    """
    if n < 2:
        return False

    for prime in SMALL_PRIMES:
        if n == prime:
            return True
        if n % prime == 0:
            return False

    if rounds < 1:
        raise NumberTheoryError("At least one Miller-Rabin round is required.")

    d = n - 1
    s = 0

    while d % 2 == 0:
        d //= 2
        s += 1

    if n < (1 << 64):
        bases = (2, 325, 9375, 28178, 450775, 9780504, 1795265022)
    else:
        bases = [
            secrets.randbelow(n - 3) + 2
            for _ in range(rounds)
        ]

    for base in bases:
        base %= n

        if base < 2:
            continue

        x = modular_power(base, d, n)

        if x in (1, n - 1):
            continue

        for _ in range(s - 1):
            x = x * x % n
            if x == n - 1:
                break
        else:
            return False

    return True


def _pollard_rho(
    n: int,
    rng: random.Random,
    max_iterations: int = 200_000,
) -> int:
    """Find a nontrivial factor using Floyd-cycle Pollard Rho."""
    if n % 2 == 0:
        return 2
    if n % 3 == 0:
        return 3

    while True:
        x = rng.randrange(2, n - 1)
        y = x
        constant = rng.randrange(1, n - 1)
        divisor = 1

        for _ in range(max_iterations):
            x = (x * x + constant) % n
            y = (y * y + constant) % n
            y = (y * y + constant) % n

            divisor = math.gcd(abs(x - y), n)

            if divisor == 1:
                continue

            if divisor != n:
                return divisor

            break


def factor_integer(n: int) -> dict[int, int]:
    """
    Factor a positive integer into prime powers.

    Returns {prime: exponent}.
    Pollard Rho is randomized and its practical runtime depends
    strongly on the size of the smallest prime factor.
    """
    if n < 1:
        raise NumberTheoryError("Factorization requires a positive integer.")

    if n == 1:
        return {}

    rng = random.Random(secrets.randbits(128))
    factors: dict[int, int] = {}
    stack = [n]

    while stack:
        current = stack.pop()

        if current == 1:
            continue

        if is_probable_prime(current):
            factors[current] = factors.get(current, 0) + 1
            continue

        divisor = _pollard_rho(current, rng)

        if divisor in (1, current):
            raise RuntimeError("Pollard Rho failed to split an integer.")

        stack.append(divisor)
        stack.append(current // divisor)

    return dict(sorted(factors.items()))


def legendre_symbol(a: int, p: int) -> int:
    """
    Calculate the Legendre symbol (a/p).

    Returns:
      0  when p divides a
      1  when a is a nonzero quadratic residue
     -1  when a is a quadratic nonresidue
    """
    if p == 2 or not is_probable_prime(p):
        raise NumberTheoryError("Legendre modulus must be an odd prime.")

    value = a % p

    if value == 0:
        return 0

    result = modular_power(value, (p - 1) // 2, p)
    return 1 if result == 1 else -1


def quadratic_reciprocity(p: int, q: int) -> tuple[int, int, int]:
    """
    Demonstrate quadratic reciprocity for distinct odd primes.

    Returns:
        ((p/q), (q/p), expected_product)
    """
    if p == q or p == 2 or q == 2:
        raise NumberTheoryError("Use distinct odd primes.")

    if not is_probable_prime(p) or not is_probable_prime(q):
        raise NumberTheoryError("Both inputs must be prime.")

    left = legendre_symbol(p, q)
    right = legendre_symbol(q, p)

    expected = (
        -1 if ((p - 1) // 2 * ((q - 1) // 2)) % 2 else 1
    )

    if left * right != expected:
        raise ArithmeticError("Quadratic reciprocity verification failed.")

    return left, right, expected


def modular_square_roots(a: int, p: int) -> tuple[int, ...]:
    """
    Find all solutions of x^2 = a (mod p) using Tonelli-Shanks.

    Returns:
        ()       if no solution exists
        (root,)  for the zero-root or characteristic-two case
        (r, p-r) otherwise
    """
    if p == 2:
        return (a % 2,)

    if p < 2 or not is_probable_prime(p):
        raise NumberTheoryError("Modulus must be prime.")

    a %= p

    if a == 0:
        return (0,)

    if legendre_symbol(a, p) != 1:
        return ()

    if p % 4 == 3:
        root = modular_power(a, (p + 1) // 4, p)
        return tuple(sorted({root, (-root) % p}))

    # Factor p - 1 into q * 2^s.
    q = p - 1
    s = 0

    while q % 2 == 0:
        q //= 2
        s += 1

    # Find a quadratic nonresidue.
    z = 2

    while legendre_symbol(z, p) != -1:
        z += 1

    c = modular_power(z, q, p)
    x = modular_power(a, (q + 1) // 2, p)
    t = modular_power(a, q, p)
    m = s

    while t != 1:
        i = 1
        temporary = t * t % p

        while i < m and temporary != 1:
            temporary = temporary * temporary % p
            i += 1

        if i == m:
            raise ArithmeticError("Tonelli-Shanks invariant failed.")

        b = modular_power(c, 1 << (m - i - 1), p)

        x = x * b % p
        b_squared = b * b % p
        t = t * b_squared % p
        c = b_squared
        m = i

    roots = tuple(sorted({x, (-x) % p}))

    if any(root * root % p != a for root in roots):
        raise ArithmeticError("A computed square root failed verification.")

    return roots


def multiplicative_order(base: int, p: int) -> int:
    """Compute the order of a nonzero element in F_p*."""
    if p <= 2 or not is_probable_prime(p):
        raise NumberTheoryError("An odd prime modulus is required.")

    base %= p

    if base == 0:
        raise NumberTheoryError("Zero has no multiplicative order.")

    order = p - 1

    for prime in factor_integer(order):
        while (
            order % prime == 0
            and modular_power(base, order // prime, p) == 1
        ):
            order //= prime

    return order


def baby_step_giant_step(
    base: int,
    target: int,
    modulus: int,
    order: int,
    max_entries: int = MAX_BSGS_ENTRIES,
) -> Optional[int]:
    """
    Solve base^x = target (mod modulus), 0 <= x < order.

    Expected complexity: O(sqrt(order)) time and memory.
    """
    if modulus <= 1 or order <= 0:
        raise NumberTheoryError("Invalid modulus or group order.")

    if max_entries <= 0:
        raise NumberTheoryError("Memory limit must be positive.")

    base %= modulus
    target %= modulus

    m = math.isqrt(order)

    if m * m < order:
        m += 1

    if m > max_entries:
        raise ComputationLimitError(
            f"BSGS requires {m} baby steps; limit is {max_entries}."
        )

    # Build a hash table containing base^j.
    baby_steps: dict[int, int] = {}
    value = 1

    for j in range(m):
        baby_steps.setdefault(value, j)
        value = value * base % modulus

    giant_factor = modular_inverse(
        modular_power(base, m, modulus),
        modulus,
    )

    gamma = target
    giant_count = (order + m - 1) // m

    for i in range(giant_count + 1):
        if gamma in baby_steps:
            candidate = i * m + baby_steps[gamma]

            if (
                candidate < order
                and modular_power(base, candidate, modulus) == target
            ):
                return candidate

        gamma = gamma * giant_factor % modulus

    return None


def chinese_remainder(
    residues: list[int],
    moduli: list[int],
) -> int:
    """Combine congruences with pairwise coprime moduli."""
    if len(residues) != len(moduli) or not moduli:
        raise NumberTheoryError("Invalid CRT input dimensions.")

    result = 0
    product = 1

    for residue, modulus in zip(residues, moduli):
        if modulus <= 1 or math.gcd(product, modulus) != 1:
            raise NumberTheoryError(
                "CRT moduli must be pairwise coprime and exceed one."
            )

        correction = (
            (residue - result)
            * modular_inverse(product, modulus)
        ) % modulus

        result += product * correction
        product *= modulus
        result %= product

    return result


def pohlig_hellman(
    base: int,
    target: int,
    p: int,
    order: int,
    max_bsgs_entries: int = MAX_BSGS_ENTRIES,
) -> Optional[int]:
    """
    Solve a discrete logarithm in a prime-field subgroup.

    The order must be the exact multiplicative order of base.

    Pohlig-Hellman decomposes the problem into prime-power
    subgroups and combines the answers with CRT.

    Its advantage is greatest when the group order is smooth.
    """
    if not is_probable_prime(p):
        raise NumberTheoryError("The modulus must be prime.")

    if order <= 0 or order > p - 1:
        raise NumberTheoryError("Invalid subgroup order.")

    base %= p
    target %= p

    if base == 0:
        raise NumberTheoryError("The base must be nonzero.")

    if modular_power(base, order, p) != 1:
        raise NumberTheoryError("The supplied order is invalid.")

    order_factors = factor_integer(order)

    for prime in order_factors:
        if modular_power(base, order // prime, p) == 1:
            raise NumberTheoryError(
                "The supplied order is not the exact multiplicative order."
            )

    if modular_power(target, order, p) != 1:
        return None

    residues: list[int] = []
    moduli: list[int] = []

    for prime, exponent in order_factors.items():
        prime_power = prime ** exponent

        # Project the full problem into the subgroup of order q^e.
        subgroup_base = modular_power(base, order // prime_power, p)
        subgroup_target = modular_power(target, order // prime_power, p)

        # The reduced generator has order q.
        digit_base = modular_power(
            subgroup_base,
            prime_power // prime,
            p,
        )

        partial = 0
        q_power = 1

        for _ in range(exponent):
            inverse_partial = modular_inverse(
                modular_power(subgroup_base, partial, p),
                p,
            )

            correction = subgroup_target * inverse_partial % p

            digit_target = modular_power(
                correction,
                prime_power // (q_power * prime),
                p,
            )

            digit = baby_step_giant_step(
                digit_base,
                digit_target,
                p,
                prime,
                max_bsgs_entries,
            )

            if digit is None:
                return None

            partial += digit * q_power
            q_power *= prime

        residues.append(partial)
        moduli.append(prime_power)

    result = chinese_remainder(residues, moduli)
    result %= order

    if modular_power(base, result, p) != target:
        raise ArithmeticError("Discrete logarithm verification failed.")

    return result


@dataclass(frozen=True)
class PrimeField:
    modulus: int

    def __post_init__(self) -> None:
        if self.modulus < 2 or not is_probable_prime(self.modulus):
            raise NumberTheoryError("The field modulus must be prime.")

    def multiply(self, a: int, b: int) -> int:
        return (a * b) % self.modulus

    def power(self, a: int, exponent: int) -> int:
        return modular_power(a, exponent, self.modulus)


@dataclass
class DiscreteLogJob:
    job_id: int
    field: PrimeField
    base: int
    target: int
    order: int
    status: JobStatus = JobStatus.PENDING
    result: Optional[int] = None
    error: Optional[str] = None


@dataclass(frozen=True)
class QuadraticResidueReport:
    value: int
    prime: int
    symbol: int
    roots: tuple[int, ...]

    @property
    def is_residue(self) -> bool:
        return self.symbol >= 0


@dataclass
class NumberTheoryWorkbench:
    max_bsgs_entries: int = MAX_BSGS_ENTRIES
    jobs: dict[int, DiscreteLogJob] = field(default_factory=dict)

    def analyze_residue(self, a: int, p: int) -> QuadraticResidueReport:
        symbol = 0 if p == 2 else legendre_symbol(a, p)
        roots = modular_square_roots(a, p)

        return QuadraticResidueReport(
            value=a % p,
            prime=p,
            symbol=symbol,
            roots=roots,
        )

    def submit_discrete_log(
        self,
        job_id: int,
        base: int,
        target: int,
        p: int,
        order: int,
    ) -> DiscreteLogJob:
        if job_id in self.jobs:
            raise NumberTheoryError("Duplicate job identifier.")

        job = DiscreteLogJob(
            job_id=job_id,
            field=PrimeField(p),
            base=base,
            target=target,
            order=order,
        )

        self.jobs[job_id] = job
        job.status = JobStatus.RUNNING

        try:
            result = pohlig_hellman(
                base,
                target,
                p,
                order,
                self.max_bsgs_entries,
            )

            job.result = result
            job.status = (
                JobStatus.SOLVED if result is not None
                else JobStatus.NO_SOLUTION
            )

        except Exception as exc:
            job.status = JobStatus.FAILED
            job.error = str(exc)
            raise

        return job


def run_self_tests() -> None:
    assert modular_power(7, 128, 13) == pow(7, 128, 13)
    assert modular_inverse(3, 11) == 4
    assert math.gcd(84, 30) == 6

    assert is_probable_prime(1019)
    assert not is_probable_prime(1021 * 1031)

    factors = factor_integer(600851475143)
    product = math.prod(p ** e for p, e in factors.items())
    assert product == 600851475143
    assert all(is_probable_prime(p) for p in factors)

    assert legendre_symbol(56 * 56, 1019) == 1
    assert legendre_symbol(0, 1019) == 0
    assert legendre_symbol(2, 1019) == -1

    roots = modular_square_roots(56 * 56, 1019)
    assert roots == (56, 963)

    assert modular_square_roots(2, 1019) == ()
    assert modular_square_roots(9, 2) == (1,)

    reciprocity = quadratic_reciprocity(7, 11)
    assert reciprocity[0] * reciprocity[1] == reciprocity[2]

    base = 2
    prime = 1019
    order = multiplicative_order(base, prime)
    assert order == 1018

    secret_exponent = 137
    public_value = modular_power(base, secret_exponent, prime)

    recovered = pohlig_hellman(
        base,
        public_value,
        prime,
        order,
    )

    assert recovered == secret_exponent

    # The target 0 is not in the multiplicative subgroup.
    assert pohlig_hellman(base, 0, prime, order) is None

    # Basic inverse failure condition.
    try:
        modular_inverse(6, 15)
    except NumberTheoryError:
        pass
    else:
        raise AssertionError("A non-invertible value was accepted.")


def main() -> None:
    run_self_tests()

    workbench = NumberTheoryWorkbench()

    print("ADVANCED NUMBER THEORY")
    print("=" * 55)

    prime = 1019
    base = 2
    order = multiplicative_order(base, prime)

    print(f"\nPrime field: F_{prime}")
    print(f"Multiplicative group order: {prime - 1}")
    print(f"Base: {base}")
    print(f"Exact multiplicative order: {order}")

    report = workbench.analyze_residue(56 * 56, prime)

    print("\nQUADRATIC RESIDUE ANALYSIS")
    print(f"Input: {report.value}")
    print(f"Legendre symbol: {report.symbol}")
    print(f"Square roots: {report.roots}")

    print("\nQUADRATIC NONRESIDUE")
    nonresidue = workbench.analyze_residue(2, prime)
    print(f"Legendre symbol of 2: {nonresidue.symbol}")
    print(f"Square roots: {nonresidue.roots}")

    print("\nINTEGER FACTORIZATION")
    number = 600851475143
    factorization = factor_integer(number)
    print(f"{number} = {factorization}")

    secret_exponent = 137
    public_value = modular_power(base, secret_exponent, prime)

    print("\nPOHLIG-HELLMAN DISCRETE LOGARITHM")
    print(f"Base: {base}")
    print(f"Target: {public_value}")
    print(f"Secret exponent used in test: {secret_exponent}")

    job = workbench.submit_discrete_log(
        job_id=1,
        base=base,
        target=public_value,
        p=prime,
        order=order,
    )

    print(f"Job state: {job.status.name}")
    print(f"Recovered exponent: {job.result}")

    print("\nQUADRATIC RECIPROCITY")
    reciprocity = quadratic_reciprocity(7, 11)
    print(f"(7/11) = {reciprocity[0]}")
    print(f"(11/7) = {reciprocity[1]}")
    print(f"Product = {reciprocity[0] * reciprocity[1]}")
    print(f"Expected = {reciprocity[2]}")

    print("\nAll mathematical verification checks passed.")
    print(
        "\nSecurity note: These implementations are educational "
        "and are not constant-time cryptographic primitives."
    )


if __name__ == "__main__":
    main()
