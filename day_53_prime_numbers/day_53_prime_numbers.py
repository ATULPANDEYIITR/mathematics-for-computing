from __future__ import annotations

from dataclasses import dataclass
from math import isqrt, log
from random import Random
from typing import Iterator


def is_prime(n: int) -> bool:
    """Return True when n is a prime integer using trial division."""
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False

    limit = isqrt(n)
    divisor = 3
    while divisor <= limit:
        if n % divisor == 0:
            return False
        divisor += 2
    return True


def prime_factorization(n: int) -> dict[int, int]:
    """
    Return the prime factorization as {prime: exponent}.

    Example:
        360 -> {2: 3, 3: 2, 5: 1}
    """
    if n < 2:
        raise ValueError("prime factorization requires n >= 2")

    factors: dict[int, int] = {}

    while n % 2 == 0:
        factors[2] = factors.get(2, 0) + 1
        n //= 2

    divisor = 3
    while divisor <= isqrt(n):
        while n % divisor == 0:
            factors[divisor] = factors.get(divisor, 0) + 1
            n //= divisor
        divisor += 2

    if n > 1:
        factors[n] = factors.get(n, 0) + 1

    return factors


def factorization_text(factors: dict[int, int]) -> str:
    return " × ".join(
        str(prime) if exponent == 1 else f"{prime}^{exponent}"
        for prime, exponent in factors.items()
    )


def sieve_of_eratosthenes(limit: int) -> list[int]:
    """Generate every prime <= limit using a boolean sieve."""
    if limit < 2:
        return []

    composite = bytearray(limit + 1)
    composite[0:2] = b"\x01\x01"

    for candidate in range(2, isqrt(limit) + 1):
        if not composite[candidate]:
            start = candidate * candidate
            composite[start : limit + 1 : candidate] = b"\x01" * (
                ((limit - start) // candidate) + 1
            )

    return [n for n in range(2, limit + 1) if not composite[n]]


def segmented_sieve(low: int, high: int) -> list[int]:
    """
    Find primes in [low, high] without allocating a sieve for all
    integers below low.
    """
    if low > high:
        raise ValueError("low must not exceed high")
    if high < 2:
        return []

    low = max(low, 2)
    base_primes = sieve_of_eratosthenes(isqrt(high))
    size = high - low + 1
    composite = bytearray(size)

    for prime in base_primes:
        first = max(prime * prime, ((low + prime - 1) // prime) * prime)
        for multiple in range(first, high + 1, prime):
            composite[multiple - low] = 1

    return [low + i for i, marked in enumerate(composite) if not marked]


def prime_counting_function(limit: int) -> int:
    return len(sieve_of_eratosthenes(limit))


def prime_gaps(primes: list[int]) -> list[int]:
    return [
        current - previous
        for previous, current in zip(primes, primes[1:])
    ]


def empirical_prime_density(primes: list[int], low: int, high: int) -> float:
    if high < low:
        raise ValueError("high must be >= low")
    interval_size = high - low + 1
    count = sum(low <= prime <= high for prime in primes)
    return count / interval_size


def estimated_prime_density(x: int) -> float:
    """Prime number theorem estimate: density near x is approximately 1 / ln(x)."""
    if x <= 1:
        raise ValueError("x must be > 1")
    return 1.0 / log(x)


def stream_primes(limit: int) -> Iterator[int]:
    """Simple incremental prime generator for cases where a full list is unnecessary."""
    primes: list[int] = []
    candidate = 2

    while candidate <= limit:
        if all(
            candidate % prime != 0
            for prime in primes
            if prime * prime <= candidate
        ):
            primes.append(candidate)
            yield candidate
        candidate += 1


@dataclass(frozen=True)
class PrimeAnalysis:
    limit: int
    primes: tuple[int, ...]
    largest_gap: int
    average_gap: float
    empirical_density: float
    theoretical_density: float


def analyze_prime_distribution(limit: int) -> PrimeAnalysis:
    if limit < 2:
        raise ValueError("limit must be >= 2")

    primes = sieve_of_eratosthenes(limit)
    gaps = prime_gaps(primes)

    return PrimeAnalysis(
        limit=limit,
        primes=tuple(primes),
        largest_gap=max(gaps, default=0),
        average_gap=sum(gaps) / len(gaps) if gaps else 0.0,
        empirical_density=len(primes) / limit,
        theoretical_density=estimated_prime_density(limit),
    )


def verify_factorization(n: int, factors: dict[int, int]) -> bool:
    reconstructed = 1

    for prime, exponent in factors.items():
        if not is_prime(prime) or exponent <= 0:
            return False
        reconstructed *= prime**exponent

    return reconstructed == n


def randomized_factorization_test(
    samples: int = 100,
    upper_bound: int = 100_000,
    seed: int = 42,
) -> None:
    rng = Random(seed)

    for _ in range(samples):
        value = rng.randint(2, upper_bound)
        factors = prime_factorization(value)

        if not verify_factorization(value, factors):
            raise AssertionError(f"Invalid factorization for {value}: {factors}")


def run_self_tests() -> None:
    assert not is_prime(0)
    assert not is_prime(1)
    assert is_prime(2)
    assert is_prime(97)
    assert not is_prime(99)

    assert prime_factorization(2) == {2: 1}
    assert prime_factorization(360) == {2: 3, 3: 2, 5: 1}
    assert factorization_text(prime_factorization(360)) == "2^3 × 3^2 × 5"

    assert sieve_of_eratosthenes(1) == []
    assert sieve_of_eratosthenes(10) == [2, 3, 5, 7]
    assert segmented_sieve(100, 120) == [101, 103, 107, 109, 113]

    randomized_factorization_test()


def main() -> None:
    run_self_tests()

    values = [84, 360, 9973, 1_000_000]

    print("Prime factorization")
    print("-------------------")
    for value in values:
        factors = prime_factorization(value)
        print(f"{value:>10} = {factorization_text(factors)}")

    limit = 100
    primes = sieve_of_eratosthenes(limit)
    analysis = analyze_prime_distribution(limit)

    print("\nSieve of Eratosthenes")
    print("---------------------")
    print(f"Primes <= {limit}: {primes}")
    print(f"π({limit}) = {prime_counting_function(limit)}")

    print("\nPrime distribution")
    print("------------------")
    print(f"Empirical density through {limit}: {analysis.empirical_density:.4f}")
    print(f"1 / ln({limit}): {analysis.theoretical_density:.4f}")
    print(f"Average prime gap: {analysis.average_gap:.4f}")
    print(f"Largest prime gap: {analysis.largest_gap}")

    interval = segmented_sieve(1_000_000, 1_000_200)
    print("\nSegmented sieve")
    print("---------------")
    print(f"Primes in [1,000,000, 1,000,200]: {interval}")

    print("\nIncremental prime stream")
    print("------------------------")
    print(list(stream_primes(50)))


if __name__ == "__main__":
    main()
