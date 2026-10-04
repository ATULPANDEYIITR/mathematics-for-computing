"""
Binomial Theorem: expansion, coefficients, identities, and generalized applications.

Self-contained executable learning implementation using only the Python standard library.

The program moves from:
    - direct binomial expansion
    - Pascal-triangle coefficient generation
    - coefficient extraction
    - binomial identities
    - polynomial multiplication
    - generalized binomial series for arbitrary exponents
    - numerical approximation
    - combinatorial interpretations
    - exact validation and edge cases
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, getcontext
from fractions import Fraction
from math import comb, factorial
from typing import Iterable


getcontext().prec = 50


# ---------------------------------------------------------------------------
# Expansion fundamentals
# ---------------------------------------------------------------------------

def binomial_coefficients(n: int) -> list[int]:
    """Return C(n, k) for k = 0 ... n using the multiplicative recurrence."""
    if not isinstance(n, int) or isinstance(n, bool):
        raise TypeError("n must be an integer")
    if n < 0:
        raise ValueError("n must be non-negative")

    coefficients = [1]
    current = 1

    for k in range(1, n + 1):
        # C(n,k) = C(n,k-1) * (n-k+1) / k.
        current = current * (n - k + 1) // k
        coefficients.append(current)

    return coefficients


def expand_binomial(
    n: int,
    a: int | Fraction = 1,
    b: int | Fraction = 1,
    variable: str = "x",
) -> list[tuple[int, int | Fraction, int]]:
    """
    Return terms of (a + b*x)^n.

    Each tuple is:
        (power_of_x, coefficient, power_of_a)

    so the mathematical term is:
        C(n,k) * a^(n-k) * b^k * x^k
    """
    if n < 0:
        raise ValueError("The ordinary finite binomial theorem requires n >= 0")

    terms = []

    for k, coefficient in enumerate(binomial_coefficients(n)):
        value = coefficient * (a ** (n - k)) * (b ** k)
        terms.append((k, value, n - k))

    return terms


def format_polynomial(
    coefficients: Iterable[int | Fraction],
    variable: str = "x",
) -> str:
    """Format coefficients in ascending power order into readable polynomial text."""
    coefficients = list(coefficients)
    pieces: list[str] = []

    for power, coefficient in enumerate(coefficients):
        if coefficient == 0:
            continue

        sign = "-" if coefficient < 0 else "+"
        magnitude = abs(coefficient)

        if power == 0:
            body = str(magnitude)
        elif power == 1:
            body = variable if magnitude == 1 else f"{magnitude}{variable}"
        else:
            body = f"{variable}^{power}" if magnitude == 1 else f"{magnitude}{variable}^{power}"

        if not pieces:
            pieces.append(f"-{body}" if coefficient < 0 else body)
        else:
            pieces.append(f" {sign} {body}")

    return "".join(pieces) if pieces else "0"


def ordinary_binomial_polynomial(
    n: int,
    a: int | Fraction = 1,
    b: int | Fraction = 1,
    variable: str = "x",
) -> str:
    """Create readable expansion text for (a + b*x)^n."""
    coefficients = []

    for k, c in enumerate(binomial_coefficients(n)):
        coefficients.append(c * (a ** (n - k)) * (b ** k))

    return format_polynomial(coefficients, variable)


# ---------------------------------------------------------------------------
# Pascal triangle and coefficient structure
# ---------------------------------------------------------------------------

def pascal_triangle(rows: int) -> list[list[int]]:
    """Build the first 'rows' rows of Pascal's triangle."""
    if rows < 0:
        raise ValueError("rows cannot be negative")

    triangle: list[list[int]] = []

    for row_number in range(rows):
        if row_number == 0:
            triangle.append([1])
            continue

        previous = triangle[-1]
        row = [1]

        for index in range(len(previous) - 1):
            row.append(previous[index] + previous[index + 1])

        row.append(1)
        triangle.append(row)

    return triangle


def print_pascal_triangle(rows: int) -> None:
    """Print Pascal's triangle with simple alignment."""
    triangle = pascal_triangle(rows)

    if not triangle:
        return

    width = len("   ".join(map(str, triangle[-1])))

    for row in triangle:
        text = "   ".join(map(str, row))
        print(text.center(width))


# ---------------------------------------------------------------------------
# Coefficient extraction
# ---------------------------------------------------------------------------

def coefficient_of_x(
    n: int,
    k: int,
    a: int | Fraction = 1,
    b: int | Fraction = 1,
) -> int | Fraction:
    """
    Extract [x^k](a + b*x)^n.

    The coefficient is C(n,k) * a^(n-k) * b^k.
    """
    if not 0 <= k <= n:
        return 0

    return comb(n, k) * (a ** (n - k)) * (b ** k)


def coefficient_of_x_power_in_sum(
    n: int,
    k: int,
    constant: int | Fraction,
    x_multiplier: int | Fraction,
) -> int | Fraction:
    """Convenience wrapper for [x^k](constant + x_multiplier*x)^n."""
    return coefficient_of_x(n, k, constant, x_multiplier)


def coefficient_from_general_linear_factors(
    n: int,
    k: int,
    constant: Fraction,
) -> Fraction:
    """
    Calculate [x^k](constant + x)^n exactly.

    Fraction is used to keep rational coefficients exact.
    """
    return Fraction(comb(n, k)) * constant ** (n - k)


# ---------------------------------------------------------------------------
# Binomial identities
# ---------------------------------------------------------------------------

def verify_pascal_identity(n: int, k: int) -> bool:
    """Verify C(n,k) = C(n-1,k-1) + C(n-1,k)."""
    if n <= 0 or not 0 <= k <= n:
        raise ValueError("Require n > 0 and 0 <= k <= n")

    left = comb(n, k)

    if k == 0:
        right = 1
    elif k == n:
        right = 1
    else:
        right = comb(n - 1, k - 1) + comb(n - 1, k)

    return left == right


def verify_symmetry(n: int, k: int) -> bool:
    """Verify C(n,k) = C(n,n-k)."""
    if not 0 <= k <= n:
        raise ValueError("Require 0 <= k <= n")

    return comb(n, k) == comb(n, n - k)


def verify_hockey_stick(n: int, k: int) -> bool:
    """
    Verify:
        C(k,k) + C(k+1,k) + ... + C(n,k) = C(n+1,k+1)
    """
    if n < k or k < 0:
        raise ValueError("Require n >= k >= 0")

    left = sum(comb(row, k) for row in range(k, n + 1))
    right = comb(n + 1, k + 1)

    return left == right


def verify_vandermonde(r: int, s: int, n: int) -> bool:
    """
    Verify Vandermonde's identity:
        sum_k C(r,k) C(s,n-k) = C(r+s,n)
    """
    if min(r, s, n) < 0:
        raise ValueError("Parameters must be non-negative")

    left = 0
    for k in range(0, n + 1):
        if k <= r and n - k <= s:
            left += comb(r, k) * comb(s, n - k)

    right = comb(r + s, n)
    return left == right


def verify_sum_of_coefficients(n: int) -> bool:
    """For (1+x)^n, the coefficient sum is 2^n."""
    return sum(binomial_coefficients(n)) == 2**n


def verify_alternating_sum(n: int) -> bool:
    """For n > 0, C(n,0)-C(n,1)+...+(-1)^n C(n,n) = 0."""
    return sum(
        ((-1) ** k) * comb(n, k)
        for k in range(n + 1)
    ) == 0


# ---------------------------------------------------------------------------
# Polynomial representation and multiplication
# ---------------------------------------------------------------------------

@dataclass
class Polynomial:
    """Polynomial represented by coefficients in ascending power order."""

    coefficients: list[Fraction]

    def __post_init__(self) -> None:
        self._normalize()

    def _normalize(self) -> None:
        while len(self.coefficients) > 1 and self.coefficients[-1] == 0:
            self.coefficients.pop()

    @classmethod
    def from_integers(cls, values: Iterable[int]) -> "Polynomial":
        return cls([Fraction(value) for value in values])

    def multiply(self, other: "Polynomial") -> "Polynomial":
        result = [
            Fraction(0)
            for _ in range(len(self.coefficients) + len(other.coefficients) - 1)
        ]

        # Convolution is the coefficient-level mechanism behind polynomial
        # multiplication and generalized product expansions.
        for i, left in enumerate(self.coefficients):
            for j, right in enumerate(other.coefficients):
                result[i + j] += left * right

        return Polynomial(result)

    def evaluate(self, x: Fraction) -> Fraction:
        """Evaluate using Horner's method."""
        result = Fraction(0)

        for coefficient in reversed(self.coefficients):
            result = result * x + coefficient

        return result

    def __str__(self) -> str:
        return format_polynomial(self.coefficients)


def polynomial_from_binomial(
    n: int,
    a: int = 1,
    b: int = 1,
) -> Polynomial:
    """Return the exact polynomial for (a + b*x)^n."""
    coefficients = [
        Fraction(coefficient_of_x(n, k, a, b))
        for k in range(n + 1)
    ]
    return Polynomial(coefficients)


# ---------------------------------------------------------------------------
# Generalized binomial theorem
# ---------------------------------------------------------------------------

def generalized_binomial_coefficient(alpha: Fraction, k: int) -> Fraction:
    """
    Generalized coefficient:
        alpha(alpha-1)...(alpha-k+1) / k!

    This works for integer and rational alpha.
    """
    if k < 0:
        raise ValueError("k must be non-negative")

    result = Fraction(1)

    for j in range(k):
        result *= alpha - j

    return result / factorial(k)


def generalized_binomial_series(
    alpha: Fraction,
    x: Fraction,
    terms: int,
) -> Fraction:
    """
    Approximate (1+x)^alpha with a finite generalized binomial series.

    Convergence of the infinite series requires |x| < 1 in the usual
    real-variable setting for non-integer alpha.
    """
    if terms <= 0:
        raise ValueError("terms must be positive")

    if abs(x) >= 1 and alpha.denominator != 1:
        raise ValueError(
            "For a non-integer exponent, this series requires |x| < 1 "
            "for the standard convergent expansion."
        )

    total = Fraction(0)

    for k in range(terms):
        total += generalized_binomial_coefficient(alpha, k) * (x ** k)

    return total


def generalized_terms(
    alpha: Fraction,
    terms: int,
) -> list[Fraction]:
    """Return generalized binomial coefficients through the requested order."""
    return [
        generalized_binomial_coefficient(alpha, k)
        for k in range(terms)
    ]


# ---------------------------------------------------------------------------
# Numerical applications
# ---------------------------------------------------------------------------

def decimal_generalized_series(
    alpha: Decimal,
    x: Decimal,
    terms: int,
) -> Decimal:
    """
    Decimal implementation of the generalized expansion.

    The recurrence avoids repeatedly constructing factorials:
        c_k = c_(k-1) * (alpha-k+1) / k
    """
    if terms <= 0:
        raise ValueError("terms must be positive")

    if abs(x) >= Decimal("1") and alpha != int(alpha):
        raise ValueError("Use |x| < 1 for a non-integer generalized expansion")

    coefficient = Decimal(1)
    total = Decimal(1)
    power = Decimal(1)

    for k in range(1, terms):
        coefficient *= alpha - Decimal(k - 1)
        coefficient /= Decimal(k)
        power *= x
        total += coefficient * power

    return total


def sqrt_via_binomial(value: Decimal, terms: int = 20) -> Decimal:
    """
    Approximate sqrt(value) through:
        sqrt(value) = (1 + x)^(1/2)
    after factoring the value as a nearby perfect scale.

    For the demonstration, values are assumed positive and close enough
    to the selected expansion point for |x| < 1.
    """
    if value <= 0:
        raise ValueError("value must be positive")

    # Use 1 as the expansion point for values in (0, 2).
    if value >= 2:
        raise ValueError("This demonstration expects 0 < value < 2")

    x = value - Decimal(1)
    return decimal_generalized_series(Decimal("0.5"), x, terms)


# ---------------------------------------------------------------------------
# Combinatorial applications
# ---------------------------------------------------------------------------

def binary_strings_with_exact_ones(length: int, ones: int) -> int:
    """
    Count binary strings of a fixed length containing exactly `ones` ones.

    Choosing the positions of the ones gives C(length, ones).
    """
    if length < 0 or not 0 <= ones <= length:
        raise ValueError("Require length >= 0 and 0 <= ones <= length")

    return comb(length, ones)


def probability_exact_successes(
    trials: int,
    successes: int,
    probability: Fraction,
) -> Fraction:
    """
    Binomial probability:
        P(X=k) = C(n,k) p^k (1-p)^(n-k)
    """
    if trials < 0 or not 0 <= successes <= trials:
        raise ValueError("Invalid trial/success count")

    if not 0 <= probability <= 1:
        raise ValueError("probability must lie between 0 and 1")

    return (
        Fraction(comb(trials, successes))
        * probability**successes
        * (1 - probability) ** (trials - successes)
    )


def expected_binomial_successes(
    trials: int,
    probability: Fraction,
) -> Fraction:
    """E[X] = np for a Binomial(n,p) random variable."""
    if trials < 0 or not 0 <= probability <= 1:
        raise ValueError("Invalid binomial distribution parameters")

    return trials * probability


def binomial_distribution(
    trials: int,
    probability: Fraction,
) -> list[Fraction]:
    """Return all exact probabilities for X = 0 ... trials."""
    return [
        probability_exact_successes(trials, k, probability)
        for k in range(trials + 1)
    ]


# ---------------------------------------------------------------------------
# Edge-case and validation demonstrations
# ---------------------------------------------------------------------------

def run_validation_examples() -> None:
    print("\nValidation and edge cases")

    cases = [
        ("n = 0", binomial_coefficients(0)),
        ("(1+x)^1", ordinary_binomial_polynomial(1)),
        ("(1+x)^2", ordinary_binomial_polynomial(2)),
        ("(1+x)^5", ordinary_binomial_polynomial(5)),
        ("(2+3x)^4", ordinary_binomial_polynomial(4, 2, 3)),
    ]

    for label, value in cases:
        print(f"{label}: {value}")

    try:
        binomial_coefficients(-1)
    except ValueError as exc:
        print(f"Rejected invalid exponent: {exc}")

    try:
        coefficient_of_x(5, 8)
    except Exception as exc:
        print(f"Unexpected error: {exc}")
    else:
        print("[x^8](1+x)^5 = 0 because the requested degree exceeds n")


# ---------------------------------------------------------------------------
# Integrated demonstration
# ---------------------------------------------------------------------------

def main() -> None:
    print("=" * 72)
    print("BINOMIAL THEOREM: COMPUTATION AND APPLICATIONS")
    print("=" * 72)

    print("\nOrdinary expansion")
    n = 5
    print(f"(1 + x)^{n} = {ordinary_binomial_polynomial(n)}")
    print(f"Coefficients: {binomial_coefficients(n)}")

    print("\nScaled binomial")
    print("(2 + 3x)^4 =", ordinary_binomial_polynomial(4, 2, 3))

    print("\nPascal triangle")
    print_pascal_triangle(8)

    print("\nCoefficient extraction")
    n = 10
    k = 4
    coefficient = coefficient_of_x(n, k)
    print(f"[x^{k}](1+x)^{n} = C({n},{k}) = {coefficient}")

    coefficient = coefficient_of_x(7, 3, 2, 5)
    print(f"[x^3](2+5x)^7 = {coefficient}")

    print("\nBinomial identities")
    print("Pascal identity:", verify_pascal_identity(12, 5))
    print("Symmetry:", verify_symmetry(12, 5))
    print("Hockey-stick:", verify_hockey_stick(12, 5))
    print("Vandermonde:", verify_vandermonde(8, 7, 6))
    print("Coefficient sum:", verify_sum_of_coefficients(12))
    print("Alternating sum:", verify_alternating_sum(12))

    print("\nPolynomial object")
    polynomial = polynomial_from_binomial(4, 2, 3)
    print("(2+3x)^4 =", polynomial)
    x = Fraction(2)
    print(f"Evaluation at x={x}: {polynomial.evaluate(x)}")

    print("\nPolynomial multiplication")
    left = Polynomial.from_integers([1, 2])      # 1 + 2x
    right = Polynomial.from_integers([3, 4, 1])  # 3 + 4x + x^2
    product = left.multiply(right)
    print(f"({left})({right}) = {product}")

    print("\nGeneralized binomial coefficients")
    alpha = Fraction(1, 2)
    coefficients = generalized_terms(alpha, 8)
    print("Coefficients for (1+x)^(1/2):")
    print(coefficients)

    print("\nGeneralized series")
    x = Fraction(1, 4)
    approximation = generalized_binomial_series(Fraction(1, 2), x, 15)
    print(f"(1+1/4)^(1/2) approximation = {approximation}")
    print(f"Decimal approximation = {float(approximation):.12f}")

    print("\nSquare-root approximation")
    value = Decimal("1.21")
    approximation = sqrt_via_binomial(value, 30)
    print(f"sqrt({value}) ≈ {approximation}")
    print(f"Built-in reference ≈ {value.sqrt()}")

    print("\nCombinatorial interpretation")
    length = 12
    ones = 5
    count = binary_strings_with_exact_ones(length, ones)
    print(
        f"Binary strings of length {length} with exactly {ones} ones: "
        f"C({length},{ones}) = {count}"
    )

    print("\nBinomial probability model")
    trials = 10
    successes = 6
    probability = Fraction(2, 5)
    exact_probability = probability_exact_successes(
        trials,
        successes,
        probability,
    )
    print(
        f"P(X={successes}) for n={trials}, p={probability}: "
        f"{exact_probability} = {float(exact_probability):.8f}"
    )
    print(
        f"Expected successes E[X] = "
        f"{expected_binomial_successes(trials, probability)}"
    )

    distribution = binomial_distribution(trials, probability)
    print("Distribution:")
    for outcome, probability_value in enumerate(distribution):
        print(
            f"  X={outcome:2d}: "
            f"{probability_value} "
            f"({float(probability_value):.6f})"
        )

    run_validation_examples()

    print("\nPerformance considerations")
    print(
        "The multiplicative coefficient recurrence computes all "
        "C(n,k) values without constructing factorials for every k."
    )
    print(
        "Python's math.comb uses an optimized exact integer algorithm "
        "and is preferable when only individual coefficients are needed."
    )
    print(
        "Generalized series are approximations when the exponent is non-integer; "
        "truncation error depends strongly on |x| and the number of terms."
    )

    print("\nSecurity and correctness considerations")
    print(
        "Exact integer and Fraction arithmetic prevents floating-point rounding "
        "from changing symbolic coefficients."
    )
    print(
        "Very large n can produce extremely large integers, so resource limits "
        "should be considered when accepting n from untrusted input."
    )


if __name__ == "__main__":
    main()
