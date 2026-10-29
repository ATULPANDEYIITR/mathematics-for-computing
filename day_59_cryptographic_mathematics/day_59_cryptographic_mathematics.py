from __future__ import annotations

from dataclasses import dataclass
from math import gcd
from secrets import randbelow, randbits
from typing import Iterable


class RSAError(ValueError):
    """Raised when an RSA mathematical invariant is violated."""


def extended_gcd(a: int, b: int) -> tuple[int, int, int]:
    """Return (g, x, y) such that ax + by = g = gcd(a, b)."""
    old_r, r = a, b
    old_x, x = 1, 0
    old_y, y = 0, 1

    while r:
        q = old_r // r
        old_r, r = r, old_r - q * r
        old_x, x = x, old_x - q * x
        old_y, y = y, old_y - q * y

    return old_r, old_x, old_y


def mod_inverse(a: int, modulus: int) -> int:
    """Compute a^-1 mod modulus when it exists."""
    if modulus <= 1:
        raise RSAError("Modulus must be greater than one.")

    a %= modulus
    g, x, _ = extended_gcd(a, modulus)
    if g != 1:
        raise RSAError(f"{a} has no modular inverse modulo {modulus}.")
    return x % modulus


def modular_pow(base: int, exponent: int, modulus: int) -> int:
    """
    Binary modular exponentiation.

    Complexity: O(log exponent) modular multiplications.
    Python's built-in pow(base, exponent, modulus) is normally faster,
    but this implementation makes the mathematics explicit.
    """
    if modulus <= 0:
        raise RSAError("Modulus must be positive.")
    if exponent < 0:
        raise RSAError("Exponent must be non-negative.")

    result = 1 % modulus
    base %= modulus

    while exponent:
        if exponent & 1:
            result = (result * base) % modulus
        base = (base * base) % modulus
        exponent >>= 1

    return result


def is_probable_prime(n: int, rounds: int = 20) -> bool:
    """
    Miller-Rabin probable-prime test.

    For the small demonstration primes used by this program, deterministic
    trial division would also work. Miller-Rabin shows the scalable approach.
    """
    if n < 2:
        return False

    small_primes = (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37)
    if n in small_primes:
        return True
    if any(n % p == 0 for p in small_primes):
        return False

    d = n - 1
    s = 0
    while d % 2 == 0:
        s += 1
        d //= 2

    for _ in range(rounds):
        a = 2 + randbelow(n - 3)
        x = pow(a, d, n)

        if x in (1, n - 1):
            continue

        for _ in range(s - 1):
            x = (x * x) % n
            if x == n - 1:
                break
        else:
            return False

    return True


def generate_prime(bits: int) -> int:
    """Generate an odd probable prime with exactly the requested bit length."""
    if bits < 8:
        raise RSAError("Prime size must be at least 8 bits.")

    while True:
        candidate = randbits(bits)
        candidate |= (1 << (bits - 1)) | 1
        if is_probable_prime(candidate):
            return candidate


@dataclass(frozen=True)
class PublicKey:
    n: int
    e: int


@dataclass(frozen=True)
class PrivateKey:
    n: int
    d: int
    p: int
    q: int
    phi: int


@dataclass(frozen=True)
class RSAKeyPair:
    public: PublicKey
    private: PrivateKey


def generate_key_pair(prime_bits: int = 128) -> RSAKeyPair:
    """
    Generate an educational RSA key pair.

    Production RSA normally uses much larger primes and secure padding such
    as RSA-OAEP. This script intentionally exposes the underlying mathematics.
    """
    if prime_bits < 16:
        raise RSAError("Use at least 16 bits per prime for this demonstration.")

    while True:
        p = generate_prime(prime_bits)
        q = generate_prime(prime_bits)

        if p == q:
            continue

        n = p * q
        phi = (p - 1) * (q - 1)

        # 65537 is the standard public exponent when it is coprime to phi.
        e = 65537
        if gcd(e, phi) != 1:
            continue

        d = mod_inverse(e, phi)
        return RSAKeyPair(
            public=PublicKey(n=n, e=e),
            private=PrivateKey(n=n, d=d, p=p, q=q, phi=phi),
        )


def validate_key_pair(keys: RSAKeyPair) -> None:
    """Check the core RSA mathematical invariants."""
    public = keys.public
    private = keys.private

    if private.p * private.q != public.n:
        raise RSAError("n is not equal to p*q.")

    if private.phi != (private.p - 1) * (private.q - 1):
        raise RSAError("Incorrect Euler totient.")

    if gcd(public.e, private.phi) != 1:
        raise RSAError("Public exponent is not invertible modulo phi(n).")

    if (public.e * private.d) % private.phi != 1:
        raise RSAError("d is not the modular inverse of e modulo phi(n).")


def encrypt_integer(message: int, key: PublicKey) -> int:
    """RSA textbook encryption: c = m^e mod n."""
    if not 0 <= message < key.n:
        raise RSAError("Message integer must satisfy 0 <= m < n.")
    return modular_pow(message, key.e, key.n)


def decrypt_integer(ciphertext: int, key: PrivateKey) -> int:
    """RSA textbook decryption: m = c^d mod n."""
    if not 0 <= ciphertext < key.n:
        raise RSAError("Ciphertext must satisfy 0 <= c < n.")
    return modular_pow(ciphertext, key.d, key.n)


def decrypt_integer_crt(ciphertext: int, key: PrivateKey) -> int:
    """
    CRT-optimized RSA decryption.

    Computing modulo p and q keeps intermediate values smaller. The result
    is reconstructed modulo n.
    """
    if not 0 <= ciphertext < key.n:
        raise RSAError("Ciphertext must satisfy 0 <= c < n.")

    dp = key.d % (key.p - 1)
    dq = key.d % (key.q - 1)
    m_p = pow(ciphertext, dp, key.p)
    m_q = pow(ciphertext, dq, key.q)

    q_inverse = mod_inverse(key.q, key.p)
    h = ((m_p - m_q) * q_inverse) % key.p
    return (m_q + h * key.q) % key.n


def text_to_integer(text: str) -> int:
    data = text.encode("utf-8")
    if not data:
        raise RSAError("Message cannot be empty.")
    return int.from_bytes(data, "big")


def integer_to_text(value: int) -> str:
    if value < 0:
        raise RSAError("Integer must be non-negative.")
    length = max(1, (value.bit_length() + 7) // 8)
    return value.to_bytes(length, "big").decode("utf-8")


def demonstrate_modular_math() -> None:
    base, exponent, modulus = 7, 560, 561
    fast = modular_pow(base, exponent, modulus)
    builtin = pow(base, exponent, modulus)

    assert fast == builtin
    print("Modular exponentiation:")
    print(f"  {base}^{exponent} mod {modulus} = {fast}")

    g, x, y = extended_gcd(240, 46)
    assert g == 2
    assert 240 * x + 46 * y == g
    print(f"Extended Euclid: gcd(240, 46) = {g}, coefficients = ({x}, {y})")

    inverse = mod_inverse(17, 3120)
    assert inverse == 2753
    assert (17 * inverse) % 3120 == 1
    print(f"Modular inverse: 17^-1 mod 3120 = {inverse}")


def demonstrate_rsa() -> None:
    keys = generate_key_pair(prime_bits=128)
    validate_key_pair(keys)

    print("\nRSA key material:")
    print(f"  p   = {keys.private.p}")
    print(f"  q   = {keys.private.q}")
    print(f"  n   = {keys.public.n}")
    print(f"  phi = {keys.private.phi}")
    print(f"  e   = {keys.public.e}")
    print(f"  d   = {keys.private.d}")

    message = 123456789
    ciphertext = encrypt_integer(message, keys.public)
    recovered = decrypt_integer(ciphertext, keys.private)
    recovered_crt = decrypt_integer_crt(ciphertext, keys.private)

    assert recovered == message
    assert recovered_crt == message

    print("\nInteger encryption:")
    print(f"  message     = {message}")
    print(f"  ciphertext  = {ciphertext}")
    print(f"  decrypted   = {recovered}")
    print(f"  CRT result  = {recovered_crt}")

    # A text message must fit below n. With 256-bit n, this message does.
    text = "RSA mathematics"
    message_int = text_to_integer(text)
    if message_int >= keys.public.n:
        raise RSAError("Text example does not fit into the demonstration modulus.")

    encrypted_text = encrypt_integer(message_int, keys.public)
    decrypted_text = integer_to_text(decrypt_integer(encrypted_text, keys.private))

    assert decrypted_text == text

    print("\nText example:")
    print(f"  plaintext   = {text}")
    print(f"  integer     = {message_int}")
    print(f"  ciphertext  = {encrypted_text}")
    print(f"  recovered   = {decrypted_text}")

    # Demonstrate a boundary failure rather than silently accepting an
    # invalid RSA message representative.
    try:
        encrypt_integer(keys.public.n, keys.public)
    except RSAError as exc:
        print(f"\nExpected validation failure: {exc}")


def run_assertions() -> None:
    assert modular_pow(2, 10, 1000) == 24
    assert mod_inverse(3, 11) == 4
    assert is_probable_prime(101)
    assert not is_probable_prime(121)

    keys = generate_key_pair(64)
    validate_key_pair(keys)

    for message in (0, 1, 2, 42, keys.public.n - 1):
        ciphertext = encrypt_integer(message, keys.public)
        assert decrypt_integer(ciphertext, keys.private) == message
        assert decrypt_integer_crt(ciphertext, keys.private) == message


if __name__ == "__main__":
    run_assertions()
    demonstrate_modular_math()
    demonstrate_rsa()
