"""
Inclusion-Exclusion Principle
A self-contained progression from overlapping-set counting to advanced
applications involving arbitrary set collections, divisibility, bitmasks,
probability, and derangements.

Run:
    python inclusion_exclusion.py
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from math import factorial, gcd
from itertools import combinations
from typing import Iterable, Sequence


# ---------------------------------------------------------------------------
# Fundamental set operations
# ---------------------------------------------------------------------------

def union_count_two_sets(
    total_a: int,
    total_b: int,
    intersection: int,
) -> int:
    """Count A ∪ B using |A ∪ B| = |A| + |B| - |A ∩ B|."""
    if min(total_a, total_b, intersection) < 0:
        raise ValueError("Set counts cannot be negative.")
    if intersection > min(total_a, total_b):
        raise ValueError("Intersection cannot exceed either set.")
    return total_a + total_b - intersection


def union_count_three_sets(
    a: int,
    b: int,
    c: int,
    ab: int,
    ac: int,
    bc: int,
    abc: int,
) -> int:
    """
    Apply:
        |A ∪ B ∪ C|
        = |A| + |B| + |C|
          - |A∩B| - |A∩C| - |B∩C|
          + |A∩B∩C|
    """
    values = [a, b, c, ab, ac, bc, abc]
    if any(value < 0 for value in values):
        raise ValueError("Set counts cannot be negative.")

    if ab > min(a, b) or ac > min(a, c) or bc > min(b, c):
        raise ValueError("Pairwise intersection is invalid.")

    if abc > min(ab, ac, bc):
        raise ValueError("Triple intersection cannot exceed a pairwise intersection.")

    return a + b + c - ab - ac - bc + abc


# ---------------------------------------------------------------------------
# Direct enumeration: a useful verification technique
# ---------------------------------------------------------------------------

def direct_union_count(sets: Sequence[set[int]]) -> int:
    """Count a union directly. Useful for validating formulas."""
    if not sets:
        return 0

    result: set[int] = set()
    for current in sets:
        result.update(current)
    return len(result)


def inclusion_exclusion_union_count(sets: Sequence[set[int]]) -> int:
    """
    General inclusion-exclusion:
        |U A_i| = sum over non-empty S of
                  (-1)^(|S|+1) |intersection(S)|

    This implementation is exponential in the number of sets because
    every non-empty subset of sets must be considered.
    """
    n = len(sets)
    if n == 0:
        return 0

    total = 0

    for mask in range(1, 1 << n):
        intersection: set[int] | None = None
        selected = 0

        for index in range(n):
            if mask & (1 << index):
                selected += 1
                if intersection is None:
                    intersection = set(sets[index])
                else:
                    intersection.intersection_update(sets[index])

        if selected % 2 == 1:
            total += len(intersection or set())
        else:
            total -= len(intersection or set())

    return total


# ---------------------------------------------------------------------------
# Exact-category counting
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class CategoryCounts:
    none: int
    only_a: int
    only_b: int
    only_c: int
    exactly_two: int
    exactly_three: int
    at_least_one: int


def three_set_categories(
    universe_size: int,
    a: int,
    b: int,
    c: int,
    ab: int,
    ac: int,
    bc: int,
    abc: int,
) -> CategoryCounts:
    """
    Convert intersection information into mutually exclusive categories.

    This is important because |A∪B∪C| answers "at least one", while many
    applications ask for "exactly one", "exactly two", or "all three".
    """
    at_least_one = union_count_three_sets(a, b, c, ab, ac, bc, abc)

    only_a = a - ab - ac + abc
    only_b = b - ab - bc + abc
    only_c = c - ac - bc + abc

    exactly_two = (ab - abc) + (ac - abc) + (bc - abc)
    exactly_three = abc
    none = universe_size - at_least_one

    values = [
        universe_size,
        only_a,
        only_b,
        only_c,
        exactly_two,
        exactly_three,
        none,
    ]

    if any(value < 0 for value in values):
        raise ValueError(
            "The supplied intersections do not describe a valid population."
        )

    return CategoryCounts(
        none=none,
        only_a=only_a,
        only_b=only_b,
        only_c=only_c,
        exactly_two=exactly_two,
        exactly_three=exactly_three,
        at_least_one=at_least_one,
    )


# ---------------------------------------------------------------------------
# Arbitrary finite sets
# ---------------------------------------------------------------------------

def intersection_size_for_mask(sets: Sequence[set[int]], mask: int) -> int:
    """Return the cardinality of the intersection selected by a bitmask."""
    intersection: set[int] | None = None

    for index, current in enumerate(sets):
        if mask & (1 << index):
            intersection = (
                set(current)
                if intersection is None
                else intersection.intersection(current)
            )

    return len(intersection or set())


def explain_general_inclusion_exclusion(sets: Sequence[set[int]]) -> dict:
    """
    Return every non-empty intersection term and its signed contribution.
    This makes the alternating-sign structure visible.
    """
    n = len(sets)
    terms = []

    for mask in range(1, 1 << n):
        selected = [i for i in range(n) if mask & (1 << i)]
        size = len(selected)
        intersection_size = intersection_size_for_mask(sets, mask)
        sign = 1 if size % 2 else -1

        terms.append(
            {
                "sets": tuple(selected),
                "intersection_size": intersection_size,
                "sign": sign,
                "contribution": sign * intersection_size,
            }
        )

    return {
        "terms": terms,
        "union_size": sum(term["contribution"] for term in terms),
    }


# ---------------------------------------------------------------------------
# Counting integers satisfying at least one divisibility condition
# ---------------------------------------------------------------------------

def count_multiples(limit: int, divisors: Sequence[int]) -> int:
    """
    Count integers in [1, limit] divisible by at least one divisor.

    For an intersection of divisibility sets, the relevant divisor is the
    least common multiple of all selected divisors.
    """
    if limit < 0:
        raise ValueError("Limit must be non-negative.")

    cleaned = sorted(set(divisors))
    if not cleaned:
        return 0
    if any(d <= 0 for d in cleaned):
        raise ValueError("Divisors must be positive.")

    def lcm(x: int, y: int) -> int:
        return x // gcd(x, y) * y

    total = 0

    for mask in range(1, 1 << len(cleaned)):
        common_multiple = 1
        selected_count = 0

        for index, divisor in enumerate(cleaned):
            if mask & (1 << index):
                selected_count += 1
                common_multiple = lcm(common_multiple, divisor)
                if common_multiple > limit:
                    break

        if common_multiple <= limit:
            contribution = limit // common_multiple
            total += contribution if selected_count % 2 else -contribution

    return total


# ---------------------------------------------------------------------------
# Coprime counting
# ---------------------------------------------------------------------------

def prime_factors(number: int) -> list[int]:
    """Return distinct prime factors using trial division."""
    if number <= 0:
        raise ValueError("Number must be positive.")

    factors = []
    candidate = 2
    remaining = number

    while candidate * candidate <= remaining:
        if remaining % candidate == 0:
            factors.append(candidate)
            while remaining % candidate == 0:
                remaining //= candidate
        candidate += 1 if candidate == 2 else 2

    if remaining > 1:
        factors.append(remaining)

    return factors


def count_coprime_up_to(n: int, base: int) -> int:
    """
    Count x in [1, n] such that gcd(x, base) = 1.

    Every non-coprime x is divisible by at least one distinct prime factor
    of base, so inclusion-exclusion counts and removes those overlaps.
    """
    if n < 0:
        raise ValueError("n must be non-negative.")
    if base <= 0:
        raise ValueError("base must be positive.")

    factors = prime_factors(base)
    result = n

    for mask in range(1, 1 << len(factors)):
        product = 1
        selected = 0

        for index, prime in enumerate(factors):
            if mask & (1 << index):
                product *= prime
                selected += 1

        term = n // product
        result += term if selected % 2 == 0 else -term

    return result


# ---------------------------------------------------------------------------
# Probability version of inclusion-exclusion
# ---------------------------------------------------------------------------

def probability_union_two(
    probability_a: Fraction,
    probability_b: Fraction,
    probability_ab: Fraction,
) -> Fraction:
    """P(A∪B) = P(A) + P(B) - P(A∩B)."""
    probabilities = [probability_a, probability_b, probability_ab]

    if any(p < 0 or p > 1 for p in probabilities):
        raise ValueError("Probabilities must lie between 0 and 1.")

    if probability_ab > min(probability_a, probability_b):
        raise ValueError("Intersection probability is too large.")

    return probability_a + probability_b - probability_ab


# ---------------------------------------------------------------------------
# Derangements: inclusion-exclusion over forbidden fixed positions
# ---------------------------------------------------------------------------

def derangements(n: int) -> int:
    """
    Count permutations of n objects in which no object remains in its
    original position.

    If A_i means "position i is fixed", then:
        D_n = n! - C(n,1)(n-1)! + C(n,2)(n-2)! - ... + (-1)^n
              C(n,n)0!
    """
    if n < 0:
        raise ValueError("n must be non-negative.")

    total = 0

    for k in range(n + 1):
        contribution = factorial(n) // factorial(k)
        total += contribution if k % 2 == 0 else -contribution

    return total


# ---------------------------------------------------------------------------
# Bitmask optimization for repeated membership queries
# ---------------------------------------------------------------------------

def union_count_with_bitmasks(universe_size: int, memberships: Sequence[int]) -> int:
    """
    Each integer in memberships represents one set as a bitmask.

    OR combines memberships because a bit is present if it belongs to at
    least one selected set.
    """
    if universe_size < 0:
        raise ValueError("Universe size cannot be negative.")

    allowed_mask = (1 << universe_size) - 1 if universe_size else 0
    combined = 0

    for membership in memberships:
        if membership < 0 or membership & ~allowed_mask:
            raise ValueError("A membership mask contains an invalid element.")
        combined |= membership

    return combined.bit_count()


# ---------------------------------------------------------------------------
# Practical case study: student technology adoption survey
# ---------------------------------------------------------------------------

def technology_adoption_case() -> dict:
    """
    A university surveys 1,000 students.

    A = students using Python
    B = students using JavaScript
    C = students using SQL

    The goal is to distinguish overlapping populations instead of simply
    adding the three totals.
    """
    total_students = 1000

    python_users = 620
    javascript_users = 540
    sql_users = 480

    python_javascript = 330
    python_sql = 280
    javascript_sql = 250
    all_three = 160

    categories = three_set_categories(
        total_students,
        python_users,
        javascript_users,
        sql_users,
        python_javascript,
        python_sql,
        javascript_sql,
        all_three,
    )

    return {
        "universe": total_students,
        "at_least_one": categories.at_least_one,
        "none": categories.none,
        "only_python": categories.only_a,
        "only_javascript": categories.only_b,
        "only_sql": categories.only_c,
        "exactly_two": categories.exactly_two,
        "all_three": categories.exactly_three,
    }


# ---------------------------------------------------------------------------
# Validation tests
# ---------------------------------------------------------------------------

def run_tests() -> None:
    assert union_count_two_sets(60, 45, 20) == 85

    assert union_count_three_sets(
        60, 50, 40,
        25, 20, 15,
        10,
    ) == 100

    sets = [
        {1, 2, 3, 4},
        {3, 4, 5, 6},
        {4, 6, 7},
    ]
    assert direct_union_count(sets) == 7
    assert inclusion_exclusion_union_count(sets) == 7

    assert count_multiples(100, [2, 3]) == 67
    assert count_multiples(100, [2, 3, 5]) == 74

    assert count_coprime_up_to(10, 6) == 3
    assert derangements(0) == 1
    assert derangements(1) == 0
    assert derangements(4) == 9

    assert probability_union_two(
        Fraction(1, 2),
        Fraction(1, 3),
        Fraction(1, 6),
    ) == Fraction(2, 3)


# ---------------------------------------------------------------------------
# Demonstration
# ---------------------------------------------------------------------------

def main() -> None:
    run_tests()

    print("INCLUSION-EXCLUSION PRINCIPLE")
    print("=" * 72)

    print("\nTwo overlapping sets")
    print("-" * 72)
    print("Students taking course A:", 60)
    print("Students taking course B:", 45)
    print("Students taking both:", 20)
    print("Students taking at least one:", union_count_two_sets(60, 45, 20))

    print("\nThree overlapping sets")
    print("-" * 72)
    result = union_count_three_sets(60, 50, 40, 25, 20, 15, 10)
    print("Students taking at least one:", result)

    print("\nExact categories")
    print("-" * 72)
    categories = three_set_categories(1000, 620, 540, 480, 330, 280, 250, 160)
    print(categories)

    print("\nGeneral set union")
    print("-" * 72)
    sets = [
        {1, 2, 3, 4},
        {3, 4, 5, 6},
        {4, 6, 7},
    ]
    explanation = explain_general_inclusion_exclusion(sets)
    print("Direct union count:", direct_union_count(sets))
    print("Inclusion-exclusion count:", explanation["union_size"])
    for term in explanation["terms"]:
        print(
            f"sets={term['sets']}, "
            f"intersection={term['intersection_size']}, "
            f"contribution={term['contribution']}"
        )

    print("\nDivisibility application")
    print("-" * 72)
    print(
        "Integers from 1 to 100 divisible by 2, 3, or 5:",
        count_multiples(100, [2, 3, 5]),
    )

    print("\nCoprimality application")
    print("-" * 72)
    print(
        "Integers in [1, 100] coprime with 30:",
        count_coprime_up_to(100, 30),
    )

    print("\nProbability application")
    print("-" * 72)
    p = probability_union_two(Fraction(1, 2), Fraction(1, 3), Fraction(1, 6))
    print("P(A or B):", p, f"= {float(p):.3f}")

    print("\nDerangements")
    print("-" * 72)
    for n in range(1, 8):
        print(f"D({n}) =", derangements(n))

    print("\nBitmask union")
    print("-" * 72)
    masks = [
        0b00101101,
        0b10000110,
        0b01010000,
    ]
    print("Distinct represented elements:", union_count_with_bitmasks(8, masks))

    print("\nTechnology adoption case study")
    print("-" * 72)
    for key, value in technology_adoption_case().items():
        print(f"{key}: {value}")

    print("\nComplexity note")
    print("-" * 72)
    print(
        "General inclusion-exclusion over n arbitrary sets can require "
        "2^n - 1 intersection terms. Specialized counting problems can "
        "often avoid this exponential cost by exploiting structure such "
        "as divisibility, prime factors, bitmasks, or dynamic programming."
    )


if __name__ == "__main__":
    main()
