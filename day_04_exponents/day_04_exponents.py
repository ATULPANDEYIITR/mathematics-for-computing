"""
Exponents: Laws, Powers, Negative Exponents, Fractional Exponents,
and Scientific Notation

This standalone study script teaches exponentiation from absolute beginner
through advanced level using executable Python examples, explanations in
comments, validation, edge cases, comparisons, numerical experiments,
scientific notation utilities, and tests.

The mathematical notation used in comments includes:
    a^n       power of a with exponent n
    a^0       zero exponent
    a^(-n)    negative exponent
    a^(p/q)   fractional exponent

Python uses ** for exponentiation:
    a ** n
"""

from __future__ import annotations

from decimal import Decimal, getcontext
from fractions import Fraction
import math
import random
import unittest


# =============================================================================
# 1. FUNDAMENTAL IDEA OF AN EXPONENT
# =============================================================================

print("=" * 80)
print("1. FUNDAMENTAL IDEA OF EXPONENTS")
print("=" * 80)

# An exponent tells us how many times a number is used as a factor.
#
# 2^5 = 2 * 2 * 2 * 2 * 2 = 32
#
# The number 2 is called the base.
# The number 5 is called the exponent, power, or index.
# The result 32 is called the value of the power.

base = 2
exponent = 5

result = base ** exponent

print(f"{base}^{exponent} = {result}")

# A small implementation of positive integer exponentiation demonstrates the
# definition directly rather than relying on Python's built-in operator.

def repeated_multiplication(base: float, exponent: int) -> float:
    """Calculate base^exponent for a non-negative integer exponent."""
    if not isinstance(exponent, int):
        raise TypeError("The exponent must be an integer.")
    if exponent < 0:
        raise ValueError("This basic implementation accepts only non-negative exponents.")

    result = 1

    for _ in range(exponent):
        result *= base

    return result


for power in range(0, 6):
    print(f"3^{power} = {repeated_multiplication(3, power)}")


# =============================================================================
# 2. WHY ANY NON-ZERO NUMBER TO THE POWER 0 IS 1
# =============================================================================

print("\n" + "=" * 80)
print("2. ZERO EXPONENT")
print("=" * 80)

# For a != 0:
#
# a^m / a^m = 1
#
# But using the quotient law:
#
# a^m / a^m = a^(m-m) = a^0
#
# Therefore:
#
# a^0 = 1
#
# The restriction a != 0 matters because 0^0 is not assigned a universal
# value in elementary arithmetic.

numbers = [2, 3, 10, -5, 0.5, 100]

for number in numbers:
    print(f"{number}^0 = {number ** 0}")

print("Python represents 0^0 as:", 0 ** 0)
print("Mathematically, 0^0 is context-dependent and is not treated as a")
print("universally defined elementary power.")


# =============================================================================
# 3. BASIC EXPONENT VOCABULARY
# =============================================================================

print("\n" + "=" * 80)
print("3. EXPONENT TERMINOLOGY")
print("=" * 80)

terminology = {
    "base": "The quantity being multiplied or raised to a power.",
    "exponent": "The quantity specifying the power.",
    "power": "An expression such as a^n, or sometimes the resulting value.",
    "coefficient": "A multiplicative factor outside a power, such as 3 in 3x^2.",
    "integer exponent": "An exponent belonging to the integers.",
    "negative exponent": "An exponent less than zero, producing a reciprocal.",
    "fractional exponent": "An exponent represented by a rational number.",
    "radicand": "The quantity inside a radical.",
    "index": "The root number in a radical, such as 3 in cube root.",
    "scientific notation": "A representation c x 10^n with 1 <= |c| < 10.",
}

for term, definition in terminology.items():
    print(f"{term}: {definition}")


# =============================================================================
# 4. THE MAIN LAWS OF EXPONENTS
# =============================================================================

print("\n" + "=" * 80)
print("4. LAWS OF EXPONENTS")
print("=" * 80)

# Law 1: Product of powers with the same base
#
# a^m * a^n = a^(m+n)
#
# Example:
# 2^3 * 2^4 = 2^7

left = 2 ** 3 * 2 ** 4
right = 2 ** (3 + 4)
print("Product law:", left, right, left == right)

# Law 2: Quotient of powers with the same non-zero base
#
# a^m / a^n = a^(m-n)
#
# Example:
# 5^7 / 5^3 = 5^4

left = 5 ** 7 / 5 ** 3
right = 5 ** (7 - 3)
print("Quotient law:", left, right, math.isclose(left, right))

# Law 3: Power of a power
#
# (a^m)^n = a^(mn)

left = (2 ** 3) ** 4
right = 2 ** (3 * 4)
print("Power-of-a-power law:", left, right, left == right)

# Law 4: Power of a product
#
# (ab)^n = a^n b^n

left = (2 * 3) ** 4
right = 2 ** 4 * 3 ** 4
print("Power-of-a-product law:", left, right, left == right)

# Law 5: Power of a quotient
#
# (a/b)^n = a^n / b^n, provided b != 0

left = (6 / 2) ** 3
right = 6 ** 3 / 2 ** 3
print("Power-of-a-quotient law:", left, right, math.isclose(left, right))

# Law 6: Zero exponent
#
# a^0 = 1 for a != 0

print("Zero-exponent law:", 17 ** 0)

# Law 7: Negative exponent
#
# a^(-n) = 1 / a^n for a != 0

left = 2 ** -3
right = 1 / (2 ** 3)
print("Negative-exponent law:", left, right, left == right)


# =============================================================================
# 5. VERIFYING THE EXPONENT LAWS PROGRAMMATICALLY
# =============================================================================

print("\n" + "=" * 80)
print("5. PROGRAMMATIC VERIFICATION OF EXPONENT LAWS")
print("=" * 80)

random.seed(42)

for _ in range(10):
    a = random.randint(1, 10)
    m = random.randint(0, 8)
    n = random.randint(0, 8)

    product_left = a ** m * a ** n
    product_right = a ** (m + n)

    quotient_left = a ** m / a ** n
    quotient_right = a ** (m - n)

    power_left = (a ** m) ** n
    power_right = a ** (m * n)

    assert product_left == product_right
    assert math.isclose(quotient_left, quotient_right)
    assert power_left == power_right

print("Randomized checks passed for product, quotient, and power-of-power laws.")


# =============================================================================
# 6. NEGATIVE EXPONENTS
# =============================================================================

print("\n" + "=" * 80)
print("6. NEGATIVE EXPONENTS")
print("=" * 80)

# A negative exponent does not mean the result is negative.
#
# 2^(-3) = 1 / 2^3 = 1/8
#
# The minus sign changes the position of the power from numerator to
# denominator.

negative_examples = [
    (2, -1),
    (2, -2),
    (2, -3),
    (5, -2),
    (10, -4),
    (-2, -3),
]

for base, exponent in negative_examples:
    print(f"{base}^{exponent} = {base ** exponent}")

# Important distinction:
#
# (-2)^3 = -8
# 2^(-3) = 1/8
#
# The first minus sign belongs to the base.
# The second minus sign belongs to the exponent.

print("(-2)^3 =", (-2) ** 3)
print("2^(-3) =", 2 ** (-3))


# =============================================================================
# 7. NEGATIVE BASES AND PARENTHESES
# =============================================================================

print("\n" + "=" * 80)
print("7. NEGATIVE BASES AND PARENTHESES")
print("=" * 80)

print("(-2)^2 =", (-2) ** 2)
print("(-2)^3 =", (-2) ** 3)
print("-2^2 =", -2 ** 2)

# Python interprets -2**2 as -(2**2), not (-2)**2.
#
# Therefore parentheses are essential when the negative sign is part of
# the base.

print("\nParentheses should be used when a negative number is the base.")


# =============================================================================
# 8. EVEN AND ODD EXPONENTS
# =============================================================================

print("\n" + "=" * 80)
print("8. EVEN AND ODD POWERS OF NEGATIVE NUMBERS")
print("=" * 80)

for exponent in range(1, 8):
    print(f"(-3)^{exponent} = {(-3) ** exponent}")

# For a negative base:
#
# even exponent -> positive result
# odd exponent  -> negative result
#
# This property is useful in algebra, polynomial analysis, and sign analysis.


# =============================================================================
# 9. FRACTIONAL EXPONENTS
# =============================================================================

print("\n" + "=" * 80)
print("9. FRACTIONAL EXPONENTS")
print("=" * 80)

# A fractional exponent connects powers and roots.
#
# a^(1/n) = nth root of a
#
# Examples:
#
# 16^(1/2) = sqrt(16) = 4
# 27^(1/3) = cube root of 27 = 3
#
# More generally:
#
# a^(m/n) = nth root of (a^m)
#          = (nth root of a)^m
#
# For real-valued elementary arithmetic, domain restrictions matter.

fractional_examples = [
    (16, Fraction(1, 2)),
    (27, Fraction(1, 3)),
    (81, Fraction(3, 4)),
    (32, Fraction(2, 5)),
]

for base, exponent in fractional_examples:
    value = base ** float(exponent)
    print(f"{base}^({exponent}) = {value}")


# =============================================================================
# 10. IMPLEMENTING RATIONAL POWERS FOR COMMON REAL CASES
# =============================================================================

print("\n" + "=" * 80)
print("10. RATIONAL EXPONENT IMPLEMENTATION")
print("=" * 80)

def rational_power(base: float, exponent: Fraction) -> float:
    """
    Evaluate base^(p/q) for real-valued cases supported by this implementation.

    For positive bases, the calculation is straightforward.

    For negative bases:
        - odd denominators can produce real results;
        - even denominators do not produce real results.

    The denominator is normalized by Fraction, so the parity check applies to
    the reduced denominator.
    """
    if not isinstance(exponent, Fraction):
        exponent = Fraction(exponent)

    numerator = exponent.numerator
    denominator = exponent.denominator

    if denominator == 1:
        return base ** numerator

    if base > 0:
        return base ** (numerator / denominator)

    if base == 0:
        if numerator < 0:
            raise ZeroDivisionError("Zero cannot be raised to a negative exponent.")
        return 0.0

    # Negative base.
    if denominator % 2 == 0:
        raise ValueError(
            "A negative base with an even root denominator has no real-valued result."
        )

    magnitude = abs(base) ** (numerator / denominator)

    # The sign depends on whether the numerator is odd.
    if numerator % 2 == 0:
        return magnitude

    return -magnitude


tests = [
    (16, Fraction(1, 2)),
    (27, Fraction(1, 3)),
    (32, Fraction(2, 5)),
    (-8, Fraction(1, 3)),
    (-8, Fraction(2, 3)),
]

for base, exponent in tests:
    try:
        print(f"{base}^({exponent}) = {rational_power(base, exponent)}")
    except (ValueError, ZeroDivisionError) as error:
        print(f"{base}^({exponent}) -> {error}")


# =============================================================================
# 11. RADICALS AND FRACTIONAL EXPONENTS
# =============================================================================

print("\n" + "=" * 80)
print("11. RADICALS AND FRACTIONAL EXPONENTS")
print("=" * 80)

# These forms are equivalent in appropriate domains:
#
# sqrt(a)       = a^(1/2)
# cube_root(a)  = a^(1/3)
# nth_root(a)   = a^(1/n)
#
# a^(m/n) can be understood as either:
#
# nth root of a^m
#
# or:
#
# (nth root of a)^m

sqrt_64 = math.sqrt(64)
power_64 = 64 ** Fraction(1, 2)

print("sqrt(64) =", sqrt_64)
print("64^(1/2) =", float(power_64))

print("cube root of 125 =", 125 ** (1 / 3))
print("125^(1/3) =", 125 ** (1 / 3))


# =============================================================================
# 12. ROOTS THAT ARE NOT PERFECT
# =============================================================================

print("\n" + "=" * 80)
print("12. NON-PERFECT ROOTS")
print("=" * 80)

# Not every root is an integer.
#
# sqrt(2) is irrational.
# Its decimal representation is non-terminating and non-repeating.

print("sqrt(2) =", math.sqrt(2))
print("sqrt(2) rounded to 5 decimal places =", round(math.sqrt(2), 5))


# =============================================================================
# 13. EXACT RATIONAL EXPONENTS WITH FRACTION
# =============================================================================

print("\n" + "=" * 80)
print("13. FRACTION OBJECTS AND EXACT EXPONENTS")
print("=" * 80)

# Python's Fraction class stores rational numbers exactly.
#
# 2/4 becomes 1/2 automatically.
# This is useful when studying rational exponents because it prevents
# accidental loss of exact numerator/denominator information.

fraction_examples = [
    Fraction(2, 4),
    Fraction(6, 8),
    Fraction(15, 10),
    Fraction(-12, 18),
]

for value in fraction_examples:
    print(f"{value} -> numerator={value.numerator}, denominator={value.denominator}")


# =============================================================================
# 14. EXPONENTS GREATER THAN ONE AND ROOTS
# =============================================================================

print("\n" + "=" * 80)
print("14. INTERPRETING m/n")
print("=" * 80)

# If exponent = m/n:
#
# numerator m -> power
# denominator n -> root
#
# Example:
#
# 64^(2/3)
#
# = cube root of 64, squared
# = 4^2
# = 16

base = 64
exponent = Fraction(2, 3)

print(f"{base}^({exponent}) =", rational_power(base, exponent))


# =============================================================================
# 15. ORDER OF OPERATIONS WITH EXPONENTS
# =============================================================================

print("\n" + "=" * 80)
print("15. ORDER OF OPERATIONS")
print("=" * 80)

# Exponentiation is performed before multiplication and addition.
#
# 2 + 3^2 = 2 + 9 = 11
# (2 + 3)^2 = 25
#
# Parentheses explicitly change the grouping.

print("2 + 3^2 =", 2 + 3 ** 2)
print("(2 + 3)^2 =", (2 + 3) ** 2)

# Exponentiation also interacts specially with unary minus.
#
# -2^2 = -(2^2)
# (-2)^2 = 4

print("-2^2 =", -2 ** 2)
print("(-2)^2 =", (-2) ** 2)


# =============================================================================
# 16. DISTRIBUTIVE PROPERTY AND A COMMON ERROR
# =============================================================================

print("\n" + "=" * 80)
print("16. POWER OF A SUM IS NOT THE SUM OF POWERS")
print("=" * 80)

# This is generally FALSE:
#
# (a + b)^n = a^n + b^n
#
# Example:
#
# (2 + 3)^2 = 25
# 2^2 + 3^2 = 13

print("(2 + 3)^2 =", (2 + 3) ** 2)
print("2^2 + 3^2 =", 2 ** 2 + 3 ** 2)

# The correct product rule is:
#
# (ab)^n = a^n b^n
#
# but a sum requires the binomial theorem or another algebraic method.


# =============================================================================
# 17. BINOMIAL CONNECTION
# =============================================================================

print("\n" + "=" * 80)
print("17. BINOMIAL EXPANSION")
print("=" * 80)

# For small powers:
#
# (a+b)^2 = a^2 + 2ab + b^2
#
# (a+b)^3 = a^3 + 3a^2b + 3ab^2 + b^3

a = 2
b = 3

left = (a + b) ** 3
right = a ** 3 + 3 * a ** 2 * b + 3 * a * b ** 2 + b ** 3

print("(a+b)^3 =", left)
print("Expanded expression =", right)
print("Equal:", left == right)


# =============================================================================
# 18. SCIENTIFIC NOTATION
# =============================================================================

print("\n" + "=" * 80)
print("18. SCIENTIFIC NOTATION")
print("=" * 80)

# Scientific notation represents a number as:
#
# c x 10^n
#
# where:
#
# 1 <= |c| < 10
#
# Examples:
#
# 4500 = 4.5 x 10^3
# 0.0045 = 4.5 x 10^-3
#
# The exponent tells us how far the decimal point moves.

scientific_values = [
    4500,
    0.0045,
    300000000,
    0.000000001,
    -720000,
    -0.00042,
]

for value in scientific_values:
    print(f"{value} -> {value:.6e}")


# =============================================================================
# 19. SCIENTIFIC NOTATION AS A MANUAL PROCESS
# =============================================================================

print("\n" + "=" * 80)
print("19. CONVERTING TO SCIENTIFIC NOTATION")
print("=" * 80)

# For a positive number greater than or equal to 1:
#
# Move the decimal point left until one non-zero digit remains on the left.
# Number of moves = positive exponent.
#
# For a number between 0 and 1:
#
# Move the decimal point right until one non-zero digit remains on the left.
# Number of moves = negative exponent.

print("4500000 = 4.5 x 10^6")
print("0.0000045 = 4.5 x 10^-6")


# =============================================================================
# 20. SCIENTIFIC NOTATION UTILITY
# =============================================================================

print("\n" + "=" * 80)
print("20. SCIENTIFIC NOTATION UTILITY")
print("=" * 80)

def scientific_notation(value: float, significant_digits: int = 6) -> tuple[float, int]:
    """
    Return (coefficient, exponent) such that:
        value = coefficient * 10**exponent

    The coefficient is normalized so that:
        1 <= abs(coefficient) < 10
    for non-zero values.

    Zero is represented as (0.0, 0).
    """
    if not math.isfinite(value):
        raise ValueError("Scientific notation requires a finite number.")

    if significant_digits < 1:
        raise ValueError("significant_digits must be at least 1.")

    if value == 0:
        return 0.0, 0

    exponent = math.floor(math.log10(abs(value)))
    coefficient = value / (10 ** exponent)

    coefficient = round(coefficient, significant_digits - 1)

    # Rounding can theoretically produce 10.0, requiring renormalization.
    if abs(coefficient) >= 10:
        coefficient /= 10
        exponent += 1

    return coefficient, exponent


for value in scientific_values:
    coefficient, exponent = scientific_notation(value, 5)
    print(f"{value} = {coefficient} x 10^{exponent}")


# =============================================================================
# 21. RECONSTRUCTING A NUMBER FROM SCIENTIFIC NOTATION
# =============================================================================

print("\n" + "=" * 80)
print("21. RECONSTRUCTING SCIENTIFIC NOTATION")
print("=" * 80)

def from_scientific_notation(coefficient: float, exponent: int) -> float:
    """Convert coefficient x 10^exponent back to an ordinary number."""
    if not isinstance(exponent, int):
        raise TypeError("The exponent must be an integer.")

    return coefficient * (10 ** exponent)


examples = [
    (4.5, 3),
    (4.5, -3),
    (7.2, 6),
    (-3.1, -5),
]

for coefficient, exponent in examples:
    value = from_scientific_notation(coefficient, exponent)
    print(f"{coefficient} x 10^{exponent} = {value}")


# =============================================================================
# 22. MULTIPLYING NUMBERS IN SCIENTIFIC NOTATION
# =============================================================================

print("\n" + "=" * 80)
print("22. MULTIPLICATION IN SCIENTIFIC NOTATION")
print("=" * 80)

# Rule:
#
# (a x 10^m)(b x 10^n)
# = (ab) x 10^(m+n)
#
# Then normalize the coefficient if necessary.

def multiply_scientific(
    coefficient_a: float,
    exponent_a: int,
    coefficient_b: float,
    exponent_b: int,
) -> tuple[float, int]:
    """Multiply two scientific-notation values and normalize the result."""
    coefficient = coefficient_a * coefficient_b
    exponent = exponent_a + exponent_b

    if coefficient == 0:
        return 0.0, 0

    adjustment = math.floor(math.log10(abs(coefficient)))
    coefficient /= 10 ** adjustment
    exponent += adjustment

    return coefficient, exponent


a = (3.0, 5)
b = (2.0, 4)

coefficient, exponent = multiply_scientific(*a, *b)

print(f"(3 x 10^5)(2 x 10^4) = {coefficient} x 10^{exponent}")


# =============================================================================
# 23. DIVIDING NUMBERS IN SCIENTIFIC NOTATION
# =============================================================================

print("\n" + "=" * 80)
print("23. DIVISION IN SCIENTIFIC NOTATION")
print("=" * 80)

# Rule:
#
# (a x 10^m)/(b x 10^n)
# = (a/b) x 10^(m-n)
#
# provided b != 0.

def divide_scientific(
    coefficient_a: float,
    exponent_a: int,
    coefficient_b: float,
    exponent_b: int,
) -> tuple[float, int]:
    """Divide two scientific-notation values and normalize the result."""
    if coefficient_b == 0:
        raise ZeroDivisionError("The divisor cannot be zero.")

    coefficient = coefficient_a / coefficient_b
    exponent = exponent_a - exponent_b

    if coefficient == 0:
        return 0.0, 0

    adjustment = math.floor(math.log10(abs(coefficient)))
    coefficient /= 10 ** adjustment
    exponent += adjustment

    return coefficient, exponent


coefficient, exponent = divide_scientific(6.0, 8, 2.0, 3)
print(f"(6 x 10^8)/(2 x 10^3) = {coefficient} x 10^{exponent}")


# =============================================================================
# 24. ADDITION AND SUBTRACTION IN SCIENTIFIC NOTATION
# =============================================================================

print("\n" + "=" * 80)
print("24. ADDITION AND SUBTRACTION IN SCIENTIFIC NOTATION")
print("=" * 80)

# Addition is different from multiplication.
#
# Exponents must first be aligned.
#
# Example:
#
# 3 x 10^5 + 2 x 10^4
# = 3 x 10^5 + 0.2 x 10^5
# = 3.2 x 10^5

value_a = 3 * 10 ** 5
value_b = 2 * 10 ** 4

print("3 x 10^5 + 2 x 10^4 =", value_a + value_b)
print("Scientific notation:", f"{value_a + value_b:.2e}")


# =============================================================================
# 25. SIGNIFICANT FIGURES AND SCIENTIFIC NOTATION
# =============================================================================

print("\n" + "=" * 80)
print("25. SIGNIFICANT FIGURES")
print("=" * 80)

# Scientific notation makes significant digits explicit.
#
# 5.20 x 10^3 contains three significant figures.
# 5.2 x 10^3 contains two significant figures.
#
# The exponent determines scale, not the number of significant figures.

measurements = [
    5.2e3,
    5.20e3,
    5.200e3,
]

for value in measurements:
    print(f"{value:.3e}")


# =============================================================================
# 26. EXPONENTS AND SCALE
# =============================================================================

print("\n" + "=" * 80)
print("26. EXPONENTS AS SCALE INDICATORS")
print("=" * 80)

# Positive powers of 10 increase scale:
#
# 10^1 = 10
# 10^2 = 100
# 10^3 = 1000
#
# Negative powers decrease scale:
#
# 10^-1 = 0.1
# 10^-2 = 0.01
# 10^-3 = 0.001

for exponent in range(-6, 7):
    print(f"10^{exponent:2d} = {10 ** exponent}")


# =============================================================================
# 27. POWERS OF TEN AND DECIMAL MOVEMENT
# =============================================================================

print("\n" + "=" * 80)
print("27. MULTIPLICATION BY POWERS OF TEN")
print("=" * 80)

number = 4.25

for exponent in [-3, -2, -1, 0, 1, 2, 3]:
    print(f"{number} x 10^{exponent} = {number * 10 ** exponent}")


# =============================================================================
# 28. EXPONENTIAL GROWTH
# =============================================================================

print("\n" + "=" * 80)
print("28. EXPONENTIAL GROWTH")
print("=" * 80)

# Exponential growth often has the form:
#
# A(t) = A0 * r^t
#
# where r > 1.
#
# Examples include repeated percentage growth and compound interest.

initial_value = 100
growth_factor = 1.10

for year in range(0, 11):
    value = initial_value * growth_factor ** year
    print(f"Year {year:2d}: {value:.2f}")


# =============================================================================
# 29. EXPONENTIAL DECAY
# =============================================================================

print("\n" + "=" * 80)
print("29. EXPONENTIAL DECAY")
print("=" * 80)

# Decay has a factor between 0 and 1.
#
# A(t) = A0 * r^t
#
# where 0 < r < 1.

initial_value = 1000
decay_factor = 0.80

for period in range(0, 11):
    value = initial_value * decay_factor ** period
    print(f"Period {period:2d}: {value:.2f}")


# =============================================================================
# 30. COMPOUND INTEREST
# =============================================================================

print("\n" + "=" * 80)
print("30. COMPOUND INTEREST")
print("=" * 80)

# Compound interest:
#
# A = P(1 + r/n)^(nt)
#
# P = principal
# r = annual interest rate as a decimal
# n = number of compounding periods per year
# t = number of years
# A = final amount

def compound_interest(
    principal: float,
    annual_rate: float,
    compounds_per_year: int,
    years: float,
) -> float:
    """Calculate compound interest using the standard compound-interest formula."""
    if principal < 0:
        raise ValueError("Principal cannot be negative.")
    if compounds_per_year <= 0:
        raise ValueError("Compounds per year must be positive.")
    if years < 0:
        raise ValueError("Years cannot be negative.")

    return principal * (
        1 + annual_rate / compounds_per_year
    ) ** (compounds_per_year * years)


amount = compound_interest(10000, 0.08, 12, 5)

print("Principal: 10000")
print("Annual rate: 8%")
print("Compounding: monthly")
print("Years: 5")
print("Final amount:", round(amount, 2))


# =============================================================================
# 31. CONTINUOUS COMPOUNDING
# =============================================================================

print("\n" + "=" * 80)
print("31. CONTINUOUS EXPONENTIAL GROWTH")
print("=" * 80)

# Continuous compounding uses:
#
# A = Pe^(rt)
#
# where e is Euler's number.

def continuous_growth(
    principal: float,
    rate: float,
    time: float,
) -> float:
    """Calculate continuous exponential growth."""
    return principal * math.exp(rate * time)


print("Continuous growth:", continuous_growth(10000, 0.08, 5))


# =============================================================================
# 32. EXPONENTS AND LOGARITHMS
# =============================================================================

print("\n" + "=" * 80)
print("32. EXPONENTS AND LOGARITHMS")
print("=" * 80)

# A logarithm answers:
#
# "What exponent is required to obtain this value?"
#
# If:
#
# b^x = y
#
# then:
#
# log_b(y) = x
#
# Python's math.log(value, base) can calculate logarithms for positive
# values and valid bases.

base = 2
value = 32

print(f"log base {base} of {value} =", math.log(value, base))
print("Verification:", base ** math.log(value, base))


# =============================================================================
# 33. SOLVING SIMPLE EXPONENTIAL EQUATIONS
# =============================================================================

print("\n" + "=" * 80)
print("33. SOLVING EXPONENTIAL EQUATIONS")
print("=" * 80)

# To solve:
#
# 2^x = 64
#
# recognize that 64 = 2^6, so x = 6.
#
# Computationally:
#
# x = log_2(64)

x = math.log(64, 2)
print("Solution to 2^x = 64:", x)

# For:
#
# 5^x = 80
#
# x = ln(80) / ln(5)

x = math.log(80) / math.log(5)
print("Solution to 5^x = 80:", x)


# =============================================================================
# 34. CHANGE OF BASE
# =============================================================================

print("\n" + "=" * 80)
print("34. CHANGE OF BASE")
print("=" * 80)

# Change-of-base formula:
#
# log_b(x) = log_k(x) / log_k(b)
#
# for valid positive x and bases.

x = 125
base = 5

using_natural_log = math.log(x) / math.log(base)
using_python_log = math.log(x, base)

print("Change-of-base result:", using_natural_log)
print("Python result:", using_python_log)


# =============================================================================
# 35. REAL EXPONENTS
# =============================================================================

print("\n" + "=" * 80)
print("35. REAL EXPONENTS")
print("=" * 80)

# Python's floating-point exponentiation supports many real exponents for
# positive bases.
#
# Example:
#
# 2^sqrt(2)

real_exponent = math.sqrt(2)

print("sqrt(2) =", real_exponent)
print("2^sqrt(2) =", 2 ** real_exponent)


# =============================================================================
# 36. THE NUMBER e
# =============================================================================

print("\n" + "=" * 80)
print("36. EULER'S NUMBER e")
print("=" * 80)

# e is approximately 2.71828.
#
# It is central to continuous exponential growth, logarithms, differential
# equations, probability, and many scientific models.

print("e =", math.e)
print("e^1 =", math.e ** 1)
print("exp(1) =", math.exp(1))
print("exp(2) =", math.exp(2))


# =============================================================================
# 37. EXPONENT RULES WITH VARIABLES
# =============================================================================

print("\n" + "=" * 80)
print("37. ALGEBRAIC EXPONENT RULES")
print("=" * 80)

# Consider:
#
# x^a * x^b = x^(a+b)
# x^a / x^b = x^(a-b)
# (x^a)^b = x^(ab)
# (xy)^a = x^a y^a
# (x/y)^a = x^a/y^a
#
# These identities require attention to domains when exponents are not
# integers, particularly over the real numbers.

print("x^a * x^b -> x^(a+b)")
print("x^a / x^b -> x^(a-b)")
print("(x^a)^b -> x^(ab)")
print("(xy)^a -> x^a y^a")
print("(x/y)^a -> x^a / y^a")


# =============================================================================
# 38. IMPORTANT DOMAIN RESTRICTIONS
# =============================================================================

print("\n" + "=" * 80)
print("38. DOMAIN RESTRICTIONS")
print("=" * 80)

# Several exponent rules have hidden domain conditions.
#
# Division requires a non-zero denominator.
# Negative exponents require a non-zero base.
# Even roots of negative real numbers do not produce real numbers.
# Non-integer powers of negative real numbers are not generally real.
#
# These restrictions become important when algebraic expressions are
# transformed mechanically.

domain_cases = [
    ("2^-3", lambda: 2 ** -3),
    ("0^-1", lambda: 0 ** -1),
    ("(-16)^(1/2)", lambda: (-16) ** 0.5),
]

for description, operation in domain_cases:
    try:
        print(description, "=", operation())
    except Exception as error:
        print(description, "->", type(error).__name__, error)


# =============================================================================
# 39. COMPLEX EXPONENTS
# =============================================================================

print("\n" + "=" * 80)
print("39. COMPLEX NUMBERS AND EXPONENTS")
print("=" * 80)

# Although elementary exponentiation is often restricted to real numbers,
# Python supports complex arithmetic.
#
# sqrt(-1) = i
#
# In Python, 1j represents the imaginary unit.

complex_value = (-16) ** 0.5
print("(-16)^0.5 in Python =", complex_value)

# A complex result is not a contradiction. It indicates that the result lies
# outside the real-number system.

print("Magnitude:", abs(complex_value))
print("Real part:", complex_value.real)
print("Imaginary part:", complex_value.imag)


# =============================================================================
# 40. COMPLEX EXPONENTIAL IDENTITY
# =============================================================================

print("\n" + "=" * 80)
print("40. EULER'S FORMULA")
print("=" * 80)

# Euler's formula:
#
# e^(i theta) = cos(theta) + i sin(theta)
#
# This connects exponential functions with trigonometric functions.

theta = math.pi

left = complex(math.cos(theta), math.sin(theta))
right = complex(math.e) ** (1j * theta)

print("cos(pi) + i sin(pi) =", left)
print("e^(i*pi) =", right)


# =============================================================================
# 41. EXPONENTS AND UNITS
# =============================================================================

print("\n" + "=" * 80)
print("41. POWERS OF UNITS")
print("=" * 80)

# Exponents appear naturally in units.
#
# Area: m^2
# Volume: m^3
#
# If a length is scaled by a factor k:
#
# area scales by k^2
# volume scales by k^3

scale_factor = 3

original_length = 2
new_length = original_length * scale_factor

original_area = original_length ** 2
new_area = new_length ** 2

original_volume = original_length ** 3
new_volume = new_length ** 3

print("Length scale factor:", scale_factor)
print("Area scale factor:", new_area / original_area)
print("Volume scale factor:", new_volume / original_volume)


# =============================================================================
# 42. EXPONENTS IN GEOMETRY
# =============================================================================

print("\n" + "=" * 80)
print("42. GEOMETRIC APPLICATION")
print("=" * 80)

# Square area:
#
# A = s^2
#
# Cube volume:
#
# V = s^3

side = 5

square_area = side ** 2
cube_volume = side ** 3

print("Square area:", square_area)
print("Cube volume:", cube_volume)


# =============================================================================
# 43. EXPONENTS IN DATA STORAGE
# =============================================================================

print("\n" + "=" * 80)
print("43. POWERS OF TWO IN COMPUTING")
print("=" * 80)

# Computers frequently use powers of two.
#
# 2^10 = 1024
# 2^20 = 1,048,576
#
# Binary representation naturally creates powers of two.

for exponent in range(0, 11):
    print(f"2^{exponent} = {2 ** exponent}")


# =============================================================================
# 44. BINARY PLACE VALUES
# =============================================================================

print("\n" + "=" * 80)
print("44. BINARY PLACE VALUES")
print("=" * 80)

# A binary number uses powers of two.
#
# For example:
#
# 1011_2
#
# = 1*2^3 + 0*2^2 + 1*2^1 + 1*2^0
# = 8 + 0 + 2 + 1
# = 11

binary_digits = [1, 0, 1, 1]

decimal_value = 0

for position, digit in enumerate(reversed(binary_digits)):
    decimal_value += digit * 2 ** position

print("Binary 1011 =", decimal_value)


# =============================================================================
# 45. EXPONENTIATION BY SQUARING
# =============================================================================

print("\n" + "=" * 80)
print("45. FAST EXPONENTIATION BY SQUARING")
print("=" * 80)

# Naive repeated multiplication performs O(n) multiplications for a^n.
#
# Exponentiation by squaring reduces the number of multiplications to
# O(log n).
#
# If n is even:
#
# a^n = (a^(n/2))^2
#
# If n is odd:
#
# a^n = a * a^(n-1)

def power_by_squaring(base: int, exponent: int) -> int | float:
    """
    Compute base^exponent using exponentiation by squaring.

    Supports positive, zero, and negative integer exponents.
    """
    if not isinstance(exponent, int):
        raise TypeError("Exponent must be an integer.")

    if base == 0 and exponent < 0:
        raise ZeroDivisionError("Zero cannot have a negative exponent.")

    if exponent < 0:
        return 1 / power_by_squaring(base, -exponent)

    result = 1
    current_base = base
    current_exponent = exponent

    while current_exponent > 0:
        if current_exponent % 2 == 1:
            result *= current_base

        current_base *= current_base
        current_exponent //= 2

    return result


large_exponent = 1_000

custom_result = power_by_squaring(2, large_exponent)
python_result = 2 ** large_exponent

print("Custom algorithm agrees with Python:", custom_result == python_result)


# =============================================================================
# 46. COMPLEXITY COMPARISON
# =============================================================================

print("\n" + "=" * 80)
print("46. EXPONENTIATION COMPLEXITY")
print("=" * 80)

# Repeated multiplication:
#
# Time: O(n)
#
# Exponentiation by squaring:
#
# Time: O(log n)
#
# This distinction matters for algorithms involving huge integer exponents.

def multiplication_count_by_squaring(exponent: int) -> int:
    """Count the loop iterations needed by exponentiation by squaring."""
    count = 0
    while exponent > 0:
        exponent //= 2
        count += 1
    return count


for exponent in [10, 100, 1_000, 1_000_000]:
    print(
        f"Exponent {exponent:,}: "
        f"approximately {multiplication_count_by_squaring(exponent)} "
        f"squaring iterations"
    )


# =============================================================================
# 47. MODULAR EXPONENTIATION
# =============================================================================

print("\n" + "=" * 80)
print("47. MODULAR EXPONENTIATION")
print("=" * 80)

# Modular exponentiation computes:
#
# a^b mod m
#
# without constructing the entire a^b integer.
#
# Python's pow(a, b, m) performs this efficiently.

base = 7
exponent = 100
modulus = 13

print(f"{base}^{exponent} mod {modulus} =", pow(base, exponent, modulus))


# =============================================================================
# 48. CUSTOM MODULAR EXPONENTIATION
# =============================================================================

print("\n" + "=" * 80)
print("48. CUSTOM MODULAR EXPONENTIATION")
print("=" * 80)

def modular_power(base: int, exponent: int, modulus: int) -> int:
    """
    Compute (base^exponent) mod modulus using repeated squaring.
    """
    if modulus <= 0:
        raise ValueError("Modulus must be positive.")

    if exponent < 0:
        raise ValueError("This implementation accepts non-negative exponents.")

    result = 1
    base %= modulus

    while exponent > 0:
        if exponent & 1:
            result = (result * base) % modulus

        base = (base * base) % modulus
        exponent >>= 1

    return result


for base, exponent, modulus in [
    (7, 100, 13),
    (2, 1000, 17),
    (12345, 6789, 97),
]:
    expected = pow(base, exponent, modulus)
    actual = modular_power(base, exponent, modulus)
    print(actual, "==", expected, "->", actual == expected)


# =============================================================================
# 49. NEGATIVE EXPONENTS IN MODULAR ARITHMETIC
# =============================================================================

print("\n" + "=" * 80)
print("49. NEGATIVE EXPONENTS MODULO m")
print("=" * 80)

# Modular negative powers require modular inverses.
#
# a^(-1) mod m means the number x satisfying:
#
# a*x ≡ 1 (mod m)
#
# An inverse exists when gcd(a, m) = 1.
#
# Python's pow(a, -1, m) can compute a modular inverse.

a = 3
m = 11

inverse = pow(a, -1, m)

print(f"Inverse of {a} modulo {m} =", inverse)
print("Verification:", (a * inverse) % m)

# Python can also directly calculate a negative modular exponent when a
# modular inverse exists.

print("3^(-2) mod 11 =", pow(3, -2, 11))


# =============================================================================
# 50. INTEGER OVERFLOW AND PYTHON
# =============================================================================

print("\n" + "=" * 80)
print("50. LARGE INTEGER POWERS")
print("=" * 80)

# Python integers have arbitrary precision.
#
# Therefore they do not overflow in the same way as fixed-width machine
# integers. Memory and computation time still become limiting factors.

large_integer = 2 ** 100
print("2^100 =", large_integer)
print("Number of decimal digits:", len(str(large_integer)))


# =============================================================================
# 51. FLOATING-POINT LIMITATIONS
# =============================================================================

print("\n" + "=" * 80)
print("51. FLOATING-POINT LIMITATIONS")
print("=" * 80)

# Floating-point numbers have finite precision.
#
# This means very large or very small powers can lose information.

floating_value = 1.000000000000001 ** 1000000

print("Floating-point exponential calculation:", floating_value)

# Extremely large powers may overflow.

try:
    print("10^400 as float:", 10.0 ** 400)
except OverflowError as error:
    print("10^400 as float ->", type(error).__name__, error)


# =============================================================================
# 52. DECIMAL FOR CONTROLLED DECIMAL ARITHMETIC
# =============================================================================

print("\n" + "=" * 80)
print("52. DECIMAL ARITHMETIC")
print("=" * 80)

# Decimal is useful when decimal representation and controlled precision are
# important, such as financial calculations.
#
# It does not make arbitrary exponentiation magically exact, but it provides
# decimal arithmetic with configurable precision.

getcontext().prec = 40

decimal_base = Decimal("1.01")
decimal_result = decimal_base ** 100

print("1.01^100 using Decimal:", decimal_result)


# =============================================================================
# 53. UNDERFLOW AND VERY SMALL POWERS
# =============================================================================

print("\n" + "=" * 80)
print("53. UNDERFLOW")
print("=" * 80)

# Floating-point underflow can turn sufficiently small non-zero values into
# zero.

small_value = 10.0 ** -324
smaller_value = 10.0 ** -400

print("10^-324 as float:", small_value)
print("10^-400 as float:", smaller_value)


# =============================================================================
# 54. LOGARITHMIC FORM OF LARGE POWERS
# =============================================================================

print("\n" + "=" * 80)
print("54. LOGARITHMIC HANDLING OF LARGE POWERS")
print("=" * 80)

# Sometimes calculating a^b directly is unnecessary.
#
# If only the number of decimal digits is needed:
#
# digits = floor(log10(a^b)) + 1
#        = floor(b * log10(a)) + 1
#
# for a > 0 and a^b >= 1.

base = 2
exponent = 1000

digits = math.floor(exponent * math.log10(base)) + 1

print(f"Number of decimal digits in {base}^{exponent}:", digits)


# =============================================================================
# 55. LOG-SUM-EXP STYLE NUMERICAL STABILITY
# =============================================================================

print("\n" + "=" * 80)
print("55. NUMERICAL STABILITY WITH EXPONENTIALS")
print("=" * 80)

# Directly evaluating exp(1000) overflows in ordinary floating point.
#
# A common numerical technique is to subtract the largest exponent:
#
# exp(x_i) / sum(exp(x_j))
#
# can be stabilized by using:
#
# exp(x_i - max(x))
#
# because the common scaling factor cancels.

def stable_softmax(values: list[float]) -> list[float]:
    """Compute a numerically stable softmax."""
    if not values:
        raise ValueError("values cannot be empty.")

    maximum = max(values)
    exponentials = [math.exp(value - maximum) for value in values]
    total = sum(exponentials)

    return [value / total for value in exponentials]


scores = [1000, 1001, 1002]

try:
    naive = [math.exp(value) for value in scores]
    naive_probabilities = [value / sum(naive) for value in naive]
except OverflowError:
    naive_probabilities = "overflow"

print("Naive exponential calculation:", naive_probabilities)
print("Stable calculation:", stable_softmax(scores))


# =============================================================================
# 56. COMMON ALGEBRAIC MISTAKES
# =============================================================================

print("\n" + "=" * 80)
print("56. COMMON EXPONENT MISTAKES")
print("=" * 80)

# Mistake 1:
#
# a^m + a^n = a^(m+n)
#
# FALSE.
#
# Exponents are added when multiplying powers with the same base.

print("2^3 + 2^4 =", 2 ** 3 + 2 ** 4)
print("2^(3+4) =", 2 ** (3 + 4))

# Mistake 2:
#
# (a+b)^n = a^n+b^n
#
# FALSE in general.

print("(2+3)^2 =", (2 + 3) ** 2)
print("2^2+3^2 =", 2 ** 2 + 3 ** 2)

# Mistake 3:
#
# a^(-n) = -a^n
#
# FALSE.
#
# a^(-n) = 1/a^n.

print("2^(-3) =", 2 ** -3)
print("-(2^3) =", -(2 ** 3))


# =============================================================================
# 57. CANCELLING EXPONENTS CORRECTLY
# =============================================================================

print("\n" + "=" * 80)
print("57. CANCELLING POWERS")
print("=" * 80)

# For a != 0:
#
# a^m / a^m = 1
#
# and:
#
# a^m / a^n = a^(m-n)

a = 7

print("7^8 / 7^3 =", a ** 8 / a ** 3)
print("7^(8-3) =", a ** (8 - 3))


# =============================================================================
# 58. ZERO BASE EDGE CASES
# =============================================================================

print("\n" + "=" * 80)
print("58. ZERO BASE EDGE CASES")
print("=" * 80)

# For positive integers n:
#
# 0^n = 0
#
# For n < 0:
#
# 0^n is undefined because it requires division by zero.
#
# 0^0 requires special treatment and is context-dependent.

for exponent in [1, 2, 5]:
    print(f"0^{exponent} =", 0 ** exponent)

try:
    print("0^-1 =", 0 ** -1)
except ZeroDivisionError as error:
    print("0^-1 ->", type(error).__name__, error)


# =============================================================================
# 59. FRACTIONAL EXPONENT EDGE CASES
# =============================================================================

print("\n" + "=" * 80)
print("59. FRACTIONAL EXPONENT EDGE CASES")
print("=" * 80)

edge_cases = [
    (-8, Fraction(1, 3)),
    (-8, Fraction(2, 3)),
    (-8, Fraction(1, 2)),
    (0, Fraction(1, 3)),
    (0, Fraction(-1, 3)),
]

for base, exponent in edge_cases:
    try:
        print(f"{base}^({exponent}) =", rational_power(base, exponent))
    except Exception as error:
        print(
            f"{base}^({exponent}) -> "
            f"{type(error).__name__}: {error}"
        )


# =============================================================================
# 60. EQUIVALENT FRACTIONAL EXPONENTS
# =============================================================================

print("\n" + "=" * 80)
print("60. EQUIVALENT FRACTIONAL EXPONENTS")
print("=" * 80)

# 1/2 = 2/4 = 3/6.
#
# Fraction reduces these automatically.

fractions = [Fraction(1, 2), Fraction(2, 4), Fraction(3, 6)]

for exponent in fractions:
    print(exponent, "->", rational_power(16, exponent))


# =============================================================================
# 61. NEGATIVE FRACTIONAL EXPONENTS
# =============================================================================

print("\n" + "=" * 80)
print("61. NEGATIVE FRACTIONAL EXPONENTS")
print("=" * 80)

# A negative fractional exponent combines two ideas:
#
# a^(-p/q) = 1 / a^(p/q)

examples = [
    (16, Fraction(-1, 2)),
    (27, Fraction(-2, 3)),
    (32, Fraction(-2, 5)),
]

for base, exponent in examples:
    print(f"{base}^({exponent}) =", rational_power(base, exponent))


# =============================================================================
# 62. EXPONENTS OF 1
# =============================================================================

print("\n" + "=" * 80)
print("62. THE NUMBER 1")
print("=" * 80)

# For every integer n:
#
# 1^n = 1.
#
# This remains true for positive and negative integer exponents.

for exponent in range(-5, 6):
    print(f"1^{exponent} =", 1 ** exponent)


# =============================================================================
# 63. POWERS OF -1
# =============================================================================

print("\n" + "=" * 80)
print("63. THE NUMBER -1")
print("=" * 80)

# Powers of -1 alternate:
#
# (-1)^even = 1
# (-1)^odd = -1

for exponent in range(0, 10):
    print(f"(-1)^{exponent} =", (-1) ** exponent)


# =============================================================================
# 64. EXPONENT EQUATIONS WITH THE SAME BASE
# =============================================================================

print("\n" + "=" * 80)
print("64. SAME-BASE EXPONENT EQUATIONS")
print("=" * 80)

# If:
#
# a^x = a^y
#
# and a > 0, a != 1,
#
# then:
#
# x = y.
#
# Example:
#
# 3^(x+2) = 3^7
#
# x+2 = 7
# x = 5

x = 7 - 2

print("Solution to 3^(x+2) = 3^7:", x)


# =============================================================================
# 65. EXPONENTIAL EQUATION WITH A CONSTANT FACTOR
# =============================================================================

print("\n" + "=" * 80)
print("65. EXPONENTIAL EQUATIONS USING LOGARITHMS")
print("=" * 80)

# Solve:
#
# 2^x = 20
#
# x = ln(20)/ln(2)

x = math.log(20) / math.log(2)

print("x =", x)
print("Verification:", 2 ** x)


# =============================================================================
# 66. SCIENTIFIC NOTATION COMPARISON
# =============================================================================

print("\n" + "=" * 80)
print("66. COMPARING ORDERS OF MAGNITUDE")
print("=" * 80)

# Scientific notation allows quick comparison.
#
# 3 x 10^8 is much larger than 7 x 10^5 because the exponent differs by 3.

numbers = [
    ("A", 3, 8),
    ("B", 7, 5),
    ("C", 2, 9),
    ("D", 8, 4),
]

for label, coefficient, exponent in sorted(
    numbers,
    key=lambda item: item[1] * 10 ** item[2],
    reverse=True,
):
    print(f"{label}: {coefficient} x 10^{exponent}")


# =============================================================================
# 67. SCIENTIFIC NOTATION NORMALIZATION
# =============================================================================

print("\n" + "=" * 80)
print("67. NORMALIZATION")
print("=" * 80)

# These values are equal:
#
# 45 x 10^3
# 4.5 x 10^4
# 0.45 x 10^5
#
# Standard scientific notation selects exactly one non-zero digit before the
# decimal point.

equivalent_forms = [
    (45, 3),
    (4.5, 4),
    (0.45, 5),
]

for coefficient, exponent in equivalent_forms:
    print(
        f"{coefficient} x 10^{exponent} = "
        f"{coefficient * 10 ** exponent}"
    )


# =============================================================================
# 68. ENGINEERING NOTATION
# =============================================================================

print("\n" + "=" * 80)
print("68. ENGINEERING NOTATION")
print("=" * 80)

# Engineering notation is similar to scientific notation, but the exponent
# is restricted to a multiple of 3.
#
# Examples:
#
# 4700 = 4.7 x 10^3
# 4700000 = 4.7 x 10^6
#
# This aligns naturally with SI prefixes such as kilo, mega, and giga.

def engineering_notation(value: float, significant_digits: int = 6) -> tuple[float, int]:
    """Return coefficient and exponent where exponent is a multiple of 3."""
    if value == 0:
        return 0.0, 0

    if not math.isfinite(value):
        raise ValueError("Value must be finite.")

    exponent = math.floor(math.log10(abs(value)) / 3) * 3
    coefficient = value / (10 ** exponent)

    coefficient = round(coefficient, significant_digits - 1)

    return coefficient, exponent


for value in [4700, 4_700_000, 0.0047, 0.0000047]:
    coefficient, exponent = engineering_notation(value, 4)
    print(f"{value} = {coefficient} x 10^{exponent}")


# =============================================================================
# 69. EXPONENTS AND PERCENTAGE CHANGE
# =============================================================================

print("\n" + "=" * 80)
print("69. REPEATED PERCENTAGE CHANGE")
print("=" * 80)

# A repeated percentage increase is multiplicative, not additive.
#
# A 10% increase repeated n times:
#
# final = initial * 1.10^n
#
# It is not:
#
# initial + initial*(0.10*n)
#
# unless a linear approximation is deliberately being used.

initial = 100
periods = 5

compound = initial * 1.10 ** periods
simple = initial * (1 + 0.10 * periods)

print("Repeated multiplicative growth:", compound)
print("Simple additive approximation:", simple)


# =============================================================================
# 70. HALF-LIFE
# =============================================================================

print("\n" + "=" * 80)
print("70. HALF-LIFE")
print("=" * 80)

# A quantity with half-life H can be modeled as:
#
# A(t) = A0 * (1/2)^(t/H)

def remaining_after_half_life(
    initial: float,
    elapsed_time: float,
    half_life: float,
) -> float:
    """Calculate remaining quantity after a specified elapsed time."""
    if initial < 0:
        raise ValueError("Initial quantity cannot be negative.")
    if half_life <= 0:
        raise ValueError("Half-life must be positive.")

    return initial * (0.5 ** (elapsed_time / half_life))


print(
    "Remaining amount:",
    remaining_after_half_life(100, 10, 5)
)


# =============================================================================
# 71. DOUBLING TIME
# =============================================================================

print("\n" + "=" * 80)
print("71. DOUBLING TIME")
print("=" * 80)

# For exponential growth:
#
# A(t) = A0 * r^t
#
# Doubling time T satisfies:
#
# r^T = 2
#
# Therefore:
#
# T = ln(2)/ln(r)

growth_factor = 1.05
doubling_time = math.log(2) / math.log(growth_factor)

print("Doubling time at 5% growth per period:", doubling_time)


# =============================================================================
# 72. LOGARITHMIC ESTIMATION OF POWERS
# =============================================================================

print("\n" + "=" * 80)
print("72. ESTIMATING LARGE POWERS")
print("=" * 80)

# Logs are useful for estimating magnitude without calculating the full
# integer.
#
# For 7^100:
#
# log10(7^100) = 100 log10(7)

base = 7
exponent = 100

log10_value = exponent * math.log10(base)
leading_power = math.floor(log10_value)

print(f"log10({base}^{exponent}) =", log10_value)
print("Highest decimal place:", leading_power)
print("Number of digits:", leading_power + 1)


# =============================================================================
# 73. RELATIVE ERROR AND POWERS
# =============================================================================

print("\n" + "=" * 80)
print("73. ERROR AMPLIFICATION IN POWERS")
print("=" * 80)

# If x has a small relative error and is raised to a large power, the relative
# effect can become significant.
#
# Example:
#
# (1 + epsilon)^n
#
# can differ considerably from 1 when n is large.

epsilon = 0.001
n = 1000

factor = (1 + epsilon) ** n

print("(1 + 0.001)^1000 =", factor)


# =============================================================================
# 74. POWER MEANS DIFFERENT THINGS IN DIFFERENT CONTEXTS
# =============================================================================

print("\n" + "=" * 80)
print("74. CONTEXTS WHERE POWERS APPEAR")
print("=" * 80)

contexts = {
    "Arithmetic": "2^5",
    "Algebra": "x^3",
    "Geometry": "side^2 for area",
    "Volume": "side^3",
    "Scientific notation": "4.2 x 10^6",
    "Probability": "p^n in repeated independent events",
    "Finance": "(1+r)^n for compound growth",
    "Computing": "2^n binary state counts",
    "Physics": "inverse-square relationships",
    "Statistics": "variance involving squared deviations",
}

for context, example in contexts.items():
    print(f"{context}: {example}")


# =============================================================================
# 75. PROBABILITY CONNECTION
# =============================================================================

print("\n" + "=" * 80)
print("75. PROBABILITY AND POWERS")
print("=" * 80)

# If independent events each have probability p, the probability that all
# n events occur is:
#
# p^n

probability_of_success = 0.8
number_of_trials = 5

probability_all_success = probability_of_success ** number_of_trials

print(
    f"Probability all {number_of_trials} independent events succeed:",
    probability_all_success,
)


# =============================================================================
# 76. INVERSE-SQUARE LAW
# =============================================================================

print("\n" + "=" * 80)
print("76. INVERSE-SQUARE RELATIONSHIP")
print("=" * 80)

# Some physical quantities scale approximately as:
#
# quantity proportional to 1/r^2
#
# If distance doubles, the quantity becomes:
#
# 1/(2^2) = 1/4
#
# of its original value.

distance_factor = 2
relative_quantity = 1 / distance_factor ** 2

print("Relative quantity when distance doubles:", relative_quantity)


# =============================================================================
# 77. FRACTIONAL POWERS AS ROOT OPERATIONS
# =============================================================================

print("\n" + "=" * 80)
print("77. ROOT-POWER EQUIVALENCE")
print("=" * 80)

def nth_root(value: float, n: int) -> float:
    """
    Calculate an nth root for real values supported by this implementation.
    """
    if n <= 0:
        raise ValueError("Root index must be positive.")

    if value < 0 and n % 2 == 0:
        raise ValueError("Even root of a negative number is not real.")

    if value < 0:
        return -((-value) ** (1 / n))

    return value ** (1 / n)


for value, root in [(16, 2), (27, 3), (625, 4), (-27, 3)]:
    print(f"{root}th root of {value} =", nth_root(value, root))


# =============================================================================
# 78. POWER AND ROOT ROUND-TRIP
# =============================================================================

print("\n" + "=" * 80)
print("78. POWER-ROOT ROUND TRIP")
print("=" * 80)

# Mathematically:
#
# (a^(1/n))^n = a
#
# within the relevant domain.
#
# Floating-point calculations can produce tiny errors.

for value in [2, 10, 100, 1000]:
    reconstructed = nth_root(value, 3) ** 3
    print(
        value,
        "->",
        reconstructed,
        "close:",
        math.isclose(value, reconstructed, rel_tol=1e-12, abs_tol=1e-12),
    )


# =============================================================================
# 79. FLOATING-POINT COMPARISON
# =============================================================================

print("\n" + "=" * 80)
print("79. FLOATING-POINT EQUALITY")
print("=" * 80)

# Do not blindly compare floating-point results using == when rounding
# errors are possible.
#
# math.isclose() allows a tolerance.

a = (1 / 3) * 3
b = 1

print("a =", a)
print("b =", b)
print("a == b:", a == b)
print("math.isclose(a, b):", math.isclose(a, b))


# =============================================================================
# 80. INTEGER POWERS VS FLOAT POWERS
# =============================================================================

print("\n" + "=" * 80)
print("80. INTEGER AND FLOATING-POINT POWERS")
print("=" * 80)

integer_result = 2 ** 100
floating_result = 2.0 ** 100

print("Integer result type:", type(integer_result).__name__)
print("Float result type:", type(floating_result).__name__)
print("Integer result:", integer_result)
print("Float result:", floating_result)


# =============================================================================
# 81. BOOLEAN VALUES AND PYTHON POWER
# =============================================================================

print("\n" + "=" * 80)
print("81. PYTHON TYPE PECULIARITY: BOOLEANS")
print("=" * 80)

# Python's bool is a subclass of int:
#
# True behaves numerically like 1.
# False behaves numerically like 0.
#
# This is a Python-specific behavior rather than a mathematical law.

print("True ** 3 =", True ** 3)
print("False ** 3 =", False ** 3)


# =============================================================================
# 82. POWER WITH COMPLEX NUMBERS
# =============================================================================

print("\n" + "=" * 80)
print("82. COMPLEX POWERS")
print("=" * 80)

complex_base = 1 + 1j
complex_exponent = 2 + 0.5j

complex_result = complex_base ** complex_exponent

print("(1+i)^(2+0.5i) =", complex_result)


# =============================================================================
# 83. PYTHON'S BUILT-IN POW
# =============================================================================

print("\n" + "=" * 80)
print("83. POWER OPERATIONS IN PYTHON")
print("=" * 80)

# Python provides:
#
# x ** y
# pow(x, y)
# pow(x, y, modulus)
#
# The three-argument form performs modular exponentiation.

print("2 ** 10 =", 2 ** 10)
print("pow(2, 10) =", pow(2, 10))
print("pow(2, 10, 1000) =", pow(2, 10, 1000))


# =============================================================================
# 84. PRACTICAL POWER CALCULATOR
# =============================================================================

print("\n" + "=" * 80)
print("84. GENERAL POWER CALCULATOR")
print("=" * 80)

def calculate_power(base: float, exponent: float):
    """
    Calculate a real or complex power.

    For negative real bases and non-integer exponents, Python may return a
    complex value when the exponent is represented as a float.
    """
    return base ** exponent


calculations = [
    (2, 10),
    (5, -2),
    (16, 0.5),
    (27, 1 / 3),
    (-8, 1 / 3),
]

for base, exponent in calculations:
    print(f"{base}^{exponent} =", calculate_power(base, exponent))


# =============================================================================
# 85. VALIDATING SCIENTIFIC NOTATION
# =============================================================================

print("\n" + "=" * 80)
print("85. VALIDATING SCIENTIFIC NOTATION")
print("=" * 80)

def is_valid_scientific_coefficient(coefficient: float) -> bool:
    """
    Determine whether a non-zero coefficient satisfies standard scientific
    notation normalization:
        1 <= abs(coefficient) < 10
    """
    if coefficient == 0:
        return True

    return 1 <= abs(coefficient) < 10


for coefficient in [0, 0.5, 1, 4.2, 9.99, 10, 42, -3.2]:
    print(
        f"Coefficient {coefficient}:",
        is_valid_scientific_coefficient(coefficient),
    )


# =============================================================================
# 86. CONVERTING SCIENTIFIC NOTATION TO ENGINEERING NOTATION
# =============================================================================

print("\n" + "=" * 80)
print("86. SCIENTIFIC VS ENGINEERING NOTATION")
print("=" * 80)

# Scientific notation:
# exponent can be any integer.
#
# Engineering notation:
# exponent is a multiple of 3.
#
# Both describe the same numerical quantity.

value = 12_300_000

scientific = scientific_notation(value, 5)
engineering = engineering_notation(value, 5)

print("Scientific notation:", scientific)
print("Engineering notation:", engineering)


# =============================================================================
# 87. POWERS AND PREFIX SCALE
# =============================================================================

print("\n" + "=" * 80)
print("87. POWERS OF TEN AND COMMON SI SCALES")
print("=" * 80)

si_scales = {
    "kilo": 10 ** 3,
    "mega": 10 ** 6,
    "giga": 10 ** 9,
    "milli": 10 ** -3,
    "micro": 10 ** -6,
    "nano": 10 ** -9,
}

for name, multiplier in si_scales.items():
    print(f"{name:>6}: {multiplier}")


# =============================================================================
# 88. ADVANCED: POWER FUNCTIONS
# =============================================================================

print("\n" + "=" * 80)
print("88. FUNCTIONS AS EXPONENTIAL MODELS")
print("=" * 80)

def exponential_model(
    initial: float,
    growth_factor: float,
    time: float,
) -> float:
    """General exponential model A(t) = initial * growth_factor^time."""
    return initial * growth_factor ** time


for time in [0, 1, 2, 5, 10]:
    print(
        f"t={time}:",
        exponential_model(500, 1.08, time),
    )


# =============================================================================
# 89. FINDING A GROWTH FACTOR
# =============================================================================

print("\n" + "=" * 80)
print("89. FINDING AN UNKNOWN GROWTH FACTOR")
print("=" * 80)

# Given:
#
# A = A0 * r^t
#
# r = (A/A0)^(1/t)

initial = 100
final = 121
time = 2

growth_factor = (final / initial) ** (1 / time)

print("Growth factor:", growth_factor)
print("Percentage growth per period:", (growth_factor - 1) * 100)


# =============================================================================
# 90. FINDING AN UNKNOWN TIME
# =============================================================================

print("\n" + "=" * 80)
print("90. FINDING UNKNOWN TIME")
print("=" * 80)

# Given:
#
# A = A0 * r^t
#
# t = log(A/A0) / log(r)

initial = 100
target = 200
growth_factor = 1.10

time = math.log(target / initial) / math.log(growth_factor)

print("Periods required to double at 10% growth:", time)


# =============================================================================
# 91. POWER LAW MODELS
# =============================================================================

print("\n" + "=" * 80)
print("91. POWER LAW VS EXPONENTIAL LAW")
print("=" * 80)

# A power-law model often has:
#
# y = C*x^k
#
# An exponential model has:
#
# y = C*r^x
#
# The exponent is attached to x in a power law, while x appears in the
# exponent in an exponential model.

def power_law(x: float, coefficient: float, exponent: float) -> float:
    """Calculate y = C*x^k for positive x."""
    if x <= 0:
        raise ValueError("x must be positive for this real-valued model.")

    return coefficient * x ** exponent


def exponential_law(x: float, coefficient: float, growth_factor: float) -> float:
    """Calculate y = C*r^x for positive growth factor."""
    if growth_factor <= 0:
        raise ValueError("Growth factor must be positive.")

    return coefficient * growth_factor ** x


for x in [1, 2, 5, 10]:
    print(
        f"x={x}: power law={power_law(x, 2, 3):.2f}, "
        f"exponential={exponential_law(x, 2, 1.5):.2f}"
    )


# =============================================================================
# 92. LOG-LOG INTERPRETATION OF POWER LAWS
# =============================================================================

print("\n" + "=" * 80)
print("92. LOGARITHMS OF POWER LAWS")
print("=" * 80)

# For:
#
# y = C*x^k
#
# taking logarithms:
#
# log(y) = log(C) + k log(x)
#
# Thus k becomes the slope on a log-log plot.

C = 4
k = 3
x = 10

y = C * x ** k

left = math.log(y)
right = math.log(C) + k * math.log(x)

print("log(y):", left)
print("log(C) + k log(x):", right)
print("Equal within tolerance:", math.isclose(left, right))


# =============================================================================
# 93. EXPONENT RULES AS STRUCTURAL TRANSFORMATIONS
# =============================================================================

print("\n" + "=" * 80)
print("93. STRUCTURAL TRANSFORMATIONS")
print("=" * 80)

# The main rules transform expressions without changing their value under
# appropriate domain conditions.

transformations = [
    ("a^m * a^n", "a^(m+n)"),
    ("a^m / a^n", "a^(m-n)"),
    ("(a^m)^n", "a^(mn)"),
    ("(ab)^n", "a^n b^n"),
    ("(a/b)^n", "a^n / b^n"),
    ("a^(-n)", "1/a^n"),
    ("a^(1/n)", "nth root of a"),
    ("a^(m/n)", "nth root of a^m"),
]

for original, transformed in transformations:
    print(f"{original:15s} -> {transformed}")


# =============================================================================
# 94. ADVANCED DOMAIN CAUTION: POWER OF A POWER
# =============================================================================

print("\n" + "=" * 80)
print("94. POWER-OF-A-POWER DOMAIN CAUTION")
print("=" * 80)

# The familiar identity:
#
# (a^b)^c = a^(bc)
#
# needs domain care for real-valued fractional powers and complex values.
#
# For positive a, the identity behaves cleanly for real exponents.
#
# Negative bases and non-integer exponents can introduce branch and domain
# issues.

positive_base = 16
left = (positive_base ** 0.5) ** 2
right = positive_base ** (0.5 * 2)

print("Positive-base comparison:")
print(left, right, math.isclose(left, right))


# =============================================================================
# 95. ADVANCED DOMAIN CAUTION: DISTRIBUTION
# =============================================================================

print("\n" + "=" * 80)
print("95. POWER DISTRIBUTION DISTINCTION")
print("=" * 80)

# Valid:
#
# (ab)^n = a^n b^n
#
# Not generally valid:
#
# (a+b)^n = a^n+b^n

a = 4
b = 5
n = 3

print("Product:")
print((a * b) ** n)
print(a ** n * b ** n)

print("Sum:")
print((a + b) ** n)
print(a ** n + b ** n)


# =============================================================================
# 96. EDGE CASE: EXPONENT ONE
# =============================================================================

print("\n" + "=" * 80)
print("96. EXPONENT ONE")
print("=" * 80)

# a^1 = a.

for value in [-10, -2.5, 0, 3, 100]:
    print(f"{value}^1 =", value ** 1)


# =============================================================================
# 97. EDGE CASE: BASE ONE
# =============================================================================

print("\n" + "=" * 80)
print("97. BASE ONE")
print("=" * 80)

# 1^x = 1 for real x where the expression is defined.

for exponent in [-5, -1, 0, 0.5, 2, 10]:
    print(f"1^{exponent} =", 1 ** exponent)


# =============================================================================
# 98. EXPONENTS IN ALGORITHM ANALYSIS
# =============================================================================

print("\n" + "=" * 80)
print("98. EXPONENTIAL COMPLEXITY")
print("=" * 80)

# "Exponential" in algorithmic complexity often means a runtime such as:
#
# O(2^n)
#
# This is different from polynomial complexity:
#
# O(n^2), O(n^3), etc.
#
# Even moderate increases in n can make 2^n grow rapidly.

for n in range(0, 21, 2):
    print(f"2^{n:2d} = {2 ** n:,}")


# =============================================================================
# 99. NUMBER OF SUBSETS
# =============================================================================

print("\n" + "=" * 80)
print("99. POWERS OF TWO AND SUBSETS")
print("=" * 80)

# A set with n elements has:
#
# 2^n
#
# possible subsets.
#
# Each element has two choices:
# included or excluded.

for n in range(0, 11):
    print(f"{n} elements -> {2 ** n} subsets")


# =============================================================================
# 100. FINAL INTEGRATED PRACTICE PROBLEMS
# =============================================================================

print("\n" + "=" * 80)
print("100. INTEGRATED PRACTICE PROBLEMS")
print("=" * 80)


def solve_practice_problems() -> None:
    """Run representative exponent problems and verify their solutions."""

    # Problem 1:
    # Simplify 2^4 * 2^3.
    answer_1 = 2 ** (4 + 3)
    assert answer_1 == 128
    print("1. 2^4 * 2^3 =", answer_1)

    # Problem 2:
    # Simplify 5^7 / 5^4.
    answer_2 = 5 ** (7 - 4)
    assert answer_2 == 125
    print("2. 5^7 / 5^4 =", answer_2)

    # Problem 3:
    # Simplify (3^2)^4.
    answer_3 = 3 ** (2 * 4)
    assert answer_3 == 6561
    print("3. (3^2)^4 =", answer_3)

    # Problem 4:
    # Evaluate 4^-2.
    answer_4 = 4 ** -2
    assert answer_4 == 1 / 16
    print("4. 4^-2 =", answer_4)

    # Problem 5:
    # Evaluate 81^(3/4).
    answer_5 = rational_power(81, Fraction(3, 4))
    assert math.isclose(answer_5, 27)
    print("5. 81^(3/4) =", answer_5)

    # Problem 6:
    # Convert 0.00072 into scientific notation.
    answer_6 = scientific_notation(0.00072, 2)
    print("6. 0.00072 =", answer_6[0], "x 10^", answer_6[1])

    # Problem 7:
    # Calculate 3 x 10^5 times 4 x 10^2.
    answer_7 = multiply_scientific(3, 5, 4, 2)
    assert math.isclose(
        answer_7[0] * 10 ** answer_7[1],
        3 * 10 ** 5 * 4 * 10 ** 2,
    )
    print("7. (3 x 10^5)(4 x 10^2) =", answer_7)

    # Problem 8:
    # Solve 2^x = 256.
    answer_8 = math.log(256, 2)
    assert math.isclose(answer_8, 8)
    print("8. 2^x = 256 -> x =", answer_8)

    # Problem 9:
    # Calculate a large modular power.
    answer_9 = modular_power(5, 12345, 97)
    assert answer_9 == pow(5, 12345, 97)
    print("9. 5^12345 mod 97 =", answer_9)

    # Problem 10:
    # Calculate compound growth.
    answer_10 = compound_interest(5000, 0.06, 12, 10)
    print("10. Compound amount =", round(answer_10, 2))


solve_practice_problems()


# =============================================================================
# 101. UNIT TESTS
# =============================================================================

print("\n" + "=" * 80)
print("101. UNIT TESTS")
print("=" * 80)


class TestExponentConcepts(unittest.TestCase):
    """Tests for the implementations in this study script."""

    def test_repeated_multiplication(self):
        self.assertEqual(repeated_multiplication(2, 0), 1)
        self.assertEqual(repeated_multiplication(2, 5), 32)

    def test_negative_integer_power(self):
        self.assertEqual(power_by_squaring(2, -3), 1 / 8)

    def test_power_by_squaring(self):
        for base in range(-5, 6):
            for exponent in range(0, 15):
                self.assertEqual(
                    power_by_squaring(base, exponent),
                    base ** exponent,
                )

    def test_rational_power(self):
        self.assertTrue(
            math.isclose(
                rational_power(16, Fraction(1, 2)),
                4,
            )
        )
        self.assertTrue(
            math.isclose(
                rational_power(27, Fraction(2, 3)),
                9,
            )
        )

    def test_negative_base_odd_root(self):
        self.assertTrue(
            math.isclose(
                rational_power(-8, Fraction(1, 3)),
                -2,
            )
        )

    def test_negative_base_even_root_rejected(self):
        with self.assertRaises(ValueError):
            rational_power(-16, Fraction(1, 2))

    def test_zero_negative_exponent_rejected(self):
        with self.assertRaises(ZeroDivisionError):
            rational_power(0, Fraction(-1, 2))

    def test_scientific_notation(self):
        coefficient, exponent = scientific_notation(4500, 4)

        self.assertTrue(math.isclose(coefficient, 4.5))
        self.assertEqual(exponent, 3)

    def test_scientific_reconstruction(self):
        value = from_scientific_notation(4.5, 3)
        self.assertTrue(math.isclose(value, 4500))

    def test_scientific_multiplication(self):
        coefficient, exponent = multiply_scientific(3, 5, 2, 4)
        value = coefficient * 10 ** exponent

        self.assertTrue(math.isclose(value, 6 * 10 ** 9))

    def test_scientific_division(self):
        coefficient, exponent = divide_scientific(6, 8, 2, 3)
        value = coefficient * 10 ** exponent

        self.assertTrue(math.isclose(value, 3 * 10 ** 5))

    def test_modular_power(self):
        for base in range(-10, 11):
            for exponent in range(0, 20):
                modulus = 17
                self.assertEqual(
                    modular_power(base, exponent, modulus),
                    pow(base, exponent, modulus),
                )

    def test_softmax(self):
        probabilities = stable_softmax([1, 2, 3])

        self.assertAlmostEqual(sum(probabilities), 1.0)
        self.assertTrue(all(value > 0 for value in probabilities))

    def test_nth_root(self):
        self.assertTrue(math.isclose(nth_root(64, 3), 4))
        self.assertTrue(math.isclose(nth_root(-27, 3), -3))

    def test_compound_interest_validation(self):
        with self.assertRaises(ValueError):
            compound_interest(-1, 0.05, 12, 1)

        with self.assertRaises(ValueError):
            compound_interest(100, 0.05, 0, 1)


test_result = unittest.TextTestRunner(
    verbosity=1
).run(
    unittest.defaultTestLoader.loadTestsFromTestCase(TestExponentConcepts)
)

if not test_result.wasSuccessful():
    raise SystemExit("One or more tests failed.")


# =============================================================================
# 102. QUICK REFERENCE
# =============================================================================

print("\n" + "=" * 80)
print("102. QUICK REFERENCE")
print("=" * 80)

quick_reference = [
    ("Positive integer power", "a^n = a*a*...*a"),
    ("Zero exponent", "a^0 = 1, a != 0"),
    ("Negative exponent", "a^-n = 1/a^n, a != 0"),
    ("Product law", "a^m*a^n = a^(m+n)"),
    ("Quotient law", "a^m/a^n = a^(m-n), a != 0"),
    ("Power of power", "(a^m)^n = a^(mn)"),
    ("Product power", "(ab)^n = a^n*b^n"),
    ("Quotient power", "(a/b)^n = a^n/b^n"),
    ("Root", "a^(1/n) = nth root of a"),
    ("Fractional power", "a^(m/n) = nth root of a^m"),
    ("Scientific notation", "c x 10^n, 1 <= |c| < 10"),
    ("Exponential model", "A = A0*r^t"),
    ("Compound interest", "A=P(1+r/n)^(nt)"),
    ("Continuous growth", "A=Pe^(rt)"),
    ("Logarithmic inverse", "b^x=y <=> log_b(y)=x"),
]

for name, formula in quick_reference:
    print(f"{name:24s}: {formula}")


# =============================================================================
# 103. END-OF-SCRIPT CHECK
# =============================================================================

print("\n" + "=" * 80)
print("END-OF-SCRIPT CHECK")
print("=" * 80)

print("All major exponent topics demonstrated successfully.")
print("Core laws, negative exponents, fractional exponents, roots,")
print("scientific notation, numerical behavior, applications,")
print("advanced algorithms, edge cases, and tests were covered.")
