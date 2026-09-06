"""
LOGARITHMS: FROM FUNDAMENTALS TO ADVANCED COMPUTATIONAL APPLICATIONS
===================================================================

A self-contained study and demonstration script covering:

1. Meaning and notation of logarithms
2. Bases and domain restrictions
3. Conversion between exponential and logarithmic forms
4. Common and natural logarithms
5. Logarithmic properties and their derivations
6. Change-of-base formula
7. Solving logarithmic and exponential equations
8. Graphs and transformations
9. Inverse relationships
10. Numerical evaluation and precision
11. Logarithms in computational complexity
12. Binary logarithms and information theory
13. Numerical stability and log-domain computation
14. Log-sum-exp
15. Floating-point considerations
16. Algorithms involving logarithms
17. Edge cases and common mistakes
18. Testing and validation

Only the Python standard library is used.
"""

from __future__ import annotations

import math
import random
import statistics
import time
from dataclasses import dataclass
from typing import Callable, Iterable, List, Sequence, Tuple


# ============================================================================
# 1. BASIC DEFINITIONS
# ============================================================================

def section(title: str) -> None:
    """Print a readable section heading."""
    print("\n" + "=" * 78)
    print(title)
    print("=" * 78)


def subsection(title: str) -> None:
    print("\n" + "-" * 78)
    print(title)
    print("-" * 78)


def exponential_to_logarithmic(base: float, exponent: float, value: float) -> str:
    """
    Demonstrate:

        base ** exponent = value
        <=> log_base(value) = exponent
    """
    if base <= 0 or base == 1:
        raise ValueError("A logarithm base must be positive and different from 1.")
    if value <= 0:
        raise ValueError("A logarithm argument must be positive.")

    return f"{base:g}^{exponent:g} = {value:g}  <=>  log_{base:g}({value:g}) = {exponent:g}"


def log_value(base: float, value: float) -> float:
    """
    Compute log_base(value).

    Change of base:
        log_b(x) = ln(x) / ln(b)
    """
    if base <= 0 or base == 1:
        raise ValueError("base must be > 0 and != 1")
    if value <= 0:
        raise ValueError("logarithm argument must be > 0")

    return math.log(value) / math.log(base)


def demonstrate_basic_definition() -> None:
    subsection("Logarithmic notation")

    examples = [
        (2, 3, 8),
        (10, 3, 1000),
        (5, 2, 25),
        (10, -2, 0.01),
        (math.e, 1, math.e),
    ]

    for base, exponent, value in examples:
        print(exponential_to_logarithmic(base, exponent, value))

    print("\nInterpretation:")
    print("log_b(x) asks: 'What exponent must be applied to b to obtain x?'")
    print("The defining equation is b^y = x <=> log_b(x) = y.")


# ============================================================================
# 2. VALID BASES AND DOMAIN
# ============================================================================

def demonstrate_domain_and_base_rules() -> None:
    subsection("Domain and base restrictions")

    print("For log_b(x) to be real-valued:")
    print("  b > 0")
    print("  b != 1")
    print("  x > 0")

    valid_examples = [
        (2, 16),
        (10, 100),
        (0.5, 8),
        (math.e, 7),
    ]

    for base, value in valid_examples:
        print(f"log_{base:g}({value:g}) = {log_value(base, value):.8f}")

    invalid_examples = [
        ("base = 0", 0, 5),
        ("base = 1", 1, 5),
        ("negative base", -2, 8),
        ("argument = 0", 2, 0),
        ("negative argument", 2, -8),
    ]

    for description, base, value in invalid_examples:
        try:
            log_value(base, value)
        except ValueError as error:
            print(f"{description}: correctly rejected -> {error}")


# ============================================================================
# 3. SPECIAL LOGARITHMS
# ============================================================================

def demonstrate_common_and_natural_logs() -> None:
    subsection("Common logarithm and natural logarithm")

    print("Common logarithm: log_10(x), commonly written log(x).")
    print("Natural logarithm: log_e(x), written ln(x).")
    print(f"e = {math.e:.15f}")

    for value in [0.01, 0.1, 1, 2, 10, 100, 1000]:
        print(
            f"x={value:8g} | log10(x)={math.log10(value):12.6f}"
            f" | ln(x)={math.log(value):12.6f}"
        )


# ============================================================================
# 4. FUNDAMENTAL LOGARITHM IDENTITIES
# ============================================================================

def demonstrate_core_identities() -> None:
    subsection("Fundamental identities")

    x = 32
    print(f"log_2({x}) = {log_value(2, x)}")
    print(f"log_2(1) = {log_value(2, 1)}")
    print(f"log_2(2) = {log_value(2, 2)}")

    print("\nInverse identities:")
    y = 4.5
    print(f"2^({y}) = {2 ** y:.8f}")
    print(f"log_2(2^({y})) = {log_value(2, 2 ** y):.8f}")

    x = 13.7
    print(f"2^(log_2({x})) = {2 ** log_value(2, x):.8f}")


# ============================================================================
# 5. PRODUCT, QUOTIENT, AND POWER RULES
# ============================================================================

def demonstrate_logarithm_properties() -> None:
    subsection("Product, quotient, and power properties")

    base = 3
    x = 9
    y = 27

    product_left = log_value(base, x * y)
    product_right = log_value(base, x) + log_value(base, y)

    quotient_left = log_value(base, x / y)
    quotient_right = log_value(base, x) - log_value(base, y)

    exponent = 4
    power_left = log_value(base, x ** exponent)
    power_right = exponent * log_value(base, x)

    print("Product rule:")
    print("log_b(xy) = log_b(x) + log_b(y)")
    print(f"Left side  = {product_left:.8f}")
    print(f"Right side = {product_right:.8f}")

    print("\nQuotient rule:")
    print("log_b(x/y) = log_b(x) - log_b(y)")
    print(f"Left side  = {quotient_left:.8f}")
    print(f"Right side = {quotient_right:.8f}")

    print("\nPower rule:")
    print("log_b(x^k) = k log_b(x)")
    print(f"Left side  = {power_left:.8f}")
    print(f"Right side = {power_right:.8f}")

    print("\nImportant limitation:")
    print("log_b(x + y) != log_b(x) + log_b(y) in general.")


# ============================================================================
# 6. CHANGE OF BASE
# ============================================================================

def demonstrate_change_of_base() -> None:
    subsection("Change-of-base formula")

    print("log_b(x) = log_k(x) / log_k(b)")
    print("Python's math.log(x, base) can also evaluate a logarithm.")

    base = 7
    value = 1000

    using_natural_log = math.log(value) / math.log(base)
    using_common_log = math.log10(value) / math.log10(base)
    using_math_log = math.log(value, base)

    print(f"log_{base}({value}) using ln:       {using_natural_log:.12f}")
    print(f"log_{base}({value}) using log10:    {using_common_log:.12f}")
    print(f"log_{base}({value}) using math.log: {using_math_log:.12f}")


# ============================================================================
# 7. NUMERICAL EVALUATION
# ============================================================================

def demonstrate_python_log_functions() -> None:
    subsection("Python logarithm functions")

    values = [1, 2, 10, 100, math.e, 1024]

    for value in values:
        print(
            f"x={value:10.6g} | "
            f"ln={math.log(value):12.8f} | "
            f"log10={math.log10(value):12.8f} | "
            f"log2={math.log2(value):12.8f}"
        )

    print("\nSpecialized functions:")
    print("math.log1p(x) computes ln(1+x) accurately when x is close to zero.")
    print("math.expm1(x) computes exp(x)-1 accurately when x is close to zero.")

    x = 1e-12
    naive = math.log(1 + x)
    stable = math.log1p(x)

    print(f"math.log(1 + {x}) = {naive:.20f}")
    print(f"math.log1p({x})  = {stable:.20f}")


# ============================================================================
# 8. SOLVING EXPONENTIAL EQUATIONS
# ============================================================================

def solve_exponential_equation(base: float, right_side: float) -> float:
    """
    Solve:

        base^x = right_side

    by taking logarithms:

        x = ln(right_side) / ln(base)
    """
    if base <= 0 or base == 1:
        raise ValueError("Invalid exponential base.")
    if right_side <= 0:
        raise ValueError("The right side must be positive.")

    return math.log(right_side) / math.log(base)


def demonstrate_exponential_equations() -> None:
    subsection("Solving exponential equations")

    equations = [
        (2, 64),
        (3, 81),
        (10, 5000),
        (5, 17),
    ]

    for base, value in equations:
        solution = solve_exponential_equation(base, value)
        reconstructed = base ** solution
        print(
            f"{base}^x = {value}: x = {solution:.10f}, "
            f"verification = {reconstructed:.10f}"
        )


# ============================================================================
# 9. SOLVING SIMPLE LOGARITHMIC EQUATIONS
# ============================================================================

def solve_log_equation(base: float, argument: float) -> float:
    """
    Solve log_base(x) = argument.

    x = base^argument
    """
    if base <= 0 or base == 1:
        raise ValueError("Invalid logarithm base.")

    return base ** argument


def demonstrate_logarithmic_equations() -> None:
    subsection("Solving logarithmic equations")

    examples = [
        (2, 7),
        (10, 3.5),
        (5, -2),
        (math.e, 4),
    ]

    for base, value in examples:
        solution = solve_log_equation(base, value)
        verification = log_value(base, solution)
        print(
            f"log_{base:g}(x) = {value:g} -> "
            f"x = {solution:.10f}; verification = {verification:.10f}"
        )


# ============================================================================
# 10. SOLVING LOGARITHMIC EQUATIONS WITH BASIC ALGEBRA
# ============================================================================

def solve_linear_log_equation(
    base: float,
    coefficient: float,
    constant: float,
    target: float,
) -> float:
    """
    Solve:

        coefficient * log_base(x) + constant = target

    Rearrangement:

        log_base(x) = (target - constant) / coefficient
        x = base^((target - constant) / coefficient)
    """
    if coefficient == 0:
        raise ValueError("Coefficient cannot be zero.")

    logarithm_value = (target - constant) / coefficient
    return solve_log_equation(base, logarithm_value)


def demonstrate_linear_log_equations() -> None:
    subsection("Linear logarithmic equations")

    base = 10
    coefficient = 2
    constant = 3
    target = 7

    solution = solve_linear_log_equation(
        base, coefficient, constant, target
    )

    left_side = coefficient * math.log10(solution) + constant

    print("Equation: 2 log10(x) + 3 = 7")
    print(f"x = {solution:.10f}")
    print(f"Verification = {left_side:.10f}")


# ============================================================================
# 11. LOGARITHMIC INEQUALITIES
# ============================================================================

def demonstrate_logarithmic_inequalities() -> None:
    subsection("Monotonicity and logarithmic inequalities")

    print("If b > 1, log_b(x) is increasing.")
    print("If 0 < b < 1, log_b(x) is decreasing.")

    examples = [
        (2, 4, 16),
        (0.5, 4, 16),
    ]

    for base, x, y in examples:
        log_x = log_value(base, x)
        log_y = log_value(base, y)

        relation = "<" if log_x < log_y else ">"
        print(
            f"base={base:g}: log({x})={log_x:.4f} "
            f"{relation} log({y})={log_y:.4f}"
        )


# ============================================================================
# 12. LOGARITHMIC GRAPHS
# ============================================================================

def demonstrate_graph_concepts() -> None:
    subsection("Graph behavior")

    print("For y = log_b(x):")
    print("  Domain: (0, infinity)")
    print("  Range: (-infinity, infinity)")
    print("  Vertical asymptote: x = 0")
    print("  x-intercept: (1, 0)")
    print("  It is the inverse of y = b^x.")

    for base in [2, math.e, 10, 0.5]:
        points = [(x, log_value(base, x)) for x in [0.25, 0.5, 1, 2, 4]]
        print(f"\nBase {base:g}:")
        for x, y in points:
            print(f"  x={x:4.2f}, y={y:10.6f}")


# ============================================================================
# 13. TRANSFORMATIONS
# ============================================================================

def transformed_logarithm(
    x: float,
    base: float,
    scale: float = 1.0,
    horizontal_shift: float = 0.0,
    vertical_shift: float = 0.0,
) -> float:
    """
    Evaluate:

        y = scale * log_base(x - horizontal_shift) + vertical_shift

    Domain requires:

        x - horizontal_shift > 0
    """
    shifted_x = x - horizontal_shift

    if shifted_x <= 0:
        raise ValueError(
            "The logarithm argument must remain positive."
        )

    return scale * log_value(base, shifted_x) + vertical_shift


def demonstrate_transformations() -> None:
    subsection("Logarithmic transformations")

    base = 10
    parameters = {
        "scale": 2,
        "horizontal_shift": 3,
        "vertical_shift": -1,
    }

    print("Function:")
    print("y = 2 log10(x - 3) - 1")
    print("Domain: x > 3")

    for x in [3.1, 4, 8, 13]:
        print(
            f"x={x:5.1f}, y={transformed_logarithm(x, base, **parameters):.8f}"
        )


# ============================================================================
# 14. LOGARITHMIC DIFFERENTIATION
# ============================================================================

def numerical_derivative(
    function: Callable[[float], float],
    x: float,
    step: float = 1e-6,
) -> float:
    """Central finite-difference approximation."""
    return (function(x + step) - function(x - step)) / (2 * step)


def demonstrate_calculus_connection() -> None:
    subsection("Calculus connection")

    print("For x > 0:")
    print("d/dx ln(x) = 1/x")
    print("d/dx log_b(x) = 1 / (x ln(b))")

    x = 3.0
    numerical = numerical_derivative(math.log, x)
    exact = 1 / x

    print(f"\nAt x={x}:")
    print(f"Numerical derivative = {numerical:.10f}")
    print(f"Exact derivative     = {exact:.10f}")

    base = 10
    function = lambda value: log_value(base, value)
    numerical_base = numerical_derivative(function, x)
    exact_base = 1 / (x * math.log(base))

    print(f"\nDerivative of log10(x) at x={x}:")
    print(f"Numerical = {numerical_base:.10f}")
    print(f"Exact     = {exact_base:.10f}")


# ============================================================================
# 15. LOGARITHMIC DIFFERENTIATION OF PRODUCTS
# ============================================================================

def demonstrate_logarithmic_differentiation() -> None:
    subsection("Logarithmic differentiation")

    print("For a positive function y:")
    print("ln(y) converts multiplication into addition.")
    print("This is useful when y is a product or contains variable exponents.")

    # Example:
    # y = x^x
    # ln(y) = x ln(x)
    # Differentiating:
    # y'/y = ln(x) + 1
    # y' = x^x [ln(x) + 1]

    x = 2.0
    y = x ** x
    derivative = y * (math.log(x) + 1)

    numerical = numerical_derivative(lambda value: value ** value, x)

    print(f"For y = x^x at x={x}:")
    print(f"y = {y:.10f}")
    print(f"Analytical derivative = {derivative:.10f}")
    print(f"Numerical derivative   = {numerical:.10f}")


# ============================================================================
# 16. DECIBELS
# ============================================================================

def power_ratio_to_decibels(power_ratio: float) -> float:
    """Convert a power ratio to decibels."""
    if power_ratio <= 0:
        raise ValueError("Power ratio must be positive.")
    return 10 * math.log10(power_ratio)


def amplitude_ratio_to_decibels(amplitude_ratio: float) -> float:
    """Convert an amplitude ratio to decibels."""
    if amplitude_ratio <= 0:
        raise ValueError("Amplitude ratio must be positive.")
    return 20 * math.log10(amplitude_ratio)


def demonstrate_decibels() -> None:
    subsection("Logarithms in decibels")

    print("Power ratio: dB = 10 log10(P2/P1)")
    print("Amplitude ratio: dB = 20 log10(A2/A1)")

    for ratio in [0.1, 0.5, 1, 2, 10, 100]:
        print(
            f"ratio={ratio:6g} | "
            f"power dB={power_ratio_to_decibels(ratio):9.4f} | "
            f"amplitude dB={amplitude_ratio_to_decibels(ratio):9.4f}"
        )


# ============================================================================
# 17. pH SCALE
# ============================================================================

def ph_from_hydrogen_ion_concentration(concentration: float) -> float:
    """pH = -log10([H+])."""
    if concentration <= 0:
        raise ValueError("Hydrogen ion concentration must be positive.")
    return -math.log10(concentration)


def demonstrate_ph() -> None:
    subsection("Logarithms in the pH scale")

    concentrations = [1e-1, 1e-3, 1e-7, 1e-10, 1e-14]

    for concentration in concentrations:
        print(
            f"[H+] = {concentration:.0e} M -> "
            f"pH = {ph_from_hydrogen_ion_concentration(concentration):.2f}"
        )


# ============================================================================
# 18. RICHTER-LIKE LOGARITHMIC SCALES
# ============================================================================

def magnitude_ratio(base: float, difference: float) -> float:
    """If difference = log_base(ratio), return the ratio."""
    return base ** difference


def demonstrate_logarithmic_scales() -> None:
    subsection("Logarithmic measurement scales")

    print("If a scale difference is logarithmic, equal additive changes")
    print("correspond to multiplicative changes in the underlying quantity.")

    for difference in [0, 1, 2, 3]:
        ratio = magnitude_ratio(10, difference)
        print(f"Difference={difference} -> underlying ratio={ratio:g}")


# ============================================================================
# 19. BINARY LOGARITHMS AND INFORMATION
# ============================================================================

def demonstrate_binary_logarithms() -> None:
    subsection("Binary logarithms and information")

    print("log2(n) measures how many binary doubling levels are needed to reach n.")
    print("For powers of two, log2(n) is an integer.")

    for n in [1, 2, 4, 8, 16, 32, 64, 100, 1024]:
        print(f"n={n:5d} -> log2(n)={math.log2(n):10.6f}")

    print("\nBits needed to represent n distinct equally likely possibilities:")
    for n in [2, 4, 8, 256, 1024, 1_000_000]:
        print(f"{n:10d} possibilities -> {math.log2(n):.6f} bits")


# ============================================================================
# 20. ENTROPY
# ============================================================================

def entropy(probabilities: Sequence[float], base: float = 2.0) -> float:
    """
    Shannon entropy:

        H(X) = -sum p_i log_b(p_i)

    Zero-probability terms contribute zero by continuity.
    """
    if base <= 0 or base == 1:
        raise ValueError("Entropy logarithm base must be > 0 and != 1.")

    if not probabilities:
        raise ValueError("At least one probability is required.")

    total = sum(probabilities)
    if not math.isclose(total, 1.0, rel_tol=1e-12, abs_tol=1e-12):
        raise ValueError("Probabilities must sum to 1.")

    if any(p < 0 for p in probabilities):
        raise ValueError("Probabilities cannot be negative.")

    return -sum(
        p * log_value(base, p)
        for p in probabilities
        if p > 0
    )


def demonstrate_entropy() -> None:
    subsection("Entropy and logarithms")

    distributions = [
        [0.5, 0.5],
        [0.25, 0.25, 0.25, 0.25],
        [0.9, 0.1],
        [0.7, 0.2, 0.1],
    ]

    for probabilities in distributions:
        print(
            f"P={probabilities} -> "
            f"H2={entropy(probabilities, 2):.8f} bits"
        )


# ============================================================================
# 21. LOGARITHMS IN ALGORITHM COMPLEXITY
# ============================================================================

def binary_search_steps(sorted_values: Sequence[int], target: int) -> int:
    """Count comparisons made by binary search."""
    left = 0
    right = len(sorted_values) - 1
    comparisons = 0

    while left <= right:
        comparisons += 1
        middle = (left + right) // 2

        if sorted_values[middle] == target:
            return comparisons
        if sorted_values[middle] < target:
            left = middle + 1
        else:
            right = middle - 1

    return comparisons


def demonstrate_binary_search_complexity() -> None:
    subsection("Binary search and O(log n)")

    for size in [1, 2, 4, 8, 16, 32, 64, 128, 1024, 1_000_000]:
        theoretical = math.log2(size) if size > 0 else 0
        print(
            f"n={size:10d} | log2(n)={theoretical:12.6f}"
        )

    values = list(range(1, 33))

    for target in [1, 16, 32, 99]:
        comparisons = binary_search_steps(values, target)
        print(
            f"target={target:3d} -> comparisons={comparisons}"
        )


# ============================================================================
# 22. LOGARITHMIC GROWTH VERSUS LINEAR AND EXPONENTIAL
# ============================================================================

def demonstrate_growth_rates() -> None:
    subsection("Growth-rate comparison")

    values = [2, 4, 8, 16, 32, 64, 128, 1024, 1_000_000]

    print(
        f"{'n':>12} {'log2(n)':>15} {'n':>15} "
        f"{'n log2(n)':>18} {'2^log2(n)':>18}"
    )

    for n in values:
        log_n = math.log2(n)
        print(
            f"{n:12g} {log_n:15.6f} {n:15g} "
            f"{n * log_n:18.6f} {2 ** log_n:18.6f}"
        )

    print("\nTypical asymptotic ordering:")
    print("log n << sqrt(n) << n << n log n << n^2 << 2^n")


# ============================================================================
# 23. DIGIT COUNTING
# ============================================================================

def decimal_digit_count(n: int) -> int:
    """
    Count decimal digits of a positive integer using logarithms.

    For n >= 1:
        digits = floor(log10(n)) + 1

    n=0 is a special case.
    """
    if n < 0:
        n = abs(n)

    if n == 0:
        return 1

    return math.floor(math.log10(n)) + 1


def binary_digit_count(n: int) -> int:
    """
    Count binary digits.

    For positive n:
        floor(log2(n)) + 1
    """
    if n < 0:
        n = abs(n)

    if n == 0:
        return 1

    return math.floor(math.log2(n)) + 1


def demonstrate_digit_counting() -> None:
    subsection("Logarithms and digit counting")

    for n in [0, 1, 9, 10, 99, 100, 999, 1000, 1024, 10**18]:
        print(
            f"n={n:20d} | decimal digits={decimal_digit_count(n):3d} "
            f"| binary digits={binary_digit_count(n):3d}"
        )


# ============================================================================
# 24. INTEGER LOG2 AND POWER-OF-TWO CHECKING
# ============================================================================

def is_power_of_two(n: int) -> bool:
    """Return True if n is a positive power of two."""
    return n > 0 and (n & (n - 1)) == 0


def demonstrate_power_of_two_properties() -> None:
    subsection("Powers of two and integer logarithms")

    for n in [0, 1, 2, 3, 4, 7, 8, 16, 31, 32, 64, 100]:
        if n > 0:
            print(
                f"n={n:3d} | power_of_two={is_power_of_two(n)} "
                f"| floor(log2(n))={math.floor(math.log2(n))}"
            )
        else:
            print(f"n={n:3d} | power_of_two=False | log2 undefined")


# ============================================================================
# 25. POPULATION / COMPOUND GROWTH
# ============================================================================

def time_to_reach(
    initial: float,
    growth_factor: float,
    target: float,
) -> float:
    """
    Solve:

        initial * growth_factor^t = target

    for t.
    """
    if initial <= 0 or growth_factor <= 0 or target <= 0:
        raise ValueError("All quantities must be positive.")

    if growth_factor == 1:
        if initial >= target:
            return 0.0
        raise ValueError("A growth factor of 1 never reaches a larger target.")

    return math.log(target / initial) / math.log(growth_factor)


def demonstrate_compound_growth() -> None:
    subsection("Compound growth and logarithms")

    initial = 10_000
    annual_factor = 1.08
    target = 20_000

    years = time_to_reach(initial, annual_factor, target)
    print(
        f"Starting value={initial}, annual factor={annual_factor}, "
        f"target={target}"
    )
    print(f"Continuous time estimate in years = {years:.8f}")

    whole_years = math.ceil(years)
    actual_value = initial * annual_factor ** whole_years

    print(
        f"After {whole_years} complete years: "
        f"{actual_value:.2f}"
    )


# ============================================================================
# 26. HALF-LIFE
# ============================================================================

def remaining_fraction_after_half_lives(number_of_half_lives: float) -> float:
    return 0.5 ** number_of_half_lives


def half_lives_to_reach_fraction(fraction: float) -> float:
    if not 0 < fraction <= 1:
        raise ValueError("Fraction must lie in (0, 1].")
    return math.log(fraction) / math.log(0.5)


def demonstrate_half_life() -> None:
    subsection("Half-life and logarithms")

    for half_lives in [0, 1, 2, 3, 5, 10]:
        fraction = remaining_fraction_after_half_lives(half_lives)
        print(
            f"{half_lives:3d} half-lives -> remaining fraction={fraction:.10f}"
        )

    target_fraction = 0.01
    required = half_lives_to_reach_fraction(target_fraction)
    print(
        f"\nHalf-lives required to reach {target_fraction:.2%}: "
        f"{required:.8f}"
    )


# ============================================================================
# 27. LOGARITHMS AND NUMERICAL SCALE
# ============================================================================

def demonstrate_order_of_magnitude() -> None:
    subsection("Orders of magnitude")

    values = [
        1e-12,
        1e-9,
        1e-6,
        1e-3,
        1,
        1e3,
        1e6,
        1e9,
        1e12,
    ]

    for value in values:
        print(
            f"{value:12.1e} -> log10={math.log10(value):8.3f}"
        )


# ============================================================================
# 28. LOG-DOMAIN MULTIPLICATION
# ============================================================================

def multiply_in_log_domain(log_x: float, log_y: float) -> float:
    """Return ln(x*y) given ln(x) and ln(y)."""
    return log_x + log_y


def demonstrate_log_domain_arithmetic() -> None:
    subsection("Arithmetic in the logarithmic domain")

    x = 1e150
    y = 1e100

    log_x = math.log(x)
    log_y = math.log(y)
    log_product = multiply_in_log_domain(log_x, log_y)

    print(f"ln(x) = {log_x:.8f}")
    print(f"ln(y) = {log_y:.8f}")
    print(f"ln(xy) = {log_product:.8f}")
    print(f"exp(ln(xy)) = {math.exp(log_product):.8e}")

    print("\nThe main advantage is that products become sums,")
    print("which can reduce overflow risk in appropriate computations.")


# ============================================================================
# 29. LOG-SUM-EXP
# ============================================================================

def log_sum_exp(values: Sequence[float]) -> float:
    """
    Stable computation of:

        log(sum(exp(x_i)))

    using:

        m + log(sum(exp(x_i - m)))

    where m = max(x_i).

    This prevents overflow for large positive values.
    """
    if not values:
        raise ValueError("At least one value is required.")

    maximum = max(values)

    if math.isinf(maximum):
        return maximum

    return maximum + math.log(
        sum(math.exp(value - maximum) for value in values)
    )


def naive_log_sum_exp(values: Sequence[float]) -> float:
    """Direct but potentially unstable implementation."""
    return math.log(sum(math.exp(value) for value in values))


def demonstrate_log_sum_exp() -> None:
    subsection("Stable log-sum-exp")

    normal_values = [1.0, 2.0, 3.0]
    stable = log_sum_exp(normal_values)
    naive = naive_log_sum_exp(normal_values)

    print(f"Normal values: stable={stable:.12f}, naive={naive:.12f}")

    large_values = [1000.0, 1001.0, 1002.0]

    print("\nLarge values:")
    print(f"Stable log-sum-exp = {log_sum_exp(large_values):.12f}")

    try:
        print(f"Naive calculation  = {naive_log_sum_exp(large_values):.12f}")
    except OverflowError as error:
        print(f"Naive calculation failed as expected: {error}")


# ============================================================================
# 30. LOG SOFTMAX
# ============================================================================

def log_softmax(values: Sequence[float]) -> List[float]:
    """
    Compute log-softmax:

        log_softmax(x_i) = x_i - log(sum(exp(x_j)))

    using stable log-sum-exp.
    """
    normalizer = log_sum_exp(values)
    return [value - normalizer for value in values]


def demonstrate_log_softmax() -> None:
    subsection("Log-softmax")

    logits = [2.0, 1.0, 0.1]

    result = log_softmax(logits)
    probabilities = [math.exp(value) for value in result]

    print(f"logits       = {logits}")
    print(f"log-softmax  = {[round(v, 8) for v in result]}")
    print(f"probabilities = {[round(v, 8) for v in probabilities]}")
    print(f"sum(probabilities) = {sum(probabilities):.12f}")


# ============================================================================
# 31. LOG PROBABILITIES
# ============================================================================

def safe_log_probability(probability: float) -> float:
    """Return ln(p), rejecting invalid probabilities."""
    if probability <= 0 or probability > 1:
        raise ValueError("Probability must satisfy 0 < p <= 1.")
    return math.log(probability)


def demonstrate_log_probabilities() -> None:
    subsection("Log probabilities")

    probabilities = [0.5, 0.1, 0.01, 1e-10]

    for probability in probabilities:
        print(
            f"p={probability:.1e} -> log(p)={safe_log_probability(probability):.10f}"
        )

    print("\nProducts of probabilities become sums of log probabilities.")

    probabilities = [0.8, 0.7, 0.9, 0.95]
    direct_product = math.prod(probabilities)
    log_product = sum(math.log(p) for p in probabilities)

    print(f"Direct product = {direct_product:.12f}")
    print(f"exp(sum(log(p))) = {math.exp(log_product):.12f}")


# ============================================================================
# 32. GEOMETRIC MEAN USING LOGARITHMS
# ============================================================================

def geometric_mean(values: Sequence[float]) -> float:
    """Compute geometric mean via the logarithmic identity."""
    if not values:
        raise ValueError("At least one value is required.")

    if any(value <= 0 for value in values):
        raise ValueError("All values must be positive.")

    return math.exp(
        sum(math.log(value) for value in values) / len(values)
    )


def demonstrate_geometric_mean() -> None:
    subsection("Geometric mean")

    values = [2, 8, 32]

    arithmetic = statistics.mean(values)
    geometric = geometric_mean(values)

    print(f"Values = {values}")
    print(f"Arithmetic mean = {arithmetic:.8f}")
    print(f"Geometric mean  = {geometric:.8f}")

    print("Geometric mean is natural for multiplicative growth factors.")


# ============================================================================
# 33. LOGARITHMIC INTERPOLATION
# ============================================================================

def logarithmic_interpolation(
    x: float,
    x_min: float,
    x_max: float,
    y_min: float,
    y_max: float,
) -> float:
    """
    Interpolate linearly in log10(x):

        t = (log10(x) - log10(x_min)) /
            (log10(x_max) - log10(x_min))

        y = y_min + t(y_max-y_min)
    """
    if min(x, x_min, x_max) <= 0:
        raise ValueError("Logarithmic interpolation requires positive x values.")

    if x_min == x_max:
        raise ValueError("x_min and x_max must differ.")

    t = (
        math.log10(x) - math.log10(x_min)
    ) / (
        math.log10(x_max) - math.log10(x_min)
    )

    return y_min + t * (y_max - y_min)


def demonstrate_log_interpolation() -> None:
    subsection("Logarithmic interpolation")

    for x in [1, 10, 100, 1000]:
        y = logarithmic_interpolation(x, 1, 1000, 0, 1)
        print(f"x={x:6g} -> interpolated y={y:.8f}")


# ============================================================================
# 34. LOG-SCALE BUCKETING
# ============================================================================

def logarithmic_bucket(value: float, base: float = 10) -> int:
    """
    Determine the integer logarithmic bucket.

    For base 10:
        1 through <10 -> 0
        10 through <100 -> 1
        100 through <1000 -> 2

    Values between 0 and 1 produce negative buckets.
    """
    if value <= 0:
        raise ValueError("Value must be positive.")
    if base <= 0 or base == 1:
        raise ValueError("Base must be positive and different from 1.")

    return math.floor(log_value(base, value))


def demonstrate_log_bucketing() -> None:
    subsection("Logarithmic bucketing")

    values = [0.01, 0.5, 1, 3, 9.9, 10, 99, 100, 999, 1000, 10000]

    for value in values:
        print(
            f"value={value:8g} -> base-10 bucket={logarithmic_bucket(value)}"
        )


# ============================================================================
# 35. BINARY SEARCH AS AN EXPLICIT LOGARITHMIC PROCESS
# ============================================================================

def binary_search_trace(
    sorted_values: Sequence[int],
    target: int,
) -> List[Tuple[int, int, int]]:
    """Return (left, middle, right) for each binary-search iteration."""
    left = 0
    right = len(sorted_values) - 1
    trace = []

    while left <= right:
        middle = (left + right) // 2
        trace.append((left, middle, right))

        if sorted_values[middle] == target:
            break

        if sorted_values[middle] < target:
            left = middle + 1
        else:
            right = middle - 1

    return trace


def demonstrate_binary_search_trace() -> None:
    subsection("Binary-search trace")

    values = list(range(1, 65))
    target = 53
    trace = binary_search_trace(values, target)

    for iteration, (left, middle, right) in enumerate(trace, start=1):
        print(
            f"iteration={iteration:2d}, "
            f"left={left:2d}, middle={middle:2d}, right={right:2d}, "
            f"value={values[middle]}"
        )

    print(
        f"Iterations = {len(trace)}, "
        f"rough logarithmic scale = {math.log2(len(values)):.4f}"
    )


# ============================================================================
# 36. NEWTON'S METHOD FOR LOGARITHMIC EQUATIONS
# ============================================================================

def newton_solve(
    function: Callable[[float], float],
    derivative: Callable[[float], float],
    initial_guess: float,
    tolerance: float = 1e-12,
    max_iterations: int = 100,
) -> Tuple[float, int]:
    """Generic Newton-Raphson solver."""
    x = initial_guess

    for iteration in range(1, max_iterations + 1):
        value = function(x)
        slope = derivative(x)

        if slope == 0:
            raise ZeroDivisionError("Newton iteration encountered zero derivative.")

        next_x = x - value / slope

        if abs(next_x - x) <= tolerance:
            return next_x, iteration

        x = next_x

    raise RuntimeError("Newton-Raphson did not converge.")


def demonstrate_newton_log_equation() -> None:
    subsection("Numerical solution of a logarithmic equation")

    # Solve ln(x) = 3.
    # f(x) = ln(x) - 3
    # f'(x) = 1/x
    function = lambda x: math.log(x) - 3
    derivative = lambda x: 1 / x

    solution, iterations = newton_solve(
        function,
        derivative,
        initial_guess=10.0,
    )

    exact = math.exp(3)

    print(f"Newton solution = {solution:.14f}")
    print(f"Exact solution  = {exact:.14f}")
    print(f"Iterations      = {iterations}")


# ============================================================================
# 37. BISECTION FOR LOGARITHMIC EQUATIONS
# ============================================================================

def bisection_solve(
    function: Callable[[float], float],
    left: float,
    right: float,
    tolerance: float = 1e-12,
    max_iterations: int = 200,
) -> Tuple[float, int]:
    """Solve f(x)=0 using the bisection method."""
    f_left = function(left)
    f_right = function(right)

    if f_left == 0:
        return left, 0
    if f_right == 0:
        return right, 0

    if f_left * f_right > 0:
        raise ValueError("Function must have opposite signs at the endpoints.")

    for iteration in range(1, max_iterations + 1):
        middle = (left + right) / 2
        f_middle = function(middle)

        if abs(f_middle) <= tolerance or abs(right - left) <= tolerance:
            return middle, iteration

        if f_left * f_middle < 0:
            right = middle
            f_right = f_middle
        else:
            left = middle
            f_left = f_middle

    raise RuntimeError("Bisection did not converge.")


def demonstrate_bisection_log_equation() -> None:
    subsection("Bisection method")

    # Solve log10(x) = 2.7.
    function = lambda x: math.log10(x) - 2.7

    solution, iterations = bisection_solve(
        function,
        left=100,
        right=1000,
    )

    exact = 10 ** 2.7

    print(f"Bisection solution = {solution:.14f}")
    print(f"Exact solution     = {exact:.14f}")
    print(f"Iterations         = {iterations}")


# ============================================================================
# 38. ERROR PROPAGATION
# ============================================================================

def demonstrate_error_sensitivity() -> None:
    subsection("Sensitivity of logarithms")

    print("For f(x)=ln(x), f'(x)=1/x.")
    print("A small absolute error dx produces approximately dx/x error in ln(x).")

    for x in [1, 10, 100, 1_000_000]:
        dx = 1e-3
        exact_change = math.log(x + dx) - math.log(x)
        approximation = dx / x

        print(
            f"x={x:10g} | exact change={exact_change:.12e} "
            f"| approximation={approximation:.12e}"
        )


# ============================================================================
# 39. FLOATING-POINT EDGE CASES
# ============================================================================

def demonstrate_floating_point_edges() -> None:
    subsection("Floating-point and boundary behavior")

    tiny_values = [1e-10, 1e-100, 1e-300]

    for value in tiny_values:
        print(f"ln({value:.0e}) = {math.log(value):.8f}")

    print("\nValues close to one:")
    for delta in [1e-4, 1e-8, 1e-12, 1e-16]:
        value = 1 + delta
        print(
            f"delta={delta:.1e} | "
            f"log(1+delta)={math.log(value):.20e} | "
            f"log1p(delta)={math.log1p(delta):.20e}"
        )

    print("\nThe distinction between log(1+x) and log1p(x)")
    print("matters when x is sufficiently small for floating-point rounding.")


# ============================================================================
# 40. OVERFLOW AND UNDERFLOW
# ============================================================================

def demonstrate_overflow_underflow() -> None:
    subsection("Overflow and underflow")

    print("Exponentiation can overflow long before logarithmic arithmetic does.")

    try:
        value = math.exp(1000)
        print(value)
    except OverflowError as error:
        print(f"math.exp(1000) -> OverflowError: {error}")

    print("\nA logarithmic representation can retain the scale:")
    print(f"ln(exp(1000)) represented symbolically = 1000")

    tiny = math.exp(-700)
    print(f"exp(-700) = {tiny:.5e}")

    try:
        print(f"exp(-1000) = {math.exp(-1000):.5e}")
    except OverflowError as error:
        print(f"Unexpected overflow: {error}")


# ============================================================================
# 41. LOGARITHM BASE COMPARISON
# ============================================================================

def demonstrate_base_comparison() -> None:
    subsection("Comparing logarithm bases")

    x = 1_000_000

    for base in [2, math.e, 10, 16]:
        print(
            f"log_{base:g}({x}) = {log_value(base, x):.8f}"
        )

    print(
        "\nChanging the base changes the numerical scale, "
        "but not the underlying logarithmic relationship."
    )


# ============================================================================
# 42. CHANGE OF BASE IDENTITY CHECK
# ============================================================================

def verify_change_of_base_randomly(
    trials: int = 100,
    seed: int = 42,
) -> None:
    subsection("Randomized verification of change of base")

    random_generator = random.Random(seed)
    maximum_error = 0.0

    for _ in range(trials):
        base = 10 ** random_generator.uniform(-1, 2)
        if math.isclose(base, 1.0, rel_tol=0, abs_tol=1e-8):
            base = 2.0

        value = 10 ** random_generator.uniform(-5, 5)

        direct = math.log(value, base)
        converted = math.log(value) / math.log(base)

        error = abs(direct - converted)
        maximum_error = max(maximum_error, error)

    print(f"Trials = {trials}")
    print(f"Maximum absolute difference = {maximum_error:.3e}")


# ============================================================================
# 43. PROPERTY TESTS
# ============================================================================

def assert_close(
    actual: float,
    expected: float,
    tolerance: float = 1e-10,
) -> None:
    if not math.isclose(actual, expected, rel_tol=tolerance, abs_tol=tolerance):
        raise AssertionError(
            f"Expected {expected}, got {actual}"
        )


def run_property_tests() -> None:
    subsection("Property-based-style numerical tests")

    bases = [0.25, 0.5, 2, 3, 10, math.e]
    values = [0.1, 0.5, 1, 2, 10, 100]

    for base in bases:
        for value in values:
            assert_close(
                base ** log_value(base, value),
                value,
                tolerance=1e-9,
            )

    for base in [2, 3, 10]:
        for x in [0.1, 1, 2, 5, 20]:
            for y in [0.2, 1.5, 4, 10]:
                assert_close(
                    log_value(base, x * y),
                    log_value(base, x) + log_value(base, y),
                    tolerance=1e-9,
                )

    print("All logarithm identity tests passed.")


# ============================================================================
# 44. COMMON MISTAKES
# ============================================================================

def demonstrate_common_mistakes() -> None:
    subsection("Common mistakes and their corrections")

    x = 100
    y = 10

    correct_quotient = math.log10(x / y)
    incorrect_quotient = math.log10(x) / math.log10(y)

    print("Mistake: log(x/y) = log(x)/log(y)")
    print(f"Correct log10({x}/{y}) = {correct_quotient}")
    print(f"Incorrect expression     = {incorrect_quotient}")

    correct_product = math.log10(x * y)
    incorrect_product = math.log10(x) * math.log10(y)

    print("\nMistake: log(xy) = log(x) * log(y)")
    print(f"Correct log10({x}*{y}) = {correct_product}")
    print(f"Incorrect expression    = {incorrect_product}")

    print("\nCorrect identities:")
    print("log(xy) = log(x) + log(y)")
    print("log(x/y) = log(x) - log(y)")
    print("log(x^k) = k log(x)")


# ============================================================================
# 45. DOMAIN CHECKING IN EQUATIONS
# ============================================================================

def valid_log_expression(argument: float) -> bool:
    return argument > 0


def demonstrate_equation_domain_checks() -> None:
    subsection("Domain checks before algebra")

    expressions = [
        ("log(x)", lambda x: x),
        ("log(x-3)", lambda x: x - 3),
        ("log(2x+1)", lambda x: 2 * x + 1),
    ]

    test_values = [-5, -1, 0, 1, 3, 4, 10]

    for name, argument_function in expressions:
        valid_values = [
            x for x in test_values
            if valid_log_expression(argument_function(x))
        ]
        print(f"{name:12s} valid among test values -> {valid_values}")

    print(
        "\nWhen solving logarithmic equations, algebraic transformations "
        "can introduce candidates outside the original domain."
    )


# ============================================================================
# 46. LOGARITHMIC VS EXPONENTIAL FUNCTIONS
# ============================================================================

def demonstrate_inverse_relationship() -> None:
    subsection("Logarithmic versus exponential functions")

    pairs = [
        (2, 3),
        (10, 2),
        (math.e, 4),
        (0.5, 5),
    ]

    for base, exponent in pairs:
        value = base ** exponent
        recovered = log_value(base, value)

        print(
            f"base={base:g}, exponent={exponent:g}, "
            f"base^exponent={value:.8f}, "
            f"log_base(value)={recovered:.8f}"
        )


# ============================================================================
# 47. AMORTIZED / TREE-BASED STRUCTURES
# ============================================================================

def tree_height_for_nodes(nodes: int, branching_factor: int) -> float:
    """
    Approximate height of a balanced tree containing `nodes` nodes
    with branching factor b:

        h ~= log_b(nodes)

    """
    if nodes <= 0:
        raise ValueError("nodes must be positive.")
    if branching_factor <= 1:
        raise ValueError("branching_factor must exceed 1.")

    return math.log(nodes, branching_factor)


def demonstrate_tree_height() -> None:
    subsection("Logarithms in balanced trees")

    for nodes in [100, 1_000, 10_000, 1_000_000]:
        for branching_factor in [2, 4, 10]:
            height = tree_height_for_nodes(nodes, branching_factor)
            print(
                f"nodes={nodes:9d}, branching={branching_factor:2d}, "
                f"logarithmic height={height:.4f}"
            )


# ============================================================================
# 48. PERFORMANCE MEASUREMENT
# ============================================================================

def benchmark_logarithm_functions(iterations: int = 200_000) -> None:
    subsection("Basic computational performance")

    values = [i + 1.0 for i in range(1000)]

    start = time.perf_counter()
    accumulator = 0.0

    for i in range(iterations):
        accumulator += math.log(values[i % len(values)])

    elapsed = time.perf_counter() - start

    print(f"Iterations = {iterations}")
    print(f"Elapsed time = {elapsed:.6f} seconds")
    print(f"Accumulator = {accumulator:.6f}")

    print(
        "\nPerformance measurements vary with Python version, "
        "hardware, operating system, and workload."
    )


# ============================================================================
# 49. PRACTICAL APPLICATION: COMPOUND INTEREST
# ============================================================================

def compound_value(
    principal: float,
    annual_rate: float,
    periods_per_year: int,
    years: float,
) -> float:
    """A = P(1+r/n)^(nt)."""
    if principal < 0:
        raise ValueError("Principal cannot be negative.")
    if periods_per_year <= 0:
        raise ValueError("Periods per year must be positive.")
    if 1 + annual_rate / periods_per_year <= 0:
        raise ValueError("Growth factor must be positive.")

    return principal * (
        1 + annual_rate / periods_per_year
    ) ** (periods_per_year * years)


def demonstrate_compound_interest() -> None:
    subsection("Compound interest")

    principal = 100_000
    annual_rate = 0.08
    periods_per_year = 12
    target = 200_000

    print(
        f"Initial principal = {principal:.2f}\n"
        f"Annual rate = {annual_rate:.2%}"
    )

    years = (
        math.log(target / principal)
        / (
            periods_per_year
            * math.log(1 + annual_rate / periods_per_year)
        )
    )

    print(f"Time to double approximately = {years:.8f} years")
    print(
        f"Value after that time = "
        f"{compound_value(principal, annual_rate, periods_per_year, years):.2f}"
    )


# ============================================================================
# 50. CONTINUOUS COMPOUNDING
# ============================================================================

def continuous_compound_value(
    principal: float,
    rate: float,
    time_years: float,
) -> float:
    return principal * math.exp(rate * time_years)


def demonstrate_continuous_compounding() -> None:
    subsection("Continuous compounding and natural logarithms")

    principal = 100_000
    rate = 0.08
    years = 5

    value = continuous_compound_value(principal, rate, years)

    print(f"A = Pe^(rt)")
    print(f"P={principal}, r={rate}, t={years}")
    print(f"A={value:.8f}")


# ============================================================================
# 51. LOGARITHMS IN SCIENTIFIC MODELING
# ============================================================================

def demonstrate_linearization() -> None:
    subsection("Linearization of exponential relationships")

    print("If y = A * b^x:")
    print("ln(y) = ln(A) + x ln(b)")
    print("Thus an exponential relationship becomes linear in log space.")

    A = 5
    b = 1.8

    print(f"\nA={A}, b={b}")

    for x in range(6):
        y = A * b ** x
        log_y = math.log(y)

        print(
            f"x={x:2d} | y={y:12.6f} | "
            f"ln(y)={log_y:12.6f} | "
            f"ln(A)+x*ln(b)={math.log(A) + x * math.log(b):12.6f}"
        )


# ============================================================================
# 52. LOGARITHMIC REGRESSION IDEA
# ============================================================================

@dataclass
class LinearModel:
    slope: float
    intercept: float

    def predict(self, x: float) -> float:
        return self.intercept + self.slope * x


def least_squares_linear_fit(
    x_values: Sequence[float],
    y_values: Sequence[float],
) -> LinearModel:
    """Simple ordinary least-squares line fit."""
    if len(x_values) != len(y_values):
        raise ValueError("x and y must have equal lengths.")
    if len(x_values) < 2:
        raise ValueError("At least two points are required.")

    x_mean = statistics.mean(x_values)
    y_mean = statistics.mean(y_values)

    numerator = sum(
        (x - x_mean) * (y - y_mean)
        for x, y in zip(x_values, y_values)
    )
    denominator = sum(
        (x - x_mean) ** 2
        for x in x_values
    )

    if denominator == 0:
        raise ValueError("x values must not all be equal.")

    slope = numerator / denominator
    intercept = y_mean - slope * x_mean

    return LinearModel(slope, intercept)


def demonstrate_exponential_fit_via_logs() -> None:
    subsection("Fitting an exponential model through logarithms")

    A = 3.5
    b = 1.7

    x_values = [0, 1, 2, 3, 4, 5]
    y_values = [A * b ** x for x in x_values]

    transformed_y = [math.log(y) for y in y_values]

    model = least_squares_linear_fit(x_values, transformed_y)

    estimated_A = math.exp(model.intercept)
    estimated_b = math.exp(model.slope)

    print(f"Actual A = {A:.8f}")
    print(f"Estimated A = {estimated_A:.8f}")
    print(f"Actual b = {b:.8f}")
    print(f"Estimated b = {estimated_b:.8f}")

    print(
        "\nThe transformation is:"
        "\nln(y) = intercept + slope*x"
        "\nA = exp(intercept)"
        "\nb = exp(slope)"
    )


# ============================================================================
# 53. EDGE CASES FOR BASES BETWEEN ZERO AND ONE
# ============================================================================

def demonstrate_fractional_bases() -> None:
    subsection("Bases between 0 and 1")

    base = 0.5

    print("A valid logarithm base does not need to be greater than 1.")
    print("When 0 < b < 1, the logarithm is decreasing.")

    for value in [0.125, 0.25, 0.5, 1, 2, 4, 8]:
        print(
            f"log_{base}({value:g}) = {log_value(base, value):.6f}"
        )


# ============================================================================
# 54. COMPLEX LOGARITHMS
# ============================================================================

def demonstrate_complex_logarithms() -> None:
    subsection("Complex logarithms")

    print(
        "The real logarithm requires a positive argument, "
        "but complex analysis extends logarithms to complex numbers."
    )

    complex_values = [
        complex(-1, 0),
        complex(1, 1),
        complex(-2, 3),
    ]

    for value in complex_values:
        result = complex(math.log(abs(value)), math.atan2(value.imag, value.real))
        print(f"Principal-style representation for ln({value}) ≈ {result}")

    print(
        "\nThe complex logarithm is multi-valued because angles can differ "
        "by integer multiples of 2*pi. Python's cmath.log handles the "
        "principal branch."
    )

    import cmath

    for value in complex_values:
        print(f"cmath.log({value}) = {cmath.log(value)}")


# ============================================================================
# 55. LOGARITHMS OF PRODUCTS WITH EXTREME MAGNITUDES
# ============================================================================

def demonstrate_extreme_product_handling() -> None:
    subsection("Extreme products")

    numbers = [1e100, 1e120, 1e90]

    log_product = sum(math.log(value) for value in numbers)

    print("Numbers:")
    for number in numbers:
        print(f"  {number:.3e}")

    print(f"\nlog(product) = {log_product:.12f}")

    try:
        direct = math.prod(numbers)
        print(f"Direct product = {direct:.3e}")
    except OverflowError as error:
        print(f"Direct product overflowed: {error}")

    print(
        "The logarithmic representation preserves multiplicative scale "
        "without necessarily constructing the enormous product."
    )


# ============================================================================
# 56. STABLE LOGARITHM OF A SUM OF TWO EXPONENTS
# ============================================================================

def log_add_exp(a: float, b: float) -> float:
    """
    Stable computation of ln(exp(a) + exp(b)).
    """
    if a < b:
        a, b = b, a

    if math.isinf(a):
        return a

    return a + math.log1p(math.exp(b - a))


def demonstrate_log_add_exp() -> None:
    subsection("Stable two-term log addition")

    pairs = [
        (1, 2),
        (100, 101),
        (1000, 1001),
        (-1000, -999),
    ]

    for a, b in pairs:
        print(
            f"a={a:6g}, b={b:6g} -> "
            f"log(exp(a)+exp(b))={log_add_exp(a, b):.12f}"
        )


# ============================================================================
# 57. LOGARITHMIC DISTANCES
# ============================================================================

def multiplicative_distance(x: float, y: float) -> float:
    """
    Symmetric distance in log space:

        |ln(x/y)|

    It measures multiplicative rather than additive separation.
    """
    if x <= 0 or y <= 0:
        raise ValueError("Values must be positive.")

    return abs(math.log(x / y))


def demonstrate_multiplicative_distance() -> None:
    subsection("Distance in logarithmic space")

    pairs = [
        (10, 20),
        (100, 200),
        (1, 2),
        (1000, 500),
        (5, 50),
    ]

    for x, y in pairs:
        print(
            f"x={x:7g}, y={y:7g} -> |ln(x/y)|={multiplicative_distance(x, y):.8f}"
        )

    print(
        "\nA doubling has the same log-distance regardless of absolute scale."
    )


# ============================================================================
# 58. COMMON LOGARITHM ESTIMATION
# ============================================================================

def estimate_decimal_order(value: float) -> int:
    """Return floor(log10(value)) for positive values."""
    if value <= 0:
        raise ValueError("Value must be positive.")
    return math.floor(math.log10(value))


def demonstrate_log_estimation() -> None:
    subsection("Estimation with logarithms")

    values = [3, 30, 300, 3000, 0.3, 0.03]

    for value in values:
        order = estimate_decimal_order(value)
        print(
            f"value={value:8g} -> order of magnitude exponent={order}"
        )


# ============================================================================
# 59. LOGARITHMIC SCALE CONVERSION
# ============================================================================

def linear_to_log_scale(
    value: float,
    minimum: float,
    maximum: float,
) -> float:
    """Map a positive value to [0, 1] using logarithmic scaling."""
    if minimum <= 0 or maximum <= 0 or value <= 0:
        raise ValueError("All values must be positive.")
    if minimum >= maximum:
        raise ValueError("minimum must be smaller than maximum.")
    if not minimum <= value <= maximum:
        raise ValueError("value must lie inside [minimum, maximum].")

    return (
        math.log10(value) - math.log10(minimum)
    ) / (
        math.log10(maximum) - math.log10(minimum)
    )


def demonstrate_log_scale_conversion() -> None:
    subsection("Logarithmic scale normalization")

    minimum = 1
    maximum = 1_000_000

    for value in [1, 10, 100, 1000, 10000, 100000, 1_000_000]:
        scaled = linear_to_log_scale(value, minimum, maximum)
        print(f"value={value:10g} -> normalized log scale={scaled:.8f}")


# ============================================================================
# 60. SECURITY-RELATED COMPUTATIONAL CONSIDERATIONS
# ============================================================================

def demonstrate_security_considerations() -> None:
    subsection("Security and reliability considerations")

    print("Logarithms can appear in:")
    print("  - password-search-space estimates")
    print("  - entropy calculations")
    print("  - cryptographic parameter analysis")
    print("  - probabilistic scoring")
    print("  - anomaly detection")

    print("\nImportant security practices:")
    print("  1. Do not confuse entropy with password security by itself.")
    print("  2. Validate domains before evaluating logarithms.")
    print("  3. Avoid unstable probability calculations.")
    print("  4. Preserve sufficient numerical precision.")
    print("  5. Treat user-controlled numeric inputs as untrusted input.")
    print("  6. Avoid assuming floating-point equality for derived values.")


# ============================================================================
# 61. INPUT VALIDATION
# ============================================================================

def safe_log_from_user_input(
    base_text: str,
    value_text: str,
) -> str:
    """
    Parse textual numeric input and evaluate a logarithm.

    This function demonstrates validation rather than using eval().
    """
    try:
        base = float(base_text)
        value = float(value_text)
    except ValueError:
        return "Invalid numeric input."

    try:
        result = log_value(base, value)
    except ValueError as error:
        return f"Invalid logarithm: {error}"

    return f"log_{base}({value}) = {result}"


def demonstrate_input_validation() -> None:
    subsection("Input validation")

    examples = [
        ("10", "1000"),
        ("2", "32"),
        ("1", "10"),
        ("10", "0"),
        ("abc", "10"),
    ]

    for base_text, value_text in examples:
        print(
            f"base={base_text!r}, value={value_text!r} -> "
            f"{safe_log_from_user_input(base_text, value_text)}"
        )


# ============================================================================
# 62. LIMITS AND ASYMPTOTIC BEHAVIOR
# ============================================================================

def demonstrate_limits() -> None:
    subsection("Asymptotic behavior")

    print("For any valid base b:")
    print("  lim(x->infinity) log_b(x) = infinity")
    print("  lim(x->0+) log_b(x) = -infinity")

    for base in [2, math.e, 10]:
        print(f"\nBase {base:g}:")
        for x in [1e-1, 1e-3, 1e-6, 1e3, 1e6]:
            print(f"  x={x:.0e} -> log={log_value(base, x):.8f}")


# ============================================================================
# 63. LOGARITHM AND EXPONENTIAL IDENTITIES
# ============================================================================

def demonstrate_identity_table() -> None:
    subsection("Identity table")

    print("Identity                         Example")
    print("-" * 65)
    print("log_b(1) = 0                     log_2(1) = 0")
    print("log_b(b) = 1                     log_2(2) = 1")
    print("log_b(b^x) = x                   log_3(3^5) = 5")
    print("b^(log_b(x)) = x                 2^(log_2(7)) = 7")
    print("log_b(xy)=log_b(x)+log_b(y)      product rule")
    print("log_b(x/y)=log_b(x)-log_b(y)     quotient rule")
    print("log_b(x^k)=k log_b(x)            power rule")
    print("log_b(x)=ln(x)/ln(b)              change of base")


# ============================================================================
# 64. PRACTICAL MINI-PROJECT: SEARCH COMPLEXITY
# ============================================================================

def compare_search_sizes() -> None:
    subsection("Mini-project: search-space reduction")

    sizes = [10, 100, 1_000, 10_000, 100_000, 1_000_000]

    print(
        f"{'Search space':>15} | {'Linear checks':>15} | "
        f"{'Binary-search scale':>22}"
    )
    print("-" * 60)

    for size in sizes:
        binary_scale = math.ceil(math.log2(size))
        print(
            f"{size:15d} | {size:15d} | {binary_scale:22d}"
        )

    print(
        "\nA balanced halving process requires logarithmically many "
        "levels because repeated halving asks how many times 2 must "
        "be multiplied to reach the original scale."
    )


# ============================================================================
# 65. PRACTICAL MINI-PROJECT: INFORMATION CAPACITY
# ============================================================================

def bits_for_symbols(number_of_symbols: int) -> float:
    if number_of_symbols <= 0:
        raise ValueError("Number of symbols must be positive.")
    return math.log2(number_of_symbols)


def demonstrate_information_capacity() -> None:
    subsection("Mini-project: information capacity")

    symbol_counts = [
        2,
        4,
        8,
        16,
        256,
        65_536,
        1_000_000,
    ]

    for count in symbol_counts:
        print(
            f"{count:10d} equally likely symbols -> "
            f"{bits_for_symbols(count):12.6f} bits"
        )


# ============================================================================
# 66. PRACTICAL MINI-PROJECT: GROWTH DOUBLING TIME
# ============================================================================

def doubling_time(growth_factor_per_period: float) -> float:
    """
    Solve:

        growth_factor^t = 2

    for t.
    """
    if growth_factor_per_period <= 0 or growth_factor_per_period == 1:
        raise ValueError("Growth factor must be positive and not equal to 1.")

    return math.log(2) / math.log(growth_factor_per_period)


def demonstrate_doubling_time() -> None:
    subsection("Mini-project: doubling time")

    for growth_factor in [1.01, 1.02, 1.05, 1.10, 1.50, 2.0]:
        print(
            f"Growth factor={growth_factor:.2f} "
            f"-> doubling periods={doubling_time(growth_factor):.8f}"
        )


# ============================================================================
# 67. RELATIONSHIP TO BIG-O NOTATION
# ============================================================================

def demonstrate_big_o_logarithm() -> None:
    subsection("Why O(log n) is efficient")

    n = 2 ** 20
    levels = math.log2(n)

    print(f"n = {n:,}")
    print(f"log2(n) = {levels:.0f}")
    print(
        "A process that halves its remaining problem size at every step "
        "needs approximately log2(n) steps."
    )

    print("\nExamples:")
    print("  binary search")
    print("  balanced binary trees")
    print("  divide-and-conquer depth")
    print("  repeated doubling/halving processes")


# ============================================================================
# 68. DISTINGUISHING LOGARITHMIC EXPRESSIONS
# ============================================================================

def demonstrate_expression_distinctions() -> None:
    subsection("Important expression distinctions")

    x = 8

    print(f"log2({x}) = {math.log2(x):.8f}")
    print(f"log(2*{x}) = {math.log(2 * x):.8f}")
    print(f"log(2) * log({x}) = {math.log(2) * math.log(x):.8f}")
    print(f"log(2) + log({x}) = {math.log(2) + math.log(x):.8f}")

    print(
        "\nOnly the product identity supports "
        "log(2x) = log(2) + log(x)."
    )


# ============================================================================
# 69. EXACT SPECIAL VALUES
# ============================================================================

def demonstrate_special_values() -> None:
    subsection("Special values")

    examples = [
        ("log2(1)", math.log2(1)),
        ("log2(2)", math.log2(2)),
        ("log2(8)", math.log2(8)),
        ("log10(1)", math.log10(1)),
        ("log10(10)", math.log10(10)),
        ("ln(1)", math.log(1)),
        ("ln(e)", math.log(math.e)),
    ]

    for expression, value in examples:
        print(f"{expression:12s} = {value:.12f}")


# ============================================================================
# 70. MAIN PROGRAM
# ============================================================================

def main() -> None:
    """Run the complete logarithm tutorial."""

    print("LOGARITHMS: COMPREHENSIVE PYTHON STUDY SCRIPT")
    print("This script demonstrates mathematical and computational uses of logs.")

    demonstrate_basic_definition()
    demonstrate_domain_and_base_rules()
    demonstrate_common_and_natural_logs()
    demonstrate_core_identities()
    demonstrate_logarithm_properties()
    demonstrate_change_of_base()
    demonstrate_python_log_functions()

    demonstrate_exponential_equations()
    demonstrate_logarithmic_equations()
    demonstrate_linear_log_equations()
    demonstrate_logarithmic_inequalities()

    demonstrate_graph_concepts()
    demonstrate_transformations()

    demonstrate_calculus_connection()
    demonstrate_logarithmic_differentiation()

    demonstrate_decibels()
    demonstrate_ph()
    demonstrate_logarithmic_scales()

    demonstrate_binary_logarithms()
    demonstrate_entropy()
    demonstrate_binary_search_complexity()
    demonstrate_growth_rates()
    demonstrate_digit_counting()
    demonstrate_power_of_two_properties()

    demonstrate_compound_growth()
    demonstrate_half_life()
    demonstrate_order_of_magnitude()

    demonstrate_log_domain_arithmetic()
    demonstrate_log_sum_exp()
    demonstrate_log_softmax()
    demonstrate_log_probabilities()
    demonstrate_geometric_mean()
    demonstrate_log_interpolation()
    demonstrate_log_bucketing()
    demonstrate_binary_search_trace()

    demonstrate_newton_log_equation()
    demonstrate_bisection_log_equation()
    demonstrate_error_sensitivity()
    demonstrate_floating_point_edges()
    demonstrate_overflow_underflow()

    demonstrate_base_comparison()
    verify_change_of_base_randomly()
    run_property_tests()

    demonstrate_common_mistakes()
    demonstrate_equation_domain_checks()
    demonstrate_inverse_relationship()
    demonstrate_tree_height()

    benchmark_logarithm_functions()

    demonstrate_compound_interest()
    demonstrate_continuous_compounding()
    demonstrate_linearization()
    demonstrate_exponential_fit_via_logs()

    demonstrate_fractional_bases()
    demonstrate_complex_logarithms()
    demonstrate_extreme_product_handling()
    demonstrate_log_add_exp()
    demonstrate_multiplicative_distance()
    demonstrate_log_estimation()
    demonstrate_log_scale_conversion()

    demonstrate_security_considerations()
    demonstrate_input_validation()
    demonstrate_limits()
    demonstrate_identity_table()

    compare_search_sizes()
    demonstrate_information_capacity()
    demonstrate_doubling_time()
    demonstrate_big_o_logarithm()
    demonstrate_expression_distinctions()
    demonstrate_special_values()

    print("\n" + "=" * 78)
    print("END OF LOGARITHM STUDY SCRIPT")
    print("=" * 78)


if __name__ == "__main__":
    main()
