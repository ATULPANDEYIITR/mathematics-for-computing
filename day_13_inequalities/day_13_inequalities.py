"""
Inequalities: Linear, Quadratic, Absolute-Value Inequalities, and Intervals

A self-contained study script progressing from elementary interval notation
through systematic solution methods, algebraic reasoning, graphs, edge cases,
comparisons, validation, and advanced implementation techniques.

The script uses only Python's standard library.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from math import isclose, sqrt
from typing import Iterable, Optional, Sequence


# ============================================================================
# 1. FOUNDATIONS
# ============================================================================

def section(title: str) -> None:
    """Print a readable section heading."""
    print("\n" + "=" * 78)
    print(title)
    print("=" * 78)


def explain_comparison_symbols() -> None:
    """
    Demonstrate the basic comparison relations.

    <   less than
    >   greater than
    <=  less than or equal to
    >=  greater than or equal to
    =   equal to

    An inequality usually describes a SET of values rather than one value.
    """
    section("1. Comparison relations and the meaning of an inequality")

    a = 3
    b = 7

    print(f"{a} < {b}  -> {a < b}")
    print(f"{a} > {b}  -> {a > b}")
    print(f"{a} <= {b} -> {a <= b}")
    print(f"{a} >= {b} -> {a >= b}")
    print(f"{a} == {b} -> {a == b}")

    print("\nExample:")
    print("x > 3 means every real number greater than 3 is a solution.")
    print("x >= 3 means every real number greater than or equal to 3 is a solution.")

    # A set of solutions is commonly represented with interval notation.
    print("\nExamples of interval notation:")
    print("(3, infinity) means x > 3")
    print("[3, infinity) means x >= 3")
    print("(-infinity, 3) means x < 3")
    print("(-infinity, 3] means x <= 3")


# ============================================================================
# 2. INTERVAL REPRESENTATION
# ============================================================================

@dataclass(frozen=True)
class Interval:
    """
    Represent one real-number interval.

    left/right:
        Finite endpoints are represented by numbers.
        None represents negative infinity on the left or positive infinity
        on the right.

    left_closed/right_closed:
        Whether the finite endpoint is included.

    Examples:
        Interval(1, 5, False, False) -> (1, 5)
        Interval(1, 5, True, False)  -> [1, 5)
        Interval(None, 5, False, True) -> (-inf, 5]
        Interval(5, None, True, False) -> [5, inf)
    """

    left: Optional[float]
    right: Optional[float]
    left_closed: bool = False
    right_closed: bool = False

    def __post_init__(self) -> None:
        if self.left is not None and self.right is not None:
            if self.left > self.right:
                raise ValueError("Left endpoint cannot exceed right endpoint.")
            if self.left == self.right and not (
                self.left_closed and self.right_closed
            ):
                raise ValueError(
                    "A zero-length interval must include its single endpoint "
                    "on both sides."
                )

        if self.left is None and self.left_closed:
            raise ValueError("Negative infinity cannot be included.")

        if self.right is None and self.right_closed:
            raise ValueError("Positive infinity cannot be included.")

    def contains(self, x: float) -> bool:
        """Return True when x belongs to the interval."""
        left_ok = True
        right_ok = True

        if self.left is not None:
            left_ok = x >= self.left if self.left_closed else x > self.left

        if self.right is not None:
            right_ok = x <= self.right if self.right_closed else x < self.right

        return left_ok and right_ok

    def notation(self) -> str:
        """Return conventional interval notation."""
        left_symbol = "[" if self.left_closed else "("
        right_symbol = "]" if self.right_closed else ")"

        left_text = "-∞" if self.left is None else str(self.left)
        right_text = "∞" if self.right is None else str(self.right)

        return f"{left_symbol}{left_text}, {right_text}{right_symbol}"

    def __str__(self) -> str:
        return self.notation()


def interval_examples() -> None:
    section("2. Intervals and interval notation")

    examples = [
        Interval(2, 8),
        Interval(2, 8, True, False),
        Interval(2, 8, False, True),
        Interval(2, 8, True, True),
        Interval(None, 8, False, True),
        Interval(2, None, True, False),
    ]

    for interval in examples:
        print(interval)

    test_interval = Interval(2, 8, True, False)
    print("\nMembership tests for [2, 8):")
    for value in [1, 2, 5, 7.999, 8, 9]:
        print(f"{value:>6} -> {test_interval.contains(value)}")

    print("\nImportant distinction:")
    print("(2, 8) excludes both endpoints.")
    print("[2, 8] includes both endpoints.")
    print("[2, 8) includes 2 but excludes 8.")
    print("(2, 8] excludes 2 but includes 8.")


# ============================================================================
# 3. LINEAR INEQUALITIES
# ============================================================================

def solve_linear_inequality(
    coefficient: Fraction,
    constant: Fraction,
    relation: str,
) -> tuple[str, Fraction]:
    """
    Solve:

        coefficient * x + constant relation 0

    for x.

    The sign of the coefficient determines whether the inequality direction
    remains unchanged or must be reversed.

    Returns:
        (solution_relation, boundary_value)

    Examples:
        2x - 6 > 0 -> x > 3
        -2x + 6 > 0 -> x < 3
    """
    if relation not in {"<", "<=", ">", ">="}:
        raise ValueError("Relation must be <, <=, >, or >=.")

    if coefficient == 0:
        # The expression is simply constant.
        truth = {
            "<": constant < 0,
            "<=": constant <= 0,
            ">": constant > 0,
            ">=": constant >= 0,
        }[relation]

        return ("all real numbers" if truth else "no real solution", Fraction(0))

    boundary = -constant / coefficient

    if coefficient > 0:
        return relation, boundary

    reversed_relation = {
        "<": ">",
        "<=": ">=",
        ">": "<",
        ">=": "<=",
    }[relation]

    return reversed_relation, boundary


def print_linear_solution(
    coefficient: Fraction,
    constant: Fraction,
    relation: str,
) -> None:
    solution_relation, boundary = solve_linear_inequality(
        coefficient,
        constant,
        relation,
    )

    print(
        f"{coefficient}x + ({constant}) {relation} 0"
        f"  ->  x {solution_relation} {boundary}"
    )


def linear_inequality_examples() -> None:
    section("3. Linear inequalities")

    print("Example 1: 2x - 6 > 0")
    print_linear_solution(Fraction(2), Fraction(-6), ">")

    print("\nExample 2: -3x + 12 >= 0")
    print_linear_solution(Fraction(-3), Fraction(12), ">=")

    print("\nExample 3: 5x + 10 < 0")
    print_linear_solution(Fraction(5), Fraction(10), "<")

    print("\nThe critical rule:")
    print(
        "When multiplying or dividing both sides by a NEGATIVE number, "
        "reverse the inequality symbol."
    )

    # Demonstrate the rule numerically.
    x = Fraction(4)
    print("\nWhy reversal is necessary:")
    print("-2x < -6")
    print("Dividing by -2 gives x > 3, not x < 3.")
    print(f"At x = {x}, the original inequality is {(-2 * x) < -6}.")


# ============================================================================
# 4. COMPOUND LINEAR INEQUALITIES
# ============================================================================

def solve_between(
    lower: Fraction,
    upper: Fraction,
    lower_closed: bool = False,
    upper_closed: bool = False,
) -> Interval:
    """Create an interval for a compound inequality."""
    return Interval(
        float(lower),
        float(upper),
        lower_closed,
        upper_closed,
    )


def compound_linear_examples() -> None:
    section("4. Compound linear inequalities")

    print("Example: 2 < x + 1 <= 7")
    print("Subtracting 1 from every part gives:")
    print("1 < x <= 6")
    print("Interval:", solve_between(Fraction(1), Fraction(6), False, True))

    print("\nExample: -5 <= 2x - 1 < 7")
    print("Add 1:")
    print("-4 <= 2x < 8")
    print("Divide by 2:")
    print("-2 <= x < 4")
    print("Interval:", solve_between(Fraction(-2), Fraction(4), True, False))

    print("\nThe same operation must be applied to every part of a compound inequality.")


# ============================================================================
# 5. LINEAR INEQUALITIES WITH FRACTIONS
# ============================================================================

def fraction_inequality_example() -> None:
    section("5. Linear inequalities with fractions")

    print("Example: x/3 - 2/5 >= 1/5")
    print("Add 2/5:")
    print("x/3 >= 3/5")
    print("Multiply by 3:")
    print("x >= 9/5")

    exact_value = Fraction(9, 5)
    print("Exact boundary:", exact_value)
    print("Decimal boundary:", float(exact_value))

    print("\nFractions are retained exactly to avoid unnecessary floating-point error.")


# ============================================================================
# 6. SPECIAL LINEAR CASES
# ============================================================================

def special_linear_cases() -> None:
    section("6. Special and degenerate linear inequalities")

    cases = [
        (Fraction(0), Fraction(5), ">"),
        (Fraction(0), Fraction(-5), ">"),
        (Fraction(0), Fraction(5), "<="),
        (Fraction(0), Fraction(-5), "<="),
    ]

    for coefficient, constant, relation in cases:
        result, boundary = solve_linear_inequality(
            coefficient,
            constant,
            relation,
        )
        print(f"0x + {constant} {relation} 0 -> {result}")

    print("\nInterpretation:")
    print("0x + 5 > 0 is always true, so every real number is a solution.")
    print("0x + (-5) > 0 is always false, so there is no solution.")


# ============================================================================
# 7. QUADRATIC FUNCTIONS AND INEQUALITIES
# ============================================================================

@dataclass(frozen=True)
class Quadratic:
    """Represent ax² + bx + c."""

    a: Fraction
    b: Fraction
    c: Fraction

    def __post_init__(self) -> None:
        if self.a == 0:
            raise ValueError("A quadratic requires a nonzero coefficient a.")

    def evaluate(self, x: Fraction | float) -> Fraction | float:
        return self.a * x * x + self.b * x + self.c

    def discriminant(self) -> Fraction:
        return self.b * self.b - 4 * self.a * self.c

    def roots(self) -> list[float]:
        """
        Return real roots.

        A quadratic inequality can be solved without explicitly calculating
        roots in some cases, but roots are the critical points of the sign
        analysis method.
        """
        d = self.discriminant()

        if d < 0:
            return []

        if d == 0:
            return [float(-self.b / (2 * self.a))]

        sqrt_d = sqrt(float(d))
        denominator = 2 * float(self.a)

        return [
            (-float(self.b) - sqrt_d) / denominator,
            (-float(self.b) + sqrt_d) / denominator,
        ]


def sign_at(value: float, tolerance: float = 1e-12) -> int:
    """Return -1 for negative, 0 for approximately zero, +1 for positive."""
    if abs(value) <= tolerance:
        return 0
    return 1 if value > 0 else -1


def quadratic_sign_chart(quadratic: Quadratic) -> None:
    """
    Display signs between ordered real roots.

    For a quadratic with two distinct roots, the sign is constant on each
    interval between roots. A single test point is sufficient for each region.
    """
    roots = sorted(set(quadratic.roots()))

    print("Quadratic:", quadratic)
    print("Real critical points:", roots)

    if not roots:
        test = 0.0
        sign = sign_at(float(quadratic.evaluate(test)))
        description = "positive" if sign > 0 else "negative"
        print(f"No real roots. The quadratic is always {description}.")
        return

    if len(roots) == 1:
        root = roots[0]
        left_test = root - 1
        right_test = root + 1

        print(f"(-∞, {root}) -> sign {sign_at(float(quadratic.evaluate(left_test)))}")
        print(f"x = {root} -> sign 0")
        print(f"({root}, ∞) -> sign {sign_at(float(quadratic.evaluate(right_test)))}")
        return

    left, right = roots
    test_points = [
        left - 1,
        (left + right) / 2,
        right + 1,
    ]

    intervals = [
        f"(-∞, {left})",
        f"({left}, {right})",
        f"({right}, ∞)",
    ]

    for interval, point in zip(intervals, test_points):
        print(
            f"{interval}: test x={point:g}, "
            f"sign={sign_at(float(quadratic.evaluate(point)))}"
        )


def solve_quadratic_inequality(
    quadratic: Quadratic,
    relation: str,
) -> list[Interval]:
    """
    Solve a quadratic inequality over the real numbers.

    The method is based on:
      1. Finding real roots.
      2. Dividing the number line at those roots.
      3. Testing the sign on each region.
      4. Including roots only for <= or >=.

    The returned list may contain zero, one, or two intervals.
    """
    if relation not in {"<", "<=", ">", ">="}:
        raise ValueError("Relation must be <, <=, >, or >=.")

    d = quadratic.discriminant()

    # No real roots: sign never changes.
    if d < 0:
        value = float(quadratic.evaluate(0))
        positive = value > 0

        satisfies = {
            "<": not positive,
            "<=": not positive,
            ">": positive,
            ">=": positive,
        }[relation]

        return [Interval(None, None)] if satisfies else []

    roots = sorted(quadratic.roots())

    # One repeated root.
    if len(roots) == 1:
        r = roots[0]
        value_away = float(quadratic.evaluate(r + 1))
        positive = value_away > 0

        if relation in {">", ">="}:
            if positive:
                if relation == ">":
                    return [
                        Interval(None, r, False, False),
                        Interval(r, None, False, False),
                    ]
                return [
                    Interval(None, r, False, True),
                    Interval(r, None, True, False),
                ]

            if relation == ">=":
                return [Interval(r, r, True, True)]

            return []

        if positive:
            if relation == "<":
                return []
            return [Interval(r, r, True, True)]

        if relation == "<":
            return [
                Interval(None, r, False, False),
                Interval(r, None, False, False),
            ]

        return [
            Interval(None, r, False, True),
            Interval(r, None, True, False),
        ]

    left, right = roots

    # Determine the sign in each open region.
    left_sign = sign_at(float(quadratic.evaluate(left - 1)))
    middle_sign = sign_at(float(quadratic.evaluate((left + right) / 2)))
    right_sign = sign_at(float(quadratic.evaluate(right + 1)))

    want_positive = relation in {">", ">="}
    include_roots = relation in {"<=", ">="}

    intervals: list[Interval] = []

    if (left_sign > 0) == want_positive:
        intervals.append(Interval(None, left, False, include_roots))

    if (middle_sign > 0) == want_positive:
        intervals.append(Interval(left, right, include_roots, include_roots))

    if (right_sign > 0) == want_positive:
        intervals.append(Interval(right, None, include_roots, False))

    return intervals


def format_intervals(intervals: Sequence[Interval]) -> str:
    """Format a list of intervals as a union."""
    if not intervals:
        return "∅"
    return " ∪ ".join(interval.notation() for interval in intervals)


def quadratic_examples() -> None:
    section("7. Quadratic inequalities")

    examples = [
        (
            Quadratic(Fraction(1), Fraction(-5), Fraction(6)),
            ">=",
        ),
        (
            Quadratic(Fraction(1), Fraction(-5), Fraction(6)),
            "<",
        ),
        (
            Quadratic(Fraction(-1), Fraction(5), Fraction(-6)),
            ">",
        ),
    ]

    for quadratic, relation in examples:
        print(
            f"\nSolve: {quadratic.a}x² + {quadratic.b}x + "
            f"{quadratic.c} {relation} 0"
        )
        print("Discriminant:", quadratic.discriminant())
        print("Roots:", quadratic.roots())
        solution = solve_quadratic_inequality(quadratic, relation)
        print("Solution:", format_intervals(solution))

    print("\nSign-chart demonstration:")
    quadratic_sign_chart(Quadratic(Fraction(1), Fraction(-5), Fraction(6)))


# ============================================================================
# 8. QUADRATIC INEQUALITY STRATEGIES
# ============================================================================

def compare_quadratic_methods() -> None:
    section("8. Comparing methods for quadratic inequalities")

    print("Method 1: Factoring")
    print("(x - 2)(x - 3) > 0")
    print("Critical points: 2 and 3")
    print("A product is positive when both factors have the same sign.")
    print("Solution: (-∞, 2) ∪ (3, ∞)")

    print("\nMethod 2: Quadratic formula")
    print("For ax² + bx + c = 0:")
    print("x = (-b ± √(b² - 4ac)) / (2a)")
    print("The roots become the critical points of the inequality.")

    print("\nMethod 3: Vertex and discriminant")
    print("Useful when factoring is inconvenient.")
    print("The discriminant tells whether real roots exist.")
    print("The leading coefficient determines the end behavior.")

    print("\nImportant:")
    print("Solving f(x) = 0 only finds boundary points.")
    print("An inequality requires determining where f(x) is positive or negative.")


# ============================================================================
# 9. QUADRATIC EDGE CASES
# ============================================================================

def quadratic_edge_cases() -> None:
    section("9. Quadratic edge cases")

    cases = [
        ("No real roots, always positive", Quadratic(Fraction(1), 0, Fraction(1))),
        ("No real roots, always negative", Quadratic(Fraction(-1), 0, Fraction(-1))),
        ("Repeated root", Quadratic(Fraction(1), Fraction(-4), Fraction(4))),
    ]

    for name, quadratic in cases:
        print(f"\n{name}")
        print("Quadratic:", quadratic)
        print("Discriminant:", quadratic.discriminant())
        print("Roots:", quadratic.roots())

        for relation in [">", ">=", "<", "<="]:
            result = solve_quadratic_inequality(quadratic, relation)
            print(
                f"  {relation} 0 -> {format_intervals(result)}"
            )


# ============================================================================
# 10. ABSOLUTE VALUE
# ============================================================================

def absolute_value_definition(x: float) -> float:
    """
    |x| is distance from x to zero.

    Algebraically:
        |x| = x       when x >= 0
        |x| = -x      when x < 0
    """
    return x if x >= 0 else -x


def demonstrate_absolute_value() -> None:
    section("10. Absolute value fundamentals")

    values = [-8, -2.5, 0, 3, 9]
    for value in values:
        print(f"|{value}| = {absolute_value_definition(value)}")

    print("\nGeometric interpretation:")
    print("|x - a| represents the distance between x and a on the number line.")
    print("|x - a| < r means x is within distance r of a.")
    print("|x - a| > r means x is farther than r from a.")


# ============================================================================
# 11. ABSOLUTE-VALUE INEQUALITY RULES
# ============================================================================

def solve_absolute_value_inequality(
    center: Fraction,
    radius: Fraction,
    relation: str,
) -> list[Interval]:
    """
    Solve |x - center| relation radius for real x.

    For radius >= 0:

        |x-a| < r   -> a-r < x < a+r
        |x-a| <= r  -> a-r <= x <= a+r
        |x-a| > r   -> x < a-r OR x > a+r
        |x-a| >= r  -> x <= a-r OR x >= a+r

    Negative radius cases are handled separately because |x-a| can never
    be negative.
    """
    if relation not in {"<", "<=", ">", ">="}:
        raise ValueError("Invalid inequality relation.")

    a = float(center)
    r = float(radius)

    if r < 0:
        if relation in {"<", "<="}:
            return []
        return [Interval(None, None)]

    left = a - r
    right = a + r

    if relation == "<":
        return [Interval(left, right, False, False)]

    if relation == "<=":
        return [Interval(left, right, True, True)]

    if relation == ">":
        return [
            Interval(None, left, False, False),
            Interval(right, None, False, False),
        ]

    return [
        Interval(None, left, False, True),
        Interval(right, None, True, False),
    ]


def absolute_value_inequality_examples() -> None:
    section("11. Absolute-value inequalities")

    examples = [
        (Fraction(2), Fraction(3), "<"),
        (Fraction(2), Fraction(3), "<="),
        (Fraction(2), Fraction(3), ">"),
        (Fraction(2), Fraction(3), ">="),
        (Fraction(2), Fraction(-1), "<"),
        (Fraction(2), Fraction(-1), ">"),
    ]

    for center, radius, relation in examples:
        solution = solve_absolute_value_inequality(
            center,
            radius,
            relation,
        )
        print(
            f"|x - {center}| {relation} {radius} "
            f"-> {format_intervals(solution)}"
        )


# ============================================================================
# 12. ABSOLUTE-VALUE EQUATIONS VERSUS INEQUALITIES
# ============================================================================

def absolute_value_equation_examples() -> None:
    section("12. Absolute-value equations versus inequalities")

    print("Equation:")
    print("|x - 4| = 3")
    print("Distance from 4 must equal 3.")
    print("x - 4 = 3 OR x - 4 = -3")
    print("x = 7 OR x = 1")

    print("\nInequality:")
    print("|x - 4| < 3")
    print("Every point whose distance from 4 is less than 3 works.")
    print("1 < x < 7")

    print("\nAnother inequality:")
    print("|x - 4| > 3")
    print("The solution lies outside the central interval.")
    print("x < 1 OR x > 7")


# ============================================================================
# 13. ABSOLUTE VALUE WITH A LINEAR EXPRESSION
# ============================================================================

def solve_absolute_linear_example() -> None:
    section("13. Absolute value containing a linear expression")

    print("Example: |2x - 6| <= 4")
    print("Convert to a compound inequality:")
    print("-4 <= 2x - 6 <= 4")
    print("Add 6:")
    print("2 <= 2x <= 10")
    print("Divide by 2:")
    print("1 <= x <= 5")
    print("Solution: [1, 5]")

    print("\nExample: |3x + 2| > 8")
    print("Split into two branches:")
    print("3x + 2 > 8 OR 3x + 2 < -8")
    print("x > 2 OR x < -10/3")
    print("Solution: (-∞, -10/3) ∪ (2, ∞)")


# ============================================================================
# 14. WHEN THE ABSOLUTE-VALUE THRESHOLD IS ZERO
# ============================================================================

def absolute_zero_radius_cases() -> None:
    section("14. Absolute-value edge case: radius zero")

    print("|x - 5| < 0 -> no solution")
    print("|x - 5| <= 0 -> x = 5")
    print("|x - 5| > 0 -> x != 5")
    print("|x - 5| >= 0 -> every real number")

    print("\nThe reason is that absolute value is always nonnegative.")


# ============================================================================
# 15. INTERSECTION AND UNION
# ============================================================================

def intersection_of_intervals(
    first: Interval,
    second: Interval,
) -> Optional[Interval]:
    """Return the intersection of two intervals when it is a single interval."""

    if first.left is None:
        left = second.left
        left_closed = second.left_closed
    elif second.left is None:
        left = first.left
        left_closed = first.left_closed
    else:
        if first.left > second.left:
            left = first.left
            left_closed = first.left_closed
        elif second.left > first.left:
            left = second.left
            left_closed = second.left_closed
        else:
            left = first.left
            left_closed = first.left_closed and second.left_closed

    if first.right is None:
        right = second.right
        right_closed = second.right_closed
    elif second.right is None:
        right = first.right
        right_closed = first.right_closed
    else:
        if first.right < second.right:
            right = first.right
            right_closed = first.right_closed
        elif second.right < first.right:
            right = second.right
            right_closed = second.right_closed
        else:
            right = first.right
            right_closed = first.right_closed and second.right_closed

    if left is not None and right is not None:
        if left > right:
            return None
        if left == right and not (left_closed and right_closed):
            return None

    return Interval(left, right, left_closed, right_closed)


def interval_operations_demo() -> None:
    section("15. Intersections and unions")

    first = Interval(1, 7, True, False)
    second = Interval(5, 10, False, True)

    print("A =", first)
    print("B =", second)
    print("A ∩ B =", intersection_of_intervals(first, second))

    print("\nUnion concept:")
    print("[1, 4) ∪ [4, 8] can be combined because 4 is included by the second set.")
    print("[1, 4) ∪ (4, 8] cannot be represented by one continuous interval.")


# ============================================================================
# 16. SOLUTION SET VALIDATION
# ============================================================================

def validate_solution_set(
    predicate,
    candidate_points: Iterable[float],
) -> None:
    """
    Evaluate a predicate on sample points.

    Testing cannot prove a continuous inequality solution by itself, but it is
    useful for checking algebra and catching implementation mistakes.
    """
    for x in candidate_points:
        print(f"x={x:>7}: {predicate(x)}")


def validation_examples() -> None:
    section("16. Validating inequality solutions")

    print("Check x² - 5x + 6 > 0.")
    predicate = lambda x: x * x - 5 * x + 6 > 0

    validate_solution_set(
        predicate,
        [-2, 0, 1.9, 2, 2.5, 3, 4, 10],
    )

    print("\nExpected solution:")
    print("(-∞, 2) ∪ (3, ∞)")


# ============================================================================
# 17. NUMBER-LINE VISUALIZATION IN TEXT
# ============================================================================

def text_number_line(
    minimum: int,
    maximum: int,
    predicate,
) -> None:
    """
    Produce a simple discrete approximation of a solution set.

    This is only a visualization aid. It is not a replacement for exact
    interval notation because real-number intervals contain infinitely many
    values between any two distinct points.
    """
    values = list(range(minimum, maximum + 1))

    print("Values:")
    print(" ".join(f"{value:>3}" for value in values))

    print("Set:   ")
    print(" ".join(" ● " if predicate(value) else " · " for value in values))


def number_line_examples() -> None:
    section("17. Number-line visualization")

    print("Approximation of x² - 5x + 6 > 0 over integers -3 through 7:")
    text_number_line(
        -3,
        7,
        lambda x: x * x - 5 * x + 6 > 0,
    )

    print("\nOpen endpoints matter:")
    print("An open endpoint means the boundary does not satisfy the inequality.")
    print("A closed endpoint means the boundary does satisfy the inequality.")


# ============================================================================
# 18. LINEAR INEQUALITY WITH PARAMETERS
# ============================================================================

def parameterized_linear_example() -> None:
    section("18. Parameterized linear inequalities")

    print("Consider ax > b.")
    print("If a > 0, then x > b/a.")
    print("If a < 0, then x < b/a.")
    print("If a = 0, the inequality becomes 0 > b.")

    print("\nThis demonstrates why a symbolic solution cannot simply divide by a")
    print("without considering the sign of the parameter.")


# ============================================================================
# 19. RATIONAL INEQUALITIES
# ============================================================================

def rational_inequality_sign_chart() -> None:
    section("19. Rational inequalities as an extension")

    print("Example: (x - 2)/(x + 1) > 0")
    print("Critical values:")
    print("  Numerator zero: x = 2")
    print("  Denominator zero: x = -1")
    print("\nThe denominator zero is NOT a solution and must remain excluded.")

    critical_points = [-1, 2]
    test_points = [-2, 0, 3]

    def expression(x: float) -> float:
        return (x - 2) / (x + 1)

    intervals = [
        "(-∞, -1)",
        "(-1, 2)",
        "(2, ∞)",
    ]

    for interval, point in zip(intervals, test_points):
        print(
            f"{interval}: test x={point}, "
            f"expression={expression(point):g}, "
            f"positive={expression(point) > 0}"
        )

    print("\nSolution: (-∞, -1) ∪ (2, ∞)")
    print(
        "This section illustrates the same sign-analysis principle used for "
        "quadratic inequalities."
    )


# ============================================================================
# 20. POLYNOMIAL SIGN ANALYSIS
# ============================================================================

def polynomial_sign_analysis_demo() -> None:
    section("20. General polynomial sign analysis")

    print("For a factored polynomial:")
    print("(x - 1)(x + 2)(x - 4) >= 0")
    print("\nCritical points:")
    print("-2, 1, 4")

    test_regions = [
        ("(-∞, -2)", -3),
        ("(-2, 1)", 0),
        ("(1, 4)", 2),
        ("(4, ∞)", 5),
    ]

    for name, point in test_regions:
        value = (point - 1) * (point + 2) * (point - 4)
        print(f"{name}: test point {point}, value={value}")

    print("\nThe zeros are included because the relation is >= 0.")
    print("The sign can only change at zeros of the numerator polynomial.")


# ============================================================================
# 21. COMMON ALGEBRAIC MISTAKES
# ============================================================================

def common_mistakes() -> None:
    section("21. Common mistakes")

    mistakes = [
        (
            "Forgetting to reverse the sign",
            "-2x > 8 does NOT give x > -4. Correct result: x < -4.",
        ),
        (
            "Treating an inequality like an equation",
            "x² > 9 does NOT mean only x = 3 or x = -3. "
            "Correct result: x < -3 or x > 3.",
        ),
        (
            "Including an excluded endpoint",
            "x > 4 uses an open endpoint at 4.",
        ),
        (
            "Excluding an included endpoint",
            "x >= 4 includes 4.",
        ),
        (
            "Ignoring denominator restrictions",
            "A rational expression cannot be evaluated where its denominator is zero.",
        ),
        (
            "Confusing absolute-value equation and inequality",
            "|x-a| < r gives an interval, while |x-a| = r usually gives two points.",
        ),
        (
            "Testing only one point in a quadratic inequality",
            "Different intervals separated by roots can have different signs.",
        ),
        (
            "Squaring without checking equivalence",
            "Squaring can introduce extraneous solutions when both sides are not known "
            "to be nonnegative.",
        ),
    ]

    for name, explanation in mistakes:
        print(f"\n{name}:")
        print(explanation)


# ============================================================================
# 22. SQUARING AND INEQUALITY LOGIC
# ============================================================================

def squaring_caution() -> None:
    section("22. Squaring inequalities and logical equivalence")

    print("For nonnegative quantities, squaring preserves order:")
    print("0 <= a < b  ->  a² < b²")

    print("\nBut arbitrary real numbers cannot be squared without care.")
    print("Example:")
    print("-3 < 2 is true.")
    print("After squaring: 9 < 4 is false.")

    print("\nTherefore, squaring an inequality requires understanding the signs")
    print("of both sides before claiming an equivalent transformed inequality.")


# ============================================================================
# 23. MONOTONICITY AND FUNCTION TRANSFORMATIONS
# ============================================================================

def monotonicity_demo() -> None:
    section("23. Monotonicity and transformations")

    print("If f is strictly increasing, then:")
    print("f(a) < f(b) whenever a < b.")

    print("\nIf f is strictly decreasing, then order reverses:")
    print("a < b -> f(a) > f(b).")

    print("\nFor positive quantities:")
    print("x < y and x,y > 0 -> x² < y².")
    print("x < y -> log(x) < log(y), when x,y > 0.")
    print("x < y -> exp(x) < exp(y).")

    print("\nThese properties provide a broader framework for solving inequalities.")


# ============================================================================
# 24. LINEAR PROGRAMMING CONNECTION
# ============================================================================

def linear_constraints_demo() -> None:
    section("24. Systems of linear inequalities")

    print("A system combines multiple constraints.")
    print("Example:")
    print("x >= 0")
    print("y >= 0")
    print("x + y <= 10")
    print("2x + y <= 14")

    points = [
        (0, 0),
        (5, 5),
        (7, 0),
        (4, 6),
        (8, 3),
    ]

    def feasible(x: float, y: float) -> bool:
        return (
            x >= 0
            and y >= 0
            and x + y <= 10
            and 2 * x + y <= 14
        )

    print("\nTesting candidate points:")
    for x, y in points:
        print(f"({x}, {y}) -> feasible={feasible(x, y)}")

    print(
        "\nA system of inequalities generally describes a region rather than "
        "a single point."
    )


# ============================================================================
# 25. BUSINESS APPLICATION
# ============================================================================

def business_application() -> None:
    section("25. Real-world application: break-even constraints")

    print("Suppose a business has:")
    print("Revenue = 80x")
    print("Cost = 50x + 900")
    print("Profit = Revenue - Cost")

    print("\nProfit >= 0:")
    print("80x - (50x + 900) >= 0")
    print("30x - 900 >= 0")
    print("x >= 30")

    print("\nInterpretation:")
    print("At least 30 units must be sold to avoid a loss.")


# ============================================================================
# 26. PHYSICS APPLICATION
# ============================================================================

def physics_application() -> None:
    section("26. Real-world application: physical bounds")

    print("Suppose a measurement x must remain within 0.05 units of 10.")
    print("The requirement is:")
    print("|x - 10| <= 0.05")

    solution = solve_absolute_value_inequality(
        Fraction(10),
        Fraction(5, 100),
        "<=",
    )

    print("Solution:", format_intervals(solution))
    print("This represents an acceptable tolerance interval.")


# ============================================================================
# 27. TEMPERATURE APPLICATION
# ============================================================================

def temperature_application() -> None:
    section("27. Real-world application: temperature tolerance")

    print("A process requires temperature T to remain between 18°C and 24°C.")
    print("The compound inequality is:")
    print("18 <= T <= 24")
    print("Interval notation: [18, 24]")

    print("\nIf the requirement is expressed as a tolerance around 21°C:")
    print("|T - 21| <= 3")
    print("The equivalent interval is [18, 24].")


# ============================================================================
# 28. INCOME TAX STYLE THRESHOLD
# ============================================================================

def threshold_application() -> None:
    section("28. Real-world application: thresholds")

    print("A service provides a discount when spending s satisfies s >= 500.")
    print("The qualifying set is [500, ∞).")

    print("\nA promotion that applies only when spending is greater than 500:")
    print("s > 500")
    print("The qualifying set is (500, ∞).")

    print("The distinction between > and >= changes whether the boundary qualifies.")


# ============================================================================
# 29. EXACT ARITHMETIC
# ============================================================================

def exact_arithmetic_demo() -> None:
    section("29. Exact arithmetic and numerical precision")

    decimal_result = 1 / 10 + 2 / 10
    exact_result = Fraction(1, 10) + Fraction(2, 10)

    print("Floating-point representation:", decimal_result)
    print("Exact rational representation:", exact_result)

    print("\nFor educational symbolic inequality boundaries, Fraction is useful")
    print("because it preserves rational values exactly.")


# ============================================================================
# 30. FLOATING-POINT EDGE CASES
# ============================================================================

def floating_point_demo() -> None:
    section("30. Floating-point considerations")

    value = 0.1 + 0.2

    print("0.1 + 0.2 =", value)
    print("Exact equality with 0.3:", value == 0.3)
    print(
        "Approximate equality:",
        isclose(value, 0.3, rel_tol=1e-12, abs_tol=1e-12),
    )

    print(
        "\nWhen numerical calculations determine interval boundaries, "
        "floating-point tolerance may be necessary."
    )


# ============================================================================
# 31. SOLUTION SET AS A PREDICATE
# ============================================================================

def predicate_view_demo() -> None:
    section("31. Inequalities as predicates")

    inequality = lambda x: x * x - 4 >= 0

    print("The inequality x² - 4 >= 0 can be treated as a Boolean predicate.")

    for x in [-3, -2, -1, 0, 1, 2, 3]:
        print(f"x={x}: {inequality(x)}")

    print("\nExact mathematical solution:")
    print("(-∞, -2] ∪ [2, ∞)")


# ============================================================================
# 32. FACTORIZATION AND SIGN CHANGES
# ============================================================================

def factor_sign_rule_demo() -> None:
    section("32. Factor multiplicity and sign changes")

    print("Consider:")
    print("(x - 2)^2")
    print("The root x=2 has even multiplicity.")
    print("The sign does not change when crossing x=2.")

    print("\nConsider:")
    print("(x - 2)^3")
    print("The root x=2 has odd multiplicity.")
    print("The sign changes when crossing x=2.")

    print(
        "\nFor polynomial inequalities, root multiplicity helps predict "
        "sign changes without testing every region."
    )


# ============================================================================
# 33. QUADRATIC VERTEX
# ============================================================================

def quadratic_vertex_demo() -> None:
    section("33. Quadratic vertex and geometric reasoning")

    quadratic = Quadratic(Fraction(1), Fraction(-6), Fraction(5))

    vertex_x = -quadratic.b / (2 * quadratic.a)
    vertex_y = quadratic.evaluate(vertex_x)

    print("Quadratic: x² - 6x + 5")
    print("Vertex x-coordinate:", vertex_x)
    print("Vertex y-coordinate:", vertex_y)
    print("Because a > 0, the parabola opens upward.")

    print("\nTherefore:")
    print("The quadratic is below zero between its two roots.")
    print("The quadratic is above zero outside the roots.")


# ============================================================================
# 34. DISCRIMINANT INTERPRETATION
# ============================================================================

def discriminant_demo() -> None:
    section("34. Discriminant and inequality structure")

    cases = [
        Quadratic(Fraction(1), 0, 1),
        Quadratic(Fraction(1), -2, 1),
        Quadratic(Fraction(1), 0, -4),
    ]

    for quadratic in cases:
        d = quadratic.discriminant()
        print(
            f"{quadratic}: discriminant={d}, "
            f"roots={quadratic.roots()}"
        )

    print("\nD < 0: no real roots.")
    print("D = 0: one repeated real root.")
    print("D > 0: two distinct real roots.")


# ============================================================================
# 35. ABSOLUTE VALUE AS PIECEWISE FUNCTION
# ============================================================================

def piecewise_absolute_demo() -> None:
    section("35. Absolute value as a piecewise function")

    print("|x - 3| can be written as:")
    print("3 - x, when x < 3")
    print("x - 3, when x >= 3")

    for x in [0, 2, 3, 4, 7]:
        piecewise = 3 - x if x < 3 else x - 3
        direct = abs(x - 3)
        print(f"x={x}: piecewise={piecewise}, abs={direct}")


# ============================================================================
# 36. INTERVAL CONVERSION
# ============================================================================

def interval_to_inequality(interval: Interval) -> str:
    """Convert common single intervals into readable inequalities."""
    if interval.left is None and interval.right is None:
        return "all real numbers"

    if interval.left is None:
        symbol = "<=" if interval.right_closed else "<"
        return f"x {symbol} {interval.right}"

    if interval.right is None:
        symbol = ">=" if interval.left_closed else ">"
        return f"x {symbol} {interval.left}"

    left_symbol = "<=" if interval.left_closed else "<"
    right_symbol = "<=" if interval.right_closed else "<"

    return f"{interval.left} {left_symbol} x {right_symbol} {interval.right}"


def interval_conversion_demo() -> None:
    section("36. Converting intervals to inequalities")

    intervals = [
        Interval(None, 4),
        Interval(None, 4, False, True),
        Interval(4, None, True, False),
        Interval(4, None, False, False),
        Interval(2, 9, True, False),
    ]

    for interval in intervals:
        print(f"{interval} -> {interval_to_inequality(interval)}")


# ============================================================================
# 37. LOGICAL CONNECTORS
# ============================================================================

def logical_connectors_demo() -> None:
    section("37. AND versus OR in inequality solutions")

    print("x > 2 AND x < 7")
    print("means x lies between 2 and 7:")
    print("(2, 7)")

    print("\nx < 2 OR x > 7")
    print("means x lies outside the central interval:")
    print("(-∞, 2) ∪ (7, ∞)")

    print("\nAbsolute-value inequalities naturally produce these two patterns:")
    print("|x-a| < r -> AND")
    print("|x-a| > r -> OR")


# ============================================================================
# 38. COMPLEMENT OF A SOLUTION SET
# ============================================================================

def complement_demo() -> None:
    section("38. Complements of intervals")

    print("The complement of x > 3 is x <= 3.")
    print("The complement of (3, ∞) is (-∞, 3].")

    print("\nThis is useful for converting:")
    print("|x-a| > r")
    print("into the complement of")
    print("|x-a| <= r")

    print("\nFor example:")
    print("|x-5| > 2")
    print("is everything outside [3, 7]:")
    print("(-∞, 3) ∪ (7, ∞)")


# ============================================================================
# 39. DE MORGAN'S LAWS
# ============================================================================

def de_morgan_demo() -> None:
    section("39. De Morgan's laws and inequality logic")

    print("NOT (A AND B) = (NOT A) OR (NOT B)")
    print("NOT (A OR B)  = (NOT A) AND (NOT B)")

    print("\nExample:")
    print("NOT (x >= 2 AND x <= 5)")
    print("means x < 2 OR x > 5.")

    print("\nThis explains why the complement of a closed interval")
    print("[2, 5] is")
    print("(-∞, 2) ∪ (5, ∞).")


# ============================================================================
# 40. ROBUST SOLVING CHECKLIST
# ============================================================================

def solving_checklist() -> None:
    section("40. General inequality-solving procedure")

    steps = [
        "Identify the type of inequality.",
        "Simplify both sides carefully.",
        "Move terms while preserving equivalence.",
        "Reverse the inequality when multiplying or dividing by a negative.",
        "For polynomial inequalities, identify critical points.",
        "For rational inequalities, include denominator restrictions.",
        "For absolute-value inequalities, use distance-based rules.",
        "Test one point in each region when sign analysis is required.",
        "Decide whether boundary points are included.",
        "Express the final set using interval notation or equivalent inequalities.",
        "Check representative values from the proposed solution and its complement.",
    ]

    for number, step in enumerate(steps, start=1):
        print(f"{number}. {step}")


# ============================================================================
# 41. INTEGRATED EXAMPLE
# ============================================================================

def integrated_example() -> None:
    section("41. Integrated example")

    print("Solve:")
    print("|x - 2| <= x + 4")

    print("\nFirst, the right-hand side must be nonnegative for the standard")
    print("absolute-value transformation to apply.")
    print("x + 4 >= 0 -> x >= -4")

    print("\nUnder that condition:")
    print("-(x + 4) <= x - 2 <= x + 4")

    print("Left inequality:")
    print("-x - 4 <= x - 2")
    print("-2 <= 2x")
    print("-1 <= x")

    print("Right inequality:")
    print("x - 2 <= x + 4")
    print("-2 <= 4")
    print("always true.")

    print("\nCombined with the required domain:")
    print("x >= -1")

    print("Solution: [-1, ∞)")


# ============================================================================
# 42. MORE COMPLEX ABSOLUTE-VALUE EXAMPLE
# ============================================================================

def advanced_absolute_example() -> None:
    section("42. Advanced absolute-value example")

    print("Solve:")
    print("|2x - 1| > |x + 3|")

    print("\nBoth sides are nonnegative, so squaring preserves equivalence:")
    print("(2x - 1)^2 > (x + 3)^2")

    print("Expand:")
    print("4x² - 4x + 1 > x² + 6x + 9")

    print("Move everything to one side:")
    print("3x² - 10x - 8 > 0")

    print("Factor:")
    print("(3x + 2)(x - 4) > 0")

    print("Critical points: -2/3 and 4")
    print("Positive outside the roots.")
    print("Solution: (-∞, -2/3) ∪ (4, ∞)")


# ============================================================================
# 43. COMPARISON TABLE AS DATA
# ============================================================================

def comparison_table() -> None:
    section("43. Comparison of major inequality types")

    rows = [
        ("Linear", "ax+b relation 0", "one boundary", "interval or ray"),
        ("Quadratic", "ax²+bx+c relation 0", "real roots", "one/two intervals"),
        ("Absolute value", "|x-a| relation r", "center ± radius", "central or exterior set"),
        ("Rational", "P(x)/Q(x) relation 0", "zeros + undefined points", "multiple intervals"),
    ]

    headers = ("Type", "Typical form", "Critical points", "Typical result")

    widths = [18, 28, 25, 32]

    print(
        "".join(
            header.ljust(width)
            for header, width in zip(headers, widths)
        )
    )
    print("-" * sum(widths))

    for row in rows:
        print(
            "".join(
                value.ljust(width)
                for value, width in zip(row, widths)
            )
        )


# ============================================================================
# 44. TESTING IMPLEMENTATIONS
# ============================================================================

def run_assertion_tests() -> None:
    section("44. Built-in implementation tests")

    # Linear inequality.
    relation, boundary = solve_linear_inequality(
        Fraction(2),
        Fraction(-6),
        ">",
    )
    assert relation == ">"
    assert boundary == Fraction(3)

    relation, boundary = solve_linear_inequality(
        Fraction(-2),
        Fraction(6),
        ">",
    )
    assert relation == "<"
    assert boundary == Fraction(3)

    # Quadratic x² - 5x + 6 > 0.
    quadratic = Quadratic(Fraction(1), Fraction(-5), Fraction(6))
    result = solve_quadratic_inequality(quadratic, ">")
    assert len(result) == 2
    assert result[0].contains(-10)
    assert result[1].contains(10)
    assert not result[0].contains(2)
    assert not result[1].contains(3)

    # Absolute value.
    result = solve_absolute_value_inequality(
        Fraction(5),
        Fraction(2),
        "<=",
    )
    assert result[0].contains(3)
    assert result[0].contains(5)
    assert result[0].contains(7)
    assert not result[0].contains(8)

    # Negative absolute-value radius.
    assert solve_absolute_value_inequality(
        Fraction(0),
        Fraction(-1),
        "<",
    ) == []

    # Interval membership.
    interval = Interval(2, 8, True, False)
    assert interval.contains(2)
    assert interval.contains(7.999)
    assert not interval.contains(8)

    print("All assertion tests passed.")


# ============================================================================
# 45. MINI PRACTICE SET WITH ANSWERS
# ============================================================================

def practice_set() -> None:
    section("45. Practice problems with programmatic answers")

    problems = [
        "1. Solve 3x - 9 >= 0.",
        "2. Solve -4x + 12 < 0.",
        "3. Solve x² - 9 <= 0.",
        "4. Solve x² - 9 > 0.",
        "5. Solve |x - 3| <= 2.",
        "6. Solve |x + 1| > 4.",
    ]

    for problem in problems:
        print(problem)

    print("\nAnswers:")

    relation, boundary = solve_linear_inequality(
        Fraction(3),
        Fraction(-9),
        ">=",
    )
    print(f"1. x {relation} {boundary}")

    relation, boundary = solve_linear_inequality(
        Fraction(-4),
        Fraction(12),
        "<",
    )
    print(f"2. x {relation} {boundary}")

    q1 = Quadratic(Fraction(1), 0, Fraction(-9))
    q2 = Quadratic(Fraction(1), 0, Fraction(-9))

    print("3.", format_intervals(solve_quadratic_inequality(q1, "<=")))
    print("4.", format_intervals(solve_quadratic_inequality(q2, ">")))

    print(
        "5.",
        format_intervals(
            solve_absolute_value_inequality(
                Fraction(3),
                Fraction(2),
                "<=",
            )
        ),
    )

    print(
        "6.",
        format_intervals(
            solve_absolute_value_inequality(
                Fraction(-1),
                Fraction(4),
                ">",
            )
        ),
    )


# ============================================================================
# 46. MAIN PROGRAM
# ============================================================================

def main() -> None:
    """
    Execute the complete educational demonstration.

    The examples are intentionally ordered from basic comparisons and
    intervals toward polynomial, absolute-value, logical, computational,
    and application-oriented reasoning.
    """
    explain_comparison_symbols()
    interval_examples()
    linear_inequality_examples()
    compound_linear_examples()
    fraction_inequality_example()
    special_linear_cases()
    quadratic_examples()
    compare_quadratic_methods()
    quadratic_edge_cases()
    demonstrate_absolute_value()
    absolute_value_inequality_examples()
    absolute_value_equation_examples()
    solve_absolute_linear_example()
    absolute_zero_radius_cases()
    interval_operations_demo()
    validation_examples()
    number_line_examples()
    parameterized_linear_example()
    rational_inequality_sign_chart()
    polynomial_sign_analysis_demo()
    common_mistakes()
    squaring_caution()
    monotonicity_demo()
    linear_constraints_demo()
    business_application()
    physics_application()
    temperature_application()
    threshold_application()
    exact_arithmetic_demo()
    floating_point_demo()
    predicate_view_demo()
    factor_sign_rule_demo()
    quadratic_vertex_demo()
    discriminant_demo()
    piecewise_absolute_demo()
    interval_conversion_demo()
    logical_connectors_demo()
    complement_demo()
    de_morgan_demo()
    solving_checklist()
    integrated_example()
    advanced_absolute_example()
    comparison_table()
    run_assertion_tests()
    practice_set()


if __name__ == "__main__":
    main()
