"""
RADICALS AND ROOTS
==================

A self-contained study and demonstration script covering:
- Square roots, cube roots, and nth roots
- Principal roots and real-number restrictions
- Perfect and non-perfect roots
- Simplifying radicals
- Adding, subtracting, multiplying, and dividing radicals
- Rational exponents
- Rationalization
- Nested radicals
- Radical equations and extraneous solutions
- Absolute-value behavior of even roots
- Complex roots and principal complex roots
- Numerical accuracy and floating-point issues
- Algorithms for exact radical simplification
- Performance considerations
- Validation, testing, and edge cases

The script uses only Python's standard library.
"""

from __future__ import annotations

import cmath
import math
from dataclasses import dataclass
from fractions import Fraction
from functools import reduce
from math import gcd
from typing import Iterable, Optional


# =============================================================================
# 1. FUNDAMENTAL DEFINITIONS
# =============================================================================

"""
A radical is an expression involving a root.

    sqrt(a)        = square root of a
    cbrt(a)        = cube root of a
    root_n(a)      = nth root of a

The notation

    n-th root of a

means a number x satisfying

    x^n = a

For even n over the real numbers, a must be non-negative if we want a
real-valued root.

For odd n, every real number has exactly one real nth root.

IMPORTANT:
The principal square root sqrt(a) is defined to be the NON-NEGATIVE
number whose square is a.

Therefore:

    sqrt(25) = 5

not -5.

But the equation

    x^2 = 25

has two solutions:

    x = 5
    x = -5

This distinction is one of the most important ideas in radical algebra.
"""


def square_root(value: float) -> float:
    """Return the principal real square root."""
    if value < 0:
        raise ValueError("A negative number has no real square root.")
    return math.sqrt(value)


def cube_root(value: float) -> float:
    """
    Return the real cube root.

    math.pow(value, 1/3) is problematic for negative values because floating
    point exponentiation can produce a domain error. This implementation
    preserves the sign explicitly.
    """
    if value == 0:
        return 0.0

    return math.copysign(abs(value) ** (1.0 / 3.0), value)


def nth_root_real(value: float, degree: int) -> float:
    """
    Calculate the real principal nth root.

    Even degree:
        value < 0 -> no real root

    Odd degree:
        negative values are allowed.
    """
    if degree <= 0:
        raise ValueError("Root degree must be a positive integer.")

    if not isinstance(degree, int):
        raise TypeError("Root degree must be an integer.")

    if value < 0 and degree % 2 == 0:
        raise ValueError(
            f"An even-degree root of {value} is not real."
        )

    if value == 0:
        return 0.0

    if value < 0:
        return -((-value) ** (1.0 / degree))

    return value ** (1.0 / degree)


# Basic examples
print("=" * 80)
print("1. BASIC ROOTS")
print("=" * 80)

print("sqrt(49) =", square_root(49))
print("cube_root(27) =", cube_root(27))
print("cube_root(-27) =", cube_root(-27))
print("5th root of 32 =", nth_root_real(32, 5))
print("5th root of -32 =", nth_root_real(-32, 5))


# =============================================================================
# 2. PERFECT POWERS
# =============================================================================

"""
A perfect square is an integer that can be written as:

    k^2

Examples:
    0, 1, 4, 9, 16, 25, 36, ...

A perfect cube has the form:

    k^3

Examples:
    -8, -1, 0, 1, 8, 27, ...

More generally, a perfect nth power is an integer of the form:

    k^n

Exact integer detection is preferable to blindly trusting floating-point
square roots when implementing mathematical algorithms.
"""


def is_perfect_square(number: int) -> bool:
    """Return True if number is a non-negative perfect square."""
    if number < 0:
        return False

    root = math.isqrt(number)
    return root * root == number


def is_perfect_power(number: int, degree: int) -> bool:
    """
    Determine whether an integer is an exact nth power.

    For odd degrees, negative bases are supported.
    For even degrees, a negative number cannot be a real perfect power.
    """
    if degree <= 0:
        raise ValueError("Degree must be positive.")

    if number < 0 and degree % 2 == 0:
        return False

    if number == 0:
        return True

    absolute_number = abs(number)

    # Estimate the candidate root.
    candidate = round(absolute_number ** (1.0 / degree))

    # Floating-point estimation may be one integer away.
    for possible_root in range(max(0, candidate - 2), candidate + 3):
        if possible_root ** degree == absolute_number:
            return True

    return False


print("\nPerfect-power examples:")
for value in [0, 1, 4, 9, 10, 16, 25, 27, 28]:
    print(
        f"{value:>2}: perfect square = {is_perfect_square(value)}, "
        f"perfect cube = {is_perfect_power(value, 3)}"
    )


# =============================================================================
# 3. PRIME FACTORIZATION
# =============================================================================

"""
Radical simplification relies heavily on prime factorization.

For example:

    sqrt(72)

Factor 72:

    72 = 2^3 * 3^2

Separate the factors into pairs because a square root consumes two identical
factors:

    sqrt(72)
    = sqrt(2^3 * 3^2)
    = sqrt(2^2 * 2 * 3^2)
    = 2 * 3 * sqrt(2)
    = 6sqrt(2)

For an nth root, factors are extracted in groups of n.
"""


def prime_factorization(number: int) -> dict[int, int]:
    """
    Return the prime factorization as {prime: exponent}.

    Example:
        72 -> {2: 3, 3: 2}
    """
    if number == 0:
        raise ValueError("Zero does not have a prime factorization.")

    number = abs(number)
    factors: dict[int, int] = {}

    while number % 2 == 0:
        factors[2] = factors.get(2, 0) + 1
        number //= 2

    divisor = 3

    while divisor * divisor <= number:
        while number % divisor == 0:
            factors[divisor] = factors.get(divisor, 0) + 1
            number //= divisor

        divisor += 2

    if number > 1:
        factors[number] = factors.get(number, 0) + 1

    return factors


def format_factorization(factors: dict[int, int]) -> str:
    """Format a prime factorization in readable mathematical notation."""
    terms = []

    for prime, exponent in sorted(factors.items()):
        if exponent == 1:
            terms.append(str(prime))
        else:
            terms.append(f"{prime}^{exponent}")

    return " * ".join(terms)


print("\nPrime factorizations:")
for number in [12, 36, 72, 180, 360, 1024]:
    factors = prime_factorization(number)
    print(f"{number} = {format_factorization(factors)}")


# =============================================================================
# 4. EXACT RADICAL REPRESENTATION
# =============================================================================

"""
A useful exact representation of a real radical is:

    coefficient * root_degree(radical_radicand)

For example:

    sqrt(72) = 6sqrt(2)

can be represented as:

    coefficient = 6
    degree      = 2
    radicand    = 2

Another example:

    cube root(54)
    = cube root(27 * 2)
    = 3 cube root(2)

This representation makes symbolic manipulation possible without external
computer-algebra packages.
"""


@dataclass(frozen=True)
class Radical:
    """
    Represent coefficient * nth_root(radicand).

    The radicand is stored in simplified form whenever created through
    simplify_radical().
    """

    coefficient: int
    degree: int
    radicand: int

    def __post_init__(self) -> None:
        if self.degree <= 0:
            raise ValueError("Degree must be positive.")

        if self.radicand < 0 and self.degree % 2 == 0:
            raise ValueError(
                "An even-degree real radical cannot have a negative radicand."
            )

    def __str__(self) -> str:
        if self.radicand == 1:
            return str(self.coefficient)

        if self.degree == 2:
            root_symbol = "√"
        else:
            root_symbol = f"root{self.degree}"

        if self.coefficient == 1:
            coefficient_part = ""
        elif self.coefficient == -1:
            coefficient_part = "-"
        else:
            coefficient_part = str(self.coefficient)

        if self.degree == 2:
            return f"{coefficient_part}{root_symbol}({self.radicand})"

        return f"{coefficient_part}{root_symbol}({self.radicand})"


def simplify_radical(
    radicand: int,
    degree: int = 2,
    coefficient: int = 1,
) -> Radical:
    """
    Simplify an integer radical exactly.

    Example:
        simplify_radical(72, 2)
        -> 6√(2)

    Algorithm:
    1. Factor the absolute radicand.
    2. Extract groups of 'degree' identical prime factors.
    3. Leave the remaining factors under the radical.
    """
    if degree <= 0:
        raise ValueError("Degree must be positive.")

    if radicand == 0:
        return Radical(0, degree, 1)

    if radicand < 0 and degree % 2 == 0:
        raise ValueError(
            "Negative radicand with an even root is not real."
        )

    sign = -1 if radicand < 0 else 1
    absolute_radicand = abs(radicand)

    factors = prime_factorization(absolute_radicand)

    outside = 1
    inside = 1

    for prime, exponent in factors.items():
        outside *= prime ** (exponent // degree)
        remaining_exponent = exponent % degree
        inside *= prime ** remaining_exponent

    # For odd roots, the negative sign belongs outside the root.
    outside *= sign * coefficient

    # A completely extracted radical has radicand 1.
    return Radical(outside, degree, inside)


print("\nRadical simplification:")

examples = [
    (72, 2),
    (48, 2),
    (200, 2),
    (54, 3),
    (128, 3),
    (432, 3),
    (-54, 3),
]

for radicand, degree in examples:
    simplified = simplify_radical(radicand, degree)
    print(
        f"root{degree}({radicand}) -> {simplified}"
    )


# =============================================================================
# 5. GENERAL ROOT EXTRACTION
# =============================================================================

"""
The extraction rule is:

    nth_root(a^k)
    = a^(k/n)

For integer prime-factor exponents:

    root_n(product p_i^e_i)

extracts:

    p_i^(floor(e_i / n))

and leaves:

    p_i^(e_i mod n)

inside the radical.

This is the generalization of "take pairs out of a square root."
"""


def radical_value(radical: Radical) -> float:
    """Numerically evaluate a Radical object."""
    return radical.coefficient * nth_root_real(
        radical.radicand,
        radical.degree,
    )


print("\nNumerical verification of exact simplification:")

for radicand, degree in [(72, 2), (54, 3), (1024, 5)]:
    simplified = simplify_radical(radicand, degree)
    original = nth_root_real(radicand, degree)
    reduced = radical_value(simplified)

    print(
        f"original={original:.12f}, "
        f"simplified={reduced:.12f}, "
        f"equal={math.isclose(original, reduced)}"
    )


# =============================================================================
# 6. RADICAL LAWS
# =============================================================================

"""
For appropriate real values:

    sqrt(a) * sqrt(b) = sqrt(ab)

provided both sides are defined in the real numbers.

Similarly:

    sqrt(a) / sqrt(b) = sqrt(a/b), b > 0

A crucial warning:

    sqrt(a + b) != sqrt(a) + sqrt(b)

in general.

Example:

    sqrt(9 + 16) = sqrt(25) = 5

but:

    sqrt(9) + sqrt(16) = 3 + 4 = 7

The radical does not distribute over addition.

Multiplication and division behave differently from addition and subtraction.
"""


def demonstrate_radical_laws() -> None:
    a = 9
    b = 16

    print("\nRadical laws:")
    print("sqrt(a) * sqrt(b) =", math.sqrt(a) * math.sqrt(b))
    print("sqrt(a*b) =", math.sqrt(a * b))

    print("\nA false rule:")
    print("sqrt(a+b) =", math.sqrt(a + b))
    print("sqrt(a)+sqrt(b) =", math.sqrt(a) + math.sqrt(b))


demonstrate_radical_laws()


# =============================================================================
# 7. ADDITION AND SUBTRACTION OF RADICALS
# =============================================================================

"""
Like radicals can be combined.

    3sqrt(2) + 5sqrt(2)
    = 8sqrt(2)

Unlike radicals cannot normally be combined:

    sqrt(2) + sqrt(3)

is already simplified.

The important subtlety is that radicals may initially look unlike but become
like after simplification:

    sqrt(8) + sqrt(18)

    = 2sqrt(2) + 3sqrt(2)

    = 5sqrt(2)
"""


def add_radicals(left: Radical, right: Radical) -> Radical:
    """
    Add two radicals when their degree and simplified radicand match.
    """
    if left.degree != right.degree:
        raise ValueError(
            "Radicals have different degrees and cannot be combined directly."
        )

    if left.radicand != right.radicand:
        raise ValueError(
            "Radicals are unlike and cannot be combined."
        )

    return Radical(
        left.coefficient + right.coefficient,
        left.degree,
        left.radicand,
    )


print("\nAdding like radicals:")

r1 = simplify_radical(8)
r2 = simplify_radical(18)

print("sqrt(8) =", r1)
print("sqrt(18) =", r2)

combined = add_radicals(r1, r2)
print("sqrt(8) + sqrt(18) =", combined)


# =============================================================================
# 8. MULTIPLICATION OF RADICALS
# =============================================================================

"""
When radicals have the same degree:

    root_n(a) * root_n(b) = root_n(ab)

Example:

    sqrt(6) * sqrt(15)
    = sqrt(90)
    = 3sqrt(10)

Coefficients multiply normally.
"""


def multiply_radicals(left: Radical, right: Radical) -> Radical:
    """Multiply two integer radicals of the same degree."""
    if left.degree != right.degree:
        raise ValueError(
            "Different-degree radicals require more general exponent handling."
        )

    coefficient = left.coefficient * right.coefficient
    radicand = left.radicand * right.radicand

    return simplify_radical(
        radicand,
        left.degree,
        coefficient,
    )


print("\nMultiplication:")
product = multiply_radicals(
    simplify_radical(6),
    simplify_radical(15),
)
print("sqrt(6) * sqrt(15) =", product)


# =============================================================================
# 9. DIVISION OF RADICALS
# =============================================================================

"""
For nonzero denominators:

    root_n(a) / root_n(b)
    = root_n(a/b)

Exact symbolic representations become more convenient when the numerator and
denominator are represented as prime factors or rational numbers.

For simple integer radicals, we can first simplify both terms and then
rationalize the denominator where appropriate.
"""


def divide_numeric_radicals(
    numerator: Radical,
    denominator: Radical,
) -> float:
    """Numerically divide two real radicals."""
    denominator_value = radical_value(denominator)

    if denominator_value == 0:
        raise ZeroDivisionError("A radical denominator cannot be zero.")

    return radical_value(numerator) / denominator_value


print("\nDivision:")
division_result = divide_numeric_radicals(
    simplify_radical(18),
    simplify_radical(2),
)
print("sqrt(18) / sqrt(2) =", division_result)


# =============================================================================
# 10. RATIONAL EXPONENTS
# =============================================================================

"""
Roots and fractional powers are equivalent:

    a^(1/n) = nth_root(a)

and

    a^(m/n) = nth_root(a^m)

For positive real a:

    a^(m/n) = (nth_root(a))^m

Examples:

    16^(1/2) = 4
    27^(1/3) = 3
    32^(2/5) = 4

For real-number algebra, negative bases require care. Expressions involving
fractional exponents may have different domain restrictions depending on how
they are represented and evaluated.
"""


def rational_power(
    base: float,
    numerator: int,
    denominator: int,
) -> float:
    """
    Evaluate base^(numerator/denominator) as a real quantity.

    The denominator must be positive.
    """
    if denominator <= 0:
        raise ValueError("Exponent denominator must be positive.")

    exponent = Fraction(numerator, denominator)

    # Integer exponents do not require root-domain handling.
    if exponent.denominator == 1:
        return base ** exponent.numerator

    degree = exponent.denominator

    if base < 0 and degree % 2 == 0:
        raise ValueError(
            "The requested rational power is not real for this negative base."
        )

    root = nth_root_real(base, degree)
    return root ** exponent.numerator


print("\nRational exponents:")
for base, numerator, denominator in [
    (16, 1, 2),
    (27, 1, 3),
    (32, 2, 5),
    (81, 3, 4),
]:
    value = rational_power(base, numerator, denominator)
    print(
        f"{base}^({numerator}/{denominator}) = {value}"
    )


# =============================================================================
# 11. RATIONALIZATION
# =============================================================================

"""
Rationalization means transforming a fraction so that the denominator no
longer contains a radical.

Example:

    1 / sqrt(2)

Multiply numerator and denominator by sqrt(2):

    sqrt(2) / 2

The denominator is now rational.

For a binomial denominator:

    1 / (a + sqrt(b))

multiply by the conjugate:

    (a - sqrt(b))

because:

    (a + sqrt(b))(a - sqrt(b))
    = a^2 - b

This uses the difference-of-squares identity.
"""


def rationalize_single_square_root_denominator(
    numerator: int,
    radicand: int,
) -> tuple[int, int, int]:
    """
    Rationalize numerator / sqrt(radicand).

    Returns:
        (new_numerator_coefficient, remaining_radical, denominator)

    Example:
        1/sqrt(2) -> (1, 2, 2)
        representing sqrt(2)/2.
    """
    if radicand <= 0:
        raise ValueError(
            "The radicand must be positive for this real rationalization."
        )

    simplified = simplify_radical(radicand)

    # numerator / (c*sqrt(r))
    # multiply by sqrt(r):
    # numerator*sqrt(r) / (c*r)
    coefficient = simplified.coefficient
    remaining = simplified.radicand

    denominator = coefficient * coefficient * remaining
    new_numerator = numerator * coefficient

    return new_numerator, remaining, denominator


print("\nRationalization:")
new_numerator, remaining_radical, denominator = (
    rationalize_single_square_root_denominator(1, 2)
)

print(
    f"1/sqrt(2) = sqrt({remaining_radical})/{denominator}"
)


def rationalize_conjugate_denominator(
    numerator: int,
    a: int,
    radicand: int,
) -> tuple[int, int, int]:
    """
    Rationalize numerator / (a + sqrt(radicand)).

    Returns a representation:

        coefficient * sqrt(radicand) + rational_part
        -------------------------------------------
                         denominator

    The representation is returned as:
        (radical_numerator_coefficient,
         rational_numerator,
         denominator)

    This function assumes the denominator is nonzero and radicand >= 0.
    """
    if radicand < 0:
        raise ValueError("This function expects a non-negative radicand.")

    denominator = a * a - radicand

    if denominator == 0:
        raise ZeroDivisionError(
            "The original denominator becomes zero."
        )

    # numerator * (a - sqrt(radicand))
    # ---------------------------------
    #       a^2 - radicand
    #
    # Therefore:
    # radical coefficient = -numerator
    # rational coefficient = numerator*a
    return -numerator, numerator * a, denominator


print("\nConjugate rationalization:")
radical_coefficient, rational_numerator, denominator = (
    rationalize_conjugate_denominator(1, 3, 2)
)

print(
    "1/(3+sqrt(2)) = "
    f"({rational_numerator} "
    f"+ ({radical_coefficient})sqrt(2))/{denominator}"
)


# =============================================================================
# 12. CONJUGATES AND DIFFERENCE OF SQUARES
# =============================================================================

"""
For:

    A + B

the conjugate is:

    A - B

Their product is:

    (A+B)(A-B) = A^2 - B^2

This is especially useful when B is a radical.

Example:

    (3 + sqrt(5))(3 - sqrt(5))
    = 9 - 5
    = 4
"""


def conjugate_product(a: float, b: float) -> float:
    """Compute (a+b)(a-b) and demonstrate difference of squares."""
    return (a + b) * (a - b)


print("\nConjugate product:")
print("(3+sqrt(5))(3-sqrt(5)) =", conjugate_product(3, math.sqrt(5)))


# =============================================================================
# 13. NESTED RADICALS
# =============================================================================

"""
Nested radicals contain one radical inside another:

    sqrt(2 + sqrt(3))

Some nested radicals simplify elegantly, but many do not.

A classic pattern is:

    sqrt(a + 2sqrt(b))

Try to represent it as:

    sqrt(m) + sqrt(n)

Squaring gives:

    m + n + 2sqrt(mn)

Therefore:

    m + n = a
    mn = b

This method works when suitable m and n exist.
"""


def simplify_nested_square_root(
    a: int,
    b: int,
) -> Optional[tuple[int, int]]:
    """
    Attempt to simplify:

        sqrt(a + 2sqrt(b))

into:

        sqrt(m) + sqrt(n)

for non-negative integer m and n.

Returns (m, n) if an integer solution exists.
"""
    if b < 0:
        return None

    # m+n=a and mn=b.
    # Therefore m and n are roots of:
    # t^2 - a*t + b = 0
    discriminant = a * a - 4 * b

    if discriminant < 0:
        return None

    root_discriminant = math.isqrt(discriminant)

    if root_discriminant * root_discriminant != discriminant:
        return None

    if (a + root_discriminant) % 2 != 0:
        return None

    m = (a + root_discriminant) // 2
    n = (a - root_discriminant) // 2

    if m < 0 or n < 0:
        return None

    return m, n


print("\nNested radical simplification:")
nested = simplify_nested_square_root(5, 6)

if nested is not None:
    m, n = nested
    print("sqrt(5 + 2sqrt(6)) = sqrt(3) + sqrt(2)")
else:
    print("No integer nested-radical decomposition found.")


# =============================================================================
# 14. EQUATIONS INVOLVING RADICALS
# =============================================================================

"""
Radical equations require domain analysis and verification.

Example:

    sqrt(x + 1) = 3

Square both sides:

    x + 1 = 9
    x = 8

Verification:

    sqrt(8+1) = 3

A more subtle example:

    sqrt(x) = x - 2

Squaring gives:

    x = (x-2)^2

which can produce candidate solutions that must be checked in the original
equation.

Squaring an equation is not automatically reversible because:

    sqrt(x)^2 = x

but:

    x^2 = y^2

implies:

    x = y OR x = -y

Squaring can introduce extraneous solutions.
"""


def solve_sqrt_linear_equation(
    constant: float,
    right_slope: float,
    right_intercept: float,
) -> list[float]:
    """
    Solve:

        sqrt(x + constant) = right_slope*x + right_intercept

for real x using algebraic squaring followed by original-equation
verification.

This is a deliberately educational implementation rather than a general
symbolic equation solver.
    """
    # sqrt(x+c) = m*x+b
    #
    # Domain:
    # x+c >= 0
    #
    # Squaring:
    # x+c = (m*x+b)^2
    #
    # Rearranged:
    # m^2*x^2 + 2mb*x + b^2 - x - c = 0

    m = right_slope
    b = right_intercept
    c = constant

    A = m * m
    B = 2 * m * b - 1
    C = b * b - c

    candidates: list[float] = []

    if math.isclose(A, 0.0):
        if math.isclose(B, 0.0):
            return []

        candidate = -C / B
        candidates.append(candidate)
    else:
        discriminant = B * B - 4 * A * C

        if discriminant < 0:
            return []

        sqrt_discriminant = math.sqrt(discriminant)

        candidates.append(
            (-B + sqrt_discriminant) / (2 * A)
        )

        candidates.append(
            (-B - sqrt_discriminant) / (2 * A)
        )

    solutions = []

    for candidate in candidates:
        if candidate + c < -1e-10:
            continue

        left = math.sqrt(max(0.0, candidate + c))
        right = m * candidate + b

        if math.isclose(left, right, rel_tol=1e-10, abs_tol=1e-10):
            if not any(
                math.isclose(candidate, existing)
                for existing in solutions
            ):
                solutions.append(candidate)

    return solutions


print("\nRadical equation:")
solutions = solve_sqrt_linear_equation(1, 0, 3)
print("sqrt(x+1) = 3 ->", solutions)

solutions = solve_sqrt_linear_equation(0, 1, -2)
print("sqrt(x) = x-2 ->", solutions)


# =============================================================================
# 15. ABSOLUTE VALUE AND EVEN ROOTS
# =============================================================================

"""
A subtle but fundamental identity is:

    sqrt(x^2) = |x|

NOT:

    sqrt(x^2) = x

For x >= 0:

    |x| = x

For x < 0:

    |x| = -x

Example:

    sqrt((-7)^2)
    = sqrt(49)
    = 7

not -7.

More generally:

    sqrt((f(x))^2) = |f(x)|
"""


def square_root_of_square(value: float) -> float:
    """Demonstrate sqrt(x^2) = |x|."""
    return math.sqrt(value * value)


print("\nAbsolute-value behavior:")
for value in [-10, -2.5, 0, 3, 10]:
    print(
        f"sqrt(({value})^2) = {square_root_of_square(value)}, "
        f"|{value}| = {abs(value)}"
    )


# =============================================================================
# 16. DOMAIN RESTRICTIONS
# =============================================================================

"""
For real-valued radicals:

Even root:
    root_2k(x) is real only when x >= 0.

Odd root:
    root_(2k+1)(x) is real for every real x.

For rational expressions containing radicals, the denominator must also be
nonzero.

Example:

    1/sqrt(x-3)

requires:

    x-3 > 0

not merely x-3 >= 0, because the denominator cannot equal zero.

Therefore:

    x > 3
"""


def domain_examples() -> None:
    examples = [
        ("sqrt(x)", "x >= 0"),
        ("1/sqrt(x)", "x > 0"),
        ("cuberoot(x)", "all real x"),
        ("sqrt(x-3)", "x >= 3"),
        ("1/sqrt(x-3)", "x > 3"),
    ]

    print("\nRepresentative domains:")
    for expression, domain in examples:
        print(f"{expression:20s} : {domain}")


domain_examples()


# =============================================================================
# 17. ROOTS OF UNITY AND COMPLEX ROOTS
# =============================================================================

"""
Real radicals are only part of the broader theory.

For a complex number z, the nth roots are solutions of:

    w^n = z

Write:

    z = r(cos(theta) + i sin(theta))

Then the nth roots are:

    r^(1/n) [
        cos((theta + 2*pi*k)/n)
        + i sin((theta + 2*pi*k)/n)
    ]

where:

    k = 0, 1, ..., n-1

Therefore every nonzero complex number has exactly n distinct complex nth
roots.

Python's cmath provides principal complex roots through complex powers.
"""


def principal_complex_root(value: complex, degree: int) -> complex:
    """Return the principal complex nth root."""
    if degree <= 0:
        raise ValueError("Degree must be positive.")

    return value ** (1 / degree)


def all_complex_roots(value: complex, degree: int) -> list[complex]:
    """
    Return all degree-th roots of a nonzero complex number.

    Uses polar form:
        z = r * exp(i*theta)
    """
    if degree <= 0:
        raise ValueError("Degree must be positive.")

    if value == 0:
        return [0j]

    radius = abs(value)
    angle = cmath.phase(value)

    roots = []

    for k in range(degree):
        root_radius = radius ** (1 / degree)
        root_angle = (angle + 2 * math.pi * k) / degree

        root = cmath.rect(root_radius, root_angle)
        roots.append(root)

    return roots


print("\nComplex roots of unity:")
roots = all_complex_roots(1 + 0j, 4)

for index, root in enumerate(roots):
    print(f"root {index + 1}: {root}")


# =============================================================================
# 18. PRINCIPAL ROOT VS ALL ROOTS
# =============================================================================

"""
For x^n = a:

- The equation asks for all solutions.
- The notation root_n(a) often denotes a principal root.

For positive real a:

    x^2 = a

has:

    x = +sqrt(a)
    x = -sqrt(a)

but:

    sqrt(a)

means only the positive root.

For odd powers:

    x^3 = 27

has exactly one real solution:

    x = 3

Complex numbers add additional roots for polynomial equations.
"""


def solve_square_equation(a: float) -> tuple[float, float]:
    """Return both real solutions of x^2 = a for a >= 0."""
    if a < 0:
        raise ValueError("There are no real solutions.")

    root = math.sqrt(a)
    return root, -root


print("\nPrincipal root versus equation solutions:")
print("sqrt(25) =", math.sqrt(25))
print("Solutions of x^2=25:", solve_square_equation(25))


# =============================================================================
# 19. APPROXIMATION VS EXACT FORM
# =============================================================================

"""
A radical such as:

    sqrt(2)

is irrational and cannot be represented exactly by a finite decimal.

A floating-point value such as:

    1.4142135623730951

is an approximation.

Exact symbolic form is useful for algebraic manipulation.
Numerical form is useful for computation.

The two forms serve different purposes.
"""


def compare_exact_and_approximate() -> None:
    exact_expression = "sqrt(2)"
    approximate_value = math.sqrt(2)

    print("\nExact vs approximate:")
    print("Exact symbolic form:", exact_expression)
    print("Floating-point approximation:", approximate_value)
    print("Rounded to 5 decimals:", round(approximate_value, 5))


compare_exact_and_approximate()


# =============================================================================
# 20. FLOATING-POINT PRECISION
# =============================================================================

"""
Floating-point arithmetic has finite precision.

For example, mathematically:

    sqrt(2)^2 = 2

but the computed value may differ by a tiny amount.

Use math.isclose() instead of exact == comparisons when validating numerical
results that involve irrational numbers or floating-point operations.
"""


def floating_point_demo() -> None:
    value = math.sqrt(2)

    print("\nFloating-point validation:")
    print("sqrt(2)^2 =", value * value)
    print("Exact equality:", value * value == 2)
    print(
        "Approximate equality:",
        math.isclose(value * value, 2.0, rel_tol=1e-12)
    )


floating_point_demo()


# =============================================================================
# 21. EXACT SQUARE-ROOT FRACTIONS
# =============================================================================

"""
Radicals frequently occur in fractions.

For example:

    sqrt(50) / 10
    = 5sqrt(2) / 10
    = sqrt(2) / 2

Exact arithmetic with Fraction can preserve rational coefficients.
"""


def simplify_square_root_fraction(
    numerator: int,
    denominator: int,
) -> Radical:
    """
    Simplify sqrt(numerator / denominator) conceptually for positive integers.

    The result is represented as a coefficient * sqrt(radicand), assuming the
    denominator is a perfect square after reduction where possible.
    """
    if denominator <= 0:
        raise ValueError("Denominator must be positive.")

    if numerator < 0:
        raise ValueError("This function handles real square roots only.")

    if numerator == 0:
        return Radical(0, 2, 1)

    fraction = Fraction(numerator, denominator)

    numerator_root = simplify_radical(fraction.numerator, 2)
    denominator_root = simplify_radical(fraction.denominator, 2)

    # If the denominator is a perfect square, absorb its root into the
    # coefficient. Otherwise, this educational function leaves the expression
    # to the general rationalization machinery.
    if denominator_root.radicand == 1:
        return Radical(
            numerator_root.coefficient,
            2,
            numerator_root.radicand * denominator_root.coefficient ** 0,
        )

    # Fallback representation:
    # sqrt(p/q) = sqrt(p*q)/q
    transformed = simplify_radical(
        fraction.numerator * fraction.denominator,
        2,
    )

    return Radical(
        transformed.coefficient,
        2,
        transformed.radicand,
    )


print("\nFractional radical example:")
print(
    "sqrt(2/8) numerically =",
    math.sqrt(Fraction(2, 8)),
)


# =============================================================================
# 22. RADICAL COMPARISON WITHOUT APPROXIMATION
# =============================================================================

"""
When comparing non-negative square roots:

    sqrt(a) < sqrt(b)

if and only if:

    a < b

because the square-root function is increasing on [0, infinity).

Thus:

    sqrt(17) < sqrt(20)

can be established without calculating either decimal approximation.

Similar monotonicity exists for odd roots over all real numbers and even roots
over their non-negative domains.
"""


def compare_square_roots(
    left_radicand: int,
    right_radicand: int,
) -> int:
    """
    Compare sqrt(left_radicand) and sqrt(right_radicand).

    Returns:
        -1 if left < right
         0 if equal
         1 if left > right
    """
    if left_radicand < 0 or right_radicand < 0:
        raise ValueError("Square-root radicands must be non-negative.")

    return (
        left_radicand > right_radicand
    ) - (
        left_radicand < right_radicand
    )


print("\nExact radical comparison:")
print("sqrt(17) compared with sqrt(20):",
      compare_square_roots(17, 20))


# =============================================================================
# 23. COMMON INVALID ALGEBRAIC TRANSFORMATIONS
# =============================================================================

"""
These identities are generally FALSE:

    sqrt(a+b) = sqrt(a) + sqrt(b)

    sqrt(a-b) = sqrt(a) - sqrt(b)

    1/(a+b) = 1/a + 1/b

The first two fail because square roots do not distribute over addition or
subtraction.

The correct multiplicative identity is:

    sqrt(ab) = sqrt(a)sqrt(b)

under appropriate real-domain conditions.

Another common error:

    sqrt(x^2) = x

The correct identity is:

    sqrt(x^2) = |x|
"""


def show_common_mistakes() -> None:
    a = 9
    b = 16

    print("\nCommon mistakes:")
    print("sqrt(9+16) =", math.sqrt(a + b))
    print("sqrt(9)+sqrt(16) =", math.sqrt(a) + math.sqrt(b))

    x = -7
    print("\nsqrt(x^2) for x=-7:", math.sqrt(x * x))
    print("x:", x)
    print("|x|:", abs(x))


show_common_mistakes()


# =============================================================================
# 24. EDGE CASES
# =============================================================================

"""
Important edge cases include:

1. Zero:
       sqrt(0) = 0

2. Negative square-root radicand:
       not real

3. Negative odd-root radicand:
       real

4. Root degree of zero or negative:
       invalid

5. Zero denominator:
       division by zero

6. Even root of a negative number:
       complex result exists, but no real result

7. Very large integers:
       Python integer arithmetic remains exact, but floating-point
       approximations may lose precision.

8. Very small floating-point values:
       underflow and numerical precision can become relevant.
"""


def test_edge_cases() -> None:
    print("\nEdge cases:")

    print("sqrt(0) =", math.sqrt(0))
    print("cuberoot(-8) =", cube_root(-8))

    try:
        nth_root_real(-16, 2)
    except ValueError as error:
        print("sqrt(-16):", error)

    try:
        nth_root_real(16, 0)
    except ValueError as error:
        print("0th root:", error)

    try:
        divide_numeric_radicals(
            simplify_radical(5),
            simplify_radical(0),
        )
    except ZeroDivisionError as error:
        print("Division by zero:", error)


test_edge_cases()


# =============================================================================
# 25. RADICAL EXPRESSIONS WITH SYMBOLIC-LIKE STRUCTURE
# =============================================================================

"""
A symbolic radical expression can be viewed as a collection of terms:

    3sqrt(2) + 5sqrt(3) - 7sqrt(2)

Combining like terms gives:

    -4sqrt(2) + 5sqrt(3)

A dictionary keyed by (degree, radicand) is a simple way to implement this
idea.
"""


def combine_radical_terms(
    terms: Iterable[Radical],
) -> list[Radical]:
    """Combine radicals with matching degree and radicand."""
    grouped: dict[tuple[int, int], int] = {}

    for term in terms:
        key = (term.degree, term.radicand)
        grouped[key] = grouped.get(key, 0) + term.coefficient

    result = []

    for (degree, radicand), coefficient in sorted(grouped.items()):
        if coefficient != 0:
            result.append(
                Radical(coefficient, degree, radicand)
            )

    return result


print("\nCombining radical terms:")

terms = [
    simplify_radical(8),
    simplify_radical(18),
    simplify_radical(12),
]

for term in terms:
    print("term:", term)

combined_terms = combine_radical_terms(terms)

print("Combined:")
for term in combined_terms:
    print(term)


# =============================================================================
# 26. MULTIPLICATIVE PROPERTY WITH DOMAIN CARE
# =============================================================================

"""
For non-negative real a and b:

    sqrt(ab) = sqrt(a)sqrt(b)

But blindly extending this rule to arbitrary complex numbers while using
principal complex roots can fail.

For example, principal complex square roots do not obey the same unrestricted
multiplicative rule as real non-negative square roots.

This distinction matters in complex symbolic computation.
"""


def demonstrate_complex_branch_behavior() -> None:
    a = -1 + 0j
    b = -1 + 0j

    left = cmath.sqrt(a * b)
    right = cmath.sqrt(a) * cmath.sqrt(b)

    print("\nComplex principal-root behavior:")
    print("sqrt((-1)*(-1)) =", left)
    print("sqrt(-1)*sqrt(-1) =", right)


demonstrate_complex_branch_behavior()


# =============================================================================
# 27. ROOT EXTRACTION ALGORITHM WITHOUT FLOATING POINT
# =============================================================================

"""
For exact integer nth-root calculations, binary search is more reliable than
floating-point exponentiation.

For a non-negative integer N, we seek the largest integer r satisfying:

    r^n <= N

If r^n == N, N is a perfect nth power.

This avoids floating-point rounding errors.
"""


def integer_nth_root_floor(number: int, degree: int) -> int:
    """
    Return floor(number^(1/degree)) exactly for non-negative integers.
    """
    if number < 0:
        raise ValueError("Number must be non-negative.")

    if degree <= 0:
        raise ValueError("Degree must be positive.")

    if number in (0, 1):
        return number

    low = 0
    high = 1

    # Find an upper bound.
    while high ** degree <= number:
        high *= 2

    # Binary search.
    while low + 1 < high:
        middle = (low + high) // 2

        if middle ** degree <= number:
            low = middle
        else:
            high = middle

    return low


print("\nExact integer nth-root algorithm:")
for number, degree in [
    (100, 2),
    (101, 2),
    (1000, 3),
    (1001, 3),
    (10**18, 6),
]:
    root = integer_nth_root_floor(number, degree)
    print(
        f"floor(root{degree}({number})) = {root}"
    )


# =============================================================================
# 28. PERFECT POWER TEST USING EXACT INTEGER ROOT
# =============================================================================

def is_perfect_power_exact(number: int, degree: int) -> bool:
    """Exact perfect-power test using integer arithmetic."""
    if number < 0:
        if degree % 2 == 0:
            return False

        return (
            integer_nth_root_floor(-number, degree) ** degree
            == -number
        )

    root = integer_nth_root_floor(number, degree)
    return root ** degree == number


print("\nExact perfect-power tests:")
for number, degree in [
    (64, 2),
    (65, 2),
    (125, 3),
    (-125, 3),
    (-16, 2),
]:
    print(
        f"{number} is a perfect {degree}-th power:",
        is_perfect_power_exact(number, degree),
    )


# =============================================================================
# 29. RADICAL SIMPLIFICATION WITH LARGE INTEGERS
# =============================================================================

"""
Exact prime factorization can become expensive for very large composite
integers.

For ordinary educational and moderate-size computational problems, trial
division is straightforward.

For production-grade large-integer factorization, specialized algorithms are
needed. The complexity of integer factorization is a separate computational
topic and should not be confused with merely calculating a numerical root.
"""


def radical_simplification_report(
    radicand: int,
    degree: int,
) -> None:
    """Display the complete simplification process."""
    if radicand == 0:
        print("0 -> 0")
        return

    factors = prime_factorization(radicand)
    simplified = simplify_radical(radicand, degree)

    print("Input:", f"root{degree}({radicand})")
    print("Prime factorization:", format_factorization(factors))
    print("Simplified:", simplified)
    print("Numerical value:", radical_value(simplified))


print("\nDetailed simplification report:")
radical_simplification_report(360, 2)
radical_simplification_report(432, 3)


# =============================================================================
# 30. ROOT INDEX RULES
# =============================================================================

"""
The root index matters.

For example:

    sqrt(64) = 8
    cube_root(64) = 4
    fourth_root(64) = 2sqrt(2)

A radical's degree cannot be ignored.

For powers:

    root_n(a^n)

equals:

    |a|       when n is even
    a         when n is odd

over the real numbers.

The absolute value in the even case is essential.
"""


def root_of_power(base: int, degree: int) -> float:
    """Demonstrate the principal real root of base^degree."""
    power = base ** degree
    return nth_root_real(power, degree)


print("\nRoot-of-power rule:")
for base in [-3, -2, 2, 3]:
    print(
        f"base={base}, even degree 2 ->",
        root_of_power(base, 2),
    )


# =============================================================================
# 31. RELATION TO EXPONENT LAWS
# =============================================================================

"""
Radical rules are consequences of exponent laws.

For positive a:

    root_n(a) = a^(1/n)

Therefore:

    root_n(a) * root_n(b)
    = a^(1/n) * b^(1/n)
    = (ab)^(1/n)

Also:

    root_n(a^m)
    = a^(m/n)

And:

    root_m(root_n(a))
    = a^(1/(mn))

This provides a unified framework for radicals and exponents.
"""


def exponent_rule_demo() -> None:
    a = 64

    left = nth_root_real(nth_root_real(a, 2), 3)
    right = nth_root_real(a, 6)

    print("\nNested-root exponent rule:")
    print("6th root(64) =", right)
    print("cube root(square root(64)) =", left)


exponent_rule_demo()


# =============================================================================
# 32. WHEN RADICALS CANNOT BE COMBINED
# =============================================================================

"""
These are unlike radicals:

    sqrt(2)
    sqrt(3)

They cannot be added into:

    sqrt(5)

Likewise:

    sqrt(2) + sqrt(8)

can be combined only after simplifying sqrt(8).

The structural form of a radical matters more than the original radicand.
"""


def can_combine_radicals(left: Radical, right: Radical) -> bool:
    """Return True if two simplified radicals are like terms."""
    return (
        left.degree == right.degree
        and left.radicand == right.radicand
    )


print("\nLike versus unlike radicals:")
left = simplify_radical(8)
right = simplify_radical(18)
third = simplify_radical(3)

print(left, "and", right, "can combine:", can_combine_radicals(left, right))
print(left, "and", third, "can combine:", can_combine_radicals(left, third))


# =============================================================================
# 33. RADICALS IN GEOMETRY
# =============================================================================

"""
Radicals naturally arise in geometry.

For a right triangle:

    a^2 + b^2 = c^2

so:

    c = sqrt(a^2 + b^2)

Example:

    a = 3
    b = 4
    c = sqrt(9+16) = 5

For a square with side s, the diagonal is:

    d = s*sqrt(2)

For a cube with side s, the space diagonal is:

    d = s*sqrt(3)
"""


def pythagorean_hypotenuse(a: float, b: float) -> float:
    """Calculate a right triangle's hypotenuse."""
    return math.sqrt(a * a + b * b)


def square_diagonal(side: float) -> float:
    """Calculate the diagonal of a square."""
    if side < 0:
        raise ValueError("Side length cannot be negative.")

    return side * math.sqrt(2)


def cube_space_diagonal(side: float) -> float:
    """Calculate the space diagonal of a cube."""
    if side < 0:
        raise ValueError("Side length cannot be negative.")

    return side * math.sqrt(3)


print("\nGeometric applications:")
print("3-4-5 triangle hypotenuse:", pythagorean_hypotenuse(3, 4))
print("Square diagonal, side 10:", square_diagonal(10))
print("Cube space diagonal, side 10:", cube_space_diagonal(10))


# =============================================================================
# 34. RADICALS IN DISTANCE FORMULAS
# =============================================================================

"""
In two dimensions:

    distance = sqrt((x2-x1)^2 + (y2-y1)^2)

In three dimensions:

    distance = sqrt(
        (x2-x1)^2 +
        (y2-y1)^2 +
        (z2-z1)^2
    )

Exact radical forms can be preferable when coordinates are integers.
"""


def distance_2d(
    x1: int,
    y1: int,
    x2: int,
    y2: int,
) -> float:
    """Euclidean distance in two dimensions."""
    return math.sqrt(
        (x2 - x1) ** 2 +
        (y2 - y1) ** 2
    )


def distance_3d(
    x1: int,
    y1: int,
    z1: int,
    x2: int,
    y2: int,
    z2: int,
) -> float:
    """Euclidean distance in three dimensions."""
    return math.sqrt(
        (x2 - x1) ** 2 +
        (y2 - y1) ** 2 +
        (z2 - z1) ** 2
    )


print("\nDistance applications:")
print("Distance between (0,0) and (3,4):",
      distance_2d(0, 0, 3, 4))

print("Distance between (0,0,0) and (1,2,2):",
      distance_3d(0, 0, 0, 1, 2, 2))


# =============================================================================
# 35. RADICALS IN THE QUADRATIC FORMULA
# =============================================================================

"""
The quadratic formula is:

    x = (-b ± sqrt(b^2 - 4ac)) / (2a)

The discriminant:

    D = b^2 - 4ac

determines the nature of the roots:

    D > 0  -> two distinct real roots
    D = 0  -> one repeated real root
    D < 0  -> two complex conjugate roots

Radicals appear naturally when D is positive but not a perfect square.
"""


def quadratic_roots(
    a: float,
    b: float,
    c: float,
) -> tuple[complex, complex]:
    """
    Solve ax^2 + bx + c = 0.

    Complex arithmetic is used so the function can handle all discriminants.
    """
    if a == 0:
        raise ValueError("This is not a quadratic equation.")

    discriminant = b * b - 4 * a * c

    sqrt_discriminant = cmath.sqrt(discriminant)

    root1 = (-b + sqrt_discriminant) / (2 * a)
    root2 = (-b - sqrt_discriminant) / (2 * a)

    return root1, root2


print("\nQuadratic-formula applications:")

for coefficients in [
    (1, -5, 6),
    (1, 0, -2),
    (1, 0, 1),
]:
    print(
        f"{coefficients[0]}x² + {coefficients[1]}x + "
        f"{coefficients[2]} = 0 ->",
        quadratic_roots(*coefficients),
    )


# =============================================================================
# 36. ERROR HANDLING PRINCIPLES
# =============================================================================

"""
Robust mathematical software should distinguish:

- Invalid input
- Undefined real operation
- Division by zero
- Complex-valued result
- Numerical approximation

Returning a misleading number is usually worse than raising an exception.

Examples:

    sqrt(-4) in real arithmetic -> ValueError
    sqrt(-4) in complex arithmetic -> 2j
    1/0 -> ZeroDivisionError
"""


def safe_real_square_root(value: float) -> Optional[float]:
    """
    Return a real square root or None when no real root exists.

    This wrapper is useful when absence of a real result is an expected
    computational outcome rather than an exceptional program state.
    """
    if value < 0:
        return None

    return math.sqrt(value)


print("\nSafe real square-root wrapper:")
print("sqrt(16) =", safe_real_square_root(16))
print("sqrt(-16) =", safe_real_square_root(-16))


# =============================================================================
# 37. TESTING RADICAL SIMPLIFICATION
# =============================================================================

"""
Mathematical code should be tested with:

- Perfect powers
- Non-perfect powers
- Prime numbers
- Composite numbers
- Zero
- Negative values for odd roots
- Negative values for even roots
- Large integers
- Multiple degrees

The key invariant for simplification is:

    value(original radical) == value(simplified radical)

within exact arithmetic where possible and within a numerical tolerance when
floating-point evaluation is involved.
"""


def test_radical_simplification() -> None:
    test_cases = [
        (0, 2),
        (1, 2),
        (4, 2),
        (8, 2),
        (72, 2),
        (100, 2),
        (125, 3),
        (54, 3),
        (-125, 3),
        (1024, 5),
    ]

    for radicand, degree in test_cases:
        original = nth_root_real(radicand, degree)
        simplified = simplify_radical(radicand, degree)
        reconstructed = radical_value(simplified)

        assert math.isclose(
            original,
            reconstructed,
            rel_tol=1e-10,
            abs_tol=1e-10,
        ), (
            f"Failed: root{degree}({radicand}) -> {simplified}"
        )


test_radical_simplification()
print("\nAll radical simplification tests passed.")


# =============================================================================
# 38. TESTING DOMAIN VALIDATION
# =============================================================================

def test_domain_validation() -> None:
    assert nth_root_real(27, 3) == 3
    assert nth_root_real(-27, 3) == -3

    try:
        nth_root_real(-27, 2)
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Negative even-degree root should fail in real arithmetic."
        )


test_domain_validation()
print("All domain-validation tests passed.")


# =============================================================================
# 39. PERFORMANCE CONSIDERATIONS
# =============================================================================

"""
Different tasks require different algorithms.

Numerical square root:
    math.sqrt()
    Highly optimized and generally preferable for numerical work.

Exact integer square root:
    math.isqrt()
    Exact and efficient.

Exact nth root:
    Binary search can guarantee correctness.

Symbolic simplification:
    Prime factorization is conceptually simple but factorization itself can be
    expensive for very large integers.

Floating-point nth roots:
    Fast but susceptible to rounding issues around perfect powers.

General principle:
Use exact integer arithmetic when correctness of an integer result matters.
Use floating-point arithmetic when approximate numerical evaluation is the
actual objective.
"""


def performance_style_square_root(number: int) -> tuple[int, float]:
    """Compare exact integer and floating-point square-root calculations."""
    exact_floor = math.isqrt(number)
    approximate = math.sqrt(number)

    return exact_floor, approximate


print("\nPerformance-oriented numerical example:")
print(
    "sqrt(10^12):",
    performance_style_square_root(10**12),
)


# =============================================================================
# 40. SECURITY AND INPUT VALIDATION
# =============================================================================

"""
Mathematical functions may be used with external input.

Do not use eval() to interpret user-entered mathematical expressions.

Unsafe approach:

    eval(user_input)

can execute arbitrary Python code.

Safer design:
- Parse only permitted numeric fields.
- Validate root degree.
- Validate denominator.
- Restrict acceptable ranges when resource consumption matters.
- Use explicit functions rather than dynamic code evaluation.

The functions in this script accept structured Python values instead of
executing arbitrary expressions.
"""


def validated_nth_root_input(
    value: float,
    degree: int,
) -> float:
    """Validate externally supplied root parameters."""
    if not isinstance(degree, int):
        raise TypeError("Degree must be an integer.")

    if degree < 1:
        raise ValueError("Degree must be at least 1.")

    if not math.isfinite(value):
        raise ValueError("Value must be finite.")

    return nth_root_real(value, degree)


print("\nValidated input:")
print("validated_nth_root_input(81, 4) =",
      validated_nth_root_input(81, 4))


# =============================================================================
# 41. ADVANCED: PRIME-EXPONENT REPRESENTATION
# =============================================================================

"""
A radical can be represented through prime exponents.

For example:

    sqrt(72)

with:

    72 = 2^3 * 3^2

becomes:

    outside:
        2^(3//2) * 3^(2//2)
        = 2 * 3
        = 6

    inside:
        2^(3%2) * 3^(2%2)
        = 2

giving:

    6sqrt(2)

This representation generalizes cleanly to any root degree.
"""


def radical_prime_exponent_decomposition(
    radicand: int,
    degree: int,
) -> tuple[int, dict[int, int]]:
    """
    Return:
        outside coefficient
        inside prime-exponent dictionary
    """
    if radicand == 0:
        return 0, {}

    sign = -1 if radicand < 0 else 1

    factors = prime_factorization(radicand)

    outside = sign
    inside: dict[int, int] = {}

    for prime, exponent in factors.items():
        outside *= prime ** (exponent // degree)

        remainder = exponent % degree

        if remainder:
            inside[prime] = remainder

    return outside, inside


print("\nPrime-exponent radical decomposition:")
outside, inside = radical_prime_exponent_decomposition(360, 2)

print("360, degree 2")
print("Outside coefficient:", outside)
print("Inside factors:", inside)


# =============================================================================
# 42. ADVANCED: RADICAL CANONICALIZATION
# =============================================================================

"""
Canonicalization means reducing mathematically equivalent representations to
a standard form.

For example:

    sqrt(8)
    2sqrt(2)

should be converted to the same internal representation:

    coefficient = 2
    degree = 2
    radicand = 2

Canonicalization makes equality checks and term combination much easier.
"""


def canonical_radical(
    coefficient: int,
    degree: int,
    radicand: int,
) -> Radical:
    """Return a canonical simplified Radical."""
    return simplify_radical(
        radicand,
        degree,
        coefficient,
    )


print("\nCanonical forms:")
print("sqrt(8) ->", canonical_radical(1, 2, 8))
print("2sqrt(2) ->", canonical_radical(2, 2, 2))


# =============================================================================
# 43. ADVANCED: RADICAL EQUALITY
# =============================================================================

"""
For canonical integer radicals:

    c1 * root_n(r1)
    c2 * root_n(r2)

are directly comparable structurally if both have the same degree and
radicand.

This is safer than comparing floating-point approximations when exact
integer structure is available.
"""


def radicals_equal(left: Radical, right: Radical) -> bool:
    """Check exact equality of canonical radical representations."""
    left = canonical_radical(
        left.coefficient,
        left.degree,
        left.radicand,
    )

    right = canonical_radical(
        right.coefficient,
        right.degree,
        right.radicand,
    )

    return left == right


print("\nExact radical equality:")
print(
    "sqrt(8) == 2sqrt(2):",
    radicals_equal(
        simplify_radical(8),
        simplify_radical(2, 2, 2),
    ),
)


# =============================================================================
# 44. ADVANCED: ROOTS OF NEGATIVE NUMBERS
# =============================================================================

"""
Over the real numbers:

    sqrt(-9)

is undefined.

Over the complex numbers:

    sqrt(-9) = 3i

The imaginary unit satisfies:

    i^2 = -1

Python represents complex values using j:

    3j

The choice between real and complex arithmetic should be explicit in
software design.
"""


def complex_square_root_of_negative(value: float) -> complex:
    """Return the principal complex square root."""
    return cmath.sqrt(complex(value))


print("\nComplex square root:")
print("sqrt(-9) over complex numbers =",
      complex_square_root_of_negative(-9))


# =============================================================================
# 45. ADVANCED: ALL NTH ROOTS OF A COMPLEX NUMBER
# =============================================================================

"""
For:

    z = r e^(i theta)

the nth roots are:

    r^(1/n) e^(i(theta + 2pi*k)/n)

for k = 0,...,n-1.

The roots lie evenly around a circle centered at the origin.
"""


def verify_complex_roots(
    value: complex,
    degree: int,
) -> None:
    """Verify numerically that each generated root satisfies w^n = value."""
    roots = all_complex_roots(value, degree)

    print(
        f"\nVerification of all {degree} complex roots for {value}:"
    )

    for root in roots:
        reconstructed = root ** degree
        print(
            f"root={root}, "
            f"root^{degree}={reconstructed}, "
            f"valid={cmath.isclose(reconstructed, value, abs_tol=1e-9)}"
        )


verify_complex_roots(1 + 0j, 5)


# =============================================================================
# 46. ADVANCED: RADICALS AND TRIGONOMETRY
# =============================================================================

"""
Exact trigonometric values often contain radicals.

Examples:

    sin(45°) = sqrt(2)/2
    cos(45°) = sqrt(2)/2

    sin(30°) = 1/2
    cos(60°) = 1/2

    sin(60°) = sqrt(3)/2
    cos(30°) = sqrt(3)/2

These values arise from geometry and are another major source of radicals in
mathematics.
"""


def degree_to_radian(degrees: float) -> float:
    """Convert degrees to radians."""
    return math.radians(degrees)


print("\nTrigonometric radical examples:")
print("sin(45°) numerical =", math.sin(degree_to_radian(45)))
print("exact form          = sqrt(2)/2")

print("cos(30°) numerical =", math.cos(degree_to_radian(30)))
print("exact form         = sqrt(3)/2")


# =============================================================================
# 47. ADVANCED: SURD TERMINOLOGY
# =============================================================================

"""
A surd is commonly used to describe an irrational radical expression that
cannot be simplified to a rational number.

Examples:

    sqrt(2)
    sqrt(3)
    5sqrt(7)

are surds.

But:

    sqrt(16) = 4

is not an irrational surd because the radical evaluates to a rational
integer.

The term "surd" is most useful in algebraic contexts involving exact
irrational radical expressions.
"""


def is_integer_square_root(number: int) -> bool:
    """Determine whether sqrt(number) is an integer."""
    return is_perfect_square(number)


print("\nSurd-related examples:")
for number in [2, 3, 16, 25, 50]:
    print(
        f"sqrt({number}) is an integer:",
        is_integer_square_root(number)
    )


# =============================================================================
# 48. ADVANCED: SOLVING RADICAL EQUATIONS SAFELY
# =============================================================================

"""
A reliable workflow for radical equations is:

1. Determine the domain.
2. Isolate one radical if possible.
3. Raise both sides to the required power.
4. Simplify.
5. Solve the resulting algebraic equation.
6. Check every candidate in the ORIGINAL equation.
7. Discard extraneous candidates.

For multiple radicals, repeated isolation and squaring may be required.

Each squaring step potentially expands the candidate set, so verification is
not optional.
"""


def verify_radical_equation_solution(
    candidate: float,
    left_function,
    right_function,
    tolerance: float = 1e-10,
) -> bool:
    """Verify a candidate solution against the original equation."""
    try:
        left = left_function(candidate)
        right = right_function(candidate)
    except (ValueError, ZeroDivisionError):
        return False

    return math.isclose(
        left,
        right,
        rel_tol=tolerance,
        abs_tol=tolerance,
    )


print("\nOriginal-equation verification:")

candidate = 8
print(
    "sqrt(x+1)=3, x=8:",
    verify_radical_equation_solution(
        candidate,
        lambda x: math.sqrt(x + 1),
        lambda x: 3,
    )
)


# =============================================================================
# 49. ADVANCED: LIMITATIONS OF FLOATING-POINT ROOTS
# =============================================================================

"""
A naive implementation:

    number ** (1/n)

may suffer from:

- Rounding errors
- Negative-number domain errors
- Incorrect exact perfect-power detection
- Overflow for very large values
- Underflow for very small values

For exact integer roots, use integer algorithms.

For numerical roots, use established numerical routines when appropriate.
"""


def naive_root(value: float, degree: int) -> float:
    """Simple floating-point root calculation for comparison."""
    return value ** (1.0 / degree)


print("\nNaive numerical root:")
print("cube root of 125 =", naive_root(125, 3))
print("cube root of 10^18 =", naive_root(10**18, 3))


# =============================================================================
# 50. COMPLETE PRACTICAL RADICAL WORKFLOW
# =============================================================================

"""
The following function combines the principal concepts:

Input:
    coefficient * root_degree(radicand)

Process:
    - validate
    - factor
    - simplify
    - evaluate
    - report exact and approximate forms
"""


def analyze_radical(
    radicand: int,
    degree: int = 2,
    coefficient: int = 1,
) -> dict[str, object]:
    """Return a structured analysis of an integer radical."""
    if degree <= 0:
        raise ValueError("Degree must be positive.")

    simplified = simplify_radical(
        radicand,
        degree,
        coefficient,
    )

    return {
        "input_radicand": radicand,
        "degree": degree,
        "coefficient": coefficient,
        "factorization": (
            None
            if radicand == 0
            else prime_factorization(radicand)
        ),
        "simplified": str(simplified),
        "approximate_value": radical_value(simplified),
        "is_perfect_power": (
            is_perfect_power_exact(
                abs(radicand),
                degree,
            )
            if radicand != 0
            else True
        ),
    }


print("\nComplete radical analysis:")
analysis = analyze_radical(720, 2)
for key, value in analysis.items():
    print(f"{key}: {value}")


# =============================================================================
# 51. COMPREHENSIVE TEST SUITE
# =============================================================================

def run_comprehensive_tests() -> None:
    """Run a broad set of mathematical correctness checks."""

    # Basic square roots
    assert square_root(0) == 0
    assert square_root(1) == 1
    assert square_root(144) == 12

    # Cube roots
    assert math.isclose(cube_root(27), 3)
    assert math.isclose(cube_root(-27), -3)

    # Exact square detection
    assert is_perfect_square(0)
    assert is_perfect_square(1)
    assert is_perfect_square(49)
    assert not is_perfect_square(50)
    assert not is_perfect_square(-4)

    # Exact powers
    assert is_perfect_power_exact(64, 2)
    assert is_perfect_power_exact(64, 3)
    assert is_perfect_power_exact(-125, 3)
    assert not is_perfect_power_exact(-16, 2)

    # Simplification
    assert simplify_radical(72) == Radical(6, 2, 2)
    assert simplify_radical(48) == Radical(4, 2, 3)
    assert simplify_radical(54, 3) == Radical(3, 3, 2)
    assert simplify_radical(-54, 3) == Radical(-3, 3, 2)

    # Multiplication
    assert multiply_radicals(
        simplify_radical(6),
        simplify_radical(15),
    ) == Radical(3, 2, 10)

    # Like radical combination
    assert add_radicals(
        simplify_radical(8),
        simplify_radical(18),
    ) == Radical(5, 2, 2)

    # Geometry
    assert math.isclose(
        pythagorean_hypotenuse(3, 4),
        5,
    )

    # Complex roots
    complex_roots = all_complex_roots(1 + 0j, 4)
    assert len(complex_roots) == 4

    for root in complex_roots:
        assert cmath.isclose(
            root ** 4,
            1 + 0j,
            abs_tol=1e-9,
        )


run_comprehensive_tests()
print("\nComprehensive test suite passed.")


# =============================================================================
# 52. STUDY CHECKPOINTS
# =============================================================================

"""
The following examples provide executable checkpoints for the most important
ideas.

Checkpoint 1:
    sqrt(98) = ?

Checkpoint 2:
    cube root(250) = ?

Checkpoint 3:
    sqrt(12) + sqrt(27) = ?

Checkpoint 4:
    1/sqrt(5) = ?

Checkpoint 5:
    sqrt(x^2) = ?

Checkpoint 6:
    Solve sqrt(x+4) = 6.

Checkpoint 7:
    Solve x^2 = 49.

Checkpoint 8:
    What is the real fifth root of -32?

The answers are demonstrated below.
"""


def study_checkpoints() -> None:
    print("\nStudy checkpoints:")

    print("1. sqrt(98) =", simplify_radical(98))

    print("2. cube root(250) =", simplify_radical(250, 3))

    first = simplify_radical(12)
    second = simplify_radical(27)
    print(
        "3. sqrt(12)+sqrt(27) =",
        add_radicals(first, second),
    )

    numerator, remaining, denominator = (
        rationalize_single_square_root_denominator(1, 5)
    )

    print(
        "4. 1/sqrt(5) =",
        f"{numerator}sqrt({remaining})/{denominator}",
    )

    print("5. sqrt(x^2) = |x| for real x.")

    print(
        "6. sqrt(x+4)=6 -> x=32"
    )

    print(
        "7. x^2=49 -> x=7 or x=-7"
    )

    print(
        "8. fifth root(-32) =",
        nth_root_real(-32, 5),
    )


study_checkpoints()


# =============================================================================
# 53. FINAL REFERENCE TABLE
# =============================================================================

"""
Important identities:

1. Principal square root:
       sqrt(a) >= 0 for a >= 0

2. Root definition:
       root_n(a)^n = a

3. Rational exponent:
       a^(1/n) = root_n(a)

4. General rational exponent:
       a^(m/n) = root_n(a^m)
       under the relevant domain conditions

5. Product:
       sqrt(ab) = sqrt(a)sqrt(b)
       for appropriate non-negative real a,b

6. Quotient:
       sqrt(a/b) = sqrt(a)/sqrt(b)
       for a >= 0, b > 0

7. Square of square root:
       sqrt(a)^2 = a
       for a >= 0

8. Square root of square:
       sqrt(a^2) = |a|

9. Conjugates:
       (a+b)(a-b) = a^2-b^2

10. Quadratic formula:
       x = (-b ± sqrt(b^2-4ac))/(2a)

11. Even-root domain:
       radicand >= 0 for real arithmetic

12. Odd-root domain:
       every real radicand is permitted

13. Rationalization:
       multiply by a suitable radical or conjugate to remove radicals from
       the denominator.

The central discipline is to distinguish exact symbolic algebra from
numerical approximation, principal roots from equation solutions, and real
roots from complex roots.
"""


# =============================================================================
# 54. SCRIPT ENTRY POINT
# =============================================================================

def main() -> None:
    """
    The demonstrations above execute as the script is loaded.

    This function serves as a conventional entry point and confirms that the
    complete educational sequence has finished successfully.
    """
    print("\n" + "=" * 80)
    print("RADICALS AND ROOTS STUDY SCRIPT COMPLETED")
    print("=" * 80)
    print(
        "The script covered fundamental roots, exact simplification, "
        "operations, rationalization, equations, domains, complex roots, "
        "algorithms, testing, numerical precision, and applications."
    )


if __name__ == "__main__":
    main()
