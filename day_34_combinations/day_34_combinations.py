"""
Combinations: binomial coefficients, combinations, and Pascal's triangle.

This executable script progresses from direct counting to exact arithmetic,
Pascal's triangle generation, dynamic programming, combinatorial identities,
and practical applications such as subset selection and probability.

Run:
    python combinations.py
"""

from __future__ import annotations

from collections import Counter
from math import factorial, gcd
from typing import Iterable


def combination_factorial(n: int, r: int) -> int:
    """Compute C(n, r) directly from factorials."""
    validate_n_r(n, r)
    if r > n - r:
        r = n - r
    return factorial(n) // (factorial(r) * factorial(n - r))


def validate_n_r(n: int, r: int) -> None:
    """Reject values that do not represent a valid binomial coefficient."""
    if not isinstance(n, int) or isinstance(n, bool):
        raise TypeError("n must be an integer")
    if not isinstance(r, int) or isinstance(r, bool):
        raise TypeError("r must be an integer")
    if n < 0:
        raise ValueError("n must be non-negative")
    if r < 0 or r > n:
        raise ValueError("r must satisfy 0 <= r <= n")


def combination_multiplicative(n: int, r: int) -> int:
    """
    Compute C(n, r) without constructing large factorials.

    The recurrence
        C(n, r) = product((n-r+i)/i), i=1..r
    is evaluated exactly by dividing at every step.
    """
    validate_n_r(n, r)
    r = min(r, n - r)

    result = 1
    for i in range(1, r + 1):
        result = result * (n - r + i) // i
    return result


def combination_gcd_reduced(n: int, r: int) -> int:
    """
    Compute C(n, r) while reducing numerator and denominator factors.

    This illustrates how exact integer arithmetic can avoid unnecessarily
    large intermediate products.
    """
    validate_n_r(n, r)
    r = min(r, n - r)

    numerator = list(range(n - r + 1, n + 1))
    denominator = list(range(1, r + 1))

    for i, d in enumerate(denominator):
        if d == 1:
            continue

        remaining = d
        for j in range(len(numerator)):
            g = gcd(remaining, numerator[j])
            if g > 1:
                remaining //= g
                numerator[j] //= g
                if remaining == 1:
                    break

        if remaining != 1:
            raise ArithmeticError("Exact factor reduction failed")

    result = 1
    for value in numerator:
        result *= value
    return result


def combination_recursive(n: int, r: int, memo: dict[tuple[int, int], int] | None = None) -> int:
    """
    Demonstrate Pascal's recurrence:

        C(n, r) = C(n-1, r-1) + C(n-1, r)

    Memoization prevents the exponential repetition of the naive recursion.
    """
    validate_n_r(n, r)

    if memo is None:
        memo = {}

    r = min(r, n - r)
    if r == 0:
        return 1

    key = (n, r)
    if key in memo:
        return memo[key]

    memo[key] = combination_recursive(n - 1, r - 1, memo) + combination_recursive(
        n - 1, r, memo
    )
    return memo[key]


def pascal_triangle(rows: int) -> list[list[int]]:
    """Build Pascal's triangle using the recurrence between adjacent rows."""
    if not isinstance(rows, int) or isinstance(rows, bool):
        raise TypeError("rows must be an integer")
    if rows < 0:
        raise ValueError("rows must be non-negative")

    triangle: list[list[int]] = []

    for row_index in range(rows):
        if row_index == 0:
            triangle.append([1])
            continue

        previous = triangle[-1]
        row = [1]

        for index in range(len(previous) - 1):
            row.append(previous[index] + previous[index + 1])

        row.append(1)
        triangle.append(row)

    return triangle


def pascal_row(n: int) -> list[int]:
    """Return row n of Pascal's triangle, where row 0 is [1]."""
    if n < 0:
        raise ValueError("row index must be non-negative")

    row = [1]
    for k in range(1, n + 1):
        row.append(row[-1] * (n - k + 1) // k)
    return row


def format_triangle(triangle: list[list[int]]) -> str:
    """Format a triangle for readable terminal output."""
    if not triangle:
        return ""

    width = len(" ".join(map(str, triangle[-1])))
    lines = []

    for row in triangle:
        content = " ".join(map(str, row))
        lines.append(content.center(width))

    return "\n".join(lines)


def verify_core_identities(n: int) -> dict[str, bool]:
    """
    Verify important binomial identities.

    Symmetry:
        C(n,r) = C(n,n-r)

    Row sum:
        sum C(n,r) = 2^n

    Pascal:
        C(n,r) = C(n-1,r-1) + C(n-1,r)
    """
    if n < 1:
        raise ValueError("n must be at least 1")

    symmetry = all(
        combination_multiplicative(n, r)
        == combination_multiplicative(n, n - r)
        for r in range(n + 1)
    )

    row_sum = sum(combination_multiplicative(n, r) for r in range(n + 1)) == 2**n

    pascal = all(
        combination_multiplicative(n, r)
        == combination_multiplicative(n - 1, r - 1)
        + combination_multiplicative(n - 1, r)
        for r in range(1, n)
    )

    return {
        "symmetry": symmetry,
        "row_sum": row_sum,
        "pascal_recurrence": pascal,
    }


def multinomial_via_sequential_selection(groups: Iterable[int]) -> int:
    """
    Count arrangements of a partition using successive combinations.

    For group sizes a,b,c,..., this computes:
        (a+b+c+...)! / (a!b!c!...)
    by choosing each group from the remaining positions.
    """
    sizes = list(groups)

    if not sizes:
        return 1
    if any(not isinstance(size, int) or size < 0 for size in sizes):
        raise ValueError("group sizes must be non-negative integers")

    remaining = sum(sizes)
    result = 1

    for size in sizes:
        result *= combination_multiplicative(remaining, size)
        remaining -= size

    return result


def choose_subsets(items: list[str], r: int) -> list[tuple[str, ...]]:
    """
    Enumerate actual r-element subsets.

    The count of the generated result must equal C(n,r).
    """
    validate_n_r(len(items), r)

    result: list[tuple[str, ...]] = []
    current: list[str] = []

    def backtrack(start: int) -> None:
        if len(current) == r:
            result.append(tuple(current))
            return

        needed = r - len(current)
        last_start = len(items) - needed

        for index in range(start, last_start + 1):
            current.append(items[index])
            backtrack(index + 1)
            current.pop()

    if r == 0:
        return [()]

    backtrack(0)
    return result


def probability_exactly_k_successes(trials: int, successes: int, probability: float) -> float:
    """
    Binomial probability:
        P(X=k) = C(n,k) p^k (1-p)^(n-k)
    """
    validate_n_r(trials, successes)

    if not 0 <= probability <= 1:
        raise ValueError("probability must be between 0 and 1")

    coefficient = combination_multiplicative(trials, successes)
    return coefficient * probability**successes * (1 - probability) ** (trials - successes)


def demonstrate_large_value() -> None:
    """Show that Python's arbitrary-precision integers preserve exact results."""
    n = 100
    r = 50
    value = combination_multiplicative(n, r)

    print("Large exact coefficient")
    print(f"C({n}, {r}) = {value}")
    print(f"Number of decimal digits: {len(str(value))}")


def demonstrate_subset_selection() -> None:
    """Apply combinations to selecting reviewers for a pull request."""
    reviewers = ["Asha", "Bharat", "Chen", "Divya", "Ethan", "Fatima"]
    required = 3

    subsets = choose_subsets(reviewers, required)

    print("\nReviewer committee selection")
    print(f"Available reviewers: {len(reviewers)}")
    print(f"Required reviewers: {required}")
    print(f"Possible committees: {len(subsets)}")
    print(f"Verified by C(n,r): {combination_multiplicative(len(reviewers), required)}")

    for committee in subsets[:5]:
        print("  ", ", ".join(committee))


def demonstrate_probability() -> None:
    """Use a binomial coefficient in a reliability-style probability model."""
    trials = 10
    successes = 7
    probability = 0.8

    exact = probability_exactly_k_successes(trials, successes, probability)

    print("\nBinomial probability")
    print(f"Trials: {trials}")
    print(f"Required successes: {successes}")
    print(f"Single-trial success probability: {probability:.2f}")
    print(f"P(X={successes}) = {exact:.8f}")


def demonstrate_edge_cases() -> None:
    """Exercise boundary values and show controlled validation failures."""
    print("\nBoundary cases")
    print("C(0,0) =", combination_multiplicative(0, 0))
    print("C(10,0) =", combination_multiplicative(10, 0))
    print("C(10,10) =", combination_multiplicative(10, 10))
    print("C(10,3) =", combination_multiplicative(10, 3))
    print("C(10,7) =", combination_multiplicative(10, 7))

    invalid_values = [(-1, 0), (5, -1), (5, 6)]

    for n, r in invalid_values:
        try:
            combination_multiplicative(n, r)
        except (TypeError, ValueError) as error:
            print(f"Rejected C({n},{r}): {error}")


def run_self_tests() -> None:
    """Verify the implementations against mathematical invariants."""
    for n in range(21):
        for r in range(n + 1):
            a = combination_factorial(n, r)
            b = combination_multiplicative(n, r)
            c = combination_gcd_reduced(n, r)
            d = combination_recursive(n, r)

            assert a == b == c == d
            assert pascal_row(n)[r] == a

    for rows in range(1, 15):
        triangle = pascal_triangle(rows)
        assert triangle[-1] == pascal_row(rows - 1)

    assert multinomial_via_sequential_selection([2, 3, 4]) == (
        factorial(9) // (factorial(2) * factorial(3) * factorial(4))
    )

    print("\nSelf-tests: all passed")


def main() -> None:
    print("COMBINATIONS, BINOMIAL COEFFICIENTS, AND PASCAL'S TRIANGLE")
    print("=" * 62)

    print("\nDirect coefficient calculations")
    for n, r in [(5, 2), (10, 4), (20, 10)]:
        print(
            f"C({n},{r}) = "
            f"{combination_factorial(n, r)} "
            f"(multiplicative: {combination_multiplicative(n, r)})"
        )

    print("\nPascal's triangle")
    triangle = pascal_triangle(9)
    print(format_triangle(triangle))

    print("\nSelected Pascal row")
    n = 8
    print(f"Row {n}: {pascal_row(n)}")

    print("\nMathematical identities")
    for identity, result in verify_core_identities(12).items():
        print(f"{identity}: {result}")

    print("\nMultinomial counting through combinations")
    groups = [2, 3, 4]
    print(f"Group sizes: {groups}")
    print("Distinct arrangements:", multinomial_via_sequential_selection(groups))

    demonstrate_subset_selection()
    demonstrate_probability()
    demonstrate_large_value()
    demonstrate_edge_cases()
    run_self_tests()


if __name__ == "__main__":
    main()
