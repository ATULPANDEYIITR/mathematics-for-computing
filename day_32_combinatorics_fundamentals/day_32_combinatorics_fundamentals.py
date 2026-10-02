"""
Combinatorics Fundamentals
==========================

A self-contained progression from basic counting ideas to practical counting
systems. The program focuses on:

- Counting principles
- Sum rule
- Product rule
- Multiplication principle
- Dependent and independent choices
- Counting without enumerating every outcome
- Inclusion-exclusion for overlapping alternatives
- Permutations and combinations as extensions of the product principle
- Repeated elements and restricted arrangements
- Probability spaces built from counting
- Validation and integer-safe calculations
- Practical counting scenarios

The program uses only the Python standard library.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations, permutations, product
from math import comb, factorial
from typing import Iterable, Sequence


# ---------------------------------------------------------------------------
# Core counting functions
# ---------------------------------------------------------------------------

def sum_rule(*counts: int) -> int:
    """
    Count mutually exclusive alternatives.

    If an outcome can be produced by exactly one of several disjoint cases,
    the total number of outcomes is the sum of the case counts.
    """
    validate_non_negative_counts(counts)
    return sum(counts)


def product_rule(*counts: int) -> int:
    """
    Count sequential choices.

    If a process has k stages and stage i has counts[i] possible choices,
    then the total number of complete outcomes is their product.

    This is the multiplication principle.
    """
    validate_non_negative_counts(counts)

    total = 1
    for count in counts:
        total *= count
    return total


def validate_non_negative_counts(counts: Iterable[int]) -> None:
    """Reject invalid cardinalities before performing a counting operation."""
    for count in counts:
        if not isinstance(count, int) or isinstance(count, bool):
            raise TypeError("Every count must be an integer.")
        if count < 0:
            raise ValueError("A number of choices cannot be negative.")


def validate_positive_integer(value: int, name: str) -> None:
    """Validate a positive integer parameter."""
    if not isinstance(value, int) or isinstance(value, bool):
        raise TypeError(f"{name} must be an integer.")
    if value <= 0:
        raise ValueError(f"{name} must be positive.")


# ---------------------------------------------------------------------------
# Sum-rule examples
# ---------------------------------------------------------------------------

def sum_rule_examples() -> None:
    print("\n=== Sum Rule ===")

    # A developer can select one development environment from exactly one
    # category. Because the categories are mutually exclusive, add them.
    editors = 4
    terminal_tools = 3
    browser_ide = 2

    total_environments = sum_rule(
        editors,
        terminal_tools,
        browser_ide,
    )

    print(
        "Development environments available through exclusive categories:",
        total_environments,
    )

    # Another direct example: a system offers either 5 cloud regions or
    # 3 dedicated regions, with a request selecting exactly one region.
    cloud_regions = 5
    dedicated_regions = 3

    print(
        "Total selectable regions under exclusive routing:",
        sum_rule(cloud_regions, dedicated_regions),
    )


# ---------------------------------------------------------------------------
# Product-rule examples
# ---------------------------------------------------------------------------

def product_rule_examples() -> None:
    print("\n=== Product Rule / Multiplication Principle ===")

    # A deployment request chooses:
    # environment -> region -> deployment window.
    environments = 3
    regions = 4
    deployment_windows = 5

    deployment_plans = product_rule(
        environments,
        regions,
        deployment_windows,
    )

    print("Complete deployment plans:", deployment_plans)

    # The choices are sequential. Once one environment, one region, and one
    # window are selected, one complete plan exists.
    print(
        "API configuration combinations:",
        product_rule(2, 3, 4),
    )


# ---------------------------------------------------------------------------
# Distinguishing sum and product rules
# ---------------------------------------------------------------------------

def sum_vs_product() -> None:
    print("\n=== Sum Rule Versus Product Rule ===")

    # SUM:
    # A customer chooses either a standard or premium support plan.
    standard_plans = 4
    premium_plans = 2
    support_choices = sum_rule(standard_plans, premium_plans)

    # PRODUCT:
    # A customer chooses a plan AND a communication channel.
    plans = 6
    channels = 3
    plan_channel_pairs = product_rule(plans, channels)

    print("Exclusive plan choices:", support_choices)
    print("Plan + communication-channel combinations:", plan_channel_pairs)


# ---------------------------------------------------------------------------
# Explicit enumeration to verify a product count
# ---------------------------------------------------------------------------

def enumerate_small_product_space() -> None:
    print("\n=== Enumerating a Small Product Space ===")

    operating_systems = ["Linux", "Windows"]
    deployment_regions = ["India", "Europe", "US"]

    configurations = list(
        product(
            operating_systems,
            deployment_regions,
        )
    )

    expected = product_rule(
        len(operating_systems),
        len(deployment_regions),
    )

    print("Configurations:")
    for configuration in configurations:
        print("  ", configuration)

    print("Enumerated count:", len(configurations))
    print("Product-rule count:", expected)

    assert len(configurations) == expected


# ---------------------------------------------------------------------------
# Dependent choices
# ---------------------------------------------------------------------------

def dependent_choice_example() -> None:
    print("\n=== Dependent Choices ===")

    # Suppose a repository has 5 possible reviewers for the first review.
    # After selecting one reviewer, that reviewer cannot be selected again
    # for the second distinct reviewer.
    first_reviewers = 5
    second_reviewers = 4

    assignments = product_rule(first_reviewers, second_reviewers)

    print(
        "Ordered pairs of distinct reviewers:",
        assignments,
    )

    # This differs from simply multiplying 5 by 5 because the second choice
    # depends on the first choice.
    assert assignments == 20


# ---------------------------------------------------------------------------
# Permutations as a direct extension of the multiplication principle
# ---------------------------------------------------------------------------

def permutation_count(n: int, r: int) -> int:
    """
    Count ordered selections of r distinct objects from n objects.

    n choices are available first, n-1 second, and so on.
    """
    validate_non_negative_counts((n, r))

    if r > n:
        raise ValueError("r cannot be greater than n.")

    total = 1
    for position in range(r):
        total *= n - position

    return total


def permutation_examples() -> None:
    print("\n=== Ordered Selections ===")

    developers = ["Asha", "Ben", "Chen", "Diya"]

    count = permutation_count(len(developers), 2)

    print("Number of ordered two-person assignments:", count)

    assignments = list(permutations(developers, 2))

    for assignment in assignments:
        print("  ", assignment)

    assert len(assignments) == count


# ---------------------------------------------------------------------------
# Combination counting
# ---------------------------------------------------------------------------

def combination_count(n: int, r: int) -> int:
    """
    Count unordered selections of r objects from n objects.

    Every unordered selection corresponds to r! orderings, so the product
    principle for ordered selections can be divided by r!.
    """
    validate_non_negative_counts((n, r))

    if r > n:
        raise ValueError("r cannot be greater than n.")

    return comb(n, r)


def combination_examples() -> None:
    print("\n=== Unordered Selections ===")

    contributors = ["Asha", "Ben", "Chen", "Diya", "Eli"]

    groups = list(combinations(contributors, 3))
    expected = combination_count(len(contributors), 3)

    print("Three-person teams:")
    for group in groups:
        print("  ", group)

    print("Combination count:", expected)

    assert len(groups) == expected


# ---------------------------------------------------------------------------
# Counting strings with the multiplication principle
# ---------------------------------------------------------------------------

def identifier_count() -> None:
    print("\n=== Identifier Counting ===")

    # An identifier consists of:
    # uppercase letter + uppercase letter + digit + digit.
    #
    # Repetition is allowed, so each position has the same number of choices.
    letters = 26
    digits = 10

    total = product_rule(
        letters,
        letters,
        digits,
        digits,
    )

    print("Possible identifiers:", total)

    # If the first digit must be non-zero, the first digit has only nine
    # choices, changing the product.
    restricted_total = product_rule(
        letters,
        letters,
        9,
        digits,
    )

    print("Identifiers whose first digit is non-zero:", restricted_total)


# ---------------------------------------------------------------------------
# Password-style counting with restrictions
# ---------------------------------------------------------------------------

def restricted_code_count() -> None:
    print("\n=== Restricted Codes ===")

    # A four-digit code cannot start with zero.
    # Digits may repeat after the first position.
    first_digit = 9
    remaining_digits = 10

    total = product_rule(
        first_digit,
        remaining_digits,
        remaining_digits,
        remaining_digits,
    )

    print("Four-digit codes without a leading zero:", total)

    # If all four digits must be distinct, the available choices shrink:
    # 9 * 9 * 8 * 7.
    distinct_total = product_rule(
        9,
        9,
        8,
        7,
    )

    print("Four-digit codes without leading zero and without repetition:",
          distinct_total)


# ---------------------------------------------------------------------------
# Inclusion-exclusion
# ---------------------------------------------------------------------------

def inclusion_exclusion_two_sets(
    first_count: int,
    second_count: int,
    intersection_count: int,
) -> int:
    """
    Count the union of two overlapping sets.

    |A ∪ B| = |A| + |B| - |A ∩ B|
    """
    validate_non_negative_counts(
        (first_count, second_count, intersection_count)
    )

    if intersection_count > first_count:
        raise ValueError("Intersection cannot exceed the first set.")

    if intersection_count > second_count:
        raise ValueError("Intersection cannot exceed the second set.")

    return first_count + second_count - intersection_count


def inclusion_exclusion_example() -> None:
    print("\n=== Inclusion-Exclusion ===")

    # Repository users may have either Python knowledge or SQL knowledge.
    # Some users have both, so adding the two groups directly double-counts
    # the overlap.
    python_users = 70
    sql_users = 55
    both = 30

    total_users = inclusion_exclusion_two_sets(
        python_users,
        sql_users,
        both,
    )

    print("Users with Python or SQL knowledge:", total_users)


# ---------------------------------------------------------------------------
# Counting with conditional availability
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class ServicePlan:
    name: str
    regions: int
    environments: int


def service_plan_count(plans: Sequence[ServicePlan]) -> int:
    """
    Count deployment configurations when each plan has its own number of
    region/environment combinations.

    The outer choice uses the sum rule because exactly one service plan is
    selected. Each plan internally uses the product rule.
    """
    if not plans:
        return 0

    total = 0

    for plan in plans:
        if plan.regions < 0 or plan.environments < 0:
            raise ValueError("Plan choice counts cannot be negative.")

        total += product_rule(
            plan.regions,
            plan.environments,
        )

    return total


def service_plan_example() -> None:
    print("\n=== Conditional Product Counts ===")

    plans = [
        ServicePlan("Development", regions=3, environments=2),
        ServicePlan("Production", regions=5, environments=3),
        ServicePlan("Disaster Recovery", regions=2, environments=1),
    ]

    total = service_plan_count(plans)

    print("Total deployable configurations:", total)

    # Development contributes 3 * 2.
    # Production contributes 5 * 3.
    # Disaster Recovery contributes 2 * 1.
    # The alternatives are added because only one service plan is selected.


# ---------------------------------------------------------------------------
# Counting arrangements with repeated objects
# ---------------------------------------------------------------------------

def repeated_arrangement_count(items: Sequence[object]) -> int:
    """
    Count distinct arrangements when some items are repeated.

    Formula:
        n! / (m1! * m2! * ...)

    The division removes duplicate permutations caused by indistinguishable
    copies of the same value.
    """
    if not items:
        return 1

    frequencies: dict[object, int] = {}

    for item in items:
        frequencies[item] = frequencies.get(item, 0) + 1

    total = factorial(len(items))

    for frequency in frequencies.values():
        total //= factorial(frequency)

    return total


def repeated_arrangement_example() -> None:
    print("\n=== Repeated Elements ===")

    word = "LEVEL"
    count = repeated_arrangement_count(tuple(word))

    print(f"Distinct arrangements of {word!r}:", count)

    # L occurs twice, E occurs twice, V once:
    # 5! / (2! * 2!) = 30.
    assert count == 30


# ---------------------------------------------------------------------------
# Counting under a positional restriction
# ---------------------------------------------------------------------------

def arrangements_with_fixed_first_element(
    items: Sequence[str],
    fixed_first: str,
) -> int:
    """
    Count arrangements in which a particular element occupies the first
    position, assuming the element occurs exactly once.
    """
    if fixed_first not in items:
        raise ValueError("The fixed element is not present.")

    if items.count(fixed_first) != 1:
        raise ValueError(
            "This implementation requires the fixed element to occur once."
        )

    remaining = len(items) - 1
    return factorial(remaining)


def fixed_position_example() -> None:
    print("\n=== Fixed-Position Restriction ===")

    services = ["API", "Worker", "Database", "Cache"]

    count = arrangements_with_fixed_first_element(
        services,
        "API",
    )

    print("Service deployment orders with API first:", count)


# ---------------------------------------------------------------------------
# Counting paths in a small grid
# ---------------------------------------------------------------------------

def grid_path_count(right_moves: int, down_moves: int) -> int:
    """
    Count shortest paths through a rectangular grid.

    Every path contains the same total number of moves, but the positions of
    the right and down moves can vary.

    The number of paths equals C(R + D, R).
    """
    validate_non_negative_counts((right_moves, down_moves))

    return comb(
        right_moves + down_moves,
        right_moves,
    )


def grid_example() -> None:
    print("\n=== Grid Path Counting ===")

    right = 4
    down = 3

    paths = grid_path_count(right, down)

    print(
        f"Shortest paths requiring {right} right moves and "
        f"{down} down moves:",
        paths,
    )


# ---------------------------------------------------------------------------
# Counting probability outcomes
# ---------------------------------------------------------------------------

def probability_from_count(
    favorable: int,
    total: int,
) -> float:
    """
    Calculate probability when all outcomes are equally likely.

    Counting supplies the sample-space size and favorable-outcome count.
    """
    validate_non_negative_counts((favorable, total))

    if total == 0:
        raise ZeroDivisionError("The sample space cannot be empty.")

    if favorable > total:
        raise ValueError(
            "Favorable outcomes cannot exceed the total outcomes."
        )

    return favorable / total


def probability_example() -> None:
    print("\n=== Counting and Probability ===")

    # A two-digit number is selected uniformly from 10 through 99.
    # There are 90 total outcomes.
    total_numbers = 90

    # Multiples of ten are:
    # 10, 20, ..., 90 -> 9 outcomes.
    favorable = 9

    probability = probability_from_count(
        favorable,
        total_numbers,
    )

    print("Probability that the selected number is a multiple of ten:",
          probability)


# ---------------------------------------------------------------------------
# Brute-force verification versus mathematical counting
# ---------------------------------------------------------------------------

def verify_distinct_binary_strings(length: int) -> None:
    """
    Verify that binary strings of a given length have 2^length outcomes.

    This function deliberately enumerates the space only for small lengths.
    Enumeration becomes impractical as length grows, which demonstrates why
    counting principles are useful.
    """
    validate_non_negative_counts((length,))

    if length > 12:
        raise ValueError(
            "Enumeration is intentionally limited to length 12."
        )

    values = ["0", "1"]

    strings = [
        "".join(bits)
        for bits in product(values, repeat=length)
    ]

    mathematical_count = product_rule(2, *([2] * (length - 1)))
    direct_power_count = 2 ** length

    print(
        f"Binary strings of length {length}:",
        len(strings),
    )
    print("Product-rule count:", mathematical_count)
    print("Power-form count:", direct_power_count)

    assert len(strings) == mathematical_count == direct_power_count


# ---------------------------------------------------------------------------
# A practical decision engine for selecting a counting rule
# ---------------------------------------------------------------------------

def classify_counting_scenario(
    *,
    alternatives_are_exclusive: bool,
    stages_are_sequential: bool,
    choices_depend_on_previous: bool,
) -> str:
    """
    Provide a structural classification.

    This does not calculate a count. It identifies the mathematical mechanism
    suggested by the structure of the problem.
    """
    if alternatives_are_exclusive and not stages_are_sequential:
        return "Use the sum rule: count disjoint alternatives and add them."

    if stages_are_sequential:
        if choices_depend_on_previous:
            return (
                "Use the product principle with stage-specific counts; "
                "the number of choices changes after earlier selections."
            )

        return (
            "Use the product rule: multiply the number of choices at "
            "each stage."
        )

    return (
        "Inspect overlap or additional restrictions before choosing a "
        "counting formula."
    )


def decision_engine_examples() -> None:
    print("\n=== Counting-Rule Decision Engine ===")

    print(
        classify_counting_scenario(
            alternatives_are_exclusive=True,
            stages_are_sequential=False,
            choices_depend_on_previous=False,
        )
    )

    print(
        classify_counting_scenario(
            alternatives_are_exclusive=False,
            stages_are_sequential=True,
            choices_depend_on_previous=False,
        )
    )

    print(
        classify_counting_scenario(
            alternatives_are_exclusive=False,
            stages_are_sequential=True,
            choices_depend_on_previous=True,
        )
    )


# ---------------------------------------------------------------------------
# Test suite
# ---------------------------------------------------------------------------

def run_tests() -> None:
    print("\n=== Verification Tests ===")

    assert sum_rule(3, 4, 5) == 12
    assert product_rule(3, 4, 5) == 60
    assert permutation_count(5, 2) == 20
    assert combination_count(5, 2) == 10
    assert repeated_arrangement_count(tuple("LEVEL")) == 30
    assert grid_path_count(4, 3) == 35
    assert inclusion_exclusion_two_sets(70, 55, 30) == 95
    assert probability_from_count(9, 90) == 0.1

    try:
        product_rule(3, -1)
    except ValueError:
        pass
    else:
        raise AssertionError("Negative counts must be rejected.")

    try:
        permutation_count(3, 5)
    except ValueError:
        pass
    else:
        raise AssertionError("r > n must be rejected.")

    try:
        probability_from_count(10, 0)
    except ZeroDivisionError:
        pass
    else:
        raise AssertionError("An empty sample space must be rejected.")

    print("All verification tests passed.")


# ---------------------------------------------------------------------------
# Main demonstration
# ---------------------------------------------------------------------------

def main() -> None:
    print("=" * 72)
    print("COMBINATORICS FUNDAMENTALS")
    print("Counting Principles, Sum Rule, Product Rule")
    print("=" * 72)

    sum_rule_examples()
    product_rule_examples()
    sum_vs_product()
    enumerate_small_product_space()
    dependent_choice_example()
    permutation_examples()
    combination_examples()
    identifier_count()
    restricted_code_count()
    inclusion_exclusion_example()
    service_plan_example()
    repeated_arrangement_example()
    fixed_position_example()
    grid_example()
    probability_example()
    verify_distinct_binary_strings(4)
    decision_engine_examples()
    run_tests()

    print("\n=== Performance Observation ===")
    print(
        "Mathematical counting can compute huge spaces without enumerating "
        "every outcome. Enumeration is useful for verification on small "
        "spaces but grows rapidly as the number of choices increases."
    )


if __name__ == "__main__":
    main()
