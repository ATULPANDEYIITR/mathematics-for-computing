from __future__ import annotations

from dataclasses import dataclass
from math import gcd
from typing import Iterable


def validate_positive_integer(value: int, name: str) -> None:
    if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
        raise ValueError(f"{name} must be a positive integer")


def mod_pow(base: int, exponent: int, modulus: int) -> int:
    """Binary modular exponentiation in O(log exponent)."""
    if modulus <= 0:
        raise ValueError("modulus must be positive")
    if exponent < 0:
        raise ValueError("exponent must be non-negative")

    result = 1 % modulus
    base %= modulus

    while exponent:
        if exponent & 1:
            result = (result * base) % modulus
        base = (base * base) % modulus
        exponent >>= 1

    return result


def phi(n: int) -> int:
    """Euler's totient function: count integers in [1, n] coprime to n."""
    validate_positive_integer(n, "n")

    result = n
    value = n
    factor = 2

    while factor * factor <= value:
        if value % factor == 0:
            result -= result // factor
            while value % factor == 0:
                value //= factor
        factor += 1 if factor == 2 else 2

    if value > 1:
        result -= result // value

    return result


def coprime_values(n: int) -> list[int]:
    validate_positive_integer(n, "n")
    return [x for x in range(1, n + 1) if gcd(x, n) == 1]


def fermat_little_theorem(a: int, p: int) -> bool:
    """
    For prime p and a not divisible by p:
        a^(p-1) ≡ 1 (mod p)
    """
    validate_positive_integer(p, "p")
    if p < 2:
        return False

    for divisor in range(2, int(p**0.5) + 1):
        if p % divisor == 0:
            raise ValueError("p must be prime")

    if a % p == 0:
        return False

    return mod_pow(a, p - 1, p) == 1


def euler_theorem(a: int, n: int) -> bool:
    """
    If gcd(a, n) = 1:
        a^phi(n) ≡ 1 (mod n)
    """
    validate_positive_integer(n, "n")

    if gcd(a, n) != 1:
        return False

    return mod_pow(a, phi(n), n) == 1


def modular_inverse(a: int, modulus: int) -> int:
    """
    Compute the modular inverse using the extended Euclidean algorithm.
    The inverse exists exactly when gcd(a, modulus) = 1.
    """
    if modulus <= 1:
        raise ValueError("modulus must be greater than 1")

    old_r, r = a % modulus, modulus
    old_s, s = 1, 0

    while r:
        quotient = old_r // r
        old_r, r = r, old_r - quotient * r
        old_s, s = s, old_s - quotient * s

    if old_r != 1:
        raise ValueError("modular inverse does not exist")

    return old_s % modulus


def inverse_using_euler(a: int, n: int) -> int:
    """
    For gcd(a,n)=1:
        a^(-1) ≡ a^(phi(n)-1) (mod n)
    """
    if n <= 1:
        raise ValueError("n must be greater than 1")
    if gcd(a, n) != 1:
        raise ValueError("a and n must be coprime")

    return mod_pow(a, phi(n) - 1, n)


def verify_theorems(primes: Iterable[int], moduli: Iterable[int]) -> None:
    for p in primes:
        for a in range(1, p):
            assert fermat_little_theorem(a, p)

    for n in moduli:
        for a in range(1, n + 1):
            if gcd(a, n) == 1:
                assert euler_theorem(a, n)


@dataclass(frozen=True)
class RSAExample:
    p: int
    q: int
    e: int

    @property
    def n(self) -> int:
        return self.p * self.q

    @property
    def phi_n(self) -> int:
        return (self.p - 1) * (self.q - 1)

    @property
    def d(self) -> int:
        return modular_inverse(self.e, self.phi_n)

    def encrypt(self, message: int) -> int:
        if not 0 <= message < self.n:
            raise ValueError("message must satisfy 0 <= message < n")
        return mod_pow(message, self.e, self.n)

    def decrypt(self, ciphertext: int) -> int:
        if not 0 <= ciphertext < self.n:
            raise ValueError("ciphertext must satisfy 0 <= ciphertext < n")
        return mod_pow(ciphertext, self.d, self.n)


def main() -> None:
    print("=== Euler Phi Function ===")
    for n in [1, 2, 5, 8, 12, 36]:
        print(f"phi({n}) = {phi(n)}")

    print("\n=== Fermat's Little Theorem ===")
    for p in [5, 7, 11, 13]:
        print(f"p={p}, a=3 -> 3^({p}-1) mod {p} = {mod_pow(3, p - 1, p)}")

    print("\n=== Euler's Theorem ===")
    for n in [8, 9, 10, 12, 15]:
        a = 5
        if gcd(a, n) == 1:
            print(f"a={a}, n={n}, phi(n)={phi(n)}, result={mod_pow(a, phi(n), n)}")

    print("\n=== Reduced Residue System ===")
    n = 12
    print(f"Numbers coprime to {n}: {coprime_values(n)}")

    print("\n=== Modular Inverses ===")
    for a, n in [(3, 10), (7, 40), (11, 26)]:
        direct = modular_inverse(a, n)
        euler_based = inverse_using_euler(a, n)
        print(f"{a}^(-1) mod {n}: direct={direct}, Euler={euler_based}")
        assert direct == euler_based

    print("\n=== RSA-Style Example ===")
    rsa = RSAExample(p=61, q=53, e=17)
    message = 65
    ciphertext = rsa.encrypt(message)
    recovered = rsa.decrypt(ciphertext)

    print(f"n = {rsa.n}")
    print(f"phi(n) = {rsa.phi_n}")
    print(f"public exponent e = {rsa.e}")
    print(f"private exponent d = {rsa.d}")
    print(f"message = {message}")
    print(f"ciphertext = {ciphertext}")
    print(f"decrypted = {recovered}")
    assert recovered == message

    print("\n=== Automated Verification ===")
    verify_theorems([2, 3, 5, 7, 11, 13], range(2, 31))
    print("Fermat and Euler theorem checks passed.")

    print("\n=== Edge-Case Validation ===")
    try:
        fermat_little_theorem(3, 15)
    except ValueError as exc:
        print(f"Rejected composite modulus: {exc}")

    try:
        modular_inverse(6, 15)
    except ValueError as exc:
        print(f"Rejected non-invertible value: {exc}")

    print("\nSecurity note: textbook modular arithmetic is educational. Real cryptographic systems require"
          " established cryptographic libraries, secure key generation, padding, side-channel resistance,"
          " and appropriately sized parameters.")


if __name__ == "__main__":
    main()
