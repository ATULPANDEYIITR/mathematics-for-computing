#!/usr/bin/env python3
"""
Combinations: binomial coefficients, combinations, and Pascal's triangle.

This self-contained program progresses from direct combinatorial reasoning to
efficient exact computation, Pascal's triangle construction, probability,
multiset-style selection, and validation of combinatorial identities.

The implementation intentionally avoids external packages.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from math import factorial, gcd
from typing import Iterable


# ---------------------------------------------------------------------------
# Fundamental definitions
# ---------------------------------------------------------------------------

def validate_n_k(n: int, k: int) -> None:
    """Validate parameters used by ordinary binomial coefficients."""
    if not isinstance(n, int) or not isinstance(k, int):
        raise TypeError("n and k must both be integers")
    if n < 0:
        raise ValueError("n must be non-negative")
    if k < 0 or k > n:
        raise ValueError("k must satisfy 0 <= k <= n")


def combination_factorial(n: int, k: int) -> int:
    """
    Compute C(n, k) using factorials.

    C(n,k) = n! / (k!(n-k)!).

    This form mirrors the mathematical definition but computes large
    intermediate factorials that are unnecessary when only one coefficient
    is required.
    """
    validate_n_k(n, k)
    return factorial(n) // (factorial(k) * factorial(n - k))


def combination_multiplicative(n: int, k: int) -> int:
    """
    Compute C(n,k) using the multiplicative recurrence.

    C(n,k) = product((n-i)/(i+1)) for i=0..k-1.

    Symmetry reduces the number of iterations because C(n,k)=C(n,n-k).
    """
    validate_n_k(n, k)

    k = min(k, n - k)
    result = 1

    for i in range(1, k + 1):
        # The division is exact at every step for this recurrence.
        result = result * (n - k + i) // i

    return result


def combination_recursive(n: int, k: int) -> int:
    """
    Direct recursive definition based on Pascal's identity.

    C(n,k) = C(n-1,k-1) + C(n-1,k).

    This is intentionally educational rather than efficient. The number of
    repeated subproblems grows rapidly without memoization.
    """
    validate_n_k(n, k)

    if k == 0 or k == n:
        return 1

    return combination_recursive(n - 1, k - 1) + combination_recursive(n - 1, k)


def combination_memoized(n: int, k: int, memo: dict[tuple[int, int], int] | None = None) -> int:
    """
    Compute C(n,k) recursively while caching previously computed values.

    This turns the exponential repeated work of naive recursion into a
    polynomial-size dynamic-programming computation.
    """
    validate_n_k(n, k)

    if memo is None:
        memo = {}

    if k > n - k:
        k = n - k

    if k == 0:
        return 1

    key = (n, k)
    if key not in memo:
        memo[key] = (
            combination_memoized(n - 1, k - 1, memo)
            + combination_memoized(n - 1, k, memo)
        )

    return memo[key]


# ---------------------------------------------------------------------------
# Pascal's triangle
# ---------------------------------------------------------------------------

def pascal_row(n: int) -> list[int]:
    """
    Return row n of Pascal's triangle.

    Row 0 is [1].
    Row n contains C(n,0), C(n,1), ..., C(n,n).
    """
    if not isinstance(n, int):
        raise TypeError("row index must be an integer")
    if n < 0:
        raise ValueError("row index must be non-negative")

    row = [1]

    for k in range(1, n + 1):
        row.append(row[-1] * (n - k + 1) // k)

    return row


def pascal_triangle(rows: int) -> list[list[int]]:
    """Build the first `rows` rows of Pascal's triangle."""
    if not isinstance(rows, int):
        raise TypeError("rows must be an integer")
    if rows < 0:
        raise ValueError("rows must be non-negative")

    triangle: list[list[int]] = []

    for n in range(rows):
        if n == 0:
            triangle.append([1])
            continue

        previous = triangle[-1]
        current = [1]

        for i in range(len(previous) - 1):
            current.append(previous[i] + previous[i + 1])

        current.append(1)
        triangle.append(current)

    return triangle


def print_pascal_triangle(rows: int) -> None:
    """Display Pascal's triangle in a centered text layout."""
    triangle = pascal_triangle(rows)

    if not triangle:
        return

    width = len(" ".join(map(str, triangle[-1])))

    for row in triangle:
        text = " ".join(map(str, row))
        print(text.center(width))


# ---------------------------------------------------------------------------
# Combinatorial selection
# ---------------------------------------------------------------------------

def combinations_without_replacement(items: Iterable, k: int) -> list[tuple]:
    """
    Generate all k-element subsets of a finite sequence.

    This is a direct implementation of the combination-generation process.
    Each generated tuple represents one distinct choice of positions.
    """
    values = list(items)

    if k < 0 or k > len(values):
        raise ValueError("k must satisfy 0 <= k <= number of items")

    result: list[tuple] = []
    current: list = []

    def backtrack(start: int) -> None:
        if len(current) == k:
            result.append(tuple(current))
            return

        remaining_needed = k - len(current)
        last_start = len(values) - remaining_needed

        for index in range(start, last_start + 1):
            current.append(values[index])
            backtrack(index + 1)
            current.pop()

    backtrack(0)
    return result


def count_team_selections(team_size: int, committee_size: int) -> int:
    """
    Count committees selected from a team.

    Order does not matter: selecting Alice then Bob is the same committee
    as selecting Bob then Alice.
    """
    return combination_multiplicative(team_size, committee_size)


# ---------------------------------------------------------------------------
# Probability using combinations
# ---------------------------------------------------------------------------

def probability_exact_successes(
    population_size: int,
    successes: int,
    draws: int,
    desired_successes: int,
) -> Fraction:
    """
    Hypergeometric probability.

    A sample of `draws` items is selected without replacement from a population
    containing `successes` target items. Return the probability that exactly
    `desired_successes` target items are selected.

    P(X=x) =
        C(successes,x) * C(population_size-successes, draws-x)
        ------------------------------------------------------------
                            C(population_size, draws)
    """
    if population_size < 0:
        raise ValueError("population_size must be non-negative")
    if not 0 <= successes <= population_size:
        raise ValueError("successes must be within the population")
    if not 0 <= draws <= population_size:
        raise ValueError("draws must be within the population")

    failures = population_size - successes

    if not 0 <= desired_successes <= successes:
        return Fraction(0, 1)

    non_success_draws = draws - desired_successes

    if not 0 <= non_success_draws <= failures:
        return Fraction(0, 1)

    numerator = (
        combination_multiplicative(successes, desired_successes)
        * combination_multiplicative(failures, non_success_draws)
    )
    denominator = combination_multiplicative(population_size, draws)

    return Fraction(numerator, denominator)


# ---------------------------------------------------------------------------
# Binomial theorem
# ---------------------------------------------------------------------------

def binomial_coefficients(n: int) -> list[int]:
    """Return all coefficients appearing in (a+b)^n."""
    return pascal_row(n)


def evaluate_binomial_expansion(a: int, b: int, n: int) -> int:
    """
    Evaluate (a+b)^n using the binomial theorem.

    (a+b)^n = sum C(n,k) a^(n-k) b^k
    """
    validate_n_k(n, 0)

    total = 0

    for k, coefficient in enumerate(binomial_coefficients(n)):
        total += coefficient * (a ** (n - k)) * (b ** k)

    return total


# ---------------------------------------------------------------------------
# Identity checks
# ---------------------------------------------------------------------------

def verify_symmetry(limit: int = 30) -> bool:
    """
    Verify C(n,k) = C(n,n-k) over a range of values.
    """
    for n in range(limit + 1):
        for k in range(n + 1):
            if combination_multiplicative(n, k) != combination_multiplicative(n, n - k):
                return False

    return True


def verify_pascal_identity(limit: int = 30) -> bool:
    """
    Verify C(n,k) = C(n-1,k-1) + C(n-1,k).

    Boundary coefficients C(n,0) and C(n,n) are both 1.
    """
    for n in range(1, limit + 1):
        for k in range(1, n):
            left = combination_multiplicative(n, k)
            right = (
                combination_multiplicative(n - 1, k - 1)
                + combination_multiplicative(n - 1, k)
            )

            if left != right:
                return False

    return True


def verify_row_sum_identity(limit: int = 30) -> bool:
    """
    Verify the identity:

        sum C(n,k) = 2^n

    which follows by setting a=b=1 in the binomial theorem.
    """
    for n in range(limit + 1):
        if sum(pascal_row(n)) != 2**n:
            return False

    return True


def verify_hockey_stick_identity(limit: int = 20) -> bool:
    """
    Verify the hockey-stick identity:

        C(r,r) + C(r+1,r) + ... + C(n,r) = C(n+1,r+1)
    """
    for r in range(limit + 1):
        for n in range(r, limit + 1):
            left = sum(combination_multiplicative(i, r) for i in range(r, n + 1))
            right = combination_multiplicative(n + 1, r + 1)

            if left != right:
                return False

    return True


# ---------------------------------------------------------------------------
# Multiset combinations
# ---------------------------------------------------------------------------

def combinations_with_repetition(n_types: int, k: int) -> int:
    """
    Count selections of k objects from n types when repetition is allowed.

    Stars-and-bars gives:

        C(n+k-1, k)

    This counts multisets, not ordered sequences.
    """
    if n_types <= 0:
        raise ValueError("n_types must be positive")
    if k < 0:
        raise ValueError("k must be non-negative")

    return combination_multiplicative(n_types + k - 1, k)


# ---------------------------------------------------------------------------
# Large values and modular computation
# ---------------------------------------------------------------------------

def combination_mod(n: int, k: int, modulus: int) -> int:
    """
    Compute C(n,k) modulo a modulus.

    For a general modulus, this implementation first computes the exact
    coefficient. That preserves correctness even when the modulus is
    composite, where modular division is not generally valid.

    The method is appropriate when exact C(n,k) remains manageable. For very
    large n with a prime modulus, specialized algorithms such as Lucas'
    theorem can avoid constructing the full integer.
    """
    validate_n_k(n, k)

    if modulus <= 0:
        raise ValueError("modulus must be positive")

    return combination_multiplicative(n, k) % modulus


# ---------------------------------------------------------------------------
# Pascal triangle as a dynamic-programming table
# ---------------------------------------------------------------------------

@dataclass
class PascalTable:
    """Store a reusable Pascal triangle for repeated coefficient queries."""

    rows: list[list[int]]

    @classmethod
    def build(cls, maximum_n: int) -> "PascalTable":
        return cls(pascal_triangle(maximum_n + 1))

    def coefficient(self, n: int, k: int) -> int:
        """Return a coefficient in O(1) table lookup time after construction."""
        validate_n_k(n, k)

        if n >= len(self.rows):
            raise IndexError(
                f"table contains rows 0 through {len(self.rows) - 1}"
            )

        return self.rows[n][k]


# ---------------------------------------------------------------------------
# Practical scenario
# ---------------------------------------------------------------------------

def project_selection_report(
    applicants: list[str],
    required_members: int,
) -> None:
    """
    Analyze a project-team selection problem.

    The names are only used to generate actual committees; the combinatorial
    count comes from the number of available applicants.
    """
    count = count_team_selections(len(applicants), required_members)

    print(f"Applicants: {', '.join(applicants)}")
    print(f"Required team size: {required_members}")
    print(f"Possible distinct teams: {count}")

    if len(applicants) <= 8:
        committees = combinations_without_replacement(
            applicants,
            required_members,
        )

        print("Generated committees:")
        for committee in committees:
            print("  " + ", ".join(committee))


# ---------------------------------------------------------------------------
# Demonstrations
# ---------------------------------------------------------------------------

def run_basic_examples() -> None:
    print("\n=== Fundamental binomial coefficients ===")

    examples = [(5, 2), (10, 3), (20, 10), (52, 5)]

    for n, k in examples:
        factorial_value = combination_factorial(n, k)
        multiplicative_value = combination_multiplicative(n, k)

        print(
            f"C({n}, {k}) = {multiplicative_value:,} "
            f"(factorial and multiplicative methods agree: "
            f"{factorial_value == multiplicative_value})"
        )

    print("\n=== Pascal's triangle ===")
    print_pascal_triangle(9)

    print("\n=== Direct recursive computation ===")
    print(f"C(6, 3) = {combination_recursive(6, 3)}")

    print("\n=== Memoized recursive computation ===")
    print(f"C(30, 15) = {combination_memoized(30, 15):,}")


def run_selection_examples() -> None:
    print("\n=== Combination generation ===")

    languages = ["Python", "JavaScript", "C++", "SQL", "Rust"]
    selections = combinations_without_replacement(languages, 3)

    print(f"Number generated: {len(selections)}")
    for selection in selections:
        print("  " + " + ".join(selection))

    print("\n=== Project committee scenario ===")
    project_selection_report(
        ["Aarav", "Meera", "Kabir", "Isha", "Rohan", "Nisha"],
        3,
    )


def run_probability_examples() -> None:
    print("\n=== Hypergeometric probability ===")

    # A system has 20 deployed components, 5 of which are known to be
    # high-priority. Four components are audited without replacement.
    probability = probability_exact_successes(
        population_size=20,
        successes=5,
        draws=4,
        desired_successes=2,
    )

    print("Probability of selecting exactly 2 high-priority components:")
    print(f"  {probability}")
    print(f"  ≈ {float(probability):.6f}")


def run_binomial_examples() -> None:
    print("\n=== Binomial theorem ===")

    a, b, n = 2, 3, 5
    direct = (a + b) ** n
    expansion = evaluate_binomial_expansion(a, b, n)

    print(f"({a} + {b})^{n} = {direct}")
    print(f"Binomial expansion evaluates to {expansion}")
    print(f"Coefficients for row {n}: {binomial_coefficients(n)}")


def run_advanced_examples() -> None:
    print("\n=== Combinations with repetition ===")

    # Six identical categories are not implied: there are three product types,
    # and four units may be selected with unlimited repetition.
    print(
        "Selections of 4 items from 3 types with repetition:",
        combinations_with_repetition(3, 4),
    )

    print("\n=== Reusable Pascal table ===")
    table = PascalTable.build(100)

    for n, k in [(50, 25), (75, 12), (100, 50)]:
        print(f"C({n}, {k}) = {table.coefficient(n, k):,}")

    print("\n=== Modular coefficient ===")
    print(f"C(100, 40) mod 1,000,003 = {combination_mod(100, 40, 1_000_003)}")


def run_identity_checks() -> None:
    print("\n=== Mathematical identity checks ===")

    checks = {
        "symmetry C(n,k) = C(n,n-k)": verify_symmetry(),
        "Pascal identity": verify_pascal_identity(),
        "row sum equals 2^n": verify_row_sum_identity(),
        "hockey-stick identity": verify_hockey_stick_identity(),
    }

    for name, result in checks.items():
        print(f"{name}: {'PASS' if result else 'FAIL'}")


def run_edge_case_examples() -> None:
    print("\n=== Boundary cases ===")

    cases = [(0, 0), (10, 0), (10, 10), (10, 1), (10, 9)]

    for n, k in cases:
        print(f"C({n}, {k}) = {combination_multiplicative(n, k)}")

    print("\n=== Invalid input handling ===")

    invalid_cases = [(-1, 0), (5, -1), (5, 7)]

    for n, k in invalid_cases:
        try:
            combination_multiplicative(n, k)
        except (TypeError, ValueError) as error:
            print(f"C({n}, {k}) rejected: {error}")


def main() -> None:
    print("COMBINATIONS AND BINOMIAL COEFFICIENTS")
    print("=====================================")

    run_basic_examples()
    run_selection_examples()
    run_probability_examples()
    run_binomial_examples()
    run_advanced_examples()
    run_identity_checks()
    run_edge_case_examples()

    print("\n=== Complexity notes ===")
    print("Factorial formulation: conceptually simple, but creates large factorials.")
    print("Multiplicative formulation: O(min(k, n-k)) iterations.")
    print("Pascal table through row n: O(n^2) time and O(n^2) memory.")
    print("A single stored Pascal coefficient can then be retrieved in O(1) time.")
    print("Generated combinations require output-sensitive work because every result must be emitted.")


if __name__ == "__main__":
    main()
