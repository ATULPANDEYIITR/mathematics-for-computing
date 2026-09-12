"""
EQUATIONS: LINEAR, QUADRATIC, POLYNOMIAL, AND SYSTEMS OF EQUATIONS

A self-contained study and practice script that progresses from elementary
equations to numerical polynomial methods and systems of equations.

The script uses only Python's standard library.

Topics covered
--------------
1. Equation terminology and mathematical foundations
2. Linear equations
3. Linear equations with fractions and decimals
4. Equations with parentheses and variables on both sides
5. Special and impossible linear equations
6. Linear equations in one variable
7. Two-variable linear equations and graph interpretation
8. Quadratic equations
9. Discriminant and classification of roots
10. Factoring quadratics
11. Completing the square
12. Quadratic formula
13. Vertex and axis of symmetry
14. Quadratic edge cases
15. Polynomial equations
16. Polynomial evaluation and arithmetic
17. Synthetic division
18. Remainder and factor theorems
19. Rational-root theorem
20. Polynomial deflation
21. Numerical polynomial root approximation
22. Systems of linear equations
23. Substitution
24. Elimination
25. Gaussian elimination
26. Matrix-based reasoning
27. Systems with unique, infinite, and no solutions
28. Numerical stability and validation
29. Applications and word-problem models
30. Testing and verification

The program prints demonstrations when executed.
"""


from __future__ import annotations

import cmath
import math
from dataclasses import dataclass
from typing import Callable, Iterable, Sequence


# =============================================================================
# SECTION 1: GENERAL EQUATION FOUNDATIONS
# =============================================================================

TOLERANCE = 1e-10


def approximately_equal(a: float | complex, b: float | complex,
                        tolerance: float = TOLERANCE) -> bool:
    """Return True when two numbers are sufficiently close."""
    return abs(a - b) <= tolerance


def format_number(value: float | complex, digits: int = 8) -> str:
    """Format real or complex numbers for educational output."""
    if isinstance(value, complex):
        real = 0.0 if abs(value.real) < 10 ** (-digits) else value.real
        imag = 0.0 if abs(value.imag) < 10 ** (-digits) else value.imag

        if imag == 0:
            return f"{real:.{digits}g}"
        if real == 0:
            return f"{imag:.{digits}g}i"

        sign = "+" if imag >= 0 else "-"
        return f"{real:.{digits}g} {sign} {abs(imag):.{digits}g}i"

    if abs(value) < 10 ** (-digits):
        value = 0.0
    return f"{value:.{digits}g}"


def verify_equation(
    left: Callable[[float], float],
    right: Callable[[float], float],
    value: float,
    tolerance: float = TOLERANCE,
) -> bool:
    """Check whether a candidate satisfies an equation."""
    return abs(left(value) - right(value)) <= tolerance


def print_section(title: str) -> None:
    """Print a consistent section heading."""
    print("\n" + "=" * 78)
    print(title)
    print("=" * 78)


# An equation asserts equality between two expressions.
#
# Example:
#
#     3x + 5 = 20
#
# The goal is to find values of x that make both sides equal.
#
# A solution is valid only if it satisfies the original equation.
#
# An important distinction:
#
#     equation:     2x + 1 = 7
#     expression:   2x + 1
#
# An expression has no equality requirement. An equation does.


# =============================================================================
# SECTION 2: LINEAR EQUATIONS
# =============================================================================

@dataclass
class LinearEquation:
    """
    Represent a one-variable linear equation.

    The equation is:
        a*x + b = c*x + d

    A linear equation normally has:
        one solution,
        no solution, or
        infinitely many solutions.
    """

    a: float
    b: float
    c: float
    d: float

    def solve(self) -> str | float:
        """
        Solve a*x + b = c*x + d.

        Rearrangement:
            a*x - c*x = d - b
            (a-c)x = d-b

        If a-c is nonzero:
            x = (d-b)/(a-c)

        If a-c == 0, the equation becomes either:
            b = d  -> infinitely many solutions
            b != d -> no solution
        """
        coefficient = self.a - self.c
        constant = self.d - self.b

        if approximately_equal(coefficient, 0):
            if approximately_equal(constant, 0):
                return "infinitely many solutions"
            return "no solution"

        return constant / coefficient

    def verify(self, x: float) -> bool:
        """Verify a candidate against the original equation."""
        return approximately_equal(
            self.a * x + self.b,
            self.c * x + self.d,
        )


def solve_linear_standard(a: float, b: float) -> str | float:
    """
    Solve ax + b = 0.

    Standard linear form:
        ax + b = 0

    Therefore:
        x = -b/a

    The case a = 0 must be handled separately.
    """
    if approximately_equal(a, 0):
        if approximately_equal(b, 0):
            return "infinitely many solutions"
        return "no solution"

    return -b / a


def solve_linear_from_points(
    x1: float,
    y1: float,
    x2: float,
    y2: float,
) -> tuple[float, float]:
    """
    Find y = mx + b through two distinct points.

    Slope:
        m = (y2-y1)/(x2-x1)

    Intercept:
        b = y1 - m*x1
    """
    if approximately_equal(x1, x2):
        raise ValueError(
            "The points have the same x-coordinate; they define a vertical line."
        )

    slope = (y2 - y1) / (x2 - x1)
    intercept = y1 - slope * x1
    return slope, intercept


def demonstrate_linear_equations() -> None:
    print_section("LINEAR EQUATIONS")

    examples = [
        LinearEquation(3, 5, 0, 20),       # 3x + 5 = 20
        LinearEquation(5, -7, 0, 18),      # 5x - 7 = 18
        LinearEquation(4, 9, 2, 17),       # 4x + 9 = 2x + 17
        LinearEquation(7, 3, 7, 8),        # impossible
        LinearEquation(7, 3, 7, 3),        # identity
    ]

    for equation in examples:
        result = equation.solve()
        print(
            f"{equation.a}x + {equation.b} = "
            f"{equation.c}x + {equation.d}  ->  {result}"
        )

    result = solve_linear_standard(4, -12)
    print("\nStandard form: 4x - 12 = 0")
    print("x =", format_number(result))

    print("\nVariables on both sides:")
    equation = LinearEquation(8, -3, 3, 12)
    solution = equation.solve()
    print("8x - 3 = 3x + 12")
    print("x =", format_number(solution))
    print("Verified:", equation.verify(solution))

    print("\nEquation involving fractions:")
    # (x/3) + 2 = 6
    # Multiplying every term by 3 gives:
    # x + 6 = 18
    fraction_solution = (6 - 2) * 3
    print("(x/3) + 2 = 6")
    print("x =", fraction_solution)

    print("\nEquation involving decimals:")
    # 0.4x + 1.2 = 3.6
    decimal_solution = (3.6 - 1.2) / 0.4
    print("0.4x + 1.2 = 3.6")
    print("x =", format_number(decimal_solution))

    print("\nLine through two points:")
    slope, intercept = solve_linear_from_points(2, 5, 6, 13)
    print("Points: (2, 5), (6, 13)")
    print("Slope =", format_number(slope))
    print("Intercept =", format_number(intercept))
    print(f"Equation: y = {slope}x + {intercept}")


# =============================================================================
# SECTION 3: LINEAR EQUATIONS WITH PARENTHESES
# =============================================================================

def solve_linear_with_parentheses(
    left_coefficient: float,
    left_constant: float,
    right_coefficient: float,
    right_constant: float,
    multiplier: float,
) -> float:
    """
    Solve:

        multiplier * (left_coefficient*x + left_constant)
            = right_coefficient*x + right_constant

    The function demonstrates the distributive property before isolation.
    """
    # Distribution:
    # k(ax+b) = kax + kb
    expanded_a = multiplier * left_coefficient
    expanded_b = multiplier * left_constant

    return (right_constant - expanded_b) / (
        expanded_a - right_coefficient
    )


def demonstrate_parentheses() -> None:
    print_section("LINEAR EQUATIONS WITH PARENTHESES")

    # 3(2x - 4) = x + 8
    # 6x - 12 = x + 8
    # 5x = 20
    # x = 4
    solution = solve_linear_with_parentheses(2, -4, 1, 8, 3)

    print("3(2x - 4) = x + 8")
    print("Expanded: 6x - 12 = x + 8")
    print("Solution:", format_number(solution))

    # A common error is distributing multiplication to only one term.
    #
    # Incorrect:
    #     3(2x - 4) = 6x - 4
    #
    # Correct:
    #     3(2x - 4) = 6x - 12


# =============================================================================
# SECTION 4: QUADRATIC EQUATIONS
# =============================================================================

@dataclass
class QuadraticEquation:
    """
    Represent a quadratic equation:

        ax^2 + bx + c = 0

    with a != 0.

    The discriminant is:
        D = b^2 - 4ac

    Root classification:
        D > 0  -> two distinct real roots
        D = 0  -> one repeated real root
        D < 0  -> two complex conjugate roots
    """

    a: float
    b: float
    c: float

    def __post_init__(self) -> None:
        if approximately_equal(self.a, 0):
            raise ValueError(
                "A quadratic equation requires a nonzero coefficient of x^2."
            )

    @property
    def discriminant(self) -> float:
        return self.b ** 2 - 4 * self.a * self.c

    def classify_roots(self) -> str:
        d = self.discriminant

        if d > TOLERANCE:
            return "two distinct real roots"
        if abs(d) <= TOLERANCE:
            return "one repeated real root"
        return "two complex conjugate roots"

    def roots(self) -> tuple[complex, complex]:
        """
        Compute roots using the quadratic formula.

        x = (-b +/- sqrt(D)) / (2a)

        cmath.sqrt handles negative discriminants and therefore allows
        the same implementation to produce complex roots.
        """
        d = self.discriminant
        sqrt_d = cmath.sqrt(d)

        root_1 = (-self.b + sqrt_d) / (2 * self.a)
        root_2 = (-self.b - sqrt_d) / (2 * self.a)

        return root_1, root_2

    def vertex(self) -> tuple[float, float]:
        """
        Find the vertex of y = ax^2 + bx + c.

        x-coordinate:
            xv = -b/(2a)

        y-coordinate:
            yv = f(xv)
        """
        x_value = -self.b / (2 * self.a)
        y_value = self.evaluate(x_value)
        return x_value, y_value

    def axis_of_symmetry(self) -> float:
        return -self.b / (2 * self.a)

    def evaluate(self, x: float | complex) -> float | complex:
        return self.a * x ** 2 + self.b * x + self.c

    def verify_roots(self) -> tuple[bool, bool]:
        root_1, root_2 = self.roots()

        return (
            abs(self.evaluate(root_1)) < 1e-8,
            abs(self.evaluate(root_2)) < 1e-8,
        )


def quadratic_formula(a: float, b: float, c: float) -> tuple[complex, complex]:
    """Standalone implementation of the quadratic formula."""
    if approximately_equal(a, 0):
        raise ValueError("a must not be zero.")

    discriminant = b * b - 4 * a * c
    square_root = cmath.sqrt(discriminant)

    return (
        (-b + square_root) / (2 * a),
        (-b - square_root) / (2 * a),
    )


def factor_quadratic_integer(
    a: int,
    b: int,
    c: int,
) -> tuple[int, int] | None:
    """
    Find integer roots when an integer factorization exists.

    This simple educational implementation searches possible integer roots
    using the rational-root theorem.

    For a monic polynomial x^2 + bx + c, integer roots must divide c.
    For general integer coefficients, candidates are p/q where:
        p divides c
        q divides a
    """
    if a == 0:
        raise ValueError("This function requires a quadratic.")

    candidates: set[float] = set()

    constant_factors = integer_divisors(abs(c)) if c != 0 else [0]
    leading_factors = integer_divisors(abs(a))

    for p in constant_factors:
        for q in leading_factors:
            if q == 0:
                continue
            candidates.add(p / q)
            candidates.add(-p / q)

    for candidate in candidates:
        value = a * candidate ** 2 + b * candidate + c
        if abs(value) < TOLERANCE:
            root_1 = candidate

            # If a*x^2 + b*x + c = a(x-r1)(x-r2),
            # product of roots = c/a.
            if not approximately_equal(root_1, 0):
                root_2 = (c / a) / root_1
            else:
                root_2 = -b / a

            if approximately_equal(root_2, round(root_2)):
                return int(round(root_1)), int(round(root_2))

    return None


def integer_divisors(number: int) -> list[int]:
    """Return positive integer divisors."""
    number = abs(number)

    if number == 0:
        return [0]

    divisors: list[int] = []

    for candidate in range(1, math.isqrt(number) + 1):
        if number % candidate == 0:
            divisors.append(candidate)

            other = number // candidate
            if other != candidate:
                divisors.append(other)

    return sorted(divisors)


def complete_the_square(a: float, b: float, c: float) -> tuple[float, float]:
    """
    Return the vertex-form parameters h and k:

        ax^2 + bx + c = a(x-h)^2 + k

    where:
        h = -b/(2a)
        k = f(h)
    """
    if approximately_equal(a, 0):
        raise ValueError("a must not be zero.")

    h = -b / (2 * a)
    k = a * h ** 2 + b * h + c
    return h, k


def demonstrate_quadratics() -> None:
    print_section("QUADRATIC EQUATIONS")

    equations = [
        QuadraticEquation(1, -5, 6),     # x^2 - 5x + 6
        QuadraticEquation(1, -4, 4),     # repeated root
        QuadraticEquation(1, 2, 5),      # complex roots
        QuadraticEquation(2, 3, -2),     # general case
    ]

    for equation in equations:
        roots = equation.roots()

        print(
            f"\nEquation: {equation.a}x^2 + "
            f"{equation.b}x + {equation.c} = 0"
        )
        print("Discriminant:", equation.discriminant)
        print("Classification:", equation.classify_roots())
        print("Roots:", format_number(roots[0]), ",", format_number(roots[1]))

        vertex = equation.vertex()
        print(
            "Vertex:",
            f"({format_number(vertex[0])}, {format_number(vertex[1])})"
        )
        print("Axis of symmetry:", format_number(equation.axis_of_symmetry()))
        print("Root verification:", equation.verify_roots())

    print("\nFactoring example:")
    factor_result = factor_quadratic_integer(1, -5, 6)
    print("x^2 - 5x + 6 = 0")
    print("Integer roots:", factor_result)
    print("Factorization: (x - 2)(x - 3) = 0")

    print("\nCompleting the square:")
    h, k = complete_the_square(1, -6, 5)
    print("x^2 - 6x + 5")
    print(f"Vertex form: (x - {h:g})^2 + ({k:g})")

    print("\nQuadratic formula with a negative discriminant:")
    roots = quadratic_formula(1, 2, 5)
    print("x^2 + 2x + 5 = 0")
    print("Roots:", format_number(roots[0]), ",", format_number(roots[1]))


# =============================================================================
# SECTION 5: QUADRATIC EDGE CASES
# =============================================================================

def solve_general_polynomial_degree_two_or_less(
    a: float,
    b: float,
    c: float,
) -> str | tuple[complex, ...]:
    """
    Solve ax^2 + bx + c = 0 while correctly handling degree reduction.

    Important edge cases:
        a = 0, b != 0 -> linear equation
        a = 0, b = 0, c != 0 -> no solution
        a = 0, b = 0, c = 0 -> infinitely many solutions
    """
    if approximately_equal(a, 0):
        if approximately_equal(b, 0):
            if approximately_equal(c, 0):
                return "infinitely many solutions"
            return "no solution"

        return (complex(-c / b),)

    return quadratic_formula(a, b, c)


def demonstrate_quadratic_edge_cases() -> None:
    print_section("QUADRATIC EDGE CASES")

    cases = [
        (0, 2, -8),    # 2x - 8 = 0
        (0, 0, 5),     # 5 = 0
        (0, 0, 0),     # 0 = 0
    ]

    for a, b, c in cases:
        result = solve_general_polynomial_degree_two_or_less(a, b, c)
        print(f"{a}x^2 + {b}x + {c} = 0  ->  {result}")


# =============================================================================
# SECTION 6: POLYNOMIAL REPRESENTATION
# =============================================================================

class Polynomial:
    """
    Represent a polynomial using coefficients in ascending powers.

    Example:

        3x^3 - 2x + 5

    is stored as:

        [5, -2, 0, 3]

    because:
        index 0 -> constant term
        index 1 -> x term
        index 2 -> x^2 term
        index 3 -> x^3 term

    This representation makes evaluation and arithmetic convenient.
    """

    def __init__(self, coefficients: Sequence[float | complex]):
        if not coefficients:
            coefficients = [0]

        self.coefficients = self._remove_trailing_zeros(
            list(coefficients)
        )

    @staticmethod
    def _remove_trailing_zeros(
        coefficients: list[float | complex],
    ) -> list[float | complex]:
        """Remove redundant highest-degree zero coefficients."""
        while (
            len(coefficients) > 1
            and abs(coefficients[-1]) <= TOLERANCE
        ):
            coefficients.pop()

        return coefficients

    @property
    def degree(self) -> int:
        """Return the polynomial degree."""
        if self.is_zero():
            return 0
        return len(self.coefficients) - 1

    def is_zero(self) -> bool:
        return all(abs(value) <= TOLERANCE for value in self.coefficients)

    def evaluate(self, x: float | complex) -> float | complex:
        """
        Evaluate the polynomial using Horner's method.

        Instead of:
            a0 + a1*x + a2*x^2 + a3*x^3

        Horner's method evaluates:
            ((a3*x + a2)*x + a1)*x + a0

        This reduces the number of multiplications and is generally
        preferable for numerical polynomial evaluation.
        """
        result: float | complex = 0

        for coefficient in reversed(self.coefficients):
            result = result * x + coefficient

        return result

    def derivative(self) -> "Polynomial":
        """
        Differentiate term by term.

        If:
            p(x) = a0 + a1x + a2x^2 + ...

        then:
            p'(x) = a1 + 2a2x + 3a3x^2 + ...
        """
        if self.degree == 0:
            return Polynomial([0])

        derivative_coefficients = [
            index * self.coefficients[index]
            for index in range(1, len(self.coefficients))
        ]

        return Polynomial(derivative_coefficients)

    def integral(self, constant: float = 0) -> "Polynomial":
        """Return an indefinite integral with the specified constant."""
        result = [constant]

        for index, coefficient in enumerate(self.coefficients):
            result.append(coefficient / (index + 1))

        return Polynomial(result)

    def __add__(self, other: "Polynomial") -> "Polynomial":
        maximum_length = max(
            len(self.coefficients),
            len(other.coefficients),
        )

        result = []

        for index in range(maximum_length):
            left = (
                self.coefficients[index]
                if index < len(self.coefficients)
                else 0
            )
            right = (
                other.coefficients[index]
                if index < len(other.coefficients)
                else 0
            )
            result.append(left + right)

        return Polynomial(result)

    def __sub__(self, other: "Polynomial") -> "Polynomial":
        maximum_length = max(
            len(self.coefficients),
            len(other.coefficients),
        )

        result = []

        for index in range(maximum_length):
            left = (
                self.coefficients[index]
                if index < len(self.coefficients)
                else 0
            )
            right = (
                other.coefficients[index]
                if index < len(other.coefficients)
                else 0
            )
            result.append(left - right)

        return Polynomial(result)

    def __mul__(self, other: "Polynomial") -> "Polynomial":
        result = [0] * (
            len(self.coefficients) + len(other.coefficients) - 1
        )

        for i, left in enumerate(self.coefficients):
            for j, right in enumerate(other.coefficients):
                result[i + j] += left * right

        return Polynomial(result)

    def scale(self, factor: float | complex) -> "Polynomial":
        return Polynomial(
            [coefficient * factor for coefficient in self.coefficients]
        )

    def __repr__(self) -> str:
        return f"Polynomial({self.coefficients!r})"

    def to_expression(self) -> str:
        """Convert coefficients into a readable mathematical expression."""
        terms: list[str] = []

        for power in range(self.degree, -1, -1):
            coefficient = self.coefficients[power]

            if abs(coefficient) <= TOLERANCE:
                continue

            if isinstance(coefficient, complex):
                coefficient_text = format_number(coefficient)
            else:
                coefficient_text = format_number(float(coefficient))

            absolute = abs(coefficient)

            if power == 0:
                term = coefficient_text
            elif power == 1:
                if approximately_equal(absolute, 1):
                    term = "x"
                else:
                    term = f"{coefficient_text}x"
            else:
                if approximately_equal(absolute, 1):
                    term = f"x^{power}"
                else:
                    term = f"{coefficient_text}x^{power}"

            if not terms:
                terms.append(term)
            else:
                if isinstance(coefficient, complex):
                    terms.append("+ " + term)
                elif coefficient > 0:
                    terms.append("+ " + term)
                else:
                    terms.append("- " + term.lstrip("-"))

        return " ".join(terms) if terms else "0"


def demonstrate_polynomial_basics() -> None:
    print_section("POLYNOMIAL BASICS")

    polynomial = Polynomial([5, -2, 0, 3])

    print("Polynomial:", polynomial.to_expression())
    print("Coefficients:", polynomial.coefficients)
    print("Degree:", polynomial.degree)

    x = 2
    print(f"p({x}) =", polynomial.evaluate(x))
    print("Derivative:", polynomial.derivative().to_expression())
    print("Integral:", polynomial.integral(7).to_expression())

    other = Polynomial([1, 4, 2])

    print("\nSecond polynomial:", other.to_expression())
    print("Sum:", (polynomial + other).to_expression())
    print("Difference:", (polynomial - other).to_expression())
    print("Product:", (polynomial * other).to_expression())

    print("\nHorner evaluation:")
    print(
        "p(2) computed by Horner's method =",
        polynomial.evaluate(2),
    )


# =============================================================================
# SECTION 7: SYNTHETIC DIVISION
# =============================================================================

def synthetic_division(
    polynomial: Polynomial,
    root: float | complex,
) -> tuple[Polynomial, float | complex]:
    """
    Divide p(x) by (x-root) using synthetic division.

    If:
        p(x) = (x-r)q(x) + R

    then R = p(r).

    The returned quotient and remainder can be used to deflate a polynomial
    after a root has been found.
    """
    coefficients = polynomial.coefficients

    if len(coefficients) <= 1:
        return Polynomial([0]), coefficients[0]

    # Synthetic division is easiest using descending coefficients.
    descending = list(reversed(coefficients))

    quotient_descending = [descending[0]]

    for coefficient in descending[1:-1]:
        next_value = coefficient + quotient_descending[-1] * root
        quotient_descending.append(next_value)

    remainder = descending[-1] + quotient_descending[-1] * root

    quotient_ascending = list(reversed(quotient_descending))

    return Polynomial(quotient_ascending), remainder


def demonstrate_synthetic_division() -> None:
    print_section("SYNTHETIC DIVISION")

    polynomial = Polynomial([-6, 11, -6, 1])
    # p(x) = x^3 - 6x^2 + 11x - 6
    #
    # Since p(1)=0, x-1 is a factor.

    quotient, remainder = synthetic_division(polynomial, 1)

    print("Polynomial:", polynomial.to_expression())
    print("Divide by (x - 1)")
    print("Quotient:", quotient.to_expression())
    print("Remainder:", remainder)

    print("Remainder theorem check:", polynomial.evaluate(1))


# =============================================================================
# SECTION 8: FACTOR AND RATIONAL-ROOT THEOREMS
# =============================================================================

def rational_root_candidates(
    coefficients: Sequence[int],
) -> list[float]:
    """
    Generate candidates from the Rational Root Theorem.

    For:
        a_n x^n + ... + a_0

    every rational root p/q in lowest terms satisfies:
        p divides a_0
        q divides a_n
    """
    polynomial = Polynomial(coefficients)

    if any(
        not isinstance(value, int)
        for value in polynomial.coefficients
    ):
        raise TypeError("Rational-root candidates require integer coefficients.")

    constant = int(polynomial.coefficients[0])
    leading = int(polynomial.coefficients[-1])

    if leading == 0:
        raise ValueError("Leading coefficient must be nonzero.")

    if constant == 0:
        return [0.0]

    candidates: set[float] = set()

    numerator_divisors = integer_divisors(abs(constant))
    denominator_divisors = integer_divisors(abs(leading))

    for numerator in numerator_divisors:
        for denominator in denominator_divisors:
            candidates.add(numerator / denominator)
            candidates.add(-numerator / denominator)

    return sorted(candidates)


def find_rational_roots(
    polynomial: Polynomial,
) -> list[float]:
    """
    Test all rational-root candidates and return the candidates that
    actually satisfy p(x)=0.
    """
    candidates = rational_root_candidates(
        [int(value) for value in polynomial.coefficients]
    )

    return [
        candidate
        for candidate in candidates
        if abs(polynomial.evaluate(candidate)) <= 1e-8
    ]


def factor_by_known_roots(
    polynomial: Polynomial,
    roots: Iterable[float | complex],
) -> Polynomial:
    """
    Repeatedly divide by x-root for each supplied root.

    This is polynomial deflation.
    """
    current = polynomial

    for root in roots:
        current, remainder = synthetic_division(current, root)

        if abs(remainder) > 1e-6:
            raise ValueError(
                f"{root} is not a root within the numerical tolerance."
            )

    return current


def demonstrate_factor_theorem() -> None:
    print_section("FACTOR THEOREM AND RATIONAL-ROOT THEOREM")

    polynomial = Polynomial([-6, 11, -6, 1])

    print("Polynomial:", polynomial.to_expression())
    print("Possible rational roots:")
    print(rational_root_candidates(
        [int(value) for value in polynomial.coefficients]
    ))

    roots = find_rational_roots(polynomial)
    print("Actual rational roots:", roots)

    reduced = factor_by_known_roots(polynomial, roots)
    print("After deflation:", reduced.to_expression())

    print(
        "\nFactor theorem principle:",
        "r is a root exactly when (x-r) is a factor."
    )


# =============================================================================
# SECTION 9: NEWTON-RAPHSON ROOT FINDING
# =============================================================================

def newton_raphson(
    function: Callable[[float], float],
    derivative: Callable[[float], float],
    initial_guess: float,
    max_iterations: int = 100,
    tolerance: float = 1e-12,
) -> tuple[float, int, bool]:
    """
    Find a numerical root using Newton-Raphson iteration.

    Formula:
        x_(n+1) = x_n - f(x_n)/f'(x_n)

    Newton's method can be very fast near a simple root, but it can fail
    when the derivative is zero or when the starting point is poor.
    """
    x = float(initial_guess)

    for iteration in range(1, max_iterations + 1):
        value = function(x)
        slope = derivative(x)

        if abs(slope) <= tolerance:
            return x, iteration, False

        next_x = x - value / slope

        if abs(next_x - x) <= tolerance:
            return next_x, iteration, True

        x = next_x

    return x, max_iterations, abs(function(x)) <= 1e-8


def bisection(
    function: Callable[[float], float],
    lower: float,
    upper: float,
    tolerance: float = 1e-12,
    max_iterations: int = 200,
) -> tuple[float, int, bool]:
    """
    Find a real root using the bisection method.

    Requirement:
        f(lower) and f(upper) must have opposite signs, unless an endpoint
        is already a root.

    Bisection is slower than Newton's method but has strong convergence
    guarantees for continuous functions under the sign-change condition.
    """
    f_lower = function(lower)
    f_upper = function(upper)

    if abs(f_lower) <= tolerance:
        return lower, 0, True

    if abs(f_upper) <= tolerance:
        return upper, 0, True

    if f_lower * f_upper > 0:
        raise ValueError(
            "Bisection requires a sign change across the interval."
        )

    for iteration in range(1, max_iterations + 1):
        midpoint = (lower + upper) / 2
        f_midpoint = function(midpoint)

        if abs(f_midpoint) <= tolerance:
            return midpoint, iteration, True

        if abs(upper - lower) <= tolerance:
            return midpoint, iteration, True

        if f_lower * f_midpoint < 0:
            upper = midpoint
            f_upper = f_midpoint
        else:
            lower = midpoint
            f_lower = f_midpoint

    return (lower + upper) / 2, max_iterations, False


def demonstrate_numerical_roots() -> None:
    print_section("NUMERICAL ROOT FINDING")

    # Solve:
    # x^3 - x - 2 = 0
    #
    # This polynomial does not have a simple rational root.
    polynomial = Polynomial([-2, -1, 0, 1])
    derivative = polynomial.derivative()

    function = lambda x: float(polynomial.evaluate(x))
    derivative_function = lambda x: float(derivative.evaluate(x))

    root_newton, iterations_newton, converged_newton = newton_raphson(
        function,
        derivative_function,
        initial_guess=1.5,
    )

    print("Polynomial:", polynomial.to_expression())
    print("\nNewton-Raphson:")
    print("Root:", format_number(root_newton))
    print("Iterations:", iterations_newton)
    print("Converged:", converged_newton)
    print("Residual:", format_number(function(root_newton)))

    root_bisection, iterations_bisection, converged_bisection = bisection(
        function,
        lower=1,
        upper=2,
    )

    print("\nBisection:")
    print("Root:", format_number(root_bisection))
    print("Iterations:", iterations_bisection)
    print("Converged:", converged_bisection)
    print("Residual:", format_number(function(root_bisection)))


# =============================================================================
# SECTION 10: DURAND-KERER / DURAND-KERNNER-STYLE COMPLEX ROOT FINDING
# =============================================================================

def polynomial_from_descending(
    coefficients: Sequence[float | complex],
) -> Polynomial:
    """Construct a Polynomial from conventional descending coefficients."""
    return Polynomial(list(reversed(coefficients)))


def durand_kerner(
    polynomial: Polynomial,
    max_iterations: int = 1000,
    tolerance: float = 1e-12,
) -> list[complex]:
    """
    Approximate all complex roots of a polynomial using the Durand-Kerner
    method, also known as the Weierstrass method.

    The polynomial must have degree >= 1.

    The method simultaneously refines n approximations:

        z_i(new) =
            z_i - p(z_i) / product(z_i - z_j), j != i

    It is useful because it can approximate all complex roots without
    explicitly factoring the polynomial.

    Numerical methods can require careful initialization and may struggle
    with repeated or closely clustered roots.
    """
    degree = polynomial.degree

    if degree < 1:
        raise ValueError("Polynomial degree must be at least 1.")

    if degree == 1:
        a = polynomial.coefficients[1]
        b = polynomial.coefficients[0]
        return [complex(-b / a)]

    leading = polynomial.coefficients[-1]

    # Normalize to monic form for numerical convenience.
    normalized = polynomial.scale(1 / leading)

    # Deterministic initial guesses distributed around a circle.
    radius = 1.0
    roots = [
        radius * cmath.exp(2j * math.pi * index / degree)
        for index in range(degree)
    ]

    for _ in range(max_iterations):
        maximum_change = 0.0
        new_roots: list[complex] = []

        for i, root in enumerate(roots):
            denominator = 1 + 0j

            for j, other_root in enumerate(roots):
                if i != j:
                    difference = root - other_root

                    # Avoid an exact zero denominator in degenerate
                    # initialization situations.
                    if abs(difference) < 1e-15:
                        difference += 1e-15

                    denominator *= difference

            correction = normalized.evaluate(root) / denominator
            updated_root = root - correction
            new_roots.append(updated_root)

            maximum_change = max(
                maximum_change,
                abs(updated_root - root),
            )

        roots = new_roots

        if maximum_change <= tolerance:
            return roots

    return roots


def demonstrate_complex_polynomial_roots() -> None:
    print_section("NUMERICAL COMPLEX ROOTS OF POLYNOMIALS")

    # x^4 + 1 = 0
    # Its roots are complex and occur symmetrically around the unit circle.
    polynomial = polynomial_from_descending([1, 0, 0, 0, 1])

    roots = durand_kerner(polynomial)

    print("Polynomial:", polynomial.to_expression())
    print("Approximate roots:")

    for root in sorted(roots, key=lambda value: (value.real, value.imag)):
        residual = polynomial.evaluate(root)
        print(
            f"  {format_number(root)}"
            f"   residual={format_number(residual)}"
        )


# =============================================================================
# SECTION 11: SYSTEMS OF LINEAR EQUATIONS
# =============================================================================

@dataclass
class SystemSolution:
    """
    Represent the result of solving a linear system.

    status:
        "unique"
        "infinite"
        "none"

    solution:
        numerical solution when the system has a unique solution
    """

    status: str
    solution: tuple[float, ...] | None = None


def solve_2x2_elimination(
    a1: float,
    b1: float,
    c1: float,
    a2: float,
    b2: float,
    c2: float,
) -> SystemSolution:
    """
    Solve:

        a1*x + b1*y = c1
        a2*x + b2*y = c2

    using determinants.

    Determinant:
        D = a1*b2 - a2*b1

    If D != 0, the system has a unique solution.

    Cramer's formulas:
        x = (c1*b2 - c2*b1)/D
        y = (a1*c2 - a2*c1)/D

    When D = 0, the equations are parallel or coincident, so additional
    consistency checking is required.
    """
    determinant = a1 * b2 - a2 * b1

    if abs(determinant) > TOLERANCE:
        x = (c1 * b2 - c2 * b1) / determinant
        y = (a1 * c2 - a2 * c1) / determinant

        return SystemSolution("unique", (x, y))

    # When the determinant is zero, compare proportional equations.
    left_ratio_x = a1 * c2 - a2 * c1
    left_ratio_y = b1 * c2 - b2 * c1

    if (
        abs(left_ratio_x) <= TOLERANCE
        and abs(left_ratio_y) <= TOLERANCE
    ):
        return SystemSolution("infinite")

    return SystemSolution("none")


def solve_by_substitution(
    a1: float,
    b1: float,
    c1: float,
    a2: float,
    b2: float,
    c2: float,
) -> SystemSolution:
    """
    Solve a 2x2 system using substitution.

    Equation 1:
        a1*x + b1*y = c1

    If b1 != 0:
        y = (c1-a1*x)/b1

    Substituting into equation 2 creates a one-variable linear equation.
    """
    if abs(b1) <= TOLERANCE:
        # Fall back to solving for x if possible.
        if abs(a1) <= TOLERANCE:
            return solve_2x2_elimination(
                a1, b1, c1,
                a2, b2, c2,
            )

        x = c1 / a1

        if abs(b2) <= TOLERANCE:
            if abs(a2 * x - c2) <= TOLERANCE:
                return SystemSolution("infinite")
            return SystemSolution("none")

        y = (c2 - a2 * x) / b2
        return SystemSolution("unique", (x, y))

    # y = alpha*x + beta
    alpha = -a1 / b1
    beta = c1 / b1

    # a2*x + b2*(alpha*x + beta) = c2
    coefficient = a2 + b2 * alpha
    constant = c2 - b2 * beta

    if abs(coefficient) <= TOLERANCE:
        if abs(constant) <= TOLERANCE:
            return SystemSolution("infinite")
        return SystemSolution("none")

    x = constant / coefficient
    y = alpha * x + beta

    return SystemSolution("unique", (x, y))


def verify_2x2_solution(
    equations: Sequence[tuple[float, float, float]],
    solution: tuple[float, float],
) -> bool:
    """Verify a two-variable solution against every equation."""
    x, y = solution

    return all(
        abs(a * x + b * y - c) <= 1e-8
        for a, b, c in equations
    )


def demonstrate_2x2_systems() -> None:
    print_section("SYSTEMS OF TWO LINEAR EQUATIONS")

    equations = (
        (2, 3, 13),
        (4, -1, 5),
    )

    print("System:")
    print("2x + 3y = 13")
    print("4x - y = 5")

    substitution_solution = solve_by_substitution(
        2, 3, 13,
        4, -1, 5,
    )

    elimination_solution = solve_2x2_elimination(
        2, 3, 13,
        4, -1, 5,
    )

    print("\nSubstitution:")
    print(substitution_solution)
    print(
        "Verified:",
        verify_2x2_solution(
            equations,
            substitution_solution.solution,
        ),
    )

    print("\nDeterminant / elimination:")
    print(elimination_solution)

    print("\nInfinite-solution system:")
    infinite = solve_2x2_elimination(
        2, 4, 6,
        1, 2, 3,
    )
    print("2x + 4y = 6")
    print("x + 2y = 3")
    print(infinite)

    print("\nNo-solution system:")
    none = solve_2x2_elimination(
        2, 4, 6,
        1, 2, 5,
    )
    print("2x + 4y = 6")
    print("x + 2y = 5")
    print(none)


# =============================================================================
# SECTION 12: GAUSSIAN ELIMINATION
# =============================================================================

def gaussian_elimination(
    matrix: Sequence[Sequence[float]],
    tolerance: float = 1e-12,
) -> SystemSolution:
    """
    Solve an augmented linear system using Gaussian elimination with
    partial pivoting.

    Input format:

        [
            [a11, a12, ..., b1],
            [a21, a22, ..., b2],
            ...
        ]

    The last column is the right-hand side.

    Partial pivoting chooses the largest available pivot in the current
    column. This improves numerical robustness compared with blindly using
    the first available pivot.

    The function supports:
        unique solutions
        infinitely many solutions
        inconsistent systems

    For educational clarity, the matrix is copied before modification.
    """
    if not matrix:
        raise ValueError("Matrix must not be empty.")

    rows = [list(map(float, row)) for row in matrix]
    column_count = len(rows[0])

    if column_count < 2:
        raise ValueError("An augmented matrix needs coefficients and a RHS.")

    if any(len(row) != column_count for row in rows):
        raise ValueError("All rows must have equal length.")

    equation_count = len(rows)
    variable_count = column_count - 1

    pivot_row = 0
    pivot_columns: list[int] = []

    for column in range(variable_count):
        # Partial pivoting: choose the row with the largest absolute
        # coefficient in the current column.
        best_row = max(
            range(pivot_row, equation_count),
            key=lambda row_index: abs(rows[row_index][column]),
        )

        if abs(rows[best_row][column]) <= tolerance:
            continue

        rows[pivot_row], rows[best_row] = (
            rows[best_row],
            rows[pivot_row],
        )

        pivot = rows[pivot_row][column]

        # Normalize pivot row.
        for j in range(column, column_count):
            rows[pivot_row][j] /= pivot

        # Eliminate the variable from every other row.
        for row in range(equation_count):
            if row == pivot_row:
                continue

            factor = rows[row][column]

            if abs(factor) <= tolerance:
                continue

            for j in range(column, column_count):
                rows[row][j] -= factor * rows[pivot_row][j]

        pivot_columns.append(column)
        pivot_row += 1

        if pivot_row == equation_count:
            break

    # Check for inconsistent rows:
    #
    #     0x + 0y + ... + 0z = nonzero
    #
    # Such a row makes the system inconsistent.
    for row in rows:
        coefficient_part = row[:variable_count]

        if (
            all(abs(value) <= tolerance for value in coefficient_part)
            and abs(row[-1]) > tolerance
        ):
            return SystemSolution("none")

    if len(pivot_columns) < variable_count:
        return SystemSolution("infinite")

    solution = [0.0] * variable_count

    for row, column in enumerate(pivot_columns):
        solution[column] = rows[row][-1]

    return SystemSolution("unique", tuple(solution))


def demonstrate_gaussian_elimination() -> None:
    print_section("GAUSSIAN ELIMINATION")

    matrix = [
        [2, 1, -1, 8],
        [-3, -1, 2, -11],
        [-2, 1, 2, -3],
    ]

    result = gaussian_elimination(matrix)

    print("Augmented matrix:")
    for row in matrix:
        print(row)

    print("\nSolution:")
    print(result)

    if result.solution is not None:
        print(
            "Expected approximately (2, 3, -1):",
            tuple(round(value, 10) for value in result.solution),
        )


# =============================================================================
# SECTION 13: MATRIX RANK AND SYSTEM CLASSIFICATION
# =============================================================================

def matrix_rank(
    matrix: Sequence[Sequence[float]],
    tolerance: float = 1e-12,
) -> int:
    """
    Calculate matrix rank using row reduction.

    Rank is the number of linearly independent rows or columns.

    For a system Ax=b:
        rank(A) < rank([A|b]) -> no solution
        rank(A) = rank([A|b]) < number of variables -> infinitely many
        rank(A) = rank([A|b]) = number of variables -> unique solution
    """
    if not matrix:
        return 0

    rows = [list(map(float, row)) for row in matrix]
    row_count = len(rows)
    column_count = len(rows[0])

    rank = 0

    for column in range(column_count):
        pivot = None

        for row in range(rank, row_count):
            if abs(rows[row][column]) > tolerance:
                pivot = row
                break

        if pivot is None:
            continue

        rows[rank], rows[pivot] = rows[pivot], rows[rank]

        pivot_value = rows[rank][column]

        for j in range(column, column_count):
            rows[rank][j] /= pivot_value

        for row in range(row_count):
            if row == rank:
                continue

            factor = rows[row][column]

            for j in range(column, column_count):
                rows[row][j] -= factor * rows[rank][j]

        rank += 1

        if rank == row_count:
            break

    return rank


def classify_system_by_rank(
    coefficient_matrix: Sequence[Sequence[float]],
    augmented_matrix: Sequence[Sequence[float]],
) -> str:
    """
    Classify a linear system through the ranks of A and [A|b].
    """
    rank_a = matrix_rank(coefficient_matrix)
    rank_augmented = matrix_rank(augmented_matrix)
    variable_count = len(coefficient_matrix[0])

    if rank_a < rank_augmented:
        return "no solution"

    if rank_a < variable_count:
        return "infinitely many solutions"

    return "unique solution"


def demonstrate_rank_classification() -> None:
    print_section("RANK-BASED CLASSIFICATION OF LINEAR SYSTEMS")

    coefficient_matrix = [
        [2, 3],
        [4, -1],
    ]

    augmented_matrix = [
        [2, 3, 13],
        [4, -1, 5],
    ]

    print("rank(A) =", matrix_rank(coefficient_matrix))
    print("rank([A|b]) =", matrix_rank(augmented_matrix))
    print(
        "Classification:",
        classify_system_by_rank(
            coefficient_matrix,
            augmented_matrix,
        ),
    )


# =============================================================================
# SECTION 14: THREE-VARIABLE SYSTEMS
# =============================================================================

def solve_three_variable_system(
    matrix: Sequence[Sequence[float]],
) -> SystemSolution:
    """
    Solve a 3-variable system through Gaussian elimination.

    This wrapper makes the intended input structure explicit.
    """
    if len(matrix) != 3:
        raise ValueError("Exactly three equations are required.")

    if any(len(row) != 4 for row in matrix):
        raise ValueError(
            "Each row must contain three coefficients and one RHS value."
        )

    return gaussian_elimination(matrix)


def demonstrate_three_variable_system() -> None:
    print_section("THREE-VARIABLE SYSTEM")

    matrix = [
        [1, 1, 1, 6],
        [2, -1, 1, 3],
        [1, 2, -1, 2],
    ]

    result = solve_three_variable_system(matrix)

    print("System:")
    print("x + y + z = 6")
    print("2x - y + z = 3")
    print("x + 2y - z = 2")
    print("\nSolution:", result)


# =============================================================================
# SECTION 15: EQUATION TRANSFORMATIONS
# =============================================================================

def demonstrate_equation_rules() -> None:
    print_section("LEGAL EQUATION TRANSFORMATIONS")

    print(
        """
The equality relation is preserved when the same valid operation is
performed on both sides.

Addition/subtraction:
    A = B
    A + C = B + C

Multiplication:
    A = B
    kA = kB

Division:
    A = B
    A/k = B/k
    only when k != 0

Important restriction:
    Multiplying or dividing an equation by zero is not a reversible
    transformation.

Squaring both sides can introduce extraneous solutions.

Example:
    sqrt(x) = -2

Squaring gives:
    x = 4

But x = 4 does NOT satisfy the original equation because:
    sqrt(4) = 2, not -2.

Therefore every transformed candidate should be checked against
the original equation when a non-equivalent operation may have been used.
"""
    )


# =============================================================================
# SECTION 16: EXTRANEOUS SOLUTIONS
# =============================================================================

def demonstrate_extraneous_solution() -> None:
    print_section("EXTRANEOUS SOLUTIONS")

    candidate = 4

    original_left = math.sqrt(candidate)
    original_right = -2

    transformed_equation_holds = (
        candidate == original_right ** 2
    )

    original_equation_holds = approximately_equal(
        original_left,
        original_right,
    )

    print("Original equation: sqrt(x) = -2")
    print("Squaring suggests x =", candidate)
    print("Squared equation holds:", transformed_equation_holds)
    print("Original equation holds:", original_equation_holds)

    print(
        "\nLesson:",
        "A candidate produced by a non-reversible transformation must be checked."
    )


# =============================================================================
# SECTION 17: ABSOLUTE-VALUE EQUATIONS
# =============================================================================

def solve_absolute_value_equation(
    value: float,
    target: float,
) -> tuple[float, ...]:
    """
    Solve |x-value| = target.

    If target > 0:
        x-value = target
        x-value = -target

    If target = 0:
        one solution

    If target < 0:
        no real solution
    """
    if target < 0:
        return ()

    if approximately_equal(target, 0):
        return (value,)

    return (
        value + target,
        value - target,
    )


def demonstrate_absolute_value() -> None:
    print_section("RELATED EQUATION: ABSOLUTE VALUE")

    print("|x - 3| = 5")
    print("Solutions:", solve_absolute_value_equation(3, 5))

    print("|x - 3| = 0")
    print("Solutions:", solve_absolute_value_equation(3, 0))

    print("|x - 3| = -1")
    print("Real solutions:", solve_absolute_value_equation(3, -1))


# =============================================================================
# SECTION 18: RATIONAL EQUATIONS AND DOMAIN RESTRICTIONS
# =============================================================================

def demonstrate_rational_equation_domain() -> None:
    print_section("RATIONAL EQUATIONS AND DOMAIN RESTRICTIONS")

    print(
        """
Example:

    1/(x-2) = 3

The denominator imposes:
    x != 2

Multiplying by x-2 gives:
    1 = 3(x-2)

Then:
    1 = 3x - 6
    7 = 3x
    x = 7/3

The candidate is valid because 7/3 != 2.

The general rule is:
    domain restrictions must be identified before algebraic manipulation,
    and candidate solutions must be checked against those restrictions.
"""
    )

    solution = 7 / 3
    print("Computed solution:", format_number(solution))
    print("Denominator:", format_number(solution - 2))
    print("Valid domain:", not approximately_equal(solution, 2))


# =============================================================================
# SECTION 19: POLYNOMIAL ROOT MULTIPLICITY
# =============================================================================

def polynomial_root_multiplicity(
    polynomial: Polynomial,
    root: float | complex,
    tolerance: float = 1e-8,
) -> int:
    """
    Estimate the multiplicity of a root by repeated synthetic division.

    For example:
        (x-2)^3

    has root 2 with multiplicity 3.

    Numerical multiplicity detection is sensitive to tolerance and
    floating-point errors.
    """
    current = polynomial
    multiplicity = 0

    while current.degree > 0:
        quotient, remainder = synthetic_division(current, root)

        if abs(remainder) <= tolerance:
            multiplicity += 1
            current = quotient
        else:
            break

    return multiplicity


def demonstrate_root_multiplicity() -> None:
    print_section("ROOT MULTIPLICITY")

    # (x-2)^3 = x^3 - 6x^2 + 12x - 8
    polynomial = Polynomial([-8, 12, -6, 1])

    multiplicity = polynomial_root_multiplicity(
        polynomial,
        2,
    )

    print("Polynomial:", polynomial.to_expression())
    print("Root:", 2)
    print("Multiplicity:", multiplicity)


# =============================================================================
# SECTION 20: Vieta's RELATIONS
# =============================================================================

def demonstrate_vieta_relations() -> None:
    print_section("VIÈTE'S RELATIONS")

    print(
        """
For:

    ax^2 + bx + c = 0

with roots r1 and r2:

    r1 + r2 = -b/a
    r1*r2 = c/a

These relationships provide a fast way to verify roots and can sometimes
produce useful information without explicitly solving the equation.
"""
    )

    equation = QuadraticEquation(2, -7, 3)
    root_1, root_2 = equation.roots()

    print("Equation: 2x^2 - 7x + 3 = 0")
    print("Roots:", format_number(root_1), format_number(root_2))

    print(
        "Root sum:",
        format_number(root_1 + root_2),
        "expected:",
        format_number(-equation.b / equation.a),
    )

    print(
        "Root product:",
        format_number(root_1 * root_2),
        "expected:",
        format_number(equation.c / equation.a),
    )


# =============================================================================
# SECTION 21: SYSTEM APPLICATIONS
# =============================================================================

def solve_ticket_word_problem() -> tuple[float, float]:
    """
    Example application.

    A venue sells adult and student tickets.

        a + s = 120
        15a + 8s = 1320

    Solve for adult tickets (a) and student tickets (s).
    """
    result = solve_2x2_elimination(
        1, 1, 120,
        15, 8, 1320,
    )

    if result.status != "unique" or result.solution is None:
        raise RuntimeError("Expected a unique solution.")

    return result.solution


def demonstrate_application() -> None:
    print_section("SYSTEM OF EQUATIONS: WORD-PROBLEM APPLICATION")

    adults, students = solve_ticket_word_problem()

    print("Total tickets:", adults + students)
    print("Adult tickets:", adults)
    print("Student tickets:", students)
    print("Revenue:", 15 * adults + 8 * students)


# =============================================================================
# SECTION 22: QUADRATIC APPLICATION
# =============================================================================

def projectile_height(
    initial_velocity: float,
    initial_height: float,
    gravity: float,
    time: float,
) -> float:
    """
    Basic projectile model:

        h(t) = h0 + v0*t - (g/2)t^2

    For Earth-like conditions, g is approximately 9.81 m/s^2.

    Solving h(t)=0 gives the time when the object reaches ground level,
    subject to the physical domain t >= 0.
    """
    return (
        initial_height
        + initial_velocity * time
        - 0.5 * gravity * time ** 2
    )


def demonstrate_quadratic_application() -> None:
    print_section("QUADRATIC APPLICATION: PROJECTILE MOTION")

    v0 = 20.0
    h0 = 2.0
    g = 9.81

    # h(t) = 2 + 20t - 4.905t^2
    #
    # Rearranged:
    # -4.905t^2 + 20t + 2 = 0
    equation = QuadraticEquation(
        -0.5 * g,
        v0,
        h0,
    )

    roots = equation.roots()

    print("Height equation:")
    print("h(t) = 2 + 20t - 4.905t^2")
    print("Ground-crossing roots:")

    for root in roots:
        print(format_number(root))

    physical_times = [
        root.real
        for root in roots
        if abs(root.imag) < 1e-8 and root.real >= 0
    ]

    print("Physically meaningful time(s):", physical_times)

    for time in physical_times:
        print(
            f"h({time:.8f}) =",
            projectile_height(v0, h0, g, time),
        )


# =============================================================================
# SECTION 23: POLYNOMIAL LONG DIVISION
# =============================================================================

def polynomial_long_division(
    dividend: Polynomial,
    divisor: Polynomial,
) -> tuple[Polynomial, Polynomial]:
    """
    Perform polynomial long division.

    Returns:
        quotient, remainder

    Such that:
        dividend = divisor * quotient + remainder

    with:
        degree(remainder) < degree(divisor)
    """
    if divisor.is_zero():
        raise ZeroDivisionError("Cannot divide by the zero polynomial.")

    remainder = Polynomial(dividend.coefficients[:])

    if remainder.degree < divisor.degree:
        return Polynomial([0]), remainder

    quotient = [0] * (remainder.degree - divisor.degree + 1)

    divisor_leading = divisor.coefficients[-1]

    while (
        not remainder.is_zero()
        and remainder.degree >= divisor.degree
    ):
        degree_difference = remainder.degree - divisor.degree
        factor = remainder.coefficients[-1] / divisor_leading

        quotient[degree_difference] += factor

        subtractor_coefficients = [0] * degree_difference + [
            coefficient * factor
            for coefficient in divisor.coefficients
        ]

        remainder = remainder - Polynomial(subtractor_coefficients)

    return Polynomial(quotient), remainder


def demonstrate_polynomial_long_division() -> None:
    print_section("POLYNOMIAL LONG DIVISION")

    dividend = Polynomial([-6, 11, -6, 1])
    divisor = Polynomial([-1, 1])

    quotient, remainder = polynomial_long_division(
        dividend,
        divisor,
    )

    print("Dividend:", dividend.to_expression())
    print("Divisor:", divisor.to_expression())
    print("Quotient:", quotient.to_expression())
    print("Remainder:", remainder.to_expression())

    reconstructed = divisor * quotient + remainder

    print("Reconstructed:", reconstructed.to_expression())
    print(
        "Correct:",
        all(
            approximately_equal(
                left,
                right,
            )
            for left, right in zip(
                dividend.coefficients,
                reconstructed.coefficients,
            )
        ),
    )


# =============================================================================
# SECTION 24: NUMERICAL CONSIDERATIONS
# =============================================================================

def demonstrate_numerical_precision() -> None:
    print_section("NUMERICAL PRECISION AND EQUATIONS")

    print(
        """
Python floating-point values use finite binary representations.

Some decimal fractions cannot be represented exactly in binary floating
point. Consequently:

    0.1 + 0.2

may not be represented as exactly 0.3.

Equation-solving programs should therefore use tolerances when comparing
floating-point values.

Exact symbolic arithmetic and numerical approximation are different tasks.

For example:
    exact mathematical equality:     1/3 = 1/3
    floating approximation:          0.333333333333...

A tolerance should be chosen according to the scale and conditioning of
the numerical problem rather than treated as a universal constant.
"""
    )

    value = 0.1 + 0.2
    print("0.1 + 0.2 =", repr(value))
    print("Direct equality with 0.3:", value == 0.3)
    print("Tolerance comparison:", approximately_equal(value, 0.3))


# =============================================================================
# SECTION 25: CONDITIONING AND STABILITY EXAMPLE
# =============================================================================

def demonstrate_near_parallel_system() -> None:
    print_section("NEAR-PARALLEL SYSTEMS AND CONDITIONING")

    print(
        """
A system can have a unique mathematical solution while being numerically
sensitive.

Consider:

    x + y = 2
    1.0000001x + y = 2.0000001

The two lines are almost parallel. Small changes in coefficients or
measurements can produce relatively large changes in the computed solution.

This is a conditioning issue, not necessarily an algorithmic bug.
"""
    )

    result = solve_2x2_elimination(
        1,
        1,
        2,
        1.0000001,
        1,
        2.0000001,
    )

    print("Computed result:", result)


# =============================================================================
# SECTION 26: COMMON MISTAKES
# =============================================================================

def demonstrate_common_mistakes() -> None:
    print_section("COMMON EQUATION-SOLVING MISTAKES")

    print(
        """
1. Changing only one side of an equation
   Wrong:
       2x + 4 = 10
       2x = 10
   Correct:
       subtract 4 from both sides
       2x = 6

2. Dividing by an expression that might be zero
   Always check whether the divisor can equal zero.

3. Losing a negative sign
   Carefully track signs when moving terms.

4. Forgetting the coefficient of x^2
   The quadratic formula divides by 2a, not just 2.

5. Using the quadratic formula when a = 0
   If a = 0, the equation is not quadratic.

6. Assuming every polynomial has only real roots
   A degree-n polynomial has n complex roots counting multiplicity,
   but not necessarily n real roots.

7. Accepting numerical approximations without verification
   Substitute the candidate back into the original polynomial or system.

8. Ignoring domain restrictions
   Denominators cannot be zero, and even roots require appropriate
   real-domain constraints when working over the real numbers.

9. Treating a rounded numerical root as exact
   A value such as 1.41421356 is an approximation to sqrt(2).

10. Confusing no solution with infinitely many solutions
       0 = 5 -> no solution
       0 = 0 -> infinitely many solutions
"""
    )


# =============================================================================
# SECTION 27: TESTING
# =============================================================================

def run_tests() -> None:
    """Run internal correctness checks."""
    print_section("AUTOMATED VERIFICATION TESTS")

    # Linear equation
    linear = LinearEquation(3, 5, 0, 20)
    linear_solution = linear.solve()
    assert isinstance(linear_solution, float)
    assert approximately_equal(linear_solution, 5)
    assert linear.verify(linear_solution)

    # Linear edge cases
    assert solve_linear_standard(0, 0) == "infinitely many solutions"
    assert solve_linear_standard(0, 5) == "no solution"

    # Quadratic
    quadratic = QuadraticEquation(1, -5, 6)
    roots = quadratic.roots()
    assert any(approximately_equal(root.real, 2) for root in roots)
    assert any(approximately_equal(root.real, 3) for root in roots)
    assert quadratic.verify_roots() == (True, True)

    # Complex quadratic
    complex_quadratic = QuadraticEquation(1, 0, 1)
    complex_roots = complex_quadratic.roots()

    assert any(
        approximately_equal(root, 1j)
        for root in complex_roots
    )
    assert any(
        approximately_equal(root, -1j)
        for root in complex_roots
    )

    # Polynomial
    polynomial = Polynomial([5, -2, 0, 3])
    assert approximately_equal(polynomial.evaluate(2), 25)

    # Derivative of 3x^3 - 2x + 5 is 9x^2 - 2
    derivative = polynomial.derivative()
    assert derivative.coefficients == [-2, 0, 9]

    # Synthetic division
    cubic = Polynomial([-6, 11, -6, 1])
    quotient, remainder = synthetic_division(cubic, 1)
    assert approximately_equal(remainder, 0)
    assert approximately_equal(quotient.evaluate(2), 0)

    # Rational roots
    rational_roots = find_rational_roots(cubic)
    assert set(rational_roots) == {1, 2, 3}

    # Bisection
    cubic_function = lambda x: x ** 3 - x - 2
    root, _, converged = bisection(cubic_function, 1, 2)
    assert converged
    assert abs(cubic_function(root)) < 1e-8

    # Newton-Raphson
    root, _, converged = newton_raphson(
        cubic_function,
        lambda x: 3 * x ** 2 - 1,
        1.5,
    )
    assert converged
    assert abs(cubic_function(root)) < 1e-8

    # 2x2 system
    system = solve_2x2_elimination(
        2, 3, 13,
        4, -1, 5,
    )
    assert system.status == "unique"
    assert system.solution is not None
    assert verify_2x2_solution(
        [(2, 3, 13), (4, -1, 5)],
        system.solution,
    )

    # Infinite and no solution
    assert solve_2x2_elimination(
        2, 4, 6,
        1, 2, 3,
    ).status == "infinite"

    assert solve_2x2_elimination(
        2, 4, 6,
        1, 2, 5,
    ).status == "none"

    # Gaussian elimination
    gaussian_result = gaussian_elimination([
        [2, 1, -1, 8],
        [-3, -1, 2, -11],
        [-2, 1, 2, -3],
    ])

    assert gaussian_result.status == "unique"
    assert gaussian_result.solution is not None

    expected = (2, 3, -1)

    for actual, expected_value in zip(
        gaussian_result.solution,
        expected,
    ):
        assert abs(actual - expected_value) < 1e-8

    # Polynomial division
    quotient, remainder = polynomial_long_division(
        Polynomial([-6, 11, -6, 1]),
        Polynomial([-1, 1]),
    )

    assert remainder.is_zero()
    assert quotient.to_expression() == "x^2 - 5x + 6"

    # Multiplicity
    repeated = Polynomial([-8, 12, -6, 1])
    assert polynomial_root_multiplicity(repeated, 2) == 3

    print("All tests passed.")


# =============================================================================
# SECTION 28: STUDY REFERENCE TABLE
# =============================================================================

def print_reference_table() -> None:
    print_section("EQUATION REFERENCE")

    rows = [
        ("Linear", "ax + b = 0", "x = -b/a, a != 0"),
        (
            "Quadratic",
            "ax^2 + bx + c = 0",
            "x = (-b +/- sqrt(b^2-4ac))/(2a)",
        ),
        (
            "System 2x2",
            "Ax = b",
            "Elimination, substitution, determinants",
        ),
        (
            "Polynomial",
            "a_nx^n + ... + a_0 = 0",
            "Factoring or numerical root methods",
        ),
    ]

    for name, form, method in rows:
        print(f"{name:<12} | {form:<32} | {method}")


# =============================================================================
# SECTION 29: MAIN EDUCATIONAL PROGRAM
# =============================================================================

def main() -> None:
    """
    Execute all demonstrations in a deliberate learning order.

    Each section can also be studied independently by calling its function.
    """
    print_section("EQUATIONS: COMPLETE PYTHON STUDY PROGRAM")

    print(
        """
This program demonstrates equations from elementary algebra through
numerical polynomial and linear-system methods.

Core idea:
An equation asks for values of variables that make an equality true.

The safest computational workflow is:

    model -> transform -> solve -> verify -> interpret

Verification is especially important when transformations are not
guaranteed to preserve equivalence or when numerical approximations
are involved.
"""
    )

    demonstrate_equation_rules()
    demonstrate_linear_equations()
    demonstrate_parentheses()
    demonstrate_quadratics()
    demonstrate_quadratic_edge_cases()
    demonstrate_polynomial_basics()
    demonstrate_synthetic_division()
    demonstrate_factor_theorem()
    demonstrate_numerical_roots()
    demonstrate_complex_polynomial_roots()
    demonstrate_2x2_systems()
    demonstrate_gaussian_elimination()
    demonstrate_rank_classification()
    demonstrate_three_variable_system()
    demonstrate_extraneous_solution()
    demonstrate_absolute_value()
    demonstrate_rational_equation_domain()
    demonstrate_root_multiplicity()
    demonstrate_vieta_relations()
    demonstrate_application()
    demonstrate_quadratic_application()
    demonstrate_polynomial_long_division()
    demonstrate_numerical_precision()
    demonstrate_near_parallel_system()
    demonstrate_common_mistakes()
    print_reference_table()
    run_tests()


if __name__ == "__main__":
    main()
