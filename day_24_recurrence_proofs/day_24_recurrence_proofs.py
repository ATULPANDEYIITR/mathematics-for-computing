"""
Recurrence Proofs
=================

Topic:
    Recursive definitions, recurrence relations, and induction-based recurrence proofs.

This file is a standalone study program. It combines executable examples with
comments that explain the mathematical ideas represented by the programs.

The central ideas are:

1. Recursive definitions describe objects in terms of smaller instances.
2. Recurrence relations describe sequences or computational costs recursively.
3. Base cases terminate recursive definitions.
4. Recursive algorithms often produce recurrences for their running time.
5. Mathematical induction can prove identities involving recursively defined
   sequences and can verify bounds on recurrence-defined running times.
6. Strong induction is useful when a result depends on several earlier cases.
7. Structural induction is the natural proof technique for recursively defined
   structures such as trees and expressions.
8. Substitution, recursion-tree reasoning, the iteration method, and the
   Master Theorem are common tools for solving or bounding recurrences.

The program uses only the Python standard library.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from math import ceil, log2
from typing import Callable, Iterable, Optional


# ---------------------------------------------------------------------------
# Section 1: Recursive definitions
# ---------------------------------------------------------------------------

def factorial(n: int) -> int:
    """
    Recursive definition of factorial.

    Mathematical definition:
        0! = 1
        n! = n * (n - 1)! for n >= 1

    The Python function follows the same definition directly.
    """
    if n < 0:
        raise ValueError("factorial is defined here only for n >= 0")

    # Base case.
    if n == 0:
        return 1

    # Recursive case.
    return n * factorial(n - 1)


def fibonacci_recursive(n: int) -> int:
    """
    Naive recursive Fibonacci implementation.

    Definition:
        F(0) = 0
        F(1) = 1
        F(n) = F(n - 1) + F(n - 2), n >= 2

    This implementation intentionally demonstrates the direct recursive
    definition. It is computationally inefficient because the same subproblems
    are evaluated repeatedly.
    """
    if n < 0:
        raise ValueError("Fibonacci index must be non-negative")

    if n == 0:
        return 0
    if n == 1:
        return 1

    return fibonacci_recursive(n - 1) + fibonacci_recursive(n - 2)


@lru_cache(maxsize=None)
def fibonacci_memoized(n: int) -> int:
    """
    Fibonacci using memoization.

    The mathematical recurrence is unchanged. Only the implementation strategy
    changes: once F(k) has been computed, its value is cached.
    """
    if n < 0:
        raise ValueError("Fibonacci index must be non-negative")

    if n < 2:
        return n

    return fibonacci_memoized(n - 1) + fibonacci_memoized(n - 2)


def fibonacci_iterative(n: int) -> int:
    """
    Iterative Fibonacci.

    This has the same mathematical recurrence but avoids recursion and stores
    only the two most recent values.
    """
    if n < 0:
        raise ValueError("Fibonacci index must be non-negative")

    previous, current = 0, 1

    for _ in range(n):
        previous, current = current, previous + current

    return previous


# ---------------------------------------------------------------------------
# Section 2: A recursive sequence with a simple closed form
# ---------------------------------------------------------------------------

def arithmetic_sequence_recursive(n: int, first: int = 3, difference: int = 5) -> int:
    """
    Recursive arithmetic sequence.

        a(0) = first
        a(n) = a(n - 1) + difference

    Closed form:
        a(n) = first + n * difference
    """
    if n < 0:
        raise ValueError("n must be non-negative")

    if n == 0:
        return first

    return arithmetic_sequence_recursive(n - 1, first, difference)


def arithmetic_sequence_closed_form(
    n: int, first: int = 3, difference: int = 5
) -> int:
    """Closed-form version of the same sequence."""
    if n < 0:
        raise ValueError("n must be non-negative")

    return first + n * difference


def verify_arithmetic_identity(limit: int = 20) -> bool:
    """
    Computationally checks an identity over a finite range.

    This is useful experimentation, but it is NOT a mathematical proof for
    infinitely many n. Induction is what establishes the general statement.
    """
    for n in range(limit + 1):
        if arithmetic_sequence_recursive(n) != arithmetic_sequence_closed_form(n):
            return False
    return True


# ---------------------------------------------------------------------------
# Section 3: Geometric recurrence
# ---------------------------------------------------------------------------

def power_of_two_recursive(n: int) -> int:
    """
    Recurrence:
        p(0) = 1
        p(n) = 2 * p(n - 1)

    Therefore:
        p(n) = 2^n
    """
    if n < 0:
        raise ValueError("n must be non-negative")

    if n == 0:
        return 1

    return 2 * power_of_two_recursive(n - 1)


def power_of_two_closed_form(n: int) -> int:
    """Closed form corresponding to the recurrence above."""
    if n < 0:
        raise ValueError("n must be non-negative")

    return 2**n


# ---------------------------------------------------------------------------
# Section 4: Linear recurrence
# ---------------------------------------------------------------------------

def triangular_recursive(n: int) -> int:
    """
    Recursive triangular-number definition:

        T(0) = 0
        T(n) = T(n - 1) + n

    Closed form:
        T(n) = n(n + 1) / 2
    """
    if n < 0:
        raise ValueError("n must be non-negative")

    if n == 0:
        return 0

    return triangular_recursive(n - 1) + n


def triangular_closed_form(n: int) -> int:
    """Closed form for triangular numbers."""
    if n < 0:
        raise ValueError("n must be non-negative")

    return n * (n + 1) // 2


# ---------------------------------------------------------------------------
# Section 5: Towers of Hanoi and its recurrence
# ---------------------------------------------------------------------------

def hanoi_move_count(n: int) -> int:
    """
    Towers of Hanoi recurrence:

        H(0) = 0
        H(n) = 2H(n - 1) + 1

    Closed form:
        H(n) = 2^n - 1
    """
    if n < 0:
        raise ValueError("number of disks must be non-negative")

    if n == 0:
        return 0

    return 2 * hanoi_move_count(n - 1) + 1


def hanoi_closed_form(n: int) -> int:
    """Closed form for the Towers of Hanoi move count."""
    if n < 0:
        raise ValueError("number of disks must be non-negative")

    return 2**n - 1


# ---------------------------------------------------------------------------
# Section 6: Recurrence expansion
# ---------------------------------------------------------------------------

def expand_recurrence_t_minus_one_plus_n(
    n: int,
    base_value: int = 0,
) -> list[str]:
    """
    Produce symbolic expansion steps for

        T(n) = T(n - 1) + n
        T(0) = base_value

    The result illustrates the iteration method:
        T(n)
        = T(n - 1) + n
        = T(n - 2) + (n - 1) + n
        ...
        = T(0) + 1 + 2 + ... + n
    """
    if n < 0:
        raise ValueError("n must be non-negative")

    lines = [f"T({n})"]

    if n == 0:
        lines.append(f"= {base_value}")
        return lines

    for current in range(n, 0, -1):
        remaining = current - 1

        if remaining == 0:
            lines.append(f"= T(0) + {current}")
        else:
            terms = " + ".join(str(value) for value in range(remaining + 1, n + 1))
            lines.append(f"= T({remaining}) + {terms}")

    lines.append(f"= {base_value} + (1 + 2 + ... + {n})")
    lines.append(f"= {base_value} + {n}({n} + 1)/2")

    return lines


# ---------------------------------------------------------------------------
# Section 7: Recursion tree cost
# ---------------------------------------------------------------------------

def recurrence_tree_cost(
    n: int,
    branching_factor: int = 2,
    cost_per_node: int = 1,
    shrink_factor: int = 2,
) -> int:
    """
    Compute a small recurrence-tree example directly.

    Recurrence:
        T(n) = b T(floor(n / s)) + c
        T(1) = c

    This function is intended for demonstration rather than for large n.
    """
    if n <= 1:
        return cost_per_node

    if branching_factor < 1:
        raise ValueError("branching_factor must be positive")

    if shrink_factor < 2:
        raise ValueError("shrink_factor must be at least 2")

    smaller = n // shrink_factor

    if smaller < 1:
        smaller = 1

    return (
        branching_factor
        * recurrence_tree_cost(
            smaller,
            branching_factor,
            cost_per_node,
            shrink_factor,
        )
        + cost_per_node
    )


# ---------------------------------------------------------------------------
# Section 8: Binary search recurrence
# ---------------------------------------------------------------------------

def binary_search(values: list[int], target: int) -> int:
    """
    Iterative binary search.

    Its recurrence for comparisons is approximately:

        T(n) = T(n / 2) + O(1)

    leading to:
        T(n) = O(log n)

    The iterative implementation avoids consuming call-stack frames.
    """
    left = 0
    right = len(values) - 1

    while left <= right:
        middle = left + (right - left) // 2

        if values[middle] == target:
            return middle

        if values[middle] < target:
            left = middle + 1
        else:
            right = middle - 1

    return -1


def binary_search_recursive(
    values: list[int],
    target: int,
    left: int = 0,
    right: Optional[int] = None,
) -> int:
    """
    Recursive binary search.

    Recursive structure:
        T(n) = T(n/2) + O(1)
    """
    if right is None:
        right = len(values) - 1

    if left > right:
        return -1

    middle = left + (right - left) // 2

    if values[middle] == target:
        return middle

    if values[middle] < target:
        return binary_search_recursive(values, target, middle + 1, right)

    return binary_search_recursive(values, target, left, middle - 1)


# ---------------------------------------------------------------------------
# Section 9: Merge sort recurrence
# ---------------------------------------------------------------------------

def merge(left: list[int], right: list[int]) -> list[int]:
    """Merge two sorted lists in linear time."""
    result: list[int] = []
    left_index = 0
    right_index = 0

    while left_index < len(left) and right_index < len(right):
        if left[left_index] <= right[right_index]:
            result.append(left[left_index])
            left_index += 1
        else:
            result.append(right[right_index])
            right_index += 1

    result.extend(left[left_index:])
    result.extend(right[right_index:])
    return result


def merge_sort(values: list[int]) -> list[int]:
    """
    Merge sort.

    Recurrence:
        T(n) = 2T(n/2) + O(n)

    This solves to:
        T(n) = O(n log n)

    The recursive algorithm also requires O(n) auxiliary storage for merging.
    """
    if len(values) <= 1:
        return values.copy()

    middle = len(values) // 2
    left = merge_sort(values[:middle])
    right = merge_sort(values[middle:])

    return merge(left, right)


# ---------------------------------------------------------------------------
# Section 10: Divide-and-conquer recurrence with uneven partitions
# ---------------------------------------------------------------------------

def quicksort_partition(values: list[int], low: int, high: int) -> int:
    """Partition around the last element as pivot."""
    pivot = values[high]
    smaller_index = low - 1

    for index in range(low, high):
        if values[index] <= pivot:
            smaller_index += 1
            values[smaller_index], values[index] = (
                values[index],
                values[smaller_index],
            )

    values[smaller_index + 1], values[high] = (
        values[high],
        values[smaller_index + 1],
    )

    return smaller_index + 1


def quicksort(values: list[int]) -> list[int]:
    """
    Quicksort implementation.

    Best/typical balanced recurrence:
        T(n) = 2T(n/2) + O(n)
        => O(n log n)

    Worst-case recurrence:
        T(n) = T(n - 1) + O(n)
        => O(n^2)

    The recurrence therefore depends strongly on the partition behavior.
    """
    result = values.copy()

    def sort(low: int, high: int) -> None:
        if low >= high:
            return

        pivot_index = quicksort_partition(result, low, high)
        sort(low, pivot_index - 1)
        sort(pivot_index + 1, high)

    sort(0, len(result) - 1)
    return result


# ---------------------------------------------------------------------------
# Section 11: Recurrence classes
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class RecurrenceExample:
    """
    Data model for a recurrence relation used in the demonstrations.

    name:
        Human-readable identifier.

    equation:
        Mathematical recurrence written as plain text.

    base_case:
        Base-case description.

    asymptotic:
        Known asymptotic classification.
    """

    name: str
    equation: str
    base_case: str
    asymptotic: str


RECURRENCE_CATALOG = [
    RecurrenceExample(
        "Factorial",
        "T(n) = T(n - 1) + O(1)",
        "T(0) = O(1)",
        "O(n)",
    ),
    RecurrenceExample(
        "Binary search",
        "T(n) = T(n/2) + O(1)",
        "T(1) = O(1)",
        "O(log n)",
    ),
    RecurrenceExample(
        "Merge sort",
        "T(n) = 2T(n/2) + O(n)",
        "T(1) = O(1)",
        "O(n log n)",
    ),
    RecurrenceExample(
        "Naive Fibonacci",
        "T(n) = T(n-1) + T(n-2) + O(1)",
        "T(0), T(1) = O(1)",
        "Exponential",
    ),
    RecurrenceExample(
        "Towers of Hanoi",
        "H(n) = 2H(n-1) + 1",
        "H(0) = 0",
        "Theta(2^n)",
    ),
]


# ---------------------------------------------------------------------------
# Section 12: Mathematical induction as an executable proof framework
# ---------------------------------------------------------------------------

@dataclass
class InductionProof:
    """
    Represents the logical structure of a proof by mathematical induction.

    The program cannot replace a formal proof. Instead, this class makes the
    logical components explicit and can mechanically test selected predicates.
    """

    proposition_name: str
    base_case_n: int
    induction_start: int
    predicate: Callable[[int], bool]
    recursive_verification: Callable[[int], bool]

    def verify_base_case(self) -> bool:
        """Check the proposition at the base case."""
        return self.predicate(self.base_case_n)

    def verify_inductive_steps(self, limit: int) -> bool:
        """
        Check P(n) -> P(n+1) computationally over a finite range.

        This is evidence about the implementation, not a replacement for the
        logical argument that the implication holds for every valid n.
        """
        if limit < self.induction_start:
            return True

        for n in range(self.induction_start, limit + 1):
            if self.predicate(n) and not self.recursive_verification(n):
                return False

        return True


def prove_triangular_formula(limit: int = 100) -> InductionProof:
    """
    Build an induction-proof model for:

        T(n) = n(n+1)/2
    """

    def proposition(n: int) -> bool:
        return triangular_recursive(n) == n * (n + 1) // 2

    def inductive_step(n: int) -> bool:
        """
        Assume T(n) = n(n+1)/2.

        Then:
            T(n+1)
              = T(n) + (n+1)
              = n(n+1)/2 + (n+1)
              = (n+1)(n+2)/2

        The code verifies the resulting equality for this n.
        """
        assumed_value = n * (n + 1) // 2
        derived_value = assumed_value + (n + 1)
        expected_next_value = (n + 1) * (n + 2) // 2
        return derived_value == expected_next_value

    proof = InductionProof(
        proposition_name="T(n) = n(n+1)/2",
        base_case_n=0,
        induction_start=0,
        predicate=proposition,
        recursive_verification=inductive_step,
    )

    assert proof.verify_base_case()
    assert proof.verify_inductive_steps(limit)
    return proof


# ---------------------------------------------------------------------------
# Section 13: Induction proof of a recurrence-defined sequence
# ---------------------------------------------------------------------------

def verify_power_of_two_induction(limit: int = 30) -> bool:
    """
    Verify the structure of the proof:

        P(n): p(n) = 2^n

    Base case:
        p(0) = 1 = 2^0

    Inductive step:
        Assume p(n) = 2^n.
        Since p(n+1) = 2p(n),
        p(n+1) = 2 * 2^n = 2^(n+1).
    """
    if not (power_of_two_recursive(0) == 2**0):
        return False

    for n in range(limit):
        assumed = power_of_two_recursive(n)
        derived_next = 2 * assumed
        expected_next = 2 ** (n + 1)

        if derived_next != expected_next:
            return False

    return True


# ---------------------------------------------------------------------------
# Section 14: Strong induction example
# ---------------------------------------------------------------------------

def can_be_composed_from_two_and_three(n: int) -> bool:
    """
    Determine whether n can be represented as 2a + 3b for non-negative
    integers a and b.

    This is an example where strong induction is natural because the proof can
    use more than one earlier value.

    For n >= 2, one possible recursive characterization is:

        P(n) = P(n-2) OR P(n-3)

    when the referenced values are in the valid domain.
    """
    if n < 0:
        return False

    @lru_cache(maxsize=None)
    def solve(value: int) -> bool:
        if value == 0:
            return True
        if value < 0:
            return False

        return solve(value - 2) or solve(value - 3)

    return solve(n)


def verify_strong_induction_composition(limit: int = 30) -> bool:
    """
    Verify computationally that every n >= 2 can be composed from 2s and 3s.

    A standard proof can establish the stronger claim using base cases such as
    2, 3, and 4 and an induction step that subtracts 2.

    This implementation checks the resulting claim.
    """
    if limit < 4:
        return True

    for n in range(2, limit + 1):
        if not can_be_composed_from_two_and_three(n):
            return False

    return True


# ---------------------------------------------------------------------------
# Section 15: Structural induction over binary trees
# ---------------------------------------------------------------------------

@dataclass
class TreeNode:
    """A simple binary-tree node for structural-induction demonstrations."""

    value: int
    left: Optional["TreeNode"] = None
    right: Optional["TreeNode"] = None


def tree_size(node: Optional[TreeNode]) -> int:
    """
    Recursive definition of tree size:

        size(empty) = 0
        size(node) = 1 + size(left) + size(right)
    """
    if node is None:
        return 0

    return 1 + tree_size(node.left) + tree_size(node.right)


def tree_height(node: Optional[TreeNode]) -> int:
    """
    Recursive tree-height definition.

        height(empty) = 0
        height(node) = 1 + max(height(left), height(right))
    """
    if node is None:
        return 0

    return 1 + max(tree_height(node.left), tree_height(node.right))


def count_leaves(node: Optional[TreeNode]) -> int:
    """Count leaves using the recursive structure of the tree."""
    if node is None:
        return 0

    if node.left is None and node.right is None:
        return 1

    return count_leaves(node.left) + count_leaves(node.right)


def count_internal_nodes(node: Optional[TreeNode]) -> int:
    """
    Count non-leaf nodes.

    For a non-empty tree:
        nodes = leaves + internal nodes
    """
    if node is None:
        return 0

    if node.left is None and node.right is None:
        return 0

    return (
        1
        + count_internal_nodes(node.left)
        + count_internal_nodes(node.right)
    )


def verify_tree_partition_identity(node: Optional[TreeNode]) -> bool:
    """
    Structural property:

        total nodes = leaves + internal nodes

    A structural induction proof follows the recursive construction of the tree:
    empty tree, leaf node, and composite node.
    """
    return tree_size(node) == count_leaves(node) + count_internal_nodes(node)


# ---------------------------------------------------------------------------
# Section 16: Building a test tree
# ---------------------------------------------------------------------------

def sample_tree() -> TreeNode:
    """Construct a small non-trivial binary tree."""
    return TreeNode(
        10,
        left=TreeNode(
            5,
            left=TreeNode(2),
            right=TreeNode(7),
        ),
        right=TreeNode(
            15,
            right=TreeNode(20),
        ),
    )


# ---------------------------------------------------------------------------
# Section 17: Recurrence substitution verification
# ---------------------------------------------------------------------------

def verify_upper_bound_for_merge_sort_style_recurrence(
    n: int,
    c: float = 2.0,
) -> bool:
    """
    Demonstrate substitution-method reasoning for:

        T(n) = 2T(floor(n/2)) + n

    Suppose we seek a bound T(n) <= c*n*log2(n+1).

    The function evaluates the actual recurrence and compares it with the
    proposed upper bound.

    A finite computational test does not constitute a proof for all n.
    The proof must establish the inequality symbolically and choose constants
    that satisfy the induction step.
    """

    if n <= 1:
        return True

    @lru_cache(maxsize=None)
    def recurrence(value: int) -> int:
        if value <= 1:
            return 1

        half = value // 2
        return 2 * recurrence(half) + value

    actual = recurrence(n)
    bound = c * n * log2(n + 1)
    return actual <= bound


# ---------------------------------------------------------------------------
# Section 18: Master Theorem classification
# ---------------------------------------------------------------------------

def master_theorem_case(
    a: int,
    b: int,
    f_order_exponent: float,
) -> str:
    """
    Classify a recurrence of the form:

        T(n) = aT(n/b) + Theta(n^d)

    using the standard Master Theorem cases.

    Let:
        p = log_b(a)

    Case 1:
        d < p
        => Theta(n^p)

    Case 2:
        d = p
        => Theta(n^p log n)

    Case 3:
        d > p
        => Theta(n^d), subject to the regularity condition.

    This helper uses only the polynomial-exponent comparison. The full theorem
    has hypotheses that must be checked separately.
    """
    if a <= 0 or b <= 1:
        raise ValueError("Require a > 0 and b > 1")

    critical_exponent = log2(a) / log2(b)

    tolerance = 1e-12

    if f_order_exponent < critical_exponent - tolerance:
        return f"Case 1: Theta(n^{critical_exponent:.4g})"

    if abs(f_order_exponent - critical_exponent) <= tolerance:
        return f"Case 2: Theta(n^{critical_exponent:.4g} log n)"

    return f"Case 3: Theta(n^{f_order_exponent:.4g})"


# ---------------------------------------------------------------------------
# Section 19: Akra-Bazzi-style example
# ---------------------------------------------------------------------------

def uneven_divide_and_conquer(values: list[int]) -> int:
    """
    A deliberately simple uneven recursive computation.

    It recursively processes roughly 2/3 and 1/3 of the input and performs
    linear combination work.

    This illustrates why the simple Master Theorem does not directly apply to
    every recurrence. The exact recurrence is approximately:

        T(n) = T(2n/3) + T(n/3) + Theta(n)

    The linear combine work dominates, yielding Theta(n) under standard
    divide-and-conquer analysis.
    """
    n = len(values)

    if n <= 1:
        return sum(values)

    first_size = max(1, (2 * n) // 3)
    second_size = n - first_size

    first_part = values[:first_size]
    second_part = values[first_size:]

    return (
        uneven_divide_and_conquer(first_part)
        + uneven_divide_and_conquer(second_part)
        + sum(values)
    )


# ---------------------------------------------------------------------------
# Section 20: Memoization and overlapping subproblems
# ---------------------------------------------------------------------------

def fibonacci_call_count(n: int) -> tuple[int, int]:
    """
    Count calls made by naive recursive Fibonacci.

    Returns:
        (F(n), number_of_function_calls)

    This makes the recurrence for the amount of work visible.
    """
    calls = 0

    def fib(value: int) -> int:
        nonlocal calls
        calls += 1

        if value < 2:
            return value

        return fib(value - 1) + fib(value - 2)

    return fib(n), calls


def fibonacci_memoized_call_count(n: int) -> tuple[int, int]:
    """
    Count calls made by memoized Fibonacci.

    The recurrence remains mathematically identical, but the implementation
    avoids recomputing overlapping subproblems.
    """
    calls = 0
    cache: dict[int, int] = {}

    def fib(value: int) -> int:
        nonlocal calls
        calls += 1

        if value in cache:
            return cache[value]

        if value < 2:
            cache[value] = value
            return value

        cache[value] = fib(value - 1) + fib(value - 2)
        return cache[value]

    return fib(n), calls


# ---------------------------------------------------------------------------
# Section 21: Tail recursion and practical Python limitations
# ---------------------------------------------------------------------------

def countdown_recursive(n: int) -> list[int]:
    """
    A tail-position recursive operation.

    Python does not perform general tail-call optimization, so a tail-recursive
    Python function can still consume stack frames. For large n, iteration is
    generally preferable.
    """
    if n < 0:
        raise ValueError("n must be non-negative")

    result: list[int] = []

    def collect(value: int) -> None:
        if value == 0:
            return

        result.append(value)
        collect(value - 1)

    collect(n)
    return result


def countdown_iterative(n: int) -> list[int]:
    """Iterative counterpart to the recursive countdown."""
    if n < 0:
        raise ValueError("n must be non-negative")

    return list(range(n, 0, -1))


# ---------------------------------------------------------------------------
# Section 22: Edge cases
# ---------------------------------------------------------------------------

def edge_case_demonstrations() -> dict[str, object]:
    """Collect representative edge cases without terminating the program."""
    results: dict[str, object] = {}

    results["factorial_zero"] = factorial(0)
    results["fibonacci_zero"] = fibonacci_recursive(0)
    results["fibonacci_one"] = fibonacci_recursive(1)
    results["triangular_zero"] = triangular_recursive(0)
    results["hanoi_zero"] = hanoi_move_count(0)
    results["binary_search_empty"] = binary_search([], 10)
    results["merge_sort_empty"] = merge_sort([])
    results["merge_sort_singleton"] = merge_sort([42])

    try:
        factorial(-1)
    except ValueError as error:
        results["factorial_negative_error"] = str(error)

    return results


# ---------------------------------------------------------------------------
# Section 23: Proof-oriented assertions
# ---------------------------------------------------------------------------

def run_proof_checks() -> None:
    """Execute finite checks corresponding to several mathematical claims."""

    # Recursive definition versus closed form.
    for n in range(21):
        assert arithmetic_sequence_recursive(n) == arithmetic_sequence_closed_form(n)
        assert power_of_two_recursive(n) == power_of_two_closed_form(n)
        assert triangular_recursive(n) == triangular_closed_form(n)
        assert hanoi_move_count(n) == hanoi_closed_form(n)

    # Multiple implementations of Fibonacci agree.
    for n in range(25):
        assert fibonacci_recursive(n) == fibonacci_memoized(n)
        assert fibonacci_memoized(n) == fibonacci_iterative(n)

    # Search correctness.
    values = list(range(0, 100, 2))
    for target in values:
        index = binary_search(values, target)
        assert index >= 0
        assert values[index] == target

        recursive_index = binary_search_recursive(values, target)
        assert recursive_index >= 0
        assert values[recursive_index] == target

    assert binary_search(values, 101) == -1
    assert binary_search_recursive(values, 101) == -1

    # Sorting correctness.
    unsorted = [7, 2, 9, 1, 5, 2, 8, 0, -3]
    expected = sorted(unsorted)

    assert merge_sort(unsorted) == expected
    assert quicksort(unsorted) == expected

    # Induction-style checks.
    prove_triangular_formula(limit=100)
    assert verify_power_of_two_induction(limit=50)
    assert verify_strong_induction_composition(limit=100)

    # Structural induction property.
    tree = sample_tree()
    assert verify_tree_partition_identity(tree)
    assert verify_tree_partition_identity(None)

    # Master Theorem examples.
    assert master_theorem_case(2, 2, 1).startswith("Case 2")
    assert master_theorem_case(1, 2, 0).startswith("Case 2")
    assert master_theorem_case(2, 2, 0).startswith("Case 1")


# ---------------------------------------------------------------------------
# Section 24: Educational reporting
# ---------------------------------------------------------------------------

def print_sequence_examples() -> None:
    print("\nRECURSIVELY DEFINED SEQUENCES")
    print("-" * 72)

    for n in range(8):
        arithmetic = arithmetic_sequence_recursive(n)
        power = power_of_two_recursive(n)
        triangular = triangular_recursive(n)

        print(
            f"n={n:2d} | "
            f"arithmetic={arithmetic:4d} | "
            f"2^n={power:4d} | "
            f"triangular={triangular:3d}"
        )


def print_fibonacci_complexity_example() -> None:
    print("\nFIBONACCI AND REPEATED SUBPROBLEMS")
    print("-" * 72)

    for n in range(5, 11):
        naive_value, naive_calls = fibonacci_call_count(n)
        memo_value, memo_calls = fibonacci_memoized_call_count(n)

        print(
            f"n={n:2d} | "
            f"value={naive_value:4d} | "
            f"naive calls={naive_calls:5d} | "
            f"memoized calls={memo_calls:3d}"
        )


def print_recurrence_catalog() -> None:
    print("\nRECURRENCE CATALOG")
    print("-" * 72)

    for example in RECURRENCE_CATALOG:
        print(f"{example.name}:")
        print(f"  recurrence: {example.equation}")
        print(f"  base case:  {example.base_case}")
        print(f"  growth:     {example.asymptotic}")


def print_induction_examples() -> None:
    print("\nINDUCTION-BASED CHECKS")
    print("-" * 72)

    triangular_proof = prove_triangular_formula()

    print(f"Proposition: {triangular_proof.proposition_name}")
    print(f"Base case valid: {triangular_proof.verify_base_case()}")
    print(
        "Inductive implication checked for n=0..100: "
        f"{triangular_proof.verify_inductive_steps(100)}"
    )
    print(f"Power-of-two induction check: {verify_power_of_two_induction()}")
    print(
        "Strong-induction composition check through 100: "
        f"{verify_strong_induction_composition(100)}"
    )


def print_tree_examples() -> None:
    print("\nSTRUCTURAL INDUCTION ON A BINARY TREE")
    print("-" * 72)

    tree = sample_tree()

    print(f"Tree size: {tree_size(tree)}")
    print(f"Tree height: {tree_height(tree)}")
    print(f"Leaf count: {count_leaves(tree)}")
    print(f"Internal-node count: {count_internal_nodes(tree)}")
    print(
        "Nodes = leaves + internal nodes: "
        f"{verify_tree_partition_identity(tree)}"
    )


def print_recurrence_expansion() -> None:
    print("\nRECURRENCE EXPANSION")
    print("-" * 72)

    for line in expand_recurrence_t_minus_one_plus_n(5):
        print(line)


def print_algorithm_examples() -> None:
    print("\nALGORITHM EXAMPLES")
    print("-" * 72)

    values = [12, 3, 19, 5, 7, 1, 10, 4]

    print(f"Original values:       {values}")
    print(f"Merge sort result:     {merge_sort(values)}")
    print(f"Quicksort result:      {quicksort(values)}")

    sorted_values = sorted(values)
    target = 10

    print(f"Binary search target:  {target}")
    print(f"Iterative index:       {binary_search(sorted_values, target)}")
    print(
        "Recursive index:      "
        f"{binary_search_recursive(sorted_values, target)}"
    )


def print_master_theorem_examples() -> None:
    print("\nMASTER THEOREM EXAMPLES")
    print("-" * 72)

    examples = [
        (1, 2, 0),  # T(n) = T(n/2) + Theta(1)
        (2, 2, 1),  # T(n) = 2T(n/2) + Theta(n)
        (4, 2, 1),  # T(n) = 4T(n/2) + Theta(n)
        (2, 4, 1),  # T(n) = 2T(n/4) + Theta(n)
    ]

    for a, b, d in examples:
        print(
            f"T(n) = {a}T(n/{b}) + Theta(n^{d}): "
            f"{master_theorem_case(a, b, d)}"
        )


def print_edge_cases() -> None:
    print("\nEDGE CASES")
    print("-" * 72)

    for key, value in edge_case_demonstrations().items():
        print(f"{key}: {value}")


# ---------------------------------------------------------------------------
# Section 25: Main demonstration
# ---------------------------------------------------------------------------

def main() -> None:
    """
    Run the complete educational demonstration.

    The assertions provide a lightweight executable test suite. The printed
    material connects the implementations to recurrence and induction ideas.
    """
    run_proof_checks()

    print("RECURRENCE PROOFS: EXECUTABLE STUDY PROGRAM")
    print("=" * 72)

    print_sequence_examples()
    print_recurrence_expansion()
    print_fibonacci_complexity_example()
    print_algorithm_examples()
    print_induction_examples()
    print_tree_examples()
    print_recurrence_catalog()
    print_master_theorem_examples()
    print_edge_cases()

    print("\nSELECTED RECURSION-TREE VALUES")
    print("-" * 72)

    for n in [1, 2, 4, 8, 16]:
        cost = recurrence_tree_cost(
            n=n,
            branching_factor=2,
            cost_per_node=1,
            shrink_factor=2,
        )
        print(f"n={n:2d} -> recurrence-tree cost={cost}")

    print("\nSUBSTITUTION-STYLE FINITE CHECKS")
    print("-" * 72)

    for n in [2, 4, 8, 16, 32, 64]:
        print(
            f"n={n:2d} | "
            f"T(n) <= 2n log2(n+1): "
            f"{verify_upper_bound_for_merge_sort_style_recurrence(n)}"
        )

    print("\nUNEQUAL DIVIDE-AND-CONQUER EXAMPLE")
    print("-" * 72)

    sample_values = list(range(1, 13))
    print(
        "Recursive result for [1..12]: "
        f"{uneven_divide_and_conquer(sample_values)}"
    )

    print("\nTAIL RECURSION VERSUS ITERATION")
    print("-" * 72)

    print(f"Recursive countdown: {countdown_recursive(5)}")
    print(f"Iterative countdown: {countdown_iterative(5)}")

    print("\nAll executable proof checks passed.")


if __name__ == "__main__":
    main()
