"""
Algebraic Expressions
=====================

A self-contained study and practice program covering:

1. Algebraic expressions and terminology
2. Variables, constants, coefficients, and terms
3. Monomials, binomials, trinomials, and polynomials
4. Like and unlike terms
5. Degree and standard form
6. Addition and subtraction of expressions
7. Multiplication and division of monomials
8. Expansion using the distributive property
9. Expansion of binomials and polynomials
10. Algebraic identities
11. Factorization
12. Common-factor extraction
13. Grouping
14. Difference of squares
15. Perfect-square trinomials
16. Sum and difference of cubes
17. Quadratic factorization
18. Evaluation and substitution
19. Polynomial arithmetic
20. Polynomial division
21. Remainder and factor theorem demonstrations
22. Expression parsing and evaluation
23. Simplification of polynomial expressions
24. Edge cases and common mistakes
25. Validation and error handling
26. Unit-style tests
27. A small interactive practice system

The program uses only Python's standard library.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from math import isclose
import re
import unittest
from typing import Dict, Iterable, List, Optional, Sequence, Tuple


# ============================================================================
# SECTION 1: FUNDAMENTAL TERMINOLOGY
# ============================================================================

def explain_fundamentals() -> None:
    print("\n" + "=" * 78)
    print("1. FUNDAMENTAL ALGEBRAIC TERMINOLOGY")
    print("=" * 78)

    print(
        """
An algebraic expression is a mathematical combination of numbers, variables,
operations, and grouping symbols.

Example:
    3x^2 - 5x + 7

The expression contains:
    3x^2  -> term
    -5x   -> term
    7     -> term

Important terminology:
    Variable   : a symbol representing a value, such as x or y.
    Constant   : a fixed numerical value, such as 7 or -3.
    Coefficient: the numerical factor multiplying a variable.
    Term       : a part of an expression separated by + or -.
    Factor     : a quantity multiplied by another quantity.
    Operator   : a mathematical operation such as +, -, *, or /.

For 6x^3:
    coefficient = 6
    variable    = x
    exponent    = 3
    degree      = 3

For -4:
    coefficient = -4
    variable    = none
    degree      = 0
"""
    )


# ============================================================================
# SECTION 2: MONOMIALS, BINOMIALS, TRINOMIALS, POLYNOMIALS
# ============================================================================

@dataclass(frozen=True)
class Term:
    coefficient: Fraction
    exponent: int

    def __post_init__(self) -> None:
        if self.exponent < 0:
            raise ValueError("Polynomial exponents must be non-negative integers.")

    def __str__(self) -> str:
        coefficient = self.coefficient
        exponent = self.exponent

        if exponent == 0:
            return format_fraction(coefficient)

        if coefficient == 1:
            coefficient_text = ""
        elif coefficient == -1:
            coefficient_text = "-"
        else:
            coefficient_text = format_fraction(coefficient)

        if exponent == 1:
            return f"{coefficient_text}x"

        return f"{coefficient_text}x^{exponent}"


def format_fraction(value: Fraction) -> str:
    """Display integers without '/1' and fractions in reduced form."""
    if value.denominator == 1:
        return str(value.numerator)
    return f"{value.numerator}/{value.denominator}"


def classify_expression(term_count: int) -> str:
    """Classify an expression by its number of non-zero terms."""
    if term_count == 0:
        return "zero polynomial"
    if term_count == 1:
        return "monomial"
    if term_count == 2:
        return "binomial"
    if term_count == 3:
        return "trinomial"
    return "polynomial"


def demonstrate_classification() -> None:
    print("\n" + "=" * 78)
    print("2. CLASSIFICATION OF ALGEBRAIC EXPRESSIONS")
    print("=" * 78)

    examples = {
        "7x^3": 1,
        "x + 4": 2,
        "x^2 - 5x + 6": 3,
        "2x^4 - x^3 + 3x^2 - 7": 4,
        "0": 0,
    }

    for expression, count in examples.items():
        print(f"{expression:25} -> {classify_expression(count)}")

    print(
        """
A monomial has exactly one non-zero term.
A binomial has exactly two non-zero terms.
A trinomial has exactly three non-zero terms.
A polynomial is a finite sum of terms involving non-negative integer powers
of the variable.

Examples:
    5x^4       -> monomial
    x + 3      -> binomial
    x^2 + 2x+1 -> trinomial
    4x^3-x+8   -> polynomial

A polynomial cannot contain:
    1/x
    x^(-2)
    sqrt(x)

Those expressions may be algebraic expressions, but they are not polynomials
in x.
"""
    )


# ============================================================================
# SECTION 3: POLYNOMIAL REPRESENTATION
# ============================================================================

class Polynomial:
    """
    Represents a single-variable polynomial in x.

    Internally:
        exponent -> coefficient

    Example:
        3x^2 - 5x + 7

    is stored as:
        {2: 3, 1: -5, 0: 7}

    Zero coefficients are removed automatically.
    """

    def __init__(
        self,
        coefficients: Optional[Dict[int, Fraction | int]] = None
    ) -> None:
        raw = coefficients or {}
        normalized: Dict[int, Fraction] = {}

        for exponent, coefficient in raw.items():
            if not isinstance(exponent, int) or exponent < 0:
                raise ValueError(
                    "Polynomial exponents must be non-negative integers."
                )

            fraction = Fraction(coefficient)

            if fraction != 0:
                normalized[exponent] = fraction

        self.coefficients = normalized

    @classmethod
    def from_terms(cls, terms: Iterable[Term]) -> "Polynomial":
        result: Dict[int, Fraction] = {}

        for term in terms:
            result[term.exponent] = result.get(term.exponent, Fraction(0))
            result[term.exponent] += term.coefficient

        return cls(result)

    @classmethod
    def constant(cls, value: Fraction | int) -> "Polynomial":
        return cls({0: Fraction(value)})

    @classmethod
    def monomial(cls, coefficient: Fraction | int, exponent: int) -> "Polynomial":
        return cls({exponent: Fraction(coefficient)})

    def copy(self) -> "Polynomial":
        return Polynomial(self.coefficients.copy())

    def is_zero(self) -> bool:
        return not self.coefficients

    def degree(self) -> int:
        """
        Degree is the largest exponent with a non-zero coefficient.

        The zero polynomial has no ordinary degree. We return -1 as a useful
        computational convention.
        """
        return max(self.coefficients, default=-1)

    def leading_coefficient(self) -> Fraction:
        if self.is_zero():
            return Fraction(0)
        return self.coefficients[self.degree()]

    def coefficient(self, exponent: int) -> Fraction:
        return self.coefficients.get(exponent, Fraction(0))

    def terms_descending(self) -> List[Term]:
        return [
            Term(self.coefficients[exponent], exponent)
            for exponent in sorted(self.coefficients, reverse=True)
        ]

    def __str__(self) -> str:
        if self.is_zero():
            return "0"

        pieces: List[str] = []

        for term in self.terms_descending():
            coefficient = term.coefficient
            exponent = term.exponent

            absolute = abs(coefficient)

            if exponent == 0:
                body = format_fraction(absolute)
            elif exponent == 1:
                if absolute == 1:
                    body = "x"
                else:
                    body = f"{format_fraction(absolute)}x"
            else:
                if absolute == 1:
                    body = f"x^{exponent}"
                else:
                    body = f"{format_fraction(absolute)}x^{exponent}"

            if not pieces:
                if coefficient < 0:
                    pieces.append("-" + body)
                else:
                    pieces.append(body)
            else:
                sign = "-" if coefficient < 0 else "+"
                pieces.append(f" {sign} {body}")

        return "".join(pieces)

    def __repr__(self) -> str:
        return f"Polynomial({self.coefficients!r})"

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Polynomial):
            return self.coefficients == other.coefficients
        if isinstance(other, (int, Fraction)):
            return self == Polynomial.constant(other)
        return NotImplemented

    def __add__(self, other: "Polynomial | int | Fraction") -> "Polynomial":
        other_poly = to_polynomial(other)
        result = self.coefficients.copy()

        for exponent, coefficient in other_poly.coefficients.items():
            result[exponent] = result.get(exponent, Fraction(0)) + coefficient

        return Polynomial(result)

    def __radd__(self, other: "Polynomial | int | Fraction") -> "Polynomial":
        return self + other

    def __neg__(self) -> "Polynomial":
        return Polynomial(
            {exponent: -coefficient
             for exponent, coefficient in self.coefficients.items()}
        )

    def __sub__(self, other: "Polynomial | int | Fraction") -> "Polynomial":
        return self + (-to_polynomial(other))

    def __rsub__(self, other: "Polynomial | int | Fraction") -> "Polynomial":
        return to_polynomial(other) - self

    def __mul__(self, other: "Polynomial | int | Fraction") -> "Polynomial":
        other_poly = to_polynomial(other)
        result: Dict[int, Fraction] = {}

        for exponent_a, coefficient_a in self.coefficients.items():
            for exponent_b, coefficient_b in other_poly.coefficients.items():
                exponent = exponent_a + exponent_b
                result[exponent] = (
                    result.get(exponent, Fraction(0))
                    + coefficient_a * coefficient_b
                )

        return Polynomial(result)

    def __rmul__(self, other: "Polynomial | int | Fraction") -> "Polynomial":
        return self * other

    def __pow__(self, exponent: int) -> "Polynomial":
        if exponent < 0:
            raise ValueError("Negative polynomial powers are not supported.")
        result = Polynomial.constant(1)

        for _ in range(exponent):
            result *= self

        return result

    def evaluate(self, x: Fraction | int | float) -> Fraction | float:
        """
        Evaluate using Horner's method.

        For:
            ax^3 + bx^2 + cx + d

        Horner form:
            ((a*x + b)*x + c)*x + d

        This reduces the number of multiplication operations.
        """
        if self.is_zero():
            return Fraction(0)

        value: Fraction | float = Fraction(0)
        highest_degree = self.degree()

        for exponent in range(highest_degree, -1, -1):
            value = value * x + self.coefficient(exponent)

        return value

    def derivative(self) -> "Polynomial":
        """Differentiate term by term using d/dx(c*x^n) = n*c*x^(n-1)."""
        result = {}

        for exponent, coefficient in self.coefficients.items():
            if exponent > 0:
                result[exponent - 1] = coefficient * exponent

        return Polynomial(result)

    def integral(self, constant: Fraction | int = 0) -> "Polynomial":
        """Compute an indefinite polynomial integral."""
        result = {0: Fraction(constant)}

        for exponent, coefficient in self.coefficients.items():
            result[exponent + 1] = coefficient / (exponent + 1)

        return Polynomial(result)

    def scale(self, scalar: Fraction | int) -> "Polynomial":
        return Polynomial(
            {
                exponent: coefficient * Fraction(scalar)
                for exponent, coefficient in self.coefficients.items()
            }
        )

    def monic(self) -> "Polynomial":
        """Normalize a non-zero polynomial so its leading coefficient is 1."""
        if self.is_zero():
            raise ValueError("The zero polynomial cannot be made monic.")
        return self.scale(1 / self.leading_coefficient())

    def content(self) -> Fraction:
        """
        Return the greatest common rational factor of coefficients.

        For integer coefficients this corresponds to the numerical content,
        subject to sign convention.
        """
        if self.is_zero():
            return Fraction(0)

        values = list(self.coefficients.values())

        numerator_gcd = values[0].numerator
        denominator_lcm = values[0].denominator

        from math import gcd

        for value in values[1:]:
            numerator_gcd = gcd(numerator_gcd, abs(value.numerator))
            denominator_lcm = denominator_lcm * value.denominator // gcd(
                denominator_lcm,
                value.denominator,
            )

        content = Fraction(numerator_gcd, denominator_lcm)

        if self.leading_coefficient() < 0:
            content = -content

        return content

    def divide_by_monomial(
        self,
        coefficient: Fraction | int,
        exponent: int,
    ) -> "Polynomial":
        """
        Divide by c*x^n.

        Every term must remain a polynomial term, so its exponent must be
        at least n.
        """
        coefficient = Fraction(coefficient)

        if coefficient == 0:
            raise ZeroDivisionError("Cannot divide by a zero monomial.")

        result = {}

        for current_exponent, current_coefficient in self.coefficients.items():
            new_exponent = current_exponent - exponent

            if new_exponent < 0:
                raise ValueError(
                    "Division produces a negative exponent and is not a polynomial."
                )

            result[new_exponent] = current_coefficient / coefficient

        return Polynomial(result)

    def divide_with_remainder(
        self,
        divisor: "Polynomial",
    ) -> Tuple["Polynomial", "Polynomial"]:
        """
        Polynomial long division.

        Returns:
            quotient, remainder

        The identity is:
            dividend = divisor * quotient + remainder

        with:
            degree(remainder) < degree(divisor)
        """
        if divisor.is_zero():
            raise ZeroDivisionError("Polynomial division by zero is undefined.")

        remainder = self.copy()
        quotient = Polynomial.constant(0)

        while not remainder.is_zero() and remainder.degree() >= divisor.degree():
            degree_difference = remainder.degree() - divisor.degree()
            coefficient_ratio = (
                remainder.leading_coefficient()
                / divisor.leading_coefficient()
            )

            term = Polynomial.monomial(
                coefficient_ratio,
                degree_difference,
            )

            quotient += term
            remainder -= divisor * term

        return quotient, remainder


def to_polynomial(
    value: Polynomial | int | Fraction
) -> Polynomial:
    if isinstance(value, Polynomial):
        return value
    return Polynomial.constant(value)


# ============================================================================
# SECTION 4: BASIC POLYNOMIAL OPERATIONS
# ============================================================================

def demonstrate_polynomial_basics() -> None:
    print("\n" + "=" * 78)
    print("3. POLYNOMIAL REPRESENTATION, DEGREE, AND STANDARD FORM")
    print("=" * 78)

    polynomial = Polynomial({
        4: 3,
        2: -5,
        1: 7,
        0: -2,
    })

    print("Polynomial:", polynomial)
    print("Internal representation:", polynomial.coefficients)
    print("Degree:", polynomial.degree())
    print("Leading coefficient:", polynomial.leading_coefficient())
    print("Coefficient of x^2:", polynomial.coefficient(2))
    print("Coefficient of x^3:", polynomial.coefficient(3))
    print("Classification:", classify_expression(len(polynomial.coefficients)))

    print(
        """
Standard form places polynomial terms in descending order of exponent.

Example:
    4 + 3x^3 - 2x + x^2

becomes:
    3x^3 + x^2 - 2x + 4

Like terms have the same variable part and exponent.

Examples:
    3x^2 and -7x^2 -> like terms
    5x and 5x^2    -> unlike terms
    4 and 4x       -> unlike terms

Only like terms can be directly combined.
"""
    )


def demonstrate_addition_and_subtraction() -> None:
    print("\n" + "=" * 78)
    print("4. ADDITION AND SUBTRACTION OF POLYNOMIALS")
    print("=" * 78)

    first = Polynomial({3: 2, 2: 5, 1: -3, 0: 4})
    second = Polynomial({3: -1, 2: 2, 1: 7, 0: -6})

    print("First :", first)
    print("Second:", second)
    print("Sum   :", first + second)
    print("Difference:", first - second)

    print(
        """
Addition combines coefficients of like powers.

For example:
    (3x^2 + 5x - 2) + (4x^2 - x + 7)

Group like terms:
    (3x^2 + 4x^2) + (5x - x) + (-2 + 7)

Result:
    7x^2 + 4x + 5

Subtraction is addition of the additive inverse:
    A - B = A + (-B)

A common mistake is changing the sign of only the first term inside
parentheses instead of every term.
"""
    )


# ============================================================================
# SECTION 5: MULTIPLICATION AND DISTRIBUTIVE PROPERTY
# ============================================================================

def demonstrate_multiplication() -> None:
    print("\n" + "=" * 78)
    print("5. MULTIPLICATION AND EXPANSION")
    print("=" * 78)

    first = Polynomial({1: 3, 0: 2})
    second = Polynomial({1: 4, 0: -5})

    product = first * second

    print(f"({first})({second}) = {product}")

    print(
        """
The distributive property states:
    a(b + c) = ab + ac

For polynomial multiplication, every term of one polynomial is multiplied
by every term of the other.

Example:
    (x + 3)(x + 5)

    = x*x + x*5 + 3*x + 3*5
    = x^2 + 5x + 3x + 15
    = x^2 + 8x + 15

Exponent rule:
    x^m * x^n = x^(m+n)

Coefficient rule:
    (a*x^m)(b*x^n) = (a*b)x^(m+n)

The implementation above performs this operation systematically by combining
every pair of terms.
"""
    )


def demonstrate_special_multiplication() -> None:
    print("\n" + "=" * 78)
    print("6. ALGEBRAIC IDENTITIES")
    print("=" * 78)

    a = Polynomial({1: 1, 0: 3})
    b = Polynomial({1: 1, 0: 5})

    print("(x + 3)^2 =", a ** 2)
    print("(x + 3)(x - 3) =", a * Polynomial({1: 1, 0: -3}))
    print("(x + 3)(x + 5) =", a * b)

    print(
        """
Important identities:

1. Square of a sum:
       (a + b)^2 = a^2 + 2ab + b^2

2. Square of a difference:
       (a - b)^2 = a^2 - 2ab + b^2

3. Difference of squares:
       (a + b)(a - b) = a^2 - b^2

4. Sum of cubes:
       a^3 + b^3 = (a + b)(a^2 - ab + b^2)

5. Difference of cubes:
       a^3 - b^3 = (a - b)(a^2 + ab + b^2)

These identities are useful in both expansion and factorization.

A frequent error is:
    (a + b)^2 = a^2 + b^2

This is false because the middle term 2ab is missing.
"""
    )


# ============================================================================
# SECTION 6: EVALUATION AND SUBSTITUTION
# ============================================================================

def demonstrate_evaluation() -> None:
    print("\n" + "=" * 78)
    print("7. SUBSTITUTION AND EVALUATION")
    print("=" * 78)

    polynomial = Polynomial({3: 2, 2: -3, 1: 4, 0: 5})

    for value in [-2, 0, 1, 3]:
        print(f"{polynomial} at x = {value}: {polynomial.evaluate(value)}")

    print(
        """
To evaluate a polynomial, substitute a value for the variable.

Example:
    P(x) = 2x^2 - 3x + 1

At x = 4:
    P(4) = 2(4^2) - 3(4) + 1
         = 32 - 12 + 1
         = 21

Negative values require careful use of parentheses:
    (-3)^2 = 9
    -3^2  = -9 under conventional operator precedence

This distinction is important when writing expressions in software.
"""
    )


# ============================================================================
# SECTION 7: EXPRESSION PARSING
# ============================================================================

TOKEN_PATTERN = re.compile(
    r"""
    (?P<NUMBER>\d+(?:\.\d+)?)
    |(?P<VARIABLE>[a-zA-Z])
    |(?P<OP>[+\-*/^()])
    |(?P<SPACE>\s+)
    """,
    re.VERBOSE,
)


@dataclass(frozen=True)
class Token:
    kind: str
    value: str


def tokenize(expression: str) -> List[Token]:
    """Convert a simple algebraic expression into tokens."""
    tokens: List[Token] = []
    position = 0

    while position < len(expression):
        match = TOKEN_PATTERN.match(expression, position)

        if match is None:
            raise ValueError(
                f"Invalid character at position {position}: "
                f"{expression[position]!r}"
            )

        kind = match.lastgroup
        value = match.group()

        position = match.end()

        if kind != "SPACE":
            tokens.append(Token(kind, value))

    return tokens


class ExpressionParser:
    """
    Recursive-descent parser for a small expression language.

    Supported:
        numbers
        x
        + - * / ^
        parentheses
        unary + and -
    """

    def __init__(self, expression: str) -> None:
        self.tokens = tokenize(expression)
        self.position = 0

    def current(self) -> Optional[Token]:
        if self.position >= len(self.tokens):
            return None
        return self.tokens[self.position]

    def consume(self) -> Token:
        token = self.current()

        if token is None:
            raise ValueError("Unexpected end of expression.")

        self.position += 1
        return token

    def match(self, kind: str, value: Optional[str] = None) -> bool:
        token = self.current()

        if token is None:
            return False

        return token.kind == kind and (
            value is None or token.value == value
        )

    def expect(self, kind: str, value: Optional[str] = None) -> Token:
        if not self.match(kind, value):
            expected = value if value is not None else kind
            actual = self.current()
            raise ValueError(
                f"Expected {expected}, got {actual.value if actual else 'end of input'}."
            )
        return self.consume()

    def parse(self) -> Polynomial:
        if not self.tokens:
            raise ValueError("Expression cannot be empty.")

        result = self.parse_expression()

        if self.current() is not None:
            raise ValueError(
                f"Unexpected token: {self.current().value}"
            )

        return result

    def parse_expression(self) -> Polynomial:
        result = self.parse_term()

        while self.match("OP", "+") or self.match("OP", "-"):
            operator = self.consume().value
            right = self.parse_term()

            if operator == "+":
                result += right
            else:
                result -= right

        return result

    def parse_term(self) -> Polynomial:
        result = self.parse_power()

        while self.match("OP", "*") or self.match("OP", "/"):
            operator = self.consume().value
            right = self.parse_power()

            if operator == "*":
                result *= right
            else:
                if right.degree() != 0:
                    raise ValueError(
                        "This polynomial-only parser permits division only by constants."
                    )

                divisor = right.coefficient(0)

                if divisor == 0:
                    raise ZeroDivisionError("Division by zero.")

                result = result.scale(1 / divisor)

        return result

    def parse_power(self) -> Polynomial:
        result = self.parse_unary()

        if self.match("OP", "^"):
            self.consume()
            exponent_poly = self.parse_power()

            if exponent_poly.degree() != 0:
                raise ValueError("Polynomial exponents must be constants.")

            exponent = exponent_poly.coefficient(0)

            if exponent.denominator != 1:
                raise ValueError("Polynomial exponent must be an integer.")

            integer_exponent = exponent.numerator

            if integer_exponent < 0:
                raise ValueError(
                    "Negative polynomial exponents are not supported."
                )

            result = result ** integer_exponent

        return result

    def parse_unary(self) -> Polynomial:
        if self.match("OP", "+"):
            self.consume()
            return self.parse_unary()

        if self.match("OP", "-"):
            self.consume()
            return -self.parse_unary()

        return self.parse_primary()

    def parse_primary(self) -> Polynomial:
        token = self.current()

        if token is None:
            raise ValueError("Expected a number, x, or parenthesized expression.")

        if token.kind == "NUMBER":
            self.consume()
            return Polynomial.constant(Fraction(token.value))

        if token.kind == "VARIABLE":
            self.consume()

            if token.value.lower() != "x":
                raise ValueError(
                    "This educational parser supports the variable x only."
                )

            return Polynomial.monomial(1, 1)

        if token.kind == "OP" and token.value == "(":
            self.consume()
            result = self.parse_expression()
            self.expect("OP", ")")
            return result

        raise ValueError(f"Unexpected token: {token.value}")


def parse_polynomial(expression: str) -> Polynomial:
    return ExpressionParser(expression).parse()


def demonstrate_parser() -> None:
    print("\n" + "=" * 78)
    print("8. PARSING ALGEBRAIC EXPRESSIONS")
    print("=" * 78)

    examples = [
        "3*x^2 + 5*x - 7",
        "(x + 2)*(x - 2)",
        "2*(x + 3)^2",
        "-(x - 4)",
        "6*x^3 - 2*x^2 + x - 9",
        "(x + 1)*(x + 1)*(x - 1)",
    ]

    for expression in examples:
        result = parse_polynomial(expression)
        print(f"{expression:40} -> {result}")

    print(
        """
Parsing converts a textual expression into a structured mathematical
representation.

The parser demonstrates several important implementation ideas:

    tokenization
    grammar
    operator precedence
    recursive descent
    parentheses
    unary operators
    validation
    error handling

The precedence used here is:

    parentheses
        ↓
    unary + and -
        ↓
    exponentiation
        ↓
    multiplication and division
        ↓
    addition and subtraction

A parser is preferable to blindly evaluating arbitrary text because explicit
grammar and validation can restrict what the program is allowed to process.
"""
    )


# ============================================================================
# SECTION 9: FACTORIZATION
# ============================================================================

def factor_out_common_monomial(polynomial: Polynomial) -> Tuple[Polynomial, Polynomial]:
    """
    Extract a common monomial factor.

    Returns:
        factor, remaining_polynomial

    Example:
        6x^3 + 9x^2

        common factor = 3x^2
        remaining    = 2x + 3
    """
    if polynomial.is_zero():
        raise ValueError("Every non-zero expression divides zero, so factoring "
                         "the zero polynomial requires a convention.")

    exponents = list(polynomial.coefficients.keys())
    minimum_exponent = min(exponents)

    coefficients = list(polynomial.coefficients.values())

    # For integer coefficients, find the integer GCD.
    if all(value.denominator == 1 for value in coefficients):
        from math import gcd

        coefficient_gcd = abs(coefficients[0].numerator)

        for coefficient in coefficients[1:]:
            coefficient_gcd = gcd(
                coefficient_gcd,
                abs(coefficient.numerator),
            )

        if coefficient_gcd == 0:
            coefficient_gcd = 1

        if polynomial.leading_coefficient() < 0:
            coefficient_gcd = -coefficient_gcd

        factor = Polynomial.monomial(coefficient_gcd, minimum_exponent)
    else:
        # For rational coefficients, use the smallest absolute rational
        # coefficient as a conservative common factor.
        factor_value = min(abs(value) for value in coefficients)

        if polynomial.leading_coefficient() < 0:
            factor_value = -factor_value

        factor = Polynomial.monomial(factor_value, minimum_exponent)

    remaining = polynomial.divide_by_monomial(
        factor.coefficient(factor.degree()),
        factor.degree(),
    )

    return factor, remaining


def factor_quadratic_integer(
    polynomial: Polynomial
) -> Optional[Tuple[Polynomial, Polynomial]]:
    """
    Factor a quadratic with integer coefficients when integer linear factors
    can be found.

    For ax^2 + bx + c, this searches for integer roots using the rational-root
    theorem candidates derived from factors of c and a.

    This is intentionally a transparent educational implementation rather than
    a symbolic algebra system.
    """
    if polynomial.degree() != 2:
        return None

    a = polynomial.coefficient(2)
    b = polynomial.coefficient(1)
    c = polynomial.coefficient(0)

    if any(value.denominator != 1 for value in (a, b, c)):
        return None

    a_int = a.numerator
    b_int = b.numerator
    c_int = c.numerator

    if c_int == 0:
        factor1 = Polynomial({1: 1, 0: 0})
        factor2 = Polynomial({1: a_int, 0: b_int})
        return factor1, factor2

    def divisors(number: int) -> List[int]:
        number = abs(number)
        result = []

        for candidate in range(1, number + 1):
            if number % candidate == 0:
                result.append(candidate)

        return result

    candidates = set()

    for p in divisors(c_int):
        for q in divisors(a_int):
            if q != 0:
                candidates.add(Fraction(p, q))
                candidates.add(Fraction(-p, q))

    for root in candidates:
        if polynomial.evaluate(root) == 0:
            first_factor = Polynomial({
                1: 1,
                0: -root,
            })

            quotient, remainder = polynomial.divide_with_remainder(first_factor)

            if remainder.is_zero():
                return first_factor, quotient

    return None


def factor_by_grouping(polynomial: Polynomial) -> Optional[Tuple[Polynomial, Polynomial]]:
    """
    Attempt a simple grouping factorization for four-term polynomials.

    Example:
        x^3 + 3x^2 + 2x + 6

        = x^2(x + 3) + 2(x + 3)
        = (x^2 + 2)(x + 3)

    The implementation tests the natural two-and-two split.
    """
    if polynomial.degree() != 3 or len(polynomial.coefficients) != 4:
        return None

    exponents = sorted(polynomial.coefficients, reverse=True)

    first = Polynomial({
        exponents[0]: polynomial.coefficient(exponents[0]),
        exponents[1]: polynomial.coefficient(exponents[1]),
    })

    second = Polynomial({
        exponents[2]: polynomial.coefficient(exponents[2]),
        exponents[3]: polynomial.coefficient(exponents[3]),
    })

    try:
        factor1, remaining1 = factor_out_common_monomial(first)
        factor2, remaining2 = factor_out_common_monomial(second)
    except ValueError:
        return None

    if remaining1 == remaining2:
        return remaining1, factor1 + factor2

    return None


def factor_difference_of_squares(
    polynomial: Polynomial
) -> Optional[Tuple[Polynomial, Polynomial]]:
    """
    Detect a^2 - b^2 where a and b are monomials.

    For example:
        x^2 - 9 = (x - 3)(x + 3)
        4x^2 - 25 = (2x - 5)(2x + 5)
    """
    if polynomial.degree() % 2 != 0:
        return None

    if len(polynomial.coefficients) != 2:
        return None

    highest = polynomial.degree()
    constant = polynomial.coefficient(0)

    if constant >= 0:
        return None

    leading = polynomial.leading_coefficient()

    if leading <= 0:
        return None

    # Integer perfect-square detection.
    if leading.denominator != 1 or (-constant).denominator != 1:
        return None

    leading_int = leading.numerator
    constant_int = (-constant).numerator

    root_leading = int(leading_int ** 0.5)
    root_constant = int(constant_int ** 0.5)

    if root_leading ** 2 != leading_int:
        return None

    if root_constant ** 2 != constant_int:
        return None

    middle_degree = highest // 2

    left = Polynomial.monomial(root_leading, middle_degree)
    right = Polynomial.constant(root_constant)

    return left - right, left + right


def factor_perfect_square_trinomial(
    polynomial: Polynomial
) -> Optional[Tuple[Polynomial, Polynomial]]:
    """
    Detect a perfect-square trinomial.

    a^2 + 2ab + b^2 = (a+b)^2
    a^2 - 2ab + b^2 = (a-b)^2
    """
    if polynomial.degree() != 2 or len(polynomial.coefficients) != 3:
        return None

    a = polynomial.coefficient(2)
    b = polynomial.coefficient(1)
    c = polynomial.coefficient(0)

    if any(value.denominator != 1 for value in (a, b, c)):
        return None

    if a < 0 or c < 0:
        return None

    a_root = int(a.numerator ** 0.5)
    c_root = int(c.numerator ** 0.5)

    if a_root ** 2 != a.numerator:
        return None

    if c_root ** 2 != c.numerator:
        return None

    expected_positive = 2 * a_root * c_root
    expected_negative = -expected_positive

    if b.numerator == expected_positive:
        factor = Polynomial({1: a_root, 0: c_root})
        return factor, factor

    if b.numerator == expected_negative:
        factor = Polynomial({1: a_root, 0: -c_root})
        return factor, factor

    return None


def demonstrate_factorization() -> None:
    print("\n" + "=" * 78)
    print("9. FACTORIZATION")
    print("=" * 78)

    examples = [
        Polynomial({3: 6, 2: 9}),
        Polynomial({2: 1, 0: -16}),
        Polynomial({2: 1, 1: 6, 0: 9}),
        Polynomial({2: 1, 1: 5, 0: 6}),
        Polynomial({3: 1, 2: 3, 1: 2, 0: 6}),
    ]

    for polynomial in examples:
        print(f"\nExpression: {polynomial}")

        factor, remainder = factor_out_common_monomial(polynomial)
        if factor.degree() > 0 or abs(factor.coefficient(0)) > 1:
            print(
                f"Common-factor extraction: "
                f"{factor} * ({remainder})"
            )

        difference = factor_difference_of_squares(polynomial)
        if difference:
            print(
                "Difference of squares:",
                f"({difference[0]})({difference[1]})"
            )

        square = factor_perfect_square_trinomial(polynomial)
        if square:
            print(
                "Perfect-square trinomial:",
                f"({square[0]})({square[1]})"
            )

        quadratic = factor_quadratic_integer(polynomial)
        if quadratic:
            print(
                "Quadratic factorization:",
                f"({quadratic[0]})({quadratic[1]})"
            )

        grouping = factor_by_grouping(polynomial)
        if grouping:
            print(
                "Grouping:",
                f"({grouping[0]})({grouping[1]})"
            )

    print(
        """
Factorization reverses multiplication.

Common techniques:

1. Greatest common factor
       6x^3 + 9x^2 = 3x^2(2x + 3)

2. Grouping
       ax + ay + bx + by
       = a(x+y) + b(x+y)
       = (a+b)(x+y)

3. Difference of squares
       a^2 - b^2 = (a-b)(a+b)

4. Perfect-square trinomial
       a^2 + 2ab + b^2 = (a+b)^2
       a^2 - 2ab + b^2 = (a-b)^2

5. Quadratic factorization
       x^2 + 5x + 6
       = (x+2)(x+3)

The order of factorization matters strategically. A common factor should
usually be extracted first because it can reveal a recognizable identity.
"""
    )


# ============================================================================
# SECTION 10: CUBIC IDENTITIES
# ============================================================================

def demonstrate_cubic_identities() -> None:
    print("\n" + "=" * 78)
    print("10. SUM AND DIFFERENCE OF CUBES")
    print("=" * 78)

    x = Polynomial.monomial(1, 1)
    two = Polynomial.constant(2)

    sum_expression = x ** 3 + two ** 3
    difference_expression = x ** 3 - two ** 3

    sum_factorization = (x + two) * (
        x ** 2 - two * x + two ** 2
    )

    difference_factorization = (x - two) * (
        x ** 2 + two * x + two ** 2
    )

    print("x^3 + 8 =", sum_expression)
    print("Factored:", sum_factorization)

    print("x^3 - 8 =", difference_expression)
    print("Factored:", difference_factorization)

    print(
        """
The signs are easy to confuse.

Sum of cubes:
    a^3 + b^3
    = (a+b)(a^2 - ab + b^2)

Difference of cubes:
    a^3 - b^3
    = (a-b)(a^2 + ab + b^2)

The first factor keeps the original sign between a and b.
The quadratic factor uses the opposite sign for the middle term and a
positive final term.
"""
    )


# ============================================================================
# SECTION 11: POLYNOMIAL DIVISION
# ============================================================================

def demonstrate_polynomial_division() -> None:
    print("\n" + "=" * 78)
    print("11. POLYNOMIAL LONG DIVISION")
    print("=" * 78)

    dividend = Polynomial({3: 1, 2: -6, 1: 11, 0: -6})
    divisor = Polynomial({1: 1, 0: -1})

    quotient, remainder = dividend.divide_with_remainder(divisor)

    print("Dividend :", dividend)
    print("Divisor  :", divisor)
    print("Quotient :", quotient)
    print("Remainder:", remainder)

    reconstructed = divisor * quotient + remainder
    print("Reconstructed dividend:", reconstructed)

    print(
        """
Polynomial division follows the same broad principle as numerical long
division.

For:
    P(x) / D(x)

the result is:
    P(x) = D(x)Q(x) + R(x)

where:
    degree(R) < degree(D)

If the remainder is zero, the divisor is a factor of the dividend.

This is useful for factorization, root finding, and polynomial simplification.
"""
    )


# ============================================================================
# SECTION 12: REMAINDER THEOREM AND FACTOR THEOREM
# ============================================================================

def remainder_theorem(
    polynomial: Polynomial,
    value: Fraction | int,
) -> Fraction:
    """
    Remainder theorem:
        Remainder of P(x) divided by x-a is P(a).
    """
    return Fraction(polynomial.evaluate(value))


def factor_theorem(
    polynomial: Polynomial,
    value: Fraction | int,
) -> bool:
    """
    Factor theorem:
        x-a is a factor of P(x) exactly when P(a)=0.
    """
    return remainder_theorem(polynomial, value) == 0


def demonstrate_theorems() -> None:
    print("\n" + "=" * 78)
    print("12. REMAINDER THEOREM AND FACTOR THEOREM")
    print("=" * 78)

    polynomial = Polynomial({3: 1, 2: -6, 1: 11, 0: -6})

    for value in [1, 2, 3, 4]:
        remainder = remainder_theorem(polynomial, value)
        is_factor = factor_theorem(polynomial, value)

        print(
            f"P({value}) = {remainder:>3} | "
            f"(x - {value}) is a factor: {is_factor}"
        )

    print(
        """
Remainder theorem:
    When P(x) is divided by x-a, the remainder is P(a).

Factor theorem:
    x-a is a factor of P(x) if and only if P(a)=0.

These are closely related:
    remainder = 0
        <=> divisor is a factor
        <=> corresponding value is a root
"""
    )


# ============================================================================
# SECTION 13: DERIVATIVE AND STRUCTURAL ANALYSIS
# ============================================================================

def demonstrate_derivative_and_integral() -> None:
    print("\n" + "=" * 78)
    print("13. POLYNOMIAL DERIVATIVE AND INTEGRAL")
    print("=" * 78)

    polynomial = Polynomial({4: 3, 3: -2, 1: 5, 0: 7})

    derivative = polynomial.derivative()
    integral = polynomial.integral()

    print("P(x)      =", polynomial)
    print("P'(x)     =", derivative)
    print("Integral  =", integral)

    print(
        """
Although derivatives and integrals belong to calculus, polynomial structure
makes both operations particularly direct.

Derivative rule:
    d/dx [a*x^n] = n*a*x^(n-1)

Integral rule:
    integral[a*x^n] dx = a/(n+1) * x^(n+1) + C

For example:
    d/dx(4x^3 - 2x + 7)
    = 12x^2 - 2

The constant disappears under differentiation.
"""
    )


# ============================================================================
# SECTION 14: FRACTIONS AND EXACT ARITHMETIC
# ============================================================================

def demonstrate_exact_arithmetic() -> None:
    print("\n" + "=" * 78)
    print("14. EXACT FRACTIONAL COEFFICIENTS")
    print("=" * 78)

    polynomial = Polynomial({
        2: Fraction(1, 2),
        1: Fraction(3, 4),
        0: Fraction(-5, 6),
    })

    second = Polynomial({
        1: Fraction(2, 3),
        0: Fraction(1, 5),
    })

    print("First :", polynomial)
    print("Second:", second)
    print("Sum   :", polynomial + second)
    print("Product:", polynomial * second)

    print(
        """
Using Fraction avoids many floating-point rounding problems.

For symbolic algebra, exact arithmetic is often preferable to decimal
floating-point arithmetic.

For example:
    1/3 + 1/3 + 1/3

is exactly 1 when represented using Fraction.

Floating-point arithmetic can represent many decimal values only
approximately, so equality tests involving symbolic coefficients require
care.
"""
    )


# ============================================================================
# SECTION 15: EDGE CASES
# ============================================================================

def demonstrate_edge_cases() -> None:
    print("\n" + "=" * 78)
    print("15. EDGE CASES AND EXCEPTIONS")
    print("=" * 78)

    zero = Polynomial.constant(0)
    constant = Polynomial.constant(7)
    linear = Polynomial({1: 4, 0: 3})

    print("Zero polynomial:", zero)
    print("Zero degree convention:", zero.degree())
    print("Constant polynomial:", constant)
    print("Constant degree:", constant.degree())
    print("Linear polynomial:", linear)
    print("Linear degree:", linear.degree())

    print(
        """
Important edge cases:

1. Zero polynomial
   The degree of the zero polynomial is convention-dependent. This program
   uses -1 as a computational convention.

2. Constant polynomial
   A non-zero constant has degree 0.

3. Missing powers
   5x^4 + 2x does not contain an x^3 or x^2 term. Their coefficients are
   treated as zero.

4. Zero coefficients
   Terms with zero coefficients are removed from the internal representation.

5. Division by zero
   Polynomial division by the zero polynomial is undefined.

6. Negative exponents
   x^-1 is not a polynomial term.

7. Fractional exponents
   x^(1/2) is not a polynomial term.

8. Non-polynomial division
   Dividing by x creates a rational expression unless every term is divisible
   by x.

9. Cancellation
   x^2 - x^2 becomes the zero polynomial.

10. Sign handling
   -(-x + 3) becomes x - 3. Every term inside the parentheses changes sign.
"""
    )


# ============================================================================
# SECTION 16: COMMON MISTAKES
# ============================================================================

def demonstrate_common_mistakes() -> None:
    print("\n" + "=" * 78)
    print("16. COMMON ALGEBRAIC MISTAKES")
    print("=" * 78)

    correct_results = {
        "(x + 3)^2": parse_polynomial("(x + 3)^2"),
        "x^2 - 9": parse_polynomial("x^2 - 9"),
        "2*x + 3*x": parse_polynomial("2*x + 3*x"),
        "x*(x + 4)": parse_polynomial("x*(x + 4)"),
    }

    for expression, result in correct_results.items():
        print(f"{expression:20} = {result}")

    print(
        """
Mistake 1:
    (a+b)^2 = a^2+b^2

Correct:
    (a+b)^2 = a^2+2ab+b^2

Mistake 2:
    x^2 + x^3 = x^5

Incorrect. Addition does not add exponents.

Correct:
    x^2 + x^3 remains x^2 + x^3

Mistake 3:
    x^2 * x^3 = x^6

Incorrect.

Correct:
    x^2 * x^3 = x^5

Mistake 4:
    3x + 2 = 5x

Incorrect because 3x and 2 are unlike terms.

Mistake 5:
    -(x - 4) = -x - 4

Incorrect.

Correct:
    -(x - 4) = -x + 4

Mistake 6:
    Cancelling terms across addition.

For example:
    (x + 2) / x

cannot be simplified to 1 + 2 without preserving the denominator structure
as a rational expression. Algebraic cancellation applies to factors, not
arbitrary terms in sums.
"""
    )


# ============================================================================
# SECTION 17: PERFORMANCE CONSIDERATIONS
# ============================================================================

def demonstrate_performance_considerations() -> None:
    print("\n" + "=" * 78)
    print("17. PERFORMANCE AND IMPLEMENTATION CONSIDERATIONS")
    print("=" * 78)

    polynomial_a = Polynomial({i: i + 1 for i in range(10)})
    polynomial_b = Polynomial({i: 2 * i + 1 for i in range(10)})

    product = polynomial_a * polynomial_b

    print("Degree of A:", polynomial_a.degree())
    print("Degree of B:", polynomial_b.degree())
    print("Degree of A*B:", product.degree())

    print(
        """
Sparse representation:
    The polynomial is stored as exponent -> coefficient.

This is useful when many coefficients are zero.

Polynomial addition:
    O(n + m) approximately, when terms are stored in dictionaries.

Naive multiplication:
    O(n*m), where n and m are the numbers of stored terms.

Evaluation with Horner's method:
    O(d), where d is the degree, rather than repeatedly computing powers.

Polynomial long division:
    Its cost depends on the degrees and sparsity of the dividend and divisor.

For very large symbolic workloads, specialized computer algebra algorithms
can substantially improve performance, but transparency is more important in
this educational implementation.
"""
    )


# ============================================================================
# SECTION 18: SECURITY AND SAFE PARSING
# ============================================================================

def demonstrate_safe_parsing() -> None:
    print("\n" + "=" * 78)
    print("18. SAFE EXPRESSION HANDLING")
    print("=" * 78)

    safe_examples = [
        "x^2 + 2*x + 1",
        "(x - 3)*(x + 3)",
        "2*x^3 - 5*x + 8",
    ]

    for expression in safe_examples:
        print(f"{expression:30} -> {parse_polynomial(expression)}")

    print(
        """
When software accepts user-entered mathematical expressions, security matters.

A dangerous design is to pass arbitrary user input directly to Python's
eval() because eval() can execute Python expressions and potentially perform
operations that were never intended.

This program instead:
    1. Tokenizes an explicitly allowed grammar.
    2. Rejects unsupported characters.
    3. Accepts only selected operators.
    4. Restricts the variable to x.
    5. Rejects unsupported polynomial operations.
    6. Raises controlled exceptions for invalid input.

This approach demonstrates the general security principle of allowlisting
valid syntax rather than executing arbitrary input.
"""
    )


# ============================================================================
# SECTION 19: COMPARISONS
# ============================================================================

def demonstrate_comparisons() -> None:
    print("\n" + "=" * 78)
    print("19. IMPORTANT DISTINCTIONS")
    print("=" * 78)

    distinctions = [
        ("Expression", "3x + 2", "A mathematical combination; it need not equal a particular value."),
        ("Equation", "3x + 2 = 11", "A statement asserting equality."),
        ("Identity", "(x+1)^2 = x^2 + 2x + 1", "True for every permitted value of x."),
        ("Polynomial", "x^3 - 2x + 1", "A finite sum of non-negative integer powers of x."),
        ("Monomial", "7x^4", "One non-zero term."),
        ("Binomial", "x + 5", "Two non-zero terms."),
        ("Trinomial", "x^2 + 3x + 2", "Three non-zero terms."),
        ("Factor", "x + 2", "A multiplicative component."),
        ("Root", "x = -2", "A value making a polynomial equal to zero."),
    ]

    for category, example, meaning in distinctions:
        print(f"{category:12} | {example:24} | {meaning}")

    print(
        """
Expression versus equation:
    An expression does not contain an equality assertion.
    An equation states that two expressions are equal.

Expression versus identity:
    An identity is an equality that holds for every value in its domain.

Expansion versus factorization:
    Expansion converts a product into a sum.
    Factorization converts a sum or polynomial into a product.

Degree versus number of terms:
    x^5 + 1 has degree 5 but only 2 terms.
    x^2 + x + 1 has degree 2 and 3 terms.

Coefficient versus factor:
    In 6x^2, 6 is a coefficient and x^2 is the variable factor.
"""
    )


# ============================================================================
# SECTION 20: PROGRESSIVE WORKED EXAMPLES
# ============================================================================

def worked_examples() -> None:
    print("\n" + "=" * 78)
    print("20. PROGRESSIVE WORKED EXAMPLES")
    print("=" * 78)

    examples = [
        ("Beginner", "3*x + 5*x - 2", "Combine like terms"),
        ("Intermediate", "(x + 4)*(x - 2)", "Expand"),
        ("Intermediate", "(x + 3)^2", "Use a square identity"),
        ("Advanced", "(x^2 - 9)*(x + 2)", "Combine identities and multiplication"),
        ("Advanced", "(x + 1)*(x + 1)*(x - 1)", "Repeated polynomial multiplication"),
    ]

    for level, expression, purpose in examples:
        result = parse_polynomial(expression)
        print(f"{level:12} | {purpose:40} | {expression} = {result}")

    print(
        """
The examples progress from simple coefficient collection to nested products.

A reliable algebraic workflow is:

    1. Identify the structure.
    2. Look for parentheses.
    3. Look for common factors.
    4. Recognize identities when applicable.
    5. Expand only when useful.
    6. Combine like terms.
    7. Put the result in standard form.
    8. Check the result by substitution or multiplication.

Factored and expanded forms are mathematically equivalent when correctly
transformed, but each form is useful for different tasks.

Factored form is often better for:
    roots
    zeros
    solving equations
    identifying structure

Expanded form is often better for:
    collecting coefficients
    comparing polynomial coefficients
    differentiation
    direct evaluation
"""
    )


# ============================================================================
# SECTION 21: VALIDATION HELPERS
# ============================================================================

def assert_polynomial_equal(
    actual: Polynomial,
    expected: Polynomial,
    message: str = "",
) -> None:
    if actual != expected:
        raise AssertionError(
            f"{message}\nExpected: {expected}\nActual: {actual}"
        )


def validate_identity(
    left: Polynomial,
    right: Polynomial,
    test_values: Sequence[int],
) -> bool:
    """
    Validate an algebraic identity numerically at several points.

    Symbolic equality is stronger, so this function is intended as a practical
    cross-check rather than a proof.
    """
    if left == right:
        return True

    for value in test_values:
        left_value = left.evaluate(value)
        right_value = right.evaluate(value)

        if left_value != right_value:
            return False

    return True


def demonstrate_validation() -> None:
    print("\n" + "=" * 78)
    print("22. VALIDATING ALGEBRAIC IDENTITIES")
    print("=" * 78)

    left = parse_polynomial("(x + 5)^2")
    right = parse_polynomial("x^2 + 10*x + 25")

    print("Left :", left)
    print("Right:", right)
    print(
        "Identity verified symbolically:",
        left == right,
    )
    print(
        "Numerical cross-check:",
        validate_identity(left, right, [-10, -1, 0, 1, 10]),
    )

    print(
        """
Symbolic equality is preferable to testing a handful of values.

Testing values is useful as a debugging technique, but a finite collection
of numerical tests cannot by itself establish that two arbitrary expressions
are identical for all possible values.

The program therefore uses direct polynomial coefficient comparison for
symbolic equality and numerical evaluation as an independent cross-check.
"""
    )


# ============================================================================
# SECTION 23: UNIT TESTS
# ============================================================================

class PolynomialTests(unittest.TestCase):

    def test_addition(self) -> None:
        first = Polynomial({2: 3, 1: 2, 0: 1})
        second = Polynomial({2: 4, 1: -2, 0: 5})

        expected = Polynomial({2: 7, 0: 6})

        self.assertEqual(first + second, expected)

    def test_subtraction(self) -> None:
        first = Polynomial({2: 5, 1: 4, 0: 2})
        second = Polynomial({2: 2, 1: 1, 0: 3})

        expected = Polynomial({2: 3, 1: 3, 0: -1})

        self.assertEqual(first - second, expected)

    def test_multiplication(self) -> None:
        first = Polynomial({1: 1, 0: 2})
        second = Polynomial({1: 1, 0: 3})

        expected = Polynomial({2: 1, 1: 5, 0: 6})

        self.assertEqual(first * second, expected)

    def test_power(self) -> None:
        polynomial = Polynomial({1: 1, 0: 2})

        self.assertEqual(
            polynomial ** 2,
            Polynomial({2: 1, 1: 4, 0: 4}),
        )

    def test_evaluation(self) -> None:
        polynomial = Polynomial({2: 2, 1: 3, 0: 1})

        self.assertEqual(polynomial.evaluate(2), 15)

    def test_derivative(self) -> None:
        polynomial = Polynomial({3: 2, 1: 4, 0: 7})

        self.assertEqual(
            polynomial.derivative(),
            Polynomial({2: 6, 0: 4}),
        )

    def test_integral(self) -> None:
        polynomial = Polynomial({2: 6, 0: 4})

        self.assertEqual(
            polynomial.integral(),
            Polynomial({3: 2, 1: 4}),
        )

    def test_parser(self) -> None:
        expression = "(x + 2)*(x - 3)"

        self.assertEqual(
            parse_polynomial(expression),
            Polynomial({2: 1, 1: -1, 0: -6}),
        )

    def test_parser_precedence(self) -> None:
        self.assertEqual(
            parse_polynomial("2*x + 3*x^2"),
            Polynomial({2: 3, 1: 2}),
        )

    def test_parentheses(self) -> None:
        self.assertEqual(
            parse_polynomial("2*(x + 3)"),
            Polynomial({1: 2, 0: 6}),
        )

    def test_division(self) -> None:
        dividend = Polynomial({3: 1, 2: -6, 1: 11, 0: -6})
        divisor = Polynomial({1: 1, 0: -1})

        quotient, remainder = dividend.divide_with_remainder(divisor)

        self.assertEqual(
            quotient,
            Polynomial({2: 1, 1: -5, 0: 6}),
        )
        self.assertTrue(remainder.is_zero())

    def test_remainder_theorem(self) -> None:
        polynomial = Polynomial({2: 1, 1: -5, 0: 6})

        self.assertEqual(remainder_theorem(polynomial, 2), 0)
        self.assertTrue(factor_theorem(polynomial, 2))

    def test_factorization_identity(self) -> None:
        original = Polynomial({2: 1, 1: 5, 0: 6})
        factors = (
            Polynomial({1: 1, 0: 2})
            * Polynomial({1: 1, 0: 3})
        )

        self.assertEqual(original, factors)

    def test_zero_polynomial(self) -> None:
        polynomial = Polynomial({2: 1, 0: -1}) - Polynomial({2: 1, 0: -1})

        self.assertTrue(polynomial.is_zero())
        self.assertEqual(polynomial.degree(), -1)

    def test_division_by_zero(self) -> None:
        with self.assertRaises(ZeroDivisionError):
            Polynomial({1: 1}).divide_with_remainder(
                Polynomial.constant(0)
            )

    def test_negative_exponent_rejected(self) -> None:
        with self.assertRaises(ValueError):
            Polynomial({-1: 3})

    def test_invalid_variable_rejected(self) -> None:
        with self.assertRaises(ValueError):
            parse_polynomial("x + y")

    def test_invalid_character_rejected(self) -> None:
        with self.assertRaises(ValueError):
            parse_polynomial("x + $")

    def test_non_constant_division_rejected(self) -> None:
        with self.assertRaises(ValueError):
            parse_polynomial("x/x")


def run_tests() -> None:
    print("\n" + "=" * 78)
    print("23. AUTOMATED TESTS")
    print("=" * 78)

    suite = unittest.defaultTestLoader.loadTestsFromTestCase(PolynomialTests)

    runner = unittest.TextTestRunner(
        verbosity=1,
        stream=None,
    )

    result = runner.run(suite)

    print(
        f"\nTests run: {result.testsRun}"
    )
    print(
        f"Failures: {len(result.failures)}"
    )
    print(
        f"Errors: {len(result.errors)}"
    )


# ============================================================================
# SECTION 24: PRACTICE PROBLEMS
# ============================================================================

def practice_problems() -> None:
    print("\n" + "=" * 78)
    print("24. PRACTICE PROBLEMS WITH COMPUTED ANSWERS")
    print("=" * 78)

    problems = [
        (
            "Combine like terms",
            "4*x + 7*x - 3",
        ),
        (
            "Expand",
            "(x + 2)*(x + 5)",
        ),
        (
            "Expand a square",
            "(x - 4)^2",
        ),
        (
            "Difference of squares",
            "(x + 7)*(x - 7)",
        ),
        (
            "Cubic product",
            "(x + 1)*(x^2 - x + 1)",
        ),
        (
            "Nested expression",
            "2*(x + 3)^2 - (x - 1)",
        ),
    ]

    for description, expression in problems:
        answer = parse_polynomial(expression)
        print(f"{description:25} | {expression:35} = {answer}")


# ============================================================================
# SECTION 25: INTERACTIVE MODE
# ============================================================================

def interactive_mode() -> None:
    print("\n" + "=" * 78)
    print("25. INTERACTIVE POLYNOMIAL CALCULATOR")
    print("=" * 78)

    print(
        """
Enter a polynomial expression using:
    x
    numbers
    +  -  *  /  ^
    parentheses

Examples:
    x^2 + 5*x + 6
    (x + 2)*(x - 3)
    2*(x - 4)^2

Type 'quit' to leave the interactive mode.
"""
    )

    while True:
        try:
            expression = input("\nExpression: ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if expression.lower() in {"quit", "exit", "q"}:
            break

        if not expression:
            print("Please enter an expression.")
            continue

        try:
            polynomial = parse_polynomial(expression)

            print("Standard form:", polynomial)
            print("Degree:", polynomial.degree())
            print("Leading coefficient:", polynomial.leading_coefficient())

            value_text = input(
                "Optional value for x (press Enter to skip): "
            ).strip()

            if value_text:
                try:
                    value = Fraction(value_text)
                    print(
                        f"Value at x = {format_fraction(value)}:",
                        polynomial.evaluate(value),
                    )
                except (ValueError, ZeroDivisionError) as error:
                    print("Invalid value:", error)

        except (ValueError, ZeroDivisionError) as error:
            print("Expression error:", error)


# ============================================================================
# SECTION 26: MAIN PROGRAM
# ============================================================================

def main() -> None:
    print("=" * 78)
    print("ALGEBRAIC EXPRESSIONS: POLYNOMIALS, MONOMIALS, FACTORIZATION, EXPANSION")
    print("=" * 78)

    explain_fundamentals()
    demonstrate_classification()
    demonstrate_polynomial_basics()
    demonstrate_addition_and_subtraction()
    demonstrate_multiplication()
    demonstrate_special_multiplication()
    demonstrate_evaluation()
    demonstrate_parser()
    demonstrate_factorization()
    demonstrate_cubic_identities()
    demonstrate_polynomial_division()
    demonstrate_theorems()
    demonstrate_derivative_and_integral()
    demonstrate_exact_arithmetic()
    demonstrate_edge_cases()
    demonstrate_common_mistakes()
    demonstrate_performance_considerations()
    demonstrate_safe_parsing()
    demonstrate_comparisons()
    worked_examples()
    demonstrate_validation()
    run_tests()
    practice_problems()

    print("\n" + "=" * 78)
    print("INTERACTIVE MODE")
    print("=" * 78)
    print(
        "The interactive calculator is disabled by default so the study script "
        "can run non-interactively."
    )

    # To use the calculator manually, uncomment the following line:
    # interactive_mode()


if __name__ == "__main__":
    main()
